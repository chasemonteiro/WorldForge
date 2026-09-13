from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html:
        raise SystemExit(msg or 'encounter polish invariant missing: '+needle)

# The Boss action shelf must give the replacement dual-world card the full panel
# width rather than leaving it in the old first column of a split action grid.
for needle in [
    "bar.className='tc-encounter-actions tc-boss-victory-actions'",
    '.tc-boss-victory-actions{grid-template-columns:1fr;',
    '.tc-boss-victory-actions>.tc-world-clear-card{grid-column:1/-1;',
    '.tc-boss-victory-actions .tc-world-clear-grid{gap:7px}',
    '.tc-boss-victory-actions .tc-world-clear-btn{min-height:48px;',
]: require(needle)

# Weapon Appeal is a single full-width action in the Weapons panel, including
# its confirmation content.
for needle in [
    "appealBar.className='tc-encounter-actions tc-weapon-appeal-actions'",
    'weaponPanel.appendChild(appealBar);',
    '.tc-weapon-appeal-actions{grid-template-columns:1fr;',
    '.tc-weapon-appeal-actions .tc-actions-3{display:block;width:100%;',
    '.tc-weapon-appeal-actions #appealConfirm{grid-column:1/-1;width:100%}',
]: require(needle)

# Active penalties open visibly by default, remain collapsible, and use a strong
# warning treatment rather than a tiny metadata disclosure.
for needle in [
    '<details class="tc-penalty-summary" open>',
    'ACTIVE WEAPON APPEAL',
    '.tc-penalty-summary{margin:12px 0 14px;',
    'border-left:3px solid var(--red)',
    ".tc-penalty-summary[open] summary:after{content:'COLLAPSE'}",
    '.tc-penalty-summary .penance-item{margin-top:7px;',
]: require(needle)

if html.count('/* --- Encounter action fit + penalty visibility --- */') != 1:
    raise SystemExit('encounter polish layer duplicated')

print('Encounter action polish: PASS — world clears and Appeal fit their panels; active penalties are prominent and open by default.')
