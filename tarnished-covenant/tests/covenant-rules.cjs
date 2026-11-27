// Covenant twists: off by default, kit and strikes only when chosen, and the
// third strike forces an Appeal through the normal builder. Synthetic states.
const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();
app.loadBuild();
app.run(`
  var plain=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true});
  var twisted=initialRunState({region:'Limgrave + Stormveil',severity:'cursed',includeDlc:true,rules:{kitRoll:true,strikes:true}});
  var c=twisted.current;
  var swapped=tcBuildKitSwap(twisted,c.id,'chase',0,'Chase');
  var s1=tcBuildStrike(twisted,c.id,'morgan',1,'Morgan');
  var s2=tcBuildStrike(s1,c.id,'morgan',1,'Morgan');
  var s3=tcBuildStrike(s2,c.id,'morgan',1,'Morgan');
  var undo=tcBuildStrike(s1,c.id,'morgan',-1,'Chase');
  var traveled=startNextRegion(twisted,'Chase','Weeping Peninsula');
  var done=completeEncounter(s2,'Chase');
`);
assert.equal(app.run('plain.rules===undefined&&!plain.current.kit&&!plain.current.strikes'),true,'no twists unless chosen');
assert.equal(app.run('twisted.rules.kitRoll&&twisted.rules.strikes'),true);
assert.equal(app.run('c.kit.chase.length===2&&c.kit.morgan.length===2'),true,'two talismans each');
assert.equal(app.run('tcTalismanFamily(c.kit.chase[0])!==tcTalismanFamily(c.kit.chase[1])'),true,'never two of one family');
assert.equal(app.run('swapped.current.kit.chase[0]!==c.kit.chase[0]&&swapped.current.kit.swaps===1'),true,'Don’t have it swaps one talisman');
assert.equal(app.run('swapped.current.chase.name===c.chase.name&&swapped.current.penances.length===0'),true,'a swap changes nothing else');
assert.equal(app.run('s2.current.strikes.morgan'),2);
assert.equal(app.run('s2.current.morgan.name===c.morgan.name'),true,'two deaths change nothing');
assert.equal(app.run('s3.current.morgan.name!==c.morgan.name'),true,'third death re-draws the weapon');
assert.equal(app.run('s3.current.penances.length'),1,'with an Appeal penalty');
assert.equal(app.run('s3.current.strikes.morgan===0&&s3.current.strikes.forced.length===1&&s3.current.strikes.totalMorgan===3'),true,'count starts again, total kept');
assert.equal(app.run('s3.current.chase.name===c.chase.name'),true,'partner keeps their weapon');
assert.equal(app.run('undo.current.strikes.morgan'),0,'undo takes a death back');
assert.equal(app.run('tcBuildStrike(twisted,"other-id","chase",1,"Chase")'),null,'stale encounter is refused');
assert.equal(app.run('traveled.rules.kitRoll&&Boolean(traveled.current.kit)'),true,'rules follow the run to the next region');
assert.equal(app.run('done.history[0].deaths.morgan===2&&done.history[0].kit.chase.length===2'),true,'the record keeps kit and deaths');
console.log('PASS tests/covenant-rules.cjs');
