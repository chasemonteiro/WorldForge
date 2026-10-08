const assert=require('node:assert/strict');
const {runtime}=require('./runtime.cjs');
(async()=>{
 const app=runtime();
 app.run(`let s=initialRunState({region:'Altus Plateau + Leyndell',severity:'standard'});let original=structuredClone(s);let rejected=s.current.chase.name;s=changeWeapons(s,'Chase','chase',false);`);
 assert.notEqual(app.run('s.current.chase.name'),app.run('rejected'));
 app.run(`s=changeWeapons(s,'Morgan','morgan',false);`);
 assert.notEqual(app.run('s.current.morgan.name'),app.run('rejected'),'Partner does not draw appealed weapon');
 assert.equal(app.run('original.current.appealedWeaponNames?.length||0'),0,'Appeal leaves input unchanged');
 app.run(`let retired=[...s.current.appealedWeaponNames];let after=completeEncounter(s,'Chase');`);
 for(const slot of ['chase','morgan'])assert(!app.json('retired').includes(app.run(`after.current.${slot}.name`)),'Next boss respects shared appeal cooldown');
 app.run(`let later=completeEncounter(after,'Morgan');`);
 assert.deepEqual(app.json('later.appealWeaponCooldown'),[],'Cooldown expires after next encounter');
 assert(app.json(`tcLegalRegionWeapons(later,later.region,later.current.target).map(w=>w.name)`).includes("Celebrant's Sickle"),'Rare weapons remain in legal pool');
 // Every gate opens only after all modeled prerequisites are recorded, in all supported kill ledgers.
 app.run(`let gateChecks=0;for(const [name,requirements] of Object.entries(TC_WEAPON_ACQUISITION_GATES)){
   for(const ledger of ['history','sanctionedBossKills','appealPenaltyBossKills']){
     const state={[ledger]:[]};if(tcWeaponAcquisitionUnlocked(state,{name}))throw Error(name+' unlocked early');
     for(let i=0;i<requirements.length;i++){
       state[ledger].push({name:requirements[i].name,region:requirements[i].region});
       if(tcWeaponAcquisitionUnlocked(state,{name})!==(i===requirements.length-1))throw Error(name+' prerequisite mismatch');
     }gateChecks++;
   }
 }`);
 assert.equal(app.run('gateChecks'),297);
 // Use actual world-clear handler and commit logic with an in-memory revisioned backend.
 app.run(`renderRun=()=>{};setToast=()=>{};
 let server={id:'synthetic-room',joinCode:'TEST00',revision:1,state:initialRunState({region:'Limgrave + Stormveil',severity:'standard'})};
 run=structuredClone(server);session={runId:server.id,displayName:'Chase',joinCode:'TEST00'};
 backend={mode:'shared',async getRun(){return structuredClone(server)},subscribe(){return ()=>{}},async updateRun(id,revision,state){if(revision!==server.revision)return {success:false,...structuredClone(server)};server={...server,revision:revision+1,state:structuredClone(state)};return {success:true,...structuredClone(server)}}};`);
 await app.run(`tcRecordWorldClear('chase')`);
 assert.equal(app.run('tcBothWorldsCleared(run.state.current)'),false);
 const revision=app.run('run.revision');
 await app.run(`tcRecordWorldClear('chase')`);
 assert.equal(app.run('run.revision'),revision,'Double tap does not save twice');
 await app.run(`tcRecordWorldClear('morgan')`);
 assert.equal(app.run('tcBothWorldsCleared(run.state.current)'),true);
 app.run(`let encounterId=run.state.current.id;run.state.current.weirdness.favor=1;
 let report=tcBuildSharedBattleReportChoice(run.state,encounterId,'rite',true,'Chase');
 let completed=tcBuildSharedBattleReportCompletion(report,encounterId,'Chase');`);
 assert.equal(app.run('completed.state.history.length'),1);
 assert.equal(app.run("tcBuildSharedBattleReportCompletion(completed.state,encounterId,'Morgan')"),null,'Cannot file same victory twice');
 app.run(`let draw=completed.state.sharedRewardDraw;let payout=tcGenerateSharedRewardPayload(completed.state,draw.count);
 let claimed=tcBuildClaimedSharedReward(completed.state,draw,payout.rewards,payout.deltas,'Chase');`);
 assert.equal(app.run("tcBuildClaimedSharedReward(claimed,draw,payout.rewards,payout.deltas,'Morgan')"),null,'Second phone cannot claim payout twice');
 const before=app.json('claimed.smithing');
 app.run(`run.state=structuredClone(claimed);pendingRewardReveal=null;session.displayName='Morgan';tcHydrateSharedRewardReveal(run.state);`);
 assert.deepEqual(app.json('pendingRewardReveal.rewards'),app.json('payout.rewards'),'Reconnecting partner sees persisted rewards');
 assert.deepEqual(app.json('run.state.smithing'),before,'Hydrating reveal does not pay again');
 // Stale phone receives latest state and retries only its intended edit.
 app.run(`run=structuredClone(server);server.state.partnerMarker='must survive';server.revision++;
 let change=latest=>({...structuredClone(latest),myMarker:'saved'});`);
 assert.equal(await app.run('commit(change(run.state),{retryBuilder:change})'),true);
 assert.equal(app.run('server.state.partnerMarker'),'must survive');
 assert.equal(app.run('server.state.myMarker'),'saved');
 // Exercise the real Build saver, including its retry closure, for both players.
 app.loadBuild();
 app.run(`renderRun=()=>{};server.state=tcNormalizeRunState(server.state);run=structuredClone(server);
 let chaseDraft=testBuild.normalizeBuild({level:83,str:32,weapon:{weaponName:'Claymore',upgrade:12}});
 server.state.builds.morgan=testBuild.normalizeBuild({level:97,dex:45});server.revision++;`);
 assert.equal(await app.run(`testBuild.saveBuild({slot:'chase',draft:chaseDraft,automatic:true})`).then(()=>app.run('server.state.builds.chase.level')),83);
 assert.equal(app.run('server.state.builds.morgan.level'),97,'Partner build survives retry');
 assert.equal(app.run('server.state.builds.morgan.dex'),45);
 assert.equal(app.run('server.state.builds.chase.weapon.upgrade'),12);
 app.run(`run=structuredClone(server);server.state.builds.chase.str=40;server.revision++;`);
 await app.run(`testBuild.saveBuild({slot:'morgan',draft:testBuild.normalizeBuild({level:98,dex:46}),automatic:true})`);
 assert.equal(app.run('server.state.builds.chase.str'),40,'Other player build survives reverse retry');
 assert.equal(app.run('server.state.builds.morgan.dex'),46);
 // Exact session breadcrumb round-trip without deleting a remembered room.
 app.run(`saveSession({runId:'synthetic-room',joinCode:'TEST00',displayName:'Morgan'});let restored=loadSession();`);
 assert.equal(app.run('restored.runId'),'synthetic-room');
 assert.equal(app.run('restored.joinCode'),'TEST00');
 console.log('Offline journeys: appeals, cooldown, 276 gate paths, dual-world clears, duplicate payout, reconnect reveal, conflict retry, session recovery PASS');
})().catch(error=>{console.error(error);process.exitCode=1});
