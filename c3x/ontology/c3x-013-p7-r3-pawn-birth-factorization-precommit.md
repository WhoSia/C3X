# C3X 0.13 P7-R3 — Counterfactual Factorization of Passed-Pawn Birth Geometry

Status: new post-P6 developmental MATHEMATICAL precommit (not a P6 rerun or new science PASS). C3X 0.14 remains a candidate, without title or opening.

Use ONLY original P5's first 16 source-frozen September Lichess broadcasts (same 15 valid full games and one Chess960 source HOLD). P6-E previously found 19 new passed-pawn events in 9 real games by comparing actual blocker sets. Do not replace, select, or manufacture additional events.

For each P6-E event at a legal move, let x = original square of a persistent pawn, y = its post-move square, E0 = opponent pawn-square configuration BEFORE the legal move and E1 = opponent pawn-square configuration AFTER it. Define the exact Boolean board predicate p(z,E)=1 iff no pawn in E lies strictly forward of square z on z's own or neighboring files. Build the **four-cell noncausal mathematical comparison**:
- p(x,E0)=0 (birth was initially blocked);
- p(y,E1)=1 (birth was finally passed);
- p(y,E0) isolates the change in focal pawn COORDINATE with opponent pawn arrangement frozen;
- p(x,E1) isolates the change in opponent pawn-square configuration with focal pawn position frozen.

Classify by the middle two truth values, WITHOUT presuming a chronology of interventions:
(1,0) POSITION_ALONE_SUFFICIENT; (0,1) OPPONENT_CONFIGURATION_ALONE_SUFFICIENT; (1,1) EITHER_FACTOR_SUFFICIENT; (0,0) JOINT_NECESSARY. Record all four blockers, FEN exact source SHA, game and ply. A diagonal pawn capture moves BOTH x->y and opponent pawn arrangement; hence an earlier heuristic label such as "PAWN_ADVANCE_THRESHOLD" can be misleading if read as purely forward rank crossing. This comparison is an algebraic counterfactual on pawn-coordinate/opponent-state *variables*, NOT a legal chess move pair, not necessarily a valid intermediate board, and not a causal engine-preference attribution.

Require identical 19 event identities and original 16 source groups. Count events and source games separately; no claim that 19 events are independent. Retain prior P6-E heuristic classifications as historical observations, but never reclassify them silently: new orthogonal taxonomy is separate. All missing/unmappable events are execution HOLD, not dropped.

This mathematically identifies paths by which the same final passed-pawn predicate can become true; it does NOT identify why an engine prefers one root, does NOT overcome P7's 0 strict same-origin root support, does NOT grant a scientific C3X 0.14 paradigm.