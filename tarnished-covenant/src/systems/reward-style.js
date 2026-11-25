/* --- Reward screens in the Ledger/Forge style ---
   Three screens, presentation only:
   - The waiting payout becomes a sealed lot. Tapping the wax seal cracks it and
     then runs the same claim (tcClaimSharedRewardDraw), so the first draw is
     still final and shared.
   - The slot machine keeps its reels, timing, sync and buttons. Its symbols are
     gold line-art, the winner glows, and the result reads like a Satchel card:
     what it is, how many you now hold, where it is used. Taxes are sealed red.
   - The New Decree shows its weapon pair as cards.
   Nothing here writes state. */
const TC_REWARD_SIGILS={
  favor:'<path d="M32 8l6 17h18l-14 11 5 18-15-11-15 11 5-18L8 25h18z"/>',
  tax:'<path d="M18 30c0-10 6-18 14-18s14 8 14 18c0 6-3 9-6 11v7H24v-7c-3-2-6-5-6-11z"/><circle cx="26" cy="30" r="3"/><circle cx="38" cy="30" r="3"/><path d="M29 48v-4M35 48v-4"/>',
  discount:'<circle cx="32" cy="32" r="20"/><circle cx="32" cy="32" r="14" opacity=".45"/><path d="M27 38l10-12M27 27h.5M37 37h.5"/>'
};
const TC_REWARD_SIGIL_FOR={favor:'favor',favor2:'favor',windfall:'favor',tax:'tax',discount:'discount',chaos:'chaos',rite:'rite',appeal:'appeal',clemency:'clemency',joint:'joint',freeboss:'freeboss',aviary:'flier',veto:'veto',blank:'blank',erdtree:'writ'};
const TC_REEL_GLYPHS={'✦':'favor','◉':'chaos','✧':'rite','⚖':'appeal','☠':'tax','◇':'blank'};
function tcRewardSigil(kind){
  const id=TC_REWARD_SIGIL_FOR[kind]||'favor';
  if(TC_REWARD_SIGILS[id])return `<svg class="tc-forge-sigil" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${TC_REWARD_SIGILS[id]}</g></svg>`;
  return typeof tcSatchelSigil==='function'?tcSatchelSigil(id):'';
}
// The reel winner and the result card both draw tcRewardIcon.
const tcRewardIconBeforeStyle=tcRewardIcon;
tcRewardIcon=function(kind){const svg=tcRewardSigil(kind);return svg?`<span class="tc-reel-sigil ${kind==='tax'?'tax':''}" aria-label="${h(String(tcRewardIconBeforeStyle(kind)))}">${svg}</span>`:tcRewardIconBeforeStyle(kind);};

const TC_REWARD_HOLD={
  favor:['favor','Spend it at Hewg’s Forge.'],favor2:['favor','Spend it at Hewg’s Forge.'],windfall:['favor','Spend it at Hewg’s Forge.'],
  chaos:['chaosRefreshes','Use it on the fight’s Chaos panel.'],rite:['riteRefreshes','Use it on the fight’s Rite panel.'],
  appeal:['appealWaivers','Offered when you appeal a weapon.'],aviary:['aviaryTickets','Redeem it from the Satchel.'],
  freeboss:['freeBossKills','Use it from the Satchel.'],veto:['bossVetoes','Use it from the Satchel.'],clemency:['clemencies','Use it from the Satchel.'],
  blank:['blankAmendments','Turn it into a Refresh from the Satchel.'],joint:['jointAppeals','Use it from the Satchel.'],erdtree:['erdtreeWrits','Use it from the Satchel.'],
  discount:['unionDiscounts','Taken off the next Bell Bearing contract by itself.']
};
function tcRewardHoldLine(state,kind){
  if(kind==='tax')return 'Pay it in the game before the next fight.';
  const entry=TC_REWARD_HOLD[kind];if(!entry)return '';
  const n=Number(smithingData(state)[entry[0]]||0);
  return `${entry[0]==='favor'?`${n} Favor in the purse now`:`You hold ${n} now`}. ${entry[1]}`;
}
function tcOpenRewardSatchel(){
  const state=run?.state;if(!state||typeof tcSatchelMarkup!=='function')return;
  const el=tcStrategicOverlay('Your Satchel',`<div class="tc-reward-satchel-view">${tcSatchelMarkup(state)}</div><p class="tc-reward-help">Spend these from Ledger → Satchel once the draw is done.</p>`,'');
  el.querySelector('.tc-kicker').textContent='Covenant Treasury';
  // Read-only while the draw is open: every Satchel button is a live spend hook.
  el.querySelectorAll('.tc-reward-satchel-view button').forEach(b=>b.remove());
  const close=el.querySelector('[data-close-strategy]');if(close)close.textContent='Back to the draw';
}
function tcDecorateRewardMachine(){
  const sec=app.querySelector('.tc-reward-machine');if(!sec||sec.dataset.tcStyled)return;
  sec.dataset.tcStyled='1';sec.classList.add('tc-reward-new');
  const title=sec.querySelector('.tc-reward-title'),m=(title?.textContent||'').match(/(\d+)\D+(\d+)/);
  if(title&&m)title.innerHTML=Number(m[2])>1?`Draw ${m[1]} <span>of ${m[2]}</span>`:'Your reward';
  sec.querySelectorAll('.tc-slot-reel span').forEach(span=>{const id=TC_REEL_GLYPHS[span.textContent.trim()];if(id)span.innerHTML=`<span class="tc-reel-sigil ${id==='tax'?'tax':''}">${tcRewardSigil(id==='flier'?'aviary':id)}</span>`;});
  const result=sec.querySelector('#tcRewardResult');if(!result)return;
  const name=result.querySelector('.tc-reward-name')?.textContent||'';
  const reward=(pendingRewardReveal?.rewards||[]).find(r=>r.label===name);
  const kind=reward?.kind||(result.classList.contains('tax')?'tax':'favor');
  const type=result.querySelector('.tc-reward-type');if(type)type.textContent=kind==='tax'?'A Covenant tax':'Into the Satchel';
  const hold=tcRewardHoldLine(run?.state,kind);
  result.querySelector('.tc-reward-detail')?.insertAdjacentHTML('afterend',`${hold?`<p class="tc-reward-hold">${h(hold)}</p>`:''}${kind==='tax'?'':'<button type="button" class="tc-reward-satchel" data-reward-satchel>See it in your Satchel</button>'}`);
  result.querySelector('[data-reward-satchel]')?.addEventListener('click',tcOpenRewardSatchel);
}
const tcRenderRewardMachineBeforeStyle=renderRewardMachine;
renderRewardMachine=function tcStyledRewardMachine(){
  const out=tcRenderRewardMachineBeforeStyle.apply(this,arguments);
  try{tcDecorateRewardMachine();}catch(error){console.warn('Reward style skipped',error);}
  return out;
};

