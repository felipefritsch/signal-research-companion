"""Visible teaching fixtures, NOT an RRSI reproduction or hidden benchmark."""

from dataclasses import asdict
from .core import CandidateChange

CANDIDATES = (
	CandidateChange("base", "Use surface label", (), 0),
	CandidateChange("memorize", "Memorize development task identifiers", ("task-id shortcut",), 1, True),
	CandidateChange("check-evidence", "Resolve labels from available evidence", ("read evidence",), 1),
	CandidateChange("extra-review", "Recheck every answer", ("read evidence", "duplicate review"), 2),
)


def tasks(split):
	if split not in ("development", "visible_transfer"):
		raise ValueError("Unknown split")
	return [{"id": f"{split}-{i}", "surface": i % 2, "evidence": (i//2) % 2,
		"truth": (i//2) % 2} for i in range(8)]


def score(candidate, split):
	items = tasks(split)
	def predict(task):
		if candidate.id == "memorize" and split == "development":
			return {t["id"]: t["truth"] for t in tasks("development")}[task["id"]]
		if "read evidence" in candidate.edits:
			return task["evidence"]
		return task["surface"]
	return sum(predict(t) == t["truth"] for t in items) / len(items)


def compare():
	# Candidate sequence and tie-breaking are frozen. Both searches inspect 3 candidates.
	# Regularization here is an explicit shortcut screen + complexity-aware tie break.
	dev = {c.id: score(c, "development") for c in CANDIDATES}
	unregularized = max(CANDIDATES, key=lambda c: dev[c.id])
	allowed = [c for c in CANDIDATES if not c.benchmark_specific]
	regularized = max(allowed, key=lambda c: (dev[c.id], -c.complexity))
	selected = {"frozen": CANDIDATES[0], "unregularized": unregularized, "regularized-inspired": regularized}
	return {"kind": "constructed deterministic counterexample", "transfer_status": "visible and consumed; not a blinded holdout",
		"results": [{"method": name, "candidate": c.id, "development_accuracy": dev[c.id],
			"transfer_accuracy": score(c, "visible_transfer"), "complexity": c.complexity,
			"search_candidates": 0 if name == "frozen" else 3} for name,c in selected.items()],
		"candidates": [asdict(c) for c in CANDIDATES],
		"unimplemented_paper_features": ["model-generated edits", "shrinking edit budget", "novelty search", "statistical selection", "interaction-aware pruning"]}
