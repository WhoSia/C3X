# C3X 0.27 P4 — Restricted Chess Mate Certificates and Evidence-Frontier Cost Audit
Date 2026-10-19. Official C3X 0.27 name unchanged.

## Independently executed construction
Built and executed a Python standard-library restricted legal chess generator only for white king+white rook versus black king. Synthetic positions; no pawn, castling, promotion, en passant, additional pieces or general mating evaluation.
Result P4_KRK_RESTRICTED_LEGAL_PASS 3. First position White Kc1 Rb3, Black Ka1, White to move, Black not already in check. White Rb3-a3: black king checked, total legal black replies 0, mate under orthodox KRK rules. White Rb3-b1 instead: black king has legal escape Ka2; not mate. A universal mate certificate requires zero complete legal replies after root, whereas non-mate requires one legal escape. This is a proof complexity asymmetry grounded in actual chess subset, not a Stockfish general legal engine test.
Code local C3X_027_P4_KRK_FORCED_MATE_CERTIFIER.py; results local C3X_027_P4_KRK_FORCED_MATE_RESULTS.json. Not yet archived as Drive bytes.

## Existing native P2-B comparison (no new legal generator)
Using 18 unique first-root states from previously user-executed WSL python-chess native response JSON, dedup evaluator/depth, P4_FRONTIER_LEDGER_PASS 610 47. 610 total legal opponent replies across states, 47 are legally capturing responses eligible for capture-conditioned immediate recapture q. 15/18 PASS, 3/18 REFUTED, matching P2-B. More specifically:
- 42 d6c5 38 legal opponent replies/1 capture reply/1 proof-relevant response witness; d6f8 40/1/1. Both PASS, no near-equal candidate distinction.
- 43 a8e8 36/3/3; d5f5 37/3/3. Both PASS, no near-equal candidate distinction.
- 99 d2c2 29/1/1 REFUTED (c6c2); h2g2 35/1/1 PASS (c2d2 -> d4d2). Case99 was prior P10 search-inversion negative control and not proof of preference difference.
The evidence-cost counts are simple response record counts, not CPU time, certificate bytes, or independent chess validation. Critically, showing only the 47 eligible captures as a positive proof needs an independently auditable *membership/coverage certificate* showing no other legal capturing replies were omitted among 610 legal choices. Do not report 47/610 as reduced legal search work: identifying the 47 required the full legal enumeration.

## Formal claim/research opportunity
Separation theorem at fixed complete position and conditional P subset: an output proof can use one selected successful t for every eligible opponent reply, but a self-contained positive universal proof also requires complete membership of P. For a negative universal, one legal eligible opponent reply and exhausted own-capture alternatives refute; the negative proof can be shorter. This separates verifier work from compact certificate transport; compressing a record != doing less underlying search. The optimal set-cover/compression lower bounds need an explicit proof calculus before calling the structure a publishable result.

## Paper test
Potential paper A (quantifier-sound chess explanation) now has restricted orthodox chess KRK mate/nonmate examples plus audited P2-B 18-state capture-conditional certificates. Still missing independently sampled full chess obvious tactical corpus and strategic sustained value proof. Paper B (evidence frontiers) has an empirical membership-vs-witness cost distinction, not an asymptotic complexity theorem or established minimal H*. Avoid theoretical novelty inflation. Human/Stockfish-causal results absent; prior 0.19/20 K4 bestmove restoration FAIL and G10 I8 human utility HOLD remain.
Next: independently chess-native H3 mate-threat/defense under full rules and predeclared independent game splits, genuine certificate size bits/computational time measure, proof of frontier complexity and counterexample to misleading PV.