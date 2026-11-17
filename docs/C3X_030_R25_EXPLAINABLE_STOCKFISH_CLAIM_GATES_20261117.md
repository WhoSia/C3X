# C3X 0.30 R25 — Explainable Stockfish: evidence and plan identity gate

## Scientific question

If the same legal root move and displayed centipawn score (or even native root value) produce different principal variations, which elements of the explanation remain valid? R24 observed that the engine can display alternative continuations. This is **not**, by itself, evidence that the engine adopted different strategic plans, that a neural feature caused the change, or that either PV is objectively superior.

## Predeclared levels of evidence

1. **NATIVE_SEARCH_OBSERVATION:** a source-produced root score and recommendation with exact native provenance, complete attempt and in-window status. Preserve the engine build, NNUE, history, options, and reporting depth.
2. **LEGAL_VARIATION_OBSERVATION:** a SAN/UCI replay verified with chess rules. A fork is not a mere prefix extension; mark whose turn diverges and any observed transposition separately. A board fact (e.g. check or attacked piece) is not automatically a causal NNUE fact.
3. **INDEPENDENT_JUDGE_COMPARISON:** both first divergent moves scored from the **same divergence board**, from the diverging player's perspective, at every declared judge depth. A depth reversal requires reporting both results, not averaging them into certainty.
4. **C3X_CAUSAL_CONTRAST:** requires a specific physical intervention, matched sham, unchanged legal world, identified ancestor transmission, and a trace to the root. **Not conferred by levels 1–3.**
5. **PLAN_TRANSPORT:** requires a predeclared target predicate, opponent reply family, horizon, witness and falsifiers. A PV is an example line, not a guarantee against unseen defenses.
6. **HUMAN_UTILITY:** requires an independent learner task on unseen positions. A valid rule explanation alone cannot pass this gate.

The implementation must **abstain** from plan identity, mechanism attribution, or human effectiveness claims when it has only an observed fork. Scientific Track A and commentary Track B remain separated by [Two-Track Constitution](C3X_TWO_TRACK_CONSTITUTION.md) and [D1 decision](C3X_030_DECISION_D1_NATIVE_CAUSALITY_FIRST_20261111.md).

## First development cohort

Reuse only the **already exposed** R24 Spanish fork and TCEC S28 League 2 round 1.4 equal-native fork. A pure-Python contract validator must reject inconsistent roots, cp scores, bounds, incomplete producer evidence, truncated PVs, and mismatched side-to-move tags. It may summarize **already verified** independent Berserk depth results, but must not fabricate fresh engine scores or independently certify chess legality without a chess engine.

The result should be a machine-readable plan-evidence ledger, a Korean comparison that distinguishes verified observation from open causal claims, and a prospective trial template. Original independent blind cohorts remain untouched. A static analysis test PASS does not promote Track A.
