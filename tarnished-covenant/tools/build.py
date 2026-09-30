#!/usr/bin/env python3
"""Offline, deterministic release builder. Never connects to a saved run."""
from pathlib import Path
import argparse, json, re, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[2]
APP=ROOT/'tarnished-covenant'

def compact(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'))

def js(value):
    if isinstance(value,str):
        if "'" in value: return json.dumps(value,ensure_ascii=False)
        return "'"+value.replace('\\','\\\\').replace('\n','\\n').replace("'","\\'")+"'"
    if isinstance(value,list): return '['+','.join(map(js,value))+']'
    if isinstance(value,dict): return '{'+','.join(k+':'+js(v) for k,v in value.items())+'}'
    return compact(value)

def outputs():
    catalog=json.loads((APP/'data/weapons.json').read_text())
    assert catalog['schemaVersion']==1,'Unknown catalog schema'
    weapons=catalog['weapons']; ids=[w['id'] for w in weapons]
    assert len(ids)==len(set(ids)), 'Duplicate weapon ID'
    pools={r:[] for r in catalog['regionOrder']}
    for w in weapons:
        for entry in w['regions']:
            assert entry['name'] in pools,'Unknown region'
            pools[entry['name']].append((entry['order'],entry['label']))
    for r,entries in pools.items():
        entries.sort()
        assert [i for i,_ in entries]==list(range(len(entries))),f'Duplicate/missing order: {r}'
        pools[r]=[label for _,label in entries]
    gates={w['id']:w for w in weapons if 'acquisition' in w}
    layout=(APP/'src/acquisition-gates.layout').read_text()
    tokens=re.findall(r'\{\{gate:([^}]+)\}\}',layout)
    assert len(tokens)==len(set(tokens)) and set(tokens)==set(gates),'Gate layout and catalog differ'
    def gate(match):
        value=gates[match[1]]['acquisition']
        return ('[\n    '+',\n    '.join(map(js,value))+'\n  ]') if len(value)>1 else js(value)
    regional='const SHEET_WEAPON_POOLS='+compact(pools)+';\nconst SHEET_BOSS_POOLS='+compact(json.loads((APP/'data/boss-pools.json').read_text()))+';'
    acquisition=re.sub(r'\{\{gate:([^}]+)\}\}',gate,layout)
    includes={'generated/regional-pools.js':regional,'generated/acquisition-gates.js':acquisition}
    def expand(text,chain=()):
        def replace(m):
            key=m[1]
            assert key not in chain,'Cyclic source include'
            assert key in includes or key.startswith('src/'),'Unknown source include'
            value=includes[key] if key in includes else (APP/key).read_text()
            return expand(value,chain+(key,))
        return re.sub(r'\{\{((?:src|generated)/[^{}]+)\}\}',replace,text)
    return {'index.html':expand((APP/'src/page.html').read_text()),'regional-pools.js':regional+'\n'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Fail if generated files differ; write nothing')
    parser.add_argument('--test',action='store_true',help='Run the offline release checks after building')
    args=parser.parse_args()
    generated=outputs()
    # Validate before replacing any output.
    with tempfile.TemporaryDirectory() as temp:
        for i,script in enumerate(re.findall(r'<script[^>]*>(.*?)</script>',generated['index.html'],re.S)):
            path=Path(temp)/f'inline-{i}.js';path.write_text(script)
            subprocess.run(['node','--check',str(path)],check=True,capture_output=True)
    for name,text in generated.items():
        path=APP/name
        if args.check:
            if path.read_text()!=text: raise SystemExit(f'Stale generated file: {name}; run python tarnished-covenant/tools/build.py')
        else:
            path.write_text(text)
    print('Release sources and generated files match.' if args.check else 'Built Tarnished Covenant offline.')
    if args.test:
        subprocess.run([sys.executable,str(APP/'tools/verify.py')],cwd=ROOT,check=True)
if __name__=='__main__':main()
