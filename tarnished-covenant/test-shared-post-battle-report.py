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
    "const guaranteedText='+1';",
    "const drawText=reportReady?String(preview.draws):'—';",
    'Every completed Covenant fight pays exactly 1 guaranteed Smithing Favor.',
    'function tcBuildSharedBattleReportCompletion(latest,encounterId,actor)',
    'delete nc.battleReportDraft;',
    'let draws=0,guaranteedFavor=1;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'guaranteedFavor\n  }:null;',
    'retryBuilder:(latest)=>tcBuildSharedBattleReportCompletion(latest,encounterId,actor)?.state||null',
]: require(needle)

if html.count('/* --- Shared post-battle report sync --- */') != 1:
    raise SystemExit('shared report layer is duplicated')

# The authoritative late renderer always shows +1 guaranteed Favor. Shared
# Rite/Chaos answers determine bonus draws only.
start=html.rfind('renderPostBattleReport=function(){')
end=html.find('function tcBuildSharedBattleReportCompletion',start)
if start<0 or end<0: raise SystemExit('late shared report renderer missing')
renderer=html[start:end]
if "const guaranteedText='+1';" not in renderer:
    raise SystemExit('late renderer does not show flat +1 guaranteed Favor')
if 'tcSharedBattleReportDraft(state)' not in renderer:
    raise SystemExit('late renderer is not hydrating the shared report draft')

for forbidden in [
    'guaranteedFavor+=riteDraws;',
    'guaranteedFavor+=chaosDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+riteDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+chaosDraws;',
]:
    if forbidden in html:
        raise SystemExit('shared report reintroduced per-source Favor: '+forbidden)

print('Shared post-battle report: PASS — both phones share answers, every completed encounter grants +1 Favor, and Rite/Chaos control bonus draws.')
