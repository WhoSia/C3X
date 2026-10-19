# C3X 0.27 — P1: Quantifier-Sound Consequence Certificates

Date: 2026-10-19. Formal theory result + source-derived coverage audit. No new engine execution. C3X 0.27 official title remains unchanged.

## A chess-native difficulty discovered in P11/P0-F
The opponent is an adversarial legal agent, not an observation sampled from a generic human preference model. A single observed PV provides an *existential witness*, not a proof over all legal replies. That is a logical limitation rooted directly in game-tree quantification.

Fix full history h, rival legal root actions a,b, a finite horizon H, and a chess-specific predicate q on resulting positions (e.g., unavoidable material loss, restoration of check safety under a forced threat, or protection of a named square). Define R(h,a) as the set of all **legal** opponent replies to root a, not just MultiPV2 reports.

- Existential opportunity E(a,q): there exists r in R(h,a), and a legal continuation pi for the original side under the registered horizon/policy, for which q is true.
- One-response robust capability U2(a,q): for **every** legal opponent reply r in R(h,a), there exists a legal original-side response t in R(h,a,r) satisfying q at the stated terminal or intermediate state: forall r exists t. This is an H=2 quantifier pattern, not a minimax value or a promise about H>2.
- The difference between existence and robust capability is not semantic decoration: an example satisfying E does not establish U2. U2 requires legally complete opponent-reply coverage *and* a witness response for each; a counterexample r for which all legal second actions fail q refutes U2. If q is defined on a fixed terminal state, specify how checkmate/stalemate termination and side-to-move are handled.
- At longer horizons alternate quantifiers according to move ownership, without pretending an engine search PV explores the whole game tree. Opponent constraints P must be an explicit subset of the legal response set; 'for all in P' must not be quietly reported as 'for all legal replies'.

## Computed P0-F source coverage audit
Using verified user-uploaded P0-F HF1 JSON (144 rows/72 unique response arms/36 comparison rows) each sampled root includes exactly two opponent MultiPV2 replies. The *complete legal opponent* counts, already enumerated by python-chess after the first root, are:
- Index42 CLASSICAL root d6c5 (Bc5): 38 legal, 2 reported unique => 2/38 = 5.26%; root d6f8 (Bf8): 40 legal, 2 reported => 2/40 = 5%.
- Index43 NNUE root a8e8 (Re8): 36 legal, 2 reported => 5.56%; root d5f5 (Qf5): 37 legal, 2 reported => 5.41%.
- Negative 47 NNUE: 35 versus 35, each has 2 reported => 5.71%.
- Negative99 CLASSICAL: 29 versus35, each 2 reported => 6.90% vs5.71%.
The fractions measure **listing coverage by move identity only**; not search node coverage, probability mass, reply plausibility or causal evidence. Repeated depths/eval modes share the same legal root states. P0-G already provides a source-guarded enumerator of all legal opponent reply identities but is unexecuted natively; P0-F gives full legal counts but not the identities.

## Minimal legal consequence certificate (new proposal)
Witness fields: game history h (repetition-aware), source checksum, root candidate a/b, precise predicate q with chess-specific sense, declared side and horizon, response family P, result status among EXISTENCE_ONLY / ROBUST_ON_DECLARED_P / REFUTED / NOT_IDENTIFIABLE, per-branch legal replay and a refuter/counterexample; the certificate must NOT contain an unsupported 'engine chose this move because q' label.

For robust q on root a at H=2, the proof obligations are:
1. Enumerate all legal r after a, record a digest plus the number and exact identities.
2. For every r show a legal t making q true under declared terminal semantics.
3. For contrast with b, exhibit a single legal reply r_b for which all legal t_b fail q, or independently prove an alternative exhaustive failure condition.
4. Confirm any chess history dependence: FEN6 alone is insufficient for repetition.
5. Use fresh event/game-disjoint cases and negative controls to determine whether the certificate explains a persistent search-rank inversion rather than merely distinguishing board futures.

This supplies a sound finite proof rule **relative to q/H/P**: with complete legal coverage and true checked continuations, U2 holds by finite quantifier enumeration. It does not show a new chess strategy law or a cause for Stockfish's ranking. If a legal reply or historical state is missing, ABSTAIN rather than fill in with prose.

## Scientific and engineering direction
Prioritize a single specific target q drawn from archived pin legality, SEE/recapture, and history-sensitive repetition failures. Be alert to vacuity: if a chosen q is trivially true in both roots, the certificate has no contrastive explanatory value. Also beware post-hoc q selection on positions 42/43; exploratory results remain discovery-only and must be frozen before unseen testing.
No immediate need for new Stockfish calls; first obtain exact P0-G response identities or use native python-chess to enumerate *all* replies and test q. Current Drive canonical custody of earlier code: https://drive.google.com/file/d/1PG8RHZw3yWuUER4aVirNeQQdxr_PQfZ-/view . User keeps WSL copy; don't ask repetitive downloads. GitHub actions read-only, no bot commits, historical 0.25/0.26 unchanged.
