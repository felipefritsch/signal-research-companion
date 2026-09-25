from pathlib import Path
import hashlib
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]

class SourceArtifacts(unittest.TestCase):
	def test_inventory_frozen_and_complete(self):
		p=ROOT/'data/public_inventory.json'
		self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),(ROOT/'data/public_inventory.sha256').read_text().strip())
		rows=json.loads(p.read_text())['records']
		self.assertEqual(len(rows),12)
		self.assertEqual(len({r['id'] for r in rows}),12)
		for issuer in ('AAPL','MSFT','GOOG','AMZN','META','NVDA'):
			self.assertEqual(sum(r['issuer']==issuer for r in rows),2)
		self.assertTrue(all(r['release_date']<='2026-09-24' for r in rows))

	def test_acquisition_hashes(self):
		for row in json.loads((ROOT/'data/public_acquisition.json').read_text()):
			with self.subTest(id=row['id']):
				self.assertEqual(row['fetch_status'],'saved')
				self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])

	def test_independently_read_revenue_fields(self):
		# Headline amounts checked against source passages separately from regex code.
		expected={'AAPL-FY2026Q2':111.2,'AAPL-FY2026Q3':109.4,'MSFT-FY2026Q3':82.9,'MSFT-FY2026Q4':90.0,
			'GOOG-2026Q1':109.9,'GOOG-2026Q2':119.8,'AMZN-2026Q1':181.5,'AMZN-2026Q2':200.6,
			'META-2026Q1':56.31,'META-2026Q2':60.80,'NVDA-FY2027Q1':81.6,'NVDA-FY2027Q2':96.2}
		rows=json.loads((ROOT/'data/public_evidence.json').read_text())
		self.assertEqual({x['id']:x['value'] for x in rows},expected)

	def test_anchor_unchanged(self):
		p=ROOT/'references/Jev_RLM_Study_and_Implementation_Guide.md'
		meta=json.loads((ROOT/'references/anchor-provenance.json').read_text())
		self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),meta['sha256'])

if __name__=='__main__':unittest.main()
