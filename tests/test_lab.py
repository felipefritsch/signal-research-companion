import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from signal_lab.core import Harness, BudgetExceeded
from signal_lab.decisions import choose_action, brier, ROUTES
from signal_lab.investigation import investigate
from signal_lab.quant import panel, evaluate_panel, incremental_mse, executable_return, assert_available
from signal_lab.evolution import compare
from signal_lab.openrouter import OpenRouterClient, request_payload


class Decisions(unittest.TestCase):
	def test_loss_rule(self):
		p=dict(zip(ROUTES,[.98,.01,.005,.005]))
		self.assertEqual(choose_action(p)['action'],'documents')
		self.assertAlmostEqual(choose_action(p)['automatic_expected_loss'],.4)
		self.assertEqual(choose_action(p,review_cost=.1)['action'],'review')

	def test_brier_independent(self):
		p=dict(zip(ROUTES,[.7,.1,.1,.1]))
		self.assertAlmostEqual(brier(p,'documents'),.12)

	def test_malformed_probabilities(self):
		for p in [{'documents':1},dict(zip(ROUTES,[.8,.1,.1,.1])),dict(zip(ROUTES,[math.nan,0,0,1])),dict(zip(ROUTES,[-.1,.1,.1,.9]))]:
			with self.subTest(p=p), self.assertRaises(ValueError): choose_action(p)

	def test_invalid_costs(self):
		with self.assertRaises(ValueError): choose_action(dict(zip(ROUTES,[1,0,0,0])),wrong_cost=-1)


class Evidence(unittest.TestCase):
	def test_task_coverage_differs_from_manifest(self):
		r=investigate()
		self.assertTrue(r['complete_for_question'])
		self.assertEqual(r['evidence_ids'],['a-current','a-previous'])
		self.assertEqual(r['manifest_records_seen'],2)
		self.assertEqual(r['manifest_size'],5)

	def test_missing_predecessor_preserved(self):
		r=investigate(issuer='B')
		self.assertFalse(r['complete_for_question'])
		self.assertEqual(r['missing'],['b-previous'])
		self.assertIsNone(r['change'])

	def test_global_read_budget(self):
		with self.assertRaises(BudgetExceeded): investigate(max_reads=1)

	def test_injection_is_inert_text(self):
		r=investigate('fixed')
		self.assertEqual(r['change'],'stable -> weakening')
		self.assertIn('export files',r['trace'][-1]['observation'])


class Quant(unittest.TestCase):
	def test_return_independent_fraction(self):
		from fractions import Fraction
		self.assertAlmostEqual(executable_return(104,105,10),float(Fraction(1,104)-Fraction(1,1000)))

	def test_invalid_prices(self):
		for entry,exit,cost in [(0,100,1),(100,-1,0),(100,101,-1),(math.nan,101,0)]:
			with self.subTest(entry=entry),self.assertRaises(ValueError): executable_return(entry,exit,cost)

	def test_future_and_missing_availability(self):
		for a in [['2020-01-02'],[None]]:
			with self.subTest(a=a),self.assertRaises(ValueError): assert_available(pd.Series(a),pd.Series(['2020-01-01']))

	def test_equal_time_allowed(self):
		assert_available(pd.Series(['2020-01-01']),pd.Series(['2020-01-01']))

	def test_panel_reproducible_and_duplicate_no_gain(self):
		f=panel();pd.testing.assert_frame_equal(f,panel())
		m=incremental_mse(f)
		self.assertAlmostEqual(m['incumbent'],m['plus_redundant'],places=15)

	def test_leakage_can_survive_time_split(self):
		r=evaluate_panel(panel()); leaked=r[r.feature=='leaked']
		self.assertTrue((leaked.mse < 1e-20).all())
		self.assertFalse(leaked.valid.any())


class Persistence(unittest.TestCase):
	def setUp(self):
		self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'runs.sqlite'
	def tearDown(self): self.tmp.cleanup()

	def test_restart_replays_result(self):
		h=Harness(self.path,'r',1);h.register('add',lambda a,b:a+b)
		self.assertEqual(h.step('s','add',{'a':2,'b':3}),5);h.close()
		h=Harness(self.path,'r',1);h.register('add',lambda **kw:self.fail('Re-executed'))
		self.assertEqual(h.step('s','add',{'a':2,'b':3}),5);h.close()

	def test_changed_inputs_rejected(self):
		h=Harness(self.path,'r');h.register('id',lambda x:x);h.step('s','id',{'x':1})
		with self.assertRaises(ValueError): h.step('s','id',{'x':2})
		h.close()

	def test_failure_consumes_budget(self):
		h=Harness(self.path,'r',1);h.register('bad',lambda:1/0)
		with self.assertRaises(ZeroDivisionError): h.step('s','bad',{})
		with self.assertRaises(RuntimeError): h.step('s','bad',{})
		with self.assertRaises(BudgetExceeded): h.step('s','bad',{},resume=True)
		h.close()

	def test_resume_and_budget_cannot_reset(self):
		h=Harness(self.path,'r',2);h.register('recover',lambda:1/0)
		with self.assertRaises(ZeroDivisionError): h.step('s','recover',{})
		h.register('recover',lambda:42);self.assertEqual(h.step('s','recover',{},resume=True),42);h.close()
		with self.assertRaises(ValueError): Harness(self.path,'r',3)

	def test_unknown_tool(self):
		h=Harness(self.path,'r')
		with self.assertRaises(ValueError): h.step('x','shell',{})
		h.close()


