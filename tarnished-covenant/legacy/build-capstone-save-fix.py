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
  const capstone=(state.history||[]).find(x=>x?.exit && x?.region===state.region)?.name || 'Regional capstone';
  const pathCards=choices.map((r,i)=>{
    const image=typeof actualRegionImage==='function'?actualRegionImage(r):'';
    const returnTrip=(state.clearedRegions||[]).includes(r);
    return `<button class="tc-crossroad-card" data-safe-travel="${h(r)}">
      <span class="tc-crossroad-art" style="background-image:linear-gradient(90deg,rgba(5,4,2,.18),rgba(5,4,2,.72)),url('${image}')"></span>
      <span class="tc-crossroad-copy"><span class="tc-crossroad-number">0${i+1}</span><span class="tc-crossroad-name">${h(r)}</span><span class="tc-crossroad-meta">${returnTrip?'Return to unfinished business':'Open this path'} <b>→</b></span></span>
    </button>`;
  }).join('');
  app.innerHTML=`<section class="tc-screen tc-safe-travel">${screenTop('Region Complete')}
    <div class="tc-victory-banner">
      <div class="tc-conquered">capstone felled</div>
      <div class="tc-travel-region">${h(state.region||'Region')}</div>
      <div class="tc-victory-mark"><span>✦</span></div>
      <div class="tc-victory-name">${h(capstone)}</div>
      <div class="tc-victory-copy">The road opens. Choose the Covenant’s next destination.</div>
    </div>
    <div class="tc-crossroads-head"><span>THE CROSSROADS</span><small>${choices.length} ${choices.length===1?'path':'paths'} available</small></div>
    <div class="tc-crossroads">${pathCards||`<div class="tc-panel"><div class="tc-muted">No path is available yet. Your victory is still saved.</div></div>`}</div>
    <div class="tc-victory-foot">
      <div><span>Battle record</span><strong>${done}</strong><small>victories</small></div>
      <button id="safeRefresh" class="tc-refresh-link">↻ Refresh app</button>
    </div>
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

old = "if(state.regionComplete) return renderRegionComplete();"
new = "if(state.regionComplete){try{return renderRegionComplete();}catch(error){console.error('Region Complete render failed:',error);return renderRegionCompleteSafe();}}"
if old not in s:
    raise SystemExit('regionComplete render hook missing')
s = s.replace(old, new, 1)

css = r'''
/* --- capstone victory / crossroads screen --- */
.tc-safe-travel{padding-bottom:92px}.tc-victory-banner{text-align:center;padding:14px 8px 20px;border-bottom:1px solid rgba(198,161,90,.24);background:radial-gradient(ellipse at 50% 25%,rgba(198,161,90,.10),transparent 68%)}
.tc-victory-banner .tc-conquered{font:850 11px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.19em;color:var(--gold);margin-bottom:8px}.tc-victory-banner .tc-travel-region{font-size:clamp(34px,9vw,48px);line-height:1.02;margin:0 auto;max-width:700px}.tc-victory-mark{width:68px;height:68px;border:1px solid rgba(198,161,90,.55);border-radius:50%;display:grid;place-items:center;margin:15px auto 12px;box-shadow:0 0 34px rgba(198,161,90,.08),inset 0 0 0 9px rgba(198,161,90,.025)}.tc-victory-mark span{font-size:28px;color:var(--gold-bright);text-shadow:0 0 18px rgba(224,193,123,.4)}.tc-victory-name{font-size:20px;line-height:1.2;color:var(--gold-bright);margin-top:2px}.tc-victory-copy{font-size:14px;line-height:1.45;color:var(--ash);font-style:italic;margin:6px auto 0;max-width:520px}
.tc-crossroads-head{display:flex;justify-content:space-between;align-items:end;gap:10px;margin:18px 3px 9px}.tc-crossroads-head span{font:850 11px/1.2 system-ui,sans-serif;letter-spacing:.16em;color:var(--gold)}.tc-crossroads-head small{font:12px/1.2 Georgia,serif;color:var(--ash);font-style:italic}.tc-crossroads{display:grid;gap:10px}.tc-crossroad-card{position:relative;min-height:104px;width:100%;overflow:hidden;border:1px solid rgba(198,161,90,.26);background:#0d0b08;color:var(--ink);text-align:left;padding:0;clip-path:polygon(10px 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,0 100%,0 10px)}.tc-crossroad-card:active{transform:scale(.992)}.tc-crossroad-art{position:absolute;inset:0;background-size:cover;background-position:center;opacity:.72}.tc-crossroad-card:after{content:"";position:absolute;inset:0;border-bottom:1px solid rgba(224,193,123,.18);pointer-events:none}.tc-crossroad-copy{position:relative;z-index:1;min-height:104px;display:grid;grid-template-columns:42px 1fr;grid-template-rows:auto auto;align-content:center;padding:15px 16px 14px}.tc-crossroad-number{grid-row:1/3;align-self:center;font:850 10px/1 system-ui,sans-serif;color:rgba(224,193,123,.55);letter-spacing:.08em}.tc-crossroad-name{font-size:clamp(24px,6.7vw,34px);line-height:1.05;text-shadow:0 2px 14px #000}.tc-crossroad-meta{font-size:13px;line-height:1.25;color:#c6bba5;font-style:italic;margin-top:5px}.tc-crossroad-meta b{color:var(--gold);font-style:normal;margin-left:4px}
.tc-victory-foot{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:17px;padding:13px 3px 3px;border-top:1px solid var(--line)}.tc-victory-foot>div{display:flex;align-items:baseline;gap:7px}.tc-victory-foot span{font:850 10px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;color:var(--ash)}.tc-victory-foot strong{font-size:25px;font-weight:400;color:var(--gold-bright)}.tc-victory-foot small{font-size:12px;color:var(--ash);font-style:italic}.tc-refresh-link{border:0;background:transparent;color:var(--ash);padding:10px 0;font:750 11px/1.2 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.08em}
@media(max-width:420px){.tc-safe-travel{padding-left:2px;padding-right:2px}.tc-victory-banner{padding-top:8px}.tc-crossroad-card,.tc-crossroad-copy{min-height:94px}.tc-crossroad-copy{grid-template-columns:34px 1fr;padding:12px 13px}.tc-crossroad-meta{font-size:12px}.tc-victory-foot{margin-top:13px}}
'''
s = s.replace('</style>', css + '\n</style>', 1)

for invariant in ["State saved, but rendering the next screen failed", 'function renderRegionCompleteSafe()', 'THE CROSSROADS', "try{return renderRegionComplete();}catch(error)"]:
    if invariant not in s:
        raise SystemExit('capstone invariant missing: '+invariant)

p.write_text(s)
