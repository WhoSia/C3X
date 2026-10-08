# C3X 0.13 P8-EP2 — En Passant Continuation Confluence as a Chess-Concept Erasure Witness

Status: **NEW POST-BUG-DISCOVERY DEVELOPMENTAL HYPOTHESIS; NO PRIOR ENGINE SCORES ON THIS PAIR OPENED.** C3X 0.14 remains an un-named, unopened candidate. This is NOT a formal 0.14 proposal.

Source frozen historically in P7-R1 first game of 2026 NZ South Island Championship, P7 source group rank in original September Lichess cohort, actual legal halfmove 32:
FEN 1r1qk2r/4bppp/QN1pp1b1/2P5/1p2n1P1/4B2P/PPPN1P2/R3K2R w KQk - 1 17.
The old P7 hazard gate mistakenly ignored an en-passant opponent pawn recapture of a double-pushed pawn. New P7 corrected source-only run 37733793448 found exact same-origin born/not-born pair a2a3 vs a2a4 that was excluded by old source-only selection. This was identified AFTER P7/P8 development outcomes but before ANY dedicated engine evaluation of the NZ pair; all P7/P8 historic HOLDs and source records remain unchanged.

## Confluence theorem to check with full chess rules
Let root S be above source FEN, legal WHITE moves A=a2a3, B=a2a4, and BLACK reply R=b4a3 in both successor worlds. Under S_A, R is an ordinary capture of pawn at a3; under S_B, R is en passant capturing the white pawn at a4 while BLACK lands on a3. Require:
- A and B are both legal from the same historical S, same WHITE pawn on a2.
- R is legally available from EACH after-root position; ordinary capture on A route, en passant on B route.
- S --A--> S_A --R--> T_A, and S --B--> S_B --R--> T_B. Verify **T_A.fen(en_passant=fen)==T_B.fen(en_passant=fen)** exactly (all six FEN fields, not merely material or score), same side to move and same move clock.
- The passed-pawn birth feature differs between S_A and S_B (original black b4 pawn newly becomes passed under B, not A). After R, the exact common chessboard T makes every BOARD-state predicate identical. Thus born/not-born root features are *not sufficient to distinguish this particular continuation*.
- The two legal replies have the same UCI b4a3 but distinct chess capture TYPES (normal vs en passant), each removes the original white pawn. The old P7 capture-hazard must count both as an opponent pawn taking the root mover.

This is a constructive local CONTINUATION CONFLUENCE witness, not proof that opponent MUST play R, nor that engine minimax/root preference is equal; other plausible replies may diverge, and legal move choice/tempo still matters.

## Freeze independent-engine checks, not outcome rescue
Only AFTER proving exact FEN equality, run Stockfish16 and pinned Ethereal 14.40 classical commit 0e47e9b67f345c75eb965d9fb3e2493b6a11d09a with Threads1 Hash16 MultiPV2 at completed depths8/12/16, two cold process repeats for legal roots A/B; preserve cp root-mover POV, PV first eight moves, engine identities and binary hashes, en passant legality. Do not filter this pair by favorable score or near-equality AFTER observing results. Record whether b4a3 appears as first Black reply in each engine's root PV for each root; absence means exact T is a legal but not necessarily preferred continuation.

Require source/tactical/EP proof as distinct evidence levels. This one NZ game cannot establish an independently replicated strategic concept or cross-engine causal mediation. Even if both engines favor same move, the structural confluence is a BOARD-AND-LEGAL-REPLY relation, NOT an intervention-isolated reason for engine preference. Only future independent source games and opponent preferences could elevate explanatory authority; 0.14 not open on this local proof.