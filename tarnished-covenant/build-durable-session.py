from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

old = '''function loadSession() {
  try { return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null'); }
  catch { return null; }
}

function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}'''
new = '''const SESSION_COOKIE = 'tarnished_covenant_session_v1';

function sessionCookiePath() {
  const path = location.pathname || '/';
  return path.endsWith('/') ? path : path.slice(0, path.lastIndexOf('/') + 1);
}

function loadSession() {
  try {
    const local = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    if (local?.runId) return local;
  } catch {}
  try {
    const prefix = `${SESSION_COOKIE}=`;
    const raw = document.cookie.split(';').map(x=>x.trim()).find(x=>x.startsWith(prefix));
    if (!raw) return null;
    const restored = JSON.parse(decodeURIComponent(raw.slice(prefix.length)));
    if (restored?.runId) {
      try { localStorage.setItem(SESSION_KEY, JSON.stringify(restored)); } catch {}
      return restored;
    }
  } catch {}
  return null;
}

function persistSessionCookie(value) {
  try {
    document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(JSON.stringify(value))}; Max-Age=31536000; Path=${sessionCookiePath()}; SameSite=Lax; Secure`;
  } catch {}
}

function rememberSharedRunUrl(value) {
  if (!value?.joinCode || location.protocol === 'file:') return;
  try {
    const url = new URL(location.href);
    url.searchParams.set('join', value.joinCode);
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  } catch {}
}

function saveSession(value) {
  try { localStorage.setItem(SESSION_KEY, JSON.stringify(value)); } catch {}
  persistSessionCookie(value);
  rememberSharedRunUrl(value);
}

function clearSession() {
  try { localStorage.removeItem(SESSION_KEY); } catch {}
  try { document.cookie = `${SESSION_COOKIE}=; Max-Age=0; Path=${sessionCookiePath()}; SameSite=Lax; Secure`; } catch {}
}'''
if old not in s:
    raise SystemExit('session storage block missing')
s = s.replace(old, new, 1)

# Do not erase the shared-room breadcrumb immediately after a successful join.
s = s.replace("    history.replaceState({}, '', location.pathname);\n    renderRun();", "    rememberSharedRunUrl(session);\n    renderRun();", 1)

# Reassert the durable breadcrumb whenever a remembered shared run successfully boots.
old_boot = '''      if (run?.state) {
        subscribe();
        renderRun();
        return;
      }'''
new_boot = '''      if (run?.state) {
        saveSession({ runId: run.id, joinCode: run.joinCode || session.joinCode, displayName: session.displayName });
        subscribe();
        renderRun();
        return;
      }'''
if old_boot not in s:
    raise SystemExit('boot resume block missing')
s = s.replace(old_boot, new_boot, 1)

required = [
    "const SESSION_COOKIE = 'tarnished_covenant_session_v1'",
    'Max-Age=31536000',
    'function rememberSharedRunUrl(',
    'saveSession({ runId: run.id, joinCode: run.joinCode || session.joinCode',
]
for needle in required:
    if needle not in s:
        raise SystemExit('durable-session invariant missing: ' + needle)

p.write_text(s)


