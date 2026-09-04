from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# iOS Add-to-Home-Screen runs as a standalone web app. Avoid the translucent
# status-bar mode, which lets the page extend under system chrome and gives
# WebKit a different viewport/safe-area model than regular Safari.
s = s.replace(
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black">',
    1,
)

css = r'''
/* --- iOS standalone shell: keep Home Screen geometry deterministic --- */
html.tc-standalone,html.tc-standalone body{min-height:100%;height:100%;}
html.tc-standalone body{
  padding:0!important;
  overflow-x:hidden;
}
html.tc-standalone .app-shell{
  min-height:100%;
  padding-top:calc(16px + env(safe-area-inset-top))!important;
  padding-bottom:calc(86px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone .tc-bottom-nav{
  bottom:0!important;
  height:calc(70px + env(safe-area-inset-bottom))!important;
  padding:5px 10px calc(5px + env(safe-area-inset-bottom))!important;
  box-sizing:border-box!important;
}
'''

if 'iOS standalone shell: keep Home Screen geometry deterministic' not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
<script>
(function(){
  var standalone = window.navigator.standalone === true;
  try { standalone = standalone || window.matchMedia('(display-mode: standalone)').matches; } catch (_) {}
  if (standalone) document.documentElement.classList.add('tc-standalone');
})();
</script>
'''

if "document.documentElement.classList.add('tc-standalone')" not in s:
    s = s.replace('</head>', js + '\n</head>', 1)

required = [
    'content="black">',
    'html.tc-standalone body',
    'height:calc(70px + env(safe-area-inset-bottom))!important',
    "window.navigator.standalone === true",
    "document.documentElement.classList.add('tc-standalone')",
]
for needle in required:
    if needle not in s:
        raise SystemExit('standalone invariant missing: ' + needle)

p.write_text(s)
