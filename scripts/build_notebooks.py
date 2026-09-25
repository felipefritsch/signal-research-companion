"""Canonical notebook scaffolds. Deliberately never calls an LLM provider."""
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
SETUP='''from pathlib import Path
import sys, json, tempfile
ROOT = Path.cwd()
if ROOT.name == 'notebooks': ROOT = ROOT.parent
assert (ROOT / 'signal_lab').is_dir(), 'Run from the companion root or notebooks directory'
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.figsize': (8, 4.2), 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
'''
def notebook(slug,title,intro,blocks,checks,next_steps):
 cells=[nbf.v4.new_markdown_cell(f'# {title}\n\n## Goal\n{intro}\n\n**Status:** worked example prepared by Codex; learner understanding unassessed. No API calls.'),
 nbf.v4.new_markdown_cell('## Setup\nRun top to bottom. All examples are synthetic unless explicitly labelled as public evidence.'),nbf.v4.new_code_cell(SETUP),nbf.v4.new_markdown_cell('## Steps')]
 for kind,text in blocks:
  cells.append(nbf.v4.new_markdown_cell(text) if kind=='md' else nbf.v4.new_code_cell(text))
 cells += [nbf.v4.new_markdown_cell('## Checks\n'+checks),nbf.v4.new_markdown_cell('## Next Steps\n'+next_steps+'\n\n**Low energy:** stop here. The checkpoint is optional; reading the worked output does not update mastery.')]
 nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
 nbf.validate(nb);nbf.write(nb,ROOT/'notebooks'/f'{slug}.ipynb')

notebook('01-research-loop','01 · The score must mean the right thing',
'Compare a reported price move with an executable trade. Read [Lesson 1](../docs/modules/01-research-loop.md) first.',[
('md','### 1. Calculate independently\nSynthetic prices: previous close 100, earliest entry 104, later exit 105. Ten basis points is an assumed **round-trip** cost of entry notional.'),
('code',"from fractions import Fraction\nfrom signal_lab.quant import executable_return\nexpected = float(Fraction(105,104) - 1 - Fraction(1,1000))\nnet = executable_return(104,105,10)\nassert abs(net - expected) < 1e-12\nvalues = pd.Series({'Unavailable close-to-close': .05, 'Executable gross': 105/104-1, 'Executable net, 10 bps': net})\n(values * 100).rename('Return (%)').to_frame()"),
('md','### 2. See the timing error\nOnly the latter two bars use an available entry. This is arithmetic, not a measured strategy.'),
('code',"ax=(values*100).plot.barh(color=['#c05746','#2b7186','#225044'])\nax.set(xlabel='Return (%)', title='Synthetic timing example: entry changes the result')\nax.invert_yaxis(); plt.tight_layout(); plt.show()"),
('md','### 3. Identify the editable surface\nChange the cost assumption as a declared sensitivity analysis. Changing entry to an unavailable close violates the experiment. Record those as different interventions.')],
'The exact fraction and shared implementation agree. No market data or model calls were used.',
'Optional: change the cost to 25 bps. Explain why this differs from changing the entry rule. Then go to [decisions](../docs/modules/02-decisions.md).')

notebook('02-decisions','02 · Prediction becomes a decision through losses',
'Work with supplied probabilities. These are invented fixtures, not Jev outputs.',[
('md','### 1. Inspect routes and consequences'),
('code',"from signal_lab.decisions import routing_fixture, choose_action, brier, rule_route\nrows=[{'truth':x['truth'], 'rule':rule_route(x['question']), **choose_action(x['p']), 'Brier':brier(x['p'],x['truth'])} for x in routing_fixture()]\npd.DataFrame(rows).round(3)"),
('md','### 2. Derive the threshold\nFor symmetric wrong-route cost 20 and perfect review cost 1, accept when `20(1−p) < 1`. Equality goes to review. The model probability must be meaningful for this decision; this plot does not establish calibration.'),
('code',"p=np.linspace(.75,1,101)\nplt.plot(p,20*(1-p),label='Automatic expected loss')\nplt.axhline(1,color='#b86a35',label='Perfect review cost')\nplt.axvline(.95,color='gray',linestyle='--',label='Threshold 0.95')\nplt.xlabel('Probability correct, assumed'); plt.ylabel('Expected loss (arbitrary units)')\nplt.title('Synthetic decision costs');plt.legend();plt.tight_layout();plt.show()")],
'Inspect the confidently wrong ambiguous-question fixture. Four invented cases do not support a calibration conclusion.',
'Optional: make review cost 2 and derive the new threshold before plotting. OpenRouter later supplies alternative models for the same interface; Jev availability is separate.')

