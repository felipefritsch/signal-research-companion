# Decisions: Jev / System One

[Start](../../START_HERE.md) · [Roadmap](../ROADMAP.md) · [Sources](../SOURCES.md)

**Objective:** Convert uncertain classifications into explicit actions without confusing schema validity with correctness.

**Prerequisites:** Stage 1; conditional probability and expected loss.

**Main reading:** TypeSafe Introduction: primitives and atomic questions.

**Optional supplement:** Original guide §§2.1–2.4.

**Mode:** DEEP STUDY + TARGETED LAB. **Estimated effort:** 4 hours across several sittings, not one required sitting.

## Revision and worked example

Prediction reports uncertainty; a decision attaches consequences. If a wrong automatic route costs 20 units and perfect review costs 1, accepting the best route has loss `20(1 − p)`. Review is preferable unless `p > 0.95`; the implementation reviews on equality.

The four routes are documents, data, both and clarify. Review is an application action, separate from the clarify label. Change the losses if missing a data lookup is more costly than an unnecessary lookup; the symmetric-cost helper is only a first example.

The notebook contains four invented probability distributions, including a confident wrong answer. A valid schema cannot prevent it. Multiclass Brier score sums squared errors across classes; it measures probabilistic accuracy, not calibration alone. Four invented cases support arithmetic practice, not reliability claims.

TypeSafe's primitives supply bounded probabilistic judgments. Product-specific confidence fields must not be silently treated as correctness probabilities. Read the vendor documentation before replacing fixtures with Jev calls.

## Connect it to the shared project

This module supplies a decision interface; it does not write the final research report. The same interface can be tested with rules, a conventional classifier, Jev or a structured-output LLM. OpenRouter broadens the latter comparison, but does not imply Jev is served there. Connect to original guide §2 and Stage 5's asymmetric costs of invalid research.

## Practical work

Open [notebook 02](../../notebooks/02-decisions.ipynb). Its code is a worked starting point. Extend only the part we are currently studying; later lesson detail is developed together.

**Guided exercise:** Change review cost and draw the accept/review boundary; inspect a confidently wrong fixture.

**Completion evidence:** Derive the review threshold and explain what calibration evidence is missing.

**Low-energy route:** read the worked example, inspect its output and leave the exercise for later. No quiz is required and no mastery update occurs automatically.

**Next-session expansion:** record the concrete question or confusing step in the learning record. The full lesson is expanded when we reach this module, rather than assigning every related topic now.
