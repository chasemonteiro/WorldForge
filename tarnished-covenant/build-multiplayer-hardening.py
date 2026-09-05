from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# -----------------------------------------------------------------------------
# Multiplayer hardening
#
# Shared saves are revision/CAS protected in Supabase. This late layer makes the
# browser side honor that model consistently: no wrapper may pre-lock a real
# action, stale phones resync after sleep/offline gaps, restarts are guarded too,
# and safe rare/inventory actions can rebase across unrelated remote updates.
# -----------------------------------------------------------------------------

# Remove any UI wrapper that takes the same __tcBoonBusy lock already owned by
# useCovenantBoon itself. Both historical wrapper names caused every click to no-op.
for token in ['tcUseCovenantBoonBeforePairing', 'tcUseCovenantBoonBeforeInteractionStabilization']:
    pattern = (
        r"\n?if\(typeof useCovenantBoon==='function'&&!window\.__tcBoonStabilized\)\{"
        r".*?const " + re.escape(token) + r"=useCovenantBoon;"
        r".*?\n\}\n?"
    )
    s = re.sub(pattern, '\n', s, count=1, flags=re.S)

# Local mode mirrors the guarded restart interface so runtime code has one shape.
local_old = '''    async restartRun(runId, state) {
      const current = loadLocalRun();
      const revision = (current?.revision ?? 0) + 1;
      const run = { ...(current || {}), id: runId, state, revision };
      saveLocalRun(run);
      if (listener) queueMicrotask(() => listener(run));
      return run;
    },'''
local_new = '''    async restartRun(runId, expectedRevision, state) {
      const current = loadLocalRun();
      if (current && Number(current.revision ?? 0) !== Number(expectedRevision ?? 0)) {
        return { success:false, ...current };
      }
      const revision = Number(expectedRevision ?? current?.revision ?? 0) + 1;
      const restarted = { ...(current || {}), id: runId, state, revision };
      saveLocalRun(restarted);
      if (listener) queueMicrotask(() => listener(restarted));
      return { success:true, ...restarted };
    },'''
if local_old in s:
    s = s.replace(local_old, local_new, 1)
elif 'async restartRun(runId, expectedRevision, state)' not in s:
    raise SystemExit('local guarded restart target missing')

# Shared restart uses a dedicated guarded RPC. Keep the old two-argument RPC in
# the database for previously installed clients, but new builds never use it.
shared_old = '''    async restartRun(runId, state) {
      const { data, error } = await supabase.rpc('restart_covenant_run', {
        p_run_id: runId,
        p_new_state: state
      });
      if (error) throw error;
      const row = Array.isArray(data) ? data[0] : data;
      return { id: runId, state: row.state, revision: Number(row.revision) };
    },'''
shared_new = '''    async restartRun(runId, expectedRevision, state) {
      const { data, error } = await supabase.rpc('restart_covenant_run_guarded', {
        p_run_id: runId,
        p_expected_revision: expectedRevision,
        p_new_state: state
      });
      if (error) throw error;
      const row = Array.isArray(data) ? data[0] : data;
      return {
        success: Boolean(row.success),
        id: runId,
        state: row.state,
        revision: Number(row.revision)
      };
    },'''
if shared_old in s:
    s = s.replace(shared_old, shared_new, 1)
elif "restart_covenant_run_guarded" not in s:
    raise SystemExit('shared guarded restart target missing')

# A stale restart must not overwrite an intervening action from the other phone.
restart_call_old = '      const restarted = await backend.restartRun(run.id, buildFreshState(run.state));'
restart_call_new = '''      const restarted = await backend.restartRun(run.id, run.revision, buildFreshState(run.state));
      if (!restarted?.success) {
        run = {...oldRun, ...restarted, joinCode: restarted?.joinCode || oldRun?.joinCode};
        renderRun();
        setToast('The Covenant changed on the other phone before restart. Review the latest state first.');
        return;
      }'''
if restart_call_old in s:
    s = s.replace(restart_call_old, restart_call_new, 1)
elif 'backend.restartRun(run.id, run.revision, buildFreshState(run.state))' not in s:
    raise SystemExit('guarded restart caller target missing')

# An old local post-battle report only blocks the encounter it belongs to.
s = s.replace("  if(postBattleReport)return 'post-battle';",
              "  if(postBattleReport?.encounterId===state?.current?.id)return 'post-battle';", 1)
if "postBattleReport?.encounterId===state?.current?.id" not in s:
    raise SystemExit('encounter-scoped post-battle lock missing')

# retryBuilder is intentionally allowed to decline a rebase. Never send null as
# a state document when a remote action made the local action obsolete.
retry_old = '      desiredState = retryBuilder(run.state);'
retry_new = '''      const rebuiltState = retryBuilder(run.state);
      if (!rebuiltState) {
        renderRun();
        setToast('The run changed on the other phone. That action no longer applies.');
        return false;
      }
      desiredState = rebuiltState;'''
if retry_old in s:
    s = s.replace(retry_old, retry_new, 1)
