# C3X 0.13 P8 — EP10 Outcome-Blind Single TT Cutoff-Occurrence Precommit

**Authored before actual EP10 engine outcomes.** Status: APPROVED_FOR_DEVELOPMENT_ONLY. No C3X 0.14 creation/name, no strategic concept causal authority.

## Scientific object

A fixed original historical CECLUB Primera Division Linares 2026 source game, frozen by earlier C3X 0.13 P7-R1/R2, full root FEN `2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17`. White legal pair `f3f4` vs `g3g4`, actual prior depth8 signed preference gap +29cp before TT masking. This pair was used to discover the coarse MAIN-path family effect in EP9 and is **not** independent confirmation.

Build official Stockfish sf_16 release pin, apply prior P8-EP9 source-level observer to `src/search.cpp`. Independently compile an unmodified EP9 observer and its EP10 successor. EP10 is not a clean stockfish-to-new comparison; it is **EP9 OFF to EP10 NONE observer equivalence**, isolating the *incremental* event selector from the previously verified clean-SF16 to EP9 OFF comparison.

The only intervention is suppressing **one** otherwise eligible TT bound early return in native C++ main search or quiescence search. Site + one-based chronological ordinal within a cold deterministic search is the locator; this is an **execution occurrence**, not a board-invariant TT key. No raw TT key or private search address is exported. All other TT uses, stores, move ordering and board legality survive. If a selected cutoff occurs, the engine continues search from that point, so descendant search paths can diverge.

## Frozen, outcome-independent experiment grid

- Exact `go depth 8` and `go depth 12` with `MultiPV=2` and `searchmoves f3f4 g3g4`, Threads=1, Hash=16 MiB, fully restarted engine process per arm, 2 cold repeats for each depth.
- Baseline EP9 binary OFF vs EP10 binary NONE; require **exact** bestmove, both candidate cp/mate score types, final PV and nodes. If observer mismatch, **entire event-claim court invalid**; preserve failure.
- Negative controls: impossible ordinal `1,000,000,000` separately at sites MAIN and QSEARCH, require zero blocked cutoffs and exact semantic equality against EP10 NONE. Never treat a sentinel miss as an effect.
- Predeclared positive candidates: site MAIN or QSEARCH × 1-based ordinals `1,2,4,8,16,32,64,128`; no exploratory new locator selection after outcome. A selected event may be absent; report zero blocking and no-op honestly. For any selected event, require exactly one native bound early return suppressed.
- Primary outcome: first root choice between f3f4 and g3g4; secondary signed comparative White cp gap, both raw score kinds, PV, nodes, selected event's site/ordinal/ply/depth/alpha/beta/TT-bound-return value and eligibility counts. Do not compare mate with cp.
- Multiple comparisons: each ordinal constitutes a different intervention. Any observed reversal is discovery-set evidence, **not** replication or statistical significance; predeclare holdout independent legal pair/source/engine before validation. Repeats assess program determinism only; not extra chess examples.
- Technical threats: patch shifts search cost; depth matching is not node matching; search ordering and alpha-beta bounds feed back; the actual event is selected by executable chronology and not invariant to other budgets; qsearch and main effects may interact. Local event-level causal influence on reported bestmove does **not** prove strategic concept/individual TT datum mediation.

## Source and prior-art safeguards

Inherit G9.4 exact TT event/provenance work and G9.5 P13–P15 pair-boundary and board–search susceptibility findings. The new experiment is a Stockfish16 event-ordinal replications test, NOT first discovery of causal TT interventions. External methodological rivals include Zhang & Nanda, *Towards Best Practices of Activation Patching* (ICLR 2024); Geiger et al., *Causal Abstraction* (JMLR 2025); Martin et al., *Re-evaluating metamorphic testing of chess engines* (Information and Software Technology 2025, DOI 10.1016/j.infsof.2025.107679). External paper effects do not certify chess causation. The Martin et al. result warns search ordering, actual game sampling and depth can explain apparent transformed-position anomalies.

## Custody and claim authority

GitHub main commit by authenticated human WhoSia only. GitHub Actions read-only permissions `contents: read` and no git push, tag, commit or bot authorship; preserve patch, manifests, raw UCI receipts and cryptographic hashes as transient artifact, then explicit Drive archive. Notion same C3X Lab page, not separate Lab. Track B only receives verified observational or locally bounded technical diagnostics unless an independently validated causal explanation certificate exists. P8 OPEN / strategic concept HOLD; 0.14 remains unnamed/unopened.
