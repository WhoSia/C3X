# C3X 0.13 P6-R1 — Passed-Pawn Birth Rival Continuation Support Census

Status: SOURCE-LOCKED DEVELOPMENT PRECOMMIT. NO ENGINE PREFERENCE OUTCOME.

Use EXACT prior P5/P6-T/E frozen 16 Lichess broadcasts. Reuse P6-E audited birth events and take earliest birth PLY per complete legal game, one root per broadcast group. Do not replace the 7 broadcast groups without births or Chess960 parser HOLD. Total per source group, not per event, remains the independent counting unit.

For each selected root: played move m produced >=1 newly passed pawn. Freeze a legal alternative m' by taking lexicographically first OTHER legal move of SAME PIECE FROM SQUARE with SAME capture status, captured piece type and promotion status, such that m' produces ZERO newly passed pawns on either side. Reject comparison if none exists. Keep source FEN, gameURL, played/alternative UCI, exact passed-pawn births, all collateral chess feature deltas.

This is the most stringent intervention *support census*, not an after-result near-equal pair selection. Do NOT relax if yield is zero. A root comparison of a move with birth vs a move without birth still changes attack geometry, pawn structure and search; even with capture class matching it does not isolate mediation through the birth fact.

This P6-R1 opens no Stockfish scores. Only if eligible alternatives appear may a separately frozen real UCI experiment measure root preference; it still cannot claim a causal concept. Failure/HOLD is primary output and guides which alternative grammar might be justified in future prospective games.