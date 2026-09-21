// Execute generated reward and Veto logic, not just source-string assertions.
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const html=fs.readFileSync('tarnished-covenant/index.html','utf8');
const ctx=vm.createContext({structuredClone,Math:Object.create(Math),Date,
 smithingData:s=>s.smithing||{},smithingCopy:structuredClone,
 pick:a=>a[0],TC_COVENANT_TAXES:[{label:'Tax',detail:'Tax'}],
 tcIsProgressionGateBoss:n=>n==='Required'});
for(const name of ['drawCovenantReward','tcBossVetoEligible','tcBossVetoAffordable','tcBuildBossVeto']){
 const match=html.match(new RegExp('function '+name+'\\([^]*?\\n\\}'));
 assert.ok(match,name); vm.runInContext(match[0],ctx);
}
const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills','bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals'];
const counts={};
for(let i=0;i<10000;i++){
 ctx.Math.random=()=> (i+.5)/10000;
 const state={smithing:Object.fromEntries(keys.map(k=>[k,0]))};
 const kind=ctx.drawCovenantReward(state).kind; counts[kind]=(counts[kind]||0)+1;
}
assert.deepEqual(counts,{favor:1200,favor2:400,chaos:1300,rite:1300,appeal:700,aviary:1000,tax:500,freeboss:1000,veto:400,clemency:600,discount:100,blank:1000,joint:300,windfall:200});
assert.ok(html.includes('const TC_ERDTREE_WRIT_CHANCE=0.07;'));
const state={smithing:{bossVetoes:1,favor:2,chaosRefreshes:1,riteRefreshes:1,appealWaivers:0},current:{id:'e',target:{name:'Old'},worldClears:[]}};
const spend=(s,kind)=>ctx.tcBuildBossVeto(s,'e','Old',{name:'New'},'Player',kind);
for(const kind of ['chaos','rite']){
 const original=JSON.stringify(state),result=spend(state,kind);
 assert.equal(result.smithing.bossVetoes,0);assert.equal(result.smithing.favor,0);
 assert.equal(result.smithing.chaosRefreshes,kind==='chaos'?0:1);
 assert.equal(result.smithing.riteRefreshes,kind==='rite'?0:1);
 assert.equal(result.smithing.appealWaivers,0);assert.equal(JSON.stringify(state),original);
 const only=structuredClone(state);only.smithing[kind==='chaos'?'riteRefreshes':'chaosRefreshes']=0;assert.ok(spend(only,kind));
}
for(const [key,value] of [['favor',1],['bossVetoes',0],['chaosRefreshes',0]]){
 const stale=structuredClone(state);stale.smithing[key]=value;assert.equal(spend(stale,'chaos'),null);
}
assert.equal(spend(state,'waiver'),null);
for(const change of [s=>s.current.id='stale',s=>s.current.target.name='Required',s=>s.current.worldClears=['chase'],s=>s.current.target.exit=true]){
 const invalid=structuredClone(state);change(invalid);assert.equal(spend(invalid,'chaos'),null);
}
for(const script of html.matchAll(/<script(?:\\s[^>]*)?>([^]*?)<\/script>/g)){
 if(script[1].trim()) new vm.Script(script[1]);
}
console.log('PASS: exact reward frequencies, selected-refresh spending, stale-state rejection, progression locks, and inline JavaScript syntax.');
vm.runInContext(html.match(/masterworkCurrent=function\(state,slot\)\{[^]*?\n\};/)[0],ctx);
ctx.tcMasterworkRecallId=()=>String(Math.random());
ctx.playerLabel=s=>s;ctx.setToast=()=>{};ctx.tcBothWorldsCleared=c=>c.worldClears.length===2;
vm.runInContext(html.match(/function tcBuildPostBattleMasterwork\([^]*?\n\}/)[0],ctx);
const mw={smithing:{masterworkCredits:2,masterworks:[],masterworkRecalls:[]},current:{id:'victory',worldClears:['chase','morgan'],chase:{name:'Sword',affinity:'Heavy'},morgan:{name:'Spear'}}};
const original=JSON.stringify(mw);
const both=ctx.tcBuildPostBattleMasterwork(mw,'victory',['chase','morgan'],['Sword','Spear']);
assert.equal(both.smithing.masterworkCredits,0);assert.equal(both.smithing.masterworkRecalls.length,2);
assert.equal(both.smithing.masterworkRecalls[0].build.affinity,'Heavy');
assert.equal(JSON.stringify(mw),original);
assert.equal(ctx.tcBuildPostBattleMasterwork(both,'victory',['chase','morgan'],['Sword','Spear']),null);
assert.equal(ctx.tcBuildPostBattleMasterwork(mw,'next',['chase'],['Sword']),null);
assert.equal(ctx.tcBuildPostBattleMasterwork(mw,'victory',['chase'],['Other']),null);
const poor=structuredClone(mw);poor.smithing.masterworkCredits=1;
assert.equal(ctx.tcBuildPostBattleMasterwork(poor,'victory',['chase','morgan'],['Sword','Spear']),null);
assert.ok(ctx.tcBuildPostBattleMasterwork(poor,'victory',['morgan'],['Spear']));
console.log('PASS: post-battle Masterwork single/both, exact builds, atomic credit spend and stale retries.');
for(const name of ['tcMasterworkSlotForIdentity','tcPastMasterworkWeapons','tcBuildPastMasterwork']){
 vm.runInContext(html.match(new RegExp('function '+name+'\\([^]*?\\n\\}'))[0],ctx);
}
const past={smithing:{masterworkCredits:1,masterworks:[],masterworkRecalls:[]},history:[{name:'Boss',chaseWeapon:'Sword',morganWeapon:'Spear'},{name:'Earlier',chaseWeapon:'Sword'}]};
assert.equal(ctx.tcPastMasterworkWeapons(past,'chase').length,1);
const archived=ctx.tcBuildPastMasterwork(past,'chase','Sword','Chase');
assert.equal(archived.smithing.masterworkCredits,0);
assert.equal(archived.smithing.masterworkRecalls[0].build.name,'Sword');
assert.equal(Object.keys(archived.smithing.masterworkRecalls[0].build).length,1);
assert.equal(past.smithing.masterworkCredits,1);
assert.equal(ctx.tcBuildPastMasterwork(archived,'chase','Sword','Chase'),null);
assert.equal(ctx.tcBuildPastMasterwork(past,'morgan','Spear','Chase'),null);
assert.equal(ctx.tcBuildPastMasterwork(past,'chase','Spear','Chase'),null);
assert.equal(ctx.tcBuildPastMasterwork(past,'chase','Unused','Chase'),null);
console.log('PASS: past Masterworks enforce ownership, completed history, one credit, deduplication and stale-spend rejection.');
