# Delivery validation — 25 September 2026

- **34 unit tests passed** after the final module changes. Coverage includes independent fraction arithmetic, probability validation, future/missing timestamps, missing evidence, persistence/replay, failure budgets, modified routing rejection and simulated OpenRouter usage/error accounting.
- **Eight notebooks executed top to bottom**, with saved outputs and no cell errors or stderr in the final pass. Each has a rendered HTML reading copy.
- **All eight HTML previews loaded in an isolated browser**, with outbound web requests blocked. Checks found no missing figures, page overflow or stderr outputs. Representative full-page screenshots and all six notebook plots were visually inspected across the review passes. Long code wraps in the final HTML exports.
- **73 local documentation/HTML links resolved.** Notebook structures validate. The final offline results and package code match recorded provenance.
- **Twelve public releases acquired and twelve headline fields extracted.** Source hashes match acquisition records; values were checked against separately read source passages. This verifies this bounded extraction, not all financial tables or historical availability.
- **Original guide copy matches its recorded SHA-256.** The source guide and existing quant-research-agent project were not edited.
- **Dependency consistency check passed.** Exact installed versions are saved in requirements-tested.txt.
- **No model completions, paid API calls, deployment or trading occurred.** OpenRouter catalogue retrieval was an unauthenticated metadata request; adapter tests used synthetic responses.

The initial notebook run exposed sandbox-specific kernel-cleanup warnings. The executor now uses local IPC and stops only its own completed kernel, avoiding unrelated process inspection. The final rerun was clean. The original synthetic run also exposed an unnecessary feature-scale change; that run is retained, with the correction documented in the experiment ledger.

These checks establish code/artifact behavior. They do not establish live-provider compatibility, live-agent quality, RRSI transfer, financial alpha or learner mastery.
