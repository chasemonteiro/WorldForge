from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

old="""  if(roll<0.85){sm.aviaryTickets+=1;return {kind:'aviary',label:'Dynasty Frequent Flier',detail:'Grants 5 sanctioned trips to the bird. The bird remains a valued member of the economy.'};}
  if(roll<0.90){sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill',detail:'Kill one optional boss of your choice in the current or a previously reached region, then remove it from future Covenant encounter draws. Does not advance regional progression.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};"""
new="""  if(roll<0.85){sm.aviaryTickets+=1;return {kind:'aviary',label:'Dynasty Frequent Flier',detail:'Grants 5 sanctioned trips to the bird. The bird remains a valued member of the economy.'};}
  if(roll<0.90){const tax=pick(TC_COVENANT_TAXES);return {kind:'tax',label:tax.label,detail:tax.detail};}
  sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill',detail:'Kill one optional boss of your choice in the current or a previously reached region, then remove it from future Covenant encounter draws. Does not advance regional progression.'};"""

if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('reward odds swap target missing')

for needle in [
    "if(roll<0.85){sm.aviaryTickets+=1;",
    "if(roll<0.90){const tax=pick(TC_COVENANT_TAXES);",
    "sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill'",
]:
    if needle not in s: raise SystemExit('reward odds invariant missing: '+needle)

p.write_text(s)
print('Reward odds swapped: Covenant Tax 5%, Sanctioned Boss Kill 10%.')
