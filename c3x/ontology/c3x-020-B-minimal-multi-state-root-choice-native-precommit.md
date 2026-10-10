# C3X 0.20-B — Minimal Sufficient Multi-State Restoration & Root-Choice Causal Falsification

**Status: PRE-OUTCOME SOURCE IMPLEMENTATION AND FACTORIAL CONTRACT. NATIVE RESULTS NOT YET OBSERVED.** 2026-10-10; C3X 0.20 ACTIVE.

## Mission / primary outcome

Find which *actual native search-state edits* can restore **the categorical original F `bestmove`** in four fixed February Stockfish16 positions. A result is successful only if the delivered treatment matches its specified original-source site, original F move is chosen, Cold duplicates agree, and frozen F/V/019-A0 control UCI outputs remain unchanged. The objective is an interpretable mechanism of **root move choice**, not additional TT instrumentation.

Prior independent February F19.5 FAIL, Jan J2/J3/J4 FAIL, and 019 K4 FAIL 0/4 remain intact. These four cases are selected *after* prior February outcomes: all effects are exploratory, not new-population confirmation.

## Frozen source/data and actual insertion sites

- Native Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b52`, depth 12, Threads1, Hash16MB, NNUE off; same source original and P4/018/019 overlays.
- Baseline 019 original court SHA256 `8639dc5d512ffb9a421164fe2631698af59e76b876aa43ac2aee99378045ab47` / Actions #38031332649.
- `tools/c3x_020_multi_state_root_repair_overlay.py` implements two independent opt-in C++ edits:
  1. Exact **SECOND** root return after child's native search and undo, before root score/alpha/PV. The earlier 019 A0 first-return edit remains independently guarded.
  2. Exact **BOUNDARY** RootMove `score` and/or `averageScore` at the *completed target depth*, after sorting, before next iterative depth. No direct alpha/beta override; next window responds through original engine control flow. Read-only snapshot `O` determines factual F and A0 source state before outcome treatments.
- Both use exact source coordinate checks, single contact counters and native `info string c3x020_...` witnesses. No environment variables ⇒ neither treatment mutates source logic.

## Prespecified cases and second return (pre-outcome)
| Game | Root role | 019 first-return depth | SECOND after A0 (depth/call/trial/move/index/alpha/beta) | A0 child → F child |
|---|---|---:|---|---|
| 3 | STRICT | 4 | 4/4/1/222/5/-190/-166 | -179 → -206 |
| 6 | STRICT | 10 | 10/19/2/1307/2/103/114 | 96 → 89 |
| 7 | BROAD | 4 | NOT_ELIGIBLE, second F/R diverging record has different move identity | — |
| 10 | STRICT | 4 | 4/5/2/2910/2/91/113 | -892 → -459 |

At completed depth of the first-return repair, BOUNDARY probes the **frozen F depth-terminal leader move** 1 / 1291 / 4020 / 2908 respectively for games 3 / 6 / 7 / 10. This is a predeclared target, not a post-hoc choice of successful move. Snapshot source score/averageScore F and A0 *values* are obtained with passive instrumentation only, before any outcome treatment; if a field is equal, its intervention is zero-dose and must be skipped and reported (not padded into positive denominator).

## Factorial arms (per case)
- `F_OBS`: F reference with passive depth-boundary state snapshot
- `FIRST`: original TT V FIRST reference
- `A0`: V FIRST + original 019 *one* child return restore (known K4 FAIL)
- `A0_OBS`: A0 + passive boundary state snapshot
- `A0_SHAM`: A0 + impossible native move 65535 for SECOND and/or BOUNDARY; no source contact
- `SECOND_ONLY`: V FIRST + targeted SECOND without A0 (g3/g6/g10); note if source path noncontact
- `A0_SECOND`: A0 + second same candidate return
- `A0_AVERAGE`: A0 + frozen F target RootMove.averageScore at completed first-return depth
- `A0_SCORE`: A0 + frozen F RootMove.score at same stage
- `A0_BOTH`: A0 + both values at same stage
- `A0_SECOND_BOTH`: combined treatment only when SECOND and BOUNDARY are eligible. If SECOND changes the boundary's expected pre-state, log CONTACT_MISMATCH / nonidentifiability and do not silently re-target based on its outcome.

The latter four BOUNDARY arms must document *nonzero actual delivered dose* and expected pre-state; never claim a nominally configured edit as measured contact.

## Scientific endpoints
**Primary**: (1) F original `bestmove` recovered or not in every delivered arm, (2) eligible and successful denominators per arm, (3) exact native dose and cold duplicate status.

**Mechanistic secondaries**: source candidate return (including SECOND), next rootMove score/averageScore, later candidate overtaking and leader depth, aspiration retry / initial window at depth+1, final six-field UCI and search nodes.

**Pre-frozen important negative:** Game 6 A0 already shares the F depth11 opening aspiration window [94,114] and first leader move1291. Simply copying those opening window *numbers* is not a meaningful new 0.20-B arm.

## Controls, falsifiers and STOP
1. F_OBS and FIRST must reproduce frozen source UCI. A0 / A0_OBS / A0_SHAM must reproduce 019 REPAIR UCI, otherwise native contamination.
2. F_OBS/A0_OBS boundary probe must be exactly one logged unchanged observation. Every accepted SECOND/BOUNDARY repair must have exactly one correctly matched source contact and the required before→after dose. Unreachable target, wrong alpha/beta, duplicate hit, silent source mismatch or observer changed output ⇒ NOT_VALID.
3. All *native* arms are independent cold doubles. The F source-move match, original legality and SHA-256 source selection remain fixed.
4. Joint interventions can produce source coordinate mismatch because the intervention changed history; classify honestly as `NONCONTACT_OR_CHANGED_PRESTATE`, never relabel it a rescue or swap to another move.
5. Even if 4/4 original F bestmoves are restored by a synthetic graft, that demonstrates a **bounded sufficiency result**, not a general root-choice law. New disjoint PGNs with independent source mapping will be required for transport.
6. Source tests and static original SF16 anchor checks precede **one consolidated read-only CI**; no automatic commit, no bot coauthor; WhoSia-only contribution and main branch.

## Execution plan
First install runner/native controls; source-only tests; then one consolidated Stockfish16 build and four-case factorial run with complete JSON evidence, source diff, SHA receipt and all unsuccessful arms retained. Review real `bestmove` and contact counts before making any mechanistic claim.
