from pathlib import Path

path = Path('tarnished-covenant/build-post-battle.py')
src = path.read_text()
src = src.replace("if 'tc-forge-claims' in s:", "if '<div class=\"tc-forge-claims\">' in s:")
exec(compile(src, str(path), 'exec'))
