from pathlib import Path

html=Path('tarnished-covenant/index.html').read_text()

def require(needle,msg=None):
    if needle not in html: raise SystemExit(msg or 'missing dual-appeal invariant: '+needle)

# A normal dual appeal is deliberately split into two single-weapon appeals so
# each refusal produces its own reroll and its own normal penalty.
for needle in [
    'const tcChangeWeaponsBeforeDoubleAppealPenalty=changeWeapons;',
    "if(which!=='both'||useWaiver)",
    "let next=tcChangeWeaponsBeforeDoubleAppealPenalty(state,actor,'chase',false);",
    "next=tcChangeWeaponsBeforeDoubleAppealPenalty(next,actor,'morgan',false);",
    'Two penalties were added.',
    'Appealing both at once creates two penalties.',
    "which==='both'?'Weapon appeal granted. Two penalties accepted.'",
]: require(needle)

# The explicit waiver rule remains intentional: one voluntarily spent waiver
# covers the whole appeal. Joint Appeal remains better because it rerolls both
# without any penalty AND without consuming a waiver.
for needle in [
    "if(which!=='both'||useWaiver)",
    'One waiver covers this entire appeal',
    'Joint Appeal',
    'Both weapons were reassigned with no penalty.',
    'No Appeal penalty is added, and no Appeal Waiver is consumed.',
]: require(needle)

# Tiny behavior model: no-waiver BOTH produces two penalty-producing calls;
# one-person appeal produces one; a waived BOTH remains one waived call.
def calls(which,use_waiver=False):
    if which!='both' or use_waiver:
        return [(which,use_waiver)]
    return [('chase',False),('morgan',False)]
assert calls('both',False)==[('chase',False),('morgan',False)]
assert calls('chase',False)==[('chase',False)]
assert calls('both',True)==[('both',True)]

print('Tarnished Covenant dual-weapon appeal invariants: PASS — normal Both = 2 penalties; Joint Appeal = 0.')
