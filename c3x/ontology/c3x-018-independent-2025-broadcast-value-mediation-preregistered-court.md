# C3X 0.18 — Independent Broadcast Game Histories, Writer–Reader Value Witness & Blind Falsification Court

**Design frozen before accessing new game positions or new engine outcomes.** Existing #2/#5 are development cases only; none may be included in the independent test denominator.

## External source and sampling

- External source: Lichess official **October 2025 broadcast PGN** archive, `https://database.lichess.org/broadcast/lichess_db_broadcast_2025-10.pgn.zst`; original PGN CC BY-SA 4.0, cite Lichess with attribution.
- Save compressed archive SHA-256 and original full UCI mainline game move history per selected game, headers including event, White/Black and GameURL/Site. Do not pass engine-derived scores into selection.
- Parse the **first 512 valid standard games** with at least 70 halfmoves, distinct game fingerprint based on headers plus all mainline UCI moves, disjoint from the 12 existing FEN4 positions. Refuse to silently skip parser errors.
- Rank eligible games by SHA-256 of canonical game fingerprint; take the **lowest 16 unique games**, from entirely separate source games; no post-outcome game exclusion. Pick each game's original position before ply `30 + (int(game_sha256[:8],16)%15)`, before the original played move. Require >=3 legal root moves and no promotion move, otherwise exclude that game **before** any engine execution and record the exclusion. Track original FEN4, played move UCI/native SF16 value, source game header, historical UCI moves, archive SHA and sample fingerprint.
- Within this data set no source-game repetition is permitted. Sampled original game histories are retained for audit, but the initial SF16 chess inference remains **standalone FEN**, not a game-history replay; keep this limitation.
- Two stages: source cohort materialization and SHA audit **before** first source-native Stockfish test, followed by frozen cohort source-native trial. Never update selected cases based on search outcomes.

## Fixed interventions and target rule

- Frozen SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; Threads=1, Hash=16MB, MultiPV=1, NNUE off, search depth=12, new independent cold process per arm.
- Root O=original, F=force originally played move first by the preexisting legal source intervention, Z=no-contact sham. Reject if O/Z final six-field UCI tuples differ; retain all 16 with failure status.
- **Passive source target**: run F with TT physical shadow and `C3X018_TT_DISCOVERY=1`; record first 32 eligible full64 writer-key-consistent TT bound-as-evaluation consumer proposals. Choose **the first recorded full64-matched candidate whose writer_serial>0 and raw payload matches the actual TT entry**. This selection depends on baseline F telemetry ONLY, not V/W2 outcomes. Do not substitute another candidate when the first target does not fire under treatment.
- Treatment V=block chosen bound-conditioned TT value-as-evaluation consumer, W2=block first two matching source writes, negative control=impossible full64 target. Run cold repeats of every treatment, preserving nonfiring cases and complete final UCI core.
- Record physical writer receipt with 16-bit raw value, bound, depth, eval and move, original 64-bit key, slot, epoch and per-process unique write serial; verify the actual consumer reads precisely that payload before source V.
- Do not identify cross-arm writer events based only on equal numeric epoch/counter or root-call IDs. Reject observed unverified key or changed payload; result class HOLD rather than crediting mediation.

## Three falsifiable forecasts and stopping authority

**P1 – Independent V transport (risky).** In the 16 new original-game positions, at least **one** source-contacted V treatment changes the final bestmove relative to F. If zero, P1=FAIL. A missing eligible target counts in the denominator and is not a successful non-effect.

**P2 – Dominance pattern (risky).** Among the 16 positions, **every V-induced categorical bestmove flip** also occurs in W2 at the predeclared corresponding source target. Any V-only flip falsifies P2. Zero V flips means P2 not confirmed (vacuous), not PASS.

**P3 – Source measurement integrity (engineering gate).** Across all first eligible V consumer proposals, 100% of *claimed writer→reader* events in the recorded witness have last writer raw payload agreement, nonzero writer serial and full64 key equality. Any mismatch is FAIL-CLOSED; if no proposals exist, NOT_TESTED rather than automatic PASS.

**Causal authority:** even a P1/P2/P3 PASS is NOT sole natural TT mediation; it is fixed-source intervention transport with writer-valued instrumentation only. Main/qsearch other uses, all SF16 alternative pathways and engine/external-population transfer remain open. Do not manuscript-freeze.

## Source-stage separation

The separate harvest workflow uploads a manifest including source archive SHA-256 and all 16 full original move histories. A reviewer must preserve the frozen manifest and its SHA before executing the TT native trial. The follow-up GitHub workflow accepts this exact committed JSON as a fixed path, never redownloads/reselects games.
