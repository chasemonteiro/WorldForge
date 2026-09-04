from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
tc = root / 'tarnished-covenant'

old_button = '''<button id="tcRewardContinue" class="btn gold" disabled>${data.index+1<total?'Draw Next Reward':'Continue'}</button>'''
new_button = '''<button id="tcRewardContinue" type="button" class="btn gold" disabled aria-disabled="true">${data.index+1<total?'Draw Next Reward':'Continue'}</button>'''

old_finish = '''    result.hidden=false;result.classList.add('revealed');btn.disabled=false;data.spinning=false;'''
new_finish = '''    result.hidden=false;result.classList.add('revealed');data.spinning=false;btn.disabled=false;btn.setAttribute('aria-disabled','false');btn.dataset.ready='1';'''

old_handler = '''  btn.addEventListener('click',()=>{\n    if(data.spinning)return;\n    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}\n    pendingRewardReveal=null;renderRun();\n  });'''
new_handler = '''  const advanceReward=(event)=>{\n    if(event)event.preventDefault();\n    if(btn.dataset.ready!=='1'||btn.disabled)return;\n    btn.dataset.ready='0';btn.disabled=true;btn.setAttribute('aria-disabled','true');data.spinning=false;\n    if(data.index+1<total){data.index+=1;data.spinning=true;renderRewardMachine();return;}\n    pendingRewardReveal=null;renderRun();\n  };\n  btn.addEventListener('click',advanceReward);\n  btn.addEventListener('pointerup',event=>{if(event.pointerType==='touch')advanceReward(event);});\n  btn.addEventListener('touchend',advanceReward,{passive:false});'''

css = '''\n/* Reward reveal Continue must remain a real iOS Home Screen tap target. */\n.tc-reward-machine #tcRewardContinue{\n  position:relative;\n  z-index:20;\n  pointer-events:auto;\n  touch-action:manipulation;\n  -webkit-tap-highlight-color:transparent;\n}\n'''

for name in ['build-reward-slot.py', 'index.html']:
    p = tc / name
    s = p.read_text()
    if old_button in s:
        s = s.replace(old_button, new_button, 1)
    elif 'id="tcRewardContinue" type="button"' not in s:
        raise SystemExit(f'{name}: reward Continue button target missing')

    if old_finish in s:
        s = s.replace(old_finish, new_finish, 1)
    elif "btn.dataset.ready='1'" not in s:
        raise SystemExit(f'{name}: reward finish target missing')

    if old_handler in s:
        s = s.replace(old_handler, new_handler, 1)
    elif 'const advanceReward=' not in s:
        raise SystemExit(f'{name}: reward handler target missing')

    if 'Reward reveal Continue must remain a real iOS Home Screen tap target.' not in s:
        if '</style>' not in s:
            raise SystemExit(f'{name}: style marker missing')
        s = s.replace('</style>', css + '\n</style>', 1)

    p.write_text(s)

for name in ['build-reward-slot.py','index.html']:
    s=(tc/name).read_text()
    for needle in [
        'id="tcRewardContinue" type="button"',
        "btn.dataset.ready='1'",
        'const advanceReward=',
        "addEventListener('touchend',advanceReward,{passive:false})",
        'touch-action:manipulation',
    ]:
        if needle not in s:
            raise SystemExit(f'{name}: invariant missing: {needle}')
