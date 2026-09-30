from pathlib import Path
import re

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# 24 Chaos triggers: broad enough that a trigger feels unpredictable without becoming impossible to notice.
triggers = r'''const chaosTriggers = [
  'WHEN CHASE OR MORGAN DIES',
  'WHEN SOMEBODY DRINKS THE FIRST CRIMSON FLASK',
  'WHEN THE BOSS HITS PHASE TWO',
  'WHEN THE FIRST STANCE BREAK MAKES EVERYONE TOO CONFIDENT',
  'WHEN A STATUS EFFECT PROCS AND SOMEONE SAYS “NICE”',
  'AFTER THE FIRST WIPE. NATURALLY.',
  'WHEN SOMEONE GETS HIT BY THE SAME MOVE TWICE',
  'WHEN SOMEBODY PANIC ROLLS DIRECTLY INTO TROUBLE',
  'WHEN BOTH PLAYERS HEAL WITHIN FIVE SECONDS OF EACH OTHER',
  'WHEN SOMEBODY WHIFFS A JUMP ATTACK BY AN EMBARRASSING AMOUNT',
  'WHEN THE BOSS GRABS SOMEBODY',
  'WHEN ONE PLAYER HAS AGGRO FOR WAY TOO LONG',
  'WHEN SOMEBODY GETS KNOCKED FLAT ON THEIR ASS',
  'WHEN THE BOSS DROPS BELOW HALF HEALTH',
  'WHEN SOMEBODY RUNS COMPLETELY OUT OF STAMINA',
  'WHEN BOTH PLAYERS ARE BELOW HALF HEALTH AT THE SAME TIME',
  'WHEN SOMEONE GETS HIT WHILE DRINKING A FLASK',
  'WHEN A PROJECTILE MISSES BY A MILE',
  'WHEN SOMEBODY FALLS OFF SOMETHING THEY ABSOLUTELY SAW',
  'WHEN SOMEONE SAYS “I GOT THIS”',
  'WHEN THE BOSS CANCELS AN ATTACK INTO ANOTHER ATTACK BECAUSE OF COURSE IT DOES',
  'WHEN SOMEBODY ACCIDENTALLY EMOTES OR CROUCHES MID-FIGHT',
  'WHEN A SUMMON / INVADER / RANDOM ENEMY MAKES THE SITUATION WORSE',
  'WHEN THE FIGHT STARTS GOING SUSPICIOUSLY WELL'
];'''
s, n = re.subn(r"const chaosTriggers = \[.*?\];", triggers, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('chaosTriggers block not found')

# 50 consequences. Mostly disruptive, some mild, some awful, a few absurd.
consequences = [
'TALISMAN TAX: Chase and Morgan each lose one talisman slot until victory.',
'JUICE BUDGET: both players lose two voluntary Crimson Flask uses for the rest of this attempt.',
'L2 BUTTON BROKE: no weapon skills for the rest of this attempt.',
'NO HEALS YET: nobody heals until both players have damaged the boss again.',
'BRICK MODE: randomly choose Chase or Morgan. That person must Heavy Load on the next serious attempt.',
'THROWN ITEM CHECK: both players must land one thrown consumable before victory.',
'AGGRO SWAP: whoever currently has aggro must stop attacking until the boss changes targets.',
'PHASE TWO BUDGET CUT: after phase two begins, only one player may heal until somebody dies or the attempt ends.',
'CROUCH OF SHAME: both players must crouch for three full seconds before either can attack again.',
'NO LOCK-ON: both players turn off target lock for 20 seconds.',
'FIVE-SECOND PENALTY: the next player hit must stop attacking for five seconds.',
'LEFT SIDE ONLY: Chase may not use light attacks for 20 seconds. Heavy attacks, skills, and panic are legal.',
'RIGHT SIDE ONLY: Morgan may not use light attacks for 20 seconds. Figure it out.',
'DODGE EMBARGO: both players may not roll for the next 10 seconds. Sprinting and screaming remain available.',
'NO SPRINTING: both players may only walk or dodge for the next 15 seconds.',
'SOLO WINDOW: Chase must fight alone for 15 seconds while Morgan avoids dealing damage.',
'SOLO WINDOW: Morgan must fight alone for 15 seconds while Chase avoids dealing damage.',
'HEALING UNION: only Chase may use Crimson Flasks until the boss changes phase or somebody dies.',
'HEALING UNION: only Morgan may use Crimson Flasks until the boss changes phase or somebody dies.',
'SHARED CUP: the team gets three total Crimson Flask uses for the remainder of this attempt.',
'ONE AND DONE: each player gets exactly one more Crimson Flask use this attempt.',
'WEAPON SKILL QUOTA: somebody must land a weapon skill before either player may heal again.',
'HEAVY ATTACK QUOTA: both players must land one charged heavy before victory.',
'JUMP ATTACK AUDIT: each player must land one jump attack before using another Crimson Flask.',
'NO CRITS: no critical attacks after stance breaks for the rest of this attempt. Just stare at the glowing spot.',
'NO GREED: after landing three hits, a player must disengage until the other player lands a hit.',
'PASS THE BOSS: nobody may attack twice in a row. Alternate successful hits until someone gets hit.',
'PERSONAL SPACE: Chase and Morgan must stay on opposite sides of the boss for 20 seconds.',
'GROUP PROJECT: Chase and Morgan must stand near each other for 10 seconds while the boss remains active.',
'NO BLUE JUICE: no Cerulean Flasks for the rest of this attempt.',
'NO RED JUICE FOR CHASE: Chase may not use another Crimson Flask this attempt.',
'NO RED JUICE FOR MORGAN: Morgan may not use another Crimson Flask this attempt.',
'FASHION EMERGENCY: on the next attempt, both players remove their helmets until victory.',
'PANTS ARE A PRIVILEGE: randomly choose one player. They remove leg armor on the next attempt.',
'TALISMAN EVICTION: randomly choose one player. Remove all talismans on the next attempt.',
'TWO-HAND DEPARTMENT: randomly choose one player. They must two-hand their assigned weapon for the rest of this attempt.',
'NO TWO-HANDING: both players must one-hand their assigned weapons for 20 seconds.',
'CAMERA DEPARTMENT CLOSED: both players fight unlocked for 30 seconds.',
'BACK UP: both players must disengage to medium distance before attacking again.',
'GET IN THERE: both players must close to melee range before either may heal again.',
'CONSUMABLE MEETING: each player must use any non-flask consumable before victory.',
'GESTURE OF DOOM: at the next safe opening, one player must perform any gesture. The other must protect them.',
'PRATTling PATE EMERGENCY BROADCAST: use any Prattling Pate before the next attempt begins. Its message is legally binding.',
'WARMING STONE BUDGET MEETING: place a Warming Stone at the next safe opportunity. Someone has to actually use it.',
'CHAIR RULES: after the next wipe, both players must sit or crouch at the fog gate for five seconds before re-entering.',
'THE GAME DETECTED FUN: reroll both assigned weapons immediately. No appeal penalty this time; Chaos did it for free.',
'ABSOLUTELY NOTHING: Chaos has reviewed the situation and decided you are already suffering enough.',
'FREE DRINK: both players may immediately use one Crimson Flask without it counting against any existing Chaos flask restriction.',
'MORALE BOOST: no new restriction. Both players must say something encouraging and deeply unconvincing before continuing.',
'BOSS UNION BREAK: stop attacking for five seconds. Healing and repositioning are allowed. The boss has requested a meeting.'
]
if len(consequences) != 50:
    raise SystemExit(f'Expected 50 consequences, got {len(consequences)}')
cons_js = ',\n    '.join(repr(x) for x in consequences)
pattern = r"(function triggerChaos\(state, actor\) \{.*?const consequences = \[)(.*?)(\];\n  next\.current\.chaosTriggered)"
s, n = re.subn(pattern, lambda m: m.group(1) + '\n    ' + cons_js + '\n  ' + m.group(3), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('triggerChaos consequences block not found')

# Shared Chaos reveal: any phone that observes a newly-triggered encounter sees the event once per page session.
needle = "let pendingRevealId = null;"
if needle not in s:
    raise SystemExit('UI state marker missing')
s = s.replace(needle, needle + "\nconst acknowledgedChaos = new Set();", 1)

# Rename visible Sanctuary labels to Site of Grace while preserving internal screen id.
s = s.replace('<span>Sanctuary</span>', '<span>Site of Grace</span>')
s = s.replace("screenTop()}", "screenTop('Site of Grace')}", 1)

# A richer, original dark-fantasy theme. Inline SVG art keeps the app self-contained.
theme_css = r'''
/* --- Ornate theme pass --- */
:root{--gold:#c9a354;--gold-bright:#f0ce7d;--ink:#f2e8d2;--ash:#aa9e89;--red:#d35f50;--violet:#a88ac3;--line:#51442d;--line-soft:#2c261d}
body{background:
radial-gradient(circle at 50% -8%,rgba(202,160,73,.15),transparent 31%),
radial-gradient(circle at 8% 35%,var(--region-glow),transparent 35%),
linear-gradient(180deg,#0b0906,#050504 65%,#090704);}
body:after{content:"";position:fixed;inset:0;pointer-events:none;opacity:.18;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cg fill='none' stroke='%23c9a354' stroke-opacity='.11'%3E%3Ccircle cx='80' cy='80' r='30'/%3E%3Cpath d='M80 10v140M10 80h140M31 31l98 98M129 31l-98 98'/%3E%3Ccircle cx='80' cy='80' r='8'/%3E%3C/g%3E%3C/svg%3E");mix-blend-mode:screen}
.tc-screen{position:relative}.tc-screen:before{content:"";position:absolute;inset:-4px -5px auto;height:130px;pointer-events:none;background:radial-gradient(ellipse at 50% 0,rgba(201,163,84,.10),transparent 70%);z-index:-1}
.tc-topline{padding:8px 12px;border-bottom:1px solid transparent;border-image:linear-gradient(90deg,transparent,#5a4829,transparent) 1;margin-bottom:13px}.tc-brand-small{font-family:Georgia,serif;font-size:9px;font-weight:400;letter-spacing:.22em}.tc-sync{font-family:Georgia,serif;font-style:italic;text-transform:none;letter-spacing:.03em;font-weight:400}
.tc-title,.tc-brief-boss,.tc-travel-region,.tc-value,.tc-feature-title,.tc-loadout-name{font-family:Georgia,'Times New Roman',serif;text-shadow:0 1px 18px rgba(0,0,0,.45)}
.tc-title{letter-spacing:.015em}.tc-subtitle{position:relative;font-family:Georgia,serif;font-weight:400;letter-spacing:.22em}.tc-subtitle:before,.tc-subtitle:after{content:'✦';color:#735d32;margin:0 9px;font-size:7px}
.tc-kicker{font-family:Georgia,serif;font-weight:400;letter-spacing:.17em}.tc-kicker:before{content:'· ';opacity:.55}.tc-kicker:after{content:' ·';opacity:.55}
.tc-panel,.tc-loadouts,.tc-feature,.tc-path,.tc-sheet{position:relative;clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px),0 10px)}
.tc-panel:before,.tc-feature:before,.tc-loadouts:before{content:"";position:absolute;pointer-events:none;inset:4px;border:1px solid rgba(201,163,84,.08);clip-path:inherit}.tc-panel{background:linear-gradient(145deg,rgba(31,25,16,.88),rgba(10,8,6,.72));box-shadow:inset 0 0 28px rgba(180,132,54,.035),0 8px 26px rgba(0,0,0,.16)}
.tc-rune{width:128px;height:128px;margin:2px auto -84px;border-color:rgba(235,197,116,.28);box-shadow:0 0 48px rgba(210,161,63,.10),inset 0 0 35px rgba(210,161,63,.08)}
.tc-rune:before{inset:14px;transform:rotate(45deg);border-color:rgba(235,197,116,.30)}.tc-rune:after{inset:37px;border-color:rgba(235,197,116,.38);box-shadow:0 0 20px rgba(235,197,116,.08)}
.tc-grace-art,.tc-boss-art{height:150px;margin:9px 0 12px;overflow:hidden;border:1px solid rgba(201,163,84,.24);position:relative;clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%,0 14px)}
.tc-grace-art svg,.tc-boss-art svg{width:100%;height:100%;display:block}.tc-grace-art:after,.tc-boss-art:after{content:"";position:absolute;inset:0;box-shadow:inset 0 -45px 55px #070604,inset 0 0 28px rgba(0,0,0,.55)}
.tc-quick button{border-color:#4c3e27;background:radial-gradient(circle at 50% 15%,rgba(192,143,54,.10),transparent 48%),linear-gradient(#17120c,#0b0906);clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px),0 10px);box-shadow:inset 0 0 18px rgba(201,163,84,.03)}.tc-quick button:active{transform:translateY(1px);filter:brightness(1.18)}
.tc-bottom-nav{border-top:1px solid #4a3b24;background:linear-gradient(180deg,rgba(16,12,8,.78),rgba(5,5,4,.98) 32%);box-shadow:0 -10px 35px rgba(0,0,0,.38)}.tc-bottom-nav:before{content:'◆';position:absolute;top:-7px;left:50%;transform:translateX(-50%);font-size:9px;color:#7d6332;background:#080604;padding:0 7px}.tc-bottom-nav button{font-family:Georgia,serif;font-weight:400}.tc-bottom-nav .nicon{font-size:20px;text-shadow:0 0 12px currentColor}
.tc-brief-head{padding-bottom:5px}.tc-brief-boss{font-size:clamp(36px,10vw,52px)}
.tc-loadouts{border-color:#504329;background:linear-gradient(110deg,rgba(27,22,14,.88),rgba(8,7,5,.74))}.tc-loadout+.tc-loadout{border-left-color:#54452b}.tc-loadout-name{color:#f0dfbd}.tc-mini-stat b{font-family:Georgia,serif;font-weight:400;color:#887553}.tc-mini-stat{font-family:Georgia,serif}
.tc-feature{border-width:1px;box-shadow:inset 0 0 35px rgba(0,0,0,.20)}.tc-feature.chaos{border-color:rgba(218,86,68,.50);background:radial-gradient(circle at 8% 50%,rgba(163,42,30,.27),transparent 38%),linear-gradient(120deg,rgba(55,15,12,.72),rgba(17,8,7,.82))}.tc-feature.rite{border-color:rgba(173,133,201,.48);background:radial-gradient(circle at 8% 50%,rgba(107,65,140,.25),transparent 38%),linear-gradient(120deg,rgba(34,20,43,.78),rgba(13,9,16,.82))}.tc-feature-glyph{text-shadow:0 0 18px currentColor}.tc-seal-inline{border:1px solid rgba(211,95,80,.45);padding:8px 13px;margin-top:7px;clip-path:polygon(7px 0,calc(100% - 7px) 0,100% 7px,100% calc(100% - 7px),calc(100% - 7px) 100%,7px 100%,0 calc(100% - 7px),0 7px);background:rgba(91,20,14,.18)}
.btn{font-family:Georgia,serif;font-weight:400;letter-spacing:.11em;border-color:#514328;background:linear-gradient(180deg,rgba(26,21,14,.88),rgba(10,8,6,.90));box-shadow:inset 0 1px rgba(255,255,255,.03)}.btn.gold{background:linear-gradient(180deg,#e0bd70,#ae8139);border-color:#edcf88;box-shadow:0 6px 22px rgba(170,117,35,.12),inset 0 1px rgba(255,255,255,.26)}
.tc-path{min-height:92px;border-color:#5c4928;box-shadow:0 9px 22px rgba(0,0,0,.20)}.tc-path-copy{padding:18px 17px;background:linear-gradient(90deg,rgba(6,5,4,.93),rgba(6,5,4,.52) 67%,rgba(6,5,4,.05))}.tc-path-name{font-size:22px;text-shadow:0 1px 9px #000}.tc-path-meta{font-family:Georgia,serif}
.tc-settings-row{padding:15px 8px;border-bottom-color:#362d20}.tc-settings-row .name{font-family:Georgia,serif;font-weight:400;color:#bda878}.tc-settings-row .desc{color:#d6cbb6}
.tc-chaos-event{min-height:calc(100svh - 28px);display:grid;align-content:center;text-align:center;padding:22px 8px;position:relative;overflow:hidden}.tc-chaos-event:before{content:"";position:absolute;inset:-20%;background:repeating-conic-gradient(from 0deg,rgba(205,63,48,.13) 0deg 1deg,transparent 1deg 17deg);animation:chaosTurn 24s linear infinite;mask-image:radial-gradient(circle,#000 0 37%,transparent 72%);pointer-events:none}.tc-chaos-event:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 43%,rgba(172,40,28,.25),transparent 34%);pointer-events:none}@keyframes chaosTurn{to{transform:rotate(360deg)}}
.tc-chaos-title{font-family:Georgia,serif;color:#e07a68;letter-spacing:.2em;text-transform:uppercase;font-size:10px;position:relative;z-index:1}.tc-chaos-seal{width:190px;height:190px;border-radius:50%;margin:24px auto;position:relative;z-index:1;border:2px solid #8d2d25;background:radial-gradient(circle,#42120f 0 22%,#1b0908 23% 49%,transparent 50%),repeating-conic-gradient(#a43b2d 0 4deg,#35110d 4deg 17deg);box-shadow:0 0 0 7px rgba(114,27,21,.22),0 0 60px rgba(211,72,52,.25),inset 0 0 36px #000}.tc-chaos-seal:before,.tc-chaos-seal:after{content:"";position:absolute;left:50%;top:-22px;width:2px;height:234px;background:linear-gradient(transparent,#ff7b61 25%,#7e251e 52%,#ff7b61 74%,transparent);transform:rotate(22deg);box-shadow:0 0 9px #d84031}.tc-chaos-seal:after{transform:rotate(-48deg);opacity:.65}.tc-chaos-event-name{font-family:Georgia,serif;font-size:clamp(38px,11vw,56px);line-height:.96;color:#f0d7bd;position:relative;z-index:1;margin:8px 0 13px}.tc-chaos-consequence{position:relative;z-index:1;max-width:560px;margin:auto;color:#ddcbb8;font-size:16px;line-height:1.45}.tc-chaos-quip{position:relative;z-index:1;color:#a77e72;font-style:italic;font-size:11px;margin:18px auto;max-width:420px}.tc-chaos-event .btn{position:relative;z-index:1;max-width:480px;margin:3px auto 0;border-color:#7d2d24;color:#efaa9d;background:linear-gradient(#35120e,#160807)}
@media(max-width:420px){.tc-grace-art,.tc-boss-art{height:128px}.tc-chaos-seal{width:155px;height:155px}.tc-chaos-seal:before,.tc-chaos-seal:after{height:198px;top:-22px}}
'''
s = s.replace('</style>', theme_css + '\n</style>', 1)

# Themed original inline art helpers and Chaos event rendering.
helpers = r'''
function thematicRegionArt(name, mode='region') {
  const n=(name||'').toLowerCase();
  let sky='#403a30',far='#25231e',near='#12110e',sun='#c59d51';
  if(n.includes('caelid')){sky='#5c251e';far='#331817';near='#160d0b';sun='#d05c3c'}
  else if(n.includes('liurnia')){sky='#2d4654';far='#1d303a';near='#10191e';sun='#80a8bb'}
  else if(n.includes('weeping')){sky='#39473e';far='#27332a';near='#111813';sun='#8a9d7f'}
  else if(n.includes('gelmir')||n.includes('jagged')){sky='#5e2f1e';far='#331d16';near='#160c09';sun='#d27744'}
  else if(n.includes('mountain')||n.includes('haligtree')){sky='#687276';far='#43494a';near='#1c2020';sun='#dad2a8'}
  else if(n.includes('leyndell')||n.includes('altus')){sky='#645433';far='#3b3120';near='#1c170f';sun='#e2ba62'}
  else if(n.includes('coast')){sky='#315764';far='#213944';near='#10191e';sun='#76a9b6'}
  else if(n.includes('abyss')){sky='#463a2b';far='#2a251d';near='#11100d';sun='#b18d51'}
  else if(n.includes('shadow')||n.includes('gravesite')){sky='#403c34';far='#29261f';near='#11100e';sun='#9d865e'}
  else if(n.includes('rauh')){sky='#405541';far='#29372b';near='#111813';sun='#8fa273'}
  const grace = mode==='grace' ? `<path d="M300 79 C294 61 303 51 300 32 C309 47 310 58 306 76" stroke="${sun}" stroke-width="3" fill="none"/><ellipse cx="302" cy="82" rx="35" ry="5" fill="${sun}" opacity=".34"/><circle cx="303" cy="58" r="8" fill="${sun}" opacity=".18"/>` : '';
  const boss = mode==='boss' ? `<path d="M302 88c-24-9-29-34-16-48 11-12 35-10 44 4 13 21-2 37-3 44z" fill="#070706" opacity=".78"/><path d="M283 57l-18 26m65-26l19 26" stroke="#090807" stroke-width="8"/>` : '';
  return `<svg viewBox="0 0 600 150" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="trg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="${sky}"/><stop offset="1" stop-color="#080706"/></linearGradient><radialGradient id="sun"><stop stop-color="${sun}" stop-opacity=".75"/><stop offset="1" stop-color="${sun}" stop-opacity="0"/></radialGradient></defs><rect width="600" height="150" fill="url(#trg)"/><circle cx="470" cy="32" r="48" fill="url(#sun)"/><path d="M0 111L58 79l45 18 72-55 52 61 66-41 50 45 71-64 50 56 59-38 77 38v51H0Z" fill="${far}"/><path d="M0 126l85-22 45 17 69-31 48 28 77-18 58 24 73-32 57 25 88-19v52H0Z" fill="${near}"/><path d="M420 102V60h13v42m-35 0V77h11v25m51 0V69h10v33" stroke="${sun}" stroke-width="2" opacity=".32"/>${grace}${boss}</svg>`;
}
const chaosQuips = [
  'The covenant bends. So do your plans.',
  'A completely avoidable problem has entered the chat.',
  'The Greater Will has adjusted the difficulty without asking.',
  'Miyazaki has noticed a positive mood developing.',
  'This seemed easier five seconds ago.',
  'The game has detected confidence.',
  'An HR complaint has been filed against the run.',
  'Fort, night.',
  'Melina has muted the group chat.',
  'This is now canon unfortunately.'
];
function chaosEventName(text){
  const t=text.toUpperCase();
  if(t.includes('NOTHING')) return 'MERCIFUL VOID';
  if(t.includes('FLASK')||t.includes('JUICE')||t.includes('DRINK')) return 'CRIMSON DECREE';
  if(t.includes('TALISMAN')) return 'CHARM EVICTION';
  if(t.includes('HEAVY')||t.includes('ARMOR')||t.includes('PANTS')||t.includes('HELMET')) return 'BURDEN OF FLESH';
  if(t.includes('LOCK-ON')||t.includes('CAMERA')) return 'BLIND COVENANT';
  if(t.includes('WEAPON')||t.includes('L2')) return 'ARMAMENT SCHISM';
  if(t.includes('SOLO')||t.includes('AGGRO')) return 'DIVIDED OATH';
  if(t.includes('HEAL')) return 'RUPTURED BOON';
  if(t.includes('GESTURE')||t.includes('CROUCH')||t.includes('CHAIR')) return 'CEREMONIAL NONSENSE';
  return pick(['RUPTURED BOON','BROKEN DECREE','ERRANT GRACE','SCARLET AMENDMENT','UNWELCOME MIRACLE','COVENANT MALFUNCTION']);
}
function renderChaosEvent(){
  const c=run.state.current;
  const eventName=chaosEventName(c.chaosConsequence||'');
  app.innerHTML=`<section class="tc-chaos-event"><div class="tc-chaos-title">Chaos Unleashed · The Seal Has Broken</div><div class="tc-chaos-seal"></div><div class="tc-kicker red">event of chaos</div><div class="tc-chaos-event-name">${h(eventName)}</div><div class="tc-kicker red">consequence</div><div class="tc-chaos-consequence">${h(c.chaosConsequence)}</div><div class="tc-chaos-quip">“${h(pick(chaosQuips))}”</div><button id="ackChaos" class="btn">Acknowledge This Bullshit</button></section>`;
  document.querySelector('#ackChaos').addEventListener('click',()=>{acknowledgedChaos.add(c.id);uiScreen='encounter';renderRun();});
}
'''
marker = "function navMarkup(active) {"
if marker not in s:
    raise SystemExit('nav helper marker missing')
s = s.replace(marker, helpers + '\n' + marker, 1)

# Add imagery to Site of Grace and Encounter without requiring external image hosting.
s = s.replace("<div class=\"tc-rune\"></div><h1 class=\"tc-title\">The Tarnished<br>Covenant</h1><div class=\"tc-subtitle\">shared challenge run</div>", "<div class=\"tc-rune\"></div><h1 class=\"tc-title\">The Tarnished<br>Covenant</h1><div class=\"tc-subtitle\">Site of Grace</div><div class=\"tc-grace-art\">${thematicRegionArt(state.region,'grace')}</div>", 1)
s = s.replace("<div class=\"tc-brief-head\"><div class=\"tc-kicker gold\">${c.target.exit?'regional capstone':'current target'}</div><div class=\"tc-brief-boss\">${h(c.target.name)}</div><div class=\"tc-brief-region\">${h(state.region)}</div></div>", "<div class=\"tc-brief-head\"><div class=\"tc-kicker gold\">${c.target.exit?'regional capstone':'current target'}</div><div class=\"tc-brief-boss\">${h(c.target.name)}</div><div class=\"tc-brief-region\">${h(state.region)}</div></div><div class=\"tc-boss-art\">${thematicRegionArt(state.region,'boss')}</div>", 1)

# Make renderRun route to the Chaos event before normal screens until this phone acknowledges it.
route = "if (state.runComplete) return renderRunComplete();"
if route not in s:
    raise SystemExit('renderRun route marker missing')
s = s.replace(route, "if (state.current?.chaosTriggered && !acknowledgedChaos.has(state.current.id)) return renderChaosEvent();\n  " + route, 1)

p.write_text(s)
