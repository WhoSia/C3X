# C3X 0.29-P28 — Full-reply shared plan falsifier and the next value test

Date: 2026-11-02. Executed in local container with original recovered C3X 0.16 Go chess law source from authenticated Drive P22 source ZIP. These are real rules-valid chess positions, not synthetic utility scores.

Question: after either 1.e4 or 1.d4 from the ordinary starting position, is white's immediate subsequent move Nf3 legal after EVERY legal black first move?

Procedure: Parse initial position, use original Board.Legal to find candidate and original Board.Do, enumerate entire Board.Legal() black response set separately for each candidate, then inspect legal white moves for g1f3. No cross-world reply UCI correspondence is assumed.

Actual local results:
- 1.e4: 20 black legal replies; for all 20, Nf3 legal.
- 1.d4: 20 black legal replies; for all 20, Nf3 legal.
- Therefore for Q='at next turn Nf3 is legal', G_Q(e4)=G_Q(d4)=1 under this 1-reply/1-own-move horizon. This is a real, exhaustive finite F2 non-discrimination result for THIS deliberately weak plan predicate.
- Full local Go test suite, including P27 and P28, passed 8/8 tests. No engine valuation was measured.
- Source Go files are kept in original Drive archive; GitHub holds portable P28 test only, requiring those historical Go sources at test time.
- P28 is not evidence about true strategic value, Stockfish choice, or independent near-equal root evaluation, nor a universal statement for all horizons.

Scientific inference: universally available 'plans' can be uninformative if plan semantics are merely move availability. Define Q with a verifiable result and tradeoffs (e.g., positional/king safety, tempo, opponent refutations), then independently evaluate connection to chosen utility before calling it explanatory.

Research follow-ons:
F1: find actual chess states where candidate a guarantees predeclared Q but candidate b's independently evaluated minimax outcome is higher. Requires engine and credible value oracle, not yet done.
F2 strong: find meaningful strategic Q shared by near-equal candidates despite a stable preference, under audited legal reply fans.
Other: counterfactual alignment of replies must compare candidate-specific full legal response domains, not forced equal UCI IDs; track coverage/horizon.
