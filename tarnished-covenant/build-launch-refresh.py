from pathlib import Path
import re
from datetime import datetime, timezone

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Replace any previous freshness guard so every generated build gets a new ID.
s=re.sub(r"\n?/\* --- Home Screen freshness guard --- \*/.*?/\* --- End Home Screen freshness guard --- \*/\n?", "\n", s, flags=re.S)

build_id=datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
js=f'''\n/* --- Home Screen freshness guard --- */\nconst TC_BUILD_ID='{build_id}';\nlet tcFreshnessCheckRunning=false;\nfunction tcForceFreshNavigation(){{\n  const url=new URL(location.href);\n  url.searchParams.set('tcv',String(Date.now()));\n  location.replace(url.toString());\n}}\nasync function tcCheckForFreshBuild(){{\n  if(tcFreshnessCheckRunning||!navigator.onLine)return;\n  tcFreshnessCheckRunning=true;\n  try{{\n    const probe=new URL(location.href);\n    probe.searchParams.set('tc_probe',String(Date.now()));\n    const response=await fetch(probe.toString(),{{cache:'no-store',headers:{{'Cache-Control':'no-cache'}}}});\n    if(!response.ok)return;\n    const text=await response.text();\n    const match=text.match(/const TC_BUILD_ID='([^']+)'/);\n    if(match&&match[1]!==TC_BUILD_ID){{\n      const fresh=new URL(location.href);\n      fresh.searchParams.set('tcv',match[1]);\n      location.replace(fresh.toString());\n    }}\n  }}catch(error){{console.warn('Freshness check failed',error);}}\n  finally{{tcFreshnessCheckRunning=false;}}\n}}\nwindow.addEventListener('pageshow',()=>setTimeout(tcCheckForFreshBuild,350));\ndocument.addEventListener('visibilitychange',()=>{{if(!document.hidden)setTimeout(tcCheckForFreshBuild,200);}});\n/* --- End Home Screen freshness guard --- */\n'''
idx=s.rfind('</script>')
if idx<0: raise SystemExit('script end marker missing')
s=s[:idx]+js+s[idx:]

# Any built-in refresh control must perform a new navigation, not merely revive
# the current iOS standalone snapshot.
s=s.replace("()=>location.reload()", "()=>tcForceFreshNavigation()")
s=s.replace("location.reload();", "tcForceFreshNavigation();")

for needle in ['TC_BUILD_ID','tcCheckForFreshBuild','tcForceFreshNavigation','cache:\'no-store\'']:
    if needle not in s: raise SystemExit('freshness invariant missing: '+needle)
p.write_text(s)
