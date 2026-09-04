from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# iOS Home Screen web apps cache status-bar configuration at install time.
# Keep black-translucent: current WebKit reports incorrect standalone viewport
# heights when the app was installed without this mode.
s = s.replace(
    '<meta name="apple-mobile-web-app-status-bar-style" content="black">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
    1,
)

css = r'''
/* --- iOS standalone viewport correction --- */
html.tc-standalone,html.tc-standalone body{
  min-height:100vh!important;
}
/* Grace + Encounter are the only primary screens locked to 100svh. WebKit's
   installed-app viewport can resolve svh short; use the standalone vh box. */
html.tc-standalone body:has(.tc-encounter-shell) .app-shell,
html.tc-standalone body:has(.tc-sanctuary-shell) .app-shell{
  height:100vh!important;
  max-height:100vh!important;
}
'''

# Remove the previous experimental standalone block if present.
start = s.find('/* --- iOS standalone shell: keep Home Screen geometry deterministic --- */')
if start != -1:
    end = s.find('</style>', start)
    if end == -1:
        raise SystemExit('could not locate end of old standalone CSS')
    s = s[:start] + s[end:]

if 'iOS standalone viewport correction' not in s:
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
    'apple-mobile-web-app-status-bar-style" content="black-translucent"',
    'iOS standalone viewport correction',
    'html.tc-standalone body:has(.tc-encounter-shell) .app-shell',
    'height:100vh!important',
    "window.navigator.standalone === true",
]
for needle in required:
    if needle not in s:
        raise SystemExit('standalone invariant missing: ' + needle)

p.write_text(s)
