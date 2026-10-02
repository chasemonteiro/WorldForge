const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();app.loadBuild();
app.run(`let fixture=tcNormalizeRunState(initialRunState({region:'Mt. Gelmir',severity:'cursed'}));
fixture.builds.chase.level=100;fixture.builds.morgan.level=120;
fixture.smithing=smithingData(fixture);fixture.smithing.appealWaivers=2;fixture.smithing.jointAppeals=1;
fixture.appealWeaponCooldown=['Serpent-Hunter'];
fixture.history.push({name:'Godskin Noble',region:'Mt. Gelmir',chaseWeapon:'Serpent-Hunter',morganWeapon:'Serpent-Hunter'});
let original=structuredClone(fixture);let target={name:'Rykard, Lord of Blasphemy',exit:true};`);
for(let i=0;i<40;i++){
 const pair=app.json('chooseWeaponPair(fixture,target)');
 for(const slot of ['chase','morgan']){
  assert.equal(pair[slot].name,'Serpent-Hunter');
  assert.equal(pair[slot].native,'Great-Serpent Hunt');
  assert.equal(pair[slot].infusable,false);
 }
}
assert.equal(app.run("makeBuild('Mt. Gelmir',target,['Serpent-Hunter'],fixture).name"),'Serpent-Hunter');
assert.equal(app.run("makeBuild('Mt. Gelmir',target,['Serpent-Hunter']).name"),'Serpent-Hunter');
assert.deepEqual(app.json('fixture'),app.json('original'),'Draw never mutates save');
app.run(`chooseTarget=()=>target;let encounter=newEncounter(fixture);fixture.current=encounter;let before=structuredClone(fixture);`);
assert.equal(app.run('encounter.chase.name'),'Serpent-Hunter');
assert.equal(app.run('encounter.morgan.name'),'Serpent-Hunter');
for(const slot of ['chase','morgan','both']){
 app.context.slot=slot;
 assert.deepEqual(app.json("changeWeapons(fixture,'Chase',slot,true)"),app.json('before'),'Fixed weapon appeal spends nothing');
}
assert.equal(app.run("tcBuildJointAppeal(fixture,fixture.current.id,'Serpent-Hunter','Serpent-Hunter',{name:'Dagger'},{name:'Greatbow'},'Chase')"),null);
assert.equal(app.run("tcBuildMasterworkRecall(fixture,fixture.current.id,'recall','Serpent-Hunter','chase','Chase')"),null);
app.run(`let ordinary=chooseWeaponPair(fixture,{name:'Godskin Noble'});`);
assert.notEqual(app.run('ordinary.chase.name'),'Serpent-Hunter');
assert.notEqual(app.run('ordinary.morgan.name'),'Serpent-Hunter');
assert.deepEqual(app.json('fixture.builds'),app.json('original.builds'),'Character builds unchanged');
console.log('Rykard: both Serpent-Hunters, repeated draws, encounter creation, appeals, rewards, save preservation PASS');
