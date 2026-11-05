# C3X 0.29-P39/R1 — First Rule-Complete Adversarial Chess-Value Certificate

2026-11-05 KST. PRE-OUTCOME registration for P39 legal outcome labels. Prior P37 eight-event games/candidates, forecasts, Stockfish/human references were already observed, so this is METHOD DEVELOPMENT ONLY, not a confirmatory heldout trial.

## Q_M2: exactly checkable chess consequence

For exact full-history legal state s and legal mover candidate m, Q_M2(s,m) is TRUE iff m checkmates immediately, OR for EVERY legal opponent reply r after m there EXISTS a legal mover reply u that immediately checkmates. All quantifiers are over the complete legal-chess move universe, not a PV sample. Immediate mate gets its own IMMEDIATE_MATE label. Terminal stalemate, drawn positions and defeats do not receive vacuous TRUE labels.

Positive certificate: explicit r-to-u checkmating witness for every legal opponent reply, with all replies enumerated. Negative certificate: one legal opponent counterexample r and exhaustive check of its entire legal mover response universe, proving no immediate checkmate. A computer-work cap gives TECHNICAL_HOLD, never FALSE. Record expansion counts.

## Frozen 8-event development court

Take exactly eight original P37 source-only cases, each with exactly two original P37 frozen SF16 24k candidates, 16 candidate worlds in all, no substitutions. Source original member SHA256 77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361, P37 pre-referee prediction member SHA256 da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051. Verify complete full-game UCI history hashes, exact ply30 history and FEN, source/prediction IDs, legal roots; immutable original Actions runs 41968008046 and 41969173637. Compute Q labels only AFTER this document/contract is committed.

Preserve all 16 outcomes including zero positives. Because the sample is exposed, do not claim unseen-game generalization. Q is a hard tactical property, not a complete positional evaluation or a full C3X plan theory. If zero positives, report that this Q has insufficient support in these cases, NOT that near-equal chess values are meaningless. Never replace games or raise the depth after inspecting outcomes.

## Future truly predictive court—not executed by this preregistration

On separately frozen game/event-disjoint future cases, seal binary Q forecasts BEFORE any chess-law verification, with strong Stockfish score+PV, foil-aware conditional JSON, real C3X conditional predictor and abstention. Do NOT provide any model the full Q proof oracle before predictions. Equalize native nodes, legal enumeration and CPU; apply independent verifier with unchanged source. The existing 3-ply material heuristic has repeatedly lost to PV and is not the full C3X model.

## Scientific fail gates

Any source-history/FEN mismatch, illegal root, false claimed checkmate, missing opponent reply, or invalid negative witness => TECHNICAL_HOLD. No completed exhaustive universe => HOLD rather than FALSE. Chess-law certificate does not assert NNUE leaf→root mediation, actual human decisions or strategic positional dominance.

## Governance

Notion science authority, Drive immutable bytes, GitHub executable provenance. User-authored WhoSia commits only. GitHub Actions contents:read and upload artifacts only. github-actions[bot] commits, merges, pushes, tags or ref mutations prohibited.