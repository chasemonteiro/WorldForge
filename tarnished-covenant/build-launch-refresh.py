from pathlib import Path
import re
import runpy
from datetime import datetime, timezone

app_path=Path('tarnished-covenant/index.html')

# This is the final production build step. Ensure late UI/stability layers cannot
# leave an outer Covenant-boon busy wrapper around the real refresh handler.
runpy.run_path('tarnished-covenant/build-refresh-handler-final.py')

# Bell Bearing contracts are regional gameplay events: Favor stays banked, but
# eligibility follows the next sequential bearing in the current or a previously
# visited region. Apply and assert this at the end of every build so earlier
# progression/UI layers cannot loosen it.
runpy.run_path('tarnished-covenant/build-region-locked-contracts.py')
runpy.run_path('tarnished-covenant/test-region-locked-contracts.py')

# Co-op bosses are one Covenant encounter across two host worlds. Avoid rerunning
# the co-op source patch after the later shared-draw patch has already rewritten
# post-battle reward generation; only apply it when the co-op layer is absent.
if 'function tcWorldClears(encounter)' not in app_path.read_text():
    runpy.run_path('tarnished-covenant/build-coop-world-clears.py')

# The earned payout is shared: either phone may initiate the one draw, but the
# first successful revision/CAS save consumes it and both phones receive that
# exact result. Apply this after the co-op layer and assert the combined state.
if 'function tcSharedRewardDrawPending(state)' not in app_path.read_text():
    runpy.run_path('tarnished-covenant/build-shared-reward-draw.py')

# Reward reveal progression itself is shared too. The drawing phone advances the
# sequence; the partner phone mirrors each reveal automatically. This also
# repairs the old detached-smithing-object bug so reward counters persist.
runpy.run_path('tarnished-covenant/build-shared-reward-reveal-sync.py')

# A partner who watched every reward live should not be mistaken for a device
# that missed the payout and forced through the offline catch-up replay again.
runpy.run_path('tarnished-covenant/build-live-reward-watch.py')

# A rare shared boon can authorize one optional off-assignment boss kill. It is
# restricted to the current or previously reached regions, removes that boss
# from future regional draws, and never grants encounter/capstone progress.
runpy.run_path('tarnished-covenant/build-free-boss-kill.py')

# Legacy reward tuning layer; the expanded 100% table below supersedes these
# thresholds while preserving the durable Sanctioned Boss Kill behavior.
runpy.run_path('tarnished-covenant/build-reward-odds-swap.py')

# Every completed Covenant encounter pays exactly +1 guaranteed Smithing Favor.
# Honored Rite/Chaos objectives determine bonus reward draws; random Favor
# results remain extra rather than multiplying the guaranteed encounter payout.
runpy.run_path('tarnished-covenant/build-favor-rebalance.py')

# Appeal Waivers are saved inventory unless the player explicitly chooses to
# spend one during a weapon appeal. Owning a waiver no longer auto-consumes it.
runpy.run_path('tarnished-covenant/build-appeal-waiver-choice.py')

# Physical progression uses a dependency graph. Required gate bosses are forced
# before blocked capstones/downstream bosses, conditional routes are respected,
# and cross-region gates can send the Covenant backward to the correct area.
runpy.run_path('tarnished-covenant/build-boss-prerequisites.py')

# Preserve the existing regional exploration threshold, but once the capstone
# would normally be eligible, force any still-unmet physical prerequisite next
# rather than leaving it behind the capstone RNG roll.
runpy.run_path('tarnished-covenant/build-capstone-prerequisite-priority.py')

# With guaranteed Favor handling progression, broaden the random treasury to the
# agreed 100% distribution and make every new strategic reward actually usable:
# Veto, Clemency, Union Discount, Blank Amendment, Joint Appeal, and Windfall.
runpy.run_path('tarnished-covenant/build-expanded-reward-pool.py')

# Encounter completion and Weapon Appeal belong to the Boss panel only. Keep the
# action block inside that swipe panel so Weapons, Chaos, and Rite remain focused
# and uncluttered. This finalizer also owns the two-penalty normal Both appeal.
runpy.run_path('tarnished-covenant/build-encounter-boss-actions.py')

# Final cross-system ownership: after one host-world victory, encounter terms are
# frozen until 2/2; strategic Veto replacements are optional-only and validated
# against latest shared state. Apply after all appeal/reward layers.
runpy.run_path('tarnished-covenant/build-today-systems-hardening.py')

# Weapon Appeal belongs on the Weapons panel; victory stays on Boss. The same
# final tune also keeps Sanctioned Boss Kill rare at 8% while preserving 100%.
runpy.run_path('tarnished-covenant/build-weapons-appeal-reward-tune.py')

# The post-battle report is one shared co-op artifact. Both phones mirror the
# same Rite/Chaos answers and guaranteed Favor total before either may file it.
runpy.run_path('tarnished-covenant/build-shared-post-battle-report.py')

# Masterworked weapons become owner-bound veteran assets with one future
# penalty-free Recall of the exact archived build, usable only before 1/2.
runpy.run_path('tarnished-covenant/build-masterwork-recall.py')

# The Compendium is an archive/case-file surface, not a spreadsheet. This late
# presentation layer keeps the underlying history schema and all interactions
# untouched while giving every recorded field a durable dossier treatment.
runpy.run_path('tarnished-covenant/build-compendium-dossier.py')

