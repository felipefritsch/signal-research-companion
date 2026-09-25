"""Explicit, non-streaming OpenRouter calls with a persistent reservation ledger.

No key discovery, retries, provider fallback or calls during import. A local
reservation is an accounting guard, NOT a provider-enforced billing ceiling.
Use a dedicated provider-side capped key as well before live experiments.
"""

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sqlite3
import time
import urllib.request
import uuid

from .core import digest

API = "https://openrouter.ai/api/v1"


def http_json(url, payload=None, key=None):
	headers = {"Content-Type": "application/json"}
	if key:
		headers["Authorization"] = "Bearer " + key
	request = urllib.request.Request(url, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
	try:
		with urllib.request.urlopen(request, timeout=60) as response:
			return json.load(response)
	except Exception:
		# Do not echo provider response bodies, headers or prompts on failure.
		raise RuntimeError("Provider request failed; no automatic retry. Reconcile billing before retrying.") from None


def catalogue():
	"""Public unauthenticated metadata request; never invoked automatically."""
	return {"retrieved_at": datetime.now(timezone.utc).isoformat(), "source": API + "/models",
		"data": http_json(API + "/models")["data"]}


def request_payload(model, prompt, provider, max_tokens=256, temperature=0.0,
		prompt_price_per_million=1.0, completion_price_per_million=2.0):
	if not model or model.startswith("openrouter/"):
		raise ValueError("Use an explicit model ID; automatic model routing is excluded from controlled trials")
	if not provider or not prompt or not isinstance(max_tokens, int) or max_tokens < 1:
		raise ValueError("Explicit provider, nonempty prompt and positive token limit required")
	for value in (temperature, prompt_price_per_million, completion_price_per_million):
		if not math.isfinite(value) or value < 0:
			raise ValueError("Settings must be finite and nonnegative")
	return {"model": model, "messages": [{"role": "user", "content": prompt}],
		"stream": False, "max_tokens": max_tokens, "temperature": temperature,
		"provider": {"only": [provider], "allow_fallbacks": False, "require_parameters": True,
			"data_collection": "deny", "max_price": {"prompt": prompt_price_per_million,
				"completion": completion_price_per_million, "request": 0}}}


class OpenRouterClient:
	def __init__(self, ledger: Path, budget_usd: float, *, live_enabled=False, transport=http_json):
		if not math.isfinite(budget_usd) or budget_usd <= 0:
			raise ValueError("A positive approved budget is required")
		self.live_enabled, self.transport = live_enabled, transport
		self.db = sqlite3.connect(ledger, timeout=10)
		self.db.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, amount REAL)")
		self.db.execute("""CREATE TABLE IF NOT EXISTS calls (
		 id TEXT PRIMARY KEY, reservation REAL, charged REAL, status TEXT, metadata TEXT)""")
		row = self.db.execute("SELECT amount FROM budget WHERE id=1").fetchone()
		if row and not math.isclose(row[0], budget_usd):
			raise ValueError("Existing ledger has a different budget; do not silently reset it")
		self.db.execute("INSERT OR IGNORE INTO budget VALUES (1,?)", (budget_usd,))
		self.db.commit()
		self.budget = budget_usd

	def complete(self, payload, *, reservation_usd, role, task_id):
		if not self.live_enabled:
			raise PermissionError("Live calls disabled. Agree a budget and select models first.")
		provider = payload.get("provider", {})
		if (payload.get("stream") is not False or len(provider.get("only", [])) != 1
			or provider.get("allow_fallbacks") is not False
			or provider.get("require_parameters") is not True
			or not isinstance(payload.get("max_tokens"), int) or payload["max_tokens"] < 1
			or not payload.get("model") or payload["model"].startswith("openrouter/")):
			raise ValueError("Controlled calls require a fixed model/provider, token cap and no fallback")
		prices = provider.get("max_price", {})
		if set(prices) != {"prompt", "completion", "request"} or any(
			not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in prices.values()):
			raise ValueError("Explicit finite provider price ceilings required")
		if not math.isfinite(reservation_usd) or reservation_usd <= 0:
			raise ValueError("Positive per-call reservation required")
		key = os.environ.get("OPENROUTER_API_KEY")
		if not key:
			raise RuntimeError("Set OPENROUTER_API_KEY explicitly in the process environment")
		call_id = str(uuid.uuid4())
		meta = {"task_id": task_id, "role": role, "requested_model": payload["model"],
			"request_hash": digest(payload), "started_at": datetime.now(timezone.utc).isoformat()}
		self.db.execute("BEGIN IMMEDIATE")
		try:
			# Ambiguous errors/missing cost block further spending until separately reconciled.
			pending = self.db.execute("SELECT COUNT(*) FROM calls WHERE status != 'accounted'").fetchone()[0]
			spent = self.db.execute("SELECT COALESCE(SUM(charged),0) FROM calls").fetchone()[0]
			if pending or spent + reservation_usd > self.budget:
				raise RuntimeError("Unreconciled call or insufficient remaining budget")
			self.db.execute("INSERT INTO calls VALUES (?,?,?,?,?)", (call_id,reservation_usd,None,"reserved",json.dumps(meta)))
			self.db.commit()
		except Exception:
			self.db.rollback()
			raise
		started = time.monotonic()
		try:
			response = self.transport(API + "/chat/completions", payload, key)
			if "error" in response:
				raise RuntimeError("Provider returned an error")
			usage = response.get("usage", {})
			cost = usage.get("cost")
			valid_cost = isinstance(cost, (int, float)) and math.isfinite(cost) and cost >= 0
			meta.update({"elapsed_seconds": time.monotonic()-started, "response_id": response.get("id"),
				"returned_model": response.get("model"), "provider": response.get("provider"),
				"usage": usage, "finish_reason": response["choices"][0].get("finish_reason")})
			text = response["choices"][0]["message"]["content"]
			if not isinstance(text, str):
				raise RuntimeError("Expected text response")
			status = "accounted" if valid_cost and cost <= reservation_usd else "needs_reconciliation"
			self.db.execute("UPDATE calls SET charged=?,status=?,metadata=? WHERE id=?",
				(cost if valid_cost else None, status, json.dumps(meta), call_id))
			self.db.commit()
			if status != "accounted":
				raise RuntimeError("Missing cost or reservation exceeded; reconcile billing before further calls")
			return {"text": text, "metadata": meta}
		except Exception:
			self.db.execute("UPDATE calls SET status='needs_reconciliation' WHERE id=? AND status='reserved'", (call_id,))
			self.db.commit()
			raise RuntimeError("Call failed or needs billing reconciliation; no automatic retry") from None

	def close(self):
		self.db.close()
