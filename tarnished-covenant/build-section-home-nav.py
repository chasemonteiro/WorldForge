from pathlib import Path

p=Path('tarnished-covenant/index.html')
s=p.read_text()

marker='/* --- Bottom nav returns primary sections to panel one --- */'
if marker not in s:
    old="""    uiScreen=btn.dataset.screen;
    renderRun();
  });
};

/* Avoid stacking duplicate modal sheets under fast taps. */"""
    new="""    /* --- Bottom nav returns primary sections to panel one --- */
    if(btn.dataset.screen==='sanctuary' && typeof tcSanctuaryPanelIndex!=='undefined')tcSanctuaryPanelIndex=0;
    if(btn.dataset.screen==='encounter' && typeof tcEncounterPanelIndex!=='undefined')tcEncounterPanelIndex=0;
    uiScreen=btn.dataset.screen;
    renderRun();
  });
};

/* Avoid stacking duplicate modal sheets under fast taps. */"""
    if old not in s:
        raise SystemExit('final delegated nav handler target missing')
    s=s.replace(old,new,1)

for needle in [marker,"btn.dataset.screen==='sanctuary'","tcSanctuaryPanelIndex=0","btn.dataset.screen==='encounter'","tcEncounterPanelIndex=0"]:
    if needle not in s:
        raise SystemExit('section-home nav invariant missing: '+needle)

p.write_text(s)
