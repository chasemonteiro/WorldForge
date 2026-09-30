from pathlib import Path

src = Path('tarnished-covenant/build-risk-rebalance.py').read_text()
src = src.replace(",'Grand Rite honored'", "")
exec(compile(src, 'build-risk-rebalance.py', 'exec'))
