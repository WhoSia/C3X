# C3X 0.29-P32 — Full-Game-History Opponent-Response Value and Three-Method Competition

Date 2026-11-04 KST. STATUS: **REAL UNMODIFIED STOCKFISH16 EXECUTED; ORIGINAL FULL PGN HISTORY VERIFIED; ARCHIVAL DEVELOPMENT (OUTCOME EXPOSED), NOT A NEW PROSPECTIVE HOLDOUT OR A MECHANISM CAUSAL IDENTIFICATION.**

## 1. Recovered old C3X source — no fresh TWIC necessary for this developmental stage

The original 0.18 engine-blind October 2025 Lichess source selection artifact from GitHub Actions run 37981820261 was *actually recovered*, extracted, and checked against its original frozen JSON SHA-256:
\`6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c\`.
Its 16 selected games are distinct by original game hash. The source stores original mainline UCI move lists and selected source ply, not just standalone FEN; Python chess rules replays all moves, validates four-field source FEN, source next move, legal root, history length and retains \`Board.move_stack\` to send UCI original game history to Stockfish. This directly addresses the history-versus-FEN non-equivalence found by 0.18.

**Long-lived custody, not dependent on expiring GitHub Actions artifacts:**
- Original C3X 0.18 source ZIP placed in Google Drive \`C3X/01_SOURCE_ACCRUAL_RAW\` with original source archive, ID \`1vn6-CY3uwv4PjaqQbQURhWzEhsxY22NV\`.
- New source16 native-result R2 ZIP in \`C3X/04_SEALED_RESULTS_COURTS\`, ID \`1DLgFj77J9FAEZ8K6ybn0PHkCu61Sy0QU\`.
- New R3 result ZIP, including native full history, competitor methods, material response lineages and receipt hashes, in same Drive results folder, ID \`1U_bIzEVLH2R9zBD78VSbjGMoqo7j6SM7\`. The folder name is historical custody; **the contents explicitly remain SOURCE-EXPOSED DEVELOPMENT, NOT a sealed blind performance claim**.

Original game data license and source origin are retained in the original selected-source manifest. We do NOT copy raw full game mainlines into the public GitHub code repository.

## 2. Native trial actually performed

Workflow: \`.github/workflows/c3x-029-p32-full-history-root-value.yml\`; pinned official Stockfish16 \`sf_16\` exact Git HEAD \`68e1e9b3811e16cad014b590d7443b9063b3eb52\`, original engine source **not modified**. Python chess 1.11.2, Threads=1, Hash=16MB, Use NNUE=false to be consistent with historical C3X SF16 evaluation. These are NOT current Stockfish default settings or a competition-strength configuration. Root and reply searches at depth 12 (whole 16), focused case 10 repeated at depth 18. MultiPV=2 at root; analyzed both top candidates plus source-played move (36 distinct root candidates total). For each root: forced root analysis and top three ranked adversarial replies at depth 12, followed by first proposed mover reply and material changes at root / after opponent reply / after mover response. The original game is fully reconstructed for every arm; each search uses a distinct \`game\` key to reset engine game state between calls. The opponent response scores are rooted in the original mover's perspective.

Authenticated CI run **41770432051 SUCCESS**: source SHA, Python unit tests, pinned native SF16 compilation, all sixteen history replays, original root and top-three reply searches, and three-method empirical comparison completed. Historical 0.17 P4 order-intervention native results and 0.27 TT-FIRST mechanism histories remain separate, and must not be falsely credited to this unmodified search.

### Cohort development statistics, not independent expected performance

| Observation | Development cohort result |
|---|---:|
| Distinct original complete-history games, all evaluated | 16 / 16 |
| Different candidate root moves actually searched | 36 |
| Original played move also top1 Stockfish depth12 | 8 / 16 |
| Depth12 root top1-top2 absolute gap <=20 cp | 6 / 16 |
| Depth12 root top1-top2 absolute gap <=50 cp | 12 / 16 |

The root-pair scores above are those from same MultiPV=2 analysis. Selecting near-equal cases **after** looking at current scores would be a source-exposed subgroup, not an independently predefined near-tie cohort. All CP values are engine estimates with finite depth. Mate scores use high sentinel and must NOT be interpreted as small centipawn differences.

## 3. A chess-true foil: the development game #10

Original source game URL (source list, not newly imported): https://lichess.org/broadcast/62nd-indian-national-championship-2025/round-11/8sPA1Pj2/Nb9VCjJh ; black to move on source ply 43; original FEN4:
\`r3k2r/p1p5/1p2b1p1/4bp2/2P2N2/BP2PKP1/P7/3R1R2 b kq -\`.

Two legal candidates:
- \`e8f7\` = \`...Kf7\`: no immediate capture, material change 0. Actual broadcast game played this move.
- \`e5f4\` = \`...Bxf4\`: black bishop captures white knight, immediate MATERIAL +320 under our declared N=320/B=330 convention; White's *legal* \`f3f4\` (\`Kxf4\`) captures the bishop, restoring material difference to **-10** (=320-330). The 320 and -10 are **material-unit accounting**, NOT Stockfish Q-scores.

**Official SF16 same-run MultiPV root depth12:** \`...Kf7 +39cp\`; \`...Bxf4 -13cp\`. **Depth18:** \`...Kf7 +13cp\`; \`...Bxf4 -13cp\`. Thus root ranking \`Kf7 > Bxf4\` persists, while the margin changes from 52cp to 26cp. Other forced root depth18 scores \`+21cp\` and \`-4cp\`, and best-opponent depth18 reply scores \`+12cp\` and \`0cp\` respectively: the search method changes numbers, so do not falsely collapse these into a unique exact Q.

Actual next broadcast mainline \`e8f7, e3e4, e5f4, f3f4\`, i.e. \`...Kf7, e4, ...Bxf4, Kxf4\`. The **first four halfmoves of the depth18 main PV reproduce this actual sequence**. This is notable observational agreement on one historical game, not proof that engine preferred \`Kf7\` specifically to prepare this exchange or that a future plan caused its original choice. The extra preparatory moves also alter the king and pawn state, so the two continuations are not an isolated single-variable experiment.

Crucial C3X finding is NEGATIVE against a weak story: "the choice is better because it captures the knight" is factually true for Bxf4's immediate move but fails as a root-preference explanation here. An unmodified Stockfish+PV baseline at depth18 **already displays the relevant sequence**. C3X branch-aware output has not established independent incremental value over that baseline.

## 4. Horizon-length counterexamples in the SAME source16

Game #11: source \`f4e5\` and best opponent \`a5e5\` appear to produce MATERIAL -900 immediately after opponent recaptures the white queen; PV then continues \`d4e5\`, recapturing black queen, and MATERIAL returns to 0. The depth12 best-reply engine value is 0cp.

Game #16: root \`e3c3\`, best opponent \`a5c3\` captures white queen; next \`b2c3\` recaptures opposing queen. Material changes from 0 to -900 to 0, and the opponent-response engine estimate is +4cp (original white mover perspective).

Thus even "after opponent best reply" *material count* is insufficient to assess a plan that permits a tactical recapture one ply later. Values must be measured after relevant own continuation as well, and should be conditional on legal adversarial responses, horizon, and an explicitly stated utility target. Material balance itself does not measure mating threats, king safety, initiative, or tablebase value.

Another source #6: for played \`c5c6\`, the opponent's SF16 top-three replies yield mover-perspective estimates +84cp (best response \`b7a8\`) vs +300/+314cp on weaker alternatives. This large observed branch spread illustrates why a single attractive PV branch cannot justify a universally good plan. It is depth12 search evidence, not an exact equilibrium bound.

## 5. DIRECT historical three-method competitor on 16 actual next opponent replies

Source next move after each played move is recovered from **actual archived game history**, and compared to:
- **A, forced-root Stockfish+PV:** one predicted opponent reply from the first line of a root-forced Stockfish analysis.
- **B, simple one-reply plan JSON:** material before/after and first engine-best opponent response (one predicted move).
- **C, reply-conditioned richer JSON:** engine ranked top three opponent response continuations (THREE predicted alternatives, not one).

| Method/coverage task | Historical actual next move |
|---|---:|
| A one-move exact prediction | **8 / 16** |
| B one-move exact prediction | **9 / 16** |
| C actual move in three proposed replies | **13 / 16** |
| C actual is first/second/third ranked | **9 / 3 / 1** |
| C omitted actual source reply | **cases 3, 9, 14** |

IMPORTANT: **13/16 is a list-of-three coverage, not one-step prediction accuracy**. Methods are *not compute-matched*: branch expansion invokes extra searches, and actual human choices are not ground-truth minimax or objective explanation labels. There is **NO DEMONSTRATED C3X SUPERIORITY** over a simple plan JSON or engine+PV. In fact, the simple plan with one response covers only one more human choice (9 rather than 8), and a full C3X formal causal search model was not run here. This is an honest competition among three preliminary representation formats/queries, not a paper-level causal-method ablation.

Interesting failure: game #14 actual opponent move \`d8d7\` is absent from all three top-reply candidates, although their three engine scores cluster within 1cp. Apparent robustness in *top-three estimated values* does NOT imply coverage of the real opponent's option set or universal robust value.

## 6. A better mathematical target and why P32 does not prove it

Let \(s\) include full legal game history, \(a\) be a candidate root action, and \(\pi\) a contingent own-move policy after each opponent response. A plan-value research question is the estimated bound \(\hat Q_d(s,a,\pi)=\min_{r \in R(s,a)} \hat V_{d-2}(T(T(s,a),r);\pi)\), where \(R(s,a)\) is an explicitly specified set of legal opponent moves, and the bottom evaluator accounts for continuation. For actual chess minimax one would require all legal opponent choices, arbitrarily deep search or solved game outcomes; our **MultiPV top3 and finite depth12/18 are not such proofs**. Nor does the numerical \(\hat Q\) identify a Stockfish internal causal mediator.

At the engineering level the three measured targets are fundamentally different:
1. **Chess truth** of material and legal moves, rules-verifiable.
2. **Engine estimate** for the adversarial continuation, source-dependent bounded-depth and search-operator-dependent.
3. **Actual engine choice cause**, which requires separate TT/order/writer/reader interventions (prior C3X 0.27+ court), not inferred from the visual quality of a line.

For scholarly novelty a future prospective test should compare matched compute of vanilla score+PV, simple foil-aware JSON and C3X full branch/causal representation on new *source-independent complete histories*. The negative alternative is that a simple search PV (or plan JSON) already contains all useful strategic content; in that case retire unsupported C3X complexity rather than relabeling traditional minimax as new.

## 7. Exact executable sources and immutable receipts

- \`harness/c3x_029_p32_original_history_reply_value_native.py\`: legal UCI prefix replay, original SF16 root and reply searches, material flux up to third ply, depth18 focused rerun.
- \`tools/test_c3x_029_p32_history_value_inputs.py\`: source history FEN fail-closed, repetition, declared material units.
- \`tools/c3x_029_p32_original_game_reply_competition.py\` and its tests: actual human next move against A/B/C predictions/coverage.
- \`.github/workflows/c3x-029-p32-full-history-root-value.yml\`: source exact SHA, fixed engine commit, executable complete-history native trial and comparison.
- P32 R3 output ZIP Drive ID \`1U_bIzEVLH2R9zBD78VSbjGMoqo7j6SM7\`; contained \`P32_ORIGINAL_HISTORY16_SF16_REPLY_VALUE.json\` SHA256 \`8e9ed5104156887221696a79416c69060dc3fa8beb48c02142337591b25efc8b\`, \`P32_THREE_METHOD_ACTUAL_REPLY_COMPARISON.json\` SHA256 \`d86e6ed214c35b86e0017a36b9ab1a3b76190bf427194feea71882dea65199a9\` and SHA manifest. Full ZIP SHA256 \`2434fa7cd7868f0afa89530e242d0a2bbabfdcb5a957b22886dcf5e7e9ebe456\`.
- Authenticated successful GitHub Actions run: https://github.com/WhoSia/C3X/actions/runs/41770432051

**No background bots authored a commit.** GitHub Actions ran binaries/read-only tests and uploaded evidence, while code changes were authored using the connected GitHub file API.

## 8. Next question: does branch information help if PV already captures the event?

Priority 1 (before another conceptual gate): quantify *matched node/time budget* and detect examples where one-branch PV gives a false or incomplete explanation but a multi-reply contingent explanation **correctly predicts an independently established branch-specific outcome**. Use original game history replay, heldout game-level split, human (or deterministic rule) gold criteria. A real failure of this criterion means no claim of excess explanation performance. Priority 2: compare root value and actual TT mediation only after this value-level competition is meaningful. No need for new TWIC until the archived complete histories are exhausted; fresh TWIC should be future source-frozen before any new engine scoring.
