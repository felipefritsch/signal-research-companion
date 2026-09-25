"""Probabilities are supplied fixtures, not Jev measurements."""

import math

ROUTES = ("documents", "data", "both", "clarify")


def validate_probabilities(probabilities):
	if set(probabilities) != set(ROUTES):
		raise ValueError("Exactly the four declared routes are required")
	if any(not math.isfinite(p) or p < 0 or p > 1 for p in probabilities.values()):
		raise ValueError("Probabilities must be finite and between zero and one")
	if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-8):
		raise ValueError("Probabilities must sum to one")


def choose_action(probabilities, wrong_cost=20.0, review_cost=1.0):
	validate_probabilities(probabilities)
	if not all(math.isfinite(v) and v >= 0 for v in (wrong_cost, review_cost)):
		raise ValueError("Costs must be finite and nonnegative")
	route = max(ROUTES, key=lambda k: probabilities[k])
	loss = wrong_cost * (1 - probabilities[route])
	# Review on ties. Perfect review and symmetric errors are explicit toy assumptions.
	return {"action": route if loss < review_cost else "review", "predicted_route": route,
		"automatic_expected_loss": loss, "chosen_expected_loss": min(loss, review_cost)}


def brier(probabilities, truth):
	validate_probabilities(probabilities)
	if truth not in ROUTES:
		raise ValueError("Unknown label")
	return sum((probabilities[k] - (k == truth)) ** 2 for k in ROUTES)


def rule_route(question):
	q = question.lower()
	docs = any(word in q for word in ("statement", "release", "document"))
	data = any(word in q for word in ("plot", "return", "series"))
	return "both" if docs and data else "documents" if docs else "data" if data else "clarify"


def routing_fixture():
	return [
		{"question": "Compare the releases and plot the series", "truth": "both", "p": dict(zip(ROUTES, [.03,.02,.93,.02]))},
		{"question": "Read this document", "truth": "documents", "p": dict(zip(ROUTES, [.98,.005,.01,.005]))},
		{"question": "What happened?", "truth": "clarify", "p": dict(zip(ROUTES, [.05,.75,.1,.1]))},
		{"question": "Plot the return series", "truth": "data", "p": dict(zip(ROUTES, [.01,.97,.01,.01]))},
	]