elif 'const rebuiltState = retryBuilder(run.state);' not in s:
    raise SystemExit('retryBuilder null guard target missing')

# On an ambiguous network failure, fetch the authoritative row before inviting a
# retry. The server may have accepted the save even if the response was lost.
catch_old = '''  } catch (error) {
    console.error(error);
    setToast('Save failed. Try again.');
    return false;
  } finally {'''
catch_new = '''  } catch (error) {
    console.error(error);
    if (backend?.mode === 'shared' && run?.id) {
      try {
        const latest = await backend.getRun(run.id);
        const changed = tcApplyAuthoritativeRun(latest, {source:'save-recovery'});
        if (changed) {
          setToast('Connection hiccup. Shared run resynced; check the latest state before retrying.');
          return false;
        }
      } catch (syncError) {
        console.warn('Shared save recovery fetch failed', syncError);
      }
    }
    setToast('Save failed. Try again.');
    return false;
  } finally {'''
if catch_old in s:
    s = s.replace(catch_old, catch_new, 1)
elif "source:'save-recovery'" not in s:
    raise SystemExit('save recovery target missing')

# Refreshes may safely survive an unrelated remote update, but never auto-spend a
# higher amendment cost or overwrite a remotely changed Rite/Chaos decree.
boon_old = '''async function useCovenantBoon(kind){
  if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;
  const key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';const c=run.state.current;const cost=tcRefreshCost(c,kind);const sm=smithingData(run.state);
  if(Number(sm[key]||0)<cost){window.__tcBoonBusy=false;return setToast(`That amendment costs ${cost} Refreshes.`);}
  let staged=smithingCopy(run.state);staged.smithing[key]-=cost;staged.current[kind+'RefreshUses']=Number(staged.current[kind+'RefreshUses']||0)+1;
  staged=kind==='chaos'?rerollChaos(staged,playerName()):rerollWeirdness(staged,playerName());
  if(kind==='chaos')try{acknowledgedChaos.delete(staged.current.id)}catch{}
  try{await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} amended. ${cost} Refresh${cost===1?'':'es'} spent.`});}finally{window.__tcBoonBusy=false;}
}'''
boon_new = '''async function useCovenantBoon(kind){
  if(window.__tcBoonBusy||!run?.state?.current)return;window.__tcBoonBusy=true;
  const key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';
  const c=run.state.current;
  const encounterId=c.id;
  const originalUses=Number(c?.[kind+'RefreshUses']||0);
  const originalChaosTriggered=Boolean(c.chaosTriggered);
  const originalChaosText=String(originalChaosTriggered?c.chaosConsequence||'':c.chaosTrigger||'');
  const originalRiteName=String(c.weirdness?.name||'');
  const cost=tcRefreshCost(c,kind);
  const actor=playerName();
  const buildRefresh=(latest)=>{
    const lc=latest?.current;if(!lc||lc.id!==encounterId)return null;
    if(Number(lc?.[kind+'RefreshUses']||0)!==originalUses)return null;
    if(kind==='chaos'){
      if(Boolean(lc.chaosTriggered)!==originalChaosTriggered)return null;
      const latestChaosText=String(originalChaosTriggered?lc.chaosConsequence||'':lc.chaosTrigger||'');
      if(latestChaosText!==originalChaosText)return null;
    }
    if(kind==='rite'&&String(lc.weirdness?.name||'')!==originalRiteName)return null;
    const latestSm=smithingData(latest);
    if(Number(latestSm[key]||0)<cost)return null;
    let rebased=smithingCopy(latest);
    rebased.smithing[key]-=cost;
    rebased.current[kind+'RefreshUses']=originalUses+1;
    rebased=kind==='chaos'?rerollChaos(rebased,actor):rerollWeirdness(rebased,actor);
    return rebased;
  };
  const sm=smithingData(run.state);
  if(Number(sm[key]||0)<cost){window.__tcBoonBusy=false;return setToast(`That amendment costs ${cost} Refreshes.`);}
  const staged=buildRefresh(run.state);
  if(!staged){window.__tcBoonBusy=false;return setToast('That amendment changed on the other phone.');}
  try{
    const saved=await commit(staged,{successToast:`${kind==='chaos'?'Chaos':'Rite'} amended. ${cost} Refresh${cost===1?'':'es'} spent.`,retryBuilder:buildRefresh});
    if(saved&&kind==='chaos')try{acknowledgedChaos.delete(encounterId)}catch{}
  }finally{window.__tcBoonBusy=false;}
}'''
if boon_old in s:
    s = s.replace(boon_old, boon_new, 1)
elif 'const buildRefresh=(latest)=>{' not in s:
    raise SystemExit('multiplayer-safe boon function target missing')

