# C3X 0.22-P2-R2 — Operator-Level Search-Memory Mediation & Exchange-Legality Counterfactuals

**2026-10-10 PRE-SEE INTERVENTION CONTRACT • Active C3X 0.22**

Formal paragraph name: **Operator-Level Search-Memory Mediation & Exchange-Legality Counterfactuals: Targeted Native SEE Witnesses, TT Score Assignment versus Cutoff, Source-Aligned Candidate Survival & Precommitted Multi-Ecology Bestmove Transfer**.

## Development data, causal treatment and constraints

Use the **already-exposed** TWIC1664 16 sources and C3X0.22-P2-R1 frozen full native StageA target selection, plus previously exposed TWIC1656/March/April cases for contrasting failure examples. All of these are **mechanistic development** and **not eligible as heldout prospective evidence** for any new model.

C++ source must be the exact Stockfish16 git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, same 0.16–0.22 source overlays; NNUE off, 1 thread, hash16 MB, depth12. The new R2 C++ patch must distinguish:
(1) actual `pos.see_ge(move, occupied, threshold)` and `pos.see_ge(move, threshold)` calls at **four genuine search.cpp callsites**: capture pruning, quiet pruning, qsearch futility and qsearch move pruning;
(2) *original returned Boolean* and threshold, candidate native move and exact root-call; native `pos.key()` identity where computable, and scope of source access;
(3) **OBS**, **FORCE_PASS** and **FORCE_FAIL** policies, called only on exact predeclared root-call and position-key; dynamic transformation of the operator Boolean only, no changes to the original chess game, legal move generation, search width/depth or original SEE implementation;
(4) FULL64 physical TT source `key/slot/epoch/first root-call`, original actual TT score-as-evaluation use versus a proven main or qsearch `return ttValue` cutoff separately;
(5) depth1..12 root leaders, final UCI, and first semantically aligned root candidate before source paths diverge.

## Specific experimental design and null checks

First execute passive SEE watch on development TWIC1664 game #2/#3/#6/#12/#13 with original O/F world and genuine first-reader TT target, per world and STRICT/BROAD source roles. Require **cold duplication** and `SEE-OBS` final six-field UCI equals precommitted untouched StageA baseline, exact source root-call/key and event existence; if there are no scoped `see_ge` calls in an originally value-used TT source window, classify `SEE_NO_CONTACT`, **not evidence SEE is absent or irrelevant globally**.

Only for **genuine scoped SEE-contact** do 2x2 source-specific interventions, randomized fixed order if feasible:
- TT unchanged + SEE original (00)
- TT FIRST reader blocked + SEE original (10)
- TT unchanged + operator SEE decision forced opposite original (01)
- TT FIRST reader blocked + SEE forced opposite original (11).
At the same watched physical source key/call and *first eligible SEE call only* to avoid unbounded intervention dose, force result to its opposite. Subsequent SEE uses are PASSIVE. Across cells, observe event contacts and actual result changed; not simple assertion that env var was set. Group by original chess game and identical source physical targets.

**Interaction variable**: for a categorical UCI outcome no scalar additive interaction is canonical; score a 2x2 contrast in root-move categorical transitions and a separate numeric score/node count; no universal scalar "mediation proportion". If the SEE event never occurs in one treatment arm, that arm is `NO_CONTACT` and a full-factorial causal mediator is **not identified**. Treat TT suppression and SEE forced-opposite as different manipulable operators; forced Boolean does not equal a naturally plausible board change or legitimate SEE threshold intervention. Prevent illegal moves.

## Exact classical exchange caution

R1's 6-ply *legal same-square* material-exchange oracle excludes broader tactics and differs from native `Position::see_ge` optimized approximate static attack ordering, pinned-blocker checks, thresholds, capture stage exceptions, early queen/rook discovery exceptions. Do not retroactively infer that a zero legal capture threat predicts zero native SEE calls or no pruning.

## Scientific decision

R2 may establish **operator access/contact and site-bounded 2x2 interventions** on development positions. It does *not* itself prove a transported **positive** exact-UCI prediction. 0.22-P2-R1 M2 54/64 equals M0, 0 correct positive flips out of 10, and 0.22-P2 TWIC1656 M1 38/64 vs M0 54/64 remain FAIL. Any new prospective test requires a **new untouched source cohort** and separate StageA literal UCI and StageB outcome commits.

Licence release and reuse decisions are explicitly handed to **C3X 0.23**, not assumed from ability to download TWIC.
