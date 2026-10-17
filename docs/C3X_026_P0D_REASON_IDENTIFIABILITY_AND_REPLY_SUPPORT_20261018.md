# C3X 0.26 — P0-D: Reason Identifiability and Reply-Support Distinctions

Status: THEORY + DESCRIPTIVE RAW AUDIT; NO NEW ENGINE CALLS.

## P11 re-analysis
Using exact P11 original SHA256 18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2, 144 rows, 72 repeated arm pairs, 36 (position, evaluator, first move) conditions, top reply swaps depth17→depth19 = **15/36**. Of all 36, reported MultiPV2 move set unchanged in **20**, one shared candidate in **16**, no common candidate in **0**. Among 15 top-reply swaps, **9** are pure order reversals within an unchanged visible top-two set, **6** replace one visible candidate. MultiPV2 is truncated evidence, not exhaustive reply reachability. Nodes and search exposure differ.

Index42/Classical after d6f8: [f2f4,e1d1] → [e1d1,f2f4] (pure rank inversion). Index43/NNUE after a8e8: [f1d1,f4d2] → [c1d1,f1d1] (observed candidate replacement). These observations are not strategic reasons, nor prove that omitted replies were never searched.

## Finite separating-set theory
For competing hypothesis set K, allowed legal interventions T, and registered prediction f_h(t), two accounts h,k are identifiable on T only if some t∈T gives observably distinct predictions f_h(t) != f_k(t) under defined tolerance. If all registered interventions predict the same observation, accounts are T-equivalent: no number of cold repeats of the same arms will distinguish them.

When finite K is pairwise T-separable, selecting one witness intervention per unordered model pair yields a finite separating collection; a minimum separating collection is a hitting-set/set-cover problem **relative to K,T and prediction observables**. It is not an 'absolutely minimum true explanation.' Interventions might be physically/legally unavailable; explicitly allow ABSTAIN.

## Scientific decision
C3X's three claims are separate: (1) board/legal continuation contrast, (2) strategy relevance of that contrast, (3) engine-search causal dependence on it. Future implementation must produce registered chess-legal predicate and intervention witnesses, not attribute latent chess strategies from MultiPV first-move strings.

Next: define two falsifiable rival predictions on index42 / index43, preserve controls 47 /99; matched search exposures and untouched event-heldout cohort before scientific validation; negative cases preserved. No retrospective renaming of C3X 0.25. 0.26 OPEN is not a positive empirical theory verdict. Github WhoSia commits only; Actions read-only.