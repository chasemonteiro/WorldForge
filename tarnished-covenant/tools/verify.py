#!/usr/bin/env python3
"""Offline release gate. Discovers all active tests and fails on any failure."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
APP=ROOT/'tarnished-covenant'
checks=[*sorted(APP.glob('test-*.py')),*sorted(APP.glob('test-*.cjs')),*sorted((APP/'tests').glob('*.cjs'))]
failures=[]
for path in checks:
    result=subprocess.run(['node' if path.suffix=='.cjs' else sys.executable,str(path)],cwd=ROOT,text=True,capture_output=True)
    print(('PASS ' if result.returncode==0 else 'FAIL ')+str(path.relative_to(APP)),flush=True)
    if result.returncode:
        failures.append(path.name);print(result.stdout+result.stderr)
if failures: raise SystemExit('Failed: '+', '.join(failures))
print(f'All {len(checks)} offline checks passed. No live backend was used.')
