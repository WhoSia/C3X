# C3X 0.29-P9-R10 — Budget Sensitivity, Score Provenance, and Robust Replay Contract

2026-10-31. Historical literature and original C3X native receipts audited. No fresh Stockfish run or private raw artifact download.

## Previously overlooked evidence that is directly relevant

C3X 0.15-P10-R2 (c3x/receipts/c3x-015-P10-R2-first-root-candidate-child-return-vs-stored-score-48-native-20261009.json) executed 48 original SF16 native processes, 24 cold pairs, two outcome-exposed TWIC worlds. Its first retained event differences often changed the CHILD SEARCH RETURN without changing the STORED ROOT SCORE (e.g. #2, root f3e5, depth4, returned 14 vs130 but stored root score both -32001). In #29 OFF B the first retained divergence changed candidate visit/order, so ordinal event equality itself fails. Event budget 1024 censored 67 later events in one arm. This source directly contradicts any P9 claim that first child-return divergence is synonymous with candidate score change.

C3X 0.15 CSWP 0.6 (c3x/ontology/c3x-015-CSWP-v0.6-incomparable-local-return-score-nodes-root-choice-source-observation-quotients.md) already separated four observables: source-local return L, reported final root score S, node count N, final bestmove Y, with actual intervention counterexamples showing their equivalence partitions do not imply one another. This is prior C3X evidence, not a new theorem.

C3X 0.13-P4 (c3x/ontology/c3x-013-p4-depth-regime-precommit.md) already preregistered Stockfish16 fixed depth 8,10,12,14,16, cold pairs and root-pair cp comparison to test depth-regime sensitivity. Do not present these testing dimensions as first invented in 0.29.

## T3 original four arm scores are not a b1b4 candidate margin

0.23-T3 game2 O/STRICT sham 20062 nodes -8cp e1g1; TT 41685 -8cp e1g1; SEE 46783 +1cp e1g1; joint 47563 -4cp b1b4. The published derived trajectory script tools/c3x_023_P1_R2_T3_derived_outcome_and_search_path_report.py exports one leader score and retry count by depth, NOT per-candidate comparable bound interval records.

Measurement specification:
- child-return (signed source call, alpha/beta and bound)
- root candidate stored value before/after (may be sentinel -32001)
- completed-depth UCI score (root POV, exact/lowerbound/upperbound)
- observed bestmove and PV
- work nodes and aspiration retries
Each has independent identity; no subtraction of terminal scores from different arms as a within-arm candidate margin.

## More disciplined replay staircase
G0: verify source byte SHA, legal full game history, exact original SF16 commit / overlay chain, binary hash / flags, NNUE off, Threads1, Hash16, completed depth12, root O/STRICT, cold TT, source SEE actor target, and observer reversibility. Reproduce 4 arms, original source contact and final UCI/nodes/cp and depth trajectory. If any mismatch, call REPLAY_FAIL, not causal replication.
G1: within pinned build vary depth 8/10/12/14/16 by complete deterministic *separate cold engines*, preregister distinct budgets and stop policy; treat as an external robustness study, not a same-setting exact replica. Existing 0.13-P4 results may be reused as methodological precedent but cannot prove this T3 source.
G2: independently vary Hash, NNUE, threads, warm/cold, architecture only after baseline parity. Threads>1 require repeated-run empirical distributions and non-iid settings by game. No unverified claims about distribution from two cold repetitions.
G3: instrument b1b4 and e1g1 per depth/aspiration attempt: candidate searched/finished, score/bound/POV, priority, RootMove stored before/after, retry and chosen root. Source-native patch must be exactly reversible and noninterfering.
G4: demonstrate chess-legal downstream structure under candidate alternative, independent of claims about internal engine motivation; outcome-blind disjoint benchmark before wider generality.

## Falsifier
At any changed engine configuration if chosen move differs from historical joint-only b1b4, robust fixed-move assertion fails for that configuration, but original pinned source-specific interaction is not thereby falsified. If 4-arm cold parity fails under purportedly original configuration, revalidate entire source and attribution before using old T3 mechanism argument.

## Academic boundary
No novelty claim for one conditional interaction or elementary score partition; search algorithms, bounded rationality and explainability already developed. Drive originals: Russell & Wefald 1991, Knuth & Moore 1975, Marsland 1986, Avin/Shpitser/Pearl 2005, previously checked. No confirmed missing paper.
