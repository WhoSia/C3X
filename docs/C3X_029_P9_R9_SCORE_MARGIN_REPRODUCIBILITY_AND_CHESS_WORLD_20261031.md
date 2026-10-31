# C3X 0.29-P9-R9 — Root Score Is Not a Candidate Margin; Robustness and Chess-World Explanation

2026-10-31. Original native receipt and archived report-generator code audited; Drive Russell & Wefald (1991) original abstract/introduction read. NO new Stockfish run, no candidate score claims.

## Critical correction
0.23-T3 May broadcast game2 O/STRICT had TT0 SEE0: e1g1, -8cp, 20062 nodes; TT1 SEE0: e1g1, -8cp, 41685; TT0 SEE1: e1g1, +1cp, 46783; TT1 SEE1: b1b4, -4cp, 47563. These scores are terminal *reported root evaluations* for DIFFERENT searches, not per-candidate fixed valuations. No reported same-attempt candidate-specific comparable score of b1b4 versus e1g1 in all four arms. Thus 'b1b4 won due to +4cp' and 'the causal candidate margin changed by 4cp' are UNSUPPORTED.

The archived script tools/c3x_023_P1_R2_T3_derived_outcome_and_search_path_report.py exports per-depth one reported native root leader, root_return_score and retry_count, not complete competing candidate score/bound intervals. The T3 aggregate receipt reports earliest root-score divergence depth8 and leader depth9 for this case, but NOT a uniquely causal score gate at these depths. Historical R3 root candidate losses in sham arms further caution against equating path-reaching with winning.

## Multi-fidelity explanation, not an intrinsic universal bestmove
Treat observed engine output as a function of legal state s, engine/version+settings theta, compute budget B, execution and history conditions omega, source intervention T: Y(s;theta,B,omega,T). For fixed deterministic pinned cold configuration, replay reproducibility tests process parity, not robustness to other depths, threads, hash/TT warm state, NNUE, hardware or engine versions. With stochastic or uncontrolled execution settings, report conditional selection frequencies and seed/run-level grouping. Do NOT assume iid independent moves or identify uncertainty from only 2 cold repeats.

Chess-semantic target distinct from engine-mechanistic target: derive relations, legal candidate consequences and counterplay from state transition s->s_a, falsify quantified predicates with legal reply witnesses; explain why 1.e4 e5 and 1.e4 c5 lead to different structures without simply parroting opening labels. Finite-horizon search cannot prove every future strategy, and historic engine score is not game-theoretic ground truth.

## New falsifiable program
P0 reproduce original pinned T3 4-arm final UCI, nodes, score and depth ladder with original binary/code and private source (rights gate). If mismatch: isolate source hash, build flags, full move history, searchmoves, TT empty/warm, Threads, Hash, NNUE, stop policy, architecture/time and observer noninterference. No mechanism claims until parity.
P1 controlled variation axes ONE AT A TIME: depth8..16, Hash size, NNUE toggles, thread count, warm TT vs cold; predeclare which are deterministic controlled alternatives and which are stochastic run distributions, handle dependence and avoid interpreting all as the same intervention. Keep source tactics and controls fixed.
P2 collect in each root iteration/aspiration attempt the candidate UCI, search started/completed, returned bound (lower/upper/exact), score POV, root current window, PV, root move priority, root winner. Compare b1b4 and e1g1 with sound comparable intervals; use abstention if incomparable. P13 QSearch patch not directly port-compatible to T3 overlay.
P3 generate legal chess explanatory contrasts, check against every relevant opponent legal reply and fresh game histories. These do not automatically explain Stockfish actual internal selection.
P4 presealed disjoint heldout evaluation, engine and depth shift, within-game clusters and clear abstention.

## Primary paper
Russell & Wefald (1991), Principles of metareasoning, Artificial Intelligence 49:361-395, Drive original https://drive.google.com/file/d/1SAvlhQSvPEXTV4QxmsnrCZtzWk-x9ZWT/view . Abstract and introductory framework checked: rational computational action under bounded resources, uncertain computation utility; supports framing but not new empirical Stockfish claim. Original Drive Knuth & Moore 1975, Marsland 1986, Avin/Shpitser/Pearl 2005 remain held/partially reviewed.

## Claim ledger
PASS historical reporting-score versus candidate-score epistemic correction and existing derived script coverage audit.
HOLD candidate margin, replay outside fixed historical setting, native source mediation, general opening strategy synthesis, academic novelty.
