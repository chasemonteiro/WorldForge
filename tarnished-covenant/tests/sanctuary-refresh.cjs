// Grace and Progress panels read the run without changing it.
const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
const app=runtime();
app.run(`
  var st=initialRunState({region:'Scadu Altus + Shadow Keep · DLC',severity:'standard',includeDlc:true});
  st.clearedRegions=['Limgrave + Stormveil'];
  st.history=[{name:'Godrick the Grafted',region:'Limgrave + Stormveil',completedAt:'2026-09-12T00:00:00Z',chaosTriggered:true,riteOutcome:'Honored'}];
  var before=JSON.stringify(st);
  var card=tcGraceNextCard(st),road=tcJourneyMarkup(st),ring=tcRuneRingMarkup(st),facts=tcRunFacts(st).join(' ');
`);
assert.ok(app.run('card.includes(st.current.target.name)&&card.includes(st.current.chase.name)'));
assert.equal(app.run("(road.match(/tc-road-stop here/g)||[]).length"),1,'exactly one current stop');
assert.ok(app.run("road.includes('tc-road-stop done')"),'cleared regions are marked');
assert.ok(app.run("ring.includes('tc-rune-mark got')"),'claimed remembrances light a rune');
assert.ok(app.run("facts.includes('<strong>1</strong> fight won')"));
assert.equal(app.run('JSON.stringify(st)===before'),true,'rendering never mutates the run');
console.log('PASS tests/sanctuary-refresh.cjs');
