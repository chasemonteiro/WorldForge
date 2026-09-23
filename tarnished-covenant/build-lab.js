/* Persistent Tarnished build lab. Weapon math adapted from Tom Clark's
   MIT-licensed Elden Ring Weapon Calculator; see THIRD_PARTY_NOTICES.md. */
(() => {
  const ATTRS=['str','dex','int','fai','arc'];
  const CORE_ATTRS=['vig','mind','end','str','dex','int','fai','arc'];
  const DAMAGE=[0,1,2,3,4], STATUS=[5,6,7,8,9,10,11];
  const TYPE_LABELS={0:'Physical',1:'Magic',2:'Fire',3:'Lightning',4:'Holy',5:'Poison',6:'Scarlet Rot',7:'Blood Loss',8:'Frost',9:'Sleep',10:'Madness',11:'Death Blight'};
  const AFFINITIES={[-1]:'Unique',0:'Standard',1:'Heavy',2:'Keen',3:'Quality',4:'Fire',5:'Flame Art',6:'Lightning',7:'Sacred',8:'Magic',9:'Cold',10:'Poison',11:'Blood',12:'Occult'};
  const BOW_TYPES=new Set([50,51,53,56]);
  const SCADU=[1,1.10,1.20,1.25,1.30,1.35,1.42,1.50,1.55,1.60,1.65,1.75,1.85,1.875,1.90,1.925,1.95,1.975,2.00,2.025,2.05];
  const STARTING_CLASSES={
    vagabond:{label:'Vagabond',level:9,vig:15,mind:10,end:11,str:14,dex:13,int:9,fai:9,arc:7},
    warrior:{label:'Warrior',level:8,vig:11,mind:12,end:11,str:10,dex:16,int:10,fai:8,arc:9},
    hero:{label:'Hero',level:7,vig:14,mind:9,end:12,str:16,dex:9,int:7,fai:8,arc:11},
    bandit:{label:'Bandit',level:5,vig:10,mind:11,end:10,str:9,dex:13,int:9,fai:8,arc:14},
    astrologer:{label:'Astrologer',level:6,vig:9,mind:15,end:9,str:8,dex:12,int:16,fai:7,arc:9},
    prophet:{label:'Prophet',level:7,vig:10,mind:14,end:8,str:11,dex:10,int:7,fai:16,arc:10},
    samurai:{label:'Samurai',level:9,vig:12,mind:11,end:13,str:12,dex:15,int:9,fai:8,arc:8},
    prisoner:{label:'Prisoner',level:9,vig:11,mind:12,end:11,str:11,dex:14,int:14,fai:6,arc:9},
    confessor:{label:'Confessor',level:10,vig:10,mind:13,end:10,str:12,dex:12,int:9,fai:14,arc:9},
    wretch:{label:'Wretch',level:1,vig:10,mind:10,end:10,str:10,dex:10,int:10,fai:10,arc:10},
    idusKnight:{label:'Idus Knight · Tarnished Edition',level:7,vig:10,mind:12,end:11,str:13,dex:15,int:8,fai:11,arc:6},
    heavyKnight:{label:'Heavy Knight · Tarnished Edition',level:10,vig:14,mind:8,end:17,str:15,dex:11,int:7,fai:8,arc:9}
  };
  const TALISMAN_NAMES=`Aged One's Exultation|Ailment Talisman|Ancestral Spirit's Horn|Arrow's Reach Talisman|Arrow's Soaring Sting Talisman|Arrow's Sting Talisman|Arsenal Charm|Arsenal Charm +1|Assassin's Cerulean Dagger|Assassin's Crimson Dagger|Axe Talisman|Beloved Stardust|Blade of Mercy|Blessed Blue Dew Talisman|Blessed Dew Talisman|Blue Dancer Charm|Blue-Feathered Branchsword|Boltdrake Talisman|Boltdrake Talisman +1|Boltdrake Talisman +2|Boltdrake Talisman +3|Bull-Goat's Talisman|Carian Filigreed Crest|Cerulean Amber Medallion|Cerulean Amber Medallion +1|Cerulean Amber Medallion +2|Cerulean Amber Medallion +3|Cerulean Seed Talisman|Cerulean Seed Talisman +1|Clarifying Horn Charm|Clarifying Horn Charm +1|Clarifying Horn Charm +2|Claw Talisman|Companion Jar|Concealing Veil|Crepus's Vial|Crimson Amber Medallion|Crimson Amber Medallion +1|Crimson Amber Medallion +2|Crimson Amber Medallion +3|Crimson Seed Talisman|Crimson Seed Talisman +1|Crucible Feather Talisman|Crucible Knot Talisman|Crucible Scale Talisman|Crusade Insignia|Curved Sword Talisman|Daedicar's Woe|Dagger Talisman|Dragoncrest Greatshield Talisman|Dragoncrest Shield Talisman|Dragoncrest Shield Talisman +1|Dragoncrest Shield Talisman +2|Dried Bouquet|Enraged Divine Beast|Erdtree's Favor|Erdtree's Favor +1|Erdtree's Favor +2|Faithful's Canvas Talisman|Fine Crucible Feather Talisman|Fire Scorpion Charm|Flamedrake Talisman|Flamedrake Talisman +1|Flamedrake Talisman +2|Flamedrake Talisman +3|Flock's Canvas Talisman|Furled Finger's Trick-Mirror|Godfrey Icon|Godskin Swaddling Cloth|Gold Scarab|Golden Braid|Graven-Mass Talisman|Graven-School Talisman|Great-Jar's Arsenal|Greatshield Talisman|Green Turtle Talisman|Haligdrake Talisman|Haligdrake Talisman +1|Haligdrake Talisman +2|Hammer Talisman|Host's Trick-Mirror|Immunizing Horn Charm|Immunizing Horn Charm +1|Immunizing Horn Charm +2|Kindred of Rot's Exultation|Lacerating Crossed-Tree|Lance Talisman|Lightning Scorpion Charm|Longtail Cat Talisman|Lord of Blood's Exultation|Magic Scorpion Charm|Marika's Scarseal|Marika's Soreseal|Millicent's Prosthesis|Moon of Nokstella|Mottled Necklace|Mottled Necklace +1|Mottled Necklace +2|Old Lord's Talisman|Outer God Heirloom|Pearl Shield Talisman|Pearldrake Talisman|Pearldrake Talisman +1|Pearldrake Talisman +2|Pearldrake Talisman +3|Perfumer's Talisman|Primal Glintstone Blade|Prince of Death's Cyst|Prince of Death's Pustule|Prosthesis-Wearer Heirloom|Radagon Icon|Radagon's Scarseal|Radagon's Soreseal|Red-Feathered Branchsword|Rellana's Cameo|Retaliatory Crossed-Tree|Ritual Shield Talisman|Ritual Sword Talisman|Roar Medallion|Rotten Winged Sword Insignia|Sacred Scorpion Charm|Sacrificial Twig|Shabriri's Woe|Shard of Alexander|Sharpshot Talisman|Shattered Stone Talisman|Silver Scarab|Smithing Talisman|Spear Talisman|Spelldrake Talisman|Spelldrake Talisman +1|Spelldrake Talisman +2|Spelldrake Talisman +3|St. Trina's Smile|Stalwart Horn Charm|Stalwart Horn Charm +1|Stalwart Horn Charm +2|Stargazer Heirloom|Starscourge Heirloom|Taker's Cameo|Talisman of All Crucibles|Talisman of Lord's Bestowal|Talisman of the Dread|Twinblade Talisman|Two Fingers Heirloom|Two-Handed Sword Talisman|Two-Headed Turtle Talisman|Verdigris Discus|Viridian Amber Medallion|Viridian Amber Medallion +1|Viridian Amber Medallion +2|Viridian Amber Medallion +3|Warrior Jar Shard|Winged Sword Insignia`.split('|');
  const PHYSICK_NAMES=`Bloodsucking Cracked Tear|Cerulean Crystal Tear|Cerulean Hidden Tear|Cerulean-Sapping Cracked Tear|Crimson Bubbletear|Crimson Crystal Tear|Crimson-Sapping Cracked Tear|Crimsonburst Crystal Tear|Crimsonburst Dried Tear|Crimsonspill Crystal Tear|Crimsonwhorl Bubbletear|Deflecting Hardtear|Dexterity-knot Crystal Tear|Faith-knot Crystal Tear|Flame-Shrouding Cracked Tear|Glovewort Crystal Tear|Greenburst Crystal Tear|Greenspill Crystal Tear|Holy-Shrouding Cracked Tear|Intelligence-knot Crystal Tear|Leaden Hardtear|Lightning-Shrouding Cracked Tear|Magic-Shrouding Cracked Tear|Oil-Soaked Tear|Opaline Bubbletear|Opaline Hardtear|Purifying Crystal Tear|Ruptured Crystal Tear|Speckled Hardtear|Spiked Cracked Tear|Stonebarb Cracked Tear|Strength-knot Crystal Tear|Thorny Cracked Tear|Twiggy Cracked Tear|Viridian Hidden Tear|Windy Crystal Tear|Winged Crystal Tear`.split('|');
  const STAT_TALISMANS={
    'starscourge heirloom':{str:5},'prosthesis-wearer heirloom':{dex:5},'stargazer heirloom':{int:5},'two fingers heirloom':{fai:5},'outer god heirloom':{arc:5},
    "radagon's scarseal":{str:3,dex:3},"radagon's soreseal":{str:5,dex:5},"marika's scarseal":{int:3,fai:3,arc:3},"marika's soreseal":{int:5,fai:5,arc:5},
    'millicent’s prosthesis':{dex:5},"millicent's prosthesis":{dex:5}
  };
  const STAT_PHYSICK={
    'strength-knot crystal tear':{str:10},'dexterity-knot crystal tear':{dex:10},
    'intelligence-knot crystal tear':{int:10},'faith-knot crystal tear':{fai:10}
  };
  const PHYSICK_NOTES={
    'bloodsucking cracked tear':'Physick active: boosts all damage by 20% while continuously draining HP; this conditional boost is not folded into menu AR.',
    'flame-shrouding cracked tear':'Physick active: boosts fire damage by 20% for 3 minutes.',
    'holy-shrouding cracked tear':'Physick active: boosts holy damage by 20% for 3 minutes.',
    'lightning-shrouding cracked tear':'Physick active: boosts lightning damage by 20% for 3 minutes.',
    'magic-shrouding cracked tear':'Physick active: boosts magic damage by 20% for 3 minutes.',
    'spiked cracked tear':'Physick active: charged attacks deal more damage; this conditional boost is not menu AR.',
    'thorny cracked tear':'Physick active: successive attacks build a damage bonus; this conditional boost is not menu AR.',
    'stonebarb cracked tear':'Physick active: attacks deal more stance damage; weapon AR is unchanged.',
    'oil-soaked tear':'Physick active: nearby enemies become more vulnerable to fire; weapon AR is unchanged.'
  };
  const CONDITIONAL_TALISMANS={
    'two-handed sword talisman':'Two-handed attacks deal 15% more damage; this is conditional damage, not menu AR.',
    'axe talisman':'Charged heavy attacks deal 10% more damage.',
    'claw talisman':'Jump attacks deal 15% more damage.',
    'spear talisman':'Piercing counterattacks deal 15% more damage.',
    'dagger talisman':'Critical attacks deal 17% more damage.',
    'shard of alexander':'Weapon skills deal 15% more damage.',
    'warrior jar shard':'Weapon skills deal 10% more damage.',
    'ritual sword talisman':'Damage increases by 10% while HP is full.',
    'red-feathered branchsword':'Damage increases by 20% while HP is below 20%.',
    'lord of blood’s exultation':'Damage increases by 20% for 20 seconds after nearby blood loss.',
    "lord of blood's exultation":'Damage increases by 20% for 20 seconds after nearby blood loss.',
    'kindred of rot’s exultation':'Damage increases by 20% for 20 seconds after nearby poison or rot.',
    "kindred of rot's exultation":'Damage increases by 20% for 20 seconds after nearby poison or rot.',
    'rotten winged sword insignia':'Successive attacks build a 6% / 8% / 13% damage bonus.',
    'winged sword insignia':'Successive attacks build a 3% / 5% / 10% damage bonus.',
    'millicent’s prosthesis':'Adds 5 Dexterity; successive attacks build a 4% / 6% / 11% damage bonus.',
    "millicent's prosthesis":'Adds 5 Dexterity; successive attacks build a 4% / 6% / 11% damage bonus.',
    'blue dancer charm':'Raises physical damage at low equip load; the exact bonus depends on total carried weight.'
  };

  let tcWeaponData=null,tcWeaponDataPromise=null,tcBuildSlot=null,tcBuildDirty=false,tcBuildAutosaveTimer=null,tcBuildAutosaveDraft=null,tcBuildAutosaveSlot=null,tcBuildChangeSeq=0;
  const graphCache=new Map();

  function blankBuild(){return {startingClass:'',level:1,vig:10,mind:10,end:10,str:10,dex:10,int:10,fai:10,arc:10,scadu:0,talismans:['','','',''],physickTears:['',''],weapon:{weaponName:'',variantName:'',upgrade:0}};}
  function itemKey(value){return String(value||'').trim().toLowerCase().replace(/[’‘]/g,"'").replace(/\s+/g,' ');}
  const PHYSICK_DUPLICATES_ALLOWED=new Set(['Crimson Crystal Tear','Cerulean Crystal Tear','Ruptured Crystal Tear'].map(itemKey));
  function talismanFamilyKey(value){
    let key=itemKey(value).replace(/\s+\+\d+$/,'');
    if(!key)return '';
    if(key==="radagon's scarseal"||key==="radagon's soreseal")return 'radagon-seal';
    if(key==="marika's scarseal"||key==="marika's soreseal")return 'marika-seal';
    if(key==='arsenal charm'||key==="great-jar's arsenal")return 'arsenal';
    if(key==='warrior jar shard'||key==='shard of alexander')return 'jar-shard';
    if(key==='winged sword insignia'||key==='rotten winged sword insignia')return 'winged-sword';
    if(key==="arrow's reach talisman"||key==="arrow's soaring sting talisman")return 'arrow-reach';
    if(key==="prince of death's cyst"||key==="prince of death's pustule")return 'prince-of-death';
    if(key==='green turtle talisman'||key==='two-headed turtle talisman')return 'turtle';
    if(key==='dragoncrest greatshield talisman'||key==='dragoncrest shield talisman')return 'dragoncrest';
    return key;
  }
  function normalizeTalismanSlots(values,length=4){
    const seen=new Set();
    return Array.from({length},(_,i)=>{
      const value=String(Array.isArray(values)?values[i]||'':'').trim(),family=talismanFamilyKey(value);
      if(!value||seen.has(family))return '';
      seen.add(family);return value;
    });
  }
  function normalizePhysickSlots(values,length=2){
    const seen=new Map();
    return Array.from({length},(_,i)=>{
      const value=String(Array.isArray(values)?values[i]||'':'').trim(),key=itemKey(value);
      if(!value)return '';
      const count=seen.get(key)||0;
      if(count&&!PHYSICK_DUPLICATES_ALLOWED.has(key))return '';
      if(count>=2)return '';
      seen.set(key,count+1);return value;
    });
  }
  function classPreset(key){return STARTING_CLASSES[String(key||'')]||null;}
  function levelForClassStats(classKey,build){
    const preset=classPreset(classKey);if(!preset)return Math.max(1,Math.min(713,Number(build?.level)||1));
    const spent=CORE_ATTRS.reduce((sum,key)=>sum+Math.max(0,(Number(build?.[key])||preset[key])-preset[key]),0);
    return Math.min(713,preset.level+spent);
  }
  function normalizeBuild(value){
    const base=blankBuild(),src=value&&typeof value==='object'?value:{};
    base.startingClass=classPreset(src.startingClass)?src.startingClass:'';
    for(const key of CORE_ATTRS)base[key]=Math.max(1,Math.min(99,Number(src[key]??base[key])||base[key]));
    const preset=classPreset(base.startingClass);
    if(preset){
      for(const key of CORE_ATTRS)base[key]=Math.max(preset[key],base[key]);
      base.level=Math.max(preset.level,Math.min(713,Number(src.level??preset.level)||preset.level));
    }else{
      base.level=Math.max(1,Math.min(713,Number(src.level??base.level)||base.level));
    }
    base.scadu=Math.max(0,Math.min(20,Number(src.scadu)||0));
    base.talismans=normalizeTalismanSlots(src.talismans,4);
    base.physickTears=normalizePhysickSlots(src.physickTears,2);
    base.weapon={...base.weapon,...(src.weapon&&typeof src.weapon==='object'?src.weapon:{})};
    base.weapon.weaponName=String(base.weapon.weaponName||'');base.weapon.variantName=String(base.weapon.variantName||'');base.weapon.upgrade=Math.max(0,Number(base.weapon.upgrade)||0);
    return base;
  }
  function ensureBuilds(state){
    if(!state.builds||typeof state.builds!=='object')state.builds={};
    state.builds.chase=normalizeBuild(state.builds.chase);
    state.builds.morgan=normalizeBuild(state.builds.morgan);
    return state;
  }
  function ownSlot(){return playerName()==='Morgan'?'morgan':'chase';}
  function selectedSlot(){return tcBuildSlot||(tcBuildSlot=ownSlot());}
  function buildFor(slot=selectedSlot()){ensureBuilds(run.state);return normalizeBuild(run.state.builds[slot]);}
  function markDirty(value=true){
    tcBuildDirty=value;const el=document.querySelector('.tc-build-save-state');
    if(el){el.classList.toggle('dirty',value);el.textContent=value?'Unsaved changes':'Saved to the Covenant';}
  }
  function talismanDeltas(build){
    const out={str:0,dex:0,int:0,fai:0,arc:0};
    for(const raw of build.talismans){const delta=STAT_TALISMANS[String(raw||'').trim().toLowerCase()];if(delta)for(const key of ATTRS)out[key]+=Number(delta[key]||0);}
    return out;
  }
  function physickDeltas(build){const out={str:0,dex:0,int:0,fai:0,arc:0};for(const raw of build.physickTears){const delta=STAT_PHYSICK[String(raw||'').trim().toLowerCase()];if(delta)for(const key of ATTRS)out[key]+=Number(delta[key]||0);}return out;}
  function effectiveAttrs(build){const t=talismanDeltas(build),p=physickDeltas(build),out={};for(const key of ATTRS)out[key]=Math.min(99,Math.max(1,Number(build[key])||1)+t[key]+p[key]);return out;}
  function applyClassConstraintsToInputs(){
    const classKey=document.querySelector('#tcBuildClass')?.value||'',preset=classPreset(classKey),level=document.querySelector('[data-build-field="level"]');
    for(const key of CORE_ATTRS){
      const field=document.querySelector(`[data-build-field="${key}"]`);if(!field)continue;
      const min=preset?Number(preset[key]):1;field.min=String(min);
      if(Number(field.value)<min)field.value=String(min);
    }
    if(level){
      level.min=String(preset?Number(preset.level):1);
      if(Number(level.value)<Number(level.min))level.value=level.min;
      level.readOnly=false;level.removeAttribute('aria-readonly');
      document.querySelectorAll('[data-step-field="level"]').forEach(b=>b.disabled=false);
    }
  }
  function refreshTalismanAvailability(){
    const selects=[...document.querySelectorAll('[data-talisman]')];
    for(const select of selects){
      const otherFamilies=new Set(selects.filter(x=>x!==select&&x.value).map(x=>talismanFamilyKey(x.value)).filter(Boolean));
      for(const option of select.options){
        if(!option.value){option.disabled=false;continue;}
        option.disabled=otherFamilies.has(talismanFamilyKey(option.value))&&option.value!==select.value;
      }
    }
  }
  function refreshBuildStatus(build=null){
    const host=document.querySelector('#tcBuildStatus');if(!host)return;
    const draft=build||currentDraft(),preset=classPreset(draft.startingClass),eff=effectiveAttrs(draft),t=talismanDeltas(draft),p=physickDeltas(draft),implied=preset?levelForClassStats(draft.startingClass,draft):null,mismatch=Boolean(preset&&implied!==draft.level);
    const classText=preset?`${preset.label} · Entered Level ${draft.level}`:`Custom stats · Level ${draft.level}`;
    const validation=mismatch?`<div class="tc-level-check warn"><span>Entered attributes imply Level <b>${implied}</b> from ${h(preset.label)}.</span><button type="button" data-sync-build-level="${implied}">Sync Level to ${implied}</button></div>`:`<div class="tc-level-check ok">${preset?'✓ Entered Level matches points spent from this class':'Level is manual in Custom mode'}</div>`;
    const stats=ATTRS.map(key=>{const bonus=(t[key]||0)+(p[key]||0),value=eff[key];return `<span class="${bonus?'boosted':''}">${key.toUpperCase()} <b>${value}</b>${bonus?`<small>+${bonus}</small>`:''}</span>`;}).join('');
    host.innerHTML=`<div class="tc-build-status-line"><strong>${h(classText)}</strong><span>${preset?'Class minimums enforced · Level is never changed automatically':'Choose a starting class for a level/stat consistency check'}</span></div>${validation}<div class="tc-effective-stats"><em>Weapon-effective stats</em>${stats}</div>`;
  }
  function currentDraft(){
    const base=buildFor();
    base.startingClass=document.querySelector('#tcBuildClass')?.value||'';
    document.querySelectorAll('[data-build-field]').forEach(el=>{const key=el.dataset.buildField;base[key]=Math.max(Number(el.min)||0,Math.min(Number(el.max)||999,Number(el.value)||0));});
    base.talismans=Array.from(document.querySelectorAll('[data-talisman]')).map(el=>el.value.trim()).slice(0,4);
    base.physickTears=Array.from(document.querySelectorAll('[data-physick]')).map(el=>el.value.trim()).slice(0,2);
    const weaponInput=document.querySelector('#tcBuildWeaponName');
    const weaponName=weaponInput?.dataset.selectedWeapon||'';
    const affinityValue=document.querySelector('#tcBuildAffinity')?.value||'';
    const variantName=tcWeaponData&&variantsFor(weaponName).some(w=>w.name===affinityValue)?affinityValue:base.weapon.variantName;
    const upgrade=Math.max(0,Number(document.querySelector('#tcBuildUpgrade')?.value)||0);
    base.weapon={weaponName,variantName,upgrade};return normalizeBuild(base);
  }
  function scheduleBuildSave(){
    clearTimeout(tcBuildAutosaveTimer);
    const changeSeq=++tcBuildChangeSeq;
    tcBuildAutosaveSlot=selectedSlot();tcBuildAutosaveDraft=currentDraft();markDirty(true);
    tcBuildAutosaveTimer=setTimeout(()=>{const draft=tcBuildAutosaveDraft,slot=tcBuildAutosaveSlot;tcBuildAutosaveTimer=null;if(draft&&slot)saveBuild({slot,draft,automatic:true,changeSeq});},650);
  }
  function loadWeaponData(){
    if(tcWeaponData)return Promise.resolve(tcWeaponData);
    if(!tcWeaponDataPromise)tcWeaponDataPromise=fetch('./assets/build/weapon-data-v1.17.json.gz',{cache:'force-cache'}).then(async r=>{
      if(!r.ok)throw new Error(`Weapon data failed to load (${r.status})`);
      const bytes=new Uint8Array(await r.arrayBuffer());
      if(bytes[0]===0x1f&&bytes[1]===0x8b){
        if(typeof DecompressionStream==='undefined')throw new Error('This browser cannot open compressed weapon records.');
        return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).json();
      }
      return JSON.parse(new TextDecoder().decode(bytes));
    }).then(data=>tcWeaponData=data);
    return tcWeaponDataPromise;
  }
  function evaluateGraph(stages){
    const key=JSON.stringify(stages);if(graphCache.has(key))return graphCache.get(key);const arr=[];
    for(let i=1;i<stages.length;i++){const prev=stages[i-1],stage=stages[i],min=i===1?1:prev.maxVal+1,max=i===stages.length-1?148:stage.maxVal;for(let value=min;value<=max;value++){if(arr[value])continue;let ratio=Math.max(0,Math.min(1,(value-prev.maxVal)/(stage.maxVal-prev.maxVal)));if(prev.adjPt>0)ratio=ratio**prev.adjPt;else if(prev.adjPt<0)ratio=1-(1-ratio)**(-prev.adjPt);arr[value]=prev.maxGrowVal+(stage.maxGrowVal-prev.maxGrowVal)*ratio;}}
    graphCache.set(key,arr);return arr;
  }
  function decodeWeapon(raw){
    const data=tcWeaponData,reinforce=data.reinforceTypes[raw.reinforceTypeId],aec={...(data.attackElementCorrects[raw.attackElementCorrectId]||{})};
    aec[5]={arc:true};aec[7]={arc:true};aec[10]={arc:true};aec[9]={};aec[6]={};aec[8]={};aec[11]={};
    const graphs={};for(const type of DAMAGE)graphs[type]=evaluateGraph(data.calcCorrectGraphs[(raw.calcCorrectGraphIds||{})[type]??0]);for(const type of STATUS)graphs[type]=evaluateGraph(data.calcCorrectGraphs[(raw.calcCorrectGraphIds||{})[type]??6]);
    const attack=reinforce.map(param=>{const row={};for(const [type,value] of raw.attack)row[type]=value*(param.attack[type]??0);const offsets=[param.statusSpEffectId1,param.statusSpEffectId2,param.statusSpEffectId3];(raw.statusSpEffectParamIds||[]).forEach((id,i)=>{if(id)Object.assign(row,data.statusSpEffectParams[id+(offsets[i]||0)]||{});});return row;});
    const scaling=reinforce.map(param=>{const row={};for(const [attr,value] of raw.attributeScaling)row[attr]=value*param.attributeScaling[attr];return row;});
    return {...raw,attack,attributeScaling:scaling,attackElementCorrect:aec,calcCorrectGraphs:graphs,scalingTiers:data.scalingTiers};
  }
  function adjustedAttrs(weapon,attrs,twoHand){
    let bonus=twoHand;if(weapon.paired)bonus=false;if(BOW_TYPES.has(weapon.weaponType))bonus=true;
    return bonus?{...attrs,str:Math.floor(attrs.str*1.5)}:attrs;
  }
  function calculate(raw,build,twoHand){
    const weapon=decodeWeapon(raw),level=Math.min(build.weapon.upgrade,weapon.attack.length-1),attrs=effectiveAttrs(build),adjusted=adjustedAttrs(weapon,attrs,twoHand);
    const unmet=Object.entries(weapon.requirements).filter(([a,n])=>adjusted[a]<n).map(([a])=>a),attack={},spellScaling={},ineffective=[];
    for(const type of [...DAMAGE,...STATUS]){const base=weapon.attack[level][type]||0;if(!base&&!weapon.sorceryTool&&!weapon.incantationTool)continue;const scalingAttrs=weapon.attackElementCorrect[type]||{};let total=1;if(unmet.some(a=>scalingAttrs[a])){total=.6;ineffective.push(type);}else{for(const attr of ATTRS){const correction=scalingAttrs[attr];if(!correction)continue;const scaling=correction===true?(weapon.attributeScaling[level][attr]||0):(correction*(weapon.attributeScaling[level][attr]||0))/(weapon.attributeScaling[0][attr]||1);if(scaling)total+=(weapon.calcCorrectGraphs[type][DAMAGE.includes(type)?adjusted[attr]:attrs[attr]]||0)*scaling;}}if(base)attack[type]=base*total;if(DAMAGE.includes(type)&&(weapon.sorceryTool||weapon.incantationTool))spellScaling[type]=100*total;}
    return {weapon,level,attack,spellScaling,unmet,ineffective,total:DAMAGE.reduce((sum,t)=>sum+(attack[t]||0),0)};
  }
  function variantsFor(name){return tcWeaponData?.weapons?.filter(w=>w.weaponName===name)||[];}
  function rawFor(build){const list=variantsFor(build.weapon.weaponName);return list.find(w=>w.name===build.weapon.variantName)||list[0]||null;}
  function affinityLabel(raw){return AFFINITIES[raw.affinityId]||raw.name.replace(raw.weaponName,'').trim()||'Standard';}
  function round(value){return Math.floor(Number(value||0)+1e-9);}
  function scalingLabel(weapon,level,attr){const value=weapon.attributeScaling[level][attr];return value?weapon.scalingTiers.find(([minimum])=>value>=minimum)?.[1]||'—':'—';}
  function conditionalNotes(build){return [...new Set([...build.talismans.map(x=>CONDITIONAL_TALISMANS[String(x||'').trim().toLowerCase()]),...build.physickTears.map(x=>PHYSICK_NOTES[String(x||'').trim().toLowerCase()])].filter(Boolean))];}
  function resultMarkup(build,raw){
    if(!raw)return `<div class="tc-weapon-empty">Choose a weapon to calculate its attack rating with this build.</div>`;
    const one=calculate(raw,build,false),two=calculate(raw,build,true),scadu=SCADU[build.scadu]||1,talismanBonus=talismanDeltas(build),physickBonus=physickDeltas(build),attrs=effectiveAttrs(build);
    const damage=[...new Set([...Object.keys(one.attack),...Object.keys(two.attack)].map(Number))].filter(t=>DAMAGE.includes(t)&&((one.attack[t]||two.attack[t])>0));
    const statuses=[...new Set([...Object.keys(one.attack),...Object.keys(two.attack)].map(Number))].filter(t=>STATUS.includes(t)&&((one.attack[t]||two.attack[t])>0));
    const requirements=ATTRS.filter(a=>raw.requirements[a]).map(a=>`<div class="${one.unmet.includes(a)?'unmet':''}"><span>${a.toUpperCase()}</span><b>${raw.requirements[a]}</b></div>`).join('')||'<div><span>Requirements</span><b>None</b></div>';
    const scaling=ATTRS.filter(a=>one.weapon.attributeScaling[one.level][a]).map(a=>`<div><span>${a.toUpperCase()}</span><b>${scalingLabel(one.weapon,one.level,a)}</b></div>`).join('')||'<div><span>Scaling</span><b>—</b></div>';
    const deltaText=ATTRS.filter(a=>talismanBonus[a]||physickBonus[a]).map(a=>`${a.toUpperCase()} +${talismanBonus[a]+physickBonus[a]}`).join(' · ');
    const notes=conditionalNotes(build),oneOk=!one.unmet.length,twoOk=!two.unmet.length,isBow=BOW_TYPES.has(two.weapon.weaponType),isCatalyst=Boolean(raw.sorceryTool||raw.incantationTool),spellType=raw.sorceryTool?1:(raw.incantationTool?4:null),spellLabel=raw.sorceryTool?'Sorcery Scaling':'Incant Scaling',oneSpell=spellType===null?0:round(one.spellScaling[spellType]),twoSpell=spellType===null?0:round(two.spellScaling[spellType]);
    const ranked=variantsFor(build.weapon.weaponName).map(candidate=>{const a=calculate(candidate,build,false),b=calculate(candidate,build,true);return {raw:candidate,one:round(a.total),two:round(b.total)};}).sort((a,b)=>Math.max(b.one,b.two)-Math.max(a.one,a.two));
    return `<div class="tc-ar-hero">
      <div class="tc-ar-card ${(!isBow&&oneOk)?'valid':'invalid'}"><span class="mode">${isBow?'one-handed reference':'one-handed AR'}</span><strong>${round(one.total)}</strong><small>${h(raw.name)} +${one.level}</small><div class="tc-ar-validity ${(!isBow&&oneOk)?'ok':'bad'}">${isBow?'Bow attacks require two hands':oneOk?'✓ Requirements met':`Needs ${one.unmet.map(a=>a.toUpperCase()).join(' / ')}`}</div>${build.scadu?`<div class="shadow">Shadow Realm · ${round(one.total*scadu)} AR</div>`:''}</div>
      <div class="tc-ar-card ${twoOk?'valid':'invalid'}"><span class="mode">two-handed AR</span><strong>${round(two.total)}</strong><small>${two.weapon.paired?'Paired weapon · no STR bonus':isBow?'Two-handing required':`Effective STR ${adjustedAttrs(two.weapon,attrs,true).str}`}</small><div class="tc-ar-validity ${twoOk?'ok':'bad'}">${twoOk?'✓ Requirements met':`Needs ${two.unmet.map(a=>a.toUpperCase()).join(' / ')}`}</div>${build.scadu?`<div class="shadow">Shadow Realm · ${round(two.total*scadu)} AR</div>`:''}</div>
    </div>
    ${isCatalyst?`<div class="tc-spell-scaling"><div><span>${spellLabel}</span><strong>${oneSpell}</strong><small>1H</small></div><div><span>${spellLabel}</span><strong>${twoSpell}</strong><small>2H</small></div><p>Spell scaling uses the same Regulation 1.17 attribute curves as the weapon calculator. Strength-scaling catalysts may improve when two-handed.</p></div>`:''}
    <div class="tc-weapon-meta">
      <div class="tc-weapon-slip"><span>Damage & buildup · 1H / 2H</span><div class="tc-damage-grid">${damage.map(t=>`<div><span>${TYPE_LABELS[t]}</span><b>${round(one.attack[t])} / ${round(two.attack[t])}</b></div>`).join('')}${statuses.map(t=>`<div><span>${TYPE_LABELS[t]}</span><b>${round(one.attack[t])}</b></div>`).join('')}</div></div>
      <div class="tc-weapon-slip"><span>Requirements & scaling</span><div class="tc-requirement-grid">${requirements}${scaling}</div></div>
    </div>
    ${one.unmet.length?`<div class="tc-weapon-note warn">Requirements not met one-handed: ${one.unmet.map(a=>a.toUpperCase()).join(', ')}. The calculator has applied the in-game attack penalty.</div>`:''}
    ${deltaText?`<div class="tc-weapon-note">Effective combat stats include active talisman and Physick bonuses: ${deltaText}.</div>`:''}
    ${build.scadu?`<div class="tc-weapon-note">Scadutree Blessing +${build.scadu} uses the current Shadow Realm damage multiplier (×${scadu}). It does not affect damage outside the Realm of Shadow.</div>`:''}
    ${isCatalyst?`<div class="tc-weapon-note">For staffs and seals, the Spell Scaling panel is the casting-power number to compare. The AR cards above still describe the catalyst’s physical weapon strike.</div>`:''}
    ${notes.map(note=>`<div class="tc-weapon-note">${h(note)}</div>`).join('')}
    ${ranked.length>1?`<div class="tc-affinity-head"><strong>Best affinities for these stats</strong><span>Sorted by the higher displayed 1H/2H AR · tap to equip</span></div><div class="tc-affinity-table">${ranked.map((row,i)=>`<button type="button" class="tc-affinity-row ${row.raw.name===raw.name?'current':''}" data-affinity-pick="${h(row.raw.name)}"><span>${i+1}. ${h(affinityLabel(row.raw))}</span><small>1H</small><b>${row.one}</b><span></span><small>2H</small><b>${row.two}</b></button>`).join('')}</div>`:''}`;
  }
  function weaponNames(){return [...new Set((tcWeaponData?.weapons||[]).map(w=>w.weaponName))].sort((a,b)=>a.localeCompare(b));}
  function refreshWeaponSearchState(){
    const input=document.querySelector('#tcBuildWeaponName'),host=document.querySelector('#tcWeaponSearchState');if(!input||!host)return;
    const selected=String(input.dataset.selectedWeapon||'').trim(),typed=String(input.value||'').trim();
    if(typed&&itemKey(typed)!==itemKey(selected)){
      host.innerHTML=selected?`Searching for <b>${h(typed)}</b>. Calculations still use <b>${h(selected)}</b> until you choose a result.`:`Searching for <b>${h(typed)}</b>. Choose a result before calculations or saving can use it.`;
      host.classList.add('active');
    }else{host.textContent='';host.classList.remove('active');}
  }
  function closeWeaponPicker({restore=true}={}){
    const host=document.querySelector('#tcWeaponPicker'),input=document.querySelector('#tcBuildWeaponName');
    if(host){host.classList.remove('open');host.hidden=true;}
    if(restore&&input){input.value=String(input.dataset.selectedWeapon||'');}
    refreshWeaponSearchState();
  }
  function renderWeaponPicker(query=null){
    const input=document.querySelector('#tcBuildWeaponName'),host=document.querySelector('#tcWeaponPicker');if(!input||!host||!tcWeaponData)return;
    const names=weaponNames(),selected=String(input.dataset.selectedWeapon||'').trim();let raw=String(query??input.value??'').trim();
    if(selected&&raw.toLowerCase()===selected.toLowerCase())raw='';
    const q=raw.toLowerCase(),matches=q?names.filter(name=>name.toLowerCase().includes(q)):names;
    host.innerHTML=matches.length?matches.map(name=>`<button type="button" class="tc-weapon-option ${name===selected?'active':''}" data-weapon-pick="${h(name)}" role="option" aria-selected="${name===selected?'true':'false'}"><span>${h(name)}</span>${name===selected?'<small>Equipped</small>':''}</button>`).join(''):`<div class="tc-weapon-picker-empty">No weapons match “${h(raw)}”.</div>`;
    host.hidden=false;host.classList.add('open');refreshWeaponSearchState();
    if(!q&&selected){requestAnimationFrame(()=>{const active=[...host.querySelectorAll('[data-weapon-pick]')].find(el=>el.dataset.weaponPick===selected);if(active)host.scrollTop=Math.max(0,active.offsetTop-host.clientHeight/2+active.offsetHeight/2);});}
  }
  function setWeaponSelection(name,{close=true,save=true}={}){
    const input=document.querySelector('#tcBuildWeaponName');if(!input||!tcWeaponData)return false;
    const canonical=weaponNames().find(n=>n.toLowerCase()===String(name||'').trim().toLowerCase());if(!canonical)return false;
    input.value=canonical;input.dataset.selectedWeapon=canonical;if(close)closeWeaponPicker({restore:false});refreshWeaponSearchState();refreshResults();if(save)scheduleBuildSave();return true;
  }
  function populateWeaponControls(build){
    const input=document.querySelector('#tcBuildWeaponName'),affinity=document.querySelector('#tcBuildAffinity'),upgrade=document.querySelector('#tcBuildUpgrade');if(!input||!affinity||!upgrade||!tcWeaponData)return;
    const names=weaponNames();let selected=String(input.dataset.selectedWeapon||build.weapon.weaponName||'').trim();
    const canonical=names.find(n=>n.toLowerCase()===selected.toLowerCase())||'';
    selected=canonical;input.dataset.selectedWeapon=selected;
    if(document.activeElement!==input||!input.value)input.value=selected;
    const variants=variantsFor(selected);const current=affinity.value;const saved=variants.some(w=>w.name===current)?current:(variants.some(w=>w.name===build.weapon.variantName)?build.weapon.variantName:(variants[0]?.name||''));affinity.innerHTML=variants.length?variants.map(w=>`<option value="${h(w.name)}">${h(affinityLabel(w))}</option>`).join(''):'<option value="">Choose weapon first</option>';if(saved)affinity.value=saved;
    const raw=variants.find(w=>w.name===affinity.value)||variants[0];const max=raw?(tcWeaponData.reinforceTypes[raw.reinforceTypeId]?.length||1)-1:25;upgrade.max=max;const typed=Number(upgrade.value);const fallback=Math.max(0,Number(build.weapon.upgrade)||0);upgrade.value=Math.min(max,Number.isFinite(typed)?Math.max(0,typed):fallback);document.querySelector('#tcUpgradeMax').textContent=`max +${max}`;
  }
  function refreshResults(){applyClassConstraintsToInputs();const build=currentDraft();refreshBuildStatus(build);refreshTalismanAvailability();refreshWeaponSearchState();if(!tcWeaponData)return;populateWeaponControls(build);const raw=rawFor({...build,weapon:{...build.weapon,variantName:document.querySelector('#tcBuildAffinity')?.value||build.weapon.variantName}});build.weapon.variantName=raw?.name||'';const host=document.querySelector('#tcWeaponResults');if(host)host.innerHTML=resultMarkup(build,raw);}
  function renderBuild(){
    ensureBuilds(run.state);const slot=selectedSlot(),build=buildFor(slot),names=covenantNames(run.state);
    app.innerHTML=`<section class="tc-screen tc-build-screen">${screenTop('Tarnished Build')}
      <div class="tc-build-hero"><div class="tc-kicker gold">living character sheet</div><h1>Build</h1><p>Keep both Tarnished current, test every weapon, and stop leaving damage on the table.</p></div>
      <div class="tc-build-player-tabs"><button type="button" data-build-slot="chase" class="${slot==='chase'?'active':''}">${h(names[0])}</button><button type="button" data-build-slot="morgan" class="${slot==='morgan'?'active':''}">${h(names[1])}</button></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Attributes</h2><span>Current in-game values</span></div>
        <div class="tc-build-origin tc-build-field"><label for="tcBuildClass">Starting class</label><select id="tcBuildClass"><option value="">Custom / keep current stats</option>${Object.entries(STARTING_CLASSES).map(([key,value])=>`<option value="${key}" ${build.startingClass===key?'selected':''}>${h(value.label)}</option>`).join('')}</select><small>Choosing a class fills its base stats and enforces that class’s minimum attributes. Level stays exactly as entered; if your stats imply a different level, Build will flag it and offer a one-tap sync.</small></div>
        <div class="tc-build-stats">
        ${[['level','Level',713],['vig','Vigor',99],['mind','Mind',99],['end','Endurance',99],['str','Strength',99],['dex','Dexterity',99],['int','Intelligence',99],['fai','Faith',99],['arc','Arcane',99],['scadu','Scadutree',20]].map(([key,label,max])=>`<div class="tc-build-field"><label for="tcBuild-${key}">${label}</label><div class="tc-number-stepper"><button type="button" data-step-field="${key}" data-step="-1" aria-label="Decrease ${label}">−</button><input id="tcBuild-${key}" data-build-field="${key}" type="number" inputmode="numeric" min="${key==='scadu'?0:1}" max="${max}" value="${build[key]}"><button type="button" data-step-field="${key}" data-step="1" aria-label="Increase ${label}">+</button></div></div>`).join('')}
      </div><div id="tcBuildStatus" class="tc-build-status" aria-live="polite"></div></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Talismans</h2><span>Stat bonuses affect AR automatically</span></div><div class="tc-build-talismans">${build.talismans.map((value,i)=>`<div class="tc-build-field"><label for="tcTalisman${i}">Slot ${i+1}</label><select id="tcTalisman${i}" data-talisman="${i}"><option value="">Empty slot</option>${value&&!TALISMAN_NAMES.includes(value)?`<option value="${h(value)}" selected>${h(value)}</option>`:''}${TALISMAN_NAMES.map(x=>`<option value="${h(x)}" ${x===value?'selected':''}>${h(x)}</option>`).join('')}</select></div>`).join('')}</div></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Wondrous Physick</h2><span>Assumes the Physick is active</span></div><div class="tc-build-talismans">${build.physickTears.map((value,i)=>`<div class="tc-build-field"><label for="tcPhysick${i}">Crystal Tear ${i+1}</label><select id="tcPhysick${i}" data-physick="${i}"><option value="">Empty slot</option>${value&&!PHYSICK_NAMES.includes(value)?`<option value="${h(value)}" selected>${h(value)}</option>`:''}${PHYSICK_NAMES.map(x=>`<option value="${h(x)}" ${x===value?'selected':''}>${h(x)}</option>`).join('')}</select></div>`).join('')}</div><div class="tc-build-helper">Strength, Dexterity, Intelligence, and Faith knot tears add +10 to weapon calculations automatically. Crimson Crystal, Cerulean Crystal, and Ruptured Crystal Tears may legally occupy both slots when you own both copies. Other offensive effects are explained below the AR result.</div></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Weapon Lab</h2><span>Regulation 1.17 data</span></div><div class="tc-weapon-controls">
        <div class="tc-build-field tc-weapon-name"><label for="tcBuildWeaponName">Weapon</label><input id="tcBuildWeaponName" value="${h(build.weapon.weaponName)}" data-selected-weapon="${h(build.weapon.weaponName)}" placeholder="Search or tap to browse every weapon" autocomplete="off" autocapitalize="off" spellcheck="false" inputmode="search" enterkeyhint="search"><div id="tcWeaponPicker" class="tc-weapon-picker" role="listbox" aria-label="Weapon results" hidden></div></div>
        <div class="tc-build-field"><label for="tcBuildAffinity">Affinity</label><select id="tcBuildAffinity"><option>Loading…</option></select></div>
        <div class="tc-build-field"><label for="tcBuildUpgrade">Upgrade · <span id="tcUpgradeMax">max</span></label><input id="tcBuildUpgrade" type="number" inputmode="numeric" min="0" max="25" value="${build.weapon.upgrade}"></div>
      </div><div id="tcWeaponSearchState" class="tc-weapon-search-state" aria-live="polite"></div><div id="tcWeaponResults" class="tc-weapon-loading">Opening the armory…</div></div>
      <div class="tc-build-save-row"><div class="tc-build-save-state">Saved automatically</div><button id="tcSaveBuild" type="button" class="btn gold">Save Now</button></div>
      <div class="tc-build-attribution">Weapon calculations and v1.17 regulation data adapted from Tom Clark’s MIT-licensed Elden Ring Weapon Calculator. Conditional buffs are listed separately from menu AR.</div>
    </section>${navMarkup('build')}`;
    bindNav();applyClassConstraintsToInputs();refreshTalismanAvailability();refreshBuildStatus(build);refreshWeaponSearchState();markDirty(false);
    loadWeaponData().then(()=>{if(uiScreen!=='build')return;populateWeaponControls(build);refreshResults();}).catch(error=>{console.error(error);const host=document.querySelector('#tcWeaponResults');if(host)host.innerHTML='<div class="tc-weapon-error">The weapon records could not be opened. Refresh the app and try again.</div>';});
  }
  async function saveBuild({slot=selectedSlot(),draft=null,automatic=false,changeSeq=tcBuildChangeSeq}={}){
    clearTimeout(tcBuildAutosaveTimer);tcBuildAutosaveTimer=null;
    draft=normalizeBuild(draft||currentDraft());
    if(automatic&&pending){
      const status=document.querySelector('.tc-build-save-state');if(status){status.textContent='Waiting to save after current Covenant action…';status.classList.add('dirty');}
      tcBuildAutosaveDraft=draft;tcBuildAutosaveSlot=slot;
      tcBuildAutosaveTimer=setTimeout(()=>saveBuild({slot,draft,automatic:true,changeSeq}),900);
      return false;
    }
    const buildState=latest=>{const next=structuredClone(latest);ensureBuilds(next);next.builds[slot]=structuredClone(draft);next.lastAction=`${playerName()} updated ${playerLabel(slot,next)}’s build.`;next.updatedAt=new Date().toISOString();return next;};
    const button=document.querySelector('#tcSaveBuild'),status=document.querySelector('.tc-build-save-state');if(button&&!automatic){button.disabled=true;button.textContent='Saving…';}if(status)status.textContent='Saving…';
    const saved=await commit(buildState(run.state),{successToast:automatic?'':`${playerLabel(slot,run.state)}’s build saved.`,retryBuilder:buildState});
    if(button&&!automatic){button.disabled=false;button.textContent='Save Now';}
    if(saved){
      if(changeSeq===tcBuildChangeSeq){
        tcBuildAutosaveDraft=null;tcBuildAutosaveSlot=null;
        if(selectedSlot()===slot)markDirty(false);
      }
    }else if(automatic&&changeSeq===tcBuildChangeSeq){
      tcBuildAutosaveDraft=draft;tcBuildAutosaveSlot=slot;
      if(status){status.textContent='Save interrupted · retrying…';status.classList.add('dirty');}
      tcBuildAutosaveTimer=setTimeout(()=>saveBuild({slot,draft,automatic:true,changeSeq}),1400);
    }else if(!automatic){
      if(button){button.disabled=false;button.textContent='Save Now';}
      if(status){status.textContent='Not saved · try again';status.classList.add('dirty');}
    }
  }

  const normalizeBefore=tcNormalizeRunState;
  tcNormalizeRunState=function(state){const normalized=normalizeBefore(state);return ensureBuilds(normalized);};
  const navBefore=navMarkup;
  navMarkup=function(active){return navBefore(active).replace('<button data-screen="settings"',`<button data-screen="build" class="${active==='build'?'active':''}"><span class="nicon">⌁</span><span>Build</span></button><button data-screen="settings"`);};
  const renderBefore=renderRun;
  renderRun=function(){
    if(run?.state)ensureBuilds(run.state);
    if(uiScreen==='build'){
      if(tcBuildDirty&&document.querySelector('.tc-build-screen')){
        const status=document.querySelector('.tc-build-save-state');
        if(status)status.textContent='Saving local edits · partner sync received';
        return;
      }
      return renderBuild();
    }
    return renderBefore();
  };

  if(!window.__tcBuildLabBound){window.__tcBuildLabBound=true;document.addEventListener('click',event=>{
    const weaponPick=event.target.closest('[data-weapon-pick]');if(weaponPick){setWeaponSelection(weaponPick.dataset.weaponPick);return;}
    const slot=event.target.closest('[data-build-slot]');if(slot){const nextSlot=slot.dataset.buildSlot,currentSlot=selectedSlot();if(nextSlot===currentSlot)return;if(tcBuildDirty){const draft=currentDraft(),changeSeq=tcBuildChangeSeq;clearTimeout(tcBuildAutosaveTimer);tcBuildAutosaveTimer=null;saveBuild({slot:currentSlot,draft,automatic:true,changeSeq});}tcBuildSlot=nextSlot;tcBuildDirty=false;renderBuild();return;}
    const stepper=event.target.closest('[data-step-field]');if(stepper){const field=document.querySelector(`[data-build-field="${stepper.dataset.stepField}"]`);if(field){const min=Number(field.min)||0,max=Number(field.max)||999;field.value=Math.max(min,Math.min(max,(Number(field.value)||0)+Number(stepper.dataset.step||0)));refreshResults();scheduleBuildSave();}return;}
    if(event.target.closest('#tcSaveBuild')){saveBuild();return;}
    const syncLevel=event.target.closest('[data-sync-build-level]');if(syncLevel){const field=document.querySelector('[data-build-field="level"]');if(field){field.value=String(Math.max(Number(field.min)||1,Math.min(Number(field.max)||713,Number(syncLevel.dataset.syncBuildLevel)||1)));refreshResults();scheduleBuildSave();}return;}
    const affinity=event.target.closest('[data-affinity-pick]');if(affinity){const select=document.querySelector('#tcBuildAffinity');if(select){select.value=affinity.dataset.affinityPick;refreshResults();scheduleBuildSave();}return;}
    if(!event.target.closest('.tc-weapon-name'))closeWeaponPicker();
  });document.addEventListener('focusin',event=>{if(event.target.matches('#tcBuildWeaponName'))renderWeaponPicker();});document.addEventListener('keydown',event=>{if(!event.target.matches('#tcBuildWeaponName'))return;if(event.key==='Escape'){closeWeaponPicker({restore:true});event.target.blur();return;}if(event.key==='Enter'){event.preventDefault();const value=event.target.value.trim(),names=weaponNames(),exact=names.find(n=>n.toLowerCase()===value.toLowerCase()),first=exact||names.find(n=>n.toLowerCase().includes(value.toLowerCase()));if(first)setWeaponSelection(first);}});document.addEventListener('input',event=>{if(!event.target.closest('.tc-build-screen'))return;if(event.target.matches('#tcBuildWeaponName')){renderWeaponPicker(event.target.value);return;}if(event.target.matches('[data-build-field],#tcBuildUpgrade')){refreshResults();scheduleBuildSave();}});document.addEventListener('change',event=>{if(!event.target.closest('.tc-build-screen'))return;if(event.target.matches('#tcBuildClass')){const preset=STARTING_CLASSES[event.target.value];if(preset)for(const key of ['level','vig','mind','end','str','dex','int','fai','arc']){const field=document.querySelector(`[data-build-field="${key}"]`);if(field)field.value=preset[key];}refreshResults();scheduleBuildSave();return;}if(event.target.matches('#tcBuildWeaponName')){const value=event.target.value.trim(),exact=weaponNames().find(n=>n.toLowerCase()===value.toLowerCase());if(exact){setWeaponSelection(exact);return;}if(!value){event.target.dataset.selectedWeapon='';closeWeaponPicker();refreshResults();scheduleBuildSave();return;}renderWeaponPicker(value);return;}if(event.target.matches('[data-talisman],[data-physick]')){const isTalisman=event.target.matches('[data-talisman]'),selector=isTalisman?'[data-talisman]':'[data-physick]',value=event.target.value.trim();if(value){const others=[...document.querySelectorAll(selector)].filter(el=>el!==event.target&&el.value);if(isTalisman){const family=talismanFamilyKey(value);if(others.some(el=>talismanFamilyKey(el.value)===family)){event.target.value='';setToast('Those talismans are mutually exclusive in-game.');}}else{const key=itemKey(value);if(!PHYSICK_DUPLICATES_ALLOWED.has(key)&&others.some(el=>itemKey(el.value)===key)){event.target.value='';setToast('You only have one copy of that Crystal Tear.');}}}refreshResults();scheduleBuildSave();return;}if(event.target.matches('#tcBuildAffinity')){refreshResults();scheduleBuildSave();}});}
  queueMicrotask(()=>{if(run&&!tcTransitionIsLocked())renderRun();});
})();
/* --- End persistent Tarnished build lab --- */
