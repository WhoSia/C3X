# C3X 0.29–P42/R19 — Root-Depth Propagation After an Exact Native Cycle Return Reversal

Date 2026-11-09 KST. **Research hypothesis registered before new R19 native run outcome.** This is one inferential link within the main unsolved causal–strategic explanation problem, not a benchmark or trivial "we counted nodes" paper.

## Strong source-native evidence now in hand

R18 original source locked Stockfish16 Game14 has a real original TT_FIRST B cycle-alpha event33 whose physical board/search-window state also occurs as C event **35** with active exact capture-prune bypass. The source-native [R18 run #42552769246](https://github.com/WhoSia/C3X/actions/runs/42552769246) **SUCCESS**. The experimental C source original draw return at this *matching original B state* was +1, immediate alpha>=beta true; under one precisely matched forced return -1, immediate cutoff became FALSE (both cold replays). **Yet final unrestricted C bestmove stayed b3a4** in two native cold repeats. Thus changing that one actually reached alpha/beta cutoff is *not sufficient under the intervention to revert C's root to B's f3f4*. This is not evidence that all cyclic draw-return paths or global modifications are irrelevant.

R18 original public artifact #13645714442 ZIP independently downloaded and SHA256 checked: `b191a3a292647305a5ef81a6df590cd3a9d61095bc3e3d7ebf89f0e527379a32`; exact member `C3X042_R18_REVERSE_C_SOURCE_CYCLE_ROOT.json` SHA256 `dcb1e80ae010490b80ab06a9a4612c52219714f37e4698f17b5488c32636eb4e`. Its JSON explicitly reports **first C-vs-reversed-C depth-boundary difference at depth 9**, while final C-root remains b3a4. This suggests compensating search decisions *at some later stage*, but the specific nature of the depth9 change is not yet published. Boundary difference may involve leader, score, or cumulative average; cannot claim a transient action reversal from a generic boundary change.

## R19 main question and positive/negative adjudication

> When a source-identified, physically executed, single cycle-alpha draw return changes the immediate cutoff but not final chess move, does that intervention actually change intermediate root candidate preference or merely root scores?

This is a proof obligation for a real source information-flow explanation. Treat **the explicit unchanged final move as an important negative** rather than a reason to skip inconvenient intermediate evidence.

R19 runs the **original R18 court, unchanged**, on the same pinned Stockfish16 build and locked original source/Stage A:
- R18 itself verifies original A/B/C, original C capture-guard contact, exact original B-board+window source identity, just one `+1→−1` native source modification per physical engine subprocess, actual cutoff TRUE→FALSE, same original historical TT reader, and cold-repeat root action b3a4.
- Within this *single* source-native experiment, R19 opens original C's 12 iterative-deepening root-boundary summaries and both repeats of reversed C from original R18 private source logs.
- Compare **actual** leader (internal root move), score and average at *every identical depth*. Require two identical per-engine physical subplays and two stable independent cold runs; fail closed if source-depth support, event or root behavior is missing/unstable.
- Publish only a rights-gated aggregate: which depths had leader changes, score differences, average differences and delta magnitudes; no raw PGN, private source key, FEN, full TT lineage, or engine binary.

[Executable native R19 original R18-replay root-depth court](../harness/c3x_029_p42_r19_native_R18_root_depth_propagation.py) · [9 adversarial synthetic tests](../harness/test_c3x_029_p42_r19_native_R18_root_depth_propagation.py) · [read-only native workflow](../.github/workflows/c3x-029-p42-r19-native-root-boundary-propagation.yml), initial [#42554337265](https://github.com/WhoSia/C3X/actions/runs/42554337265) started.

The R19 verdict may be:
1. Actual **root leader changes at one or more intermediate depths**, but original final move still b3a4. This is a stronger *transient computational preference sensitivity* fact, not a final action mediation proof.
2. **Only root score/average changes**, no intermediate leader change. This narrows source effect to score book-keeping or future bound changes; no transient root choice claim.
3. No change in any of 12 recorded boundaries despite event and cutoff difference; source effect was locally active but not detectable in the measured summary.
4. Source/cold/provenance drift: HOLD and retain failed attempt.

The original code and old artifact SHA remain immutable; R19 adds independent audit fields and new source runner, not a patch to change old data. Even a leader flip at intermediate depth is **not a claim** that the same cycle event naturally mediates the original TT_FIRST→guard branch restoration, because source intervention can change future node support and other TT/history states.

## Main flagship still unresolved

Game14 is postselected and Stockfish16 has NNUE OFF. A rigorous final paper must identify the causal decision-computation under source-native intervention **and** show the computation is faithful to strategically meaningful adversarial chess futures through independent value judgement and *prospective* held-out cases. No postselected Game14 source-trace-only finding gives that prospective or chess-semantic PASS. Preserve earlier R18 negative result and broaden only when genuine native intervention provides evidence.


## 2026-11-09 — Actual R19 original-source native result (after preregistration)

Actual original-source [R19 native #42554337265](https://github.com/WhoSia/C3X/actions/runs/42554337265) **COMPLETED SUCCESS**, all strict source regression tests, original 16-game StageA hash verification, exact unchanged R18 physical reverse and source-native two-cold court, publication rights checks and aggregate-only artifact upload. The original event happened at C ordinal **35**; the source forced draw score **+1→−1** and changed the local alpha>=beta cutoff TRUE→FALSE. Original and reverse C both selected b3a4 in both cold runs.

Independent inspection of native public ZIP #13647101061 confirmed SHA256 `30c070a09fd91b7c7e912f1fa864f74d3bdc5692ff54052af39c4bc42c25f272`, JSON member `C3X042_R19_ROOT_BOUNDARY_PROPAGATION.json` SHA256 `c23f914a450866c6550d4a1ea4ab6a4ffeb7810009ffbd3ec62f306958be6954`. [Permanent human-authored provenance receipt](../evidence/C3X_029_P42_R19_ACTUAL_INTERIM_ROOT_LEADER_RECEIPT_20261109.json).

Crucial **actual original-source root boundary observation**:

| Depth | Leader changed? | Reverse-C minus original C root score | Reverse-C minus original C average |
|:--|:--|--:|--:|
| 1–8 | No | 0 | 0 |
| **9** | **YES** | **−15** | −19 |
| **10** | **YES** | **−16** | −20 |
| **11** | **YES** | **+15** | +21 |
| **12** | **NO** | **−15** | −9 |

Therefore the exact native single-event cycle-alpha branch reversal changes intermediate root *leader identity* at depths 9,10,11, not just score, despite leaving final b3a4 root action intact. At depth 12 original and reversed C leader identity agrees again, **but numeric search boundary does not**. This is evidence of transient downstream *decision-state* intervention sensitivity and later *action-level* convergence, **not** proof that the full source search state converged or that one specific new ancestor score is the unique source mediator.

### Next identity challenge (R20)

[New R20 native runner](../harness/c3x_029_p42_r20_source_native_legal_root_candidate_transport.py), [ten adversarial tests](../harness/test_c3x_029_p42_r20_source_native_legal_root_candidate_transport.py), [read-only workflow](../.github/workflows/c3x-029-p42-r20-native-legal-root-candidate.yml), initial [run #42554911743](https://github.com/WhoSia/C3X/actions/runs/42554911743) triggered. This extends the same original R18→R19 full source custody and **legally decodes every source-native Stockfish root leader** (a normal `Move` source raw integer encoding) against the exact chess position, to identify whether the reverse-C intermediate lead is B=f3f4 or a third legal candidate. Any nonlegal/special/unrecognized move is HOLD, not falsely labeled strategic. Full chess future, TT/SEE guard natural mediation, and prospective generalization remain HOLD.
