from pathlib import Path
import re
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
tc = root / 'tarnished-covenant'

HARDENED_JS = r'''
function tcResumeDelay(ms){return new Promise(resolve=>setTimeout(resolve,ms));}

function tcRenderResumeStatus(message='Reconnecting to Covenant…', detail='Your saved run is still remembered on this phone.'){
  setRegionTheme('');
  const code=session?.joinCode||incomingCode||'';
  app.innerHTML=`${header(true)}
    <section class="menu-section stack tc-resume-guard">
      <div class="menu-title">${h(message)}</div>
      <div class="sub center">${h(detail)}</div>
      ${code?`<div class="center"><span class="mode-pill">saved room · ${h(code)}</span></div>`:''}
      <div class="status">Do not start a new Covenant. The app is recovering the existing one.</div>
    </section>`;
}

function tcActivateRememberedRun(recovered, remembered){
  run=recovered;
  session={
    runId:run.id,
    joinCode:run.joinCode||remembered?.joinCode||incomingCode||'',
    displayName:remembered?.displayName||'Tarnished'
  };
  saveSession(session);
  subscribe();
  renderRun();
  return true;
}

function tcRenderResumeRecovery(lastError){
  setRegionTheme('');
  const code=session?.joinCode||incomingCode||'';
  app.innerHTML=`${header(true)}
    <section class="menu-section stack tc-resume-guard">
      <div class="menu-title">Covenant still saved</div>
      <div class="sub center">The cloud connection did not recover yet. Your saved run reference has not been erased.</div>
      ${code?`<div class="center"><span class="mode-pill">saved room · ${h(code)}</span></div>`:''}
      <button id="tcRetryResume" class="btn gold" type="button">Retry Existing Covenant</button>
      ${code?`<button id="tcRetryRoom" class="btn ghost" type="button">Reconnect to Saved Room ${h(code)}</button>`:''}
      <div class="status warn">${h(lastError?.message||'Temporary sync failure.')} · Starting a new run is intentionally blocked from this recovery screen.</div>
    </section>`;
  document.querySelector('#tcRetryResume')?.addEventListener('click',boot);
  document.querySelector('#tcRetryRoom')?.addEventListener('click',async()=>{
    tcRenderResumeStatus('Rejoining saved room…','Using the room code stored on this phone.');
    try{
      if(backend.mode!=='shared')backend=await createBackend(config);
      if(backend.mode!=='shared')throw new Error('Shared sync is still unavailable.');
      const joined=await backend.joinRun(code,session?.displayName||'Tarnished');
      tcActivateRememberedRun(joined,session);
    }catch(error){console.warn(error);tcRenderResumeRecovery(error);}
  });
}

async function tcRecoverRememberedRun(){
  const remembered={...(session||{})};
  const hasSharedBreadcrumb=Boolean(remembered.joinCode||incomingCode);
  const delays=[0,450,1000,1800];
  let lastError=null;
  tcRenderResumeStatus();

  for(let attempt=0;attempt<delays.length;attempt+=1){
    if(delays[attempt])await tcResumeDelay(delays[attempt]);
    try{
      if(hasSharedBreadcrumb && backend.mode!=='shared'){
        tcRenderResumeStatus('Reconnecting to shared Covenant…',`Recovery attempt ${attempt+1} of ${delays.length}.`);
        backend=await createBackend(config);
      }

      if(remembered.runId && (!hasSharedBreadcrumb || backend.mode==='shared')){
        const recovered=await backend.getRun(remembered.runId);
        if(recovered?.state)return tcActivateRememberedRun(recovered,remembered);
        throw new Error('Saved run was not returned yet.');
      }
    }catch(error){lastError=error;console.warn('Covenant resume attempt failed',attempt+1,error);}
  }

  const code=remembered.joinCode||incomingCode||'';
  if(code && backend.mode==='shared'){
    try{
      tcRenderResumeStatus('Rejoining saved room…','The saved run ID did not answer, so the app is recovering through its room code.');
      const joined=await backend.joinRun(code,remembered.displayName||'Tarnished');
      if(joined?.state)return tcActivateRememberedRun(joined,remembered);
    }catch(error){lastError=error;console.warn('Saved room recovery failed',error);}
  }

  tcRenderResumeRecovery(lastError||new Error('Covenant sync is temporarily unavailable.'));
  return false;
}

async function boot(){
  if(session?.runId||session?.joinCode||incomingCode){
    return tcRecoverRememberedRun();
  }
  renderHome();
}
'''


def replace_boot(text: str) -> str:
    if 'function tcRecoverRememberedRun()' in text:
        return text
    pattern = r"async function boot\(\) \{.*?\n\}\n\nfunction renderHome\(\)"
    replacement = HARDENED_JS + "\n\nfunction renderHome()"
    text, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('boot function target missing')
    return text

# Patch currently deployed generated app.
p = tc / 'index.html'
s = replace_boot(p.read_text())
p.write_text(s)

# Make the same guard durable for future full builds by extending the existing
# session-persistence owner script after its normal patch is written.
p = tc / 'build-durable-session.py'
s = p.read_text()
marker = '# --- Startup resume guard: never fall through to New Covenant on a transient sync failure. ---'
if marker not in s:
    escaped = repr(HARDENED_JS)
    durable = f'''\n\n{marker}\np = Path('tarnished-covenant/index.html')\ns = p.read_text()\nif 'function tcRecoverRememberedRun()' not in s:\n    import re\n    pattern = r"async function boot\\(\\) \\{{.*?\\n\\}}\\n\\nfunction renderHome\\(\\)"\n    replacement = {escaped} + "\\n\\nfunction renderHome()"\n    s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)\n    if n != 1:\n        raise SystemExit('durable resume guard boot target missing')\n    p.write_text(s)\n'''
    s += durable
    p.write_text(s)

for name in ['index.html','build-durable-session.py']:
    text=(tc/name).read_text()
    for needle in ['tcRecoverRememberedRun','Retry Existing Covenant','Starting a new run is intentionally blocked','backend.joinRun(code']:
        if needle not in text:
            raise SystemExit(f'{name}: resume invariant missing: {needle}')
