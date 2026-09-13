from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

required=[
    'let draws=0,guaranteedFavor=1;',
    'nc.smithingRiteFavor=true;draws+=riteDraws;',
    'nc.smithingChaosFavor=true;draws+=chaosDraws;',
    'nextState.smithing.favor+=guaranteedFavor;',
    'nc.favorEarned=guaranteedFavor;',
    'next.history[0].favorEarned=Math.max(0,Number(next.history[0].favorEarned||0))+favorEarned;',
    'Guaranteed Smithing Favor',
    'Bonus Covenant reward draws',
    'Every completed Covenant encounter pays 1 guaranteed Smithing Favor.',
    '1 guaranteed per completed Covenant encounter',
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

# Rite and Chaos must only control bonus draws. Guaranteed Favor is a flat +1 per
# completed encounter and must never creep back into per-source accumulation.
for forbidden in [
    'guaranteedFavor+=riteDraws;',
    'guaranteedFavor+=chaosDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+riteDraws;',
    'guaranteedFavor=Number(guaranteedFavor)+chaosDraws;',
]:
    if forbidden in html:
        raise SystemExit('per-source guaranteed Favor returned: '+forbidden)

if html.count('let draws=0,guaranteedFavor=1;') < 1:
    raise SystemExit('flat +1 guaranteed Favor initialization missing')

print('Tarnished Covenant Smithing Favor invariants: PASS — exactly +1 guaranteed Favor per completed encounter; Rite/Chaos still control bonus draws.')
