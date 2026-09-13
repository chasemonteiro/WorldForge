from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing shared contract sync invariant: '+needle)

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or 'forbidden shared contract sync residue: '+needle)

for needle in [
    "const TC_SHARED_CONTRACT_SEEN_PREFIX='tc-shared-contract-seen-v1';",
    'function tcSharedContractPresentationKey(state=run?.state)',
    "return [ct.bearingId||'unknown',ct.commissionedAt||'legacy',ct.status||'task'].join('|');",
    'function tcSharedContractSeenStorageKey(state=run?.state,identity=playerName())',
    'function tcSharedContractWasSurfaced(state=run?.state,identity=playerName())',
    'function tcRememberSharedContractSurfaced(state=run?.state,identity=playerName())',
    'function tcMaybeSurfaceSharedContract(state=run?.state)',
    'if(!state||postBattleReport||pendingRewardReveal?.rewards?.length)return;',
    'const ct=smithingData(state).activeContract;',
    'if(!ct||!bellById(ct.bearingId)||tcSharedContractWasSurfaced(state))return;',
    'tcRememberSharedContractSurfaced(state);',
    'requestAnimationFrame(()=>{',
    'renderSmithingContract();',
    'const tcRenderRunBeforeSharedContractSync=renderRun;',
    'tcMaybeSurfaceSharedContract(run?.state);',
]: require(needle)

# There must be only one final sync layer after repeated builds.
if html.count('/* --- Shared Bell Bearing contract presentation --- */')!=1:
    raise SystemExit('shared contract presentation layer duplicated')
if html.count('const tcRenderRunBeforeSharedContractSync=renderRun;')!=1:
    raise SystemExit('shared contract render wrapper duplicated')

# The contract itself remains persisted shared state rather than becoming a local-only popup.
for needle in [
    'activeContract: raw.activeContract || null',
    'next.smithing.activeContract={bearingId:b.id,task,status:\'task\'',
    'function renderSmithingContract()',
    'data-smith-action="open-contract"',
]: require(needle)

print('Tarnished Covenant shared Bell Bearing contract sync: PASS — persisted contract auto-surfaces independently on each device.')
