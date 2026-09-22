/* Persistent Tarnished build lab. Weapon math adapted from Tom Clark's
   MIT-licensed Elden Ring Weapon Calculator; see THIRD_PARTY_NOTICES.md. */
(() => {
  const ATTRS=['str','dex','int','fai','arc'];
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
  const TALISMAN_NAMES=[
    'Starscourge Heirloom','Prosthesis-Wearer Heirloom','Stargazer Heirloom','Two Fingers Heirloom','Outer God Heirloom',
    "Radagon's Scarseal","Radagon's Soreseal","Marika's Scarseal","Marika's Soreseal",'Two-Handed Sword Talisman',
    'Axe Talisman','Claw Talisman','Spear Talisman','Dagger Talisman','Shard of Alexander','Warrior Jar Shard',
    'Ritual Sword Talisman','Red-Feathered Branchsword','Lord of Blood’s Exultation','Kindred of Rot’s Exultation',
    'Rotten Winged Sword Insignia','Winged Sword Insignia','Millicent’s Prosthesis','Blue Dancer Charm'
  ];
  const STAT_TALISMANS={
    'starscourge heirloom':{str:5},'prosthesis-wearer heirloom':{dex:5},'stargazer heirloom':{int:5},'two fingers heirloom':{fai:5},'outer god heirloom':{arc:5},
    "radagon's scarseal":{str:3,dex:3},"radagon's soreseal":{str:5,dex:5},"marika's scarseal":{int:3,fai:3,arc:3},"marika's soreseal":{int:5,fai:5,arc:5},
    'millicent’s prosthesis':{dex:5},"millicent's prosthesis":{dex:5}
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

  let tcWeaponData=null,tcWeaponDataPromise=null,tcBuildSlot=null,tcBuildDirty=false;
  const graphCache=new Map();

  function blankBuild(){return {startingClass:'',level:1,vig:10,mind:10,end:10,str:10,dex:10,int:10,fai:10,arc:10,scadu:0,talismans:['','','',''],weapon:{weaponName:'',variantName:'',upgrade:0}};}
  function normalizeBuild(value){
    const base=blankBuild(),src=value&&typeof value==='object'?value:{};
    base.startingClass=STARTING_CLASSES[src.startingClass]?src.startingClass:'';
    for(const key of ['level','vig','mind','end','str','dex','int','fai','arc'])base[key]=Math.max(1,Math.min(713,Number(src[key]??base[key])||base[key]));
    for(const key of ['vig','mind','end','str','dex','int','fai','arc'])base[key]=Math.min(99,base[key]);
    base.scadu=Math.max(0,Math.min(20,Number(src.scadu)||0));
    base.talismans=Array.from({length:4},(_,i)=>String(Array.isArray(src.talismans)?src.talismans[i]||'':''));
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
  function effectiveAttrs(build){const d=talismanDeltas(build),out={};for(const key of ATTRS)out[key]=Math.min(99,Math.max(1,Number(build[key])||1)+d[key]);return out;}
  function currentDraft(){
    const base=buildFor();
    base.startingClass=document.querySelector('#tcBuildClass')?.value||'';
    document.querySelectorAll('[data-build-field]').forEach(el=>{const key=el.dataset.buildField;base[key]=Math.max(Number(el.min)||0,Math.min(Number(el.max)||999,Number(el.value)||0));});
    base.talismans=Array.from(document.querySelectorAll('[data-talisman]')).map(el=>el.value.trim()).slice(0,4);
    const weaponName=document.querySelector('#tcBuildWeaponName')?.value.trim()||'';
    const variantName=document.querySelector('#tcBuildAffinity')?.value||'';
    const upgrade=Math.max(0,Number(document.querySelector('#tcBuildUpgrade')?.value)||0);
    base.weapon={weaponName,variantName,upgrade};return normalizeBuild(base);
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
    const unmet=Object.entries(weapon.requirements).filter(([a,n])=>adjusted[a]<n).map(([a])=>a),attack={},ineffective=[];
    for(const type of [...DAMAGE,...STATUS]){const base=weapon.attack[level][type]||0;if(!base&&!weapon.sorceryTool&&!weapon.incantationTool)continue;const scalingAttrs=weapon.attackElementCorrect[type]||{};let total=1;if(unmet.some(a=>scalingAttrs[a])){total=.6;ineffective.push(type);}else{for(const attr of ATTRS){const correction=scalingAttrs[attr];if(!correction)continue;const scaling=correction===true?(weapon.attributeScaling[level][attr]||0):(correction*(weapon.attributeScaling[level][attr]||0))/(weapon.attributeScaling[0][attr]||1);if(scaling)total+=(weapon.calcCorrectGraphs[type][DAMAGE.includes(type)?adjusted[attr]:attrs[attr]]||0)*scaling;}}if(base)attack[type]=base*total;}
    return {weapon,level,attack,unmet,ineffective,total:DAMAGE.reduce((sum,t)=>sum+(attack[t]||0),0)};
  }
  function variantsFor(name){return tcWeaponData?.weapons?.filter(w=>w.weaponName===name)||[];}
  function rawFor(build){const list=variantsFor(build.weapon.weaponName);return list.find(w=>w.name===build.weapon.variantName)||list[0]||null;}
  function affinityLabel(raw){return AFFINITIES[raw.affinityId]||raw.name.replace(raw.weaponName,'').trim()||'Standard';}
  function round(value){return Math.floor(Number(value||0)+1e-9);}
  function scalingLabel(weapon,level,attr){const value=weapon.attributeScaling[level][attr];return value?weapon.scalingTiers.find(([minimum])=>value>=minimum)?.[1]||'—':'—';}
  function conditionalNotes(build){return [...new Set(build.talismans.map(x=>CONDITIONAL_TALISMANS[String(x||'').trim().toLowerCase()]).filter(Boolean))];}
  function resultMarkup(build,raw){
    if(!raw)return `<div class="tc-weapon-empty">Choose a weapon to calculate its attack rating with this build.</div>`;
    const one=calculate(raw,build,false),two=calculate(raw,build,true),scadu=SCADU[build.scadu]||1,deltas=talismanDeltas(build),attrs=effectiveAttrs(build);
    const damage=[...new Set([...Object.keys(one.attack),...Object.keys(two.attack)].map(Number))].filter(t=>DAMAGE.includes(t)&&((one.attack[t]||two.attack[t])>0));
    const statuses=[...new Set([...Object.keys(one.attack),...Object.keys(two.attack)].map(Number))].filter(t=>STATUS.includes(t)&&((one.attack[t]||two.attack[t])>0));
    const requirements=ATTRS.filter(a=>raw.requirements[a]).map(a=>`<div class="${one.unmet.includes(a)?'unmet':''}"><span>${a.toUpperCase()}</span><b>${raw.requirements[a]}</b></div>`).join('')||'<div><span>Requirements</span><b>None</b></div>';
    const scaling=ATTRS.filter(a=>one.weapon.attributeScaling[one.level][a]).map(a=>`<div><span>${a.toUpperCase()}</span><b>${scalingLabel(one.weapon,one.level,a)}</b></div>`).join('')||'<div><span>Scaling</span><b>—</b></div>';
    const deltaText=ATTRS.filter(a=>deltas[a]).map(a=>`${a.toUpperCase()} +${deltas[a]}`).join(' · ');
    const notes=conditionalNotes(build);
    const ranked=variantsFor(build.weapon.weaponName).map(candidate=>{const a=calculate(candidate,build,false),b=calculate(candidate,build,true);return {raw:candidate,one:round(a.total),two:round(b.total)};}).sort((a,b)=>Math.max(b.one,b.two)-Math.max(a.one,a.two));
    return `<div class="tc-ar-hero">
      <div class="tc-ar-card"><span class="mode">one-handed AR</span><strong>${round(one.total)}</strong><small>${h(raw.name)} +${one.level}</small>${build.scadu?`<div class="shadow">Shadow Realm · ${round(one.total*scadu)} AR</div>`:''}</div>
      <div class="tc-ar-card"><span class="mode">two-handed AR</span><strong>${round(two.total)}</strong><small>${two.weapon.paired?'Paired weapon · no STR bonus':BOW_TYPES.has(two.weapon.weaponType)?'Two-handing required':`Effective STR ${adjustedAttrs(two.weapon,attrs,true).str}`}</small>${build.scadu?`<div class="shadow">Shadow Realm · ${round(two.total*scadu)} AR</div>`:''}</div>
    </div>
    <div class="tc-weapon-meta">
      <div class="tc-weapon-slip"><span>Damage & buildup · 1H / 2H</span><div class="tc-damage-grid">${damage.map(t=>`<div><span>${TYPE_LABELS[t]}</span><b>${round(one.attack[t])} / ${round(two.attack[t])}</b></div>`).join('')}${statuses.map(t=>`<div><span>${TYPE_LABELS[t]}</span><b>${round(one.attack[t])}</b></div>`).join('')}</div></div>
      <div class="tc-weapon-slip"><span>Requirements & scaling</span><div class="tc-requirement-grid">${requirements}${scaling}</div></div>
    </div>
    ${one.unmet.length?`<div class="tc-weapon-note warn">Requirements not met one-handed: ${one.unmet.map(a=>a.toUpperCase()).join(', ')}. The calculator has applied the in-game attack penalty.</div>`:''}
    ${deltaText?`<div class="tc-weapon-note">Effective combat stats include talisman bonuses: ${deltaText}.</div>`:''}
    ${build.scadu?`<div class="tc-weapon-note">Scadutree Blessing +${build.scadu} uses the current Shadow Realm damage multiplier (×${scadu}). It does not affect damage outside the Realm of Shadow.</div>`:''}
    ${notes.map(note=>`<div class="tc-weapon-note">${h(note)}</div>`).join('')}
    ${ranked.length>1?`<div class="tc-affinity-head"><strong>Best affinities for these stats</strong><span>Tap one to equip it</span></div><div class="tc-affinity-table">${ranked.map((row,i)=>`<button type="button" class="tc-affinity-row ${row.raw.name===raw.name?'current':''}" data-affinity-pick="${h(row.raw.name)}"><span>${i+1}. ${h(affinityLabel(row.raw))}</span><small>1H</small><b>${row.one}</b><span></span><small>2H</small><b>${row.two}</b></button>`).join('')}</div>`:''}`;
  }
  function populateWeaponControls(build){
    const input=document.querySelector('#tcBuildWeaponName'),list=document.querySelector('#tcWeaponNames'),affinity=document.querySelector('#tcBuildAffinity'),upgrade=document.querySelector('#tcBuildUpgrade');if(!input||!list||!affinity||!upgrade||!tcWeaponData)return;
    const names=[...new Set(tcWeaponData.weapons.map(w=>w.weaponName))].sort((a,b)=>a.localeCompare(b));list.innerHTML=names.map(name=>`<option value="${h(name)}"></option>`).join('');
    let exact=names.find(n=>n.toLowerCase()===input.value.trim().toLowerCase());if(!exact&&input.value.trim())exact=names.find(n=>n.toLowerCase().includes(input.value.trim().toLowerCase()));if(exact)input.value=exact;
    const variants=variantsFor(exact||'');const saved=affinity.value||build.weapon.variantName;affinity.innerHTML=variants.length?variants.map(w=>`<option value="${h(w.name)}">${h(affinityLabel(w))}</option>`).join(''):'<option value="">Choose weapon first</option>';if(variants.some(w=>w.name===saved))affinity.value=saved;
    const raw=variants.find(w=>w.name===affinity.value)||variants[0];const max=raw?(tcWeaponData.reinforceTypes[raw.reinforceTypeId]?.length||1)-1:25;upgrade.max=max;upgrade.value=Math.min(max,Number(upgrade.value)||build.weapon.upgrade||0);document.querySelector('#tcUpgradeMax').textContent=`max +${max}`;
  }
  function refreshResults(){if(!tcWeaponData)return;const build=currentDraft();populateWeaponControls(build);const raw=rawFor({...build,weapon:{...build.weapon,variantName:document.querySelector('#tcBuildAffinity')?.value||build.weapon.variantName}});build.weapon.variantName=raw?.name||'';const host=document.querySelector('#tcWeaponResults');if(host)host.innerHTML=resultMarkup(build,raw);}
  function renderBuild(){
    ensureBuilds(run.state);const slot=selectedSlot(),build=buildFor(slot),names=covenantNames(run.state);
    app.innerHTML=`<section class="tc-screen tc-build-screen">${screenTop('Tarnished Build')}
      <div class="tc-build-hero"><div class="tc-kicker gold">living character sheet</div><h1>Build</h1><p>Keep both Tarnished current, test every weapon, and stop leaving damage on the table.</p></div>
      <div class="tc-build-player-tabs"><button type="button" data-build-slot="chase" class="${slot==='chase'?'active':''}">${h(names[0])}</button><button type="button" data-build-slot="morgan" class="${slot==='morgan'?'active':''}">${h(names[1])}</button></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Attributes</h2><span>Current in-game values</span></div>
        <div class="tc-build-origin tc-build-field"><label for="tcBuildClass">Starting class</label><select id="tcBuildClass"><option value="">Custom / keep current stats</option>${Object.entries(STARTING_CLASSES).map(([key,value])=>`<option value="${key}" ${build.startingClass===key?'selected':''}>${h(value.label)}</option>`).join('')}</select><small>Choosing a class fills its starting level and attributes. Keep editing these values as you level.</small></div>
        <div class="tc-build-stats">
        ${[['level','Level',713],['vig','Vigor',99],['mind','Mind',99],['end','Endurance',99],['str','Strength',99],['dex','Dexterity',99],['int','Intelligence',99],['fai','Faith',99],['arc','Arcane',99],['scadu','Scadutree',20]].map(([key,label,max])=>`<div class="tc-build-field"><label for="tcBuild-${key}">${label}</label><input id="tcBuild-${key}" data-build-field="${key}" type="number" inputmode="numeric" min="${key==='scadu'?0:1}" max="${max}" value="${build[key]}"></div>`).join('')}
      </div></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Talismans</h2><span>Stat bonuses affect AR automatically</span></div><div class="tc-build-talismans">${build.talismans.map((value,i)=>`<div class="tc-build-field"><label for="tcTalisman${i}">Slot ${i+1}</label><input id="tcTalisman${i}" data-talisman="${i}" list="tcTalismanNames" value="${h(value)}" placeholder="Choose or type a talisman"></div>`).join('')}</div><datalist id="tcTalismanNames">${TALISMAN_NAMES.map(x=>`<option value="${h(x)}"></option>`).join('')}</datalist></div>
      <div class="tc-build-section"><div class="tc-build-section-head"><h2>Weapon Lab</h2><span>Regulation 1.17 data</span></div><div class="tc-weapon-controls">
        <div class="tc-build-field tc-weapon-name"><label for="tcBuildWeaponName">Weapon</label><input id="tcBuildWeaponName" list="tcWeaponNames" value="${h(build.weapon.weaponName)}" placeholder="Search any weapon" autocomplete="off"><datalist id="tcWeaponNames"></datalist></div>
        <div class="tc-build-field"><label for="tcBuildAffinity">Affinity</label><select id="tcBuildAffinity"><option>Loading…</option></select></div>
        <div class="tc-build-field"><label for="tcBuildUpgrade">Upgrade · <span id="tcUpgradeMax">max</span></label><input id="tcBuildUpgrade" type="number" inputmode="numeric" min="0" max="25" value="${build.weapon.upgrade}"></div>
      </div><div id="tcWeaponResults" class="tc-weapon-loading">Opening the armory…</div></div>
      <div class="tc-build-save-row"><div class="tc-build-save-state">Saved to the Covenant</div><button id="tcSaveBuild" type="button" class="btn gold">Save Build</button></div>
      <div class="tc-build-attribution">Weapon calculations and v1.17 regulation data adapted from Tom Clark’s MIT-licensed Elden Ring Weapon Calculator. Conditional buffs are listed separately from menu AR.</div>
    </section>${navMarkup('build')}`;
    bindNav();markDirty(false);
    loadWeaponData().then(()=>{if(uiScreen!=='build')return;populateWeaponControls(build);refreshResults();}).catch(error=>{console.error(error);const host=document.querySelector('#tcWeaponResults');if(host)host.innerHTML='<div class="tc-weapon-error">The weapon records could not be opened. Refresh the app and try again.</div>';});
  }
  async function saveBuild(){
    const slot=selectedSlot(),draft=currentDraft();draft.weapon.variantName=document.querySelector('#tcBuildAffinity')?.value||draft.weapon.variantName;
    const buildState=latest=>{const next=structuredClone(latest);ensureBuilds(next);next.builds[slot]=structuredClone(draft);next.lastAction=`${playerName()} updated ${playerLabel(slot,next)}’s build.`;next.updatedAt=new Date().toISOString();return next;};
    const button=document.querySelector('#tcSaveBuild');if(button){button.disabled=true;button.textContent='Saving…';}
    const saved=await commit(buildState(run.state),{successToast:`${playerLabel(slot,run.state)}’s build saved.`,retryBuilder:buildState});if(saved)markDirty(false);else if(button){button.disabled=false;button.textContent='Save Build';}
  }

  const normalizeBefore=tcNormalizeRunState;
  tcNormalizeRunState=function(state){const normalized=normalizeBefore(state);return ensureBuilds(normalized);};
  const navBefore=navMarkup;
  navMarkup=function(active){return navBefore(active).replace('<button data-screen="settings"',`<button data-screen="build" class="${active==='build'?'active':''}"><span class="nicon">⌁</span><span>Build</span></button><button data-screen="settings"`);};
  const renderBefore=renderRun;
  renderRun=function(){if(run?.state)ensureBuilds(run.state);if(uiScreen==='build')return renderBuild();return renderBefore();};

  if(!window.__tcBuildLabBound){window.__tcBuildLabBound=true;document.addEventListener('click',event=>{
    const slot=event.target.closest('[data-build-slot]');if(slot){tcBuildSlot=slot.dataset.buildSlot;tcBuildDirty=false;renderBuild();return;}
    if(event.target.closest('#tcSaveBuild')){saveBuild();return;}
    const affinity=event.target.closest('[data-affinity-pick]');if(affinity){const select=document.querySelector('#tcBuildAffinity');if(select){select.value=affinity.dataset.affinityPick;markDirty();refreshResults();}return;}
  });document.addEventListener('input',event=>{if(!event.target.closest('.tc-build-screen'))return;if(event.target.matches('[data-build-field],[data-talisman],#tcBuildUpgrade')){markDirty();refreshResults();}});document.addEventListener('change',event=>{if(!event.target.closest('.tc-build-screen'))return;if(event.target.matches('#tcBuildClass')){const preset=STARTING_CLASSES[event.target.value];if(preset)for(const key of ['level','vig','mind','end','str','dex','int','fai','arc']){const field=document.querySelector(`[data-build-field="${key}"]`);if(field)field.value=preset[key];}markDirty();refreshResults();return;}if(event.target.matches('#tcBuildWeaponName,#tcBuildAffinity')){markDirty();refreshResults();}});}
  queueMicrotask(()=>{if(run&&!tcTransitionIsLocked())renderRun();});
})();
/* --- End persistent Tarnished build lab --- */
