// A boss moved out of a region's pool is replaced in an unstarted encounter only.
// Synthetic states only; no room is opened.
const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();
app.run(`
  var gp=initialRunState({region:'Gravesite Plain · DLC',severity:'standard',includeDlc:true});
  gp.current.target={name:'Chief Bloodfiend',exit:false};
  var fixed=tcRepairOutOfPoolTarget(structuredClone(gp));
  var started=structuredClone(gp);started.current.worldClears=['chase'];
  var capstone=structuredClone(gp);capstone.current.target={name:regions[gp.region].exit,exit:true};
  var required=structuredClone(gp);required.current.target={name:'Chief Bloodfiend',exit:false,required:true};
  var inPool=structuredClone(gp);inPool.current.target={name:'Ghostflame Dragon',exit:false};
`);
assert.equal(app.run("regions['Gravesite Plain · DLC'].bosses.includes('Chief Bloodfiend')"),false);
assert.equal(app.run("regions['Ancient Ruins of Rauh · DLC'].bosses.includes('Chief Bloodfiend')"),true);
assert.equal(app.run("regions['Gravesite Plain · DLC'].bosses.includes('Red Bear')"),false);
assert.equal(app.run("regions['Ancient Ruins of Rauh · DLC'].bosses.includes('Red Bear')"),true);
assert.ok(app.run('fixed&&!fixed.current.target.exit&&regions[gp.region].bosses.includes(fixed.current.target.name)'));
assert.equal(app.run('fixed.current.chase.name===gp.current.chase.name||weaponBlockedByTarget(gp.current.chase,fixed.current.target)'),true);
assert.equal(app.run('fixed.current.rite===gp.current.rite||JSON.stringify(fixed.current.rite)===JSON.stringify(gp.current.rite)'),true);
assert.equal(app.run('tcRepairOutOfPoolTarget(started)'),null);
assert.equal(app.run('tcRepairOutOfPoolTarget(capstone)'),null);
assert.equal(app.run('tcRepairOutOfPoolTarget(required)'),null);
assert.equal(app.run('tcRepairOutOfPoolTarget(inPool)'),null);
console.log('PASS tests/boss-pool-repair.cjs');
