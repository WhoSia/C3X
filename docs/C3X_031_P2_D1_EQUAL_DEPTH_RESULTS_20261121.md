# C3X 0.31/P2-D1 — Seven-Game Equal-Depth Transport: Five Choice Contrasts, Only One Original Candidate-Pair Reproduction

**Date:** 2026-11-21. **Science status:** **EXPLORATORY_POSTOUTCOME_EQUAL_DEPTH_DIAGNOSIS**, real original Stockfish16 experiments, full legal game histories, **seven postselected P2 root-flip cases**, not a new independent seven-game result. Source P2-D1 depth protocol [frozen before new searches](C3X_031_P2_D1_EQUAL_DEPTH_PREREG_20261121.md).

## 1. Physically performed searches and source identity

The 0.31/P2 native prospective TWIC1670 cohort initially produced **seven final `bestmove` flips** across its 128 physically reached 32k-node source-gate events, but six of seven differed in completed iterative deepening depth. P2-D1 retained **all seven**, fixed exactly 13 target-depth cells (original completed depth plus treatment completed depth if distinct), and used the previous P2 **same source game histories and same physical R33 OPEN event IDs**, not newly chosen candidate positions.

Actual read-only [native GHA #44874168539](https://github.com/WhoSia/C3X/actions/runs/44874168539) executed **78 new source-native Stockfish16 searches**: for each of 13 depth cells, pre-R33 baseline, R33 observer off, R33 observer-only×2, and physically signed futility+null-off treatment×2. No physical sample or event replacement. **All thirteen baseline reference-vs-observer parity checks passed**, all original cold control and treatment replays were deterministic. For **12/13 depth cells**, the original P2 physical event OPEN matched and the target was completed; for **P2-043-1 depth 9** the physical source target could not be matched and was explicitly **HOLD_SOURCE_CONTACT_OR_IDENTITY**, not a zero-effect observation.

Source-pinned base: official SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, pre-R33 executable SHA256 `78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb`, physical patched gate SHA `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1`, NNUE SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`. Original P2 source event SHA `17915c7d9ae56dd950cd026d07a4917a414213415ea3b28af256b305eb8ad146`; original node-limited treatment JSON SHA `69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f`. All supplied history/source/world inputs were rehashed by the native GHA itself.

[Original P2-D1 complete event results ZIP, Drive](https://drive.google.com/file/d/1aVvUcC4yx0GPGVnMiu-cd-BOwy0RgPRw/view): ZIP SHA256 `c9a060afea6d0fc93cd20f08eb12699fe4aca2763eb0e78d536e43bff19840c5`, JSON SHA256 `e2a56d69342fbe60a522f62b69ca01c08446008c482a571b8dc0a47e5ba95f90`. [Original 156 native stdout/stderr log ZIP, Drive](https://drive.google.com/file/d/10ON1bo3ocLr6hwfyVbAf_TI8cqBkgrm9/view), SHA `e45dca037f748a06e5043194de397ca26659af726c174a9505f097a5566202bc`. [Public inspection JSON ZIP, Drive](https://drive.google.com/file/d/1sCRSC2SQ6OWCIN_jddWpbhlBbL74SpwU/view), JSON SHA `ed325549d1a4cf25fb362791ade8d811253a9dc29b2d15e039b75390e25fb791`. Original source ZIP and member CRC verified after download.

## 2. What equal completed depth does and does not preserve

Across **13** registered candidate-depth cells, **12** physically matched the original source target: **8** had a different bestmove between source control and treatment, **4** did not. The thirteenth is HOLD. Among the seven cells at each game's **original completed depth**, **5/7** had a source-caused final-choice contrast, **2/7** did not. Crucially, these observations are not *five replications of the same original candidate pairs*: in **only 1/7** original-depth cells were **both** original node-limited `bestmove` identities reproduced exactly.

| Event and original depth | Original 32k-node control → treatment | At fixed original depth: control → treatment | Same original pair? |
| --- | --- | --- | --- |
| P2-008-1 / depth13 | `e2c4 → g3e4` | `e2d3 → g3e4` | **No** |
| P2-027-1 / depth11 | `g2g3 → f1f2` | `g2g3 → e5d3` | **No** |
| **P2-028-0 / depth16** | `d4e5 → f4e5` | **`d4e5 → f4e5`** | **Yes** |
| P2-034-1 / depth12 | `c4d3 → c4c2` | `h4h5 → c4c2` | **No** |
| P2-035-0 / depth12 | `e5f3 → f2f3` | `e5f3 → e5f3` | **No contrast** |
| P2-043-1 / depth11 | `f3d2 → c1b2` | `f3h4 → c1b2` | **No** |
| P2-055-0 / depth17 | `d2d1 → d3b5` | `d2d1 → d2d1` | **No contrast** |

The within-fixed-depth differences prove that source perturbation effects can persist at the same **completed depth** in several exposed games. They **do not** show that the *same original preference contrast* survives when the stopping rule changes. In particular, the initial P2-008-1 node-capped run already finished depth13, yet removing the node cap changes its untouched baseline from `e2c4` to `e2d3`. This is a vivid negative example of treating `completed_depth=13` as a complete search-state equivalence class.

## 3. Second registered depth arm: additional counterexamples

For the six whose node-capped treatments finished at a depth different from their original baseline, the secondary fixed treatment-depth arm was also executed:

- **P2-027-1 depth10:** `g2g3 → f1f2` exactly reproduces the original node-capped move pair, but at **treatment** depth, not the original baseline depth11, where treatment instead chooses `e5d3`.
- **P2-028-0 depth15:** `d4e5 → f4e5` again retains the original node-capped pair. Together with its depth16 result, this is the only game for which the identical candidate pair survives at **both** registered fixed depths.
- P2-034-1 depth11: no contrast (`c4d3` both conditions), despite original-depth12 fixed source contrast with a different baseline `h4h5`.
- P2-035-0 depth10: a contrast `g2g1 → f2f3`, but the original-depth12 result shows no choice contrast. The original node-capped P2 control candidate `e5f3` is not a robust context-free move identity under this change of stopping rule.
- P2-043-1 depth9: source target **not physically matched**; abstain, even though public moves are unchanged.
- P2-055-0 depth13: unchanged `d3b5` in both fixed depth arms; depth17 unchanged `d2d1`. The original 32k-node root flip vanished in both fixed-depth comparisons, consistent with stopping/search-allocation sensitivity.

**Absolute rate claims (e.g., 5/7) must say post-outcome selected; the experimental unit is one original game with correlated depth arms, never 13 independent new games.**

## 4. Source-state hypothesis sharpened by the one exact-pair survivor

**P2-028-0 is now the best exploratory source-state mediator case**, because it retains the *same actual legal-history `d4e5 → f4e5` root move contrast* at fixed depth **16** and depth **15**. At depth16, the actual source control searched **35,662 nodes** and the intervention searched **36,217 nodes**, a difference of 555 nodes, in two deterministic fresh-process runs each. The target physical source event was **`C3X_R33_OPEN event=19, attempt=16, source-root=d4e5, depth=1, ply=5`**; original native child return changed `-2429 → -2500` when the candidate's child futility gate was suppressed. This is a physical source intervention and downstream root-choice contrast under a full game history.

**Important:** 555 different nodes is still *different search work*. Equal depth and approximately equal node count do not prove matching node visitation, TT contents, history heuristics, aspiration windows or which candidate's source return mediated the choice. It cannot by itself prove that `f4e5` is better chess or helpful to a learner. P2-028 is **post-outcome-selected**, not fresh holdout evidence for a new theoretical model.

**P3 next experiment:** at a same-prefix reference source checkpoint just before event19, explicitly capture and restore single-family TT and history/ordering mediators and compare true sham, no-contact and real fixed depth16 controls. Freeze an intervention contrast against a pre-specified root `d4e5` vs `f4e5` outcome; a specific source path must be shown necessary/sufficient to explain the root change, and the root menu/budget details must be controlled. Avoid automatically transferring R35's separate single-game mediation conjecture to this newly selected P2 game.

The original eight M2-risk-based high/low P3 diagnostic cases were separately picked in Notion *before P2 labels* and remain retained, including negative predictions. P2-028 is an **additional mechanism target selected after outcomes**, not their substitute.

## 5. Reproducible scientific authority

- [Actual fixed-depth source generator](../harness/c3x_031_p2_d1_equal_depth.py), [six preflight signed-source/depth tests](../tests/test_c3x_031_p2_d1_equal_depth.py), [native 78-search workflow](../.github/workflows/c3x-031-p2-d1-equal-depth.yml). [Native success #44874168539](https://github.com/WhoSia/C3X/actions/runs/44874168539).
- [Independent 156-native-log verifier](../harness/c3x_031_p2_d1_independent_court.py), [negative claims tests](../tests/test_c3x_031_p2_d1_independent_court.py), [read-only audit workflow](../.github/workflows/c3x-031-p2-d1-independent.yml). This performs **zero new source searches**; all native outcomes are the original #44874168539 data. Early failed CI runs caused by a synthetic mutation test not targeting the correct original pair and then an incomplete test argument after strengthening source custody remain visible as **engineering negatives**, not chess science negatives. A later green independent GHA should be cited only after observed.
- [Original P2 64-game native prospective result and negative forecast court](C3X_031_P2_TWIC1670_TRUE_NATIVE_TRANSPORT_RESULTS_20261121.md) remains authoritative for original `32k nodes` endpoint; this D1 follow-up **does not rewrite its rates, treatments, labels or model score**.

**Claim ceiling:** native fixed-depth causal total-effect diagnostics are established for physically matched cases, but the correct minimal decision-state abstraction, TT/history mediation, opponent-robust chess planning and learner value all remain **HOLD**.
