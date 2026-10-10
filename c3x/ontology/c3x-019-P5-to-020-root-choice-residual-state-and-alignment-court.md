# C3X 0.19 P5 → 0.20 Flowing — Root-Choice Residual-State and Semantic Alignment Court

**Status:** DESIGN / ADVERSARIAL AUDIT. C3X 0.19 stays ACTIVE; C3X 0.20 is FORMAL NAME PROPOSAL ONLY. 2026-10-10.

## Frozen facts (do not reinterpret CI success as K4 success)
- Native original Stockfish16 court: https://github.com/WhoSia/C3X/actions/runs/38031332649
- Source receipt: `c3x/receipts/c3x-019-feb-four-single-return-restoration-root-choice-null-and-beta-rescue-20261010.json`.
- Frozen February adaptive cases 3 STRICT, 6 STRICT, 7 BROAD, 10 STRICT. Each has ONE synthetic root child-return edit after completed child search / undo, before root score updates. **K1,K2,K3,K5,K6,K7 PASS; K4 FAIL (0/4)**.
- F / FIRST / REPAIR bestmove: 3 a1c1 / e1e3 / e1e3; 6 g2g4 / e3d2 / e3d2; 7 g8e7 / e8f7 / e8f7; 10 d8b8 / b7a6 / b7a6.
- #6 return 114→103 restores local depth10 beta boundary and trial exit (beta 114); final choice still FIRST. 117111→138901 nodes; cp35→36.
- Prior independent February F19.5 FAIL; January J2/J3/J4 FAIL; original unbounded P1 R5 FAIL. Four P4 cases were post-outcome selected. No transport/generalization claims.

## Observation versus intervention
Let `S_d=(TT_d,rootMoves_d,PV_d,history_d,window_d,searchHeuristics_d,...) ` denote the generally *unobserved* full search state at a depth-d boundary. An emitted log `O_d=h(S_d)` is only a projection. Equality of event counters, root-call IDs, move IDs, score, and even a full UCI line does not entail state equality.

For a single root child-return `C` with F reference value `c_F`, the supported result is:
`do(C:=c_F)` within V-first history, with earlier native child-search effects intact, did not restore F bestmove in 4 selected positions. This is **NOT** a full state intervention `do(S:=S_F)`, and does not identify a unique TT→candidate→root mediated effect.

## Audit 1 — first observed difference versus first causal difference
The existing `c3x_019_February_semantic_root_prefix_audit.py` compares logs after ignoring observer counters. Its `candidate_identity` includes `root_call`, `trial`, `index`, `move`, `alpha`, `beta`, `before`: useful exact pre-divergence contact guard, NOT proof of state equivalence after intervention. `first_semantic_divergence` uses a positional zip and returns None when one trace is a strict prefix of the other; therefore **absence of a reported mismatch cannot certify equal complete traces**. Fail closed on length mismatch.

The `root_leader_milestone_ladder` uses per-depth final `after_sort`, which can label an outcome for two distinct aspiration-trial histories. First child-return / terminal value / terminal leader depth observations:
- game3: 4 / 4 / 4
- game6: 10 / 10 / 11
- game7: 4 / 8 / 11
- game10: 4 / 5 / 6
These are **descriptive milestones**, not latencies of uniquely identified causal propagation.

## 0.20-A prospective *analysis* protocol (four already observed cases; exploratory)
1. Preserve frozen F/FIRST/REPAIR/OBS/SHAM records, immutable source source-hashes and complete denominator. No re-selecting cases from successes.
2. Read first actual return-contact witness; compare FIRST to REPAIR and independently compare both to F. Keep the comparison in native source stages: post-child value, root candidate score/averageScore/PV, depth trial window exit, per-depth last after_sort, next-depth root candidate order, final UCI.
3. Within each arm, order by actual event stream and depth; across arms, align only on stable move/position and semantically admissible source stage with a common *proven* prehistory. Split comparable prefixes at first nontrivial semantic difference. After split, mark `PATH_DIVERGED`, not `MATCHED_CAUSAL_STATE`, even if root-call counters coincide.
4. Define classifications `LOCAL_ONLY`, `BOUNDARY_RECOVERED`, `LEADER_RECOVERED`, `FINAL_RECOVERED`, `NONCONTACT`, `AMBIGUOUS_OR_CENSORED`. An earlier category cannot silently imply any later category.
5. For game6 specifically, report the depth10 repaired trial and earliest later **observed** divergence between REPAIR and F; keep search-effort, TT writes already issued and prior rootMove history as rival causes, not established causes.

## 0.20-B bounded *future* factorial (no results claimed)
Precommit treatment arms for all four frozen games independent of outcomes: V FIRST; observed-only; sham; single return repair; return + one pre-specified rootMove persistent score/averageScore repair; return + one pre-specified window/retry repair; and appropriate joint arm only if the source edit is meaningfully well-defined. Every arm has cold duplicate, exact source contact, source diff, UCI checks, failure on missing contact / malformed state / ambiguous source anchor. No magical resetting of TT, search histories, child subtree, PV or ordering without explicit separate intervention and provenance. **Primary endpoint** categorical final F bestmove return; secondaries local candidate/alpha-beta/root lead restoration, all reported separately. Do not use February four to claim independent generalization.

## 0.20-C / D / E scientific gates
C: identify a competing non-target move that overtakes a prior leader, matching legal position and depth-stage without assuming equal root-call IDs. Include negative explanations (candidate already ahead, score was alpha-screened, no real contact, path truncation).
D: only after the causal selection rule is fixed, select a disjoint new cohort from PGN with an engine-free selector, freeze SHA before engine inspection, pre-register alpha/beta crossing and leader-change prediction plus an allowed FAIL.
E: source-map another engine by actual root search, TT value/cutoff and aspiration semantics; matching names or numerical evaluations do not establish equivalent interventions.

## CI, attribution and stop
Use local source tests and existing frozen native artifacts first; ONE consolidated read-only Actions experiment only once specified falsifiers and independent negative controls are ready. Do not rewrite README ACTIVE version or flip 0.20 to ACTIVE without explicit user approval. GitHub commits WhoSia-only, main only, no Actions auto-push. If measured modifications only affect log serialization/observer timing or give post-hoc targeted successes without root-competition predictions, STOP and report the limitation.
