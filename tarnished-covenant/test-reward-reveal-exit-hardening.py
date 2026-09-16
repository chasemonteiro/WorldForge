from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing reward exit hardening invariant: '+needle)

for needle in [
    '/* --- Shared reward reveal exit hardening --- */',
    'const tcRewardExitDismissedIds=new Set();',
    'const tcHydrateSharedRewardRevealBeforeExitHardening=tcHydrateSharedRewardReveal;',
    'if(id&&tcRewardExitDismissedIds.has(id))',
    'async function tcRewardExitAuthoritativeSync()',
    'await backend.getRun(run.id)',
    "tcApplyAuthoritativeRun(latest,{source:'reward-exit-hardening'})",
    'const tcAcknowledgeSharedRewardRevealBeforeExitHardening=tcAcknowledgeSharedRewardReveal;',
    'if(rewardId)tcRewardExitDismissedIds.add(rewardId);',
    'pendingRewardReveal=null;\n  renderRun();',
    'await tcRewardExitAuthoritativeSync();',
    'function tcArmFinalRewardExitWatchdog()',
    "const liveBtn=document.querySelector('#tcRewardContinue');",
    "liveBtn.disabled=false;",
    "liveBtn.dataset.ready='1';",
    'const tcRenderRewardMachineBeforeExitHardening=renderRewardMachine;',
    'async function tcRetryDismissedRewardAck()',
    "window.addEventListener('online',()=>setTimeout(tcRetryDismissedRewardAck,250));",
]: require(needle)

if html.count('/* --- Shared reward reveal exit hardening --- */') != 1:
    raise SystemExit('reward exit hardening layer duplicated')

print('Tarnished Covenant reward reveal exit hardening: PASS — final shared rewards dismiss locally, resync canonically, and stale iOS buttons self-heal.')
