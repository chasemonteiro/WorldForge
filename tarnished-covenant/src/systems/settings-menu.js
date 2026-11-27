/* --- Settings: an actual settings menu ---
   This phone (identity, screen awake, reduce motion, battery saver, text size),
   the Covenant (room code, player names, sync), the run (ruleset and difficulty
   explained, a rules reference), your data (download a backup), the app
   (version, refresh, what's new) and a danger zone (leave, restart).
   Phone preferences live in localStorage under TC_PREFS_KEY and never touch the
   shared run. The only shared writes here are renaming the players (a revision-
   checked commit) and the existing restart. Difficulty and ruleset stay fixed. */
const TC_PREFS_KEY='tc-phone-prefs-v1';
let tcPrefs=(()=>{try{return {still:false,battery:false,large:false,awake:false,quiet:false,...JSON.parse(localStorage.getItem(TC_PREFS_KEY)||'{}')};}catch(_){return {still:false,battery:false,large:false,awake:false};}})();
function tcSavePrefs(){try{localStorage.setItem(TC_PREFS_KEY,JSON.stringify(tcPrefs));}catch(_){}}
function tcApplyPrefs(){
  const root=document.documentElement;
  root.classList.toggle('tc-pref-still',Boolean(tcPrefs.still));
  root.classList.toggle('tc-pref-large',Boolean(tcPrefs.large));
  root.classList.toggle('tc-pref-battery',Boolean(tcPrefs.battery));
  root.classList.toggle('tc-pref-quiet',Boolean(tcPrefs.quiet));
  tcSyncAmbient();
  void tcUpdateWakeLock();
}
// Reduce motion: the app's own JS checks this media query (reel, lot, paging),
// so answer it for them; CSS is covered by html.tc-pref-still.
const tcMatchMediaReal=window.matchMedia?window.matchMedia.bind(window):null;
if(tcMatchMediaReal&&!window.__tcMatchMediaWrapped){
  window.__tcMatchMediaWrapped=true;
  window.matchMedia=function(query){
    if(tcPrefs.still&&/prefers-reduced-motion\s*:\s*reduce/.test(String(query)))return {matches:true,media:String(query),onchange:null,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){},dispatchEvent(){return false;}};
    return tcMatchMediaReal(query);
  };
}
// Battery saver: pause every endless (ambient) animation except the reel spin.
function tcSyncAmbient(){
  if(typeof document.getAnimations!=='function')return;
  for(const anim of document.getAnimations()){
    const timing=anim.effect?.getTiming?.(),target=anim.effect?.target;
    if(!timing||timing.iterations!==Infinity||target?.closest?.('.tc-slot-reel'))continue;
    if(tcPrefs.battery&&anim.playState==='running'){anim.pause();anim.__tcPrefPaused=true;}
    else if(!tcPrefs.battery&&anim.__tcPrefPaused){anim.__tcPrefPaused=false;anim.play();}
  }
}
setInterval(()=>{if(tcPrefs.battery&&document.visibilityState==='visible')tcSyncAmbient();},2500);
// Keep the screen awake while a fight is open.
let tcWakeLock=null;
const tcWakeSupported='wakeLock' in navigator;
function tcFightOpen(){return Boolean(run?.state&&(uiScreen==='encounter'||postBattleReport||pendingRewardReveal));}
async function tcUpdateWakeLock(){
  const want=tcWakeSupported&&tcPrefs.awake&&document.visibilityState==='visible'&&tcFightOpen();
  try{
    if(want&&!tcWakeLock){tcWakeLock=await navigator.wakeLock.request('screen');tcWakeLock.addEventListener('release',()=>{tcWakeLock=null;});}
    else if(!want&&tcWakeLock){const lock=tcWakeLock;tcWakeLock=null;await lock.release();}
  }catch(_){tcWakeLock=null;}
}
document.addEventListener('visibilitychange',()=>{void tcUpdateWakeLock();});
const tcRenderRunBeforePrefs=renderRun;
renderRun=function(){const out=tcRenderRunBeforePrefs.apply(this,arguments);void tcUpdateWakeLock();if(tcPrefs.battery)requestAnimationFrame(tcSyncAmbient);return out;};
try{tcApplyPrefs();}catch(error){console.warn('Phone preferences skipped',error);}

