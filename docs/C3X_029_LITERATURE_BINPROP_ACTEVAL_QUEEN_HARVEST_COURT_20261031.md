# C3X 0.29 — Literature Court: BinProp, ACT-Eval, QUEEN, CCC, Cui and Harvest Backflow
Date: 2026-10-31. SOURCE-LEVEL READING AND SCIENTIFIC DESIGN ONLY, not a head-to-head empirical benchmark.

## Custody verification
Two PDFs were explicitly read from connected Drive, renamed in place, moved from original parent 1MLtYh0pv8QUZDReYzRqjDrOjRkSJAD16 to verified 10_PAPERS root 1D2M4LHcejREhlyp6vTd71xxLLx-6ldUP; metadata reread confirms exact parent and title. IDs unchanged:
- 1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6: Press & Golubev (2026), Explaining Chess and Go in Natural Language - BinProp, arXiv 2610.23166v1 (source title/author abstract checked).
- 1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA: Hebbar, Sheng, Oh & Viswanath (2026), Hallucinations on the Board: Tool-Augmented Evaluation of LLM Chess Commentary, arXiv 2608.04240v1.
Review is extracted-text and selected method/results/limitations sections. Figure/printed-layout and full reproduction NOT independently audited.

## Paper-specific source claims and experimental contrasts
BINPROP: Original PDF introduction and Sections 2–4. Binary board predicates, engine-grounded evaluation from Stockfish18 plausible continuations, 100 starting chess positions, 12 positives+12 negatives+8 nearby negatives per root. Nearby negative shares a good-move search prefix then deviates, challenging uninformative board correlates. Position-selection criterion places preferred move at +75..+125 cp and alternatives at -125..+50, requiring >=75 cp score gap; its core task therefore is NOT the small near-equal marginal preference of original C3X, although both share contrastive motif discovery. BinProp generates Python motifs and validates across positive/negative/nearby-negative positions, ranks up to 3. Source table mean: Qwen3.5 0.102→0.174, GPT-5.6 Sol 0.062→0.205, DeepSeek-V4 0.173→0.214, Fable5 about 0.031→0.296. These are paper-specific engine-grounded scores, not human pedagogical improvement or strict causal attribution to Stockfish internals. Key rival to C3X is robust counterfactual concept discovery, not merely language fluency.

ACT-EVAL: Original PDF abstract, Introduction, Section 3, Section4.2, 6.2/Limitations. 325 position-move pairs, 125 expert gold atoms, atomic factual correctness, coverage against expert atoms, move-quality distinction, engine-backed tools; backend Stockfish14.1 depth18 (source section). Untooled GPT-5.4 subclaim error 22%; tool ablation on 29 confirmed errors misses 21% with tools versus 48% no-tool. This is a *test of a commentary judge*, not a generator whose human learning gains are established; source's fixed tool coverage is nonexhaustive. Match baseline and same evidence before claiming C3X advantage.

QUEEN: Bhaskar/Cheng/Chen 2026 4B encoder-decoder with domain-adapted chess QA + iterative natural-language Bellman-like distillation; source-reported 1782→2697 Elo in its evaluation, not FIDE or C3X comparable. Explanation fluency/coherence and game competence are different dimensions from source-causal explanation. Strong production/model rival, not automatically a test for C3X causal fidelity.
CCC: Kim et al. original 2024 preprint, expert chess concept guided commentary and GCC-Eval with human evaluations. 2026 ACT-Eval exposes possible high GCC-Eval ratings for hallucinations. Important distinction: strong concept and fluency baselines must be evaluated for atom-true correctness.
Cui/Ling/Ng 2026: strategy verbalization tested for off-main-line and human effectiveness; source says natural language often worse than uncompressed JSON strategy representation. C3X P5/P6 compression may reduce machine-executable information; NEVER equate succinct prose with superior strategy conveyance.

## Harvest genealogy and authority hygiene
Read existing Research OS Harvest Citation and Provenance Audit 2026-10-17, Harvest Citation Exhaustive B01 and Harvest_LR-20260905-A.md.
Authority C0 unknown source; C1 metadata; C2 abstract/front matter; C3 source passage with locator; C4 independently examined limitations/counterexamples; C5 independent external replication. Reading PDF alone never C5. Preserve claim-level source locator, baseline, transport caveat. Archive/Notion Harvest XII duplicate namespaces, no blind summation. Literature carry-over is an ANALOGY/inference unless experimentally tested in C3X. Weyuker 1983 distinguishes adequacy of test set from passing test; Kuhn 1999 specifies detection conditions, not universal completeness; adapting these ideas to chess commentary testing is a proposed engineering principle not original authors' empirical claim.

## Important recovered scientific distinction
BinProp mostly selects positions with >=75 cp preferred-to-alternative gap. The *founding C3X marginal near-equal* target is not simply BinProp's benchmark. That is a narrow research niche but NOT superiority by itself. Need compare on exactly matched positions and engine budgets; avoiding easy large-gap near-zero explanation cases is potential advantage only if measured.

## Concrete new research competition (preregister before results)
Trial A: Feed the SAME fixed legal candidate pair and exact board history to R0 score/PV, R1 CCC concepts, R2 BinProp binary motifs, R3 C3X joint-policy proof/refuter. Equalize engine effort and available continuation samples. Disclose which tasks each approach can perform rather than force artificial outputs.
Trial B: two strata: original strict near-equal candidate root and BinProp-like >=75cp-gap candidate root. Predeclare stratification; game-disjoint fresh holdout. Evaluate concept discriminativeness, logical claim correctness vs full declared legal reply domain, nearby-negative robust pass rate, response coverage/abstention, compute budget, and expert human understanding as separate outcomes.
Trial C: Attribution boundary: source TT/SEE intervention plus chess consequence can be called aligned explanation ONLY with same-root within-run causal evidence; allow NO_CAUSAL_CERT otherwise.
Stop rule: If C3X gains only by abstaining on nearly everything or uses far more compute at matched coverage, no demonstrated useful advantage. If BinProp's engine-grounded concept metric and C3X's strict universal certificate use different objectives, do NOT compare scores as if same metric. Run old complete real P3 recapture 0/18 and near-equal pair42/43 non-discrimination as development negative controls; NEVER advertise them as fresh.

## Source links
https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view
https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view
https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view
https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view
https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view
https://docs.google.com/document/d/1KfHbPocXjD1jo4Rb7sW_v9Mj56rwzjywUMU2DEYCnUk/edit

STATUS: source-level partial C3/C4 audit; no new tournament/engine result. Next step must be actual development source-matched small competitor benchmark, not more instrumental microcommits or claiming model advantage.
