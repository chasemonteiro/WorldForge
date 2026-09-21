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
assert.deepEqual(counts,{favor:1200,favor2:400,chaos:1300,rite:1300,appeal:700,aviary:400,tax:500,freeboss:1000,veto:400,clemency:600,discount:500,blank:1000,joint:300,windfall:400});
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
