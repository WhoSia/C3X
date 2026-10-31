# C3X 0.29-P9-R16 — Question-first causal adjudication: root bound semantics before ranking
2026-10-31. This is an epistemic and static-code research audit, not a Stockfish execution.

## Priority research question
When the 2026-05 game2 O/STRICT depth12 TT1+SEEflip world selects b1b4 while each singleton selects e1g1, is the root decision attributable to (A) different candidate search support, (B) changed candidate score/bound and aspiration resolution, (C) root move ordering/tie or historical search-state differences, or combinations? The original four output cp readings (-8,-8,+1,-4) are one terminal root score per treatment world and not a comparative b1b4-v-e1g1 value table.

## Actual source review
- T3 original receipt: c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json.
- C3b / root-loser historical records: c3x/receipts/c3x-024-P2-R2-native-ancestor-root-full-and-partial-development-20261011.json and c3x/receipts/c3x-024-P2-R3-source-root-candidate-reached-but-not-final-and-May11-partial-20261011.json.
- R15 score comparator: tools/c3x_029_p9_r15_root_bound_comparison.py.
The R15 inequalities are valid *only if supplied intervals already have valid common semantic meaning*: the code validates no Stockfish score provenance, common search-window semantic class, fail-soft semantics, move-specific score ownership, mate/cp conversion, or window resets. Reusing such 'CERTIFIED' wording on unverified native return values would overstate scientific authority.

## Distinguish three score objects
1. Local fail-soft return conditioned on a window and search path, whose numeric value is not automatically a certified bound on a fixed game-theoretic action value.
2. Stored RootMove score/scoreBound after Stockfish's iteration/retry state, whose provenance and completeness must be logged.
3. Externally reported UCI cp, a presentation of selected search result, not four-way candidate payoff matrix.
A bounded result can be compared only after explicit collector assurance that a and b bound the SAME declared estimand at common root context and completed search policy. Without that, ABSTAIN and label 'syntactic interval consistency only'.

## Testable rival mechanisms
H_entry: b1b4 root search starts/completes in joint but not singleton at same depth/attempt.
H_bound: both searched in matched attempts yet bound, retry or stored score rank changes.
H_order: same eligible candidates but processing order, tie policy, window or PV transport differs.
The hypotheses are not necessarily exclusive across iterations. Event non-observation in censored traces cannot establish no entry.

## Gated next action
P0 Verify the existing R11-R15 tests using the exact repo and record output/commit SHA. A GitHub search for a commit-associated PR workflow run returned empty because this connector lists only PR-triggered runs: it is NOT evidence of no push CI.
P1 Rebuild/replay original depth12 May source using existing sealed private data, engine SHA and original exact site intervention; verify UCI,nodes,cp, contacts and search identity. Only after parity.
P2 Introduce read-only collector logging root candidate UCI, frame/rootcall, treatment, completed depth, retry, search window, score_kind/POV, score origin, store before/after and selected move. Ensure exact source reversibility and original parity.
P3 Test depth changes as separate estimands and freeze prospective heldout predictions, instead of post-hoc story fitting.

## Historical negative results retained
M0/M2 TWIC1664 54/64 with M2 0/10 true flips; 0.24 July/Aug predictors no outperformance; 0.23 game11 operator-only negative. Existing operator interaction is a postselected development instance, not transport law.

## Literature
Drive originals previously verified: Knuth & Moore 1975; Marsland 1986; Russell & Wefald 1991; Avin et al. 2005. No new outside reference asserted.

## Final gate
R16 = scientific QUESTION AND EVIDENCE-SEMANTICS AUDIT PASS, no new mechanism, no engine replay, full R11-R15 suite still unconfirmed. Do not claim test PASS from file existence.
