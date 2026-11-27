// Themed runs: every catalog weapon has a class; characters steer draws to
// their classes when the region allows; lore adds its own Rites. Synthetic.
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {runtime,root}=require('./runtime.cjs');
const app=runtime();
app.loadBuild();
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/weapons.json'),'utf8')).weapons;
assert.equal(catalog.filter(w=>!app.run(`tcWeaponClass(${JSON.stringify(w.name)})`)).length,0,'every catalog weapon has a class');
app.run(`
  var plain=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true});
  var ch=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true,rules:{theme:{kind:'character'}}});
  var fits=0,total=0;
  for(let i=0;i<8;i++){const e=newEncounter(ch);for(const s of ['chase','morgan']){total++;if(tcBuildFits(ch,s,e[s]))fits++;}}
  var base=0;for(let i=0;i<8;i++){const e=newEncounter(plain);for(const s of ['chase','morgan'])if(tcBuildFits(ch,s,e[s]))base++;}
  var lore=initialRunState({region:'Liurnia of the Lakes',severity:'cursed',includeDlc:true,rules:{theme:{kind:'lore',id:'carian'}}});
  var loreRites=0;for(let i=0;i<45;i++){const r=tcPickRite(lore);if(TC_LORE_THEMES.carian.rites.some(x=>x[0]===r[0]))loreRites++;}
  var appealed=changeWeapons(ch,'Chase','chase',false);
`);
assert.equal(app.run('plain.rules===undefined'),true,'no theme unless chosen');
assert.equal(app.run("ch.rules.theme.kind==='character'&&Boolean(TC_CHARACTERS[ch.rules.theme.chase])&&ch.rules.theme.chase!==ch.rules.theme.morgan"),true,'two different characters dealt');
assert.ok(app.run('fits/total')>app.run('base/total')+0.2,`characters steer draws (${app.run('fits')}/${app.run('total')} vs ${app.run('base')} unthemed)`);
assert.ok(app.run('loreRites')>=5&&app.run('loreRites')<=30,'about a third of Rites are the faction’s own');
assert.equal(app.run("lore.rules.theme.id==='carian'"),true);
assert.equal(app.run('appealed.current.penances.length'),1,'an Appeal still carries its penalty');
console.log('PASS tests/covenant-themes.cjs');
