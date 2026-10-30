# C3X 0.29-P6 — Lossless Explanatory Compression: Feature Sufficiency and Common Contingent Policies

**2026-10-31 | Mathematical development using archived P3 contingent-strategy obligations. No new Stockfish experiment or native chess replay.**

## 1. Definition and elementary theorem

Fix a finite nonempty declared opponent-reply set R, and for each r let A(r) be the subset of *semantically valid executable responses* satisfying all claims the explanation makes (all chess predicates jointly, not one predicate at a time). Let z:R->Z be a proposed interpretable explanation-feature map, e.g., 'opponent captured' or 'opponent checked'. A policy that is allowed to inspect **only z(r)** and must select a single concrete action label is sound on R iff, for every feature cell C_z={r:z(r)=z}, the action intersection intersection_{r in C_z} A(r) is nonempty.

Proof: Necessity: same z entails same chosen action, so it belongs to all A(r) in the cell. Sufficiency: choose one member of the intersection for each cell. This is a statement about literal shared action identity; when different board states require different UCI move instances, a higher-level *action schema* must be declared and shown executable at each r. It is invalid to merge unrelated moves by re-labeling.

**Censoring:** If A(r) is incompletely observed, nonempty intersections from partial logs do not certify the full chess property. If the response domain is restricted to capture replies, the theorem makes only a capture-conditioned assertion. In all-reply use, P3 full-legality provenance still applies.

## 2. Exact optimization problem and finite calculation

Given a complete finite relation A, define a *shared concrete-action vocabulary compression* as a subset T of action labels such that for every opponent reply r, T ∩ A(r) != ∅. Minimize |T|. This is the standard hitting set (equivalently set cover after transposition), not a newly invented chess algorithm. It minimizes number of distinct response moves, NOT length of an intelligible natural-language rule or complexity of chess-specific predicates.

Toy synthetic relation: R={r1,r2,r3,r4},
P-allowed actions: r1={tA,tB}, r2={tB}, r3={tA,tC}, r4={tC}.
Q-allowed actions: r1={tB}, r2={tB}, r3={tA}, r4={tC}.
Under P alone optimal T_P={tB,tC}, 2 labels; under Q alone optimal T_Q={tA,tB,tC}, 3 labels.
For the **conjunctive** claim P AND Q, use allowed actions A_joint(r)=A_P(r)∩A_Q(r). Here T_joint={tA,tB,tC} is required, 3 labels, and its finite policy is r1->tB, r2->tB, r3->tA, r4->tC.

This shows why compressing independent P and Q certificates separately does not generally produce a valid single joint strategy. Minimal model: one response r, P requires left, Q requires right, each separately satisfiable but the joint intersection is empty. The explanation must either abstain from the conjunction or explicitly say that two different actions achieve two separate objectives.

Independent JS exhaustive enumeration of all 7×7=49 nonempty two-response/three-action relations confirmed the computed minimum chosen by subsets is sound and minimal. This is a synthetic mathematical calculation, not a C3X original chess run.

## 3. Feature ambiguity is more informative than mere textual compression

When z groups two opponent responses that have disjoint legal/success action sets, NO perfect z-only explanation policy exists, regardless of how fluent its prose is. One must refine z (show the user the distinction), broaden the action representation with a *proved* conditional subrule, or report failure. This provides counterexample-guided abstraction refinement: each witnessed disjoint cell yields a pair of responses that an adequate feature vocabulary must separate.

Distinguish feature-cell sufficiency (common intersection in every cell) from global action-vocabulary minimization (minimum hitting set); neither alone optimizes human comprehension, minimal description length, or adversarial chess robustness beyond declared horizon.

## 4. Link to archived C3X and prior work

- 0.27 P3 had 18 original root-state complete legal-reply certificates, narrow strict-recature contingent witnesses; 15/18 pass **conditional on opponent capture**, all 18 fail universal strict immediate recapture. Treat its responses as development source and do not automatically promote their recapture policies to chess merit.
- 0.29 P5 establishes the common-witness obligation for conjunctive claims; P6 establishes when a proposed *compressed explanation-feature map* can represent that common witness.
- 0.25 P13-R4 real QSearch signed-parent assignments and P14-P6 same-board TT intervention root flip are a separate source-mechanism axis. A sound strategic policy is not a claim of why Stockfish selected a root move.
- Related foundations: finite game strategy synthesis, hitting set/decision-tree optimization, concept and causal abstraction; do not present these elementary underlying results as novel. This project contributes the **proposed explanatory interface and verification protocol**, which remains to be evaluated on actual legal states and human users.

## 5. Next scientific falsifiers

1. Choose predeclared simple chess features z on full P2B source and evaluate each feature cell's common-action intersection; known limitation: identical raw UCI move labels may not represent comparable chess action semantics across different post-reply states.
2. Record the smallest explicit opposing response pair r1,r2 with z(r1)=z(r2) but empty common valid action set; this is a concrete *feature-insufficiency refuter*, not merely a local disagreement in evaluation scores.
3. Refine z with one additional semantic test, verify its necessity and reassess minimal explainable policy complexity without exploiting outcome labels.
4. Test natural-language compression and human heldout transfer only after executable strategy correspondence. Keep source-native engine-mechanism evidence separate until joined on identical actual root and intervention.

**Status:** proven finite necessity/sufficiency statement; synthetic optimization calculation verified by exhaustive JS 49 relations; no 0.29 heldout strategic-explanation or AGI generalization claim. No WSL, native Stockfish or GitHub bot commit.
