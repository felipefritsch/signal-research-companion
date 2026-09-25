"""Small shared contracts and a persistent, deterministic teaching harness."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Callable


def digest(value) -> str:
	return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class ResearchTask:
	id: str
	question: str
	evidence_ids: tuple[str, ...]
	mode: str = "synthetic"


@dataclass(frozen=True)
class EvidenceRecord:
	id: str
	source: str
	text: str
	available_at: str
	version: str = "v1"


@dataclass(frozen=True)
class ExperimentSpec:
	id: str
	hypothesis: str
	variant: str
	seed: int = 7
	purpose: str = "diagnostic"
	data_version: str = "synthetic-v1"


@dataclass
class RunResult:
	id: str
	status: str
	metrics: dict
	evidence_ids: list[str]
	unresolved: list[str]
	resources: dict
	versions: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CandidateChange:
	id: str
	hypothesis: str
	edits: tuple[str, ...]
	complexity: int
	benchmark_specific: bool = False


class BudgetExceeded(RuntimeError):
	pass


class Harness:
	"""Local serial tool runner. It is not an arbitrary-code security sandbox.

	Only pre-registered deterministic tools are supported. Completed steps are
	replayed by identity; failed steps may be retried explicitly with resume=True.
	A crash during a tool produces an interrupted step; rerunning that step is
	safe only for idempotent tools. We make no exactly-once side-effect claim.
	"""

	def __init__(self, path: Path, run_id: str, max_calls: int = 4):
		if max_calls < 1:
			raise ValueError("max_calls must be positive")
		self.db = sqlite3.connect(path)
		self.run_id = run_id
		self.max_calls = max_calls
		self.tools: dict[str, Callable] = {}
		self.db.executescript("""
		CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, max_calls INTEGER);
		CREATE TABLE IF NOT EXISTS steps (
		 run TEXT, step TEXT, tool TEXT, input_hash TEXT, status TEXT, output TEXT,
		 PRIMARY KEY(run, step));
		CREATE TABLE IF NOT EXISTS events (
		 run TEXT, step TEXT, status TEXT, at TEXT);
		""")
		row = self.db.execute("SELECT max_calls FROM runs WHERE id=?", (run_id,)).fetchone()
		if row and row[0] != max_calls:
			raise ValueError("Cannot change a persisted run's call budget")
		self.db.execute("INSERT OR IGNORE INTO runs VALUES (?,?)", (run_id, max_calls))
		self.db.commit()

	def register(self, name: str, function: Callable):
		self.tools[name] = function

	def _event(self, step, status):
		self.db.execute("INSERT INTO events VALUES (?,?,?,?)", (
			self.run_id, step, status, datetime.now(timezone.utc).isoformat()))

	def step(self, step_id: str, tool: str, arguments: dict, *, resume=False):
		if tool not in self.tools:
			raise ValueError("Tool is not registered")
		key = digest(arguments)
		row = self.db.execute("SELECT tool,input_hash,status,output FROM steps WHERE run=? AND step=?",
			(self.run_id, step_id)).fetchone()
		if row:
			if (row[0], row[1]) != (tool, key):
				raise ValueError("Step identity reused with different inputs")
			if row[2] == "completed":
				return json.loads(row[3])
			if not resume:
				raise RuntimeError("Step failed or was interrupted; explicit resume required")
		count = self.db.execute("SELECT COUNT(*) FROM events WHERE run=? AND status='started'",
			(self.run_id,)).fetchone()[0]
		if count >= self.max_calls:
			raise BudgetExceeded("Whole-run call budget exhausted, including failures")
		self.db.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,?)",
			(self.run_id, step_id, tool, key, "started", None))
		self._event(step_id, "started")
		self.db.commit()
		try:
			result = self.tools[tool](**arguments)
			encoded = json.dumps(result, allow_nan=False)
		except Exception:
			self.db.execute("UPDATE steps SET status='failed' WHERE run=? AND step=?", (self.run_id, step_id))
			self._event(step_id, "failed")
			self.db.commit()
			raise
		self.db.execute("UPDATE steps SET status='completed',output=? WHERE run=? AND step=?",
			(encoded, self.run_id, step_id))
		self._event(step_id, "completed")
		self.db.commit()
		return result

	def close(self):
		self.db.close()
