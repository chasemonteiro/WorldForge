const assert=require('node:assert/strict');
const fs=require('node:fs'),zlib=require('node:zlib');
const {runtime,root}=require('./runtime.cjs');
const catalog=JSON.parse(fs.readFileSync(root+'/data/weapons.json','utf8'));
const data=JSON.parse(zlib.gunzipSync(fs.readFileSync(root+'/assets/build/weapon-data-v1.17.json.gz')));
const calculator=new Set(data.weapons.map(w=>w.weaponName));
const normalize=s=>s.replace(/\s*\(\+\d+\)$/,'').normalize('NFKD').toLowerCase().replace(/[^a-z0-9]/g,'');
assert.equal(new Set(catalog.weapons.map(w=>w.id)).size,catalog.weapons.length,'Stable IDs are unique');
for(const weapon of catalog.weapons){
 assert.match(weapon.id,/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
 assert(calculator.has(weapon.calculatorName),weapon.name+' must reference calculator data');
 assert.equal(normalize(weapon.name),normalize(weapon.calculatorName),'Calculator alias resolves to same weapon');
 assert(weapon.regions.length>0,weapon.name+' has a region');
 const regions=new Set();
 for(const region of weapon.regions){assert(!regions.has(region.name),weapon.name+' duplicates a region');regions.add(region.name)}
}
const app=runtime();
const known=new Set(catalog.weapons.map(w=>normalize(w.name)));
for(const [region,value] of Object.entries(app.json('regions'))){
 for(const weapon of value.weapons)assert(known.has(normalize(weapon.name)),region+': uncatalogued runtime weapon '+weapon.name);
}
console.log(`Catalog integrity: ${catalog.weapons.length} stable weapon IDs, calculator references, all 22 runtime regions PASS`);
