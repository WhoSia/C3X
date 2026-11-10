# C3X 0.30 — Mechanistic Strategy Reconstruction: Prior-Art Replication, Decision Tracing & Counterfactual Plan Evaluation

**Version opened:** 2026-11-10 KST. This is the accepted full version name, not a provisional alias.

**Scientific canonical page:** [Notion C3X 0.30 Master](https://app.notion.com/p/414ef561cf92813e8186fa51f780ee55)

## Nonfragmentation and predecessor inheritance

C3X 0.29 is not discarded. This document specifies how to **reuse methods, data, negative outcomes, and exact experimental receipts** across the version boundary without relabeling any past science. R24–R30 of 0.29 remain immutable in historical naming and original commit receipts. Their source code is not retroactively reversioned.

- The real root question is **whether an original engine's executed computation causes a final first-move selection because it carries information about a future executable plan that survives diverse opponent responses**, on **the same legal full history**.
- **A** source search interventions (Game14), **B/E** recursive source contingent opponent policy and independent Berserk reference (historical Sahel/Cerrado), **D** NNUE/classical representation (historical P34) are currently different games and cannot be conflated into **F** same-world mediation.
- A prior untouched official Lichess broadcast cohort with a frozen **8-eligible-game** criterion returned only **7** qualifying games, twice the same original-source SHA (52,773 bytes). It remains **HOLD**, not a stealth 7-game validation.
- C3X 0.29 prior R27: original source 4 roots, 2 opponent layers k3, 36 real four-ply contingent paths, 64 source searches. R27 J1 judged 36 leaves at two depths (72 searches), showed off-PV worst-path shifts. Cui already introduced the principle; no novelty credit claimed.
- C3X 0.29 prior R28/29: BinProp-inspired 12 same-prefix nearby negatives, 8 static and 8 tactical path features mostly failed; no generalized success.
- C3X 0.29 prior R30: SARFA equations 1–4 verified with 25 synthetic A/B/C contract tests, 24 real Stockfish forced-root searches/256,560 nodes in **unreachable-piece-deletion method pilot**. Sandmann staged-choice observation contract and Ciancarini nine-stage source audit; historical same-state final-action causal strategic promotion **0/3**.

Original predecessor receipts: [0.29 R30 canonical report](C3X_029_P42_R30_DRIVE_00_TO_10_PRIOR_ART_IMPLEMENTATION_SARFA_SANDMANN_MAPPING_20261110.md) · [Notion 0.29 R30](https://app.notion.com/p/414ef561cf9281dbbebfc8cad2823d2d).

## Primary paper custody, before code

| Method donor | Verified original PDF in user's Google Drive | Implementation scope |
| --- | --- | --- |
| Cui et al. 2026 | [Primary PDF](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) | R27 recursive two-level tree only, full verbalization and puzzle player pending |
| Press & Golubev BinProp | [Primary PDF](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view) | R28/29 nearby negatives and fixed features only; complete LM concept discovery pending |
| Puri et al. SARFA ICLR2020 v4 | [Primary PDF](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view) | R30 original math and chess engine method pilot; 0.30 R1 stable exact kernel |
| Sandmann et al. v4 | [Primary PDF](https://drive.google.com/file/d/1dAF7reY9DpwBlZFERxrF54qSNYOLbRi0/view) | 0.29 staged-choice contract; Leela activation and steering pending |
| Ciancarini & Pareschi v1 | [Primary PDF](https://drive.google.com/file/d/1OxYGSk2bmFD4Rdr0tXHJPAWT_w-wkMyF/view) | R1–R9 classification-derived evidence ledger; full mapping study not reproduced |
| Spinnato 2025 piece SHAP | [Primary PDF](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view) | 0.30 R2 exact finite-coalition Shapley math, not paper's complete SamplingExplainer chess experiment |
| QUEEN 2026 | [Primary PDF](https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view) | Interface/decoder and evaluation method reproduction to design |
| Parfenova 2026 | [Primary PDF](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view) | Masked move / mismatched plausible narratives reproduction to design |
| Hebbar et al. ACT-Eval 2026 | [Primary PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) | Tool-based chess explanatory fact checking to design |

The original 00 folder MUST be searched before declaring missing source. Three paper PDFs (SARFA, Sandmann, Ciancarini) were previously incorrectly labelled missing but have been read, renamed and moved with identical IDs into `10_PAPERS`. Cite original owned PDFs first, append a missing-literature table at the END.

## Versioned 0.30 actual implementations

### R1 — R30-A SARFA log-domain numerics correctness

- **Source:** [original owned Puri et al. ICLR2020 PDF](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view), equations 1–4.
- **Core implementation:** [`harness/c3x_030_r1_sarfa_logdomain.py`](../harness/c3x_030_r1_sarfa_logdomain.py) · [10 tests](../harness/test_c3x_030_r1_sarfa_logdomain.py).
- **Actual read-only CI [SUCCESS #42747118216](https://github.com/WhoSia/C3X/actions/runs/42747118216)**, only Python 3.12 stdlib, no `python-chess`, no chess engine.
- Reproduces R30-A original positive specificity, off-target relevance and harmonic SARFA results on ordinary Q vectors.
- **Concrete original R30 math defect demonstrated:** for off-target Q scores `b=0,c=-1000` changing to `b=-1000,c=0`, the old probability-domain KL underflowed `P(c)` to numerical zero, returning `+inf`. The log-domain evaluator correctly returns finite **KL≈1000** while preserving same fixed support. In general underflow support is a floating-point artifact, not genuine probability support change.
- Always report temperature, explicit Q units, signed probability drop, independent source-action score support; underflow fix **not** empirical chess explanation improvement.
- This does **not** rewrite/deprecate R30 native paper pilot receipts. They remain scientifically intact at their original scope.

### R2 — Spinnato piece-wise Shapley exact small support

- **Source:** [Spinnato 2025 owned original](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view). Original uses piece-wise feature removal, king-only neutral baseline 0.5, chess engine evaluation and SHAP SamplingExplainer with bounded samples. Removing chess pieces is not a legal chess-world transition.
- **Core implementation:** [`harness/c3x_030_r2_exact_piece_shapley_kernel.py`](../harness/c3x_030_r2_exact_piece_shapley_kernel.py) · [8 tests](../harness/test_c3x_030_r2_exact_piece_shapley_kernel.py).
- **Actual read-only CI [SUCCESS #42747317750](https://github.com/WhoSia/C3X/actions/runs/42747317750)**, stdlib only; no physical chess runtime installation in chat.
- Given every subset's declared scalar value for `n<=12` distinct piece features, compute mathematically exact Shapley `phi_i = Σ_{S not containing i} [1/(n C(n-1,|S|))](v(S+i)-v(S))`. Verify total `baseline + Σ phi = v(all)`; detect omitted subsets, duplicate names, nonfinite values, interaction symmetry and negative contributors.
- **Synthetic two-piece pure synergy** `v(∅)=v({a})=v({b})=0, v({a,b})=6` gives **phi(a)=phi(b)=3**. No chess model and no source code causal decision argument in this example.
- Original Spinnato's Stockfish17.1/SHAP SamplingExplainer 10,000-perturbation chess benchmark, legal-state repair, piece feature removal and chess pedagogical explanation have **not** been replicated. Exact mathematics on supplied coalition values is a robust foundation, not a shortcut to claiming a full paper replication.

### R3 — Real pinned Stockfish16 + Spinnato-inspired *conditional* 3-piece SHAP

- Original primary [Spinnato 2025 Drive paper](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view), legacy original piece-ablation caveats.
- [Source-native chess coalition builder](../harness/c3x_030_r3_native_stockfish_conditional_piece_shapley.py), [9 mock/legality tests](../harness/test_c3x_030_r3_native_stockfish_conditional_piece_shapley.py), [R3 genuine CI #42748378432 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42748378432), also inherited R2's 8 tests (total 17). First CI #42748289909 FAILED due to `Mock.side_effect` precedence in a depth boundary fixture; repaired without modifying evidence or source admission rules.
- **Two existing authentic historically selected chess worlds, 8 combinations of 3 legally removable pieces each, 16 genuine original Stockfish16 depth10 analyses, 168,167 nodes**. Source chess archive and forecasts hashes verified. Exact conditional Shapley additive sum computed over each 8-combination complete score table.
- Sahel chosen `a1:R,c1:B,f1:R`, no selected pieces white-win logistic proxy 0.0378798511 vs full 0.5531583435; native 81,581 nodes. Cerrado chosen `c1:R,d1:Q,f1:R`, conditional baseline 0.0151155546 vs full 0.4926405315; native 86,586 nodes. Both are heuristic cp-logistic proxies, **not calibrated actual win probabilities**.
- JSON SHA256 `5bab62f215795766530798d82825ad6f452f552355c9d5bda60add860b4a2a66`, artifact ZIP SHA `7ce842ae52c87d120b0b1238a3903411bff2116dc26a45dfa034d69d7f88fdf7`. Detailed [R3 scientific report](C3X_030_R3_GENUINE_STOCKFISH_CONDITIONAL_SHAPLEY_AND_ACT_EVAL_FOLLOWON_20261110.md).
- **Paper-replication boundary:** other pieces are held FIXED rather than original full nonking-piece game (king-only baseline), and original used Stockfish17.1/SamplingExplainer up to 10k. Piece removals aren't guaranteed reachable game histories; historical data already exposed, no source root choice causation, no model user study.

### R4 — Hebbar et al. ACT-Eval symbolically checkable chess atoms

- Original primary [Hebbar et al. 2026 ACT-Eval Drive PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view).
- [Six-type typed factual verifier](../harness/c3x_030_r4_acteval_symbolic_claim_verifier.py), [11 regression tests](../harness/test_c3x_030_r4_acteval_symbolic_claim_verifier.py), [R4 genuine original-state CI #42748913518 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42748913518). Two real SHA-frozen original legal histories, four candidate roots, their legality/capture/check statements and deliberately inverted claims, **12 source-derived true atoms + 12 constructed false foils = 24 exact checked facts**. No chess-engine new searches. JSON SHA `2de6ad9faaf659bc591cb5b894390b91dd823241834f537ef76f1c7c1e6f7bdd`, artifact ZIP SHA `6fda8cd2fb7d588077f7cab71bcdf3c01ce353f52073d112ecc6a8e828d1a7b8`.
- [R4 detailed scientific report](C3X_030_R4_ACT_EVAL_ATOMIC_CLAIM_VERIFIER_NATIVE_CHESS_RULES_20261110.md). **Not the full 325-case ACT-Eval model-generated chess commentary, gold strategic coverage, LLM claim extraction/tool routing or human calibration**. Constructed false foils are deterministic integrity tests, not evidence of naturally occurring LLM hallucinations.
- Next reproductions: Parfenova move-masked, FEN-only/explanation-only and unrelated-foil protocols; actual move recovery from separate decoder, not invented paraphrases.

### R5 — Parfenova masked explanation controls and ACT-Eval verified real history

- [Original held Parfenova 2026 v1 PDF](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view). [Full R5 report](C3X_030_R5_PARFENOVA_LEXICAL_MASK_AND_ACTEVAL_BLIND_ARM_PROTOCOL_20261110.md).
- [Masking and five-arm builder](../harness/c3x_030_r5_parfenova_move_mask_control_protocol.py), [24 R5+R4 tests](../harness/test_c3x_030_r5_parfenova_move_mask_control_protocol.py), [**CI final SUCCESS #42755543672**](https://github.com/WhoSia/C3X/actions/runs/42755543672).
- Real original P37 SHA-locked legal 2-game source histories; 4 source candidate root moves, **20 condition packets**. Arms: FEN-only, explanation-only, unmasked, regex-masked, unrelated foil sourced from other game; all explicit move legality, capture/check conditions verified by inherited R4 ACT-Eval chess-rule checker. Artificial commentary is generated by a simple deterministic template with UCI/SAN, **not** a language model.
- Important real engineering discovery: do **not** give a decoder a single JSON containing BOTH reference move labels and masked/unmasked arms. R5 now exports **five distinct blind decoder-only JSON files** (only FEN/explanation per entry, no target case/candidate labels) and keeps a separate truth-bearing scientific audit. Decoder contexts MUST remain isolated between conditions; files themselves are not a decoder experiment.
- Final audit JSON SHA `4221f90ed5ab86ef38b05e47d248f5906048c7c5812d0430c2c48fc680760f0b`; artifact ZIP SHA `e019640a754e8e4189931d039bd08ba7adc39582dcb5d8d53efe8697e87a9976` (artifact ID 13735083135). Intermediate CI [#42755482606 FAILED](https://github.com/WhoSia/C3X/actions/runs/42755482606) because workflow didn't yet pass newly mandatory `--decoder-dir`, then repaired and final CI passed.
- **Not reproduced:** Parfenova original 200 puzzles, actual generated explanation corpus, independent decoder and token scorer, measured recovery/accuracy or faithful engine reasoning. Regex masking is a lexical approximation not semantic blindness. Original C3X same-world physical causal mediation and 8-game cohort still HOLD.

## Evidence protocol and truthful promotions

Declare distinct engineering/evidence states: `READ`, `SPECIFIED`, `IMPLEMENTED`, `SYNTHETIC_TESTED`, `SOURCE_NATIVE`, `INDEPENDENTLY_JUDGED`, `PAPER_BENCHMARK_REPRODUCED`, `PROSPECTIVE`, `CAUSAL`. No automatic upgrade. Each module must retain paper version and source Drive ID, honest adaptation, unit tests, CI result, negative controls, native input bytes, quantified compute when available, failed attempts and explicit unproven mechanisms.

Source-only actions shall run in read-only GitHub Actions `permissions: contents: read` with original-source SHA and pinned dependencies. Never reinstall `python-chess` repeatedly in Chat ephemeral runtime. Github source: human `WhoSia` commits only; no GitHub-Actions[bot] source writes. Notion=semantic scientific master, Drive=original PDFs and verified raw byte custody, GitHub=code and CI evidence.

## Immediate project route

1. Implement Spinnato piece-value coalition capture from actual native Stockfish on a small stable position and a declared finite set of pieces; preserve invalid subset policy instead of silently imputing. Only then compare to SARFA under a common **source scoring contract**; note SHAP attributes piece value and SARFA attributes selected-action probability are different estimands.
2. Extend Cui beyond the existing two opponent layers toward the original paper's full puzzle-play protocol and verbalization control. No misleading 'full Cui' claim.
3. Add BinProp's actual concept-proposal / near-negative rejection loop and Parfenova's masked/mismatched explanation controls.
4. Reuse inherited R20 A/G14 intervention evidence, R27 policies, R30 native SARFA pilot to design an **original SOURCE-WORLD joined intervention**, not fabricated same-world equivalence across games.
5. Obtain genuinely qualified new original PGN, respecting immutable 8-game C gate or a separately preregistered future event.

## Drive 미보유 문헌 표

No missing primary article among the nine directly cited primary papers above, all individually supported by a known existing Drive PDF. Check new titles using `00`, `10_PAPERS`, exact arXiv and version patterns before changing this table.