notebook('03-investigation','03 · Available context is not observed context',
'Trace a fixed scan and a scripted selective policy over five manifest records. Neither path calls a language model.',[
('md','### 1. Compare the two access policies'),
('code',"from signal_lab.investigation import investigate\nfixed=investigate('fixed'); selective=investigate()\npd.DataFrame([{k:r[k] for k in ['mode','complete_for_question','manifest_records_seen','manifest_size','change']} for r in [fixed,selective]])"),
('md','### 2. Observe the context boundary'),
('code',"pd.DataFrame(selective['trace'])"),
('md','### 3. Missing evidence must survive synthesis'),
('code',"missing=investigate(issuer='B')\nassert missing['change'] is None\npd.DataFrame([{'issuer':missing['issuer'],'complete':missing['complete_for_question'],'missing':', '.join(missing['missing'])}])"),
('code',"plt.bar(['Fixed scan','Selective fixture'],[len(fixed['trace']),len(selective['trace'])],color=['#2b7186','#b86a35'])\nplt.ylim(0,6);plt.ylabel('Document reads');plt.title('Scripted access cost for issuer A — equal task coverage')\nplt.tight_layout();plt.show()")],
'Archive coverage and question coverage differ. The missing document remains explicit. The policy is prewritten; no RLM-quality or efficiency claim follows.',
'Optional: draw which observations a real controller would receive before choosing each read. Discuss a question for which the selective policy would miss necessary evidence.')

notebook('04-harness','04 · Recover work without pretending every action is atomic',
'Persist one completed deterministic calculation, reopen the session and replay the saved result.',[
('md','### 1. Register a bounded tool and persist its answer'),
('code',"from signal_lab.core import Harness, BudgetExceeded\nfrom signal_lab.quant import executable_return\nwith tempfile.TemporaryDirectory() as tmp:\n    path=Path(tmp)/'run.sqlite'\n    h=Harness(path,'lesson',max_calls=1)\n    h.register('return',executable_return)\n    first=h.step('s1','return',{'entry':104,'exit':105,'cost_bps':10})\n    h.close()\n    h=Harness(path,'lesson',max_calls=1)\n    h.register('return',lambda **kwargs: 999)\n    replay=h.step('s1','return',{'entry':104,'exit':105,'cost_bps':10})\n    events=h.db.execute('SELECT step,status FROM events').fetchall()\n    h.close()\nassert first == replay and replay != 999\npd.DataFrame(events,columns=['step','status'])"),
('md','### 2. Reason about interruption\nA crash after a real external side effect but before persistence can leave an ambiguous outcome. This local runner supports idempotent teaching tools; it does not promise exactly-once external writes. Prime Agent child handles likewise need explicit completion and failure handling.'),
('code',"pd.DataFrame([{'first_result':first,'replayed_result':replay,'actual_tool_attempts':sum(s=='started' for _,s in events)}])")],
'Only one tool attempt occurred despite reopening. See tests for failures consuming budget, explicit resume and changed inputs being rejected.',
'Optional: add one evidence-validation function to the allowed tools. Keep arbitrary shell/code execution outside this teaching runner.')

