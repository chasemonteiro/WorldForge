from pathlib import Path

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
elif new_panel not in s:
    raise SystemExit('Encounter Boss panel creation target missing')

old_mount = "hint.after(bar);tcWirePanelTrack(track,tabs,4,"
new_mount = "bossPanel.appendChild(bar);tcWirePanelTrack(track,tabs,4,"
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

if 'hint.after(bar);tcWirePanelTrack(track,tabs,4,' in s:
    raise SystemExit('Encounter action bar still lives outside the swipe panels')

p.write_text(s)
print('Encounter victory and appeal actions moved into Boss panel only.')
