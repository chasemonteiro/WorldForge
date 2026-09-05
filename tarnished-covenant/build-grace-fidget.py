from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent native-Grace fidget layer: livelier wisps + local per-encounter tap counter.
s=re.sub(r"\n?/\* --- Grace fidget tuning --- \*/.*?/\* --- End Grace fidget tuning --- \*/\n?", "\n", s, flags=re.S)
s=re.sub(r"\n?/\* --- Grace tap counter behavior --- \*/.*?/\* --- End Grace tap counter behavior --- \*/\n?", "\n", s, flags=re.S)

if 'TC_GRACE_TAP_COOLDOWN_MS=100' not in s:
    raise SystemExit('100ms Grace tap cadence missing')
if 'tc-grace-native-svg' not in s:
    raise SystemExit('Native Grace markup missing')

# Keep reruns clean, then count only taps that make it through the 100ms acceptance gate.
s=s.replace('tcGraceLastTapAt=now;tcGraceTapPulse(btn);tcIncrementGraceTapCounter(btn);',
            'tcGraceLastTapAt=now;tcGraceTapPulse(btn);')
needle='tcGraceLastTapAt=now;tcGraceTapPulse(btn);'
if needle not in s:
    raise SystemExit('Grace accepted-tap hook missing')
s=s.replace(needle, needle+'tcIncrementGraceTapCounter(btn);', 1)

# The wisp builder recreates this markup before this layer runs on a normal build.
if 'tc-grace-tap-count' not in s:
    caption=r'<span class=\"tc-grace-idle-caption\"></span>'
    if caption not in s:
        raise SystemExit('Grace caption markup missing')
    s=s.replace(caption, caption+r'<span class=\"tc-grace-tap-count\">${tcGraceTapCountLabel()}</span>', 1)

