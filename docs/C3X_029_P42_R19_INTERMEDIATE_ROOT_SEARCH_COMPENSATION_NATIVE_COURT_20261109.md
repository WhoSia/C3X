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
