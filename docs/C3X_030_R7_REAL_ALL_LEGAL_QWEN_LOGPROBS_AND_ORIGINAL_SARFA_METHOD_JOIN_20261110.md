# C3X 0.30/R7 — Real Qwen All-Legal UCI Token Probabilities and SARFA Prompt-Effect Integration

**Version:** C3X 0.30 — Mechanistic Strategy Reconstruction: Prior-Art Replication, Decision Tracing & Counterfactual Plan Evaluation. **Recorded:** 2026-11-10 KST. **Status:** **two original-source-anchored actual-model analyses executed in read-only GitHub Actions**, with distinct prior-art methods faithfully isolated. **DO NOT PROMOTE to chess engine source-computation causality, independently solved Lichess puzzles, or full human explanation faithfulness.**

## I. Methodological basis: two actual owned original PDFs

**Primary 1 — [Angelina Parfenova (2026), *Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness*, original full Google Drive arXiv 2609.22245v1](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view).** Original: independent decoder recovery, **complete legal action-set token log-likelihood**, 200 Lichess endgame puzzles with model-generated action vs gold reference action, strict/maximal lexical masking, independently generated actual explanations and other-puzzle explanations, multiple large decoders. Original's sum of all candidate tokens' log likelihood motivates R7; R7 is NOT its full benchmark reproduction.

**Primary 2 — [Puri et al. (2020), *Explain Your Move: Understanding Agent Actions Using Specific and Relevant Feature Attribution* (SARFA), ICLR 2020, original full Google Drive arXiv 1912.12191v4](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view).** Equations (1)-(4) motivate R7-C: selection probability shift, other-action KL, relevance and their harmonic combination. Its original Chess/Go/Atari evaluations are NOT repeated. **R1's tested log-domain SARFA implementation** is reused without silently reinterpreting chess cp as a source-agent behavior.

## II. Exact inherited materials and forward-only data boundary

The 0.29 source-only P37 original game artifact and earlier predictions are byte-frozen; R5 created five **per-arm blind** FEN/explanation JSONs from two historically exposed chess positions (Sahel and Cerrado) and four originally nominated source root moves, **two targets per board**. The original R5 truth audit SHA is `4221f90ed5ab86ef38b05e47d248f5906048c7c5812d0430c2c48fc680760f0b`; the R5 FEN-only BLIND SHA is `3709dd687f468170af80446f7ebe853b51328a866161c572597b96abf0504bbc`.

R7 first freezes **all legal UCI action options** from **FEN-only BLIND** input, with no targeted candidate or game identifiers. [`r7s_blind_all_legal_support_freeze.py`](../harness/c3x_030_r7s_blind_all_legal_support_freeze.py). Exact supported legal move counts for the four rows are **[43, 43, 36, 36]**, i.e. **158 candidate strings per condition × 5 conditions = 790 real teacher-forced candidate UCI evaluations**. The first two and last two represent repeated target labels on the same underlying board; those pairs are NOT independent observations.

R7 model scoring does not read the reference/target audit. Each arm is processed in a fresh Python/model invocation; each candidate is evaluated with a fresh **clone of the exact same original prompt KV cache**. The **explanation-only arm's candidate set is still constrained by the separate original FEN-only BLIND support, but the model prompt itself does NOT contain that FEN**. Thus its rank is conditional on experimenter's separate choice set; it is **not** unrestricted evidence of explanation-only free-form chess reconstruction.

The source sample was historically selected/inspected before this work. **No prospective or held-out generalization claims.**

## III. R7-A/B — ACTUAL open model, complete legal action token likelihood

- [Actual source scorer](../harness/c3x_030_r7a_real_qwen_all_legal_token_scorer.py), [posthoc target rank evaluator](../harness/c3x_030_r7b_posthoc_all_legal_rank_evaluator.py), [10 regression tests](../harness/test_c3x_030_r7_all_legal_likelihood_contracts.py), [read-only workflow](../.github/workflows/c3x-030-r7-all-legal-qwen-scores.yml).
- Same **genuinely executed** CPU model from R6: [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), pinned SHA `7ae557604adf67be50417f59c2c2f167def9a775`, torch 2.5.1 CPU, transformers 4.47.1. Qwen2.5 0.5B is NOT original Parfenova's Qwen3 32B or Llama 70B.
- R6 actual original chat template/prompt and model configuration reused. Every legal candidate `u` is tokenized precisely as **`tokenizer.encode(" "+u, add_special_tokens=False)`**, after identical R6 assistant-generation prefix; **no EOS** scored. This leading whitespace and tokenization policy materially affects absolute ranking. The primary score is **sum of conditional log-probabilities** over the UCI continuation; a second **per-token mean** ranking is solely a sensitivity measure for token-length bias, NOT an original sequence likelihood. Equal scores tie-break by UCI lexicographic. Each subsequent token is teacher-forced, not generated. The whole exact legal action list is scored, with no beam/truncated subset.
- All five independent model score files are written AND hashed **BEFORE** a distinct posthoc process opens the truth-bearing audit and computes historical nominee rank. All support and source SHA checks were completed before first inference.

