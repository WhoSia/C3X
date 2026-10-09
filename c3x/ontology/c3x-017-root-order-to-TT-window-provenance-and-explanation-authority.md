# C3X 0.17 — Root Search Divergence & Explanation Evidence Court

**2026-10-10 — new intervention/observability object, within C3X 0.17.** No version increment for an implementation of the same primitive question. Preserve original legacy C3X016-P4 source and its SHA, native #37948775813 SUCCESS and 12 frozen positions.

## Empirical input already confirmed
SF16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`. 12 independent Lichess source-position FENs, three each geometry opportunities SKewer, interference, defender-removal, and source-negative. Source-legal candidate moved to initial root front (F) vs unchanged (O) vs impossible no-contact (Z); actual 72 patched +12 original searches. **All 12 moved; 2 final bestmove changed, 8 score/bound changed, 11 nodes changed, 10 PV changed**. The move changes were source cases #6 (interference ray, `c3a4→e4d6`) and #8 (defender-removal ray, `e6h3→h5g7`). These are root-order effects, NOT proof of learned tactics.

## Next reverse-engineering warrant
Instead of comparing only final search metrics, instrument Stockfish's two original source regions:
1. `Thread::search` iterative aspiration loop, BEFORE and AFTER `search<Root>`, and AFTER stable sorting: rootDepth; trial sequence; alpha and beta input; bestValue; front candidate; candidate root scores; fail-high/fail-low/exact window class.
2. `search` rootNode per-move consumer, AFTER value has returned from its child and AFTER updating `rm.score`: rootDepth, concrete candidate native Move, moveCount, returned child value, search alpha/beta, previously stored and subsequently stored root score, PV flag, node count.

Record **first changed aligned event** under O versus F for source #6/#8 plus two unchanged cases chosen by historical input ID rather than after observing the next trial. Distinguish `F_order` (known introduced manipulation) from `F_child_return`, `F_candidate_store`, `F_aspiration_window`, `F_TT_writer` and `F_TT_reader`; do not infer TT from alpha/beta or UCI score alone. Unmatched event sequences require an `ALIGNMENT_AMBIGUOUS` label. A first recorded difference is neither the first physical divergence nor a natural but-for mediator until independently manipulated.

**Observer technical gate:** same SF16 commit/compiler, thread1 hash16 NNUE-off, fixed depth12; both arms and Z; 2 cold repeats, original binary baseline. Passive observer must preserve original P4 complete final tuple (bestmove, score value/kind/bound, nodes, root PV) for each world. Censor over budget explicitly. Any different original O/Z result → FAIL_OBSERVER_NONINTERFERENCE. Never silently shrink to only positive worlds: all 12 inherited positions are frozen, two-move-change cases are descriptive focus only.

## Engine → explanation-service authority ladder

A finished explanation is an **evidence-labeled typed record**:
- `BOARD_LEGAL`: proved legal move and opponent legal reply.
- `TACTIC_CANDIDATE`: falsifiable ray/defender/mobility proposal (NOT a winning combination).
- `TACTIC_FORCING_CERTIFIED`: explicit finite line and every relevant opposing legal counterresponse audited under specified horizon; NOT certified by a single engine PV.
- `OPERATOR_CONTACT`: instrumented SEE/qsearch/TT/ordering/alpha-beta site actually executed.
- `SOURCE_CAUSAL`: preregistered exact one-site intervention with matching baseline/sham, effect and failure cases.
- `ENGINE_SUPPORTED_MOVE`: SF16 root recommendation with exact depth/hardware/search policy; engines can err.
- `LONG_PLAN_HYPOTHESIS`: pawn structure/king activity/space etc. plus alternative plans/horizon; no proof from a one-ply motif.
- `ABSTAIN`: unsupported "brilliant", "only move", "forced mate", "understood skewer", "TT caused choice".

Enforce precedence: a reason for the final selected move is NOT the same as a software cause of choosing that move. A move can be an excellent tactic regardless of whether a root-order experiment flips a finite-depth Stockfish evaluation; a source effect can occur without a human motif. Give separate human-facing sections: **What the move does** / **What replies must be considered** / **What the engine actually searched** / **What the counterfactual intervention changed** / **What is not established**.

## Puzzle and brilliant move expansion

Use source-licensed Lichess puzzle positions or authored puzzle examples only after explicit source SHA/license audit; keep original game source and puzzle composer annotations independent. Include tactical classes pins, skewers, interference, deflection, removal of defender, discovered attacks, zugzwang, sacrifices, mating nets and quiet only-move defense; separately positional concepts pawn majority, passed pawn and king safety. Define "brilliant" as editorial candidate requiring *opportunity cost and concrete losing alternatives*, not an absolute engine truth. Require a counterdefense court before persuasive prose. Include negative instances that look dramatic but fail against a legal defense.

## Result ceilings at opening
The existing 0.17 12-position native root-order study is PASS; the **new detailed trace and a puzzle-to-source causal explanation service remain unvalidated** until implementation and independent tests. Retain earlier 0.15 C1 overall-accuracy FAIL (42/64 vs no-change 53/64) and 0.16 natural TT physical link scope; do not claim natural TT mediation or learned NNUE concepts.
