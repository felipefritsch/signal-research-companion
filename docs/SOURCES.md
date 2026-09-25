# Source map and reading decisions

Verification date: 25 September 2026. The original guide is a preserved user-supplied artifact, including its prior source assessments. This project rechecked selected primary pages and source passages; it does not claim to re-read every attachment or independently replicate the papers.

| ID | Primary source / selected reading | Purpose and verification scope |
|---|---|---|
| A | [Original guide](../references/Jev_RLM_Study_and_Implementation_Guide.md) | Full text read; unchanged copy with SHA-256 provenance |
| K | [Karpathy autoresearch](https://github.com/karpathy/autoresearch) — README “How it works”, “Design choices” | Bounded edit/run/evaluate loop; repository read, GPU experiment not run |
| J | [System One and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | Vendor product framing; not independent efficacy evidence |
| J1 | [TypeSafe Introduction](https://docs.typesafe.ai/introduction), [Confidence](https://docs.typesafe.ai/confidence) | Assign primitives, composed questions and confidence distinction; section mapping inherited from anchor, recheck before live adapter |
| R | [RLM v1](https://arxiv.org/html/2512.24601v1) — introduction, method, Table 1, limitations | Mechanism and ablations; fixed version for study |
| R1 | [Prime RLM article](https://www.primeintellect.ai/blog/rlm) | Supplement for implementation tradeoffs; anchor's reviewed source, not reread in full here |
| P | [Prime Agent](https://www.primeintellect.ai/blog/prime-agent) | Runtime and continual harness; launch page checked, package not installed |
| P1 | [Prime Agent repository](https://github.com/PrimeIntellect-ai/prime-agent) | Later implementation reference; no compatibility claim |
| E | [RRSI v1](https://arxiv.org/html/2609.24972v1) | Selected method/results context checked; no reproduction |
| E1 | [RRSI repository](https://github.com/google-research/rrsi) — method-to-code map | Compare paper mechanisms with our limited exercise |
| B | [Baker interview](https://www.ai-street.co/p/jump-tradings-lucas-baker-on-ai-agents) | Supplied local PDF used; pp. 5–7 and 9–10 text rechecked. Clipped line endings are not reconstructed as quotes |
| F | Existing local Factor Evaluation Guide | Four evaluation questions and nuanced additivity treatment re-read; no existing study rerun |
| O | [OpenRouter API](https://openrouter.ai/docs/api/reference/overview) | Unified chat request/response; adapter contract verified with mocks only |
| O1 | [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) | Provider pinning, supported parameters and price filters |
| O2 | [Usage accounting](https://openrouter.ai/docs/guides/administration/usage-accounting) | Token/cost logging; missing cost remains unknown |
| O3 | [Models](https://openrouter.ai/docs/guides/overview/models), [public catalogue](https://openrouter.ai/api/v1/models) | Unauthenticated catalogue snapshot saved; not an entitlement or availability guarantee |
| D | [Mercury paper](https://arxiv.org/abs/2506.17298), [Mercury model page](https://openrouter.ai/inception/mercury) | Optional diffusion reading; architecture/vendor claims, not measured lab speedups |
| U | [Public inventory](../data/public_inventory.json) | Twelve official quarterly releases, with dates and fiscal labels; current retrieval does not certify historical versions |

## Local continuity references

The private Baker PDF is at `/Users/felipefritsch/Documents/Recruiting 2026/Firm Mateiral/Jump Trading’s Lucas Baker on AI Agents - by Matt Robinson.pdf`.

The factor guide is `/Users/felipefritsch/Documents/dev/quant-research-agent/FACTOR_EVALUATION_GUIDE.md`. The existing project's charter and state were inspected only; neither was modified. The source interview does not authorize attribution of our proposed architecture to Jump Trading.

## Study selection

Study decision losses, information sets, context management, evaluation and research selection deeply. Learn APIs and persistence by bounded practice. Defer model training, full RRSI reproduction, production orchestration, live trading and large agent fleets. Use the original guide's Murphy reading only when the expected-loss derivation needs a refresher; its edition/page checks are inherited from that guide.

The original X link remains a discovery source with limited access, as documented in the anchor. It is not additional inspected evidence.
