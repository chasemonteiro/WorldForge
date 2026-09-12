from pathlib import Path

s=Path('tarnished-covenant/index.html').read_text()

required=[
    'function changeWeapons(state, actor, which, useWaiver = false)',
    'const waived = Boolean(useWaiver && sm.appealWaivers > 0);',
    'function tcShowAppealWaiverChoice(which)',
    'Spend 1 Appeal Waiver',
    'Keep Waiver · Take Penalty',
    'changeWeapons(run.state,playerName(),which,Boolean(useWaiver))',
    'if(waivers>0)tcShowAppealWaiverChoice(which)',
    "else void tcResolveWeaponAppeal(which,false);",
    "successToast:useWaiver?'Weapon appeal granted. Appeal Waiver spent.':'Weapon appeal granted. Penalty accepted.'",
]
for needle in required:
    if needle not in s:
        raise SystemExit('Appeal Waiver choice invariant missing: '+needle)

forbidden=[
    'const waived = sm.appealWaivers > 0;',
    'Appeal Waiver available · this appeal is penalty-free and will consume 1 waiver.',
]
for needle in forbidden:
    if needle in s:
        raise SystemExit('automatic Appeal Waiver behavior survived: '+needle)

print('PASS: Appeal Waivers are explicitly spend-or-save during weapon appeals.')
