# Optional lab — model choice and efficiency through OpenRouter

**Objective:** choose a model for a specific job using quality, reliability, latency and total cost. **Prerequisite:** Stages 2–4. **Mode:** TARGETED LAB. **Effort:** 1–3 hours offline; bounded live work fits within the optional six-hour allowance.

**Main reading:** [OpenRouter API](https://openrouter.ai/docs/api/reference/overview). **Supplement:** [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection). Read the [Mercury paper](https://arxiv.org/abs/2506.17298) only for the diffusion mechanism branch.

OpenRouter gives us a common calling interface for different models and providers. It does not guarantee lower cost than calling a provider directly. The relevant comparison is cost per valid task at acceptable quality and latency, including failures, reviews and retries.

## Connect models to roles

| Role | Required behavior | Main measures |
|---|---|---|
| Router | Valid route or explicit review; avoid costly mistakes | Expected decision loss, invalid-output rate, latency |
| Extractor | Exact source-supported fields and evidence IDs | Exact match, coverage, unsupported-claim rate |
| Investigator | Find cross-document evidence within a budget | Task completion, evidence recall, total calls and cost |
| Critic | Identify real defects without inventing them | Defect recall, false alarms, cost per useful review |
| Synthesizer | Preserve supported claims and uncertainty | Citation support, completeness, total task cost |

A cheap router plus stronger exception handler is a hypothesis to test against a single-model baseline. A more expensive model may be cheaper overall if it avoids extra investigation and review. Keep a homogeneous baseline before trying mixed-model orchestration.

## Diffusion versus autoregressive generation

An autoregressive model emits a sequence token by token. A diffusion language model iteratively refines a token sequence, potentially updating multiple positions at once. That mechanism can change latency and throughput, but does not determine research correctness.

The saved catalogue lists `inception/mercury-2.5` and `inception/mercury-2` on the verification date. They are **candidates**, not selected defaults or measured winners. Confirm model and provider availability immediately before any live run. Vendor speed claims are not copied into this project's results. Tool use and structured output support must be checked per model/provider.

## Compare fairly

Freeze task text, source material, output limits, validators and model settings. Pin provider routing and disable fallback for controlled trials. Start with three repeats per task/model, treating them as exploratory rather than enough for stable tail estimates. Randomize/interleave model order and record prompt/corpus hashes, provider, returned model ID, reasoning settings, caching and usage.

Report quality and failures before cost rankings. Record end-to-end latency and total input/output/reasoning/cache tokens where returned. Tokens per second are not perfectly comparable across tokenizers. This first adapter is non-streaming: it measures completion latency, **not time to first token**. Do not claim diffusion speed from a token-price calculation.

For `valid_tasks > 0`, `cost_per_valid_task = all_recorded_cost / valid_tasks`; otherwise it is undefined. Show unsupported capabilities as unavailable, not zeros. Keep RRSI comparisons on the same backbone first; changing both the model and harness obscures attribution.

## What is ready

- A saved public model catalogue with timestamp and current advertised price metadata.
- A non-streaming client with explicit model/provider, token cap, no fallback, no automatic retries, provider price ceilings, local spending reservations and usage logging.
- Simulated-response tests for successful calls, missing usage, errors, disabled live mode and exhausted budgets.
- [Offline notebook](../notebooks/08-model-efficiency.ipynb) with cost arithmetic, catalogue inspection and request construction only.

The `max_price` fields use dollars per million prompt/completion tokens; catalogue pricing is dollars per token. The notebook performs that conversion explicitly.

## Before live calls

Choose the tasks, specific model/provider pairs and a total budget with Felipe. Use a dedicated capped OpenRouter key, supply it only in `OPENROUTER_API_KEY`, and keep paid calls out of automatic notebook execution. A local reservation is **not** a hard provider-side billing guarantee: costs can be missing or exceed estimates. Missing/ambiguous costs halt subsequent calls until reconciled; reservations are never silently released after a timeout.

The default config has `live_enabled: false` and no approved budget. No live benchmark runner is enabled. The callable adapter is ready for a deliberately reviewed small batch; catalogue GET requests require no key and do not generate completions.

**Checkpoint, optional:** explain why a model that costs twice as much per token might cost less per valid completed investigation. Low-energy mode: inspect the worked table only.
