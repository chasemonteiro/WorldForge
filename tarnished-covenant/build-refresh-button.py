from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

old='''  <div class="tc-kicker gold" style="margin-top:22px">run management</div>
  <button id="restartRun" class="tc-settings-row danger" style="width:100%;border-left:0;border-right:0;border-top:0;background:transparent;text-align:left"><div class="lefty"><div class="name">restart covenant</div><div class="desc">Erase progress and return to the beginning.</div></div><span>↻</span></button>'''
new='''  <div class="tc-kicker gold" style="margin-top:22px">app</div>
  <button id="refreshApp" class="tc-settings-row" style="width:100%;border-left:0;border-right:0;border-top:0;background:transparent;color:var(--ink);text-align:left"><div class="lefty"><div class="name">refresh app</div><div class="desc">Load the latest published version. Your Covenant stays connected.</div></div><span>↻</span></button>
  <div class="tc-kicker gold" style="margin-top:22px">run management</div>
  <button id="restartRun" class="tc-settings-row danger" style="width:100%;border-left:0;border-right:0;border-top:0;background:transparent;text-align:left"><div class="lefty"><div class="name">restart covenant</div><div class="desc">Erase progress and return to the beginning.</div></div><span>↻</span></button>'''
if old not in s:
    raise SystemExit('settings management marker missing')
s=s.replace(old,new,1)

old="bindNav();bindShare();document.querySelector('#restartRun').addEventListener('click',showRestart);document.querySelector('#leave').addEventListener('click',()=>{unsubscribe?.();run=null;clearSession();session=null;renderHome();});"
new="bindNav();bindShare();document.querySelector('#refreshApp')?.addEventListener('click',()=>{const u=new URL(window.location.href);u.searchParams.set('_refresh',Date.now().toString());window.location.replace(u.toString());});document.querySelector('#restartRun').addEventListener('click',showRestart);document.querySelector('#leave').addEventListener('click',()=>{unsubscribe?.();run=null;clearSession();session=null;renderHome();});"
if old not in s:
    raise SystemExit('settings binding marker missing')
s=s.replace(old,new,1)

for needle in ['id="refreshApp"','Load the latest published version','searchParams.set(\'_refresh\'']:
    if needle not in s:
        raise SystemExit('refresh invariant missing: '+needle)

p.write_text(s)
