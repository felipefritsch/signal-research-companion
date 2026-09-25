"""Render a compact Markdown report and figures from a selected offline run."""
from pathlib import Path
import json
import sys
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR',tempfile.mkdtemp(prefix='signal-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def render(run, output):
	output.mkdir(exist_ok=True,parents=True)
	r=json.loads((run/'results.json').read_text())
	q=pd.read_csv(run/'predictor_results.csv')
	e=pd.DataFrame(r['evolution']['results'])
	plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
	fig,ax=plt.subplots(1,2,figsize=(13,4.5))
	(q.pivot(index='feature',columns='split',values='mse')*1e8).plot.bar(ax=ax[0],color=['#2b7186','#b86a35'])
	ax[0].set(title='Synthetic prediction: invalid inputs can look excellent',ylabel='MSE (basis points squared)',xlabel='Predictor')
	ax[0].tick_params(axis='x',rotation=0)
	ax[0].legend(['Development','Visible transfer'],fontsize=9)
	e.set_index('method')[['development_accuracy','transfer_accuracy']].plot.bar(ax=ax[1],color=['#2b7186','#b86a35'])
	ax[1].set(title='Constructed harness-selection counterexample',ylabel='Correct fraction (8 tasks per split)',xlabel='',ylim=(0,1.15))
	ax[1].tick_params(axis='x',rotation=12)
	ax[1].legend(['Development','Visible transfer'],fontsize=9)
	fig.text(.5,.01,'Scripted, developer-visible examples. Leaked and spurious predictors are invalid. No live agent or alpha evidence.',ha='center',fontsize=10)
	fig.tight_layout(rect=(0,.055,1,1));fig.savefig(output/'comparison.png',dpi=150);plt.close(fig)
	rows='\n'.join(f"| {x['method']} | {x['candidate']} | {x['development_accuracy']:.0%} | {x['transfer_accuracy']:.0%} | {x['complexity']} |" for x in r['evolution']['results'])
	meta=json.loads((ROOT/'data/public_evidence.json').read_text())
	source_count=sum(x['status']=='extracted' for x in meta)
	text=f'''# Offline research demonstrator — initial evidence

[Start](../START_HERE.md) · [Experiment ledger](../docs/EXPERIMENT_LEDGER.md) · [Interview walkthrough](../docs/INTERVIEW.md)

The project now demonstrates the core boundaries using reproducible synthetic examples and public-source bookkeeping. **Live-model quality, RRSI effectiveness and financial predictability remain untested.**

![Synthetic prediction and harness-selection comparisons](comparison.png)

## What the executed examples show

- **Decision costs:** the routing notebook turns supplied probabilities into accept/review choices. Its four invented cases cannot establish calibration or Jev performance.
- **Context access:** the fixed scan reads five records; the scripted selective policy reads two and answers issuer A's comparison. Issuer B's missing predecessor yields an incomplete result. This is not a measured RLM speedup.
- **Persistence:** the same completed calculation is replayed after reopening without another tool attempt. Failures and attempted retries count toward a persisted budget.
- **Timing:** the unavailable close-to-close return is 5%; the available gross return is {r['headline_example']['executable_gross']:.4%}; the net return under an assumed 10 bps round-trip charge is {r['headline_example']['executable_net_10bps']:.4%}.
- **Additivity:** a duplicated useful predictor changes later-period MSE by {r['incremental_mse']['plus_redundant']-r['incremental_mse']['incumbent']:.2e}, numerical zero. This is a linear-algebra example, not a general rejection rule for correlated signals.
- **Public evidence:** {source_count}/12 releases have source-specific revenue/net-sales extractions. Current copies and date-only metadata do not establish intraday historical availability.

## Harness selection

| Method | Selected candidate | Development | Visible transfer | Added complexity |
|---|---|---:|---:|---:|
{rows}

The construction makes the task-ID shortcut look good on development and fail to transfer. The regularized-inspired selector rejects that shortcut and avoids redundant review. These outcomes are designed into the example, not empirical support for RRSI. The transfer set is visible and consumed. Deterministic repetition has no informative stochastic uncertainty.

## Component decisions

| Component | Current decision | Evidence needed next |
|---|---|---|
| Deterministic calculation and evidence checks | Keep for the learning lab | Extend independent cases as behavior expands |
| Decision interface | Keep; Jev untested | Labelled tasks and a fair rule/classifier/model comparison |
| Adaptive investigation | Further test | Live controller versus fixed/retrieval baselines at matched budgets |
| Persistent harness | Keep for local idempotent tools | Actual async isolation and recovery tests before broader tools |
| RRSI-inspired selection | Keep as a teaching example | Independent live task families and the full declared search protocol |
| OpenRouter model mix / diffusion | Further test; no completions run | Approved budget, pinned providers, quality and total-cost measurements |
| Financial signal | Park | Admitted point-in-time data, explicit target, independent prediction/cost/additivity evidence |

## Limits and provenance

Run source: `{run.relative_to(ROOT)}`. Inspect its `experiment.json`, `provenance.json`, `results.json`, `predictor_results.csv` and synthetic panel. API completions: **0**. Paid API spend: **$0**. Public web downloads and the unauthenticated catalogue request are separate from model calls.

No finding here demonstrates learner mastery. Full lessons are expanded progressively. The first useful next step is [Lesson 1](../docs/modules/01-research-loop.md), not a larger agent fleet.
'''
	(output/'REPORT.md').write_text(text)
	(output/'DOSSIER.md').write_text('''# Initial research dossier

**Status: PARK financial hypothesis; KEEP validated teaching mechanisms.**

**Proposed hypothesis:** an evidence-aware research workflow can reject invalid signal ideas before more expensive investigation. This is a process hypothesis, not an alpha claim.

**Evidence:** the diagnostic run identifies synthetic timing/leakage failures, preserves missing evidence and constructs a development-shortcut failure. Public releases supply traceable descriptive records only.

**Specification:** fixed seed, declared candidates and synthetic data-generating process; earlier-half fit and later-half visible transfer; no permitted changes to arithmetic or task truth. Source inventory frozen before public acquisition and extraction.

**Results:** see the companion report and machine-readable run. No live agents, financial backtest or blinded transfer benchmark were executed.

**Critique:** deterministic success is expected from the fixture design. A live model may choose different steps, make extraction errors or consume extra budget. Current source copies cannot certify historical availability. A cheaper model may need more retries and cost more per valid task.

**Decision:** preserve the lab as an executable lesson. Before financial research, define target returns, information dates, universe, costs and incumbent signals. Before live agents, choose a budget and isolated evaluation set. Promote means advance to an appropriate next research stage, never automatically deploy capital.

**Would change the decision:** independently evaluated improvement on fresh tasks under matched budgets; valid predictive evidence after documented information and execution constraints. Negative findings and rejected variants remain in the ledger.
''')
	print('Rendered report and dossier:',output)

if __name__=='__main__': render(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