# A 1-in-5000 Grace success should not be lost merely because the other phone
# made an unrelated save at the same moment. Rebase only while the same encounter
# is current and no phone has already claimed its one allowed Grace Favor.
grace_old = "  try{await commit(next,{successToast:'Administrative anomaly detected. +1 Smithing Favor.'});}\n  finally{tcGraceFavorBusy=false;}"
grace_new = """  try{
    await commit(next,{
      successToast:'Administrative anomaly detected. +1 Smithing Favor.',
      retryBuilder:(latest)=>{
        if(!latest?.current||latest.current.id!==encounterId||latest.graceIdleFavorEncounterId===encounterId)return null;
        const rebased=smithingCopy(latest);
        rebased.smithing.favor=Number(rebased.smithing.favor||0)+1;
        rebased.graceIdleFavorEncounterId=encounterId;
        rebased.lastAction='A Site of Grace produced an administrative anomaly. +1 Smithing Favor.';
        rebased.updatedAt=new Date().toISOString();
        return rebased;
      }
    });
  }
  finally{tcGraceFavorBusy=false;}"""
if grace_old in s:
    s = s.replace(grace_old, grace_new, 1)
elif 'latest.graceIdleFavorEncounterId===encounterId' not in s:
    raise SystemExit('Grace multiplayer rebase target missing')

# Remove a prior copy if this hardener is re-run on an already hardened page.
s = re.sub(r'\n?/\* --- Multiplayer synchronization hardening --- \*/.*?/\* --- End multiplayer synchronization hardening --- \*/\n?', '\n', s, flags=re.S)

js = r'''
/* --- Multiplayer synchronization hardening --- */
let tcSharedSyncBusy=false;

function tcClearStaleSharedTransients(previousState,nextState){
  const previousId=previousState?.current?.id||null;
  const nextId=nextState?.current?.id||null;
  if(postBattleReport?.encounterId && postBattleReport.encounterId!==nextId)postBattleReport=null;
  if(pendingRevealId && pendingRevealId!==nextId)pendingRevealId=null;
  if(previousId&&nextId&&previousId!==nextId){try{acknowledgedChaos.clear();}catch{}}
}

function tcApplyAuthoritativeRun(incoming,{source='realtime'}={}){
  if(!incoming?.state||!run)return false;
  const incomingRevision=Number(incoming.revision||0);
  const currentRevision=Number(run.revision||0);
  if(incomingRevision<=currentRevision)return false;
  const previousState=run.state;
  run={...run,...incoming,revision:incomingRevision};
  tcClearStaleSharedTransients(previousState,run.state);
  try{renderRun();}catch(error){console.error(`Shared ${source} render failed`,error);}
  return true;
}

async function tcSyncAuthoritativeRun(source='recovery'){
  if(backend?.mode!=='shared'||!run?.id||tcSharedSyncBusy||pending)return false;
  tcSharedSyncBusy=true;
  try{
    const latest=await backend.getRun(run.id);
    return tcApplyAuthoritativeRun(latest,{source});
  }catch(error){
    console.warn(`Shared ${source} sync failed`,error);
    return false;
  }finally{tcSharedSyncBusy=false;}
}

subscribe=function(){
  unsubscribe?.();
  if(!run?.id)return;
  unsubscribe=backend.subscribe(run.id,incoming=>{
    if(!incoming?.state)return;
    tcApplyAuthoritativeRun(incoming,{source:'realtime'});
  });
  if(backend.mode==='shared')window.setTimeout(()=>tcSyncAuthoritativeRun('subscribe'),350);
};

if(!window.__tcMultiplayerRecoveryBound){
  window.__tcMultiplayerRecoveryBound=true;
  window.addEventListener('online',()=>tcSyncAuthoritativeRun('online'));
  window.addEventListener('pageshow',()=>tcSyncAuthoritativeRun('pageshow'));
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible')tcSyncAuthoritativeRun('resume');
  });
  window.__tcMultiplayerHeartbeat=window.setInterval(()=>{
    if(document.visibilityState==='visible')tcSyncAuthoritativeRun('heartbeat');
  },30000);
}
/* --- End multiplayer synchronization hardening --- */
'''
idx = s.rfind('</script>')
if idx < 0:
    raise SystemExit('script end marker missing')
s = s[:idx] + js + '\n' + s[idx:]

required = [
    "restart_covenant_run_guarded",
    'backend.restartRun(run.id, run.revision, buildFreshState(run.state))',
    "postBattleReport?.encounterId===state?.current?.id",
    'const rebuiltState = retryBuilder(run.state);',
    "source:'save-recovery'",
    'const buildRefresh=(latest)=>{',
    'latest.graceIdleFavorEncounterId===encounterId',
    'function tcApplyAuthoritativeRun(',
    'function tcSyncAuthoritativeRun(',
    "window.addEventListener('online'",
    "window.addEventListener('pageshow'",
    "document.addEventListener('visibilitychange'",
    '30000',
    'Multiplayer synchronization hardening',
]
for needle in required:
    if needle not in s:
        raise SystemExit('multiplayer invariant missing: '+needle)

for forbidden in [
    'tcUseCovenantBoonBeforePairing',
    'tcUseCovenantBoonBeforeInteractionStabilization',
    "supabase.rpc('restart_covenant_run',",
    'backend.restartRun(run.id, buildFreshState(run.state))',
]:
    if forbidden in s:
        raise SystemExit('multiplayer forbidden residue: '+forbidden)

p.write_text(s)
