# C3X 0.13 P6-M — Pawn Concepts as Exact Boolean Geometry

Status: MATHEMATICAL PRECOMMIT; NO STRATEGIC CAUSALITY CLAIM.

For color c and file f, n[c,f] counts pawns on that file. With n outside 0..7 defined as zero:
I_c(s) = sum_{f=0}^7 n[c,f] * 1[n[c,f-1] = n[c,f+1] = 0].
This is the actual definition implemented by c3x_explain.concepts._isolated_pawns. It counts PAWNS, not occupied isolated files: doubled isolated pawns each contribute. I is invariant under a legal non-promoting pawn push on the same file with no capture. The prior unrestricted phrase "all noncapture forward pawn moves" is FALSE under promotion: advancing a7a8q deletes a pawn and can change I.

For a pawn at (f,r), let EnemyAhead_c(f,r) be enemy pawn squares (g,t) with |g-f|<=1 and t>r (white) or t<r (black). Define p_c(f,r)=1 iff EnemyAhead is empty. Then P_c(s)=sum_{own pawns} p_c(f,r) is the implemented passed-pawn count, an occupancy-relative predicate, not a safety or promotion inevitability claim. At fixed enemy pawn positions, a non-promoting forward push is monotonic for THAT pawn's p: no enemy pawn ahead can appear after pushing. It may toggle 0->1 by moving past an adjacent-file enemy pawn's rank, despite leaving I invariant. Promotion removes the pawn and invalidates that monotonic accounting unless separately typed.

Two legal synthetic fixtures MUST be measured separately from natural-game confirmation:
- PASSED_BOUNDARY: FEN '4k3/8/p7/2p5/P2P4/8/8/4K3 w - - 0 1'. Legal root pawn pushes d4d5 (crosses black c5 threshold) vs a4a5 (still blocked by a6). No captures or promotions. Their isolation and center-occupancy counts match; passed-pawn count is different. Yet they are DIFFERENT pawns and different geometry, so alternative move preference cannot identify the passed-pawn feature as its mediator.
- ISOLATION_CAPTURE: FEN '4k3/8/8/1p2p3/2PP1P2/8/8/4K3 w - - 0 1'. Two legal captures c4b5 (isolation count 1 -> 3) vs d4e5 (1 -> 1). Both capture one opposing pawn, preserving material-change count, but the captured pawn, pawn coordinates and tactical effects differ. This is a controlled counterexample to the claim that isolation cannot change via legal moves, NOT an isolated causal intervention.

Every fact must be checked by chess rules, include legal UCI move validation, unchanged root source position and original-side score perspective, and a comparison to independent Stockfish processes at complete depths 8, 12, 16. Do not convert repeated cp ranking into concept sufficiency. Report both feature vector changes and confounding collateral. No target/sham causal certificate or cross-provider transfer is granted.

Potential conceptual paradigm shift (NOT YET EARNED): replace untyped feature labels by typed predicate + reachable intervention grammar + support set + source/engine/budget context + falsifier. 0.14 is NOT opened unless independent evidence demonstrates explanatory generality beyond this formal distinction.