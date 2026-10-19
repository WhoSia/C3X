# C3X 0.27 P3 — Native Branch Logic Certificates (2026-10-19)

## Actual execution
- Input: user-supplied, WSL-native-validated C3X_027_P2B_STRICT_RECAPTURE_H2.json; SHA256 e990188ad9da4f2035d70d9010448157f8a41fe14830904245e68164d2ae8f0c. Previously native script P2B_PASS 144 72 18 36.
- New standard-library P3 adapter: C3X_027_P3_NATIVE_TREE_CLAIM_ADAPTER.py SHA256 a5c34bba5a9a83ff6defe1ecb79ab1dcc054912a1a33e9cc33e6a7dabad46309.
- Executed P3_NATIVE_BRANCH_LOGIC_PASS 18 9 {'TRUE': 15, 'FALSE': 3} [99].
- Output JSON C3X_027_P3_NATIVE_TREE_CLAIM_RESULTS.json SHA256 71905402214fde41e6cf286ac21d33dcfcc2f45cf25c478980ba22438eed77b9. All 72 arm copies canonicalized as 18 chess states; cross-mode/depth legal response signatures agree. Nine unique pairs evaluated.
- NO independent python-chess legal replay this run: legality inherits original user's native WSL P2B enumeration. No newly validated H3+ proof, move-strength inference, causal Stockfish mechanism, or learner outcome.

## Quantified chess results
After candidate root a, opponent r in declared set P, original response t legal: q means t immediately captures exactly opponent recently moved piece. Two types P: all legal replies versus opponent's actual capturing replies (nonempty required).
For all legal opponent replies: 18/18 refuted. For opponent-capture-only: 15/18 true, 3/18 refuted; one pair (idx99) has distinct conditional statuses. Cases 31 both roots false due r=a6b5. Cases 42,43 both roots true; index47 negative both true. Case99 original White Rxc2 after d2c2: Black Qxc2 c6c2 not directly capturable; alternative White Kg2 h2g2: only legal Black capturing reply Rxd2 c2d2; White Qxd2 d4d2 is legal. This is a local legal contrast, not strategic advantage.

## Proof-rule interpretation
Existence witness: single legal response/capture pair. Universal conditional TRUE: enumerate every eligible opponent capturing reply and provide one own legal recapture for each; FALSE: a single eligible opponent reply with independently checked no matching own capture. A positive proof cannot compress away opponent branch coverage absent another proven lemma. Proposed pointer-only minimal negative proof still requires source position and independently reproducible legality check.
Theorem: forced reachability within H implies existential reachability within H; converse fails. For fixed target reachability-within-H, forceability monotone in H (not for exact-H endpoint claims). Previous claim that all horizon properties are nonmonotonic was too broad.

## Previous C3X 0.9+ reuse
G9.5 frozen quotient failure/HOLD; G10 engine-specific survival; I8 HUMAN_UTILITY_CLAIM_HOLD; 0.13 history versus FEN, passed pawn counterexamples; 0.19/20 K4 0/4 final root restoration; 0.23 TT×SEE interaction; 0.24 prospective failed prediction; 0.25 TT physical source contact not identical to root mediation. These delimit chess-rule proof versus original engine causation and human benefit.

## Paper readiness
Proposed Quantifier-Sound Chess Explanations paper currently has real finite H2 legal results and logic certificates, but cannot claim novel H* discovery, meaningful discrimination on target 42/43, out-of-sample chess strategic explanation, or human transfer. Next: verify constructed obvious tactical examples with independent native chess legality; horizon-sensitive forced outcome q in independent games and disjoint source cohorts; positive/negative proof compression bounds; no retrospective feature selection on negative control 99.

No new WSL run, Stockfish call, or Drive binary custody of this new script/output; local paths in assistant runtime currently available.