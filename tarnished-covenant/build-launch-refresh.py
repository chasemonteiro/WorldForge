from pathlib import Path
import re
import runpy
from datetime import datetime, timezone

# This is the final production build step. Ensure late UI/stability layers cannot
# leave an outer Covenant-boon busy wrapper around the real refresh handler.
runpy.run_path('tarnished-covenant/build-refresh-handler-final.py')

p=Path('tarnished-covenant/index.html')
s=p.read_text()

# Keep the custom Safari / iOS Home Screen icon present on every full rebuild.
# The PNG itself is a durable asset on the app branch; the versioned filename
# also helps iOS avoid reusing an older cached touch icon.
s=re.sub(r'\n?\s*<link rel="apple-touch-icon"[^>]*>','',s)
s=re.sub(r'\n?\s*<link rel="icon"[^>]*data-tc-app-icon[^>]*>','',s)
icon_anchor='  <meta name="apple-mobile-web-app-title" content="Tarnished Covenant">\n'
if icon_anchor not in s:
    raise SystemExit('apple mobile title anchor missing')
icon_tags='''  <link rel="apple-touch-icon" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png">\n  <link rel="icon" type="image/png" sizes="180x180" href="./assets/tarnished-covenant-icon-v1.png" data-tc-app-icon>\n'''
s=s.replace(icon_anchor,icon_anchor+icon_tags,1)

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

for needle in ['TC_BUILD_ID','tcCheckForFreshBuild','tcForceFreshNavigation','cache:\'no-store\'','rel="apple-touch-icon"','tarnished-covenant-icon-v1.png']:
    if needle not in s: raise SystemExit('freshness/icon invariant missing: '+needle)
p.write_text(s)
