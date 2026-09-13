from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle):
    if needle not in html: raise SystemExit('shared report invariant missing: '+needle)

for needle in [
    '/* --- Shared post-battle report sync --- */',
    'function tcSharedBattleReportDraft(state=run?.state)',
    'battleReportDraft',
    'function tcBuildSharedBattleReportChoice(latest,encounterId,kind,value,actor)',
    "if(typeof tcBothWorldsCleared==='function'&&!tcBothWorldsCleared(c))return null;",
    'retryBuilder:build',
    'const draft=tcSharedBattleReportDraft(state);',
    "const guaranteedText=reportReady?`+${preview.guaranteedFavor}`:'—';",
    "const drawText=reportReady?String(preview.draws):'—';",
    'Waiting for the shared honor-system checks. No +0 is assumed while answers are pending.',
    'function tcBuildSharedBattleReportCompletion(latest,encounterId,actor)',
    'delete nc.battleReportDraft;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'guaranteedFavor\n  }:null;',
    'retryBuilder:(latest)=>tcBuildSharedBattleReportCompletion(latest,encounterId,actor)?.state||null',
]: require(needle)

if html.count('/* --- Shared post-battle report sync --- */') != 1:
    raise SystemExit('shared report layer is duplicated')

# The authoritative late renderer must not assume +0 while the partner is still
# answering the report; unresolved state is an em dash and the total comes from
# the shared draft only.
start=html.rfind('renderPostBattleReport=function(){')
end=html.find('function tcBuildSharedBattleReportCompletion',start)
if start<0 or end<0: raise SystemExit('late shared report renderer missing')
renderer=html[start:end]
if '<strong>+${draws}</strong>' in renderer:
    raise SystemExit('late renderer still uses a phone-local +draws total')
if 'tcSharedBattleReportDraft(state)' not in renderer:
    raise SystemExit('late renderer is not hydrating the shared report draft')

print('Shared post-battle report: PASS — report choices, guaranteed Favor preview, and finalization are authoritative across both phones.')
