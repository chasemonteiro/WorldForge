from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

required=[
    'let draws=0,guaranteedFavor=0;',
    'guaranteedFavor+=riteDraws;',
    'guaranteedFavor+=chaosDraws;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;',
    'Guaranteed Smithing Favor',
    'Bonus Covenant reward draws',
    'Honor pays Smithing Favor immediately.',
    'earned directly by honoring Rites and enduring Chaos',
    'return 4 + tier*2;',
]
for needle in required:
    if needle not in html:
        raise SystemExit('Favor rebalance invariant missing: '+needle)

# Existing random +Favor remains a bonus rather than the sole source.
for needle in [
    "sm.favor+=1;return {kind:'favor'",
    "sm.favor+=2;return {kind:'favor2'",
]:
    if needle not in html:
        raise SystemExit('random Favor bonus unexpectedly missing: '+needle)

# This is intentionally exact. A prior late-build patch matched its own output
# and appended another guaranteed award every deployment.
if html.count('guaranteedFavor+=riteDraws;') != 1:
    raise SystemExit('Rite guaranteed Favor must appear exactly once')
if html.count('guaranteedFavor+=chaosDraws;') != 1:
    raise SystemExit('Chaos guaranteed Favor must appear exactly once')
if 'guaranteedFavor+=riteDraws;guaranteedFavor+=riteDraws;' in html:
    raise SystemExit('Rite guaranteed Favor multiplied by repeated rebuild')
if 'guaranteedFavor+=chaosDraws;guaranteedFavor+=chaosDraws;' in html:
    raise SystemExit('Chaos guaranteed Favor multiplied by repeated rebuild')

print('Tarnished Covenant guaranteed Smithing Favor + bonus reward invariants: PASS — exactly one direct Favor award per source.')
