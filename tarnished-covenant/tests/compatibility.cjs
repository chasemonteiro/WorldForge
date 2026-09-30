const assert=require('node:assert/strict');
const fs=require('node:fs');
const {runtime,root}=require('./runtime.cjs');
const baseline=JSON.parse(fs.readFileSync(root+'/tests/release-baseline.json','utf8'));
const app=runtime();
assert.deepEqual(app.json('regions'),baseline.regions,'Final region metadata and weapon order must preserve the captured release');
assert.deepEqual(app.json('TC_WEAPON_ACQUISITION_GATES'),baseline.gates,'Acquisition rules must preserve the captured release');
for(const [region,expected] of Object.entries(baseline.scenarios)){
 let actual;
 try{actual=app.json(`initialRunState({region:${JSON.stringify(region)},severity:'standard',includeDlc:true})`)}catch(error){actual={expectedError:error.message}}
 assert.deepEqual(actual,expected,`Seeded encounter behavior changed in ${region}`);
}
// Older saves keep names, IDs, progression, builds, rewards, and unknown extension fields.
// Work on a synthetic copy; no actual room is opened or read.
app.loadBuild();
app.run(`let oldSave=initialRunState({region:'Limgrave + Stormveil',severity:'standard'});
oldSave.builds={chase:{startingClass:'',level:83,vig:30,mind:20,end:20,str:25,dex:25,int:10,fai:10,arc:10,scadu:0,talismans:['','','',''],physickTears:['',''],weapon:{weaponName:'Claymore',variantName:'Claymore',upgrade:12}},morgan:{level:92,str:40}};
oldSave.extensionFromFuture={mustSurvive:true};
let savedCopy=structuredClone(oldSave);let normalized=tcNormalizeRunState(structuredClone(oldSave));`);
for(const key of ['current','history','clearedRegions','extensionFromFuture'])assert.deepEqual(app.json(`normalized.${key}`),app.json(`savedCopy.${key}`),key+' preserved');
assert.equal(app.run('normalized.builds.chase.level'),83);
assert.equal(app.run('normalized.builds.morgan.level'),92);
assert.equal(app.run('normalized.builds.chase.weapon.upgrade'),12);
assert.deepEqual(app.json('oldSave'),app.json('savedCopy'),'Original save fixture unchanged');
console.log('Release compatibility: 22 regions, identical gates/order, seeded encounters, legacy save preservation PASS');
