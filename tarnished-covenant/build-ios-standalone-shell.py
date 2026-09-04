from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Keep the installed iOS web app in the viewport mode that avoids the short
# standalone svh box seen on this device.
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
/* body already owns env(safe-area-inset-top). Grace + Encounter used to add
   that same inset again inside app-shell, which pushed both screens down by
   roughly one iPhone status-bar safe area. Keep only the normal 8px shell gap. */
html.tc-standalone body:has(.tc-encounter-shell) .app-shell,
html.tc-standalone body:has(.tc-sanctuary-shell) .app-shell{
  height:100vh!important;
  max-height:100vh!important;
  padding-top:8px!important;
}
/* Keep the Encounter actions comfortably above the fixed bottom nav without
   changing the viewport, nav, panel sizing, or Ledger geometry. */
html.tc-standalone .tc-encounter-actions{
  margin-bottom:88px!important;
}

/* The three transient Covenant notices fit on the phone. Keep the document
   fixed and let the notice itself own the available space instead of creating
   a pointless body scroll. */
html.tc-standalone:has(.tc-chaos-event),
html.tc-standalone:has(.tc-reveal),
html.tc-standalone:has(.tc-reward-machine),
html.tc-standalone body:has(.tc-chaos-event),
html.tc-standalone body:has(.tc-reveal),
html.tc-standalone body:has(.tc-reward-machine){
  height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone body:has(.tc-chaos-event) .app-shell,
html.tc-standalone body:has(.tc-reveal) .app-shell{
  height:calc(100vh - env(safe-area-inset-top))!important;
  max-height:calc(100vh - env(safe-area-inset-top))!important;
  overflow:hidden!important;
  padding:8px 14px calc(70px + env(safe-area-inset-bottom))!important;
}
html.tc-standalone body:has(.tc-reward-machine) .app-shell{
  height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  max-height:calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
  overflow:hidden!important;
  padding:6px 14px!important;
}
html.tc-standalone .tc-chaos-event,
html.tc-standalone .tc-reveal,
html.tc-standalone .tc-reward-machine{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
html.tc-standalone .tc-chaos-event{padding:4px 8px!important}
html.tc-standalone .tc-reward-machine{padding:8px 14px!important;justify-content:center!important}
html.tc-standalone .tc-reveal{padding:0 2px!important}

/* The Weapons panel has ample vertical room on a phone. Give each Tarnished a
   full-width card instead of squeezing both assignments side-by-side. */
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadouts{
  grid-template-columns:1fr!important;
}
html.tc-standalone .tc-encounter-panel[data-panel="weapons"] .tc-loadout + .tc-loadout{
  border-left:0!important;
  border-top:1px solid #54452b!important;
}
'''

# Replace any earlier standalone correction as one unit. This block is owned by
# this patch and is intentionally the final CSS inserted before </style>.
for marker in (
    '/* --- iOS standalone shell: keep Home Screen geometry deterministic --- */',
    '/* --- iOS standalone viewport correction --- */',
):
    start = s.find(marker)
    if start != -1:
        end = s.find('</style>', start)
        if end == -1:
            raise SystemExit('could not locate standalone CSS end')
        s = s[:start] + s[end:]
        break

if '</style>' not in s:
    raise SystemExit('style marker missing')
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
    'padding-top:8px!important',
    'html.tc-standalone .tc-encounter-actions',
    'margin-bottom:88px!important',
    "window.navigator.standalone === true",
]
for needle in required:
    if needle not in s:
        raise SystemExit('standalone invariant missing: ' + needle)

p.write_text(s)
