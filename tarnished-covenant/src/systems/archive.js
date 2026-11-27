/* --- Past Covenants (the archive) ---
   Beginning a new Covenant saves the old one first. On the shared backend the
   server copies its own copy of the run into public.run_archives in the same
   transaction that starts the new run (archive_and_restart_covenant_run); in
   local mode the run is copied into localStorage (TC_LOCAL_ARCHIVE_KEY) before
   it is replaced. Archived runs are read-only: they are opened, never resumed.
   The viewer reuses the Remembrances codex and Dossiers markup, which are pure
   functions of a state, on a normalized copy of the archived state. */
const TC_LOCAL_ARCHIVE_KEY='tarnished-covenant-archive-v1';
function tcArchiveSummary(state){
  if(!state)return {};
  const history=Array.isArray(state.history)?state.history:[];
  const times=history.map(x=>Date.parse(x?.completedAt)).filter(Number.isFinite);
  let req=[],done=0;
  try{req=requiredRemembrances(state);done=req.filter(n=>hasRemembrance(state,n)).length;}catch(_){}
  return {
    names:covenantNames(state),region:state.region||'',includeDlc:Boolean(state.includeDlc),severity:state.severity||'',
    fights:history.length,chaos:history.filter(x=>x?.chaosTriggered).length,rites:history.filter(x=>x?.riteOutcome==='Honored').length,
    masterworks:(()=>{try{return smithingData(state).masterworks.length;}catch(_){return 0;}})(),
    remembrances:[done,req.length],lastBoss:history[0]?.name||'',
    startedAt:times.length?new Date(Math.min(...times)).toISOString():(state.current?.createdAt||null),
    endedAt:new Date().toISOString()
  };
}
function tcLocalArchives(){try{const list=JSON.parse(localStorage.getItem(TC_LOCAL_ARCHIVE_KEY)||'[]');return Array.isArray(list)?list:[];}catch(_){return [];}}
function tcLocalArchivePush(oldRun){
  if(!oldRun?.state)return;
  const list=tcLocalArchives();
  list.unshift({id:crypto.randomUUID(),run_id:oldRun.id,archived_at:new Date().toISOString(),archived_revision:Number(oldRun.revision||0),summary:tcArchiveSummary(oldRun.state),state:oldRun.state});
  // localStorage throws when full; never let that block the restart's own save.
  try{localStorage.setItem(TC_LOCAL_ARCHIVE_KEY,JSON.stringify(list));}catch(error){console.warn('Local archive full',error);throw new Error('This phone is out of space to keep the old run. Download a backup in Settings first.');}
}
async function tcListArchives(){
  if(typeof backend?.listArchives!=='function')return [];
  return backend.listArchives(run?.id);
}
function tcArchiveDates(s){
  const f=v=>{const t=Date.parse(v);return Number.isFinite(t)?new Date(t).toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'}):'';};
  const a=f(s?.startedAt),b=f(s?.endedAt);return a&&b?`${a} – ${b}`:(b||a||'');
}
function tcArchiveLine(s){
  const parts=[s?.region?`Reached ${String(s.region).replace(/ · DLC$/,'')}`:'',`${s?.fights||0} ${s?.fights===1?'fight':'fights'}`,Array.isArray(s?.remembrances)?`${s.remembrances[0]} of ${s.remembrances[1]} remembrances`:''];
  return parts.filter(Boolean).join(' · ');
}
async function tcOpenArchiveList(){
  const sheet=tcSettingsSheet('Past Covenants','<p class="tc-set-p muted">Opening the archive…</p>');
  const body=sheet.el.querySelector('.tc-set-sheet-body');
  let list=[];
  try{list=await tcListArchives();}catch(error){console.warn(error);body.innerHTML='<p class="tc-set-p">The archive couldn’t be reached. Check your connection and try again.</p>';return;}
  if(!list.length){body.innerHTML=`<p class="tc-set-p">No past Covenants yet.</p><p class="tc-set-p muted">When you begin a new Covenant, this one is saved here first, with its remembrances and every case file.</p>${tcQuipSafe('The clerk has cleared a shelf.')}`;return;}
  body.innerHTML=`<div class="tc-past-list">${list.map(a=>`<button type="button" class="tc-set-row" data-archive-id="${h(a.id)}"><span><strong>${h(tcArchiveDates(a.summary)||'A past Covenant')}</strong><small>${h(tcArchiveLine(a.summary))}</small></span><em>Open</em></button>`).join('')}</div>`;
  body.querySelectorAll('[data-archive-id]').forEach(btn=>btn.addEventListener('click',async()=>{
    btn.disabled=true;const em=btn.querySelector('em');if(em)em.textContent='Opening…';
    try{const rec=await backend.getArchive(btn.dataset.archiveId);sheet.close();tcOpenArchiveView(rec);}
    catch(error){console.warn(error);if(em)em.textContent='Try again';btn.disabled=false;}
  }));
}
function tcQuipSafe(text){return typeof tcQuip==='function'?tcQuip(text):'';}
function tcOpenArchiveView(rec){
  if(!rec?.state)return setToast('That Covenant couldn’t be opened.');
  const state=tcNormalizeRunState(structuredClone(rec.state)),s=rec.summary&&Object.keys(rec.summary).length?rec.summary:tcArchiveSummary(state);
  document.querySelector('.tc-past-view')?.remove();
  const view=document.createElement('section');view.className='tc-past-view';view.setAttribute('role','dialog');view.setAttribute('aria-modal','true');
  const names=Array.isArray(s.names)?s.names:covenantNames(state);
  view.innerHTML=`<div class="tc-past-inner">
    <div class="tc-past-top"><button type="button" class="tc-pick-close" data-past-close aria-label="Close">✕</button><span>Past Covenant</span></div>
    <h2>${h(names[0]||'')} &amp; ${h(names[1]||'')}</h2>
    <p class="tc-past-dates">${h(tcArchiveDates(s))}</p>
    <div class="tc-dossier-tally"><span><b>${s.fights||0}</b>fights</span><span><b>${Array.isArray(s.remembrances)?s.remembrances[0]:0}</b>remembrances</span><span><b>${s.chaos||0}</b>Chaos</span><span><b>${s.masterworks||0}</b>Masterworks</span></div>
    <p class="tc-past-line">${h(tcArchiveLine(s))}${s.lastBoss?`. Last felled: ${h(s.lastBoss)}.`:''}</p>
    ${tcQuipSafe('Filed, sealed and shelved. The clerk does not lend these out.')}
    <div class="tc-ledger-tabs tc-past-tabs"><button type="button" class="active" data-past-tab="rem">Remembrances</button><button type="button" data-past-tab="dos">Dossiers</button></div>
    <div class="tc-past-body" data-past-pane="rem">${tcRemembranceCodexMarkup(state)}</div>
    <div class="tc-past-body" data-past-pane="dos" hidden>${compendiumLedgerMarkup(state)}</div>
  </div>`;
  document.body.appendChild(view);
  try{tcDossierFilter='all';tcApplyDossierFilter(view.querySelector('.tc-dossiers'));}catch(_){}
  view.querySelectorAll('[data-past-tab]').forEach(btn=>btn.addEventListener('click',()=>{
    view.querySelectorAll('[data-past-tab]').forEach(b=>b.classList.toggle('active',b===btn));
    view.querySelectorAll('[data-past-pane]').forEach(p=>{p.hidden=p.dataset.pastPane!==btn.dataset.pastTab;});
  }));
  view.querySelector('[data-past-close]').addEventListener('click',()=>view.remove());
}
/* --- End archive --- */
