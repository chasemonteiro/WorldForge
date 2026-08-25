from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Final runtime safety net for the screen navigation helpers. These are deliberately
# injected immediately before app startup so a later build patch cannot accidentally
# remove the helpers while leaving render functions that call them.
marker = "async function startApp(){ backend = await createBackend(config); boot(); }"
if marker not in s:
    raise SystemExit('startApp marker missing for nav safety layer')

helpers = r'''
function navMarkup(active) {
  return `<nav class="tc-bottom-nav">
    <button data-screen="sanctuary" class="${active==='sanctuary'?'active':''}"><span class="nicon">⌂</span><span>Site of Grace</span></button>
    <button data-screen="encounter" class="${active==='encounter'?'active':''}"><span class="nicon">✦</span><span>Encounter</span></button>
    <button data-screen="ledger" class="${active==='ledger'?'active':''}"><span class="nicon">▤</span><span>Ledger</span></button>
    <button data-screen="settings" class="${active==='settings'?'active':''}"><span class="nicon">⚙</span><span>Settings</span></button>
  </nav>`;
}
function bindNav() {
  document.querySelectorAll('[data-screen]').forEach(btn=>btn.addEventListener('click',()=>{
    uiScreen = btn.dataset.screen;
    pendingRevealId = null;
    renderRun();
  }));
}
'''

s = s.replace(marker, helpers + '\n' + marker, 1)

# Runtime helpers must be present in the final assembled document, not merely in a
# source patch. This catches the exact failure seen on a joining Safari client.
for needle in ['function navMarkup(active)', 'function bindNav()', 'function renderRun()']:
    if needle not in s:
        raise SystemExit(f'Navigation invariant missing: {needle}')

p.write_text(s)
