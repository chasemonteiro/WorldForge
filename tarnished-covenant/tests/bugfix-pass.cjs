// Regressions from the 2026-10-08 bug pass. Synthetic states only; no room is opened.
const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();

// Region travel keeps run-level records and rolls the first encounter against the real history.
app.run(`
  var src=initialRunState({region:'Limgrave + Stormveil',severity:'standard'});
  src.history=[{name:'Godrick the Grafted',region:'Limgrave + Stormveil'}];
  src.clearedRegions=['Limgrave + Stormveil'];
  src.sanctionedBossKills=[{name:'Tree Sentinel',region:'Limgrave + Stormveil'}];
  src.appealPenaltyBossKills=[{name:'Bloodhound Knight Darriwil',region:'Limgrave + Stormveil'}];
  src.appealWeaponCooldown=['Claymore'];
  src.pendingDebt='Owe one';
  src.extensionFromFuture={keep:true};
  var travelled=startNextRegion(src,'Chase','Weeping Peninsula');
`);
assert.deepEqual(app.json('travelled.sanctionedBossKills'),[{name:'Tree Sentinel',region:'Limgrave + Stormveil'}]);
assert.deepEqual(app.json('travelled.appealPenaltyBossKills'),[{name:'Bloodhound Knight Darriwil',region:'Limgrave + Stormveil'}]);
assert.deepEqual(app.json('travelled.appealWeaponCooldown'),['Claymore']);
assert.deepEqual(app.json('travelled.extensionFromFuture'),{keep:true});
assert.equal(app.run('travelled.current.covenantDebt'),'Owe one','Capstone debt lands on the first encounter of the next region');
assert.equal(app.run('travelled.pendingDebt'),null);
assert.equal(app.run('travelled.history.length'),1);
assert.equal(app.run("travelled.region"),'Weeping Peninsula');

// A return trip never opens on a boss already killed in that region.
app.run(`
  var back=structuredClone(travelled);
  back.history=[...back.history,...regions['Weeping Peninsula'].bosses.slice(0,Math.max(0,regions['Weeping Peninsula'].bosses.length-2)).map(name=>({name,region:'Weeping Peninsula'}))];
  var killed=new Set(back.history.filter(h=>h.region==='Limgrave + Stormveil').map(h=>h.name));
  var returned=startNextRegion(back,'Morgan','Limgrave + Stormveil');
`);
assert.ok(!app.run("killed.has(returned.current?.target?.name)"),'Return trip must not open on a killed boss: '+app.run('returned.current?.target?.name'));

// Shared reward reveal clears once two different phones have seen it, whatever their identity strings.
app.run(`
  var rs=initialRunState({region:'Limgrave + Stormveil',severity:'standard'});
  rs.sharedRewardReveal={id:'r1',rewards:[{kind:'favor'}],seenBy:['Chase']};
  var acked=tcBuildSharedRewardAck(rs,'r1','Tarnished');
`);
assert.equal(app.run('acked.sharedRewardReveal'),null);

// Erdtree Writ supply is not reduced twice by a Writ-paid Avatar recorded through an appeal.
app.run(`
  var ws=initialRunState({region:'Limgrave + Stormveil',severity:'standard'});
  ws.appealPenaltyBossKills=[{name:'Erdtree Avatar',region:'Weeping Peninsula',erdtreeTargetId:'weeping'}];
  var cap=tcErdtreeWritIssueCap(ws);
`);
assert.equal(app.run('cap'),app.run('TC_ERDTREE_TARGETS.length'));

// Armory correction never touches an encounter once a world is cleared.
app.run(`
  var lk=initialRunState({region:'Siofra River + Nokron',severity:'standard'});
  lk.current.chase={...lk.current.chase,name:'Nox Flowing Hammer'};
  lk.current.worldClears=['chase'];
  var lockedSlots=tcEncounterMutationLocked(lk)?tcUnobtainableAssignedSlots(lk):['not-locked'];
  var free=structuredClone(lk);free.current.worldClears=[];
  var freeSlots=tcUnobtainableAssignedSlots(free);
`);
assert.deepEqual(app.json('lockedSlots'),[]);
assert.deepEqual(app.json('freeSlots'),['chase']);

// The Haligtree's Elphael weapons wait for Loretta; Troll's Hammer lives on the Altus Plateau.
assert.equal(app.run("tcWeaponAcquisitionUnlocked({history:[]},{name:'Rotten Crystal Sword'})"),false);
assert.equal(app.run("tcWeaponAcquisitionUnlocked({history:[{name:'Loretta, Knight of the Haligtree',region:'Miquella’s Haligtree'}]},{name:'Rotten Crystal Sword'})"),true);
assert.ok(app.run("regions['Altus Plateau + Leyndell'].weapons.some(w=>(w.name||w)===\"Troll's Hammer\")"));
assert.ok(!app.run("regions['Mt. Gelmir'].weapons.some(w=>(w.name||w)===\"Troll's Hammer\")"));
console.log('Bug pass regressions: travel records, return trips, reward ack, writ cap, armory lock, gate data PASS');
