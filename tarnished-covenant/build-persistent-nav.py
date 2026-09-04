from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

css=r'''
/* --- Persistent bottom navigation: measured viewport chrome, never screen content --- */
.tc-nav-anchor{display:none!important}
body.tc-run-active{min-height:var(--tc-vvh,100dvh)!important}
body.tc-run-active .app-shell{min-height:var(--tc-vvh,100dvh)!important}
body.tc-run-active:has(.tc-sanctuary-shell) .app-shell,
body.tc-run-active:has(.tc-encounter-shell) .app-shell{height:var(--tc-vvh,100dvh)!important;max-height:var(--tc-vvh,100dvh)!important;min-height:var(--tc-vvh,100dvh)!important}
body>.tc-bottom-nav.tc-persistent-nav{position:fixed!important;z-index:130!important;left:50%!important;right:auto!important;top:var(--tc-nav-top,auto)!important;bottom:auto!important;transform:translateX(-50%)!important;width:min(760px,100%)!important;animation:none!important}
body>.tc-bottom-nav.tc-persistent-nav[hidden]{display:none!important}
/* A fixed descendant of an animated/transformed screen becomes screen-relative
   in WebKit. The persistent bar is outside .tc-screen; keep screen entry motion
   visual-only so no future fixed descendants inherit that trap either. */
.tc-screen{animation:tcScreenFade .18s ease-out!important}
@keyframes tcScreenFade{from{opacity:.45}to{opacity:1}}
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Persistent bottom navigation lifecycle + measured iOS visual viewport --- */
let tcPersistentBottomNav=null;
let tcPersistentNavObserver=null;
let tcPersistentNavClickInstalled=false;
let tcViewportListenersInstalled=false;

function tcPersistentNavHtml(){
  return `<button data-screen="sanctuary"><span class="nicon">⌂</span><span>Site of Grace</span></button>
    <button data-screen="encounter"><span class="nicon">✦</span><span>Encounter</span></button>
    <button data-screen="ledger"><span class="nicon">▤</span><span>Ledger</span></button>
    <button data-screen="settings"><span class="nicon">⚙</span><span>Settings</span></button>`;
}

function tcEnsurePersistentNav(){
  if(tcPersistentBottomNav?.isConnected)return tcPersistentBottomNav;
  tcPersistentBottomNav=document.createElement('nav');
  tcPersistentBottomNav.className='tc-bottom-nav tc-persistent-nav';
  tcPersistentBottomNav.innerHTML=tcPersistentNavHtml();
  tcPersistentBottomNav.hidden=true;
  document.body.appendChild(tcPersistentBottomNav);
  return tcPersistentBottomNav;
}

/* iOS can report a stale CSS viewport until a long/scrollable screen forces a
   relayout. Do not let document length determine app geometry. Read the actual
   visual viewport in pixels and use that value for both the full-screen shell
   and the nav's top edge. A synchronous rect read forces the first layout now. */
function tcApplyVisualViewport(){
  if(!document.body.classList.contains('tc-run-active'))return;
  const vv=window.visualViewport;
  const viewportHeight=Math.max(1,Math.round(vv?.height||window.innerHeight||document.documentElement.clientHeight));
  const viewportTop=Math.round(vv?.offsetTop||0);
  document.documentElement.style.setProperty('--tc-vvh',`${viewportHeight}px`);
  const nav=tcEnsurePersistentNav();
  if(nav.hidden)return;
  const navHeight=Math.max(1,Math.round(nav.getBoundingClientRect().height));
  const navTop=Math.max(0,viewportTop+viewportHeight-navHeight);
  document.documentElement.style.setProperty('--tc-nav-top',`${navTop}px`);
  /* Force the shell to consume the same measurement before the next paint. */
  document.querySelector('.app-shell')?.getBoundingClientRect();
}

function tcInstallViewportListeners(){
  if(tcViewportListenersInstalled)return;
  tcViewportListenersInstalled=true;
  const refresh=()=>tcApplyVisualViewport();
  window.visualViewport?.addEventListener('resize',refresh,{passive:true});
  window.visualViewport?.addEventListener('scroll',refresh,{passive:true});
  window.addEventListener('resize',refresh,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(refresh,50),{passive:true});
  window.addEventListener('pageshow',()=>{
    refresh();
    requestAnimationFrame(refresh);
    setTimeout(refresh,80);
    setTimeout(refresh,260);
  });
}

function tcSyncPersistentNav(){
  const anchor=app.querySelector('.tc-nav-anchor');
  const nav=tcEnsurePersistentNav();
  if(!anchor){nav.hidden=true;return;}
  const active=anchor.dataset.tcNavActive||uiScreen||'sanctuary';
  nav.querySelectorAll('[data-screen]').forEach(btn=>btn.classList.toggle('active',btn.dataset.screen===active));
  nav.hidden=false;
  tcApplyVisualViewport();
}

/* Normal app screens render an invisible anchor instead of recreating the bar.
   MutationObserver hides the persistent chrome automatically on modal/transition
   screens that do not render an anchor. */
navMarkup=function(active){
  return `<span class="tc-nav-anchor" data-tc-nav-active="${h(active)}" aria-hidden="true"></span>`;
};

bindNav=function(){
  tcInstallViewportListeners();
  tcSyncPersistentNav();
  if(!tcPersistentNavClickInstalled){
    tcPersistentNavClickInstalled=true;
    document.addEventListener('click',event=>{
      const btn=event.target.closest?.('.tc-persistent-nav [data-screen]');
      if(!btn)return;
      if(tcTransitionIsLocked()){
        event.preventDefault();
        setToast('Finish the current Covenant notice first.');
        renderRun();
        return;
      }
      uiScreen=btn.dataset.screen;
      renderRun();
    });
  }
  if(!tcPersistentNavObserver){
    tcPersistentNavObserver=new MutationObserver(()=>queueMicrotask(tcSyncPersistentNav));
    tcPersistentNavObserver.observe(app,{childList:true,subtree:true});
  }
};

/* First-paint geometry must be explicit before any specialized run screen paints. */
const tcRenderRunBeforePersistentChrome=renderRun;
renderRun=function(){
  document.body.classList.add('tc-run-active');
  tcInstallViewportListeners();
  /* Seed the viewport variable before screen markup is replaced. */
  const vv=window.visualViewport;
  const firstHeight=Math.max(1,Math.round(vv?.height||window.innerHeight||document.documentElement.clientHeight));
  document.documentElement.style.setProperty('--tc-vvh',`${firstHeight}px`);
  const result=tcRenderRunBeforePersistentChrome();
  tcSyncPersistentNav();
  /* iOS standalone can settle its visual viewport just after first paint. These
     remeasures are independent of navigation and replace the old Ledger side effect. */
  requestAnimationFrame(tcApplyVisualViewport);
  setTimeout(tcApplyVisualViewport,80);
  setTimeout(tcApplyVisualViewport,260);
  return result;
};

/* Leaving the run restores normal document safe-area behavior and removes chrome. */
const tcRenderHomeBeforePersistentChrome=renderHome;
renderHome=function(){
  document.body.classList.remove('tc-run-active');
  document.documentElement.style.removeProperty('--tc-vvh');
  document.documentElement.style.removeProperty('--tc-nav-top');
  if(tcPersistentBottomNav)tcPersistentBottomNav.hidden=true;
  return tcRenderHomeBeforePersistentChrome();
};

queueMicrotask(()=>{
  if(run){
    document.body.classList.add('tc-run-active');
    tcInstallViewportListeners();
    tcSyncPersistentNav();
  }
});
'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
    'tc-persistent-nav','tc-nav-anchor','tcPersistentNavObserver',
    'document.body.appendChild(tcPersistentBottomNav)','navMarkup=function(active)',
    "document.body.classList.add('tc-run-active')",'tcRenderRunBeforePersistentChrome',
    "document.body.classList.remove('tc-run-active')",'window.visualViewport',
    "--tc-vvh", "--tc-nav-top", 'tcApplyVisualViewport',
    "nav.querySelectorAll('[data-screen]').forEach"
]:
    if needle not in s: raise SystemExit('persistent nav invariant missing: '+needle)

p.write_text(s)
