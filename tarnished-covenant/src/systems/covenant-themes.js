/* --- Themed runs: lore factions and dealt characters ---
   rules.theme = {kind:'lore', id} (shared by both players)
              or {kind:'character', chase:id, morgan:id} (dealt per player).
   Chosen only when a Covenant begins. Weapon classes come from
   src/weapon-classes.js (generated from the calculator data).
   - Lore: about half of all draws are steered toward the faction's signature
     arms when the region has any; a third of Odd Rites come from the
     faction's own Rites. Affinity and spell guidance is shown, not enforced.
   - Characters: each player's weapons are drawn from their character's weapon
     classes when the region offers them (re-sampling the normal draw, so
     gates, used weapons and region decks still apply); spell and armor rules
     are shown for the honor system.
   If a region has nothing that fits, the ordinary draw stands. */
const TC_LORE_THEMES={
  carian:{name:'Carian',line:'Moon, glintstone and the Carian royal family.',arms:/carian|moon|glintstone|crystal|azur|lusat|meteorite|astrologer|academy|rennala|ranni|loretta|dark moon/i,affinity:'Magic or Cold',spells:'Sorceries welcome; incantations frowned upon.',rites:[['Moonlit Etiquette','Before the first attack, both players crouch and bow to the boss.'],['Glintstone Doctrine','At least one sorcery must be cast during the fight. Any sorcery counts.'],['Royal Composure','No jumping attacks for the whole fight.']]},
  golden:{name:'Golden Order',line:'The Erdtree, its knights and its fundamentalists.',arms:/golden|erdtree|order|epitaph|sacred|gold|leyndell|marika|radagon|godfrey|morgott|crucible/i,affinity:'Sacred',spells:'Golden Order and Erdtree incantations; no sorceries.',rites:[['Gilded Formality','Open the fight with an incantation or a buff. Anything golden counts.'],['Measured Steps','No rolling for the first thirty seconds.'],['Fundamentalist Vow','No bleed or poison weapons or items this fight.']]},
  mohg:{name:'Mohg’s Dynasty',line:'Blood, the Formless Mother and the Bloody Fingers.',arms:/blood|mohg|reduvia|rivers|bloody|bloodhound|eleonora|helice|morgott|varr|nagakiba|curseblade/i,affinity:'Blood or Occult',spells:'Bloodflame incantations; nothing holy.',rites:[['Blood Tithe','Make the boss bleed at least once.'],['Bloody Welcome','Each player must take damage before dealing any.'],['Formal Banquet','No healing until the boss is below half health.']]},
  rot:{name:'Scarlet Rot',line:'Malenia’s bloom, the Kindred and the cleanrot knights.',arms:/rot|cleanrot|venom|poison|scarlet|malenia|miquella|scythe|thorn/i,affinity:'Poison or Occult',spells:'Rot and Miquella incantations.',rites:[['Bloom of Rot','Inflict poison or scarlet rot on the boss at least once.'],['Rotten Patience','No healing for the first sixty seconds.'],['Unbloomed','Neither player wears a helmet this fight.']]},
  fire:{name:'Fire and the Fell God',line:'The Fire Giants, the Fire Monks and Messmer’s flame.',arms:/fire|flame|magma|giant|fell|blasphemous|messmer|monk|torch|salamander|ember/i,affinity:'Fire or Flame Art',spells:'Fire incantations and fire sorceries.',rites:[['Kindled','Deal fire damage at least once: a weapon, a pot or a spell.'],['Giant’s Stance','Two-hand your weapon for the whole fight.'],['Burning Vigil','No shield blocking this fight.']]}
};
const TC_CHARACTERS={
  carianKnight:{name:'Carian Knight',classes:['Straight Sword','Thrusting Sword','Greatsword','Glintstone Staff','Thrusting Shield'],affinity:'Magic or Cold',spells:'Sorceries only.',armor:'Knightly. Blue, if you have it.'},
  bloodyFinger:{name:'Bloody Finger',classes:['Katana','Curved Sword','Dagger','Claw','Backhand Blade'],affinity:'Blood or Occult',spells:'Bloodflame incantations only.',armor:'Something sinister.'},
  beast:{name:'Wandering Beast',classes:['Fist','Claw','Beast Claw','Colossal Weapon','Hand-to-Hand Art'],affinity:'Heavy or Keen',spells:'Beast incantations only.',armor:'Furs, or nothing much.'},
  goldenKnight:{name:'Golden Order Knight',classes:['Straight Sword','Greatsword','Halberd','Sacred Seal','Light Greatsword'],affinity:'Sacred',spells:'Golden Order and Erdtree incantations.',armor:'Gold, of course.'},
  duelist:{name:'Duelist',classes:['Thrusting Sword','Heavy Thrusting Sword','Katana','Curved Sword','Light Greatsword'],affinity:'Keen or Quality',spells:'No spells.',armor:'Light. No shield.'},
  giantSlayer:{name:'Giant-Slayer',classes:['Colossal Sword','Colossal Weapon','Great Hammer','Greataxe','Great Katana'],affinity:'Heavy',spells:'No spells.',armor:'As heavy as you can carry.'},
  sentinel:{name:'Spear Sentinel',classes:['Spear','Great Spear','Halberd','Reaper'],affinity:'Quality or Heavy',spells:'Incantations only.',armor:'Soldier’s kit.'},
  apostle:{name:'Godskin Apostle',classes:['Twinblade','Curved Greatsword','Dagger','Curved Sword'],affinity:'Fire or Flame Art',spells:'Godskin and black flame incantations.',armor:'Robes. Stretchy ones.'},
  marksman:{name:'Marksman',classes:['Light Bow','Bow','Greatbow','Crossbow','Ballista','Throwing Blade'],affinity:'Any',spells:'No spells.',armor:'Light, to keep your distance.'},
  pilgrim:{name:'Scarlet Pilgrim',classes:['Reaper','Whip','Spear','Curved Sword','Flail'],affinity:'Poison or Occult',spells:'Rot incantations only.',armor:'Tattered.'}
};
function tcWeaponKey(n){return String(n||'').replace(/\s*\(\+\d+\)$/,'').replace(/[’‘]/g,"'").trim().toLowerCase();}
function tcWeaponClass(name){return (typeof TC_WEAPON_CLASSES!=='undefined'&&TC_WEAPON_CLASSES[tcWeaponKey(name)])||'';}
function tcTheme(state){const t=state?.rules?.theme;return t&&(t.kind==='lore'&&TC_LORE_THEMES[t.id]||t.kind==='character')?t:null;}
function tcCharacterFor(state,slot){const t=tcTheme(state);return t?.kind==='character'?TC_CHARACTERS[t[slot]]||null:null;}
function tcBuildFits(state,slot,build){
  const t=tcTheme(state);if(!t||!build?.name)return true;
  if(t.kind==='character'){const ch=tcCharacterFor(state,slot);return !ch||ch.classes.includes(tcWeaponClass(build.name));}
  return TC_LORE_THEMES[t.id].arms.test(build.name);
}
// Re-sample the ordinary draw until it fits the theme (or give up and keep the best).
const tcChooseWeaponPairBeforeTheme=chooseWeaponPair;
chooseWeaponPair=function(state,target){
  let pair=tcChooseWeaponPairBeforeTheme(state,target);
  const t=tcTheme(state);if(!t||!pair)return pair;
  const score=p=>(tcBuildFits(state,'chase',p?.chase)?1:0)+(tcBuildFits(state,'morgan',p?.morgan)?1:0);
  // Lore steers about half the draws; characters always try.
  const goal=t.kind==='lore'?(Math.random()<0.5?1:0):2;
  for(let i=0;i<20&&score(pair)<goal;i++){const p=tcChooseWeaponPairBeforeTheme(state,target);if(p&&score(p)>score(pair))pair=p;}
  // Characters: re-deal just the slot that still doesn't fit.
  if(pair&&t.kind==='character'){
    for(const slot of ['chase','morgan']){
      if(tcBuildFits(state,slot,pair[slot]))continue;
      const other=slot==='chase'?'morgan':'chase',avoid=[pair[other]?.name].filter(Boolean);
      for(let i=0;i<20;i++){let b=null;try{b=makeBuild(state.region,target,avoid,state);}catch(_){break;}if(b&&tcBuildFits(state,slot,b)&&b.name!==pair[other]?.name){pair={...pair,[slot]:b};break;}}
    }
  }
  return pair||null;
};
// An Appeal re-draws one or both weapons; keep the character's classes there too.
const tcChangeWeaponsBeforeTheme=changeWeapons;
changeWeapons=function(state,actor,which,useWaiver=false){
  const next=tcChangeWeaponsBeforeTheme(state,actor,which,useWaiver);
  const t=tcTheme(next);if(!t||t.kind!=='character'||!next?.current)return next;
  const c=next.current;
  for(const slot of (which==='both'?['chase','morgan']:[which])){
    if(tcBuildFits(next,slot,c[slot]))continue;
    const other=slot==='chase'?'morgan':'chase',avoid=[c[other]?.name,state.current?.[slot]?.name,...(c.appealedWeaponNames||[])].filter(Boolean);
    for(let i=0;i<30;i++){let b=null;try{b=makeBuild(next.region,c.target,avoid,next);}catch(_){break;}if(b&&tcBuildFits(next,slot,b)){c[slot]=b;break;}}
  }
  return next;
};
const tcPickRiteBeforeTheme=tcPickRite;
tcPickRite=function(state,minTier=2){
  const t=tcTheme(state);
  if(t?.kind==='lore'&&Math.random()<0.34){
    const recent=new Set((state?.history||[]).slice(0,6).map(x=>x?.oddRite?.name).filter(Boolean));
    const pool=TC_LORE_THEMES[t.id].rites.filter(r=>!recent.has(r[0]));
    if(pool.length)return pick(pool);
  }
  return tcPickRiteBeforeTheme(state,minTier);
};
function tcDealCharacters(){
  const ids=Object.keys(TC_CHARACTERS),a=pick(ids);let b=pick(ids);
  for(let i=0;i<10&&b===a;i++)b=pick(ids);
  return {chase:a,morgan:b};
}
const tcInitialRunStateBeforeTheme=initialRunState;
initialRunState=function(options={}){
  const state=tcInitialRunStateBeforeTheme(options),want=options?.rules?.theme;
  if(!state||!want)return state;
  let theme=null;
  if(want.kind==='lore'&&TC_LORE_THEMES[want.id])theme={kind:'lore',id:want.id};
  else if(want.kind==='character')theme={kind:'character',...tcDealCharacters()};
  if(!theme)return state;
  state.rules={...(state.rules||{}),theme};
  // The first fight was dealt before the theme existed; deal its weapons again.
  if(state.current?.target){const pair=chooseWeaponPair(state,state.current.target);if(pair){state.current.chase=pair.chase;state.current.morgan=pair.morgan;}}
  return state;
};

