from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

BASE = 'https://p325k7wa.twic.pics/high/elden-ring/elden-ring/02-screenshots/'
DLC = 'https://p325k7wa.twic.pics/high/elden-ring/elden-ring/08-shadow-of-the-erdtree/elden-ring-expansion-SOTE/01-screenshot/'

def er(name):
    return BASE + name + '?twic=v1/cover=1600/quality=82'

def dlc(name):
    return DLC + name + '?twic=v1/cover=1600/quality=82'

images = {
  'Limgrave + Stormveil': er('ELDENRING_03_4K.jpg'),
  'Weeping Peninsula': er('ELDENRING_13_4K.jpg'),
  'Liurnia of the Lakes': er('ELDENRING_08_4K.jpg'),
  'Caelid': er('ELDENRING_12_4K.jpg'),
  'Altus Plateau + Leyndell': er('ELDENRING_10_4K.jpg'),
  'Mt. Gelmir': er('ELDENRING_15_4K.jpg'),
  'Mountaintops of the Giants': er('ELDENRING_16_4K.jpg'),
  'Miquella’s Haligtree': er('elden-ring-newscreen03.png'),
  'Crumbling Farum Azula': er('elden-ring-newscreen05.png'),
  'Siofra River + Nokron': er('ELDENRING_06_4K.jpg'),
  'Lake of Rot + Grand Cloister': er('ELDENRING_11_4K.jpg'),
  'Deeproot Depths': er('ELDENRING_09_4K.jpg'),
  'Mohgwyn Palace': er('elden-ring-newscreen04.png'),
  'Leyndell, Ashen Capital': er('elden-ring-godfrey-vertical-art.jpg'),
  'The Erdtree': er('ELDENRING_01_4K.jpg'),
  'Gravesite Plain · DLC': dlc('ERSOTE-screenshot-1.png'),
  'Cerulean Coast · DLC': dlc('ERSOTE-screenshot-6.png'),
  'Dragon’s Pit + Jagged Peak · DLC': dlc('ERSOTE-screenshot-7.png'),
  'Scadu Altus + Shadow Keep · DLC': dlc('ERSOTE-screenshot-4.png'),
  'Abyssal Woods · DLC': dlc('ERSOTE-screenshot-8.png'),
  'Ancient Ruins of Rauh · DLC': dlc('ERSOTE-screenshot-9.png'),
  'Enir-Ilim · DLC': dlc('ERSOTE-screenshot-10.png'),
}

map_js = 'const TC_REGION_IMAGES = {\n' + ',\n'.join(f"  {k!r}: {v!r}" for k,v in images.items()) + '\n};\nfunction actualRegionImage(name){ return TC_REGION_IMAGES[name] || TC_REGION_IMAGES[\'Limgrave + Stormveil\']; }\n'

# Insert before the themed artwork helper regardless of its argument names/defaults.
match = re.search(r'function\s+thematicRegionArt\s*\(', s)
if not match:
    raise SystemExit('thematicRegionArt function missing')
s = s[:match.start()] + map_js + '\n' + s[match.start():]

# Replace inline SVG art calls with real image-backed panels using tolerant regex hooks.
s, n = re.subn(
    r'<div class="tc-grace-art">\$\{thematicRegionArt\(state\.region\s*,\s*[\'\"]grace[\'\"]\)\}</div>',
    '<div class="tc-grace-art tc-photo" style="background-image:linear-gradient(180deg,rgba(3,3,2,.08),rgba(4,3,2,.42)),url(\'${actualRegionImage(state.region)}\')"></div>',
    s,
    count=1
)
if n != 1:
    raise SystemExit('Site of Grace art target missing')

s, n = re.subn(
    r'<div class="tc-boss-art">\$\{thematicRegionArt\(state\.region\s*,\s*[\'\"]boss[\'\"]\)\}</div>',
    '<div class="tc-boss-art tc-photo" style="background-image:linear-gradient(180deg,rgba(4,3,2,.12),rgba(5,4,3,.58)),url(\'${actualRegionImage(state.region)}\')"></div>',
    s,
    count=1
)
if n != 1:
    raise SystemExit('Encounter art target missing')

s, n = re.subn(
    r'<span class="tc-path-art">\$\{regionArtSvg\(r\)\}</span>',
    '<span class="tc-path-art tc-path-photo" style="background-image:linear-gradient(90deg,rgba(5,5,4,.14),rgba(5,5,4,.34)),url(\'${actualRegionImage(r)}\')"></span>',
    s,
    count=1
)
if n != 1:
    raise SystemExit('Travel art target missing')

# Add photo treatment and a CC0 texture to the Chaos reveal.
css = r'''
/* --- Real image asset pass --- */
.tc-photo{background-size:cover;background-position:center 45%;background-repeat:no-repeat}
.tc-grace-art.tc-photo{min-height:170px;box-shadow:inset 0 -70px 70px rgba(5,4,3,.80),0 12px 34px rgba(0,0,0,.24)}
.tc-boss-art.tc-photo{min-height:155px;background-position:center 38%;filter:saturate(.88) contrast(1.03)}
.tc-path-photo{background-size:cover;background-position:center;background-repeat:no-repeat;transform:scale(1.01);transition:transform .22s ease,filter .22s ease}
.tc-path:active .tc-path-photo{transform:scale(1.035);filter:brightness(1.12)}
.tc-chaos-event{background-image:linear-gradient(rgba(8,2,2,.45),rgba(3,2,2,.72)),url('https://commons.wikimedia.org/wiki/Special:Redirect/file/RED_RUST_TEXTURE.jpg');background-size:cover;background-position:center}
@media(max-width:480px){.tc-grace-art.tc-photo{min-height:145px}.tc-boss-art.tc-photo{min-height:132px}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s)
