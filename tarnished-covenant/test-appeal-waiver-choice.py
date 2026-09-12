from pathlib import Path

s=Path('tarnished-covenant/index.html').read_text()

required=[
    'function changeWeapons(state, actor, which, useWaiver = false)',
    'const waived = Boolean(useWaiver && sm.appealWaivers > 0);',
    'function tcLegacyShowAppealMenu()',
    'function tcShowAppealWaiverChoice(which)',
    'function showAppealMenu()',
    'Spend 1 Appeal Waiver',
    'Keep Waiver · Take Penalty',
    'changeWeapons(run.state,playerName(),which,Boolean(useWaiver))',
    'if(waivers>0)tcShowAppealWaiverChoice(which)',
    "else void tcResolveWeaponAppeal(which,false);",
    "successToast:useWaiver?'Weapon appeal granted. Appeal Waiver spent.':which==='both'?'Weapon appeal granted. Two penalties accepted.':'Weapon appeal granted. Penalty accepted.'",
]
for needle in required:
    if needle not in s:
        raise SystemExit('Appeal Waiver choice invariant missing: '+needle)

if 'const waived = sm.appealWaivers > 0;' in s:
    raise SystemExit('automatic Appeal Waiver consumption remains in changeWeapons')

# The assembled page may retain a renamed dead legacy menu for compatibility,
# but exactly one active showAppealMenu declaration must remain.
if s.count('function showAppealMenu(){') != 1:
    raise SystemExit('expected exactly one active showAppealMenu override')

print('PASS: Appeal Waivers are explicitly spend-or-save during weapon appeals.')
