# C3X 0.29-P35/R7 — Native SF16 UCI Deadlock Falsification, R4 Cold Replay and R6 Real Root-Competition Receipt

Date: 2026-11-05 KST. **NEW VERIFIED NATIVE EVIDENCE, NOT AN NNUE FEATURE→ROOT CAUSAL PROOF.** Do not rename exposed development games as heldout.

## 1. The actual R6 failure was a protocol bug, now source-proven

Previous P35/R5 native run [41936514739](https://github.com/WhoSia/C3X/actions/runs/41936514739) and R6 run [41953730304](https://github.com/WhoSia/C3X/actions/runs/41953730304) both **FAIL** at first real-search line with `P35_R5_ENGINE_TIMEOUT` after 120 seconds, **not** at compiler, basic UCI mock test, native source cloning or NNUE net load.

Checked pristine official Stockfish16 `src/uci.cpp` at commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Git blob SHA `ed16f24c382ec5d11555f9ab0fab4fa29b42dc47`. Original code explicitly comments `if (token == "searchmoves") // Needs to be the last command on the line`; subsequent `while (is >> token) limits.searchmoves.push_back(UCI::to_move(pos,token));` consumes the `nodes` option if it follows searchmoves. Thus the old `go searchmoves e8f7 nodes 24000` had **no parsed nodes limit**, explaining timeout.

Minimal human-authored fixes:
- [Corrected original engine harness](https://github.com/WhoSia/C3X/blob/main/harness/c3x_029_p35_r5_search_route_court.py): `go nodes 24000 searchmoves ...`, searchmoves LAST; unrestricted remains `go nodes 24000`.
- [UCI mock regression](https://github.com/WhoSia/C3X/blob/main/tools/test_c3x_029_p35_r6_three_arm_uci_contract.py) explicitly rejects old option order.
- [CI rerun workflow](https://github.com/WhoSia/C3X/blob/main/.github/workflows/c3x-029-p35-r5-eval-dispatch.yml) remains `permissions: contents: read`; source and artifact reads only, no commit/push/tag.

Relevant three GitHub user commits: `1dc66565d1145583cbde647c7c6fe6876365e174`, `66ad4f98439cef722e4dca0076a644c29b473ea9`, `09806822009cdbab2f40b5c3ef215388307e40cc`.

## 2. Previously unconfirmed P35/R4 cold replay now independently verified PASS

[Original Stockfish16 two-cold-replay run 41786141445](https://github.com/WhoSia/C3X/actions/runs/41786141445): completed **SUCCESS**, original 12 full-history direct evaluations produced identical native raw traces in two new per-board engine processes and against the old P34 originals. Downloaded artifact ZIP original SHA256 `d7d8746d50975040f1724a6ebd67425c5fa142ee648ffea89530db97567044a3`; intrinsic verdict `P35_R4_12_BOARD_COLD_REPLAY_PASS`, 12 boards × 2 cold reruns, raw trace identity exact. **New binary SHA equals historical original binary SHA:** `6458324545ef0f43b5a74de75c980e08413251247bba500d9befac113a43f325`. Network SHA256 (file `nn-5af11540bbfe.nnue`) `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`. This establishes static evaluator exact replay under this pinned machine build, NOT leaf-to-root source mediation.

## 3. P35/R6 three-arm REAL Stockfish16 native result now PASS

[Corrected native run 41954743133](https://github.com/WhoSia/C3X/actions/runs/41954743133): completed **SUCCESS**, native job `127006828484` full steps PASS including original and modified engine builds, original 0.18 source and 0.29-P34 reference SHA checks, both Python test suites, 16 source-executed search processes, all final parity assertions and artifact upload.

Downloaded original artifact `c3x-p35-r6-native-real-sf16-three-arm-root-competition` ID `13383060083`, ZIP SHA256 `093ace9b9eabb610cc1a6096bfa1e648c66c7a2257290d710ba670039afdb6dc`; JSON `P35_R6_THREE_ARM_ROOT_COMPETITION.json` contains **8/8 strict vanilla-vs-instrumented bestmove/score/PV/nodes parity**, not only fixed bestmove. All have requested `24000` nodes and actual nodes `24004..24029`. Original-source exact instrumentation diff adds only a C stdio header and guarded `std::fprintf(stderr,...)` after computed evaluator return value, in actual `Eval::evaluate()`. This does not prove a change in root choice.

### Actual observed data (2 source-exposed development games, not 8 independent games)

| Game | Arm | Root restriction | Bestmove | Score cp, root side-to-move POV | Actual nodes | NNUE eval calls | HCE eval calls | HCE rate among actual eval calls | Instrument parity |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| 10 | forced | e8f7 | e8f7 | +69 | 24007 | 12974 | 77 | 0.590% | PASS |
| 10 | forced | e5f4 | e5f4 | -12 | 24011 | 13640 | 31 | 0.227% | PASS |
| 14 | forced | c2c3 | c2c3 | +71 | 24012 | 12760 | 554 | 4.161% | PASS |
| 14 | forced | d5d3 | d5d3 | -8 | 24027 | 13412 | 535 | 3.836% | PASS |
| 10 | paired | e8f7,e5f4 | **e8f7** | +67 | 24029 | 13657 | 70 | 0.510% | PASS |
| 10 | **unrestricted** | all legal | **e8f7** | +43 | 24004 | 13463 | 47 | 0.348% | PASS |
| 14 | paired | c2c3,d5d3 | **c2c3** | +85 | 24010 | 11954 | 608 | 4.840% | PASS |
| 14 | **unrestricted** | all legal | **c2c3** | +88 | 24010 | 12575 | 772 | 5.784% | PASS |

Total **107129 actual Eval::evaluate dispatch log events** across eight instrumented search contexts. Direct `Use NNUE=true` enters actual NNUE route for ~94-99.7% of logged evaluation events, but HCE fallback is nonzero in **all eight**. Full unrestricted roots had **no third candidate** on these two original games at 24000 nodes. The P9 third-candidate finding in a different case and context remains intact. This sample does not estimate the population frequency of third-candidate events.

**Root margin warning:** Forced-root scores +69 and -12 are from separate fresh independent 24k search contexts; they are not a single jointly calibrated exact move-pair utility contrast. Pair/restriction choice and unrestricted bestmove are native search observations. Root score change between paired versus full search shows context sensitivity (game10 +67 vs +43; game14 +85 vs +88) even with same selected bestmove; not a causal mediator attribution.

## 4. Exact evidence and custody

Original native archive preserved at [Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/1iRnnsRu-37go3RZzoIPS88IJbPS1EYCb/view), filename `C3X_0.29_P35_R6_NATIVE_SF16_THREE_ARM_SEARCH_20261105.zip`. Raw Drive bytes not modified after upload. ZIP SHA above is GitHub original zipped artifact; cross-platform file identity should be checked by Drive raw fetch before asserting identical uploaded byte content. Original archived P34 source game raw remains immutable.

## 5. Scientific ceiling and stop decision

**PROMOTE:** P35 static native exact replay, actual search-time NNUE/HCE dispatcher observations, and nonperturbing 3-arm search parity on 2 source-exposed games.

**HOLD:** Neural representation feature causal effect, leaf-to-ancestor-to-root natural-choice mediation, independent game/engine transport, better consequence forecast than plain Stockfish+PV or simple foil-aware JSON, any human comprehension benefit.

**PI decision: NO MORE DIAGNOSTIC GATES IN THE SHORT TERM.** We have overcome the one narrow native source-path blocker. Return to a single falsifiable chess consequence question; freeze one previously unexposed source-disjoint near-equal move pair, predeclare a legal opponent reply consequence Q, compare same-budget Stockfish score+PV vs simple foil-aware JSON vs C3X with equal forecast set size. If no incremental result or the strong baseline wins, record a genuine negative and simplify. Do not interpret static NNUE rank reversal as neural feature concept discovery.

## Research OS authority

Notion scientific judgment / GitHub executable provenance / Drive original raw bytes. GitHub Actions read-only compute and artifact upload; `github-actions[bot]` must never author or move repository refs. No external bot authorship in the fixes.
