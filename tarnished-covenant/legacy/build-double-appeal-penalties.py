from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# A normal appeal of BOTH assigned weapons is two separate refusals and therefore
# carries two separate penalties. Joint Appeal remains the special treasury boon
# that rerolls both with no penalty and no Appeal Waiver cost.
s=re.sub(
    r"\n?/\* --- Double penalty for dual weapon appeal --- \*/.*?"
    r"/\* --- End double penalty for dual weapon appeal --- \*/\n?",
    "\n",
    s,
    flags=re.S,
)

# Make the active appeal copy explicit about the difference between one weapon
# and both weapons. A deliberately spent Appeal Waiver still covers the whole
# appeal, preserving the spend-or-save rule already in production.
s=s.replace(
    'Changing an assigned weapon normally creates a severe random penalty.',
    'Changing one assigned weapon creates one severe random penalty. Appealing both at once creates two penalties.',
)
s=s.replace(
    "successToast:useWaiver?'Weapon appeal granted. Appeal Waiver spent.':'Weapon appeal granted. Penalty accepted.'",
    "successToast:useWaiver?'Weapon appeal granted. Appeal Waiver spent.':which==='both'?'Weapon appeal granted. Two penalties accepted.':'Weapon appeal granted. Penalty accepted.'",
)

js=r'''
/* --- Double penalty for dual weapon appeal --- */
const tcChangeWeaponsBeforeDoubleAppealPenalty=changeWeapons;
changeWeapons=function(state,actor,which,useWaiver=false){
  // One voluntarily spent waiver still covers the whole appeal, exactly as the
  // explicit waiver-choice screen promises. Without a waiver, appealing both
  // weapons is resolved as two individual appeals: one reroll + one penalty each.
  if(which!=='both'||useWaiver){
    return tcChangeWeaponsBeforeDoubleAppealPenalty(state,actor,which,useWaiver);
  }
  let next=tcChangeWeaponsBeforeDoubleAppealPenalty(state,actor,'chase',false);
  next=tcChangeWeaponsBeforeDoubleAppealPenalty(next,actor,'morgan',false);
  next.lastAction=`${actor} appealed both assigned weapons. Two penalties were added.`;
  return next;
};
/* --- End double penalty for dual weapon appeal --- */
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

required=[
    'const tcChangeWeaponsBeforeDoubleAppealPenalty=changeWeapons;',
    "if(which!=='both'||useWaiver)",
    "tcChangeWeaponsBeforeDoubleAppealPenalty(state,actor,'chase',false)",
    "tcChangeWeaponsBeforeDoubleAppealPenalty(next,actor,'morgan',false)",
    'Two penalties were added.',
    'Appealing both at once creates two penalties.',
]
for needle in required:
    if needle not in s: raise SystemExit('double-appeal penalty invariant missing: '+needle)

p.write_text(s)
print('Normal dual-weapon appeals now incur two penalties; Joint Appeal remains penalty-free.')
