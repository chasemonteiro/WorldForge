/* --- Multiplayer synchronization hardening --- */
let tcSharedSyncBusy=false;
let tcDeferredSharedSyncSource='';
let tcRealtimeStatus='UNKNOWN';
let tcRealtimeRepairTimer=null;

function tcClearStaleSharedTransients(previousState,nextState){
  const previousId=previousState?.current?.id||null;
  const nextId=nextState?.current?.id||null;
  if(postBattleReport?.encounterId && postBattleReport.encounterId!==nextId)postBattleReport=null;
  if(pendingRevealId && pendingRevealId!==nextId)pendingRevealId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(tcPendingRegionContractEncounterId && tcPendingRegionContractEncounterId!==nextId)tcPendingRegionContractEncounterId=null;
  if(previousId&&nextId&&previousId!==nextId){try{acknowledgedChaos.clear();}catch{}}
}

function tcApplyAuthoritativeRun(incoming,{source='realtime'}={}){
  if(!incoming?.state||!run)return false;
  if(incoming?.id&&run?.id&&incoming.id!==run.id){
    console.warn(`Ignored late ${source} payload for another Covenant`,incoming.id);
    return false;
  }
  const incomingRevision=Number(incoming.revision||0);
  const currentRevision=Number(run.revision||0);
  if(incomingRevision<=currentRevision)return false;
  const previousState=run.state;
  run={...run,...incoming,revision:incomingRevision};
  tcClearStaleSharedTransients(previousState,run.state);
  try{renderRun();}catch(error){console.error(`Shared ${source} render failed`,error);}
  return true;
}

function tcDrainDeferredSharedSync(){
  if(pending||tcSharedSyncBusy||!tcDeferredSharedSyncSource)return;
  const source=tcDeferredSharedSyncSource;
  tcDeferredSharedSyncSource='';
  tcSyncAuthoritativeRun(`deferred-${source}`);
}

async function tcSyncAuthoritativeRun(source='recovery'){
  if(backend?.mode!=='shared'||!run?.id)return false;
  if(pending||tcSharedSyncBusy){tcDeferredSharedSyncSource=source;return false;}
  tcSharedSyncBusy=true;
  try{
    const runId=run.id;
    const latest=await backend.getRun(runId);
    if(run?.id!==runId)return false;
    return tcApplyAuthoritativeRun(latest,{source});
  }catch(error){
    console.warn(`Shared ${source} sync failed`,error);
    return false;
  }finally{
    tcSharedSyncBusy=false;
    queueMicrotask(tcDrainDeferredSharedSync);
  }
}

function tcScheduleRealtimeRepair(source='realtime'){
  if(backend?.mode!=='shared'||!run?.id||tcRealtimeRepairTimer)return;
  tcRealtimeRepairTimer=window.setTimeout(()=>{
    tcRealtimeRepairTimer=null;
    if(backend?.mode!=='shared'||!run?.id||navigator.onLine===false)return;
    try{subscribe();}catch(error){console.warn('Realtime resubscribe failed',error);}
    tcSyncAuthoritativeRun(`repair-${source}`);
  },1200);
}

window.tcHandleRealtimeChannelStatus=function(status,error,runId,intentionalClose=false){
  if(!run?.id||run.id!==runId)return;
  tcRealtimeStatus=status||'UNKNOWN';
  if(status==='SUBSCRIBED'){
    if(tcRealtimeRepairTimer){clearTimeout(tcRealtimeRepairTimer);tcRealtimeRepairTimer=null;}
    window.setTimeout(()=>tcSyncAuthoritativeRun('realtime-subscribed'),0);
    return;
  }
  if(intentionalClose)return;
  if(status==='CHANNEL_ERROR'||status==='TIMED_OUT'||status==='CLOSED'){
    console.warn(`Realtime channel ${status}`,error||'');
    tcScheduleRealtimeRepair(String(status).toLowerCase());
  }
};

subscribe=function(){
  unsubscribe?.();
  if(!run?.id)return;
  const subscribedRunId=run.id;
  unsubscribe=backend.subscribe(subscribedRunId,incoming=>{
    if(!incoming?.state||run?.id!==subscribedRunId)return;
    tcApplyAuthoritativeRun(incoming,{source:'realtime'});
  });
  if(backend.mode==='shared')window.setTimeout(()=>tcSyncAuthoritativeRun('subscribe'),350);
};

if(!window.__tcMultiplayerRecoveryBound){
  window.__tcMultiplayerRecoveryBound=true;
  window.addEventListener('online',()=>{tcScheduleRealtimeRepair('online');tcSyncAuthoritativeRun('online');});
  window.addEventListener('pageshow',()=>{if(tcRealtimeStatus!=='SUBSCRIBED')tcScheduleRealtimeRepair('pageshow');tcSyncAuthoritativeRun('pageshow');});
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible'){
      if(tcRealtimeStatus!=='SUBSCRIBED')tcScheduleRealtimeRepair('resume');
      tcSyncAuthoritativeRun('resume');
    }
  });
  window.__tcMultiplayerHeartbeat=window.setInterval(()=>{
    if(document.visibilityState==='visible')tcSyncAuthoritativeRun('heartbeat');
  },30000);
}
/* --- End multiplayer synchronization hardening --- */