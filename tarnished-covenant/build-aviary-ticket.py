from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Persist a bankable bird-farm reward alongside the other Covenant boons.
old = """    appealWaivers: Number(raw.appealWaivers || 0),
    chaosRefreshes: Number(raw.chaosRefreshes || 0),
    riteRefreshes: Number(raw.riteRefreshes || 0)
  };"""
new = """    appealWaivers: Number(raw.appealWaivers || 0),
    chaosRefreshes: Number(raw.chaosRefreshes || 0),
    riteRefreshes: Number(raw.riteRefreshes || 0),
    aviaryTickets: Number(raw.aviaryTickets || 0)
  };"""
if old not in s:
    raise SystemExit('smithingData boon inventory target missing')
s = s.replace(old, new, 1)

# Rebalance the positive side of the prize table to make room for a rare
# Mohgwyn bird-farm permission slip while keeping the 6% tax chance intact.
old = """function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.38){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor',detail:'One mark of Smithing Favor is added to the Covenant treasury.'};}
  if(roll<0.43){sm.favor+=2;return {kind:'favor2',label:'+2 Smithing Favor',detail:'A rare double grant. The accountants are furious.'};}
  if(roll<0.61){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh',detail:'Reroll one unopened Chaos trigger on a future encounter.'};}
  if(roll<0.79){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh',detail:'Reroll one Odd Rite on a future encounter.'};}
  if(roll<0.94){sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver',detail:'Your next Weapon Appeal is penalty-free.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};
}"""
new = """function drawCovenantReward(state){
  const sm=state.smithing || (state.smithing=smithingData(state));
  const roll=Math.random();
  if(roll<0.35){sm.favor+=1;return {kind:'favor',label:'+1 Smithing Favor',detail:'One mark of Smithing Favor is added to the Covenant treasury.'};}
  if(roll<0.40){sm.favor+=2;return {kind:'favor2',label:'+2 Smithing Favor',detail:'A rare double grant. The accountants are furious.'};}
  if(roll<0.56){sm.chaosRefreshes+=1;return {kind:'chaos',label:'Chaos Refresh',detail:'Reroll one unopened Chaos trigger on a future encounter.'};}
  if(roll<0.72){sm.riteRefreshes+=1;return {kind:'rite',label:'Rite Refresh',detail:'Reroll one Odd Rite on a future encounter.'};}
  if(roll<0.86){sm.appealWaivers+=1;return {kind:'appeal',label:'Appeal Waiver',detail:'Your next Weapon Appeal is penalty-free.'};}
  if(roll<0.94){sm.aviaryTickets+=1;return {kind:'aviary',label:'Dynasty Frequent Flier',detail:'Grants 5 sanctioned trips to the bird. The bird remains a valued member of the economy.'};}
  const tax=pick(TC_COVENANT_TAXES);
  return {kind:'tax',label:tax.label,detail:tax.detail};
}"""
if old not in s:
    raise SystemExit('reward table target missing')
s = s.replace(old, new, 1)

old = """  const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',tax:'☠'};"""
new = """  const icons={favor:'✦',favor2:'✦✦',chaos:'◉',rite:'✧',appeal:'⚖',aviary:'𓅪',tax:'☠'};"""
if old not in s:
    raise SystemExit('reward icon map missing')
s = s.replace(old, new, 1)

old = "function tcRewardClass(kind){return kind==='tax'?'tax':kind==='chaos'?'chaos':kind==='rite'?'rite':kind==='appeal'?'appeal':'favor';}"
new = "function tcRewardClass(kind){return kind==='tax'?'tax':kind==='chaos'?'chaos':kind==='rite'?'rite':kind==='appeal'?'appeal':kind==='aviary'?'aviary':'favor';}"
if old not in s:
    raise SystemExit('reward class helper missing')
s = s.replace(old, new, 1)

# Show the banked reward in the Smithing/Covenant boon inventory.
old = """    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
  </div><div class=\"tc-muted\">Waivers make the next weapon appeal penalty-free. Refreshes are the only way to reroll a current Rite or unopened Chaos decree.</div></div>`;"""
new = """    <div><strong>${sm.riteRefreshes}</strong><span>Rite Refresh${sm.riteRefreshes===1?'':'es'}</span></div>
    <div><strong>${sm.aviaryTickets}</strong><span>Dynasty Frequent Flier${sm.aviaryTickets===1?'':'s'}</span></div>
  </div><div class=\"tc-muted\">Waivers make the next weapon appeal penalty-free. Refreshes reroll a Rite or unopened Chaos decree. Each Dynasty Frequent Flier grants 5 sanctioned trips to the Mohgwyn bird.</div></div>`;"""
if old not in s:
    raise SystemExit('boon ledger markup target missing')
s = s.replace(old, new, 1)

# Give the new symbol its own visual identity and let four boon counters reflow cleanly.
css = r'''
/* --- Dynasty Frequent Flier reward --- */
.tc-reward-result.aviary{border-color:rgba(144,161,119,.42);background:linear-gradient(90deg,transparent,rgba(89,107,68,.14),transparent)}
.tc-reward-result.aviary .tc-reward-icon,.tc-reward-result.aviary .tc-reward-name{color:#c7d1a5}
.tc-boon-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
@media(max-width:430px){.tc-boon-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
if '</style>' not in s:
    raise SystemExit('style marker missing')
s = s.replace('</style>', css + '\n</style>', 1)

for invariant in ['aviaryTickets', "kind:'aviary'", 'Dynasty Frequent Flier', 'valued member of the economy']:
    if invariant not in s:
        raise SystemExit('aviary invariant missing: ' + invariant)

p.write_text(s)
