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
