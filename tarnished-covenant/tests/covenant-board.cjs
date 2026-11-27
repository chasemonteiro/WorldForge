// Bounty board: off unless chosen; three posts; picking sets the target and
// re-deals weapons; payout and region recording on completion; expiry.
const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();
app.loadBuild();
app.run(`
  var plain=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true});
  var b=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true,rules:{board:true}});
  var post=b.board.posts[0];
  var picked=tcBuildBountyPick(b,b.current.id,post.id,'Chase');
  var again=tcBuildBountyPick(picked,b.current.id,post.id,'Chase');
  var favorBefore=smithingData(picked).favor;
  var done=completeEncounter(picked,'Chase');
`);
assert.equal(app.run('plain.board===undefined&&!plain.current.bountyPending'),true,'no board unless chosen');
assert.equal(app.run('b.rules.board===true&&b.current.bountyPending===true'),true);
assert.equal(app.run('b.board.posts.length'),3,'three bounties posted');
assert.equal(app.run('new Set(b.board.posts.map(p=>p.name)).size'),3,'all different');
assert.equal(app.run('picked.current.target.name===post.name&&!picked.current.bountyPending'),true,'picking sets the fight');
assert.equal(app.run('picked.current.bounty.value>=1&&picked.board.posts.length===2'),true,'the post comes down');
assert.equal(app.run('again'),null,'a bounty is taken once');
assert.equal(app.run('done.history[0].bountyFavor===picked.current.bounty.value'),true,'the record keeps the payout');
assert.equal(app.run('smithingData(done).favor>=favorBefore+picked.current.bounty.value'),true,'Favor paid');
assert.equal(app.run('done.current.bountyPending===true&&done.board.posts.length===3'),true,'board refilled for the next fight');
assert.equal(app.run('done.board.posts.some(p=>p.name===post.name)'),false,'a felled boss is not re-posted');
// Waiting raises the pay; three fights later it expires.
app.run(`var s=structuredClone(b);var p0=s.board.posts[1];s.history=[{name:'x',region:s.region},{name:'y',region:s.region}];`);
assert.equal(app.run('tcBountyValue(s,p0)-tcBountyValue(b,p0)'),2,'two fights waiting adds 2');
app.run(`s.history.push({name:'z',region:s.region});tcRefreshBoard(s);`);
assert.equal(app.run('s.board.posts.some(p=>p.id===p0.id)'),false,'expired after three fights');
// A bounty from an earlier region is recorded under that region.
app.run(`var bt=structuredClone(picked);bt.current.bounty.region='Weeping Peninsula';var dbt=completeEncounter(bt,'Chase');`);
assert.equal(app.run("dbt.history[0].region==='Weeping Peninsula'&&dbt.history[0].backtrack===true"),true);
console.log('PASS tests/covenant-board.cjs');
