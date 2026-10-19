# C3X 0.27 P3 — Consequence Claim Calculus and Historical Reuse
Date: 2026-10-19. Official 0.27 title unchanged.

## Formal results
Fix full chess history, a complete finite perfect-information legal tree, target q, and horizon H.
E_H means an eligible legal path achieves q within H; G_H means the claimant can force q within H against all adversarial moves.
Theorem 1: G_H implies E_H for nonempty complete legal trees. Converse false for an opponent fork where one branch avoids q.
Theorem 2: If q is an absorbing reachability objective, G_H implies G_(H+1). No such claim follows for exact-at-H endpoint properties or varying q_H. This corrects earlier overbroad suggestions about nonmonotonicity.
Theorem 3: forall opponent replies in declared subset P cannot be reported as forall all legal opponent replies without complete coverage. EMPTY_CONDITION is not meaningful positive empirical support.
Theorem 4: Legal move possibility, adversarial guarantee, material value, original Stockfish causal mechanism, and learner improvement are distinct explanation authority levels.

## Real abstract checker execution
Local standard-library script C3X_027_P3_FINITE_CLAIM_VERIFIER.py executed with result P3_FINITE_TOY_PASS 3 cases monotone-reachability-check=PASS. Cases: obvious forced two-ply target, apparent PV victory defeated by other legal opponent branch, own-side option existence. Code SHA256 58b797827b0ef45203935662e3113bd47035a193e32abe185dc8f782a7ff0152. Output JSON SHA256 26015f506cbf2a32dcd928622e1c8280a5b3937f75dd9a5c1e28abb29058b081. This evaluator assumes the abstract supplied tree is legally complete; it is NOT new chess-native validation.

## Drive archive C3X 0.9+ thorough targeted reread
Connected Drive chat files C3X 10,12,14,16,18,20,21,23,25 were newly fetched and source statements reviewed.
G9.5 P5 representation selection FAIL/HOLD and P7 target-blind reuse failure/HOLD: recycle frozen quotient/counterexample procedures, not claims of universal global field.
G10 0.9 P19 engine survival / identity variation and PRESEALED-AWAITING-FRESH-WORLD limitation: chess rule certificate independent of engine-specific search evidence.
Explanation Track I8 was CLOSED, HUMAN_UTILITY_CLAIM_HOLD; G10 P1 near-equal question selector HOLD. Existing human explanation renderer can be reused, but not certified pedagogical efficacy.
0.13 passed-pawn counterexamples and FEN history insufficiency tests: full h essential for repetition claims.
0.17 source TT writer/consumer and PIN/SEE atom vocabulary: reuse native interventions and legal microstructure.
0.19/0.20 selective restoration K4 bestmove recovery FAIL 0/4 despite other checkpoints: local causal search changes do not guarantee root choice.
0.21–0.25 TT source interactions; actual TT returns/parents not automatically value propagation; 0.24 fresh move-choice prediction failure; 0.25 M6 64 source contacts with only 1 root move change: distinguish mechanism contact, action result and explanation.
P2-B 18 legal root states, all-response q refuted 18/18, opponent-capture-conditioned 15/18 positive, only position99 (negative strict inversion control) distinguishes rivals; P2-D case99 selected lines each net 0 simple rook-material. No general cause claimed.

## Candidate papers, not completed publications
(A) Quantifier-Sound Chess Explanations: Proof-Carrying Consequence Contracts Beyond Principal Variations — full legal certificates, selection-vs-universal PV errors, obvious and subtle source-disjoint examples.
(B) Evidence-Frontier Discovery for Bounded Chess Explanations — proof depth, coverage, certificate complexity under fixed chess claim; requires nontrivial complexity / verification result.
(C) Faithful Chess Explanations Across Search and Human Reasoning — source causal intervention, verified chess predicate, prospective learner transfer; mechanism and human utility still HOLD.

## Next
Add history-aware complete legal move generator and exact terminating-game semantics; test obvious tactical and subtle near-equal claims, UNKNOWN if budget exhausted. Preserve old FAIL/HOLD, no bots or new branches, no Drive byte claim for newly local script.