from pathlib import Path
import re
import runpy

p=Path('tarnished-covenant/index.html')

# The raster frame renderer was retired after iOS decode/compositing flashes.
# This late step now reapplies and verifies the native Grace layers only.
runpy.run_path('tarnished-covenant/build-grace-wisp-tuning.py')
runpy.run_path('tarnished-covenant/build-grace-fidget.py')
s=p.read_text()

s=re.sub(r"\n?/\* --- Stable Grace frame renderer --- \*/.*?/\* --- End Stable Grace frame renderer --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Stable Grace frame behavior --- \*/.*?/\* --- End Stable Grace frame behavior --- \*/\n?", "\n", s, flags=re.S)

for needle in [
    'tc-grace-native-svg','tcGraceNativeMarkup','TC_GRACE_TAP_COOLDOWN_MS=100',
    'Grace wisp tuning','Grace fidget tuning','tc-grace-tap-count','tcIncrementGraceTapCounter(btn)'
]:
    if needle not in s:
        raise SystemExit('Native Grace invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame','tc-grace-idle-art-stack']:
    if retired in s:
        raise SystemExit('Retired image-frame Grace residue: '+retired)

p.write_text(s)

# Multiplayer hardening must run late, after the final encounter/Grace wrappers
# exist, so clean production builds cannot resurrect stale shared-state behavior.
runpy.run_path('tarnished-covenant/build-multiplayer-hardening.py')
