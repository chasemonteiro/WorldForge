from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Smithing Favor rebalance
#
# Rite/Chaos completion is the reliable currency path. Honoring an eligible Rite
# or Chaos award now grants its Favor value directly AND still earns the same
# number of random Covenant reward draws. Random +Favor results remain bonuses.
# Contract prices stay 6/8/10/12 so progression remains meaningful.
# -----------------------------------------------------------------------------

old="  const nc=nextState.current;\n  let draws=0;\n  const riteDraws=Number(nc.weirdness?.favor??1);"
new="  const nc=nextState.current;\n  let draws=0,guaranteedFavor=0;\n  const riteDraws=Number(nc.weirdness?.favor??1);"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('post-battle guaranteed Favor counter target missing')

old="nc.smithingRiteFavor=true;draws+=riteDraws;"
new="nc.smithingRiteFavor=true;draws+=riteDraws;guaranteedFavor+=riteDraws;"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Rite guaranteed Favor target missing')

old="nc.smithingChaosFavor=true;draws+=chaosDraws;"
new="nc.smithingChaosFavor=true;draws+=chaosDraws;guaranteedFavor+=chaosDraws;"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Chaos guaranteed Favor target missing')

old="""  nc.postBattleRewards=[];
  nc.favorEarned=0;
  const completed=completeEncounter(nextState,playerName());"""
new="""  nextState.smithing=smithingData(nextState);
  nextState.smithing.favor+=guaranteedFavor;
  nc.postBattleRewards=[];
  nc.favorEarned=guaranteedFavor;
  const completed=completeEncounter(nextState,playerName());"""
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('guaranteed Favor persistence target missing')

# Random Favor from the later shared draw is a bonus on top of the guaranteed
# amount already written to the completed encounter history.
old="next.history[0].favorEarned=favorEarned;"
new="next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('history Favor accumulation target missing')

old='<div class="tc-report-total"><span>Covenant reward draws</span><strong>${draws}</strong></div>'
new='<div class="tc-report-total"><span>Guaranteed Smithing Favor</span><strong>+${draws}</strong></div><div class="tc-report-total"><span>Bonus Covenant reward draws</span><strong>${draws}</strong></div>'
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('battle-report Favor summary target missing')

old="Each earned draw can become Smithing Favor, a Refresh, or a rare Appeal Waiver."
new="Honor pays Smithing Favor immediately. Each Favor point earned here also grants one bonus Covenant reward draw."
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('battle-report Favor explanation target missing')

old='one possible reward from honoring rites and enduring Chaos'
new='earned directly by honoring Rites and enduring Chaos · bonus draws can add more'
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Smithing Favor ledger explanation target missing')

required=[
    'let draws=0,guaranteedFavor=0;',
    'guaranteedFavor+=riteDraws;',
    'guaranteedFavor+=chaosDraws;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;',
    'Guaranteed Smithing Favor',
    'Bonus Covenant reward draws',
    'Honor pays Smithing Favor immediately.',
    'earned directly by honoring Rites and enduring Chaos',
]
for needle in required:
    if needle not in s: raise SystemExit('Favor rebalance invariant missing: '+needle)

p.write_text(s)
print('Smithing Favor rebalanced: honored Rite/Chaos values are guaranteed currency plus bonus reward draws.')
