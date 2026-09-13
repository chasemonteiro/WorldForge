from pathlib import Path
import runpy

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Keep the Encounter victory / co-op clear / Weapon Appeal action area inside
# the Boss panel. The information-architecture renderer originally mounted the
# action bar after the swipe track, which made it visible under Weapons, Chaos,
# and Rite as well.
old_panel = "track.append(tcMakePanel('tc-encounter-panel','Target','boss',overviewNodes),"
new_panel = "const bossPanel=tcMakePanel('tc-encounter-panel','Target','boss',overviewNodes);track.append(bossPanel,"
if old_panel in s:
    s = s.replace(old_panel, new_panel, 1)
elif new_panel not in s and "const weaponPanel=tcMakePanel('tc-encounter-panel','Assigned Weapons','weapons',weaponNodes);" not in s:
    raise SystemExit('Encounter panel creation target missing')

old_mount = 'hint.after(bar);'
new_mount = 'bossPanel.appendChild(bar);'
if old_mount in s:
    s = s.replace(old_mount, new_mount, 1)
elif new_mount not in s:
    raise SystemExit('Encounter action-bar mount target missing')

required = [
    "const bossPanel=tcMakePanel('tc-encounter-panel','Target','boss',overviewNodes);",
    'track.append(bossPanel,',
    'bossPanel.appendChild(bar);',
    "tcBindCoopWorldClearControls(run?.state,run?.state?.current);",
]
for needle in required:
    if needle not in s:
        raise SystemExit('Boss-only Encounter action invariant missing: ' + needle)

if 'hint.after(bar);' in s:
    raise SystemExit('Encounter action bar still lives outside the swipe panels')

p.write_text(s)
print('Encounter victory and appeal actions moved into Boss panel only.')

# A normal appeal of both weapon assignments is two refusals, so it must carry
# two penalties. Apply this after all late appeal/reward layers so Joint Appeal
# remains the explicit zero-penalty two-weapon exception.
runpy.run_path('tarnished-covenant/build-double-appeal-penalties.py')
runpy.run_path('tarnished-covenant/test-double-appeal-penalties.py')
