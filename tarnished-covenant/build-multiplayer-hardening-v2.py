from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Multiplayer hardening v2
#
# Protects against the remaining browser-side races found after the first CAS /
# reconnect pass: late events from an old room, stale RPC responses arriving
# after a newer Realtime revision, silent Realtime channel failure, duplicate
# room mutations, and a cleared session silently rejoining from a stale ?join=.
# -----------------------------------------------------------------------------

# Pin the browser SDK so a future minor release cannot change runtime behavior
# underneath an otherwise unchanged static build.
floating = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
pinned = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.115.0/+esm'
if floating in s:
    s = s.replace(floating, pinned, 1)
elif pinned not in s:
    raise SystemExit('Supabase SDK import target missing')

# The invite code must be mutable so Leave Run can really detach this browser.
if "const incomingCode = new URLSearchParams(location.search).get('join')?.trim().toUpperCase() || '';" in s:
    s = s.replace(
        "const incomingCode = new URLSearchParams(location.search).get('join')?.trim().toUpperCase() || '';",
        "let incomingCode = new URLSearchParams(location.search).get('join')?.trim().toUpperCase() || '';",
        1,
    )
elif "let incomingCode = new URLSearchParams(location.search).get('join')?.trim().toUpperCase() || '';" not in s:
    raise SystemExit('mutable incomingCode target missing')

clear_old = '''function clearSession() {
  try { localStorage.removeItem(SESSION_KEY); } catch {}
  try { document.cookie = `${SESSION_COOKIE}=; Max-Age=0; Path=${sessionCookiePath()}; SameSite=Lax; Secure`; } catch {}
}'''
clear_new = '''function clearSession() {
  try { localStorage.removeItem(SESSION_KEY); } catch {}
  try { document.cookie = `${SESSION_COOKIE}=; Max-Age=0; Path=${sessionCookiePath()}; SameSite=Lax; Secure`; } catch {}
  incomingCode = '';
  try {
    const url = new URL(location.href);
    url.searchParams.delete('join');
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  } catch {}
}'''
if clear_old in s:
    s = s.replace(clear_old, clear_new, 1)
elif "url.searchParams.delete('join')" not in s:
    raise SystemExit('leave-room URL cleanup target missing')

# Monitor Realtime channel status. A subscription object existing is not proof
# that the websocket successfully joined; surface status to the recovery layer.
subscribe_old = '''    subscribe(runId, fn) {
      if (channel) supabase.removeChannel(channel);
      channel = supabase.channel(`covenant-${runId}`)
        .on('postgres_changes', {
          event: 'UPDATE', schema: 'public', table: 'runs', filter: `id=eq.${runId}`
        }, payload => fn(normalizeRun(payload.new)))
        .subscribe();
      return () => {
        if (channel) supabase.removeChannel(channel);
        channel = null;
      };
    }'''
subscribe_new = '''    subscribe(runId, fn) {
      if (channel) supabase.removeChannel(channel);
      let intentionalClose = false;
      let localChannel = null;
      localChannel = supabase.channel(`covenant-${runId}`)
        .on('postgres_changes', {
          event: 'UPDATE', schema: 'public', table: 'runs', filter: `id=eq.${runId}`
        }, payload => {
          const incoming = normalizeRun(payload.new);
          if (incoming?.id && incoming.id !== runId) return;
          fn(incoming);
        })
        .subscribe((status, error) => {
          if (typeof window.tcHandleRealtimeChannelStatus === 'function') {
            window.tcHandleRealtimeChannelStatus(status, error, runId, intentionalClose);
          }
        });
      channel = localChannel;
      return () => {
        intentionalClose = true;
        if (localChannel) supabase.removeChannel(localChannel);
        if (channel === localChannel) channel = null;
      };
    }'''
if subscribe_old in s:
    s = s.replace(subscribe_old, subscribe_new, 1)
