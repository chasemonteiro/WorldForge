from pathlib import Path
import re

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Idempotent native-Grace visual tuning layer.
s=re.sub(r"\n?/\* --- Grace wisp tuning --- \*/.*?/\* --- End Grace wisp tuning --- \*/\n?", "\n", s, flags=re.S)

if 'const TC_GRACE_TAP_COOLDOWN_MS=400;' in s:
    s=s.replace('const TC_GRACE_TAP_COOLDOWN_MS=400;','const TC_GRACE_TAP_COOLDOWN_MS=100;',1)
elif 'const TC_GRACE_TAP_COOLDOWN_MS=100;' not in s:
    raise SystemExit('Grace tap cooldown marker missing')

new_markup=r'''function tcGraceNativeMarkup(){
  return `<span class="tc-grace-native-glow"></span>
  <svg class="tc-grace-native-svg" viewBox="0 0 220 150" aria-hidden="true" focusable="false">
    <ellipse class="tcg-pool outer" cx="110" cy="116" rx="58" ry="11"></ellipse>
    <ellipse class="tcg-pool middle" cx="110" cy="116" rx="45" ry="8"></ellipse>
    <ellipse class="tcg-pool inner" cx="110" cy="116" rx="30" ry="5"></ellipse>

    <path class="tcg-flame-body" d="M110 115 C99 103 101 91 107 79 C100 65 103 51 111 36 C119 51 120 65 114 79 C122 91 121 104 110 115 Z"></path>
    <path class="tcg-root root-left" d="M109 114 C99 112 88 114 77 120"></path>
    <path class="tcg-root root-right" d="M111 114 C122 111 134 114 146 120"></path>
    <path class="tcg-root root-curl" d="M109 113 C101 108 98 105 100 100"></path>

    <path class="tcg-wisp ribbon far-left" d="M108 114 C87 103 80 91 88 79 C95 68 87 59 79 53"></path>
    <path class="tcg-wisp left" d="M108 114 C94 102 91 90 98 78 C105 67 102 56 94 47"></path>
    <path class="tcg-wisp fine inner-left" d="M109 113 C101 97 108 89 105 77 C101 66 106 57 102 49"></path>
    <path class="tcg-wisp main" d="M110 114 C106 98 118 88 114 75 C109 62 116 53 113 42 C110 32 115 26 112 18"></path>
    <path class="tcg-wisp fine inner-right" d="M111 113 C120 99 113 90 117 78 C121 67 116 58 121 49"></path>
    <path class="tcg-wisp right" d="M112 114 C128 102 132 90 124 77 C118 67 122 57 132 47"></path>
    <path class="tcg-wisp ribbon far-right" d="M112 114 C135 104 142 92 135 80 C128 69 136 61 145 55"></path>
    <path class="tcg-wisp crown" d="M112 38 C102 33 103 26 110 22 C117 18 117 13 113 9"></path>
    <path class="tcg-wisp crown crown-side" d="M112 43 C122 37 124 29 119 24"></path>

    <circle class="tcg-core" cx="110" cy="115" r="3.4"></circle>
    <circle class="tcg-mote m1" cx="89" cy="96" r="1.6"></circle>
    <circle class="tcg-mote m2" cx="130" cy="91" r="1.25"></circle>
    <circle class="tcg-mote m3" cx="103" cy="82" r="1.15"></circle>
    <circle class="tcg-mote m4" cx="121" cy="104" r="1.4"></circle>
    <circle class="tcg-mote m5" cx="82" cy="108" r="1.05"></circle>
    <circle class="tcg-mote m6" cx="139" cy="101" r="1.1"></circle>
  </svg>
  <span class="tc-grace-idle-caption"></span>`;
}'''
pattern=r"function tcGraceNativeMarkup\(\)\{.*?\n\}"
if not re.search(pattern,s,flags=re.S):
    raise SystemExit('tcGraceNativeMarkup function missing')
s=re.sub(pattern,new_markup,s,count=1,flags=re.S)

