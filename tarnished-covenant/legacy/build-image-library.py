"""Apply user-supplied boss/location art after all presentation layers."""
from pathlib import Path
import json
import re

root=Path('tarnished-covenant')
p=root/'index.html'
s=p.read_text()
catalog=json.loads((root/'image-catalog.json').read_text())
regions={
 'Limgrave + Stormveil':'limgrave', 'Weeping Peninsula':'limgrave',
 'Liurnia of the Lakes':'liurnia of the lakes', 'Caelid':'caelid',
 'Altus Plateau + Leyndell':'altus plateau', 'Mt. Gelmir':'mt gelmir',
 'Mountaintops of the Giants':'mountaintops of the giants',
 'Miquella’s Haligtree':'haligtree', 'Crumbling Farum Azula':'farum azula',
 'Siofra River + Nokron':'underground', 'Lake of Rot + Grand Cloister':'underground',
 'Deeproot Depths':'underground', 'Mohgwyn Palace':'mohgwyn palace',
 'Leyndell, Ashen Capital':'altus plateau', 'The Erdtree':'altus plateau',
 'Gravesite Plain · DLC':'gravesite plain', 'Cerulean Coast · DLC':'cerulean coast',
 'Dragon’s Pit + Jagged Peak · DLC':'jagged peak',
 'Scadu Altus + Shadow Keep · DLC':'scadu altus', 'Abyssal Woods · DLC':'abyssal woods',
 'Ancient Ruins of Rauh · DLC':'ancient ruins of rauh', 'Enir-Ilim · DLC':'enir ilim'
}
# Explicit corrections for archive spellings, encounter titles, and shared variants.
# Never fuzzy-match different named bosses (e.g. Red Bear versus Ralva).
aliases={
 'Abductor Virgins (Duo)':'abductor duo',
 'Ancient Dragon-Man':'ancient dragon man',
 'Blackgaol Knight':'blackgaol knight or knight of the solitary gaol',
 'Borealis the Freezing Fog':'borealis of the freezing fog',
 "Commander O'Neil":'commander oneil',
 'Count Ymir, Mother of Fingers':'count ymir',
 'Crucible Knight & Crucible Knight Ordovis':'crucible knight ordovis',
 'Crucible Knight and Misbegotten Warrior':'misbegotten warrior and crucible knight',
 'Crystalian':'crystalian ringblade',
 'Crystalian Spear & Crystalian Ringblade':'crystalian ringblade',
 'Crystalian Spear & Crystalian Staff (Duo)':'crystalian ringblade',
 'Demi-Human Chief':'demi human chiefs',
 'Full-Grown Fallingstar Beast':'fallingstar beast',
 'Godfrey, First Elden Lord / Hoarah Loux':'godrey hoarah loux',
 'Godskin Duo':'godksin duo',
 'Godskin Apostle and Godskin Noble (Spiritcaller Snail)':'spiritcaller snail',
 'Jori, Elder Inquisitor':'jori elder inquisitor',
 'Mad Pumpkin Heads':'mad pumpkin head',
 'Maliketh, the Black Blade':'malekith the black blade',
 'Morgott, the Omen King':'morgott omen king',
 'Nox Swordstress & Nox Monk':'nox swordstress and nox priest',
 'Omenkiller & Miranda the Blighted Bloom':'omenkiller',
 'Perfumer Tricia and Misbegotten Warrior':'perfumer tricia',
 'Putrid Avatar':'erdtree avatar',
 'Putrid Crystalian Trio':'putrid crystallians',
 'Putrid Grave Warden Duelist':'grave warden duelist',
 'Putrid Tree Spirit':'ulcerated tree spirit',
 'Radagon of the Golden Order / Elden Beast':'radagon elden beast',
 'Red Wolf of the Champion':'red wolf of radagon',
 'Spirit-Caller Snail':'spiritcaller snail',
 'Tree Sentinel (Duo)':'tree sentinel duo',
 'Valiant Gargoyle & Valiant Gargoyle (Twinblade)':'valiant gargoyles',
 'Valiant Gargoyles':'valiant gargoyles',
 'Vyke, Knight of the Roundtable':'vyke',
}
def key(name): return re.sub(r'[^a-z0-9]+',' ',name.lower()).strip()
bosses=dict(catalog['bosses'])
for name,asset in aliases.items(): bosses[key(name)]=catalog['bosses'][asset]
for path in set(bosses.values()) | set(catalog['regions'].values()):
    if not (root/path).is_file(): raise SystemExit('Missing image: '+path)
region_map={name:catalog['regions'][asset] for name,asset in regions.items()}
# Replace original remote map, preserving all existing callers.
s,n=re.subn(r'const TC_REGION_IMAGES = \{.*?\n\};', 'const TC_REGION_IMAGES = '+json.dumps(region_map,ensure_ascii=False,indent=2)+';',s,count=1,flags=re.S)
if n!=1: raise SystemExit('Region map missing')
start='/* --- Imported boss image library --- */'
end='/* --- End imported boss image library --- */'
s=re.sub(re.escape(start)+'.*?'+re.escape(end)+'\n?', '', s, flags=re.S)
js=start+'\nconst TC_BOSS_IMAGES='+json.dumps(bosses,ensure_ascii=False)+';\n'+r'''
function tcBossImageKey(name){return String(name||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}
function actualBossImage(name,region){
  const key=tcBossImageKey(name);
  // Distinct supplied variants share the same title in regional gameplay data.
  if(key==='dragonkin soldier'&&region==='Lake of Rot + Grand Cloister')return TC_BOSS_IMAGES['dragonkin soldier lake of rot'];
  if(key==='divine beast dancing lion'&&region==='Ancient Ruins of Rauh · DLC')return TC_BOSS_IMAGES['divine beast dancing lion deathblight'];
  const base=tcBossImageKey(String(name||'').replace(/\s*\([^)]*\)/g,''));
  return TC_BOSS_IMAGES[key]||TC_BOSS_IMAGES[base]||actualRegionImage(region);
}
'''+end+'\n'
anchor='function thematicRegionArt('
s=s.replace(anchor,js+'\n'+anchor,1)
# Encounter portraits use the current boss; Grace and travel retain region scenery.
pattern=r'(<div class="tc-boss-art[^\n]*?)actualRegionImage\(state\.region\)'
s,n=re.subn(pattern,r'\1actualBossImage(c.target.name,state.region)',s)
if n==0 and 'actualBossImage(c.target.name,state.region)' not in s:
    raise SystemExit('Encounter portrait hook missing')
# Older archive cards use the same exact-name resolver.
s=s.replace('actualRegionImage(entry.region||run.state.region)','actualBossImage(entry.name,entry.region||run.state.region)')
p.write_text(s)
print('Applied imported image library: 22 regions, 141 boss assets, explicit aliases and regional variants')
