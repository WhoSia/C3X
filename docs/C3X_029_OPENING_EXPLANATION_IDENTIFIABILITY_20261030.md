# C3X 0.29 — Contrastive Explanation Identifiability: Local Legal Proof, Global Generalization and Causal-Strategic Alignment

**2026-10-30 | FORMALLY OPEN — QUESTION/DESIGN PROMOTION ONLY; EMPIRICAL PROMOTION HOLD.** Prior official 0.27 and 0.28 titles and receipts remain intact. This version opens a new mathematical and scientific explanation-generalization problem; it does not claim an AGI explanation system or new native A/B/C evidence.

## Research problem

An explanation is not simply the engine's selected move, its centipawn score, a native search event trace, or a valid finite tactical contrast. It is an answer to a declared alternative A versus B that identifies a chess-relevant proposition, quantifies over an explicit opponent response policy, provides a checked witness and falsifier, and states the region in which the proposition generalizes. The long-run ambition is verified reasoning transfer to new positions and human understanding; these are separate empirical endpoints.

Prior 0.26 and 0.27 already distinguished search process, legal consequence geometry and understanding; 0.28 adds source-exact TT/SEE and E1/E2 ancestor tracing. 0.29 adds a **new question**: when does a locally valid chess explanation license a globally meaningful claim, versus when are many inequivalent concepts indistinguishable on the measured reply support?

## P0 theorem: local contrast does not identify a global reason

Let Omega be the 64 possible king-destination squares and A,B the sets of legal observed opponent replies after contrasting root moves in the restricted KRK-1 example. Upstream simple KRK checker gives A={g7,h7}, B={g7,g8,h7}. Let q:Omega->{0,1} be an arbitrary Boolean chess-state predicate represented only by the opponent king's square. The contrast certificate is (forall x in A, q(x)=1) AND (exists y in B, q(y)=0). As A is a subset of B and B minus A={g8}, these conditions force q(g7)=q(h7)=1 and q(g8)=0. This is one unique truth assignment on observed support S=A union B, but the other |Omega-S|=61 square values are unconstrained. Therefore exactly 2^61 global Boolean predicates satisfy that same local certificate. This counts arbitrary mathematical Boolean predicates, NOT 2^61 cognitively meaningful chess strategic concepts.

Explicit inequivalent explanations: q1(s) = 'black king is on rank 7'; q2(s) = 'black king is not on g8'. They are identical on S={g7,h7,g8} and both satisfy the local contrast; on square a7 both are true, so a7 is NOT a disagreement point. A valid disagreement point is **a8** (q1 false, q2 true); neither is observed in the KRK reply support. This correction must be reflected in code and tests: don't accidentally publish a7 as witness. This is a finite nonidentifiability proof independent of scores and TT logs.

Computational court: tools/c3x_029_local_global_explanation_court.py computes the 8 possible truth assignments on S and finds exactly one satisfying contrast; applies the 64-square combinatorial count 2^61=2305843009213693952 and explicit q1/q2. Locally equivalent checker ran Python unittest PASS; new GitHub implementation and test were committed, but the public implementation uses illustrative_disagreement_square='a8', explicitly checked against q1/q2, with regression tests pinning the witness.

## Distinct epistemic levels

Level L: legally checked contrast over a declared finite support and quantifier, not proof of bestmove. Level G: transport to new chess contexts with explicit counterexample search and preregistered semantic predicate family, not proof of unique psychological reason. Level M: actual source-native mechanism TT/SEE return/parent/root causal evidence, not automatically chess semantics. Level H: held-out human learning/transfer under controlled comparisons, unmeasured.

## Competing explanatory hypotheses

H-mechanism: source algorithm and search budget explain a root preference with no stable chess-specific distinguishability under changed legal opponents. H-consequence: a preregistered chess predicate and its refuters generalize to independent contexts, though engine internal pathway may vary. H-both: both are separately established. H-underdetermined: multiple semantic explanations agree on all registered support; output should ABSTAIN on unique/global explanation. Avoid choosing q after observing bestmove on the prospective heldout cohort.

## Experiment plan and promotion criteria

P1: minimally extend existing 0.27 certificate schema to include support S, scope, full legal reply enumeration digest, declarative q vocabulary, equivalence class under S, off-support falsifier, no-vacuity checks; no generic tool ecosystem.

P2: revisit archived development examples 42/43, negative controls 47/99 from 0.26/0.27. Their previous MultiPV2 2 of 29-40 reply coverage cannot justify universal claims; use original full history and full legal response enumeration if accessible. Keep post-outcome enriched cases DEVELOPMENT only.

P3: source-native 0.28 P13 score consumption and E1/E2 remain essential independent component. Do not confuse the 0.25 P12 24 TT return-parent frame pairs with actual parent score consumption (NOT INSTRUMENTED). Same-aspiration final score and TT bound semantics prerequisite for a genuine choice-stability certificate.

P4: preregister fresh-heldout cross-position falsification and human transfer outcomes before claims of generalization, explanation uniqueness or AGI-grade behavior. Include bland score/PV commentary as baseline.

**Evidence and governance:** No new WSL/Stockfish outcomes. September provisional 64 remains unchanged; selected index20 castling-rights validity and history source-family coverage still HOLD; no confirmatory freeze. All commits by authorized human identity only, GitHub Actions read-only and bot commits forbidden. Notion semantic log should retain both theorem and the corrected off-support witness.