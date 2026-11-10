# C3X 0.30/P5 — Original Martin Mirror Metamorphic Replication on Contrastive Chess Move Gaps

**2026-11-11 KST · verified original Stockfish16 source CI, not a posthoc unverifiable plan.** This work broadens C3X beyond explanation aesthetics: an educational statement such as “A is 0.05 pawns better than B” should disclose the **stability of this small source-engine gap under meaningful transformations and search depths**. P5 is a narrow, newly implemented **prior-art reproduction/adaptation**, not a claim to have reproduced all of the original studies or established a novel explanation algorithm.

## 1. Owned primary literature actually read in Google Drive

| Source / exact owned original | Technical proposition used | Implemented scope |
|---|---|---|
| [**Martin, Khelladi, Matricon & Acher (2025), *Re-evaluating Metamorphic Testing of Chess Engines: A Replication Study*, Information and Software Technology 181, 107679; DOI 10.1016/j.infsof.2025.107679**](https://drive.google.com/file/d/1bMl15sK_8G0h9GbuJehObn9zj8RoKKX7/view) | Transformation of chess position to an equivalent **color-swapped vertical mirror**, evaluation preservation as a metamorphic expectation, relative and absolute discrepancy, critical depth/dataset/engine-source dependence; finite-search discrepancy can reflect normal search, NOT necessarily engine bugs | **ONE original-paper mirror relation**, adapted to candidate-A minus candidate-B **forced-root** gap, three depths; **not** full original relation families, real-world large dataset, threshold calibration or version study |
| [**Jacovi & Goldberg (2020), *Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?*, ACL 2020**](https://drive.google.com/file/d/11ltQLiTQxQuFiKMJb5jnVtK5U--WtNXP/view) | Separate explanation plausibility, readability and behavioral or causal faithfulness; a graded, explicit definition is better than pretending all good explanations are faithful | **Disclosure policy only**, not original Jacovi benchmark, no human-grader measurement |
| [**Sandmann, Lapuschkin & Samek (2026), *The Algorithm Is Not the Behavior: Learned Priors Override Look-Ahead in a Chess-Playing Neural Network*, NeurIPS 2026, arXiv 2508.21380v4**](https://drive.google.com/file/d/1dAF7reY9DpwBlZFERxrF54qSNYOLbRi0/view) | In a chess model, look-ahead-like internal computation and final chosen action can disagree; learned prior can override an internally computed alternative. Internal computation evidence ≠ chosen-action causality. | **Research warning only**; no Lc0 activation patching, logit lens, or reported original reproduction |
| [**Bhaskar, Cheng & Chen (2026), *Language Models that Play Chess and Explain Their Moves* (QUEEN), arXiv 2610.03695v1**](https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view) | Combines chess-expert encoder, LM, iterative position-conditioned future explanation and distillation; evaluates explanation accuracy, substantiation and coherence | **Design candidate**, no pretrained QUEEN inference or training attempted |
| [**Shivkumar et al. (2026), *Bridging Chess Engines and Language Models: A Novel Framework for Generating Human-Like Chess Commentary*, IEEE Access DOI 10.1109/ACCESS.2026.3725218**](https://drive.google.com/file/d/1BOP1Qx7kApbNWKCf7KbKbowPrTTTP6IR/view) | Separate board-state evaluation, structured annotation, natural-language rendering, diverse validity and fluency metrics | **Design candidate for next evidence-first commentary module**; we did not run PPO or commercial LLM commentary generation |

The sources above were **actually searched and read from the user's own Drive copies**. The last three are *study inputs*, NOT claimed as replicated implementations. [Original C3X 1.md](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view) and [Cui 2026 primary strategy tree](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) remain the product's central problem and search representation.

## 2. Exact P5 experiment and original UCI engine

[**P5 implementation**](../product/c3x_metamorphic_gap_audit.py) · [**P5 correctness tests**](../product/test_c3x_metamorphic_gap_audit.py) · [**real native CI #42922314048 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42922314048).

Two predeclared **illustrative positions**, NOT randomly selected heldout corpus:
- Standard starting FEN, compare `e2e4` vs `d2d4`.
- Chess starting position after legal history `e2e4 e7e5 g1f3 b8c6`, compare `f1c4` vs `d2d4`.

For each board (s), candidate (a,b), construct its semantically equivalent mirror `board.mirror()` and mirror the UCI source/destination ranks with `chess.square_mirror`. Formally, using `M` for vertical-and-color mirror:

```text
g(s,d)  = V_d(s; forced a, POV original mover) - V_d(s; forced b, POV original mover)
g(Ms,d) = V_d(Ms; forced Ma, POV transformed mover) - V_d(Ms; forced Mb, POV transformed mover)
DeltaMirror_d = g(Ms,d) - g(s,d)
```

At each depth `d in {8,10,12}`, both original and mirrored boards undergo **two independently forced Stockfish UCI root analyses**. The source POV is the player who has the turn *in that board*, so white/black swapping doesn't cause a fake score sign inversion. Strict `board.mirror().mirror()` FEN identity and legal-move mirror bijection are checked, as are original forced-root PV identity and real depth/nodes completeness. Chess castling state is transformed by the python-chess library. For finite cp scores, record both candidate cp, their gaps, signed and absolute gap delta, Martin-style relative discrepancy `|g-g'|/(|g|+|g'|)` with zero-denominator case, and literal sign flip. Mate scores are marked separately, not silently converted to centipawns.

**2 positions × 2 root actions × 2 board equivalence variants × 3 depth levels = 24 actual Stockfish native searches**. Source pinned to official Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, NNUE off, one thread, Hash16MB. Actual CI rebuilt upstream source and checked exact commit SHA; unit tests used synthetic engines ONLY to verify contracts. **58 actual test cases passed** in the original P5 CI (P1-P4 + new P5). No independent family was used in this stage.

## 3. Measured source results

All scores centipawns, original move maker's POV. A−B is move A's value minus B's value at the same finite depth. **Delta** measures source engine's transformed gap minus original gap, NOT the statistical impact of a randomized treatment.

| FEN case | Source depth | Original (g) | Mirrored (g') | (g'-g) | Strict opposite-sign |
| --- | ---: | ---: | ---: | ---: | --- |
| Starting e4 vs d4 | 8 | −5 | +18 | +23 | **YES** |
| Starting e4 vs d4 | 10 | −5 | +14 | +19 | **YES** |
| Starting e4 vs d4 | 12 | +14 | +18 | +4 | No |
| After 1.e4 e5 2.Nf3 Nc6, Bc4 vs d4 | 8 | +4 | +26 | +22 | No |
| Same mid-opening board | 10 | −13 | −6 | +7 | No |
| Same mid-opening board | 12 | 0 | +18 | +18 | No (strict-sign check excludes zero) |

**Research conclusion:** The source finite-depth **contrastive** ranking may reverse under an exact legal color-swap/rank-mirror of the same position: starting e4 vs d4 at depths 8 and 10, with those candidate-pair gaps small. At depth12 the two transformed gaps agree in sign and the gap discrepancy reduces to 4cp. The mid-opening case shows non-monotonic behavior. Two chosen boards at three depths **cannot** establish an overall failure rate, a monotonic convergence law, a true chess-theoretic preference, any statistical significant effect, or an engine bug. Martin et al. show that finite-depth search structure and depth choices are critical. Large source-search-depth claims and precise tolerance cutoffs require additional precommitted systematic experiment, preferably with independent engine types and depth/budget controls.

The initial **[CI #42922025090 failed](https://github.com/WhoSia/C3X/actions/runs/42922025090)** only after the 24 actual searches and their output had already completed: the *post-run assertion erroneously assumed JSON object key iteration depth order* `["8","10","12"]` though `sort_keys=True` serialized `["10","12","8"]`. Corrected to compare the exact **set** of depth keys rather than order. **No scientific calculation or source score was changed or fitted to observed results.** Final CI #42922314048 completed all steps SUCCESS.

**Immutable actual native result JSON SHA256:** `ab6fec99e3b19e94b2b58e56e6605f4278ff84e74c04e2485326c723c50753b0`. Artifact ID **13811154304**, archive sha256 `1beece936a8d5633777f4ff2bfc4ad48d473e6a1835af25f5ba786e59e091670`. The CI artifact is stored on GitHub, not claimed to be preserved as Drive original bytes.

## 4. Product integration and strict evidence boundaries

[**P5 native localhost API**](../product/c3x_local_web.py) adds `POST /api/mirror` with the preexisting strict request contract: FEN, legal move A, legal move B. Reject illegal moves **before spawning** actual UCI engine, and use same localhost-only binding/Origin/content-length controls as P3/P4. Each user-selected legal FEN triggers **12 NEW genuine Stockfish forced-root searches** (two candidate moves × original/mirror × three depths) and returns direct observable source data, not cached P5 fixed-board outcomes.

[**P5 browser UI**](../product/c3x_board.html) / [**JavaScript**](../product/c3x_board.js) has a separate opt-in **원본·대칭 국면 12회 실제 재검색** button. It prints original A−B, mirrored A−B, signed change and sign flip across three depths. It never calls this equivalent-board score difference proof of an original root decision's physical causal mechanism. A fresh arbitrary-FEN audit is different from the pre-frozen benchmark JSON and must be labeled as such. This is **not** a third independent chess judge; it is source-only stability auditing.

**Browser visual and actual-click acceptance must be verified separately.** Older P3/P4 Chromium CI green does not retroactively prove this new P5 button. The extended Playwright test now includes click and **actual /api/mirror** native source call, asserts three rendered rows and saves audit JSON plus desktop/mobile screenshots; promotion only after final P5 browser CI success.

## 5. How the additional literature will steer actual software architecture

Martin suggests an **evaluation-stability evidence tier**, not another arbitrary "confidence percentage". Jacovi/Goldberg distinguishes **plausibility/readability** from **decision faithfulness**, so polished explanations must never silently hide root-action reversals. Sandmann et al. explicitly demonstrate the more fundamental mechanistic warning that internal computation can fail to become final behavior; our original Stockfish **search computation → selected root → followup strategic value** claim requires actual within-engine instrumentation and physical intervention, not just explanation text. QUEEN suggests eventual **expert-encoder → structure-guided language generation → verify explained continuation** integration, and Shivkumar suggests a separate validated annotation layer before any natural-language text generation.

This motivates the next practical work unit: **P6 evidence-backed structured commentary** on currently real P1/P2/P4 output (every generated clause traceable to FEN, legal SAN move, exact concept or source engine query); add simple verifiable branch-if–then sentences first, then introduce pretrained model language as an optional rendering layer without giving it permission to alter evidence, and evaluate it with ACT-Eval-style explicit chess claims and independently unseen opponent response continuations. QUEEN and Shivkumar's original complete training/results will NOT be claimed unless genuinely run.

## Hold

- The original exact full Martin benchmark and quantitative threshold calibration **NOT replicated**.
- User learning outcome vs Chess.com/Lichess **NOT measured**.
- Independent arbiter for arbitrary live FEN **NOT implemented** (only earlier pinned Berserk source-leaf court).
- Same-world original Stockfish *physical search computation causing the final choice and robust future plan* **HOLD**.
- Historical prospective 8-game cohort **7/8 HOLD** retained.
- Source winning values/ground truth at unlimited depth **NOT established**.

## 미보유 문헌

The five actually inspected primary papers and the original C3X/Cui previously known papers are **all confirmed present in Google Drive as full original PDFs**. **No newly identified missing research paper this unit.** Data/model weights for original experiments are separate missing assets and are not mislabeled as "missing literature."