// Setup: a theme choice under the twists.
const tcTwistsMarkupBeforeTheme=tcTwistsMarkup;
tcTwistsMarkup=function(){
  const chip=(value,label)=>`<button type="button" class="tc-theme-chip ${value==='none'?'on':''}" data-theme-pick="${value}" aria-pressed="${value==='none'}">${h(label)}</button>`;
  return `${tcTwistsMarkupBeforeTheme()}<div class="tc-twists tc-theme-pick"><span class="label">Theme</span>
    <div class="tc-theme-chips">${chip('none','None')}${chip('character','Deal us characters')}${Object.entries(TC_LORE_THEMES).map(([id,t])=>chip('lore:'+id,t.name)).join('')}</div>
    <p class="tc-theme-help" data-theme-help>No theme: weapons are drawn as usual.</p></div>`;
};
function tcThemeHelp(value){
  if(value==='character')return 'Each of you is dealt a character that limits your weapon classes and spells. Revealed when the Covenant begins.';
  const lore=value?.startsWith('lore:')&&TC_LORE_THEMES[value.slice(5)];
  if(lore)return `${lore.line} Draws lean toward its arms, some Rites are its own. Infuse with ${lore.affinity} where you can.`;
  return 'No theme: weapons are drawn as usual.';
}
document.addEventListener('click',event=>{
  const chip=event.target.closest('[data-theme-pick]');if(!chip)return;
  event.preventDefault();const box=chip.closest('.tc-theme-pick');
  box.querySelectorAll('[data-theme-pick]').forEach(c=>{const on=c===chip;c.classList.toggle('on',on);c.setAttribute('aria-pressed',String(on));});
  const help=box.querySelector('[data-theme-help]');if(help)help.textContent=tcThemeHelp(chip.dataset.themePick);
});
const tcReadTwistsBeforeTheme=tcReadTwists;
tcReadTwists=function(root=document){
  const rules=tcReadTwistsBeforeTheme(root)||{};
  const value=root.querySelector?.('[data-theme-pick].on')?.dataset.themePick||'none';
  if(value==='character')rules.theme={kind:'character'};
  else if(value.startsWith('lore:'))rules.theme={kind:'lore',id:value.slice(5)};
  return Object.values(rules).some(Boolean)?rules:undefined;
};