elif 'tcHandleRealtimeChannelStatus(status, error, runId, intentionalClose)' not in s:
    raise SystemExit('Realtime status callback target missing')

# Never allow a late RPC response to roll the browser backward after a newer
# partner revision has already arrived through Realtime.
result_old = '''      const result = await backend.updateRun(run.id, expectedRevision, desiredState);
      if (result.success) {
        run = { ...run, state: result.state, revision: result.revision };'''
result_new = '''      const result = await backend.updateRun(run.id, expectedRevision, desiredState);
      const resultRevision = Number(result.revision || 0);
      if (result.success) {
        if (resultRevision >= Number(run.revision || 0)) {
          const previousState = run.state;
          run = { ...run, state: result.state, revision: resultRevision };
          if (typeof tcClearStaleSharedTransients === 'function') tcClearStaleSharedTransients(previousState, run.state);
        }'''
if result_old in s:
    s = s.replace(result_old, result_new, 1)
elif 'const resultRevision = Number(result.revision || 0);' not in s:
    raise SystemExit('save-response revision guard target missing')

conflict_old = '''      run = { ...run, state: result.state, revision: result.revision };
      if (!retryBuilder) {'''
conflict_new = '''      if (resultRevision >= Number(run.revision || 0)) {
        const previousState = run.state;
        run = { ...run, state: result.state, revision: resultRevision };
        if (typeof tcClearStaleSharedTransients === 'function') tcClearStaleSharedTransients(previousState, run.state);
      }
      if (!retryBuilder) {'''
if conflict_old in s:
    s = s.replace(conflict_old, conflict_new, 1)
elif 'if (resultRevision >= Number(run.revision || 0)) {' not in s:
    raise SystemExit('conflict-response revision guard target missing')

# If a wake/online recovery request happens during a save, defer it rather than
# dropping it until the next heartbeat.
finally_old = '''  } finally {
    pending = false;
  }
}'''
finally_new = '''  } finally {
    pending = false;
    if (typeof tcDrainDeferredSharedSync === 'function') queueMicrotask(tcDrainDeferredSharedSync);
  }
}'''
if finally_old in s:
    s = s.replace(finally_old, finally_new, 1)
elif 'queueMicrotask(tcDrainDeferredSharedSync)' not in s:
    raise SystemExit('deferred sync drain target missing')

# Prevent accidental double-tap room creation / joining from producing duplicate
# room mutations while the first network request is still in flight.
if 'let tcEntryMutationBusy = false;' not in s:
    anchor = 'let pending = false;\nlet toastTimer = null;'
    if anchor not in s:
        raise SystemExit('entry mutation guard anchor missing')
    s = s.replace(anchor, 'let pending = false;\nlet tcEntryMutationBusy = false;\nlet toastTimer = null;', 1)

create_anchor = '''    if (!one || !two) return setToast('Name both Tarnished first.');
    const state = initialRunState({'''
create_repl = '''    if (!one || !two) return setToast('Name both Tarnished first.');
    if (tcEntryMutationBusy) return;
    tcEntryMutationBusy = true;
    const state = initialRunState({'''
if create_anchor in s:
    s = s.replace(create_anchor, create_repl, 1)
elif 'tcEntryMutationBusy = true;\n    const state = initialRunState({' not in s:
    raise SystemExit('new-run double-submit guard target missing')

create_catch_old = '''    } catch (error) {
      console.error(error);
      setToast(error.message || 'Could not create Covenant.');
    }
  });
}'''
create_catch_new = '''    } catch (error) {
      console.error(error);
      setToast(error.message || 'Could not create Covenant.');
    } finally {
      tcEntryMutationBusy = false;
    }
  });
}'''
if create_catch_old in s:
    s = s.replace(create_catch_old, create_catch_new, 1)
elif "setToast(error.message || 'Could not create Covenant.');\n    } finally {\n      tcEntryMutationBusy = false;" not in s:
    raise SystemExit('new-run guard release target missing')

