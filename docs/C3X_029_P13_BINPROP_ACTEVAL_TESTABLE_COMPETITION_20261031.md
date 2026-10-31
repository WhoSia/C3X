# C3X 0.29-P13 — A Direct Competitive Evaluation Question after Reading BinProp and ACT-Eval

2026-10-31. Research, retrieved original PDFs from Drive. No native chess benchmark and no model superiority claimed.

## What the papers actually measure
Press/Golubev, BinProp arXiv 2610.23166v1, original Section 2 evaluation: 100 sampled chess roots, 12 positive, 12 negative and eight nearby-negative continuation positions per root, with four positive and four negative examples visible as support; held-out 8 positive, 8 negative and 8 nearby-negative remain to score. Nearby negatives follow a top candidate then switch a later choice, destroying its evaluated advantage without the large early board-context difference. A binary Python motif's score is the MIN of positive TPR, negative TNR and nearby-negative TNR, not average classification accuracy. Motif construction uses a different 200k winning/losing board pool. Root candidates are usually gap>=75cp: their published results are not for the C3X original nearly-equal margin problem.
Hebbar/Sheng/Oh/Viswanath, ACT-Eval arXiv 2608.04240v1, Section4.2: untooled GPT-5.4 subclaim error 22.0% -> 9.2% with tools while gold atom recall 44.6% -> 44.0%; best tested tool model golden recall 60.9%. Section5 human calibration involved 4 Lichess 1800-2200 blitz annotators (two for study2) and raw agreement judge vs annotator ~69-83%, averaged 74.5%, with prevalence-sensitive Kappa. Tool correctness is not strategic completeness; evaluation of generated prose is not source-causal mechanism proof.

## Scientific question after this reading
At matched computation, identical legal source states and game-disjoint fresh positions, do C3X quantified contingent certificates improve near-equal move *contrastive correctness* without collapsing gold-atom coverage compared with BinProp, ACT-Eval tool-backed evaluation and strong conventional chess commentary?

## Implemented contract and scope
tools/c3x_029_p13_nearby_negative_minimax_evaluator.py calculates the MIN of binary accuracy for positive, negative and nearby-negative groups. It uses only supplied group labels and boolean predictions; it does NOT reconstruct Stockfish continuations, claim that a score is causally correct or validate chess legality. Its return explicitly says SYNTACTIC_EVALUATION_ONLY and HOLD until original game-cluster, source and legality audits. Regression tests check uneven group accuracy, duplicate case IDs, missing nearby group and wrong types.

## Previously overlooked distinction
Worst-group accuracy is one necessary anti-spurious-motif benchmark; C3X universal contingent policy `forall r exists t` uses a different target with full quantification over the declared legal reply domain. Neither score dominates the other without shared experimental outcomes and comparable coverage. ACT-Eval's atom precision and coverage are complementary axes; an always-abstain verifier with zero false claims is a poor explanation product. Thus freeze multi-axis evaluation rather than optimize a single source-internal certificate metric.

## Prereg experiment
- A and B strata: strict near-equal roots vs >=75cp gap roots, both game-disjoint and source-provenance audited.
- Different generation pipelines receive identical public chess board and continuation budget, with no private engine trace exclusive to C3X.
- Positive/negative/nearby negative groups constructed and sealed with separate first-stage support and heldout condition; ensure no shared PGN game across training and test groups, and document linked-position correlation.
- Explain output scored on (i) worst-group binary motif robustness, (ii) chess-rule truth of quantified claim, (iii) gold atom recall and factual precision, (iv) explanation coverage at matching risk, (v) token/engine budget, (vi) human transfer as separate prereg outcome.
- Include legacy case42/43 and all-reply immediate recapture 0/18 as development negative controls only.
- HOLD if human annotations or software artifacts unavailable, or groups cannot be aligned; do not force false equivalence of unlike outputs.

Evidence: Direct Drive PDFs BinProp 1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6 and ACT-Eval 1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA, now verified in 10_PAPERS; related QUEEN/CCC/Cui and Harvest older source audit documented at docs/C3X_029_LITERATURE_BINPROP_ACTEVAL_QUEEN_HARVEST_COURT_20261031.md.

STATUS: new comparator code and tests committed; real test run and source labels unverified, no improvement over literature established.
