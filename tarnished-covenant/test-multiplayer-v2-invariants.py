from pathlib import Path

html = Path('tarnished-covenant/index.html').read_text()

def require(needle):
    if needle not in html:
        raise SystemExit('missing multiplayer v2 invariant: ' + needle)

def forbid(needle):
    if needle in html:
        raise SystemExit('forbidden multiplayer v2 residue: ' + needle)

for needle in [
    '@supabase/supabase-js@2.115.0/+esm',
    "let incomingCode = new URLSearchParams(location.search).get('join')",
    "url.searchParams.delete('join')",
    'tcHandleRealtimeChannelStatus(status, error, runId, intentionalClose)',
    "status==='CHANNEL_ERROR'||status==='TIMED_OUT'||status==='CLOSED'",
    'tcScheduleRealtimeRepair',
    'const subscribedRunId=run.id;',
    'incoming.id!==run.id',
    'const resultRevision = Number(result.revision || 0);',
    'resultRevision >= Number(run.revision || 0)',
    'tcDrainDeferredSharedSync',
    'queueMicrotask(tcDrainDeferredSharedSync)',
    'let tcEntryMutationBusy = false;',
]:
    require(needle)

for needle in [
    '@supabase/supabase-js@2/+esm',
    "const incomingCode = new URLSearchParams(location.search).get('join')",
]:
    forbid(needle)

if html.count('function tcApplyAuthoritativeRun(') != 1:
    raise SystemExit('expected one authoritative shared-state applier')
if html.count('window.tcHandleRealtimeChannelStatus=function(') != 1:
    raise SystemExit('expected one Realtime status handler')
if html.count('resultRevision >= Number(run.revision || 0)') < 2:
    raise SystemExit('expected both success and conflict responses to be revision guarded')

print('Tarnished Covenant multiplayer v2 invariants: PASS')