join_old = '''async function joinSharedRun(code, identity) {
  try {'''
join_new = '''async function joinSharedRun(code, identity) {
  if (tcEntryMutationBusy) return false;
  tcEntryMutationBusy = true;
  try {'''
if join_old in s:
    s = s.replace(join_old, join_new, 1)
elif 'async function joinSharedRun(code, identity) {\n  if (tcEntryMutationBusy) return false;' not in s:
    raise SystemExit('join double-submit guard target missing')

join_catch_old = '''  } catch (error) {
    console.error(error);
    setToast(error.message || 'Could not join that Covenant.');
  }
}'''
join_catch_new = '''  } catch (error) {
    console.error(error);
    setToast(error.message || 'Could not join that Covenant.');
    return false;
  } finally {
    tcEntryMutationBusy = false;
  }
}'''
if join_catch_old in s:
    s = s.replace(join_catch_old, join_catch_new, 1)
elif "setToast(error.message || 'Could not join that Covenant.');\n    return false;\n  } finally {\n    tcEntryMutationBusy = false;" not in s:
    raise SystemExit('join guard release target missing')

# Replace the v1 recovery block with a status-aware, room-id-safe implementation.
block_pattern = re.compile(
    r'/\* --- Multiplayer synchronization hardening --- \*/.*?/\* --- End multiplayer synchronization hardening --- \*/',
    re.S,
)
if not block_pattern.search(s):
    raise SystemExit('multiplayer synchronization block missing')

