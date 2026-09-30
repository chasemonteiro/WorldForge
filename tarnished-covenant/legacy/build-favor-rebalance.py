from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# -----------------------------------------------------------------------------
# Smithing Favor rebalance
#
# Every completed Covenant encounter now pays exactly ONE guaranteed Smithing
# Favor. Honored Rite/Chaos objectives still determine the number of bonus random
# Covenant reward draws. Random +Favor results remain bonuses on top.
#
# IMPORTANT: this file is a late production patch and is run repeatedly. Normalize
# the base report here; the later shared-report patch owns the authoritative co-op
# renderer/finalizer, and final tests assert that no legacy per-source Favor remains.
# -----------------------------------------------------------------------------

s,n=re.subn(r"  let draws=0(?:,guaranteedFavor=\d+)?;", "  let draws=0,guaranteedFavor=1;", s, count=1)
if n!=1:
    raise SystemExit('post-battle guaranteed Favor counter target missing')

rite_pat=re.compile(r"nc\.smithingRiteFavor=true;draws\+=riteDraws;(?:guaranteedFavor\+=riteDraws;|guaranteedFavor=Number\(guaranteedFavor\)\+riteDraws;)*")
s,n=rite_pat.subn("nc.smithingRiteFavor=true;draws+=riteDraws;",s,count=1)
if n!=1:
    raise SystemExit('Rite bonus-draw target missing')

chaos_pat=re.compile(r"nc\.smithingChaosFavor=true;draws\+=chaosDraws;(?:guaranteedFavor\+=chaosDraws;|guaranteedFavor=Number\(guaranteedFavor\)\+chaosDraws;)*")
s,n=chaos_pat.subn("nc.smithingChaosFavor=true;draws+=chaosDraws;",s,count=1)
if n!=1:
    raise SystemExit('Chaos bonus-draw target missing')

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

old="next.history[0].favorEarned=favorEarned;"
new="next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('history Favor accumulation target missing')

old='<div class="tc-report-total"><span>Guaranteed Smithing Favor</span><strong>+${draws}</strong></div><div class="tc-report-total"><span>Bonus Covenant reward draws</span><strong>${draws}</strong></div>'
new='<div class="tc-report-total"><span>Guaranteed Smithing Favor</span><strong>+1</strong></div><div class="tc-report-total"><span>Bonus Covenant reward draws</span><strong>${draws}</strong></div>'
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('battle-report Favor summary target missing')

old="Honor pays Smithing Favor immediately. Each Favor point earned here also grants one bonus Covenant reward draw."
new="Every completed Covenant encounter pays 1 guaranteed Smithing Favor. Honored Rite and Chaos objectives determine bonus Covenant reward draws."
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('battle-report Favor explanation target missing')

for old_copy in [
    'earned directly by honoring Rites and enduring Chaos · bonus draws can add more',
    'earned directly by honoring Rites and enduring Chaos · bonus Favor can still drop from Covenant rewards',
]:
    if old_copy in s:
        s=s.replace(old_copy,'1 guaranteed per completed Covenant encounter · bonus draws can add more',1)

required=[
    'let draws=0,guaranteedFavor=1;',
    'nc.smithingRiteFavor=true;draws+=riteDraws;',
    'nc.smithingChaosFavor=true;draws+=chaosDraws;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;',
    'Guaranteed Smithing Favor',
    '<strong>+1</strong>',
    'Bonus Covenant reward draws',
    'Every completed Covenant encounter pays 1 guaranteed Smithing Favor.',
    '1 guaranteed per completed Covenant encounter',
]
for needle in required:
    if needle not in s: raise SystemExit('Favor rebalance invariant missing: '+needle)

p.write_text(s)
print('Smithing Favor base layer rebalanced: +1 guaranteed Favor per completed encounter; Rite/Chaos still award bonus draws.')
