"""Run all offline teaching demonstrations and write a fresh evidence bundle."""

from dataclasses import asdict
from pathlib import Path
import json
import platform
import sys
import tempfile

from .core import ExperimentSpec, Harness, RunResult, digest
from .decisions import routing_fixture, choose_action, brier, rule_route
from .investigation import investigate
from .quant import panel, evaluate_panel, incremental_mse, executable_return
from .evolution import compare


def run(output: Path):
	output.mkdir(parents=True, exist_ok=False)
	routing = [{"question": x["question"], "truth": x["truth"], "rule": rule_route(x["question"]),
		**choose_action(x["p"]), "brier": brier(x["p"], x["truth"])} for x in routing_fixture()]
	frame = panel()
	frame.to_csv(output / "synthetic_panel.csv", index=False)
	quant = evaluate_panel(frame)
	quant.to_csv(output / "predictor_results.csv", index=False)
	with tempfile.TemporaryDirectory() as tmp:
		h = Harness(Path(tmp)/"run.sqlite", "fixture", max_calls=1)
		h.register("return", executable_return)
		first = h.step("calculation", "return", {"entry":104,"exit":105,"cost_bps":10})
		h.close()
		h = Harness(Path(tmp)/"run.sqlite", "fixture", max_calls=1)
		h.register("return", lambda **kwargs: (_ for _ in ()).throw(AssertionError("Must replay")))
		replayed = h.step("calculation", "return", {"entry":104,"exit":105,"cost_bps":10})
		h.close()
	results = {"routing": routing, "investigation": [investigate(m) for m in ("fixed","adaptive-fixture")],
		"missing_evidence": investigate(issuer="B"), "evolution": compare(),
		"incremental_mse": incremental_mse(frame), "harness": {"value": first,"replayed": replayed},
		"headline_example": {"unavailable_close_return": .05, "executable_gross": executable_return(104,105),
			"executable_net_10bps": first}, "live_models": "NOT RUN", "real_predictability": "NOT TESTED"}
	spec = ExperimentSpec(output.name, "Demonstrate information and selection failures", "fixed-teaching-examples", data_version="synthetic-v2")
	record = RunResult(output.name, "completed", {}, ["synthetic-v2"],
		["All transfer examples visible; no model-performance or alpha inference"],
		{"api_calls":0,"api_cost_usd":0}, {"python":platform.python_version(),"spec_hash":digest(asdict(spec))})
	(output/"results.json").write_text(json.dumps(results,indent=2,allow_nan=False)+"\n")
	(output/"experiment.json").write_text(json.dumps({"spec":asdict(spec),"run":asdict(record)},indent=2)+"\n")
	code = {p.name:digest(p.read_text()) for p in Path(__file__).parent.glob("*.py")}
	(output/"provenance.json").write_text(json.dumps({"code":code,"panel_hash":digest(frame.to_csv(index=False)),
		"results_hash":digest(results),"evaluation_status":"diagnostic; visible transfer consumed"},indent=2)+"\n")
	return results


if __name__ == "__main__":
	if len(sys.argv) != 2:
		raise SystemExit("Usage: python -m signal_lab.demo NEW_OUTPUT_DIRECTORY")
	run(Path(sys.argv[1]))
	print("Offline demonstration complete. No API calls. Output:", sys.argv[1])
