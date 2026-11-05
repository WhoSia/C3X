# C3X 0.29-P41 — Research Director Decision: Primary Papers, Genuine Hard-Value Experiment and Native CI Queue

Date 2026-11-05 KST. **P41 has made primary-literature, mathematics/cost and reproducibility progress but NO source-independent chess-value forecast PASS.** Distinguish written tests from completed CI. GitHub runner jobs 42020782459 (R2/R3) and 42021466003 (R4) currently **QUEUED** at writing, NOT PASS or FAIL. We cannot assert actual new referee scores or newly identified NNUE-mediated choice.

## R1 paper novelty reassessment (read original Drive PDFs)

[Primary-source claim-by-claim matrix](C3X_029_P41_R1_PRIMARY_PDF_PRIOR_ART_MATRIX_AND_MISSING_REGISTER_20261105.md), [missing/unreadable table](C3X_029_P41_MISSING_UNREADABLE_PAPERS_REGISTER_20261105.md). Direct primary manuscripts: Cui Ling Ng 2026 (19zqCJXM631qasR9uIyg4GuBZxIBO7czw), BinProp Press Golubev 2026 (1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6), Jenner 2024 (13QG6G_Ir67Q87Tkb1J9MOMn-TN4Zh63p), Poupart 2024 (1jX9SqJCjdOSqmQ0f0r41L8YXJQCL567Q), Geiger 2025 (1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK), Schut 2025 (1Mg4vfb2t-MIr6juCAzCC1qdv8sq1f8uj), ACT-Eval (1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA), QUEEN (1I1HikAacandg5b75R0zymJlgxAQ41gbG), Ruoss ChessBench (1UBwx4nKx6i12tiHmqYZpAow644_Ts63x), Parfenova (1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R), Nasu 2018 (1zAxUc2M9AOplr3UFbKUrQ5PLcA-dLOwj), Kim et al (1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74), Cui strategy utility and BinProp near-negatives are especially binding.

Important NEW constraint: Cui already sampled off-main-line adversarial responses and measured terminal chess utility; 30-person human study, raw JSON branches frequently outperform prose. Therefore simple reply-aware plans, terminal engine utility, human teaching or JSON branch policies cannot be claimed novel. BinProp already tests near-negative, contrastive executable motifs. C3X must compete against at least **Cui-style strong engine-backed branch JSON**, not a strawman one-reply JSON; match total search and legal-expansion budgets.

## R2 mathematically robust bounded regret

Patched [P40 value-regret calculator](../tools/c3x_029_p40_r4_plan_regret_contract.py) and [tests](../tools/test_c3x_029_p40_r4_plan_regret_contract.py): unknown/one-sided engine score intervals, infinities, NaNs cannot be imputed or produce nonsensical `inf-inf`; absence of independent judge is explicitly `HOLD_NO_INDEPENDENT_VALUE_JUDGE` even when pure math says a plan is low regret. Tests committed; original CI runner [42020782459](https://github.com/WhoSia/C3X/actions/runs/42020782459) QUEUED, no PASS at current read.

## R3 budget feasibility grounded in actual source-native branch ledger

[Original P39/R2 immutable data](https://github.com/WhoSia/C3X/actions/runs/41993256831) (SHA256 `84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf`) has 8 exposed games, 16 roots, exactly 644 opponent first replies, 24,894 own legal continuations and 25,554 total legal action expansions. 96k nodes per own continuation would request exactly **2,389,824,000 total nodes** for one engine family before reruns, baseline budget and CPU. This is arithmetic projected requested search nodes, **not actual engine usage**. No full universal plan-value pilot should be launched without resource gate. One preregistered strong opponent counterexample suffices to falsify a universal low-regret claim, while a sampled response subset cannot certify universal robustness. [Original-source cost audit](../tools/c3x_029_p41_r3_original_branch_cost.py), [tests](../tools/test_c3x_029_p41_r3_original_branch_cost.py), CI QUEUED same run as R2.

## R4 independent engine receipt technical eligibility gate

[Code](../tools/c3x_029_p41_r4_judge_receipt_gate.py), [tests](../tools/test_c3x_029_p41_r4_judge_receipt_gate.py): exact original chess UCI move history, FEN, root/counter-reply/own move legality, PV, true consumed nodes ≥90% requested, depth≥3, family/source commit/binary and network digest, viewpoint and score-bound labels. Historic P38 Ethereal 2–5-node/depth1 outcomes are rejected by the gate, but no independent referee was actually validated yet. Passing a JSON receipt does NOT prove family independent nor true chess value. [Read-only CI 42021466003](https://github.com/WhoSia/C3X/actions/runs/42021466003) QUEUED at record time, not PASS.

## Hard scientific target remains unchanged; proposed P41/R5→P42

Freeze a **single challenging near-equal move-pair and ONE opponent response selected independently of outcome labels**, carry forward all parent game history. For technical proof of value quality, use a genuine separate family judge that first passes full source/binary/network provenance and native node consumption on an end-to-end chess-world receipt. Then test an explicitly selective plan P, a matched-cost Cui-like JSON branch strategy and full Stockfish PV against independently verified conditional value. A single certified response with regret > threshold refutes universal plan robustness; a failure to find one is HOLD. Never substitute a shallow material/mobility proxy. For any positive claim, require a subsequently frozen historically game/event-disjoint cohort and full response guarantee or explicitly bounded scope. NNUE mediation remains separate until source-native causal intervention.

## Missing / source quality

Sandmann, Lapuschkin & Samek exact v4 paper updated 2026-10-29 (arxiv:2508.21380) is not located in bounded Drive search: MISSING, not read. Gobet & Simon 1996 PDF is held but extracted text is only 425-character repeated watermark: content unreadable. Ruoss ChessBench IS held under its correct title and was read; do not mark missing. All source filenames, IDs, status in P41 missing register. No claim of global completeness.

## Execution governance

GitHub author/committer WhoSia, bot-author commits forbidden; Actions `contents:read` source and read-only tests, no repository mutation. Notion semantic meaning, Drive original PDF raw bytes, GitHub paper audit and executable version history. **Scientific judgement: R1 literature complete for specifically checked papers; R2/R3/R4 implementation evidence available, CI results queued, independent value/novel explanation still HOLD.**