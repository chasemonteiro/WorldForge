const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
(async()=>{
 const app=runtime();
 app.run(`let fixture=initialRunState({region:'Limgrave + Stormveil',severity:'standard'});
 fixture.smithing=smithingData(fixture);fixture.smithing.aviaryTickets=2;
 fixture.builds={chase:{level:83},morgan:{level:97}};fixture.extensionFromFuture={preserve:true};
 let original=structuredClone(fixture);let redeemed=tcBuildDynastyFlierRedemption(fixture,2,'redemption-1','Chase');`);
 assert.equal(app.run('redeemed.smithing.aviaryTickets'),1);
 assert.equal(app.run('redeemed.smithing.dynastyFlierRedemptions[0].visits'),5);
 assert.equal(app.run('redeemed.smithing.dynastyFlierRedemptions[0].redeemedBy'),'Chase');
 assert.deepEqual(app.json('fixture'),app.json('original'),'Builder does not mutate input');
 for(const key of ['current','region','history','cleared','clearedRegions','builds','extensionFromFuture']){
  assert.deepEqual(app.json(`redeemed.${key}`),app.json(`original.${key}`),key+' survives redemption');
 }
 assert.equal(app.run("tcBuildDynastyFlierRedemption(redeemed,1,'redemption-1','Morgan')"),null,'Operation cannot replay');
 assert.equal(app.run("tcBuildDynastyFlierRedemption(redeemed,2,'redemption-2','Morgan')"),null,'Stale confirmation cannot spend another ticket');
 app.run(`let second=tcBuildDynastyFlierRedemption(redeemed,1,'redemption-2','Morgan');`);
 assert.equal(app.run('second.smithing.aviaryTickets'),0);
 assert.equal(app.run('second.smithing.dynastyFlierRedemptions.length'),2);
 assert.equal(app.run("tcBuildDynastyFlierRedemption(second,0,'redemption-3','Chase')"),null);
 for(const value of [-1,0,0.5,NaN]){
  app.context.balance=value;
  assert.equal(app.run("tcBuildDynastyFlierRedemption({...fixture,smithing:{...fixture.smithing,aviaryTickets:balance}},balance,'invalid','Chase')"),null);
 }
 // Reward resolution cannot be interrupted; legacy saves start with no redemption log.
 assert.deepEqual(app.json('tcDynastyFlierRedemptions(original)'),[]);
 assert.equal(app.run("tcBuildDynastyFlierRedemption({...fixture,sharedRewardDraw:{id:'payout',count:1}},2,'blocked','Chase')"),null);
 app.run(`let copy=smithingCopy(redeemed);let normalized=tcNormalizeRunState(copy);`);
 assert.deepEqual(app.json('normalized.smithing.dynastyFlierRedemptions'),app.json('redeemed.smithing.dynastyFlierRedemptions'),'Log survives normalization');
 app.run(`let traveled=startNextRegion(redeemed,'Chase','Weeping Peninsula');`);
 assert.deepEqual(app.json('traveled.smithing.dynastyFlierRedemptions'),app.json('redeemed.smithing.dynastyFlierRedemptions'),'Redemption log survives region travel');
 assert.equal(app.run('traveled.smithing.aviaryTickets'),1,'Unspent ticket survives travel');
 const html=app.run('covenantBoonMarkup(fixture)');
 assert(html.includes('data-use-dynasty-flier'));
 assert(html.includes('Redeem Frequent Flier · 5 Bird Visits'));
 assert(app.run('covenantBoonMarkup(second)').includes('data-use-dynasty-flier disabled'));
 // Real commit retries safely when the partner already spent a ticket.
 app.run(`renderRun=()=>{};setToast=()=>{};
 let server={id:'synthetic-room',revision:1,state:structuredClone(fixture)};
 run=structuredClone(server);session={runId:server.id,displayName:'Chase'};
 backend={mode:'shared',async updateRun(id,revision,state){if(revision!==server.revision)return {success:false,...structuredClone(server)};server={...server,revision:revision+1,state:structuredClone(state)};return {success:true,...structuredClone(server)}}};
 server.state=tcBuildDynastyFlierRedemption(server.state,2,'partner-first','Morgan');server.revision++;`);
 assert.equal(await app.run("tcRedeemDynastyFlier(2,'stale-phone')"),false);
 assert.equal(app.run('server.state.smithing.aviaryTickets'),1);
 assert.equal(app.run('server.state.smithing.dynastyFlierRedemptions.length'),1);
 // Unrelated partner edits are preserved when the ticket balance still matches.
 app.run(`run=structuredClone(server);server.state.builds.morgan.level=99;server.revision++;`);
 assert.equal(await app.run("tcRedeemDynastyFlier(1,'next-ticket')"),true);
 assert.equal(app.run('server.state.builds.morgan.level'),99);
 assert.equal(app.run('server.state.smithing.aviaryTickets'),0);
 // A failed network save never consumes a ticket; the in-flight guard ignores double taps.
 app.run(`server.state=structuredClone(fixture);server.revision++;run=structuredClone(server);
 let resolveSave;backend.updateRun=()=>new Promise(resolve=>resolveSave=resolve);
 let firstSave=tcRedeemDynastyFlier(2,'double-tap');`);
 assert.equal(await app.run("tcRedeemDynastyFlier(2,'double-tap')"),false);
 app.run(`resolveSave({success:false,...structuredClone(server)});`);
 // Retry is also delayed: fail that request explicitly and verify no persisted spend.
 await new Promise(resolve=>setImmediate(resolve));
 app.run(`resolveSave({success:false,...structuredClone(server)});`);
 assert.equal(await app.run('firstSave'),false);
 assert.equal(app.run('server.state.smithing.aviaryTickets'),2);
 assert.equal(app.run('tcDynastyFlierBusy'),false);
 console.log('Dynasty redemption: five visits, shared balance, replay/double-tap protection, conflicts, failed saves, legacy state, UI PASS');
})().catch(error=>{console.error(error);process.exitCode=1});