// Slide-up sheet (same look as the Build pickers).
function tcSettingsSheet(title,body){
  document.querySelector('.tc-pick-sheet-wrap')?.remove();
  const wrap=document.createElement('div');wrap.className='tc-pick-sheet-wrap';
  wrap.innerHTML=`<div class="tc-pick-sheet tc-set-sheet" role="dialog" aria-modal="true" aria-label="${h(title)}"><div class="tc-pick-head"><strong>${h(title)}</strong><button type="button" class="tc-pick-close" data-pick-close aria-label="Close">✕</button></div><div class="tc-set-sheet-body">${body}</div></div>`;
  document.body.appendChild(wrap);requestAnimationFrame(()=>wrap.classList.add('open'));
  const close=()=>{wrap.classList.remove('open');setTimeout(()=>wrap.remove(),260);};
  wrap.addEventListener('click',e=>{if(e.target===wrap||e.target.closest('[data-pick-close]'))close();});
  return {el:wrap,close};
}
const TC_DIFFICULTY={
  normal:['Silly','Chaos decrees grow harsher as the run goes on. Silly gives them no head start.'],
  hard:['Maidenless','Chaos decrees grow harsher as the run goes on. Maidenless gives them a small head start, so the nastier ones turn up a little sooner.'],
  cursed:['Miyazaki Has Noticed You','Chaos decrees grow harsher as the run goes on. Miyazaki Has Noticed You gives them the biggest head start, so mid- and late-run decrees turn up much sooner.']
};
const TC_VERSION='2.0';
const TC_WHATS_NEW=[
  ['Twists for a new Covenant','Kit roll (two talismans a fight), Strikes (a third death re-draws your weapon), Hostile draft (you pick your partner’s weapon) and Region bingo (5×5 cards that pay Favor).'],
  ['Bounty board','Pick your fight from three posted bounties, old regions included. They pay Favor, grow while they wait, and expire.'],
  ['Themes','Lore runs for five factions, or dealt characters that limit each of you to their weapon classes.'],
  ['Past Covenants','Beginning a new Covenant saves the old one first. Open it any time from Settings.'],
  ['Progress','The rune ring turns under your finger and tells you about each remembrance.'],
  ['Personality','Soapstone messages, Hewg’s grumbling and the clerk’s remarks. Switch them off in Settings if you like.'],
  ['Settings','A real settings menu: screen awake, reduce motion, battery saver, larger text, backups.'],
  ['Earlier in 2.0','New Build screen, sealed reward lots and the iron reel, the battle report, Encounter world seals, the Ledger’s Satchel, Dossiers and codex, and Hewg’s Forge and Surplus.']
];
function tcRulesMarkup(){
  const rows=[
    ['Each fight','A boss, a weapon for each of you, an Odd Rite and a Chaos trigger. Beat the boss in both worlds, then file the battle report.'],
    ['Odd Rite','Honor it during the fight and it pays reward draws when you file.'],
    ['Chaos','If the trigger happens, the decree breaks loose. Endure it to earn its reward draws. A Chaos Refresh rewrites a decree before it breaks.'],
    ['Appeals','Changing an assigned weapon adds a random penalty, unless you spend an Appeal Waiver. A Joint Appeal rerolls both weapons with no penalty, and a Letter of Clemency strikes one penalty.'],
    ['Favor and the Forge','Every filed fight pays +1 Smithing Favor, and some reward draws pay more. Spend it on Bell Bearing contracts; each one also earns a Masterwork credit. With every bearing home, Hewg’s Surplus opens.'],
    ['Masterworks','Spend a credit to save a weapon. You can Recall it once later, with no Appeal penalty.'],
    ['Rewards and taxes','Reward draws come from the Covenant treasury. A tax is a chore to pay in the game before the next fight.'],
    ['Skipping bosses','A Covenant Veto sends back a boss that isn’t required (2 Favor and a Refresh). A Sanctioned Boss Kill marks an optional boss as done. Skipping never re-rolls your weapons.'],
    ['Regions','Claim a region’s remembrances to move on. The final seal opens when every remembrance is claimed.']
  ];
  return `<div class="tc-rules">${rows.map(([t,d])=>`<div><strong>${h(t)}</strong><p>${h(d)}</p></div>`).join('')}</div>`;
}
function tcSettingsSyncLine(){
  if(backend?.mode!=='shared')return ['This phone only','Saved on this phone. Nothing to sync.'];
  const live=typeof tcRealtimeStatus!=='undefined'&&tcRealtimeStatus==='SUBSCRIBED';
  return [live?'Live':'Reconnecting…',`Revision ${Number(run?.revision||0)}. ${live?'Changes from the other phone arrive on their own.':'Changes will catch up when the connection returns.'}`];
}
function tcToggle(key,label,line,disabled){
  const on=Boolean(tcPrefs[key])&&!disabled;
  return `<button type="button" class="tc-set-row toggle" role="switch" aria-checked="${on}" data-pref="${key}" ${disabled?'disabled':''}><span><strong>${h(label)}</strong><small>${h(line)}</small></span><i class="tc-switch ${on?'on':''}" aria-hidden="true"></i></button>`;
}
renderSettings=function(){
  const state=run.state,names=covenantNames(state),me=typeof tcMasterworkSlotForIdentity==='function'?tcMasterworkSlotForIdentity():null;
  const myName=me?playerLabel(me,state):String(playerName());
  const diff=TC_DIFFICULTY[state.severity]||TC_DIFFICULTY.cursed;
  const [syncTitle,syncLine]=tcSettingsSyncLine();
  app.innerHTML=`<section class="tc-screen tc-settings-new">${screenTop('Settings')}
    <h4 class="tc-forge-h">This phone</h4>
    <div class="tc-set-group">
      <button type="button" class="tc-set-row" data-set="identity"><span><strong>Playing as ${h(myName)}</strong><small>Recall, reports and “your turn” checks go by this.</small></span><em>Switch</em></button>
      ${tcToggle('awake','Keep screen awake','While a fight is open, so the phone doesn’t lock mid-boss.'+(tcWakeSupported?'':' Not supported on this phone.'),!tcWakeSupported)}
      ${tcToggle('still','Reduce motion','Stops flames and embers; the reel lands at once.')}
      ${tcToggle('battery','Battery saver','Pauses background animation. The reel and seals still move.')}
      ${tcToggle('large','Larger text','Makes everything a little bigger.')}
      <button type="button" class="tc-set-row toggle" role="switch" aria-checked="${!tcPrefs.quiet}" data-pref="quiet" data-pref-inverse><span><strong>Covenant commentary</strong><small>Small asides from the clerk, Hewg and the soapstone.</small></span><i class="tc-switch ${tcPrefs.quiet?'':'on'}" aria-hidden="true"></i></button>
    </div>
    <h4 class="tc-forge-h">The Covenant</h4>
    <div class="tc-set-group">
      <div class="tc-set-code"><span>Room code</span><strong>${h(run.joinCode||'LOCAL')}</strong><div><button type="button" class="tc-satchel-act" data-set="copy">Copy</button><button type="button" id="share" class="tc-satchel-act">Share</button></div></div>
      <button type="button" class="tc-set-row" data-set="names"><span><strong>Player names</strong><small>${h(names[0])} and ${h(names[1])}</small></span><em>Rename</em></button>
      <button type="button" class="tc-set-row" data-set="sync"><span><strong>${h(syncTitle)}</strong><small>${h(syncLine)}</small></span><em>${backend?.mode==='shared'?'Sync now':''}</em></button>
    </div>
    <h4 class="tc-forge-h">The run</h4>
    <div class="tc-set-group">
      <button type="button" class="tc-set-row" data-set="ruleset"><span><strong>${state.includeDlc?'Base game + Shadow of the Erdtree':'Base game'}</strong><small>Every remembrance required. Set when the Covenant began.</small></span><em>About</em></button>
      <button type="button" class="tc-set-row" data-set="difficulty"><span><strong>${h(diff[0])}</strong><small>Difficulty. Set when the Covenant began.</small></span><em>About</em></button>
      <button type="button" class="tc-set-row" data-set="archive"><span><strong>Past Covenants</strong><small>Finished runs, with their remembrances and case files.</small></span><em>Open</em></button>
      <button type="button" class="tc-set-row" data-set="rules"><span><strong>How the Covenant works</strong><small>Appeals, Favor, Masterworks, Chaos, Rites and rewards.</small></span><em>Read</em></button>
    </div>
    <h4 class="tc-forge-h">Your data</h4>
    <div class="tc-set-group">
      <button type="button" class="tc-set-row" data-set="backup"><span><strong>Download a backup</strong><small>Saves the whole run as a file. Read-only; nothing changes.</small></span><em>Save</em></button>
    </div>
    <h4 class="tc-forge-h">App</h4>
    <div class="tc-set-group">
      <button type="button" class="tc-set-row" id="refreshApp"><span><strong>Version ${h(TC_VERSION)}</strong><small>Build ${h(typeof TC_BUILD_ID!=='undefined'?TC_BUILD_ID:'')}. Refresh to load the latest; you stay connected.</small></span><em>Refresh</em></button>
      <button type="button" class="tc-set-row" data-set="news"><span><strong>What’s new</strong><small>Version ${h(TC_VERSION)}: twists, bounties, themes and more.</small></span><em>Read</em></button>
    </div>
    <h4 class="tc-forge-h danger">Danger zone</h4>
    <div class="tc-set-group danger">
      <button type="button" class="tc-set-row" data-set="leave"><span><strong>Leave this run</strong><small>Back to the opening screen. The run itself is kept.</small></span></button>
      <button type="button" class="tc-set-row" data-set="restart"><span><strong>Begin a new Covenant</strong><small>This run is saved to Past Covenants, then a fresh run starts${backend?.mode==='shared'?' for both of you':''}.</small></span></button>
      <div id="restartConfirm"></div>
    </div>
    ${tcSettingsFooter(state)}
  </section>${navMarkup('settings')}`;
  bindNav();bindShare();
  document.querySelector('#refreshApp')?.addEventListener('click',()=>{const u=new URL(window.location.href);u.searchParams.set('_refresh',Date.now().toString());window.location.replace(u.toString());});
  app.querySelectorAll('[data-pref]').forEach(btn=>btn.addEventListener('click',()=>{
    const key=btn.dataset.pref;tcPrefs[key]=!tcPrefs[key];tcSavePrefs();tcApplyPrefs();
    const shown=btn.hasAttribute('data-pref-inverse')?!tcPrefs[key]:tcPrefs[key];
    btn.setAttribute('aria-checked',String(shown));btn.querySelector('.tc-switch')?.classList.toggle('on',shown);
  }));
  app.querySelectorAll('[data-set]').forEach(btn=>btn.addEventListener('click',()=>tcSettingsAction(btn.dataset.set,btn)));
};
function tcSettingsFooter(state){
  const times=(state.history||[]).map(x=>Date.parse(x?.completedAt)).filter(Number.isFinite);
  const start=times.length?Math.min(...times):Date.parse(state.current?.createdAt);
  const est=Number.isFinite(start)?new Date(start).toLocaleDateString(undefined,{month:'long',year:'numeric'}):'';
  return `<p class="tc-quip tc-set-footer">Tarnished Covenant ${h(TC_VERSION)}${est?` · est. ${h(est)}`:''} · no maidens were consulted</p>`;
}
async function tcRenamePlayers(one,two){
  const build=latest=>{if(!latest)return null;const next=structuredClone(latest);next.playerNames=[one,two];next.lastAction=`${playerName()} renamed the Tarnished.`;next.updatedAt=new Date().toISOString();return next;};
  const staged=build(run.state);if(!staged)return;
  await commit(staged,{retryBuilder:build,successToast:'Names saved.'});
}
async function tcDownloadBackup(){
  const payload={app:'Tarnished Covenant',build:typeof TC_BUILD_ID!=='undefined'?TC_BUILD_ID:'',exportedAt:new Date().toISOString(),joinCode:run?.joinCode||null,revision:run?.revision??null,state:run?.state};
  const name=`tarnished-covenant-${run?.joinCode||'local'}-${new Date().toISOString().slice(0,10)}.json`;
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
  try{
    const file=new File([blob],name,{type:'application/json'});
    if(navigator.canShare?.({files:[file]})){await navigator.share({files:[file],title:'Tarnished Covenant backup'});return;}
  }catch(error){if(error?.name==='AbortError')return;}
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),4000);
  setToast('Backup saved.');
}
function tcSettingsAction(kind){
  const state=run.state,names=covenantNames(state);
  if(kind==='identity'){
    const now=String(playerName()).toLowerCase()==='morgan'?'morgan':'chase',other=now==='chase'?'morgan':'chase',otherId=other==='chase'?'Chase':'Morgan';
    const s=tcSettingsSheet('Switch who this phone plays as?',`<p class="tc-set-p">This phone is ${h(playerLabel(now,state))}. Switch only if it was set up as the wrong person. If both phones play as the same Tarnished, Recall and the reward draw get confused.</p><button type="button" class="btn gold" data-confirm-identity>Play as ${h(playerLabel(other,state))}</button>`);
    s.el.querySelector('[data-confirm-identity]').addEventListener('click',()=>{session={...session,displayName:otherId};saveSession(session);s.close();setToast(`This phone now plays as ${playerLabel(other,state)}.`);renderRun();});
  }else if(kind==='copy'){
    const code=run.joinCode||'';
    (navigator.clipboard?.writeText(code)||Promise.reject()).then(()=>setToast('Room code copied.'),()=>setToast(`Room code: ${code}`));
  }else if(kind==='names'){
    const s=tcSettingsSheet('Player names',`<p class="tc-set-p">Names are labels only; nothing else changes. Both phones see the new names.</p><label class="tc-set-label" for="tcName1">First Tarnished</label><input id="tcName1" class="tc-pick-search" maxlength="32" value="${h(names[0])}"><label class="tc-set-label" for="tcName2">Second Tarnished</label><input id="tcName2" class="tc-pick-search" maxlength="32" value="${h(names[1])}"><button type="button" class="btn gold" data-save-names>Save names</button>`);
    s.el.querySelector('[data-save-names]').addEventListener('click',async e=>{
      const one=s.el.querySelector('#tcName1').value.trim(),two=s.el.querySelector('#tcName2').value.trim();
      if(!one||!two)return setToast('Name both Tarnished first.');
      if(one===names[0]&&two===names[1])return s.close();
      e.currentTarget.disabled=true;s.close();await tcRenamePlayers(one,two);
    });
  }else if(kind==='sync'){
    if(backend?.mode!=='shared')return;
    setToast(typeof tcWaitLine==='function'?tcWaitLine('Syncing…'):'Syncing…');
    Promise.resolve(typeof tcSyncAuthoritativeRun==='function'?tcSyncAuthoritativeRun('settings'):false).then(()=>{setToast('Up to date.');if(uiScreen==='settings')renderRun();});
  }else if(kind==='ruleset'){
    tcSettingsSheet(state.includeDlc?'Base game + Shadow of the Erdtree':'Base game',`<p class="tc-set-p">${state.includeDlc?'Every remembrance in the base game and in Shadow of the Erdtree is required, and the Realm of Shadow regions are in the draw.':'Every base-game remembrance is required. Shadow of the Erdtree regions are left out.'}</p><p class="tc-set-p muted">Chosen when the Covenant began. It stays fixed for the whole run.</p>`);
  }else if(kind==='difficulty'){
    const d=TC_DIFFICULTY[state.severity]||TC_DIFFICULTY.cursed;
    tcSettingsSheet(d[0],`<p class="tc-set-p">${h(d[1])}</p><p class="tc-set-p muted">Chosen when the Covenant began. It stays fixed so the run’s rules don’t move under you.</p>`);
  }else if(kind==='archive'){
    void tcOpenArchiveList();
  }else if(kind==='rules'){
    tcSettingsSheet('How the Covenant works',tcRulesMarkup());
  }else if(kind==='backup'){
    void tcDownloadBackup();
  }else if(kind==='news'){
    tcSettingsSheet('What’s new',`<div class="tc-rules">${TC_WHATS_NEW.map(([t,d])=>`<div><strong>${h(t)}</strong><p>${h(d)}</p></div>`).join('')}</div>`);
  }else if(kind==='leave'){
    const s=tcSettingsSheet('Leave this run?',`<p class="tc-set-p">You’ll go back to the opening screen. The run is kept${backend?.mode==='shared'?', and you can rejoin with the room code':''}.</p><button type="button" class="btn ghost" data-confirm-leave>Leave the run</button>`);
    s.el.querySelector('[data-confirm-leave]').addEventListener('click',()=>{s.close();unsubscribe?.();run=null;clearSession();session=null;renderHome();});
  }else if(kind==='restart'){
    const s=tcSettingsSheet('Begin a new Covenant?',`<p class="tc-set-p">This run is saved to Past Covenants, where you can open it any time. Then bosses, regions, Favor and the Satchel start fresh${backend?.mode==='shared'?' for both of you':''}. The saved run can be read but not resumed.</p><label class="tc-set-label" for="tcRestartWord">Type RESTART to continue</label><input id="tcRestartWord" class="tc-pick-search" autocomplete="off" autocapitalize="characters" spellcheck="false"><button type="button" class="btn curse" data-confirm-restart disabled>Continue</button>`);
    const input=s.el.querySelector('#tcRestartWord'),go=s.el.querySelector('[data-confirm-restart]');
    input.addEventListener('input',()=>{go.disabled=input.value.trim().toUpperCase()!=='RESTART';});
    go.addEventListener('click',()=>{s.close();showRestart();document.querySelector('#restartConfirm')?.scrollIntoView({block:'center',behavior:'smooth'});});
  }
}
/* --- End Settings --- */
