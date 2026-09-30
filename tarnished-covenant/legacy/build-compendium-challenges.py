from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

def jsq(text):
    return "'" + text.replace('\\','\\\\').replace("'","\\'") + "'"

extra_rites = [
("Off The Sauce","Do not use the Flask of Wondrous Physick for this encounter.","True",1),
("Talisman Teetotaler","Both players remove all talismans for the encounter.","Grand",2),
("Daring Disrobement","Each player removes two armor pieces of their choice for the encounter.","Grand",2),
("The Waver","Both players must one-hand their assigned weapon for the entire encounter. The other hand stays empty.","True",1),
("Thin Crust","Both players must reach Light Load before the pull and keep it for the encounter.","True",1),
("Deep Dish","Both players must reach Heavy Load before the pull and keep it for the encounter.","Grand",2),
("Substance Over Style","No weapon skills for the entire encounter.","True",1),
("Original Flavor","Use the assigned weapon exactly as issued: no changing affinity, no alternate Ash of War, no backup weapon.","True",1),
("QuikClot","Do not intentionally add extra Hemorrhage sources. If your assigned weapon has innate bleed, that is allowed.","True",1),
("Warm Heart","Do not intentionally add extra Frostbite sources. If your assigned weapon has innate frost, that is allowed.","True",1),
("Antidote Inherent","Do not intentionally add Poison sources during the encounter.","True",1),
("Putrefaction Preventative","Do not intentionally add Scarlet Rot sources during the encounter.","True",1),
("Emissary of Insomnia","Do not intentionally add Sleep sources during the encounter.","True",1),
("Panacea","Do not intentionally add any status source beyond whatever your assigned weapon already has.","Grand",2),
("Rejuvenating Rocks","After the first player drops below half health, Crimson Flasks are forbidden until someone stands in a Warming Stone effect.","Grand",2),
("Apeshit Intermission","After the boss reaches half health, both players must make their next damaging hit with a throwable before resuming weapon attacks.","True",1),
("Living Off The Land","Before victory, each player must land damage with one crafted offensive item.","True",1),
("Fastest Draw","If either player uses grease, it must be Drawstring Grease for this encounter.","Minor",0),
("Hygienic Hero","No weapon grease of any kind for this encounter.","Minor",0),
("Critical Convalescence","After the first stance break, nobody may use a Crimson Flask until a critical hit is landed or the stagger window ends unused.","True",1),
("Three Strikes","If the team wipes three times on this boss, both assigned weapons are condemned and must be rerolled before attempt four.","Grand",2),
("The Wheel","If one player dies three times while using the same assigned weapon on this encounter, that player must reroll it before the next serious attempt.","Grand",2),
("Boss and Toss","After victory, both current assigned weapons are retired from the very next encounter only.","Grand",2),
("Arsenal Aesthete","After victory, each current assigned weapon becomes ineligible for that same player on the next two encounters.","Grand",2),
("No Need For Golden Seed","Each player voluntarily removes two Crimson Flask uses from their personal budget for this encounter.","True",1),
("No Tears, No Fears","No Physick and one fewer Crimson Flask use per player for this encounter.","True",1),
("Mana From The Heavens","After your Cerulean Flasks are exhausted, FP recovery may only come from Starlight Shards for the rest of the encounter.","Grand",2),
("The Wall, Temporarily","For 20 consecutive seconds during the fight, one randomly chosen player may not roll. Blocking, sprinting, spacing, and suffering are legal.","True",1),
]

extra_chaos = [
"OFF THE SAUCE: Flask of Wondrous Physick is disabled for the rest of this attempt.",
"TALISMAN TEETOTALER: both players remove all talismans until victory or wipe.",
"DARING DISROBEMENT: each player removes two armor pieces until victory or wipe.",
"THE WAVER: both players must one-hand their assigned weapon for the rest of this attempt. The other hand stays empty.",
"THIN CRUST: both players must reach Light Load before the next attempt and keep it until victory or wipe.",
"DEEP DISH: both players must reach Heavy Load before the next attempt and keep it until victory or wipe.",
"SUBSTANCE OVER STYLE: no weapon skills for the remainder of this attempt.",
"ORIGINAL FLAVOR: no changing affinity, Ash of War, or assigned weapon before the next attempt. Use exactly what the Covenant issued.",
"STATUS EMBARGO: no intentionally added bleed, frost, poison, rot, sleep, or madness sources for the rest of this attempt.",
"REJUVENATING ROCKS: Crimson Flasks are locked until someone stands in a Warming Stone effect.",
"APESHIT INTERMISSION: both players must make their next damaging hit with a throwable before weapon attacks resume.",
"LIVING OFF THE LAND: each player must land damage with one crafted offensive item before either may heal again.",
"HYGIENIC HERO: no weapon grease for the remainder of this attempt.",
"CRITICAL CONVALESCENCE: after the next stance break, no Crimson Flask until a critical hit is landed or the stagger window expires.",
"THE WALL: randomly choose one player. No rolling for 30 seconds. Blocking, sprinting, spacing, and prayer remain legal.",
"THREE STRIKES: if this is your third team wipe on the current boss, both assigned weapons are condemned and must be rerolled before attempt four.",
"THE WHEEL: if a player reaches three deaths on this encounter with the same assigned weapon, that player must reroll before the next serious attempt.",
"BOSS AND TOSS: if you win this attempt, both assigned weapons are retired from the next encounter only.",
"ARSENAL AESTHETE: if you win this attempt, each current weapon is barred from that same player for the next two encounters.",
"NO NEED FOR GOLDEN SEED: each player loses two voluntary Crimson Flask uses for the remainder of this attempt.",
"NO TEARS, NO FEARS: Physick is disabled and each player loses one voluntary Crimson Flask use for the remainder of this attempt.",
"MANA FROM THE HEAVENS: once Cerulean Flasks are gone, the only legal FP recovery is Starlight Shards for the rest of this attempt.",
"SCAVENGER LAW: until victory or wipe, no purchased consumable may be used. Only found or crafted items are legal.",
"DRAWSTRING BUREAU: any grease used for the rest of this attempt must be Drawstring Grease.",
"PANACEA PLAYTHROUGH: do not intentionally add any status source beyond what your assigned weapon already carries.",
"ONE TOOL POLICY: no weapon swapping, no backup weapon, no offhand weapon. Your current assigned weapon is the only weapon you may deal damage with.",
]

needle="];\nconst TC_RITE_META"
if needle not in s:
    raise SystemExit('TC_EXTRA_RITES closing marker missing')
rite_js=''.join("\n ["+jsq(name)+","+jsq(text)+","+jsq(tier)+","+str(favor)+"]," for name,text,tier,favor in extra_rites)
s=s.replace(needle, rite_js+"\n];\nconst TC_RITE_META",1)

needle="].map(text=>({text,favor:1}));"
if needle not in s:
    raise SystemExit('TC_EXTRA_CHAOS closing marker missing')
chaos_js=',' + ''.join("\n "+jsq(x)+"," for x in extra_chaos)
s=s.replace(needle, chaos_js+"\n].map(text=>({text,favor:1}));",1)

s=s.replace('Honor system: when you have actually completed the demand in Elden Ring, certify it here.', 'Honor system: one assigned weapon per player, no backup weapon. When you have actually completed the demand in Elden Ring, certify it here.')

for required in ['ONE TOOL POLICY','BOSS AND TOSS','ARSENAL AESTHETE','THE WAVER','TALISMAN TEETOTALER']:
    if required not in s:
        raise SystemExit('compendium challenge missing: '+required)

p.write_text(s)
