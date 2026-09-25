"""Deterministic, source-specific single-field extraction from frozen current copies."""
from pathlib import Path
import hashlib
import json
import re
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
'AAPL':r'quarterly revenue of \$([\d.]+) billion',
'MSFT':r'Revenue was \$([\d.]+) billion',
'GOOG':r'Consolidated Alphabet revenues increased.{0,100}?to \$([\d.]+) billion',
'AMZN':r'Net sales increased \d+% to \$([\d.]+) billion',
'META':r'Revenue was \$([\d.]+) billion',
'NVDA':r'(?:Record revenue of|reported revenue for the second quarter.{0,100}?of) \$([\d.]+) billion',
}

def extract():
	inventory=ROOT/'data/public_inventory.json'
	if hashlib.sha256(inventory.read_bytes()).hexdigest() != (ROOT/'data/public_inventory.sha256').read_text().strip():
		raise ValueError('Frozen inventory changed')
	acquisitions=json.loads((ROOT/'data/public_acquisition.json').read_text())
	rows=[]
	for a in acquisitions:
		if a['fetch_status']!='saved':
			rows.append({'id':a['id'],'status':'unavailable','value':None});continue
		p=ROOT/a['path'];raw=p.read_bytes()
		if hashlib.sha256(raw).hexdigest()!=a['sha256']: raise ValueError('Source changed: '+a['id'])
		if p.suffix=='.pdf':
			text=' '.join(PdfReader(p).pages[0].extract_text().split()); locator='PDF page 1'
		else:
			soup=BeautifulSoup(raw,'html.parser')
			for node in soup(['script','style','nav','footer']): node.decompose()
			text=' '.join(soup.get_text(' ',strip=True).split());locator='normalized HTML text'
		match=re.search(PATTERNS[a['issuer']],text,re.I)
		if not match:
			rows.append({'id':a['id'],'status':'unresolved','value':None});continue
		# Short source span preserves provenance without reproducing the release.
		span=text[match.start(1)-1:match.end(1)+8]
		rows.append({'id':a['id'],'issuer':a['issuer'],'period':a['period'],'release_date':a['release_date'],
			'status':'extracted','field':'quarterly reported revenue/net sales','value':float(match.group(1)),
			'unit':'USD billion (rounded headline amount)','source':a['url'],'source_sha256':a['sha256'],
			'locator':locator,'normalized_text_offset':match.start(1),'short_span':span,
			'method':'source-specific regular expression; not an LLM','historical_availability':'unverified intraday/version',
			'interpretation':'descriptive evidence only; not standardized cross-company profitability or a signal'})
	(ROOT/'data/public_evidence.json').write_text(json.dumps(rows,indent=2)+'\n')
	return rows

if __name__=='__main__':
	rows=extract();print('Public records:',len(rows),'extracted:',sum(x['status']=='extracted' for x in rows))
