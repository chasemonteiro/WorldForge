/* Rykard always uses his encounter-specific armament, for both players. */
function tcIsRykardTarget(target){
  return tcBossKey(target?.name)===tcBossKey('Rykard, Lord of Blasphemy');
}
function tcSerpentHunterBuild(){
  return buildFromWeapon(W('Serpent-Hunter','Great Spear','Somber Smithing Stones','Great-Serpent Hunt',false));
}
const tcChooseWeaponPairBeforeRykard=chooseWeaponPair;
chooseWeaponPair=function(state,target){
  if(tcIsRykardTarget(target))return {chase:tcSerpentHunterBuild(),morgan:tcSerpentHunterBuild()};
  return tcChooseWeaponPairBeforeRykard(state,target);
};
const tcMakeBuildBeforeRykard=makeBuild;
makeBuild=function(regionName,target,avoidNames=[],state=null){
  if(tcIsRykardTarget(target))return tcSerpentHunterBuild();
  return tcMakeBuildBeforeRykard(regionName,target,avoidNames,state);
};
// Avoid spending penalties or rewards on rerolls of a fixed assignment.
const TC_RYKARD_ARMAMENT_NOTICE='Rykard always assigns Serpent-Hunter to both players. No weapon appeal is needed.';
const tcShowAppealBeforeRykard=showAppealMenu;
showAppealMenu=function(){
  if(tcIsRykardTarget(run?.state?.current?.target))return setToast(TC_RYKARD_ARMAMENT_NOTICE);
  return tcShowAppealBeforeRykard();
};
const tcChangeWeaponsBeforeRykard=changeWeapons;
changeWeapons=function(state,actor,which,useWaiver=false){
  if(tcIsRykardTarget(state?.current?.target))return structuredClone(state);
  return tcChangeWeaponsBeforeRykard(state,actor,which,useWaiver);
};
const tcOpenJointAppealBeforeRykard=tcOpenJointAppeal;
tcOpenJointAppeal=function(){
  if(tcIsRykardTarget(run?.state?.current?.target))return setToast(TC_RYKARD_ARMAMENT_NOTICE);
  return tcOpenJointAppealBeforeRykard();
};
const tcBuildJointAppealBeforeRykard=tcBuildJointAppeal;
tcBuildJointAppeal=function(latest,...args){
  if(tcIsRykardTarget(latest?.current?.target))return null;
  return tcBuildJointAppealBeforeRykard(latest,...args);
};
const tcBuildMasterworkRecallBeforeRykard=tcBuildMasterworkRecall;
tcBuildMasterworkRecall=function(latest,...args){
  if(tcIsRykardTarget(latest?.current?.target))return null;
  return tcBuildMasterworkRecallBeforeRykard(latest,...args);
};
