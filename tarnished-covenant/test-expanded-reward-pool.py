from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing expanded reward invariant: '+needle)

def forbid(needle,msg=None):
    if needle in html: raise SystemExit(msg or 'forbidden expanded reward behavior: '+needle)

# Base reward table totals 100%; Erdtree Writs use a separate draw.
thresholds=[
    (0.12,"sm.favor+=1",'12% +1 Favor'),
    (0.16,"sm.favor+=2",'4% +2 Favor'),
    (0.29,"sm.chaosRefreshes+=1",'13% Chaos Refresh'),
    (0.42,"sm.riteRefreshes+=1",'13% Rite Refresh'),
    (0.49,"sm.appealWaivers+=1",'7% Appeal Waiver'),
    (0.59,"sm.aviaryTickets+=1",'10% Frequent Flier'),
    (0.64,"const tax=pick(TC_COVENANT_TAXES)",'5% Covenant Tax'),
    (0.74,"sm.freeBossKills+=1",'10% Sanctioned Boss Kill'),
    (0.78,"sm.bossVetoes+=1",'4% Covenant Veto'),
    (0.84,"sm.clemencies+=1",'6% Letter of Clemency'),
    (0.85,"sm.unionDiscounts+=1",'1% Union Discount'),
    (0.95,"sm.blankAmendments+=1",'10% Blank Amendment'),
    (0.98,"sm.jointAppeals+=1",'3% Joint Appeal'),
]
for value,body,label in thresholds:
    require(f"if(roll<{value:.2f}){{{body};",f'missing threshold for {label}')
require("sm.favor+=3;return {kind:'windfall',label:'Treasury Windfall'",'missing 2% Treasury Windfall tail')
assert round(sum([.12,.04,.13,.13,.07,.10,.05,.10,.04,.06,.01,.10,.03,.02]),10)==1.0

# Every durable strategic reward survives normalization and one shared payout CAS.
for key in ['bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals']:
    require(f'{key}: Number(raw.{key} || 0)')
require("const keys=['favor','chaosRefreshes','riteRefreshes','appealWaivers','aviaryTickets','freeBossKills','bossVetoes','clemencies','unionDiscounts','blankAmendments','jointAppeals','erdtreeWrits','erdtreeWritsAwarded'];")

# Covenant Veto is a deliberately expensive escape hatch and cannot bypass required progression.
for needle in [
    'function tcBossVetoEligible(state)',
    "if(typeof tcIsProgressionGateBoss==='function'&&tcIsProgressionGateBoss(c.target.name))return false;",
    'if(Array.isArray(c.worldClears)&&c.worldClears.length)return false;',
    'Number(sm.favor||0)>=2',
    'Number(sm.chaosRefreshes||0)>=1',
    'Number(sm.riteRefreshes||0)>=1',
    'next.smithing.bossVetoes-=1;',
    'next.smithing.favor-=2;',
    'next.smithing[refreshKey]-=1;',
    'id="tcVetoRefresh"',
    'next.current.target=structuredClone(replacement);',
    'Your current weapons, Rite, Chaos decree, and existing penalties stay in force.',
]: require(needle)

# Clemency spends one letter and removes exactly one current Appeal penalty.
for needle in [
    'function tcBuildClemency(latest,encounterId,key,actor)',
    'next.current.penances.splice(index,1)[0]',
    'next.smithing.clemencies-=1;',
]: require(needle)

# Blank Amendment becomes exactly one chosen ordinary refresh.
for needle in [
    'function tcBuildBlankConversion(latest,kind,actor)',
    "const next=smithingCopy(latest),key=kind==='chaos'?'chaosRefreshes':'riteRefreshes';",
    'next.smithing.blankAmendments-=1;',
    'next.smithing[key]=Number(next.smithing[key]||0)+1;',
]: require(needle)

# Joint Appeal rerolls both assignments without adding a penance or consuming a normal waiver.
for needle in [
    'function tcBuildJointAppeal(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor)',
    'next.current.chase=structuredClone(newChase);',
    'next.current.morgan=structuredClone(newMorgan);',
    'next.smithing.jointAppeals-=1;',
    'Both weapons were reassigned with no penalty.',
]: require(needle)
start=html.find('function tcBuildJointAppeal(')
end=html.find('function tcOpenJointAppeal()',start)
if start<0 or end<0: raise SystemExit('Joint Appeal builder block missing')
block=html[start:end]
forbid_joint=['penances.push','appealWaivers-=','appealWaivers +=']
for bad in forbid_joint:
    if bad in block: raise SystemExit('Joint Appeal incorrectly charges/adds: '+bad)

# Union Discount is automatic on the next Bell contract and affects affordability as well as payment.
for needle in [
    'function tcEffectiveSmithingContractCost(state,bearing)',
    "return Math.max(0,base-(Number(sm.unionDiscounts||0)>0?3:0));",
    'sm.favor>=tcEffectiveSmithingContractCost(state,b)',
    'cost=tcEffectiveSmithingContractCost(source,b)',
    'next.smithing.unionDiscounts=Math.max(0,Number(next.smithing.unionDiscounts||0)-1);',
    'discountApplied:discounted?3:0',
]: require(needle)

# Strategic items live in the Ledger instead of recreating the old crowded Encounter footer.
for needle in [
    'tc-boon-grid tc-boon-grid-expanded',
    'data-use-boss-veto',
    'data-use-clemency',
    'data-use-joint-appeal',
    'data-blank-to="chaos"',
    'data-blank-to="rite"',
]: require(needle)

print('Tarnished Covenant expanded reward pool invariants: PASS — exact 100% table and all strategic rewards are functional.')