css=r'''
/* --- Grace fidget tuning --- */
.tc-grace-idle-caption{bottom:12px}
.tc-grace-tap-count{
  position:absolute;left:0;right:0;bottom:1px;text-align:center;pointer-events:none;
  font:700 5.9px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.145em;
  color:#625a4a;opacity:.78;font-variant-numeric:tabular-nums;
}
.tc-grace-idle-button.tc-tapped .tc-grace-tap-count{color:#9f895d;opacity:.95}

/* Let the individual strands wander on different clocks instead of breathing together. */
.tc-grace-native-svg .tcg-wisp.main{animation-duration:1.68s}
.tc-grace-native-svg .tcg-wisp.left{animation-duration:2.32s;animation-delay:.08s}
.tc-grace-native-svg .tcg-wisp.right{animation-duration:2.06s;animation-delay:.41s}
.tc-grace-native-svg .tcg-wisp.crown{animation-duration:1.47s}
.tc-grace-native-svg .tcg-wisp.far-left{animation-duration:2.72s;animation-delay:.18s}
.tc-grace-native-svg .tcg-wisp.far-right{animation-duration:3.08s;animation-delay:.63s}
.tc-grace-native-svg .tcg-wisp.inner-left{animation-duration:1.82s;animation-delay:.31s}
.tc-grace-native-svg .tcg-wisp.inner-right{animation-duration:2.17s;animation-delay:.04s}
.tc-grace-native-svg .tcg-wisp.crown-side{animation-duration:1.91s;animation-delay:.37s}

@keyframes tcGraceWispMain{
  0%{opacity:.72;transform:rotate(-4.3deg) translateX(-1.4px) scaleX(.96) scaleY(.94)}
  46%{opacity:1;transform:rotate(2.6deg) translateX(.8px) scaleX(1.025) scaleY(1.075)}
  100%{opacity:.84;transform:rotate(4.8deg) translateX(1.5px) scaleX(.985) scaleY(1.015)}
}
@keyframes tcGraceWispLeft{
  0%{opacity:.36;transform:rotate(-7deg) translateX(-2px) scaleY(.91)}
  53%{opacity:.86;transform:rotate(4.6deg) translateX(1px) scaleY(1.085)}
  100%{opacity:.58;transform:rotate(-1.5deg) translateX(-.5px) scaleY(.99)}
}
@keyframes tcGraceWispRight{
  0%{opacity:.34;transform:rotate(6.7deg) translateX(2px) scaleY(.92)}
  48%{opacity:.84;transform:rotate(-5deg) translateX(-1px) scaleY(1.09)}
  100%{opacity:.56;transform:rotate(1.2deg) translateX(.5px) scaleY(1.01)}
}
@keyframes tcGraceCrown{
  0%{opacity:.3;transform:rotate(-7deg) translateX(-1px) scale(.9)}
  50%{opacity:.82;transform:rotate(5.5deg) translateX(1px) scale(1.08)}
  100%{opacity:.5;transform:rotate(-1deg) scale(.98)}
}
@keyframes tcGraceRibbonLeft{
  0%{opacity:.18;transform:rotate(-7.2deg) translateX(-2.5px) scaleY(.89)}
  52%{opacity:.66;transform:rotate(6deg) translateX(1.6px) scaleY(1.105)}
  100%{opacity:.38;transform:rotate(-2.1deg) scaleY(.98)}
}
@keyframes tcGraceRibbonRight{
  0%{opacity:.17;transform:rotate(7deg) translateX(2.5px) scaleY(.9)}
  45%{opacity:.63;transform:rotate(-6.2deg) translateX(-1.7px) scaleY(1.1)}
  100%{opacity:.35;transform:rotate(2deg) scaleY(.99)}
}
@keyframes tcGraceFineLeft{
  0%{opacity:.2;transform:rotate(-4deg) translateX(-1px) scaleY(.9)}
  57%{opacity:.72;transform:rotate(4.8deg) translateX(.8px) scaleY(1.11)}
  100%{opacity:.42;transform:rotate(-1deg) scaleY(1)}
}
@keyframes tcGraceFineRight{
  0%{opacity:.2;transform:rotate(4.2deg) translateX(1px) scaleY(.91)}
  43%{opacity:.7;transform:rotate(-4.7deg) translateX(-.8px) scaleY(1.105)}
  100%{opacity:.4;transform:rotate(1.2deg) scaleY(1)}
}
@keyframes tcGraceCrownSide{
  0%{opacity:.16;transform:rotate(6deg) translateX(1px) scale(.91)}
  55%{opacity:.64;transform:rotate(-6.5deg) translateX(-1px) scale(1.09)}
  100%{opacity:.36;transform:rotate(1deg) scale(.98)}
}
@media(max-height:740px){
  .tc-grace-idle-caption{bottom:10px}
  .tc-grace-tap-count{font-size:5.45px;bottom:0}
}
@media(max-height:650px){
  .tc-grace-idle-caption{bottom:9px}
  .tc-grace-tap-count{font-size:5px;letter-spacing:.12em;bottom:0}
}
/* --- End Grace fidget tuning --- */
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

js=r'''
/* --- Grace tap counter behavior --- */
const tcGraceTapMemory=new Map();
let tcGraceTapPersistTimer=0;
function tcGraceTapStorageKey(){
  const encounterId=run?.state?.current?.id||'none';
  const runId=run?.id||run?.runId||run?.joinCode||run?.join_code||'local';
  return `tc-grace-taps:${runId}:${encounterId}`;
}
function tcReadGraceTapCount(){
  const key=tcGraceTapStorageKey();
  if(tcGraceTapMemory.has(key))return tcGraceTapMemory.get(key);
  let count=0;
  try{count=Math.max(0,Number(localStorage.getItem(key))||0);}catch(_){}
  tcGraceTapMemory.set(key,count);return count;
}
function tcGraceTapCountLabel(){return `TAPS ${tcReadGraceTapCount().toLocaleString()}`;}
function tcRenderGraceTapCount(btn,count=tcReadGraceTapCount()){
  const out=btn?.querySelector('.tc-grace-tap-count');
  if(out)out.textContent=`TAPS ${Number(count||0).toLocaleString()}`;
}
function tcIncrementGraceTapCounter(btn){
  const key=tcGraceTapStorageKey();
  const count=tcReadGraceTapCount()+1;
  tcGraceTapMemory.set(key,count);tcRenderGraceTapCount(btn,count);
  window.clearTimeout(tcGraceTapPersistTimer);
  tcGraceTapPersistTimer=window.setTimeout(()=>{try{localStorage.setItem(key,String(count));}catch(_){}},350);
}
/* --- End Grace tap counter behavior --- */
'''
idx=s.rfind('</script>')
if idx<0:
    raise SystemExit('script end marker missing')
s=s[:idx]+js+'\n'+s[idx:]

for needle in [
    'Grace fidget tuning','tc-grace-tap-count','tcIncrementGraceTapCounter(btn)',
    'tcGraceTapStorageKey','TAPS ${tcReadGraceTapCount().toLocaleString()}',
    'TC_GRACE_TAP_COOLDOWN_MS=100'
]:
    if needle not in s:
        raise SystemExit('Grace fidget invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame']:
    if retired in s:
        raise SystemExit('Retired image Grace residue: '+retired)

p.write_text(s)