notebook('05-quant-validity','05 · Temporal splitting cannot repair a future-leaking feature',
'Use a known synthetic panel to distinguish useful, redundant, spurious and invalid information.',[
('md','### 1. Generate and inspect the panel\n180 dates × eight invented assets. Common shocks create cross-sectional dependence. A toy 0.004 coefficient defines the useful signal; it is not estimated economic truth.'),
('code',"from signal_lab.quant import panel,evaluate_panel,incremental_mse,assert_available\nf=panel(seed=7); result=evaluate_panel(f)\nresult.round(7)"),
('md','### 2. Compare prediction errors\nThe spurious predictor uses outcomes in its development construction. The leaked predictor equals the target. Both are invalid; perfect error is not a pass.'),
('code',"pivot=result.pivot(index='feature',columns='split',values='mse')*1e8\nax=pivot.plot.bar(color=['#2b7186','#b86a35'])\nax.set(title='Synthetic predictive error — leaked and spurious inputs are INVALID',ylabel='MSE (basis points squared)',xlabel='Predictor')\nplt.xticks(rotation=0);plt.tight_layout();plt.show()"),
('md','### 3. Check incremental prediction and timestamps'),
('code',"incremental_mse(f)"),
('code',"future=f['available_at']+pd.Timedelta(days=1)\ntry:\n    assert_available(future,f['decision_at'])\nexcept ValueError as error:\n    print('Expected rejection:',error)"),
('md','Metadata checks catch declared late arrivals. They cannot detect a lied-about timestamp or contamination inside model weights. Provenance is part of the research design, not just a parser check.')],
'Train/test rows are split by date; duplicate information gives no incremental least-squares gain. No naive independent-row significance or real-return inference is reported.',
'Optional: explain why a leaked feature can succeed on the later half. Read the Baker bridge before designing any historical LLM signal test.')

notebook('06-evolution','06 · Selection can reward a shortcut',
'Inspect a deliberately constructed search example. It is RRSI-inspired design practice, not a paper replication.',[
('md','### 1. Inspect all candidate changes before seeing selection'),
('code',"from signal_lab.evolution import compare\ne=compare()\npd.DataFrame(e['candidates'])"),
('md','### 2. Compare the frozen rule and two selectors'),
('code',"results=pd.DataFrame(e['results']);results"),
('code',"ax=results.set_index('method')[['development_accuracy','transfer_accuracy']].plot.bar(color=['#2b7186','#b86a35'])\nax.set(ylim=(0,1.15),ylabel='Correct fraction (8 constructed tasks per split)',xlabel='',title='Visible teaching fixture — not measured agent generalization')\nplt.xticks(rotation=0);plt.tight_layout();plt.show()"),
('md','The lookup shortcut wins the unregularized tie-break; screening it selects a reusable evidence rule. Extra review adds complexity without changing these constructed answers. Real pruning must account for interactions and noise.'),
('code',"print(e['transfer_status'])\nprint('Paper mechanisms not implemented:', ', '.join(e['unimplemented_paper_features']))")],
'Both search methods inspect the same candidate shortlist. Transfer fixtures are visible and consumed. No stochastic variability can be estimated from identical deterministic reruns.',
'Optional: suggest a case where the extra review could matter. A live comparison needs fresh isolated tasks, a fixed backbone and matched search budgets.')

notebook('07-synthesis','07 · Transfer evidence bookkeeping to public releases',
'Inspect a frozen 12-release source inventory and source-specific deterministic extraction. This is public descriptive evidence, not a return forecast.',[
('md','### 1. Verify the inventory and acquired bytes'),
('code',"import hashlib\ninventory_path=ROOT/'data/public_inventory.json'\nassert hashlib.sha256(inventory_path.read_bytes()).hexdigest()==(ROOT/'data/public_inventory.sha256').read_text().strip()\ninv=json.loads(inventory_path.read_text()); acquired=json.loads((ROOT/'data/public_acquisition.json').read_text())\nassert len(inv['records'])==12\nfor a in acquired:\n    if a['fetch_status']=='saved':\n        assert hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()==a['sha256']\npd.DataFrame(inv['records'])[['issuer','period','release_date','available_at_intraday']]"),
('md','### 2. Inspect the extracted field and evidence\nAmounts are rounded headline revenue/net-sales figures in USD billion. Different fiscal periods and company definitions are preserved; do not treat this as a standardized performance ranking.'),
('code',"evidence=pd.DataFrame(json.loads((ROOT/'data/public_evidence.json').read_text()))\nevidence[['id','status','value','unit','short_span']]"),
('md','### 3. Convert evidence into a research proposal\nA proposed hypothesis might concern guidance revisions and subsequent returns. Before testing it, define guidance versus realized revenue, acquire actual guidance fields, fix decision/entry timestamps, admit return data and choose controls. The current revenue extraction does not establish that hypothesis.'),
('code',"pd.DataFrame([{'inventory_records':len(inv['records']),'acquired_records':sum(x['fetch_status']=='saved' for x in acquired),'extracted_records':sum(evidence.status=='extracted'),'live_model_runs':0}])")],
'Source hashes and counts are inspectable. Intraday historical availability remains unknown. The source-specific parser is not an LLM extraction benchmark.',
'Optional: inspect one source and verify its field and fiscal label. Use the dossier template to state what is established and what remains unresolved.')

