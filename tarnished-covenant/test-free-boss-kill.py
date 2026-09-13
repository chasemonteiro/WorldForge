from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or f'missing Sanctioned Boss Kill invariant: {needle}')

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or f'forbidden Sanctioned Boss Kill behavior: {needle}')

# Reward exists and persists through shared payout deltas.
for needle in [
    'freeBossKills: Number(raw.freeBossKills || 0)',
    "kind:'freeboss',label:'Sanctioned Boss Kill'",
    "const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills','bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals'];",
    "freeboss:'⚔'",
]: require(needle)

# Current/reached regions only; no regionUnlocked forward travel.
for needle in [
    'function tcFreeBossEligibleRegions(state)',
    "[state?.region,...(state?.clearedRegions||[])]",
    'function tcEligibleFreeBossChoices(state)',
    "if(region===activeRegion&&name===activeName)continue;",
]: require(needle)

# Redemption spends exactly one shared token and records a pool exclusion.
for needle in [
    'function tcBuildSanctionedBossKill(latest,region,name,actor)',
    'if(Number(sm.freeBossKills||0)<1)return null;',
    'next.smithing.freeBossKills=Math.max(0,Number(next.smithing.freeBossKills||0)-1);',
    'next.sanctionedBossKills=[...tcSanctionedBossKills(next)',
    'retryBuilder:(latest)=>tcBuildSanctionedBossKill(latest,choice.region,choice.name,actor)',
]: require(needle)

# Draw-pool exclusion is independent of encounter history/progression.
for needle in [
    'for(const entry of (state.sanctionedBossKills||[]))',
    'if(entry?.region===regionName&&entry?.name)names.add(entry.name);',
    'does not advance regional or capstone progress',
]: require(needle)

# The redemption builder must not fake a normal encounter completion.
start=html.find('function tcBuildSanctionedBossKill(latest,region,name,actor)')
end=html.find('function tcCloseFreeBossKillPicker()',start)
if start<0 or end<0: raise SystemExit('redemption builder block missing')
block=html[start:end]
for forbidden in ['next.cleared++','completeEncounter(','next.history.unshift','regionComplete=true']:
    if forbidden in block: raise SystemExit('Sanctioned Boss Kill incorrectly advances Covenant progression: '+forbidden)

# The current assigned boss cannot be bypassed using this boon.
require("if(region===activeRegion&&name===activeName)continue;")

# Expanded reward model keeps Tax at 5% (.59-.64) and Sanctioned Boss Kill
# at 8% (.64-.72), before the newer strategic reward bands.
require("if(roll<0.59){sm.aviaryTickets+=1;")
require("if(roll<0.64){const tax=pick(TC_COVENANT_TAXES);")
require("if(roll<0.72){sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill'")
forbid("if(roll<0.90){sm.freeBossKills+=1;")

print('Tarnished Covenant Sanctioned Boss Kill invariants: PASS — boss kill 8%, tax 5% inside expanded pool')
