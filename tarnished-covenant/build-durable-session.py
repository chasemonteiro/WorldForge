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