notebook('08-model-efficiency','08 · OpenRouter model economics and diffusion candidates',
'Inspect a saved catalogue and perform cost arithmetic offline. No key is loaded and no network request is made.',[
('md','### 1. Read the saved diffusion candidates\nCatalogue prices are advertised metadata, not measured bills or quality evidence. Confirm availability again before paid experiments.'),
('code',"catalog=json.loads((ROOT/'data/openrouter_catalogue.json').read_text())\nmodels=[m for m in catalog['data'] if m['id'].startswith('inception/')]\nprices=pd.DataFrame([{'model':m['id'],'USD_per_million_input':float(m['pricing']['prompt'])*1e6,'USD_per_million_output':float(m['pricing']['completion'])*1e6,'context':m['context_length']} for m in models])\nprices"),
('md','### 2. Calculate a token-only estimate\nAssume 2,000 input and 300 output tokens per task, 40 tasks and three repeats. This excludes additional reasoning, retries, provider fees and uncertainty about actual tokenization. It is a scenario, not budget approval.'),
('code',"estimate=prices.copy()\nestimate['scenario_USD']=(2000*estimate.USD_per_million_input+300*estimate.USD_per_million_output)/1e6*40*3\nestimate[['model','scenario_USD']]"),
('md','### 3. Cheaper tokens can produce more expensive completed work\nThe following model names and measurements are **invented**. There are 20 attempted tasks in each row, including failures in the total spend.'),
('code',"toy=pd.DataFrame({'fixture':['Cheap A','Stronger B'],'total_cost_USD':[.10,.16],'valid_tasks':[8,18]})\ntoy['cost_per_valid_task']=toy.total_cost_USD/toy.valid_tasks\ntoy"),
('code',"ax=toy.set_index('fixture').cost_per_valid_task.plot.bar(color=['#b86a35','#2b7186'])\nax.set(ylabel='USD per valid task',xlabel='',title='Invented scenario: total cost includes failed tasks')\nplt.xticks(rotation=0);plt.tight_layout();plt.show()"),
('md','### 4. Inspect the request without sending it'),
('code',"from signal_lab.openrouter import request_payload\nrequest=request_payload('inception/mercury-2.5','Synthetic task: choose documents, data, both or clarify.','PROVIDER_TO_SELECT_AFTER_BUDGET_REVIEW')\n{k:v for k,v in request.items() if k!='messages'}")],
'The adapter does not send this request. There is no latency or quality ranking of actual models. Compare role-specific quality and errors before cost; diffusion architecture is not a guarantee.',
'Choose task cases before models. Agree a spending cap and provider pair before live calls. Non-streaming completion latency cannot be reported as time to first token.')

index=['# Notebook index','', 'All notebooks contain worked examples. They make no paid or unauthenticated network calls. Saved outputs come from local execution; no learner mastery is implied.','']
for p in sorted((ROOT/'notebooks').glob('*.ipynb')):index.append(f'- [{p.stem}]({p.name})')
index.extend(['','Open in VS Code/Jupyter, or use the corresponding rendered HTML files in `reports/notebooks/`. Run from the project root or notebook directory.'])
(ROOT/'notebooks/README.md').write_text('\n'.join(index)+'\n')
print('Created eight notebook scaffolds')
