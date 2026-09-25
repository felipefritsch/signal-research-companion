# Baker, autoresearch and the quant research harness

Source: Matt Robinson's interview with Lucas Baker, supplied PDF, especially pp. 5–10 and 11–12. The prior task “Analyze AI agents for signal work” was recovered and its distinctions preserved. This is interpretation and a proposed learning architecture, not documentation of Jump Trading's internal system.

| Discussion theme | Study implication | Lab component |
|---|---|---|
| Bounded autoresearch and reward hacking | The optimized score must retain its intended meaning | Protected numerical/evaluation rules |
| Fewer better ideas and adversarial critique | Spend effort on mechanism and falsifiers before search | Hypothesis and critique fields |
| Organized fleets | Roles, messages and stopping rules matter | Serial proposer/reviewer design before scaling |
| Model-building versus direct LLM signals | Model weights can enter the historical information set | Contamination case and prospective design |
| Infrastructure and integration | A benchmark gain must survive real workflow constraints | Costs, failure handling and evidence records |

## Four distinct failures in a headline signal

1. **Document leakage:** revised text or a later transcript is treated as available earlier.
2. **Model contamination:** a later-trained LLM recognizes the event or its outcome, despite historically bounded input text.
3. **Execution timing:** credited price movement occurred before the permitted entry.
4. **Research selection:** many prompts, features or universes were tried and only the winner reported.

The interview describes headlines and next-day stock returns; earnings are our worked application, not an exact quotation of the interview question.

```text
original release → feed receipt → model processing → order entry → outcome
       each timestamp and version must support the claimed trade
model training / updates → may already contain later event information
```

An “as of” prompt does not erase weights. Disabling browsing closes one channel only. Identifier masking is a sensitivity check, not proof of cleanliness. Stronger designs freeze the full pipeline and make timestamped predictions before outcomes occur, or use appropriately documented historical model vintages. A small newer sample may be cleaner but statistically weak.

Apply the factor outline after these validity checks: economic mechanism → predictive evidence → implementability → additivity. Costs, common shocks, issuer repetition, overlapping returns and selection history all affect interpretation. A plausible causal story does not rescue corrupted data.

## Bound the future live experiment

The proposer sees development cases and a narrow editable surface. A critic identifies benchmark-specific rules and unsupported mechanisms. A deterministic evaluator performs time/units/return checks. A researcher reviews the dossier. For any future parallel agents, compare against the same serial baseline and count coordination costs; agreement between agents is not independent ground truth.
