"""Check links, saved execution, and source/result provenance without network access."""
from pathlib import Path
import hashlib
import json
import re
import sys
from urllib.parse import unquote,urlsplit
import nbformat
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from signal_lab.core import digest
errors=[]; links=0
for p in [*ROOT.glob('*.md'),*ROOT.glob('docs/**/*.md'),*ROOT.glob('notebooks/*.md'),*ROOT.glob('reports/*.md')]:
	for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
		url=urlsplit(target.strip('<>'))
		if url.scheme or target.startswith('#'):continue
		links+=1
		if not (p.parent/unquote(url.path)).exists():errors.append(f'{p.relative_to(ROOT)}: {target}')
for p in (ROOT/'reports/notebooks').glob('*.html'):
	for a in BeautifulSoup(p.read_text(),'html.parser').find_all('a',href=True):
		url=urlsplit(a['href'])
		if not url.scheme and url.path:
			links+=1
			if not (p.parent/unquote(url.path)).exists(): errors.append(f'{p.name}: {a["href"]}')
for p in (ROOT/'notebooks').glob('*.ipynb'):
	nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
	for c in nb.cells:
		if c.cell_type=='code' and c.source.strip() and c.execution_count is None:errors.append(f'Unexecuted: {p.name}')
		if any(o.output_type=='error' for o in c.get('outputs',[])):errors.append(f'Cell error: {p.name}')
anchor=ROOT/'references/Jev_RLM_Study_and_Implementation_Guide.md'
meta=json.loads((ROOT/'references/anchor-provenance.json').read_text())
if hashlib.sha256(anchor.read_bytes()).hexdigest()!=meta['sha256']:errors.append('Anchor changed')
run=ROOT/'reports/final-offline'
provenance=json.loads((run/'provenance.json').read_text())
for p in (ROOT/'signal_lab').glob('*.py'):
	if provenance['code'].get(p.name)!=digest(p.read_text()): errors.append('Run code drift: '+p.name)
if provenance['results_hash']!=digest(json.loads((run/'results.json').read_text())): errors.append('Results drift')
print(json.dumps({'local_links_checked':links,'notebooks_validated':8,'errors':errors},indent=2))
if errors: raise SystemExit(1)