### Genuine execution receipt and preserved failures

Initial [R7 CI #42779114022 FAILED](https://github.com/WhoSia/C3X/actions/runs/42779114022): a synthetic boundary test erroneously supplied a noncanonical audit SHA for its second fail-injection invocation; **production audit SHA gate was never relaxed**.

Second [R7 CI #42779206805 FAILED](https://github.com/WhoSia/C3X/actions/runs/42779206805): real pinned Qwen returned legacy tuple cache on first forced continuation while the new scorer required dynamic-cache `get_seq_length`. Corrected to explicitly create a `DynamicCache`, test valid prefix cache length, and deep-copy it for each subsequent **independently forced candidate continuation**. No successful model score from that failed execution was presented as a result.

**[R7 final genuine Qwen all-legal CI #42779413096 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42779413096)**. Ten tests passing, SHA-original materials verified, full 790 actual UCI string probabilities computed, and the separate posthoc target evaluator passed.

| Five independent input arms | Original R6 strict free-generation top-1 nominee match | R7 summed UCI-logprob top-1 | R7 top-3 | R7 mean-token-logprob top-3 |
| --- | ---: | ---: | ---: | ---: |
| `fen_only` | 0/4 | **0/4** | **0/4** | **0/4** |
| `explanation_only` | 0/4 | **0/4** | **0/4** | **0/4** |
| `fen_plus_unmasked` | **3/4** | **4/4** | **4/4** | **4/4** |
| `fen_plus_strict_masked` | 0/4 | **0/4** | **0/4** | **0/4** |
| `fen_plus_unrelated_foil` | 0/4 | **0/4** | **0/4** | **0/4** |

Actual R7 FEN-only Top-3, Sahel: `g2g4, g2g3, c1e3`; Cerrado: `e2e4, g2e4, c1c4`. In the masked arm, Sahel: `g2g4, g2g3, f2f4`; Cerrado: `e2e4, g2e4, c1c4`. These *ranks are actual Qwen outputs*, not engine move recommendations, independent judge values, or original chess solution choices. For every unmasked historical target, the R7 Top-1 equals its exact exposed UCI (`e5f4, e5c3, e5f6, d1c2`). The R6 free-generation parser did not recover `e5f6` while its R7 target rank was first.

**R7 final posthoc top-k JSON SHA256** `af821bdeaf15f48631a063d69bfd9d241aeb06c42d5c7eb50f1c657a54530bab`. Archived native Action artifact `c3x030-r7-real-Qwen-ALL-legal-five-arm-token-likelihood`, id `13745222726`, archive digest `sha256:75ae5051677271d4f2f80e0d84c18a5fb5cb17ada309bf3834a13f7d17c76431`. Includes all five **complete actual UCI score vectors**, not merely Top-3.

## IV. R7-C — source-original SARFA Eq.1–4 on these REAL source-blind model logits

- [Implementation](../harness/c3x_030_r7c_sarfa_on_real_qwen_explanation_prompt_contrast.py), [8 exact-method interface tests](../harness/test_c3x_030_r7c_sarfa_actual_model_prompt_contrast.py), plus 10 inherited R1 SARFA tests, [read-only CI](../.github/workflows/c3x-030-r7c-real-model-sarfa.yml).
- All **five exact R7 real-model output JSON SHAs** and original R5 label audit SHA are re-verified before treatment comparison. **NO NEW model inference** is claimed in this R7-C step; it reuses actual empirically executed R7 likelihoods. The source input record and complete original 36/43 legal action set are unchanged for each paired arm.
- For original full-board `fen_only` model logits \(q_0(a)\) and explanation arm logits \(q_e(a)\), use the **source-original SARFA** implementation with **treated explanation = original** and **FEN-only = perturbed control**. Treating temperature as **1 in model log-score units** makes \(P_e(a) = \exp q_e(a)/\sum_{b\in A} \exp q_e(b)\). Selected probability increase \(\Delta p = P_e(a^*)-P_0(a^*)\). Off-target relevance \(K=1/(1+D_{KL}(P_0(-a^*)\Vert P_e(-a^*)))\), and positive SARFA \(2K\max(0,\Delta p)/(K+\max(0,\Delta p))\).
- **Important:** This `P_e` is normalized only over **legal-UCI continuation strings under a fixed experimentally chosen textual encoding**. It is not unrestricted actual model free-generation probability nor original Stockfish behavior. Changing the prompt text is a legitimate **LLM input intervention** but NOT an intervention on the source engine's physical search or a proof of original C3X chess plan mediation.

Initial [R7-C #42780603680 FAILED](https://github.com/WhoSia/C3X/actions/runs/42780603680), second [#42780708619 FAILED](https://github.com/WhoSia/C3X/actions/runs/42780708619): transitive chess-package imports from older scoring/audit modules for two constants broke an intentionally pure-Python math workflow. Removed transitive imports, pinned explicit exact schema+source SHA and tested without `python-chess`; production source hash checks were not weakened.

**[R7-C final CI #42780731162 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42780731162)**, 18 numerical/source-interface regression tests green, all five original R7 source JSON SHAs verified, actual SARFA method applied.

| Treated LLM explanation arm relative to FEN-only | Cases with strictly positive target choice-probability change | Actual observed magnitude |
| --- | ---: | --- |
| `explanation_only` | 3/4 | Extremely small changes, many effectively zero |
| `fen_plus_unmasked` | **4/4** | **Very large** increases \(\Delta p\approx[0.998992, 0.977514, 0.999706, 0.977658]\) |
| `fen_plus_strict_masked` | 2/4 | At most around \(10^{-6}\) positive; near-zero, no practical move-ranking recovery |
| `fen_plus_unrelated_foil` | 3/4 | Extremely small changes |

For unmasked direct-label cases, **actual SARFA saliency** \([0.243361,0.181775,0.491875,0.770345]\), less than the raw \(\Delta p\) in cases where many nonselected action probabilities shift; measuring **other-action relevance** rather than mere Top-1 correctness matters.

**Sign count (2/4 vs 3/4) in the effectively numerical-zero arms is NOT evidence of an explanation improvement.** This is the major conclusion from the cross-method exercise: a lexical label can produce huge candidate preference changes without proving semantic faithfulness, and a few mathematically positive micro-changes must not be called human-meaningful. The real-model SARFA treatment moves input text in an LLM, not the internal original source chess engine.

R7-C result JSON SHA `2215e49b14cdc4c2d6a7d55ae00ed59743d716706d246bb0105f76f283d50d39`. Artifact id `13745268337`, ZIP digest `sha256:f02e468741a0977c38860f4ece50d7ef1e77f46e1ac30e634bac0cdc66e89309`.

## V. Required methodological next steps (beyond present tiny-data pilot)

1. **Tokenization sensitivity**: leading-space vs no-space candidate suffix, EOS include/exclude, UCI length dependence; raw probabilities are only comparable under frozen consistent candidate representation. The per-token mean sensitivity Top-3 counts were stable here, not necessarily for another encoding.
2. **Natural explanation acquisition and independent controls**: authentic generated chess explanations, best puzzle reference vs generated move, unrelated foil sampled from a pre-frozen distinct puzzle corpus, independent held-out 200-puzzle original test. The current four source nominees on two repeated chess boards were retrospectively selected and constructed into synthetic commentary: cannot support any general significance.
3. **Strong explanation methods**: Cui real multi-layer plan and BinProp nearby negatives vs ACT-Eval factual tool truth, with actual held-out user evaluation. Do not confuse better label recovery with source calculation explanation.
4. **Original chess mechanism A+B+D+F join**: physical source Stockfish search/NNUE intervention → observed final original root action → independently valued response-robust contingent future plan on the SAME position/history is still **HOLD**, as inherited from 0.29. Previously preregistered new eligible-game source gate **7/8 HOLD** is immutable. Never infer this causal link from current language model prompt effects.

## VI. Governance and methodological release assurance

GitHub human-authored commits, no GitHub-Actions[bot] code writes. Both scoring workflows read-only `permissions: contents: read`, checkout `persist-credentials: false`. Original PDF citation prefers Drive copies. GitHub records source code, failures and machine receipts; Notion semantic scientific judgments; Drive original PDFs/raw source bytes only when actually verified. Never claim original raw PGN uploaded to Drive merely because GitHub Action artifact exists. R7-A reuses pinned chess 1.11.2 on read-only runner only, R7-C stdlib alone.

## Drive 미보유 문헌 표

| Original primary work directly cited | Drive ownership |
| --- | --- |
| Parfenova (2026), arXiv 2609.22245v1 | **원문 보유 확인** |
| Puri et al. (2020), SARFA arXiv 1912.12191v4 | **원문 보유 확인** |
| Hebbar et al. (2026), ACT-Eval (R4/R5 inherited) | **원문 보유 확인** |

**실제 미보유로 확인된 문헌 없음.** Original Parfenova's 200-puzzle *dataset* and other large *decoder model weights* are different acquisition categories, not unowned citations.