js = r'''/* --- Multiplayer synchronization hardening --- */
let tcSharedSyncBusy=false;
let tcDeferredSharedSyncSource='';
let tcRealtimeStatus='UNKNOWN';
let tcRealtimeRepairTimer=null;

function tcClearStaleSharedTransients(previousState,nextState){
  const previousId=previousState?.current?.id||null;
  const nextId=nextState?.current?.id||null;
  if(postBattleReport?.encounterId && postBattleReport.encounterId!==nextId)postBattleReport=null;
  if(pendingRevealId && pendingRevealId!==nextId)pendingRevealId=null;
  if(previousId&&nextId&&previousId!==nextId){try{acknowledgedChaos.clear();}catch{}}
}

function tcApplyAuthoritativeRun(incoming,{source='realtime'}={}){
  if(!incoming?.state||!run)return false;
  if(incoming?.id&&run?.id&&incoming.id!==run.id){
    console.warn(`Ignored late ${source} payload for another Covenant`,incoming.id);
    return false;
  }
  const incomingRevision=Number(incoming.revision||0);
  const currentRevision=Number(run.revision||0);
  if(incomingRevision<=currentRevision)return false;
  const previousState=run.state;
  run={...run,...incoming,revision:incomingRevision};
  tcClearStaleSharedTransients(previousState,run.state);
  try{renderRun();}catch(error){console.error(`Shared ${source} render failed`,error);}
  return true;
}

function tcDrainDeferredSharedSync(){
  if(pending||tcSharedSyncBusy||!tcDeferredSharedSyncSource)return;
  const source=tcDeferredSharedSyncSource;
  tcDeferredSharedSyncSource='';
  tcSyncAuthoritativeRun(`deferred-${source}`);
}

async function tcSyncAuthoritativeRun(source='recovery'){
  if(backend?.mode!=='shared'||!run?.id)return false;
  if(pending||tcSharedSyncBusy){tcDeferredSharedSyncSource=source;return false;}
  tcSharedSyncBusy=true;
  try{
    const runId=run.id;
    const latest=await backend.getRun(runId);
    if(run?.id!==runId)return false;
    return tcApplyAuthoritativeRun(latest,{source});
  }catch(error){
    console.warn(`Shared ${source} sync failed`,error);
    return false;
  }finally{
    tcSharedSyncBusy=false;
    queueMicrotask(tcDrainDeferredSharedSync);
  }
}

function tcScheduleRealtimeRepair(source='realtime'){
  if(backend?.mode!=='shared'||!run?.id||tcRealtimeRepairTimer)return;
  tcRealtimeRepairTimer=window.setTimeout(()=>{
    tcRealtimeRepairTimer=null;
    if(backend?.mode!=='shared'||!run?.id||navigator.onLine===false)return;
    try{subscribe();}catch(error){console.warn('Realtime resubscribe failed',error);}
    tcSyncAuthoritativeRun(`repair-${source}`);
  },1200);
}

window.tcHandleRealtimeChannelStatus=function(status,error,runId,intentionalClose=false){
  if(!run?.id||run.id!==runId)return;
  tcRealtimeStatus=status||'UNKNOWN';
  if(status==='SUBSCRIBED'){
    if(tcRealtimeRepairTimer){clearTimeout(tcRealtimeRepairTimer);tcRealtimeRepairTimer=null;}
    window.setTimeout(()=>tcSyncAuthoritativeRun('realtime-subscribed'),0);
    return;
  }
  if(intentionalClose)return;
  if(status==='CHANNEL_ERROR'||status==='TIMED_OUT'||status==='CLOSED'){
    console.warn(`Realtime channel ${status}`,error||'');
    tcScheduleRealtimeRepair(String(status).toLowerCase());
  }
};

subscribe=function(){
  unsubscribe?.();
  if(!run?.id)return;
  const subscribedRunId=run.id;
  unsubscribe=backend.subscribe(subscribedRunId,incoming=>{
    if(!incoming?.state||run?.id!==subscribedRunId)return;
    tcApplyAuthoritativeRun(incoming,{source:'realtime'});
  });
  if(backend.mode==='shared')window.setTimeout(()=>tcSyncAuthoritativeRun('subscribe'),350);
};

if(!window.__tcMultiplayerRecoveryBound){
  window.__tcMultiplayerRecoveryBound=true;
  window.addEventListener('online',()=>{tcScheduleRealtimeRepair('online');tcSyncAuthoritativeRun('online');});
  window.addEventListener('pageshow',()=>{if(tcRealtimeStatus!=='SUBSCRIBED')tcScheduleRealtimeRepair('pageshow');tcSyncAuthoritativeRun('pageshow');});
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible'){
      if(tcRealtimeStatus!=='SUBSCRIBED')tcScheduleRealtimeRepair('resume');
      tcSyncAuthoritativeRun('resume');
    }
  });
  window.__tcMultiplayerHeartbeat=window.setInterval(()=>{
    if(document.visibilityState==='visible')tcSyncAuthoritativeRun('heartbeat');
  },30000);
}
/* --- End multiplayer synchronization hardening --- */'''
s = block_pattern.sub(js, s, count=1)

required = [
    '@supabase/supabase-js@2.115.0/+esm',
    "let incomingCode = new URLSearchParams(location.search).get('join')",
    "url.searchParams.delete('join')",
    'tcHandleRealtimeChannelStatus(status, error, runId, intentionalClose)',
    'const resultRevision = Number(result.revision || 0);',
    'queueMicrotask(tcDrainDeferredSharedSync)',
    'let tcEntryMutationBusy = false;',
    'incoming.id!==run.id',
    "status==='CHANNEL_ERROR'||status==='TIMED_OUT'||status==='CLOSED'",
    'tcScheduleRealtimeRepair',
    'const subscribedRunId=run.id;',
]
for needle in required:
    if needle not in s:
        raise SystemExit('multiplayer v2 invariant missing: ' + needle)

if floating in s:
    raise SystemExit('floating Supabase SDK import remains')
if "const incomingCode = new URLSearchParams(location.search).get('join')" in s:
    raise SystemExit('immutable incomingCode remains')

p.write_text(s)
print('Tarnished Covenant multiplayer hardening v2 applied.')
