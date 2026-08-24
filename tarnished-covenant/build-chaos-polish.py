from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

css = r'''
/* --- Chaos reveal readability + motion polish --- */
.tc-chaos-event{
  isolation:isolate;
  min-height:calc(100svh - 28px);
  padding:34px 20px calc(34px + env(safe-area-inset-bottom));
  animation:tcChaosFadeIn .7s cubic-bezier(.22,.8,.24,1) both;
}
.tc-chaos-event:before{
  opacity:.42;
  animation:chaosTurn 42s linear infinite;
}
.tc-chaos-event:after{
  background:
    radial-gradient(circle at 50% 43%,rgba(172,40,28,.19),transparent 34%),
    linear-gradient(180deg,rgba(4,2,2,.16),rgba(4,2,2,.48));
}
.tc-chaos-title{
  animation:tcChaosRise .55s .18s cubic-bezier(.22,.8,.24,1) both;
  text-shadow:0 2px 14px #000;
}
.tc-chaos-seal{
  animation:tcChaosSealIn .8s .08s cubic-bezier(.2,.85,.25,1.08) both;
}
.tc-chaos-event-name{
  animation:tcChaosRise .62s .34s cubic-bezier(.22,.8,.24,1) both;
  line-height:1.02;
  max-width:620px;
  margin:14px auto 14px;
  text-wrap:balance;
  text-shadow:0 3px 22px rgba(0,0,0,.92),0 0 18px rgba(175,58,43,.14);
}
.tc-chaos-consequence{
  animation:tcChaosRise .65s .48s cubic-bezier(.22,.8,.24,1) both;
  max-width:560px;
  padding:16px 18px;
  border-top:1px solid rgba(224,122,104,.26);
  border-bottom:1px solid rgba(224,122,104,.18);
  background:linear-gradient(90deg,transparent,rgba(9,4,4,.72) 14%,rgba(9,4,4,.78) 86%,transparent);
  color:#f0dfd0;
  font-size:17px;
  line-height:1.52;
  letter-spacing:.005em;
  text-shadow:0 2px 8px #000;
}
.tc-chaos-quip{
  animation:tcChaosRise .55s .62s cubic-bezier(.22,.8,.24,1) both;
  color:#c89b8f;
  font-size:12px;
  line-height:1.45;
  text-shadow:0 2px 8px #000;
}
.tc-chaos-event .btn{
  animation:tcChaosRise .55s .73s cubic-bezier(.22,.8,.24,1) both;
  min-height:48px;
  font-size:10px;
}
@keyframes tcChaosFadeIn{
  from{opacity:0;background-color:#020101}
  to{opacity:1}
}
@keyframes tcChaosRise{
  from{opacity:0;transform:translateY(14px);filter:blur(2px)}
  to{opacity:1;transform:none;filter:none}
}
@keyframes tcChaosSealIn{
  0%{opacity:0;transform:scale(.82) rotate(-5deg);filter:blur(5px)}
  68%{opacity:1;transform:scale(1.025) rotate(.8deg);filter:none}
  100%{opacity:1;transform:scale(1) rotate(0);filter:none}
}
@media(max-width:480px){
  .tc-chaos-event{padding:26px 16px calc(28px + env(safe-area-inset-bottom))}
  .tc-chaos-event-name{font-size:clamp(33px,10vw,46px);margin-top:10px}
  .tc-chaos-consequence{font-size:16px;padding:14px 12px;line-height:1.48}
  .tc-chaos-seal{margin:18px auto 20px}
}
@media(prefers-reduced-motion:reduce){
  .tc-chaos-event,.tc-chaos-title,.tc-chaos-seal,.tc-chaos-event-name,.tc-chaos-consequence,.tc-chaos-quip,.tc-chaos-event .btn{animation:none!important}
  .tc-chaos-event:before{animation:none!important}
}
'''

if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)
p.write_text(s)