css=r'''
/* --- Grace wisp tuning --- */
.tc-grace-native-svg .tcg-flame-body{
  fill:rgba(224,193,123,.065);stroke:rgba(239,211,146,.22);stroke-width:.8;
  transform-box:fill-box;transform-origin:center bottom;
  filter:drop-shadow(0 0 7px rgba(220,181,102,.18));
  animation:tcGraceFlameBody 2.7s ease-in-out infinite alternate;
}
.tc-grace-native-svg .tcg-root{
  fill:none;stroke:rgba(238,207,137,.52);stroke-width:1.05;stroke-linecap:round;
  filter:drop-shadow(0 0 4px rgba(210,171,92,.28));
  transform-box:fill-box;transform-origin:center;
}
.tc-grace-native-svg .root-left{animation:tcGraceRootLeft 2.4s ease-in-out infinite alternate}
.tc-grace-native-svg .root-right{animation:tcGraceRootRight 2.65s ease-in-out .35s infinite alternate}
.tc-grace-native-svg .root-curl{stroke:rgba(255,228,164,.58);animation:tcGraceRootCurl 1.9s ease-in-out .15s infinite alternate}
.tc-grace-native-svg .tcg-wisp.ribbon{stroke:rgba(207,168,91,.46);stroke-width:1.05}
.tc-grace-native-svg .tcg-wisp.far-left{animation:tcGraceRibbonLeft 3.15s ease-in-out .25s infinite alternate}
.tc-grace-native-svg .tcg-wisp.far-right{animation:tcGraceRibbonRight 2.95s ease-in-out .7s infinite alternate}
.tc-grace-native-svg .tcg-wisp.fine{stroke:rgba(255,226,157,.48);stroke-width:.82;filter:drop-shadow(0 0 2px rgba(255,226,154,.45))}
.tc-grace-native-svg .tcg-wisp.inner-left{animation:tcGraceFineLeft 2.1s ease-in-out .4s infinite alternate}
.tc-grace-native-svg .tcg-wisp.inner-right{animation:tcGraceFineRight 2.35s ease-in-out .15s infinite alternate}
.tc-grace-native-svg .tcg-wisp.crown-side{stroke:rgba(232,197,119,.48);stroke-width:.9;animation:tcGraceCrownSide 2.2s ease-in-out .5s infinite alternate}
.tc-grace-native-svg .m5{animation:tcGraceMoteB 3.7s linear 2.15s infinite}
.tc-grace-native-svg .m6{animation:tcGraceMoteA 3.05s linear 1.4s infinite}
@keyframes tcGraceFlameBody{from{opacity:.42;transform:scaleX(.9) scaleY(.97)}to{opacity:.76;transform:scaleX(1.08) scaleY(1.035)}}
@keyframes tcGraceRootLeft{from{opacity:.3;transform:translateX(2px) scaleX(.93)}to{opacity:.72;transform:translateX(-2px) scaleX(1.05)}}
@keyframes tcGraceRootRight{from{opacity:.28;transform:translateX(-2px) scaleX(.94)}to{opacity:.68;transform:translateX(2px) scaleX(1.06)}}
@keyframes tcGraceRootCurl{from{opacity:.28;transform:rotate(-2deg)}to{opacity:.8;transform:rotate(3deg)}}
@keyframes tcGraceRibbonLeft{from{opacity:.22;transform:rotate(-2.5deg) scaleY(.94)}to{opacity:.62;transform:rotate(3deg) scaleY(1.06)}}
@keyframes tcGraceRibbonRight{from{opacity:.2;transform:rotate(3deg) scaleY(.95)}to{opacity:.58;transform:rotate(-3deg) scaleY(1.055)}}
@keyframes tcGraceFineLeft{from{opacity:.25;transform:rotate(-1deg) scaleY(.95)}to{opacity:.68;transform:rotate(2.2deg) scaleY(1.05)}}
@keyframes tcGraceFineRight{from{opacity:.24;transform:rotate(1.5deg) scaleY(.96)}to{opacity:.65;transform:rotate(-2deg) scaleY(1.045)}}
@keyframes tcGraceCrownSide{from{opacity:.2;transform:rotate(2deg) scale(.95)}to{opacity:.6;transform:rotate(-3deg) scale(1.05)}}

/* --- Grace native scale --- */
.tc-grace-idle{flex-basis:148px;min-height:116px;max-height:205px}
.tc-grace-idle-button{width:min(276px,78vw);height:168px;padding-bottom:18px}
.tc-grace-native-svg{width:258px;height:162px;top:49.5%}
.tc-grace-native-glow{width:92%;height:80%;top:54%}
@media(max-height:740px){
  .tc-grace-idle{flex-basis:112px;min-height:92px;max-height:154px}
  .tc-grace-idle-button{height:126px;width:min(228px,66vw);padding-bottom:14px}
  .tc-grace-native-svg{width:210px;height:132px}
  .tc-grace-native-glow{width:88%;height:76%}
}
@media(max-height:650px){
  .tc-grace-idle{flex-basis:88px;min-height:72px;max-height:112px}
  .tc-grace-idle-button{height:98px;width:188px;padding-bottom:10px}
  .tc-grace-native-svg{width:170px;height:107px}
  .tc-grace-native-glow{width:84%;height:72%}
}
/* --- End Grace native scale --- */

/* --- End Grace wisp tuning --- */
'''
if '</style>' not in s: raise SystemExit('style marker missing')
s=s.replace('</style>',css+'\n</style>',1)

for needle in [
    'TC_GRACE_TAP_COOLDOWN_MS=100','tcg-flame-body','far-left','far-right','inner-left','inner-right',
    'root-left','root-right','Grace wisp tuning'
]:
    if needle not in s: raise SystemExit('Grace wisp tuning invariant missing: '+needle)
for retired in ['TC_GRACE_ART_FRAMES','tc-grace-idle-art-frame']:
    if retired in s: raise SystemExit('Retired image Grace residue: '+retired)

p.write_text(s)
