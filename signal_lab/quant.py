"""A known data-generating process, deliberately unsuitable for alpha claims."""

import numpy as np
import pandas as pd


def panel(seed=7, periods=180, assets=8):
	if periods < 30 or assets < 2:
		raise ValueError("Need at least 30 periods and two assets")
	rng = np.random.default_rng(seed)
	x = rng.normal(size=(periods, assets))
	common = rng.normal(0, .006, (periods, 1))
	y = .004 * x + common + rng.normal(0, .015, x.shape)
	# Keep feature scale comparable across halves so the lesson isolates a
	# correlation failure rather than a thousand-fold units change.
	noise = rng.normal(0, .02, size=x.shape)
	# Deliberate developer-visible trap: strong correlation confined to development.
	spurious = noise.copy()
	spurious[:periods//2] = y[:periods//2] + rng.normal(0, .002, y[:periods//2].shape)
	dates = pd.date_range("2000-01-01", periods=periods, freq="D", tz="UTC")
	return pd.DataFrame({"time": np.repeat(np.arange(periods), assets),
		"asset": np.tile([f"S{i}" for i in range(assets)], periods),
		"decision_at": np.repeat(dates, assets), "available_at": np.repeat(dates, assets),
		"useful": x.ravel(), "redundant": (2*x).ravel(), "spurious": spurious.ravel(),
		"leaked": y.ravel(), "return": y.ravel()})


def assert_available(available, decision):
	a, d = pd.to_datetime(available, utc=True), pd.to_datetime(decision, utc=True)
	if a.isna().any() or d.isna().any() or (a > d).any():
		raise ValueError("Missing or future information at decision time")


def evaluate_panel(frame):
	assert_available(frame.available_at, frame.decision_at)
	cut = int(frame.time.max() + 1) // 2
	train, test = frame[frame.time < cut], frame[frame.time >= cut]
	rows = []
	for feature in ("useful", "redundant", "spurious", "leaked"):
		coef = np.linalg.lstsq(np.column_stack([np.ones(len(train)), train[feature]]), train["return"], rcond=None)[0]
		for split, part in (("development", train), ("visible_transfer", test)):
			prediction = coef[0] + coef[1]*part[feature].to_numpy()
			rows.append({"feature": feature, "split": split, "mse": float(np.mean((prediction-part["return"])**2)),
				"correlation": float(np.corrcoef(prediction, part["return"])[0,1]),
				"valid": feature not in ("spurious", "leaked")})
	return pd.DataFrame(rows)


def executable_return(entry, exit, cost_bps=0):
	if not all(np.isfinite(v) for v in (entry, exit, cost_bps)) or min(entry, exit) <= 0 or cost_bps < 0:
		raise ValueError("Positive prices and finite nonnegative round-trip cost required")
	# Cost is explicitly round-trip bps of entry notional, not per-leg cost.
	return exit / entry - 1 - cost_bps / 10000


def incremental_mse(frame):
	cut = (frame.time.max()+1)//2
	train, test = frame[frame.time < cut], frame[frame.time >= cut]
	values = {}
	for name, columns in {"incumbent": ["useful"], "plus_redundant": ["useful", "redundant"]}.items():
		x = np.column_stack([np.ones(len(train)), train[columns]])
		beta = np.linalg.lstsq(x, train["return"], rcond=None)[0]
		pred = np.column_stack([np.ones(len(test)), test[columns]]) @ beta
		values[name] = float(np.mean((pred-test["return"])**2))
	return values
