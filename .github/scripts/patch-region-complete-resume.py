from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
tc = root / 'tarnished-covenant'

old = '''renderRun=function(){
  document.querySelector('#tcAppealOverlay')?.remove();
  if(run?.state)run.state=tcNormalizeRunState(run.state);
  const transition=tcBlockingTransition(run?.state);
  if(transition==='corporate')return renderCorporateContractNotice();
  return tcRenderRunBeforeHardening();
};'''
new = '''renderRun=function(){
  document.querySelector('#tcAppealOverlay')?.remove();
  /* Region-complete recovery must bypass the older wrapper chain entirely.
     This state is already authoritative in Supabase; do not let transient
     reward/UI wrappers prevent the player from choosing the next region. */
  if(run?.state?.regionComplete && !pendingRewardReveal?.rewards?.length && !postBattleReport){
    return renderRegionCompleteSafe();
  }
  if(run?.state)run.state=tcNormalizeRunState(run.state);
  const transition=tcBlockingTransition(run?.state);
  if(transition==='corporate')return renderCorporateContractNotice();
  return tcRenderRunBeforeHardening();
};'''

# Patch deployed app.
p = tc / 'index.html'
s = p.read_text()
if old in s:
    s = s.replace(old, new, 1)
elif 'Region-complete recovery must bypass the older wrapper chain entirely.' not in s:
    raise SystemExit('index.html: hardening render wrapper target missing')
p.write_text(s)

# Patch maintenance owner so future full builds preserve the repair.
p = tc / 'build-regression-hardening.py'
s = p.read_text()
if old in s:
    s = s.replace(old, new, 1)
elif 'Region-complete recovery must bypass the older wrapper chain entirely.' not in s:
    raise SystemExit('build-regression-hardening.py: render wrapper target missing')
p.write_text(s)

for name in ['index.html','build-regression-hardening.py']:
    text=(tc/name).read_text()
    for needle in [
        'Region-complete recovery must bypass the older wrapper chain entirely.',
        'return renderRegionCompleteSafe();',
        'function tcRecoverRememberedRun',
    ]:
        if needle not in text:
            raise SystemExit(f'{name}: missing invariant: {needle}')
