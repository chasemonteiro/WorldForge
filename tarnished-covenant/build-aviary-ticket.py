"""Retired compatibility guard.

Dynasty Frequent Flier remains part of the challenge-first reward table.
Reward probabilities are owned only by build-challenge-ruleset.py; persistence,
presentation, and archive durability are enforced by build-final-release-hardening.py.
"""
from pathlib import Path

s = Path('tarnished-covenant/index.html').read_text()
for needle in ['aviaryTickets', "kind:'aviary'", 'Dynasty Frequent Flier']:
    if needle not in s:
        raise SystemExit('Frequent Flier invariant missing: ' + needle)
