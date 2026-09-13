from pathlib import Path
import re

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
  const bar=document.createElement('div');bar.className='tc-encounter-actions tc-boss-victory-actions';bar.appendChild(complete);bossPanel.appendChild(bar);
  const appealBar=document.createElement('div');appealBar.className='tc-encounter-actions tc-weapon-appeal-actions';if(actions3)appealBar.appendChild(actions3);if(appealConfirm)appealBar.appendChild(appealConfirm);if(actions3||appealConfirm)weaponPanel.appendChild(appealBar);
"""
if old in s:
    s=s.replace(old,new,1)
else:
    # Normalize an already-tuned build so repeated production builds are safe.
    s=s.replace("const bar=document.createElement('div');bar.className='tc-encounter-actions';bar.appendChild(complete);bossPanel.appendChild(bar);",
                "const bar=document.createElement('div');bar.className='tc-encounter-actions tc-boss-victory-actions';bar.appendChild(complete);bossPanel.appendChild(bar);",1)
    if "const weaponPanel=tcMakePanel('tc-encounter-panel','Assigned Weapons','weapons',weaponNodes);" not in s:
        raise SystemExit('weapon-panel appeal mount target missing')

# Make current Appeal penalties impossible to miss while preserving the ability
# to collapse them after the player has read them. New renders open the warning.
s=s.replace(
    '${c.penances?.length?`<details class="tc-penalty-summary"><summary>${c.penances.length} active armament ${c.penances.length===1?\'penalty\':\'penalties\'}</summary>${penanceMarkup(c)}</details>`:\'\'}',
    '${c.penances?.length?`<details class="tc-penalty-summary" open><summary>${c.penances.length} ACTIVE WEAPON APPEAL ${c.penances.length===1?\'PENALTY\':\'PENALTIES\'}</summary>${penanceMarkup(c)}</details>`:\'\'}',
    1,
)

# Remove/reapply this late presentation layer idempotently.
s=re.sub(r"\n?/\* --- Encounter action fit \+ penalty visibility --- \*/.*?/\* --- End Encounter action fit \+ penalty visibility --- \*/\n?","\n",s,flags=re.S)
css=r'''
/* --- Encounter action fit + penalty visibility --- */
/* Boss: the dual-world card replaces #complete after panel enhancement, so it
   must occupy the entire action shelf instead of inheriting the old split grid. */
.tc-boss-victory-actions{grid-template-columns:1fr;padding:8px 0 5px;background:linear-gradient(180deg,rgba(8,8,6,.55),var(--bg) 35%)}
.tc-boss-victory-actions>.tc-world-clear-card{grid-column:1/-1;width:100%;margin:0;padding:12px 12px 11px;border-color:rgba(198,161,90,.32);background:linear-gradient(180deg,rgba(31,27,19,.72),rgba(12,11,8,.64))}
.tc-boss-victory-actions .tc-world-clear-head{margin-bottom:9px;align-items:center}.tc-boss-victory-actions .tc-world-clear-head strong{font-size:17px}.tc-boss-victory-actions .tc-world-clear-note{font-size:10px;line-height:1.35;max-width:36em}.tc-boss-victory-actions .tc-world-clear-count{padding:5px 7px;border:1px solid rgba(198,161,90,.28);background:rgba(198,161,90,.06)}
.tc-boss-victory-actions .tc-world-clear-grid{gap:7px}.tc-boss-victory-actions .tc-world-clear-btn{min-height:48px;padding:9px 8px;font-size:8px;line-height:1.25;white-space:normal}

/* Weapons: one action belongs here, so give it the whole shelf. */
.tc-weapon-appeal-actions{grid-template-columns:1fr;padding:10px 0 4px;margin-top:10px;background:linear-gradient(180deg,rgba(56,18,15,.08),var(--bg) 38%);border-top-color:rgba(201,102,90,.18)}
.tc-weapon-appeal-actions .tc-actions-3{display:block;width:100%;margin:0}.tc-weapon-appeal-actions .tc-actions-3 .btn{width:100%;min-height:48px;height:auto;padding:11px 13px;font-size:9px;letter-spacing:.075em}.tc-weapon-appeal-actions #appealConfirm{grid-column:1/-1;width:100%}.tc-weapon-appeal-actions #appealConfirm:empty{display:none}.tc-weapon-appeal-actions .confirm{margin:8px 0 0;width:100%;max-width:none}

/* Appeal penalties are active encounter rules, not incidental metadata. */
.tc-penalty-summary{margin:12px 0 14px;padding:0;border:1px solid rgba(201,102,90,.55);border-left:3px solid var(--red);background:linear-gradient(180deg,rgba(100,28,22,.20),rgba(42,13,11,.14));box-shadow:0 0 24px rgba(150,43,34,.06);overflow:hidden}
.tc-penalty-summary summary{position:relative;list-style:none;padding:12px 86px 12px 34px;color:#ef9589;font:900 9px/1.3 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.09em;cursor:pointer;background:rgba(126,38,30,.10)}
.tc-penalty-summary summary::-webkit-details-marker{display:none}.tc-penalty-summary summary:before{content:'!';position:absolute;left:11px;top:50%;transform:translateY(-50%);display:grid;place-items:center;width:15px;height:15px;border:1px solid var(--red);border-radius:50%;color:#f0a093;font:900 10px/1 system-ui,sans-serif}.tc-penalty-summary summary:after{content:'VIEW';position:absolute;right:11px;top:50%;transform:translateY(-50%);color:#a9665d;font:800 7px/1 system-ui,sans-serif;letter-spacing:.09em}.tc-penalty-summary[open] summary:after{content:'COLLAPSE'}
.tc-penalty-summary .curse-section{margin:0;padding:13px 13px 10px;border:0;border-top:1px solid rgba(201,102,90,.26);background:radial-gradient(circle at 0 0,rgba(117,33,26,.18),transparent 52%)}
.tc-penalty-summary .curse-head{font-size:12px;margin:5px 0 8px}.tc-penalty-summary .penance-item{margin-top:7px;padding:11px 10px;border:1px solid rgba(201,102,90,.22);border-left:2px solid rgba(201,102,90,.58);background:rgba(24,9,8,.32)}.tc-penalty-summary .penance-item+.penance-item{margin-top:8px}.tc-penalty-summary .penance-name{font-size:18px;color:#f0dfd3;margin:5px 0}.tc-penalty-summary .penance-text{font-size:12px;line-height:1.45;color:#d7c4b6}.tc-penalty-summary .scope{color:#e77e72}
@media(max-width:430px){.tc-boss-victory-actions .tc-world-clear-grid{grid-template-columns:1fr 1fr}.tc-boss-victory-actions .tc-world-clear-btn{font-size:7.5px;padding-left:5px;padding-right:5px}.tc-penalty-summary summary{padding-right:72px}}
@media(max-width:350px){.tc-boss-victory-actions .tc-world-clear-grid{grid-template-columns:1fr}.tc-penalty-summary summary{padding-right:12px}.tc-penalty-summary summary:after{display:none}}
/* --- End Encounter action fit + penalty visibility --- */
'''
if '</style>' not in s: raise SystemExit('encounter polish style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

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
    "bar.className='tc-encounter-actions tc-boss-victory-actions'",
    'bossPanel.appendChild(bar);',
    'weaponPanel.appendChild(appealBar);',
    '/* --- Encounter action fit + penalty visibility --- */',
    '.tc-boss-victory-actions>.tc-world-clear-card{grid-column:1/-1;',
    '.tc-weapon-appeal-actions{grid-template-columns:1fr;',
    '.tc-penalty-summary[open] summary:after{content:\'COLLAPSE\'}',
    'ACTIVE WEAPON APPEAL',
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
print('Encounter action shelves polished; Appeal penalties emphasized; Sanctioned Boss Kill remains 8%.')