runpy.run_path('tarnished-covenant/test-coop-world-clears.py')
runpy.run_path('tarnished-covenant/test-shared-reward-draw.py')
runpy.run_path('tarnished-covenant/test-live-reward-watch.py')
runpy.run_path('tarnished-covenant/test-free-boss-kill.py')
runpy.run_path('tarnished-covenant/test-favor-rebalance.py')
runpy.run_path('tarnished-covenant/test-appeal-waiver-choice.py')
runpy.run_path('tarnished-covenant/test-boss-prerequisites.py')
runpy.run_path('tarnished-covenant/test-capstone-prerequisite-priority.py')
runpy.run_path('tarnished-covenant/test-expanded-reward-pool.py')
runpy.run_path('tarnished-covenant/test-today-systems-audit.py')
runpy.run_path('tarnished-covenant/test-shared-post-battle-report.py')
runpy.run_path('tarnished-covenant/test-masterwork-recall.py')
runpy.run_path('tarnished-covenant/test-compendium-dossier.py')

p=app_path
s=p.read_text()

# Keep the custom Safari / iOS Home Screen icon present on every full rebuild.
# The PNG itself is a durable asset on the app branch; the versioned filename
# also helps iOS avoid reusing an older cached touch icon.
s=re.sub(r'\n?\s*<link rel="apple-touch-icon"[^>]*>','',s)
s=re.sub(r'\n?\s*<link rel="icon"[^>]*data-tc-app-icon[^>]*>','',s)
icon_anchor='  <meta name="apple-mobile-web-app-title" content="Tarnished Covenant">\n'
if icon_anchor not in s:
    raise SystemExit('apple mobile title anchor missing')
icon_tags='''  <link rel="apple-touch-icon" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png">\n  <link rel="icon" type="image/png" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png" data-tc-app-icon>\n'''
s=s.replace(icon_anchor,icon_anchor+icon_tags,1)

# Replace any previous freshness guard so every generated build gets a new ID.
s=re.sub(r"\n?/\* --- Home Screen freshness guard --- \*/.*?/\* --- End Home Screen freshness guard --- \*/\n?", "\n", s, flags=re.S)

build_id=datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
js=f'''\n/* --- Home Screen freshness guard --- */\nconst TC_BUILD_ID='{build_id}';\nlet tcFreshnessCheckRunning=false;\nfunction tcForceFreshNavigation(){{\n  const url=new URL(location.href);\n  url.searchParams.set('tcv',String(Date.now()));\n  location.replace(url.toString());\n}}\nasync function tcCheckForFreshBuild(){{\n  if(tcFreshnessCheckRunning||!navigator.onLine)return;\n  tcFreshnessCheckRunning=true;\n  try{{\n    const probe=new URL(location.href);\n    probe.searchParams.set('tc_probe',String(Date.now()));\n    const response=await fetch(probe.toString(),{{cache:'no-store',headers:{{'Cache-Control':'no-cache'}}}});\n    if(!response.ok)return;\n    const text=await response.text();\n    const match=text.match(/const TC_BUILD_ID='([^']+)'/);\n    if(match&&match[1]!==TC_BUILD_ID){{\n      const fresh=new URL(location.href);\n      fresh.searchParams.set('tcv',match[1]);\n      location.replace(fresh.toString());\n    }}\n  }}catch(error){{console.warn('Freshness check failed',error);}}\n  finally{{tcFreshnessCheckRunning=false;}}\n}}\nwindow.addEventListener('pageshow',()=>setTimeout(tcCheckForFreshBuild,350));\ndocument.addEventListener('visibilitychange',()=>{{if(!document.hidden)setTimeout(tcCheckForFreshBuild,200);}});\n/* --- End Home Screen freshness guard --- */\n'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+s[idx:]

# Any built-in refresh control must perform a new navigation, not merely revive
# the current iOS standalone snapshot.
s=s.replace("()=>location.reload()", "()=>tcForceFreshNavigation()")
s=s.replace("location.reload();", "tcForceFreshNavigation();")

for needle in ['TC_BUILD_ID','tcCheckForFreshBuild','tcForceFreshNavigation','cache:\'no-store\'','rel="apple-touch-icon"','tarnished-covenant-icon-v1.png','function tcSharedRewardDrawPending(state)','function tcSharedRewardIndex(shared)','function tcSharedRewardObservedAll(shared,identity=playerName())','const next=smithingCopy(latest),sm=next.smithing;','Guaranteed Smithing Favor','nextState.smithing.favor+=guaranteedFavor;','function tcShowAppealWaiverChoice(which)','Keep Waiver · Take Penalty','bossPanel.appendChild(bar);','weaponPanel.appendChild(appealBar);','function tcBuildSanctionedBossKill(latest,region,name,actor)',"if(roll<0.64){const tax=pick(TC_COVENANT_TAXES);","if(roll<0.72){sm.freeBossKills+=1;return {kind:'freeboss',label:'Sanctioned Boss Kill'",'function tcBuildBossVeto(latest,encounterId,oldBoss,replacement,actor)','function tcEffectiveSmithingContractCost(state,bearing)','function tcBuildClemency(latest,encounterId,key,actor)','function tcBuildJointAppeal(latest,encounterId,oldChase,oldMorgan,newChase,newMorgan,actor)','function tcNextUnmetPrerequisite(state,targetName,seen=new Set())','function tcOutstandingRouteGateForCurrentRegion(state)','function tcIsProgressionGateBoss(name)','function tcIsRequiredRemembranceBoss(state,name)','function tcEncounterMutationLocked(state=run?.state)','function tcBossVetoReplacementLegal(state,replacement,oldBoss)','function tcCapstonePrerequisiteDue(state)','function tcCompendiumDossierMarkup(entry,index,state)','Office of Covenant Records','function tcSharedBattleReportDraft(state=run?.state)','function tcBuildMasterworkRecall(latest,encounterId,recordId,expectedCurrentWeapon,slot,actor)','masterworkRecalls','RECALL AVAILABLE','PREREQUISITE NEXT']:
    if needle not in s: raise SystemExit('freshness/icon/gameplay invariant missing: '+needle)
p.write_text(s)