// Showing the theme: on the Weapons tab, and in Settings.
function tcThemeMarkup(state){
  const t=tcTheme(state);if(!t)return '';
  if(t.kind==='lore'){const l=TC_LORE_THEMES[t.id];return `<section class="tc-theme-card"><h5>${h(l.name)} Covenant</h5><p>${h(l.line)} Draws lean toward its arms.</p><p class="tc-theme-rules">Infuse with ${h(l.affinity)} where you can. ${h(l.spells)}</p></section>`;}
  return ['chase','morgan'].map(slot=>{const ch=tcCharacterFor(state,slot);if(!ch)return '';const w=state.current?.[slot]?.name,fits=tcBuildFits(state,slot,state.current?.[slot]);
    return `<section class="tc-theme-card"><h5>${h(playerLabel(slot,state))} · ${h(ch.name)}</h5><p>${h(ch.classes.join(', '))}.</p><p class="tc-theme-rules">${h(ch.spells)} Infuse with ${h(ch.affinity)}. ${h(ch.armor)}</p>${w&&!fits?`<p class="tc-theme-off">This region had nothing in your classes, so ${h(w)} stands in.</p>`:''}</section>`;}).join('');
}
function tcDecorateTheme(){
  const state=run?.state;if(!tcTheme(state))return;
  const weapons=app.querySelector('.tc-encounter-panel[data-panel="weapons"]');if(!weapons)return;
  const cards=weapons.querySelectorAll('.tc-loadout');if(!cards.length)return;
  const html=tcThemeMarkup(state);let box=weapons.querySelector('.tc-theme-box');
  if(!box){box=document.createElement('div');box.className='tc-theme-box';const anchor=weapons.querySelector('.tc-kit-box')||(cards[0].parentElement!==weapons?cards[0].parentElement:cards[cards.length-1]);anchor.after(box);}
  if(box.dataset.sig!==html){box.dataset.sig=html;box.innerHTML=html;}
}
if(!window.__tcThemeBound){
  window.__tcThemeBound=true;let queued=false;
  const go=()=>{queued=false;try{tcDecorateTheme();}catch(error){console.warn('Theme decoration skipped',error);}};
  const start=()=>new MutationObserver(()=>{if(queued||!app.querySelector('.tc-encounter-shell'))return;queued=true;requestAnimationFrame(go);}).observe(document.body,{childList:true,subtree:true});
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
}
/* --- End themed runs --- */
