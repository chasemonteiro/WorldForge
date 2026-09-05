from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle):
    if needle not in html:
        raise SystemExit('missing multiplayer invariant: '+needle)

def forbid(needle):
    if needle in html:
        raise SystemExit('forbidden multiplayer residue: '+needle)

# Shared-state writes and destructive restart both use revision-aware contracts.
for needle in [
    "p_expected_revision: expectedRevision",
    "supabase.rpc('update_covenant_state'",
    "supabase.rpc('restart_covenant_run_guarded'",
    'backend.restartRun(run.id, run.revision, buildFreshState(run.state))',
]: require(needle)

# Reconnect/wake recovery must fetch the authoritative row rather than trusting
# Realtime to replay events that happened while the PWA was asleep.
for needle in [
    'function tcApplyAuthoritativeRun(',
    'function tcSyncAuthoritativeRun(',
    "window.addEventListener('online'",
    "window.addEventListener('pageshow'",
    "document.addEventListener('visibilitychange'",
    "tcSyncAuthoritativeRun('heartbeat')",
    '30000',
]: require(needle)

# Stale local transient UI cannot lock a newer encounter received from partner.
require("postBattleReport?.encounterId===state?.current?.id")
require('tcClearStaleSharedTransients')

# Safe conflict rebase behavior: unrelated partner updates may not destroy a rare
# Grace success or an amendment, but relevant remote changes abort the retry.
for needle in [
    'const rebuiltState = retryBuilder(run.state);',
    'if (!rebuiltState)',
    'const buildRefresh=(latest)=>{',
    "latest.graceIdleFavorEncounterId===encounterId",
    "source:'save-recovery'",
]: require(needle)

# Exactly one lock owner for Covenant Refreshes. Outer wrappers deadlock the real handler.
for needle in [
    'tcUseCovenantBoonBeforePairing',
    'tcUseCovenantBoonBeforeInteractionStabilization',
    "supabase.rpc('restart_covenant_run',",
    'backend.restartRun(run.id, buildFreshState(run.state))',
]: forbid(needle)

if html.count('function tcApplyAuthoritativeRun(')!=1:
    raise SystemExit('expected one authoritative shared-state applier')
if html.count('function tcSyncAuthoritativeRun(')!=1:
    raise SystemExit('expected one shared-state recovery fetcher')

print('Tarnished Covenant multiplayer invariants: PASS')