// The sealed lot.
renderSharedRewardDraw=function(){
  const draw=run?.state?.sharedRewardDraw;
  if(!tcSharedRewardDrawPending(run?.state))return renderRun();
  const count=Math.max(1,Number(draw.count||1));
  app.innerHTML=`<section class="tc-shared-draw-screen tc-lot">
    <p class="tc-lot-kicker">Covenant Treasury</p>
    <h1>${count===1?'One sealed reward':`${count} sealed rewards`}</h1>
    <p class="tc-lot-boss">For the fall of ${h(draw.boss||'the enemy')}</p>
    <button type="button" id="tcOpenLot" class="tc-lot-envelope" aria-label="Break the seal and draw ${count===1?'the reward':`all ${count} rewards`}">
      <svg class="tc-lot-paper" viewBox="0 0 240 160" aria-hidden="true"><rect x="6" y="6" width="228" height="148" rx="4"/><path class="tc-lot-flap" d="M6 10l114 78 114-78"/><path d="M6 154l84-58M234 154l-84-58" opacity=".5"/></svg>
      <span class="tc-lot-wax"><span class="half l"></span><span class="half r"></span><span class="tc-lot-mark">${tcRewardSigil('favor')}</span></span>
    </button>
    <p class="tc-lot-hint">Tap the seal to break it.</p>
    <p class="tc-lot-note">Either of you can open it. The first opening is final and shows on both phones.</p>
  </section>${typeof navMarkup==='function'?navMarkup('encounter'):''}`;
  if(typeof bindNav==='function')bindNav();
  const btn=document.querySelector('#tcOpenLot');
  btn?.addEventListener('click',()=>{
    if(btn.dataset.opening||tcSharedRewardDrawBusy||pending)return;
    btn.dataset.opening='1';btn.classList.add('cracked');btn.disabled=true;
    const hint=document.querySelector('.tc-lot-hint');if(hint)hint.textContent=typeof tcWaitLine==='function'?tcWaitLine('Drawing…'):'Drawing…';
    const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
    window.setTimeout(()=>{void tcClaimSharedRewardDraw();},reduced?0:650);
  });
};

// New Decree: the weapon pair as cards.
const tcRenderDecreeRevealBeforeStyle=renderDecreeReveal;
renderDecreeReveal=function(){
  tcRenderDecreeRevealBeforeStyle();
  try{
    const state=run.state,c=state.current,wrap=app.querySelector('.tc-reveal-weapons');if(!wrap||!c)return;
    wrap.classList.add('tc-decree-weapons');
    wrap.innerHTML=['chase','morgan'].map(slot=>`<div class="tc-report-weapon"><span>${h(playerLabel(slot,state))}</span><strong>${h(c[slot]?.name||'—')}</strong><em>${h(c[slot]?.role||'')}</em></div>`).join('');
  }catch(error){console.warn('Decree style skipped',error);}
};
/* --- End reward style --- */
