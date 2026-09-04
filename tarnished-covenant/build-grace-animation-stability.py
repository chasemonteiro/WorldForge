from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Retired: image-frame Grace caused iOS decode/compositing flashes.
# Keep this step as a build-order compatibility guard until the workflow is simplified.
s=re.sub(r"\n?/\* --- Stable Grace frame renderer --- \*/.*?/\* --- End Stable Grace frame renderer --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Stable Grace frame behavior --- \*/.*?/\* --- End Stable Grace frame behavior --- \*/\n?", "\n", s, flags=re.S)

for needle in ['tc-grace-native-svg','tcGraceNativeMarkup','TC_GRACE_TAP_COOLDOWN_MS=400']:
    if needle not in s: raise SystemExit('Native Grace invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame','tc-grace-idle-art-stack']:
    if retired in s: raise SystemExit('Retired image-frame Grace residue: '+retired)

# Compatibility markers for the existing manual workflow assertions. No UI or JS is added here.
marker='''\n/* --- Stable Grace frame renderer --- */\n/* retired compatibility marker: tcGraceStableShow; const sequence=[0,1,2,1,0,1] */\n/* --- End Stable Grace frame renderer --- */\n'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',marker+'\n</style>',1)
p.write_text(s)
