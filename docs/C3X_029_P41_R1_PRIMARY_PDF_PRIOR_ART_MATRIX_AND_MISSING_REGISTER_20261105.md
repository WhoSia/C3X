# C3X 0.29-P41/R1 — Original-Drive-PDF Prior-Art Audit and Missing Register

2026-11-05 KST. Read primary-source extracted PDF text directly via authenticated Google Drive, including the methods, evidence, experiments, baseline and limitations passages of the manuscripts below. **Targeted primary-source study, not a claim to have checked each image or every page line by line.**

## Critical direct competitor: Cui, Ling & Ng 2026

Communicating Chess Strategies in Natural Language — Drive 19zqCJXM631qasR9uIyg4GuBZxIBO7czw. Selective partial branch trees, sampled opponent responses and worst downstream continuation within explored set (Tree-Expanded Puzzle Playing). Lichess puzzle evaluation; §6.2 raw JSON branch strategy often outperforms verbalized strategy because verbalization loses contingencies; §6.3 **30 students** with chess-skill stratification; §8 player recipient confounding and LLM-vs-human mismatch. Authors explain that sampled branch worst-case result gives an **upper bound** on true worst-case value, not complete universal all-reply proof. **Prior art preempts: off-main-line chess planning descriptions, response-conditioned evaluation and human utility.** C3X must beat strong JSON branch policy AND source-factual Stockfish PV; do not compare only to a single PV string.

## Critical concept rival: Press & Golubev 2026 BinProp

Explaining Chess and Go in Natural Language — Drive 1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6. Stockfish18 continuations after a better move versus a foil; executable Boolean motif discovery; uses **nearby negatives** sharing most of positive continuation before a later value-degrading move. Motif test 8 positive, 8 negative, 8 near-negative, min group accuracy; 200k training positions, 100 master test positions. Thus generic contrastive motifs and near-negative evaluation are already prior art. Distinct contribution must be measured conditional VALUE and causal mechanism, not a motif associated with favorable outcomes.

## Source-intervention prior art: Jenner et al 2024, Poupart 2024 and Geiger et al 2025

Jenner Evidence of Learned Look-Ahead in a Chess-Playing Neural Network — Drive 13QG6G_Ir67Q87Tkb1J9MOMn-TN4Zh63p: Leela future-move target-square neural evidence and interventions, including targeted single-entry attention ablation. Authors' Limitations explicitly acknowledge no complete underlying algorithm and single-line rather than multi-branch search. Poupart Contrastive Sparse Autoencoders for Interpreting Planning of Chess-Playing Agents — Drive 1jX9SqJCjdOSqmQ0f0r41L8YXJQCL567Q: contrastive Leela SAE and a feature taxonomy, limits of SAE training quality and human interpretation. Geiger Causal Abstraction JMLR 2025 — Drive 1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK: intervention algebras, graded faithfulness, causal mediation and activation/path patching. None permits claiming generic NNUE lookahead or patching as new; C3X must demonstrate its PARTICULAR source-executed NNUE→alpha-beta/TT ancestor→natural root choice mediation.

## Human concepts/faithfulness prior art

Schut et al 2025 PNAS AlphaZero Concept Discovery and Transfer — Drive 1Mg4vfb2t-MIr6juCAzCC1qdv8sq1f8uj: concept optimization, novelty/teachability filtering and preliminary **four-grandmaster** study. Hebbar et al 2026 ACT-Eval — Drive 1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA: 325 position-move pairs, 125 expert gold, tool-check factual/coverage atoms; §5 four chess annotators (two in recall study), 50 atom sample for correctness. Parfenova 2026 — Drive 1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R: 200 endgame puzzles, move masking/token-level tests and warning that fluent rationales can bias decisions without evidencing correctness. All bar a claim of novelty for merely producing clear, checked or persuasive commentary.

## Other essential originals verified

Bhaskar et al 2026 QUEEN — Drive 1I1HikAacandg5b75R0zymJlgxAQ41gbG: Lc0 encoder + language decoder and iterative distillation, 4B, reported Elo 1782→2697; evaluation includes **1000 near-optimal move positions with at least five moves within 3% win probability**. Ruoss et al 2024 ChessBench — Drive 1UBwx4nKx6i12tiHmqYZpAow644_Ts63x: 10M games/15B annotations from Stockfish16, amortized future values, not a novel chess value-learning problem. Nasu 2018 NNUE — Drive 1zAxUc2M9AOplr3UFbKUrQ5PLcA-dLOwj: efficient incremental neural Shogi evaluation; original preface states experimental evaluations are NOT part of that document. Kim et al concept-guided chess commentary — Drive 1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74: expert-guided commentary and GCC-Eval, already prior art.

## Scientifically possible but NOT verified novelty

H1: source-grounded plan-selective response-conditional value regret forecast adds reliable, independently adjudicated information beyond matched-cost Stockfish PV + **Cui-style engine-backed JSON branching strategy** + BinProp near-negative motif baseline, on truly game/event-disjoint near-equal cohort.

H2: a precise NNUE internal intervention, source/execution pinned, causally changes identified alpha-beta ancestor path and unrestricted natural root choice, and the same H1 value-plan variable predicts the mediated effect. Mechanistic hypothesis distinct from overall causal evidence.

## Missing / incomplete holdings, bounded Drive search

1. Sandmann et al 2026 future move lookahead vs action, arXiv:2508.21380 — query author Sandmann and look-ahead returned no matching PDF. **MISSING IN BOUNDED SEARCH**, not a global proof of absence; obtain full PDF before detailed quantitative citation.

2. Gobet & Simon 1996 grandmaster recognition/look-ahead — original PDF Drive 1p6Vm1HA3No37suP4GR3IWIjEjwQP27Br IS HELD but extracted text only **425 characters of repeated download watermark**: **HELD, CONTENT UNREADABLE**. Do not claim detailed paper read; need restored PDF text or page inspection.

3. No other specific title asserted missing. **ChessBench IS held** under Ruoss et al 2024; Cui and Parfenova also held. Literature inventory is bounded.

## Fatal research decision

C3X's P40 plan-regret is a VALID mathematical contract but its mere existence is not a paper novelty versus Cui; source-native NNUE presence is not source-feature mediation. Historical P37 weak 3-ply C3X plan lost to PV; P39 force-mate 0/16; P39 mobility did not beat deep bounded referee after upper/lower censorship. HOLD all promotional claims until real independent judge and prospective plan forecast outcome. Neither paper-writing nor proxy swapping is a solution.

Notion meaning, Drive original bytes, GitHub code; WhoSia source commits only and no github-actions[bot] repository contributions.