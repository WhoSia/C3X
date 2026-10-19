# C3X 0.27 P5 — Bounded Mate Horizon and Provenance Audit
Date 2026-10-19. This is a research execution report, not full-chess independent validation.

## Executed result
Local code C3X_027_P5_KRK_HORIZON.py SHA256 f74d2cbf55b55b39e5c7c94fd897a0ad87a3f199e5d285ac1bcf7c027488bd33; output C3X_027_P5_KRK_HORIZON_RESULTS.json SHA256 3de3d1fe5c50b31d1dbb7df9f428c859429d02c2eb25c8a7b09628d38cb6f707. PASS message P5_RESTRICTED_KRK_HORIZON_PASS. Reuses the P4 self-contained KRK legal subset generator and produces force-mate-within-H results for H=1,2,3 for 6 prior white first moves plus a novel constructed three-ply example. The restriction is K+R vs K, no additional pieces/special rules; not independent python-chess and not a full-chess verifier.

## New first strict H* example
White king b1, rook c4, Black king a3, White to move. Fixed White root Kb1c2, unique legal Black move Ka3a2, then White Rc4a4 mate. Force-mate reachability within H after the original initial turn: FALSE at H1, FALSE at H2, TRUE at H3. Hence H*=3 FOR THIS PRECISE ROOT AND PREDICATE, in restricted legal KRK rules. At H3 evaluator explores 19 move/action nodes, compact line has three ply tokens (root + only Black reply + mating second White move) plus a replay/coverage proof that Black had no other legal defense and mate has zero Black escapes. This is not a general optimal-computation or minimal-certificate theorem.
Prior P4 constructed samples: three mate-in-one roots true at H1/H2/H3, and three chosen nonmate first moves false through H3. Thus the verifier distinguishes nontrivial H*=1 and H*=3 examples and fails to force within H3 on some bad roots. Some nonmate examples have visit counts 13,57,54, showing failed claims can be costly depending on traversal.

## P11 original-data provenance
Fresh parse of original 144 P11 rows: exactly 9 distinct source_game_sha256 values, 9 distinct initial FENs, with evaluator/depth/repeat copies sharing the same game source per index. This is 9 game-provenance identities in the SAME original selected observational cohort, NOT a new game-disjoint heldout sample. Case42/43 prior conditional immediate recapture both rivals PASS, while control99 one FAIL one PASS. An independent blind tactical-versus-subtle tournament evaluation is still UNEXECUTED.

## Scientific boundaries
Correct truth domain labels: constructed restricted chess subset vs source-based earlier python-chess WSL enumerated original game positions vs future entirely new heldout real games. This P5 result cannot prove Stockfish causal choice, strategic advantage, or human training transfer. Ordinary chess rules include other kinds of moves and repetition, so later independently verify constructed FEN with fully featured python-chess. The restricted KRK code uses its own legal-move checks and exhaustive reply policy, not a generalized legal chess implementation.

## Paper connection
A: Quantifier-Sound Chess Explanations now has a grounded H* example and explicit positive/negative/UNKNOWN authority boundary, but limited toy-domain generality.
B: Evidence-Frontier Discovery now has first measured H1/H2/H3 forced-reachability and non-equivalence of 19 expanded nodes vs 3 ply words, but no lower bound on proof length or general computational class.
C: Stockfish source causal mediation and human transfer remain independent HOLD.

Next: compare at identical fixed q across independent full-rule chess games; add explicit source-format history; run full-rule Python-chess chess mate in one/two and bounded budget with UNKNOWN outcome, record node counts/serialized certificate lengths; preserve negatives 42/43.