class Evolution(unittest.TestCase):
	def test_constructed_counterexample(self):
		r={x['method']:x for x in compare()['results']}
		self.assertEqual(r['unregularized']['candidate'],'memorize')
		self.assertEqual(r['unregularized']['transfer_accuracy'],.5)
		self.assertEqual(r['regularized-inspired']['candidate'],'check-evidence')
		self.assertEqual(r['regularized-inspired']['transfer_accuracy'],1)
		self.assertIn('visible',compare()['transfer_status'])


class Provider(unittest.TestCase):
	def setUp(self):
		self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'calls.sqlite'
		self.payload=request_payload('test/model','Public synthetic prompt','TestProvider')
		self.env=patch.dict(os.environ,{'OPENROUTER_API_KEY':'not-a-real-key'});self.env.start()
	def tearDown(self): self.env.stop();self.tmp.cleanup()

	def response(self,cost=.002):
		return {'id':'fixture-id','model':'test/model','provider':'TestProvider','usage':{'cost':cost,'prompt_tokens':10,'completion_tokens':5},'choices':[{'finish_reason':'stop','message':{'content':'documents'}}]}

	def test_payload_pins_provider(self):
		self.assertFalse(self.payload['provider']['allow_fallbacks'])
		self.assertEqual(self.payload['provider']['only'],['TestProvider'])
		self.assertTrue(self.payload['provider']['require_parameters'])

	def test_altered_routing_is_rejected_before_call(self):
		c=OpenRouterClient(self.path,.1,live_enabled=True,transport=lambda *a:self.fail('Should block'))
		self.payload['provider']['allow_fallbacks']=True
		with self.assertRaises(ValueError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		c.close()

	def test_explicit_free_model_is_supported(self):
		payload=request_payload('vendor/model:free','Synthetic prompt','ExplicitProvider',prompt_price_per_million=0,completion_price_per_million=0)
		self.assertEqual(payload['model'],'vendor/model:free')

	def test_disabled_does_not_call(self):
		c=OpenRouterClient(self.path,1,transport=lambda *a:self.fail('Network attempted'))
		with self.assertRaises(PermissionError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		c.close()

	def test_success_accounts_actual_usage(self):
		c=OpenRouterClient(self.path,.1,live_enabled=True,transport=lambda *a:self.response())
		r=c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		self.assertEqual(r['text'],'documents');self.assertEqual(r['metadata']['usage']['cost'],.002)
		self.assertNotIn('Public synthetic prompt',c.db.execute('SELECT metadata FROM calls').fetchone()[0]);c.close()

	def test_missing_cost_blocks_next_call(self):
		c=OpenRouterClient(self.path,.1,live_enabled=True,transport=lambda *a:self.response(None))
		with self.assertRaises(RuntimeError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		c.transport=lambda *a:self.fail('Should block')
		with self.assertRaises(RuntimeError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='b')
		c.close()

	def test_ambiguous_failure_no_retry(self):
		calls=[]
		def fail(*args): calls.append(1);raise TimeoutError()
		c=OpenRouterClient(self.path,.1,live_enabled=True,transport=fail)
		for i in range(2):
			with self.assertRaises(RuntimeError): c.complete(self.payload,reservation_usd=.01,role='router',task_id=str(i))
		self.assertEqual(len(calls),1);c.close()

	def test_exhausted_budget(self):
		c=OpenRouterClient(self.path,.001,live_enabled=True,transport=lambda *a:self.fail('Should block'))
		with self.assertRaises(RuntimeError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		c.close()

	def test_cost_exceeds_reservation(self):
		c=OpenRouterClient(self.path,.1,live_enabled=True,transport=lambda *a:self.response(.02))
		with self.assertRaises(RuntimeError): c.complete(self.payload,reservation_usd=.01,role='router',task_id='a')
		self.assertEqual(c.db.execute('SELECT charged,status FROM calls').fetchone(),(.02,'needs_reconciliation'));c.close()

	def test_invalid_budget(self):
		for value in [math.nan,math.inf,0,-1]:
			with self.subTest(value=value),self.assertRaises(ValueError): OpenRouterClient(self.path,value)


if __name__=='__main__': unittest.main()
