# Quant research validity

[Start](../../START_HERE.md) · [Roadmap](../ROADMAP.md) · [Sources](../SOURCES.md)

**Objective:** Separate extraction quality, predictive evidence and implementable incremental value.

**Prerequisites:** Stages 1–4; linear regression and return arithmetic.

**Main reading:** Existing Factor Evaluation Guide: four questions and original nuance.

**Optional supplement:** Baker PDF pp. 9–10; original guide §5.2.

**Mode:** DEEP STUDY + TRANSFER. **Estimated effort:** 6 hours across several sittings, not one required sitting.

## Revision and worked example

The synthetic panel is generated with `return = 0.004 × useful + common_shock + noise`. A redundant column is exactly twice the useful predictor. A spurious column tracks returns only in the development half. A leaked column equals the outcome. Their meanings are known because we built the generator.

Fit coefficients only on earlier observations. A chronological test exposes the spurious relationship's failure, but the leaked outcome still looks excellent. This is the crucial lesson: temporal splitting cannot repair an invalid feature. Availability metadata and feature lineage must be checked too.

The shared factor framework asks four questions: economic rationale, prediction, implementation and additivity. The synthetic experiment establishes arithmetic and failure mechanisms. It cannot establish an economic rationale, real costs, capacity or a profitable factor.

A duplicate predictor should not improve a least-squares forecast conditional on its original. The notebook checks this. Later financial analysis needs dependence-aware uncertainty, overlapping-label controls, candidate-on-incumbent and reverse comparisons, exposures and cost stress. No t-statistic from independent-row assumptions is reported here.

See the [Baker bridge](../BAKER_BRIDGE.md) for the separate pretrained-weight contamination problem.

## Connect it to the shared project

An LLM-generated label can be faithful to a document yet useless for returns. A predictor can forecast returns but fail after cost or add nothing to an incumbent. Keep these claims separate. The financial evaluation loop and the agent-task evaluation loop use different outcomes. Original guide §§5.2 and 7 anchors the distinction.

## Practical work

Open [notebook 05](../../notebooks/05-quant-validity.ipynb). Its code is a worked starting point. Extend only the part we are currently studying; later lesson detail is developed together.

**Guided exercise:** Compare useful, duplicate, spurious and future-leaking predictors; recalculate the executable return.

**Completion evidence:** Identify four leakage/selection channels and describe what each financial gate would need.

**Low-energy route:** read the worked example, inspect its output and leave the exercise for later. No quiz is required and no mastery update occurs automatically.

**Next-session expansion:** record the concrete question or confusing step in the learning record. The full lesson is expanded when we reach this module, rather than assigning every related topic now.
