from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old = """  btn.addEventListener('click',()=>{
    if(data.spinning)return;
    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}
    pendingRewardReveal=null;renderRun();
  });"""

new = """  btn.addEventListener('click',()=>{
    if(data.spinning)return;
    if(data.index+1<total){
      data.index+=1;
      data.spinning=true;
      renderRewardMachine();
      return;
    }
    // Rewards were persisted before this reveal began, so the final Continue
    // only needs to dismiss the local reveal and route to the already-saved state.
    pendingRewardReveal=null;
    btn.disabled=true;
    try{
      const state=run?.state;
      if(state?.runComplete){
        uiScreen='sanctuary';
        return renderRunComplete();
      }
      if(state?.regionComplete){
        uiScreen='sanctuary';
        try{return renderRegionComplete();}
        catch(error){console.error('Reward handoff to Region Complete failed:',error);return renderRegionCompleteSafe();}
      }
      if(state?.current){
        uiScreen='encounter';
        return renderRun();
      }
      uiScreen='sanctuary';
      return renderRun();
    }catch(error){
      console.error('Reward handoff failed; reloading saved run:',error);
      window.location.reload();
    }
  });"""

if old not in s:
    raise SystemExit('reward Continue listener target missing')
s = s.replace(old, new, 1)

# Make sure the button remains a dependable touch target on iPhone.
css = r'''
/* --- reward Continue handoff hardening --- */
#tcRewardContinue{position:relative;z-index:3;touch-action:manipulation;min-height:54px}
#tcRewardContinue:not(:disabled){pointer-events:auto}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for invariant in ['Reward handoff failed; reloading saved run', 'renderRegionCompleteSafe()', '#tcRewardContinue{position:relative']:
    if invariant not in s:
        raise SystemExit('reward Continue invariant missing: ' + invariant)

p.write_text(s)
