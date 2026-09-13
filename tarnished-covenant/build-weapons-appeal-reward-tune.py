from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Keep victory / co-op clear on the Boss panel, but put Weapon Appeal where the
# player is actually looking at weapon assignments.
old="""  const bossPanel=tcMakePanel('tc-encounter-panel','Target','boss',overviewNodes);track.append(bossPanel,tcMakePanel('tc-encounter-panel','Assigned Weapons','weapons',weaponNodes),tcMakePanel('tc-encounter-panel','Chaos Decree','chaos',chaosNodes),tcMakePanel('tc-encounter-panel','Rite & Amendments','rite',riteNodes));tabs.after(track);
  const hint=document.createElement('div');hint.className='tc-encounter-hint';hint.textContent='Swipe between briefing panels';track.after(hint);
  const bar=document.createElement('div');bar.className='tc-encounter-actions';bar.appendChild(complete);if(actions3)bar.appendChild(actions3);if(appealConfirm)bar.appendChild(appealConfirm);bossPanel.appendChild(bar);
"""
new="""  const bossPanel=tcMakePanel('tc-encounter-panel','Target','boss',overviewNodes);const weaponPanel=tcMakePanel('tc-encounter-panel','Assigned Weapons','weapons',weaponNodes);track.append(bossPanel,weaponPanel,tcMakePanel('tc-encounter-panel','Chaos Decree','chaos',chaosNodes),tcMakePanel('tc-encounter-panel','Rite & Amendments','rite',riteNodes));tabs.after(track);
  const hint=document.createElement('div');hint.className='tc-encounter-hint';hint.textContent='Swipe between briefing panels';track.after(hint);
  const bar=document.createElement('div');bar.className='tc-encounter-actions';bar.appendChild(complete);bossPanel.appendChild(bar);
  const appealBar=document.createElement('div');appealBar.className='tc-encounter-actions tc-weapon-appeal-actions';if(actions3)appealBar.appendChild(actions3);if(appealConfirm)appealBar.appendChild(appealConfirm);if(actions3||appealConfirm)weaponPanel.appendChild(appealBar);
"""
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('weapon-panel appeal mount target missing')

# Sanctioned Boss Kill drops from 10% to 8%. The freed 2 points go to two lighter
# tactical rewards rather than more Favor: Clemency +1%, Blank Amendment +1%.
# Resulting table remains exactly 100%:
# 12 / 4 / 15 / 15 / 7 / 6 / 5 / 8 / 4 / 6 / 5 / 6 / 4 / 3.
replacements={
    "if(roll<0.74){sm.freeBossKills+=1;":"if(roll<0.72){sm.freeBossKills+=1;",
    "if(roll<0.78){sm.bossVetoes+=1;":"if(roll<0.76){sm.bossVetoes+=1;",
    "if(roll<0.83){sm.clemencies+=1;":"if(roll<0.82){sm.clemencies+=1;",
    "if(roll<0.88){sm.unionDiscounts+=1;":"if(roll<0.87){sm.unionDiscounts+=1;",
}
for old_t,new_t in replacements.items():
    if old_t in s:
        s=s.replace(old_t,new_t,1)
    elif new_t not in s:
        raise SystemExit('reward threshold target missing: '+old_t)

required=[
    "const weaponPanel=tcMakePanel('tc-encounter-panel','Assigned Weapons','weapons',weaponNodes);",
    'bossPanel.appendChild(bar);',
    'weaponPanel.appendChild(appealBar);',
    "if(roll<0.72){sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill'",
    "if(roll<0.76){sm.bossVetoes+=1;",
    "if(roll<0.82){sm.clemencies+=1;",
    "if(roll<0.87){sm.unionDiscounts+=1;",
    "if(roll<0.93){sm.blankAmendments+=1;",
    "if(roll<0.97){sm.jointAppeals+=1;",
]
for needle in required:
    if needle not in s: raise SystemExit('weapons/reward tune invariant missing: '+needle)

p.write_text(s)
print('Weapon Appeal moved to Weapons panel; Sanctioned Boss Kill tuned to 8%.')
