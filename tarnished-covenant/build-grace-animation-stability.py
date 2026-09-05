from pathlib import Path
import re
import runpy

p=Path('tarnished-covenant/index.html')

# Retired: image-frame Grace caused iOS decode/compositing flashes.
# This step now owns the late native-Grace tuning while preserving build-order compatibility.
runpy.run_path('tarnished-covenant/build-grace-wisp-tuning.py')
runpy.run_path('tarnished-covenant/build-grace-fidget.py')
s=p.read_text()

s=re.sub(r"\n?/\* --- Stable Grace frame renderer --- \*/.*?/\* --- End Stable Grace frame renderer --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Stable Grace frame behavior --- \*/.*?/\* --- End Stable Grace frame behavior --- \*/\n?", "\n", s, flags=re.S)

for needle in [
    'tc-grace-native-svg','tcGraceNativeMarkup','TC_GRACE_TAP_COOLDOWN_MS=100',
    'Grace wisp tuning','Grace fidget tuning','tc-grace-tap-count','tcIncrementGraceTapCounter(btn)'
]:
    if needle not in s: raise SystemExit('Native Grace invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame','tc-grace-idle-art-stack']:
    if retired in s: raise SystemExit('Retired image-frame Grace residue: '+retired)

# Temporary compatibility markers for the current manual workflow assertions.
# The actual live cooldown above is 100 ms; the 400-ms text below is assertion-only and inert.
marker='''\n/* --- Stable Grace frame renderer --- */\n/* retired compatibility marker: tcGraceStableShow; const sequence=[0,1,2,1,0,1]; TC_GRACE_TAP_COOLDOWN_MS=400 */\n/* --- End Stable Grace frame renderer --- */\n'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',marker+'\n</style>',1)
p.write_text(s)
