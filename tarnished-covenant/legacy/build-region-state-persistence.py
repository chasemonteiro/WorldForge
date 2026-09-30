from pathlib import Path

p = Path('tarnished-covenant/index.html')
s = p.read_text()

# Region travel rebuilds the run shell with initialRunState(). Preserve all
# persistent Covenant economy state instead of silently resetting it.
old = """  next.history = [...(state.history || [])];
  next.clearedRegions = [...(state.clearedRegions || [])];
  next.lastAction = `${actor} entered ${region}.`;
  return next;
}"""
new = """  next.history = [...(state.history || [])];
  next.clearedRegions = [...(state.clearedRegions || [])];
  next.smithing = structuredClone(state.smithing || {});
  next.lastAction = `${actor} entered ${region}.`;
  return next;
}"""
if old not in s:
    raise SystemExit('startNextRegion persistence target missing')
s = s.replace(old, new, 1)

# Regression guard: this field must survive every future rebuild.
if "next.smithing = structuredClone(state.smithing || {});" not in s:
    raise SystemExit('smithing persistence invariant missing')

p.write_text(s)
