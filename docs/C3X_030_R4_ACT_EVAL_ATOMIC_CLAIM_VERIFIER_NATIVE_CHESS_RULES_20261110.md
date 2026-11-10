# C3X 0.30/R4 — ACT-Eval-inspired tool-verifiable chess atomic claim slice

**Date:** 2026-11-10 KST. **Verdict:** a real, SHA-provenanced original-chess-position run of a deterministic **symbolic claim verifier**, with constructed negative/positive controls. **Not** a replication of the full ACT-Eval language modeling benchmark, expert gold strategic coverage or model behavior.

## Source donor and exact technical scope

- **Original verified owned Drive primary paper:** [Hebbar, Sheng, Oh & Viswanath (2026), *Hallucinations on the Board: Tool-Augmented Evaluation of LLM Chess Commentary* (ACT-Eval), arXiv 2608.04240v1](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view).
- The paper separates **atomic factual correctness**, domain-grounded **tool routing**, expert **gold atom coverage** and move-quality judgments. Its original benchmark comprises 325 position–move pairs and evaluated model-generated chess comments with human comparison; **none of these natural-language-specific datasets or model calls were run in R4**.
- R4 implements ONLY the independently decidable chess-rules-verifiable factual atom checker. The supported typed claims are: `legal_move` (UCI), `move_is_capture`, `move_gives_check`, `piece_on_square` (piece symbol or empty), `square_attacked_by` (white/black) and `white_material_minus_black` (1/3/3/5/9 pawn/minor/rook/queen). Actual legality is checked with pinned `chess==1.11.2`, not guessed from a generative explanation.
- Input schema rejects unexpected fields, malformed UCI, invalid square/color, and nonlegal moves for tactical checks. If a move itself is illegal, `legal_move` can genuinely report false, but for a `move_is_capture` claim the checker **does not silently manufacture a false tactical result** from an impossible move; it raises a fail-closed error.

## Authentic original game and controlled adversarial correctness run

[Implementation](../harness/c3x_030_r4_acteval_symbolic_claim_verifier.py) · [11 tests](../harness/test_c3x_030_r4_acteval_symbolic_claim_verifier.py) · [CI source workflow](../.github/workflows/c3x-030-r4-acteval-atomic-chess.yml).

Source original P37 full legal-history artifact SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`, and pre-referee prediction artifact SHA `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`, were revalidated in the native read-only runner prior to code execution. For the two previously exposed Sahel/Cerrado source games and **their four historically nominated candidate root moves**, the checker evaluates each original board's actual legality, capture and checking status of each selected move.

For **each true board-derived fact**, R4 also constructs a deliberately false *foil* by flipping the expected Boolean value **without changing source game history**. This is a correctness regression, **not a random draw from a real LLM error distribution**.

Actual [SUCCESS GitHub Actions #42748913518](https://github.com/WhoSia/C3X/actions/runs/42748913518):

| Actual test material | Count | Verified as |
| --- | ---: | --- |
| 2 historic original legal prefixes, four root candidate actions, three facts each | **12** | All factual source-derived claims |
| Opposite expected Boolean for each exact same source assertion | **12** | All deliberately constructed false foils |
| **Total original-state atomic tool claims** | **24** | Correctly distinguished by symbolic chess rules |
| Mock/mutated claim unit tests | **11** | All passing, including legal-action, check, capture, attacked square, piece, material and malformed input gates |

Final JSON SHA256 `2de6ad9faaf659bc591cb5b894390b91dd823241834f537ef76f1c7c1e6f7bdd`; downloadable Action artifact ID **13732991253**, artifact ZIP SHA256 `6fda8cd2fb7d588077f7cab71bcdf3c01ce353f52073d112ecc6a8e828d1a7b8`. No new Stockfish/Berserk native searches in R4; deterministic chess rules only in CI.

## 0.29→0.30 methodological continuity

R27 builds executable chess strategies; R28/29 shows many simple static and temporal features fail on independently scored nearby-negative trajectories; R30 constructs source-action attribution and audit interfaces; R3 measures conditional piece attributions on authentic source positions. R4 adds a distinct **factual truth condition** for any future natural-language description: if a statement says that `e2e4` is illegal or that an occupied square is empty, the evaluator must detect that before any strategic-language fluency or plan-utility metric is trusted.

This does not automatically verify commentary about **strategic plans, future best play, piece coordination, or whether the original engine used an explanation**. A future full ACT-Eval replication requires paper-specific 325 cases, claim extraction, LLM tool routing, expert gold atom alignment, and actual human-calibration reporting. R4 is method accumulation, not new interpretability novelty.

## Next direction

The high-value next test is a **masked explanation / foil interface** from [Parfenova original PDF in Drive](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view): insist on removing explicit SAN/UCI candidate-move labels before assessing any generated explanation's move recoverability, and compare explanation-only, FEN-only, random-but-plausible unrelated explanation, and masked/unmasked modes. This will require actual candidate explanations and a decoder or deterministic surrogate; simply creating artificial text with known answers is a pipeline test, not behavioral validation.

Distinct same-world source-computation→root-choice→future-plan natural mediation still **HOLD**. The original 0.29 precommitted source cohort remains **7 eligible of 8 required — HOLD**.

## Drive 미보유 문헌

**None in this R4 report**: original ACT-Eval and Parfenova primary PDFs are confirmed accessible in the user's Google Drive.