# --- Startup resume guard: never fall through to New Covenant on a transient sync failure. ---
p = Path('tarnished-covenant/index.html')
s = p.read_text()
if 'function tcRecoverRememberedRun()' not in s:
    import re
    pattern = r"async function boot\(\) \{.*?\n\}\n\nfunction renderHome\(\)"
    replacement = '\nfunction tcResumeDelay(ms){return new Promise(resolve=>setTimeout(resolve,ms));}\n\nfunction tcRenderResumeStatus(message=\'Reconnecting to Covenant…\', detail=\'Your saved run is still remembered on this phone.\'){\n  setRegionTheme(\'\');\n  const code=session?.joinCode||incomingCode||\'\';\n  app.innerHTML=`${header(true)}\n    <section class="menu-section stack tc-resume-guard">\n      <div class="menu-title">${h(message)}</div>\n      <div class="sub center">${h(detail)}</div>\n      ${code?`<div class="center"><span class="mode-pill">saved room · ${h(code)}</span></div>`:\'\'}\n      <div class="status">Do not start a new Covenant. The app is recovering the existing one.</div>\n    </section>`;\n}\n\nfunction tcActivateRememberedRun(recovered, remembered){\n  run=recovered;\n  session={\n    runId:run.id,\n    joinCode:run.joinCode||remembered?.joinCode||incomingCode||\'\',\n    displayName:remembered?.displayName||\'Tarnished\'\n  };\n  saveSession(session);\n  subscribe();\n  renderRun();\n  return true;\n}\n\nfunction tcRenderResumeRecovery(lastError){\n  setRegionTheme(\'\');\n  const code=session?.joinCode||incomingCode||\'\';\n  app.innerHTML=`${header(true)}\n    <section class="menu-section stack tc-resume-guard">\n      <div class="menu-title">Covenant still saved</div>\n      <div class="sub center">The cloud connection did not recover yet. Your saved run reference has not been erased.</div>\n      ${code?`<div class="center"><span class="mode-pill">saved room · ${h(code)}</span></div>`:\'\'}\n      <button id="tcRetryResume" class="btn gold" type="button">Retry Existing Covenant</button>\n      ${code?`<button id="tcRetryRoom" class="btn ghost" type="button">Reconnect to Saved Room ${h(code)}</button>`:\'\'}\n      <div class="status warn">${h(lastError?.message||\'Temporary sync failure.\')} · Starting a new run is intentionally blocked from this recovery screen.</div>\n    </section>`;\n  document.querySelector(\'#tcRetryResume\')?.addEventListener(\'click\',boot);\n  document.querySelector(\'#tcRetryRoom\')?.addEventListener(\'click\',async()=>{\n    tcRenderResumeStatus(\'Rejoining saved room…\',\'Using the room code stored on this phone.\');\n    try{\n      if(backend.mode!==\'shared\')backend=await createBackend(config);\n      if(backend.mode!==\'shared\')throw new Error(\'Shared sync is still unavailable.\');\n      const joined=await backend.joinRun(code,session?.displayName||\'Tarnished\');\n      tcActivateRememberedRun(joined,session);\n    }catch(error){console.warn(error);tcRenderResumeRecovery(error);}\n  });\n}\n\nasync function tcRecoverRememberedRun(){\n  const remembered={...(session||{})};\n  const hasSharedBreadcrumb=Boolean(remembered.joinCode||incomingCode);\n  const delays=[0,450,1000,1800];\n  let lastError=null;\n  tcRenderResumeStatus();\n\n  for(let attempt=0;attempt<delays.length;attempt+=1){\n    if(delays[attempt])await tcResumeDelay(delays[attempt]);\n    try{\n      if(hasSharedBreadcrumb && backend.mode!==\'shared\'){\n        tcRenderResumeStatus(\'Reconnecting to shared Covenant…\',`Recovery attempt ${attempt+1} of ${delays.length}.`);\n        backend=await createBackend(config);\n      }\n\n      if(remembered.runId && (!hasSharedBreadcrumb || backend.mode===\'shared\')){\n        const recovered=await backend.getRun(remembered.runId);\n        if(recovered?.state)return tcActivateRememberedRun(recovered,remembered);\n        throw new Error(\'Saved run was not returned yet.\');\n      }\n    }catch(error){lastError=error;console.warn(\'Covenant resume attempt failed\',attempt+1,error);}\n  }\n\n  const code=remembered.joinCode||incomingCode||\'\';\n  if(code && backend.mode===\'shared\'){\n    try{\n      tcRenderResumeStatus(\'Rejoining saved room…\',\'The saved run ID did not answer, so the app is recovering through its room code.\');\n      const joined=await backend.joinRun(code,remembered.displayName||\'Tarnished\');\n      if(joined?.state)return tcActivateRememberedRun(joined,remembered);\n    }catch(error){lastError=error;console.warn(\'Saved room recovery failed\',error);}\n  }\n\n  tcRenderResumeRecovery(lastError||new Error(\'Covenant sync is temporarily unavailable.\'));\n  return false;\n}\n\nasync function boot(){\n  if(session?.runId||session?.joinCode||incomingCode){\n    return tcRecoverRememberedRun();\n  }\n  renderHome();\n}\n' + "\n\nfunction renderHome()"
    s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('durable resume guard boot target missing')
    p.write_text(s)
