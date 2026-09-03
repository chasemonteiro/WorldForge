from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# A successful backend save could be mislabeled as "Save failed" if the render
# immediately following it threw. Separate persistence from presentation and make
# the region-complete transition deliberately defensive.
old = """      if (result.success) {
        run = { ...run, state: result.state, revision: result.revision };
        renderRun();
        if (successToast) setToast(successToast);
        return true;
      }"""
new = """      if (result.success) {
        run = { ...run, state: result.state, revision: result.revision };
        try {
          renderRun();
        } catch (renderError) {
          console.error('State saved, but rendering the next screen failed:', renderError);
          // The save already succeeded. Never tell the player it failed. For a
          // capstone, fall back to a minimal travel screen that cannot depend on
          // the now-null current encounter.
          if (run.state?.regionComplete && !run.state?.runComplete) {
            renderRegionCompleteSafe();
          } else {
            setToast('Saved successfully. Refresh the app if this screen looks stuck.');
          }
        }
        if (successToast) setToast(successToast);
        return true;
      }"""
if old not in s:
    raise SystemExit('commit success block not found')
s = s.replace(old, new, 1)

marker = 'function renderRunComplete() {'
if marker not in s:
    raise SystemExit('renderRunComplete marker missing')
helper = r'''
function renderRegionCompleteSafe(){
  const state=run.state;
  const choices=(typeof availableNextRegions==='function'?availableNextRegions(state):[])||[];
  const done=(state.history||[]).length;
  app.innerHTML=`<section class="tc-screen tc-safe-travel">${screenTop('Region Complete')}
    <div class="tc-travel-hero"><div class="tc-conquered">region conquered</div><div class="tc-travel-region">${h(state.region||'Region')}</div><div class="tc-travel-sigil"></div></div>
    <div class="tc-safe-victory">Capstone victory recorded.</div>
    <div class="tc-muted tc-safe-copy">Your progress is saved. Choose where the Covenant goes next.</div>
    <div class="tc-kicker gold" style="text-align:center;margin:18px 0 10px">paths now open</div>
    <div class="tc-paths">${choices.length?choices.map(r=>`<button class="tc-path" data-safe-travel="${h(r)}"><span class="tc-path-copy"><span class="tc-path-name">${h(r)}</span><span class="tc-path-meta">Travel here next</span></span></button>`).join(''):`<div class="tc-panel"><div class="tc-muted">No path is available yet. Your victory is still saved.</div></div>`}</div>
    <div class="tc-panel" style="margin-top:16px"><div class="tc-kicker gold">battle record</div><div class="tc-value">${done} victories recorded</div></div>
    <button id="safeRefresh" class="btn ghost">Refresh App</button>
  </section>${navMarkup('sanctuary')}`;
  bindNav();
  document.querySelector('#safeRefresh')?.addEventListener('click',()=>location.reload());
  document.querySelectorAll('[data-safe-travel]').forEach(btn=>btn.addEventListener('click',()=>{
    try{
      const next=startNextRegion(state,playerName(),btn.dataset.safeTravel,state.severity);
      uiScreen='sanctuary';pendingRevealId=null;commit(next);
    }catch(error){console.error(error);setToast('Could not open that path. Refresh and try again.');}
  }));
}
'''
s = s.replace(marker, helper + '\n' + marker, 1)

# If the normal Region Complete renderer itself throws during startup/refresh,
# renderRun should still recover instead of dumping the player into a broken app.
old = "if(state.regionComplete) return renderRegionComplete();"
new = "if(state.regionComplete){try{return renderRegionComplete();}catch(error){console.error('Region Complete render failed:',error);return renderRegionCompleteSafe();}}"
if old not in s:
    raise SystemExit('regionComplete render hook missing')
s = s.replace(old, new, 1)

css = r'''
/* --- capstone save/transition recovery --- */
.tc-safe-travel{padding-bottom:92px}.tc-safe-victory{text-align:center;font:400 23px/1.15 Georgia,serif;color:var(--gold-bright);margin:8px 0}.tc-safe-copy{text-align:center;font-size:14px;line-height:1.45}.tc-safe-travel .tc-path{min-height:64px}.tc-safe-travel #safeRefresh{margin-top:12px}
'''
s = s.replace('</style>', css + '\n</style>', 1)

for invariant in ["State saved, but rendering the next screen failed", 'function renderRegionCompleteSafe()', 'Capstone victory recorded.', "try{return renderRegionComplete();}catch(error)"]:
    if invariant not in s:
        raise SystemExit('capstone invariant missing: '+invariant)

p.write_text(s)
