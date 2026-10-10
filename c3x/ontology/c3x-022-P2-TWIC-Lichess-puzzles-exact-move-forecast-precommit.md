# C3X 0.22-P2 — Move-Specific Search-State Forecasts across TWIC and Lichess Puzzles

**PRE-SOURCE / PRE-NEW-NATIVE RESULT COMMIT, 2026-10-10.** C3X 0.22 ACTIVE; this protocol precedes newly chosen corpus outcomes. Distinct ecologies must not be pooled before each result is reported.

## Two fixed source ecologies

**TWIC**: Mark Crowther The Week in Chess issue **1656** (2026-08-03), verified official ZIP at https://theweekinchess.com/zips/twic1656g.zip. Archive: https://theweekinchess.com/twic . TWIC site explicitly reserves rights and describes the magazine as personal use only, and says to contact them for an online project. Source use is an internal pilot. DO NOT redistribute the original TWIC PGN, ZIP or its full moves in C3X public repo or Actions artifacts; only minimal selected-position research facts/derived features and SHA provenance, pending explicit distribution permission.

**Lichess**: official puzzle CSV Zstandard https://database.lichess.org/lichess_db_puzzle.csv.zst. Open Lichess dataset under CC0. Source schema PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags,DailyDate. Source SHA to be calculated on actual downloaded immutable snapshot BEFORE any native engine. Important: FEN describes puzzle position BEFORE first scripted adversary move. Apply Moves[0] legally to obtain the solver's proper Standard Chess root board. The correct move Moves[1] is an external solution label, NOT an explanation of native Stockfish or a source for choosing TT-sensitive games.

## Engine-free source selection rule: frozen before source reading

Historical FEN4 exclusions from EIGHT prior sources: C3X016 P4, 2025 Oct/Nov/Dec, 2026 Jan/Feb/Mar/Apr. Dedupe within and across the two new ecologies. No chess engine or evaluations while choosing cases.

For TWIC: scan at most first 20,000 PGN games, first 512 eligible Standard Chess games with >=70 halfmoves; game SHA = canonical hash over headers and full UCI mainline; selected ply index = 30+(first8 SHA hex modulo 15); played move legal, not a promotion, >=3 legal root moves; no historical FEN4 or within-week duplicate. Sort 512 game hashes and choose first 16. Store only SHA, limited source metadata, 4-field root FEN, played legal move, source ordinal and move count; **never upload the full TWIC game source or complete move list**.

For puzzles: stream first 20,000 official CSV rows, collect first 512 valid unique Standard Chess puzzle positions after legally applying scripted Moves[0], with >=3 root legal moves, valid Moves[1] legal in solver board and not a promotion, exclude eight historical FEN4 and chosen TWIC FEN4. Sort selected puzzle positions by SHA(PuzzleId+4-field normalized solver FEN) and choose 16. Keep source id, rating, date/themes *as metadata only*, solve-move labels in a separately sealed file, and no source label access during forecast making. If puzzle dump changes hash, stop and lock the observed snapshot SHA before native.

Freeze the chosen 16 source positions and each one's ALL legal root move geometric/legality state transitions (C3X021 primitive extractor), with source artifacts SHA, before any new native run.

## Two-stage EXACT root-move forecast, baseline stage blinded to TT intervention

**Stage A:** pinned Stockfish16 git 68e1e9b3811e16cad014b590d7443b9063b52; Threads1, Hash16, NNUE off, depth12. Run cold exact native baseline O (original root move order) and F (recorded move rotated first) in each selected game, separately discover O and F passive source writer-reader events without TT intervention, match selected physical pair under the original frozen January STRICT and BROAD pair selectors. Cold repeat and sham guards must PASS. Stage A then writes **literal specific game IDs and exact predicted UCI moves for ALL potentially eligible 16*2*2=64 role cells**, to a SHA- and Git-committed file BEFORE any native FIRST-reader intervention. No V mode in Stage A.

**Frozen baseline challenger rule named CROSS-ORDER RESTORATION:** if O and F baseline bestmoves disagree, predict O+FIRST -> F baseline bestmove, and F+FIRST -> O baseline bestmove. If O and F choose the same bestmove, predict neither first-reader intervention changes final choice (exact chosen move remains common bestmove). For missing physical eligible pair predict NO_TREATMENT, preserve role cell denominator. This rule makes concrete exact UCI forecasts conditional on native O/F only and is intentionally vulnerable to the known April15 third-move counterexample; do NOT rescue failed predictions post hoc.

**Stage B:** separate workflow, supplied with SHA-frozen Stage A exact per-cell predictions and physical source triplets, executes FIRST selected real native TT reader suppression twice cold for each eligible order-role cell. Verify full64 key/slot/epoch/native candidate/root call and writer provenance; no physical contact is NONCONTACT, not a test PASS. Compare ACTUAL exact UCI bestmove vs predicted UCI and binary flip. Report full 64 cells, conditional delivered contacts, per-game success, positive flip precision/recall, majority no-change baseline; STRICT/BROAD cells within one game correlated, NEVER independent samples. Source root depth ladders only claim alignment before path divergence.

**Falsification:** the per-game exact-move rule fails on any contacted cell where the predicted UCI differs; overall accuracy dominated by no-change is inadequate for a good prediction method. If positive flip cases are not correctly predicted, don't call it predictive success even if raw exact matching on many unchanged cells is high. The two new source ecologies are distinct tests, not source shopping.

## Paper and legal guard

Paper A candidate: When Search Order Changes the Move: Source-Exact Transposition-Table Interventions in Alpha–Beta Chess Search. Prior March/April and C3X020 adaptive February are model development, not held-out; failed historical K4/F19.5/Jan J2-J4/CPP224/PAG retained. A 16 TWIC + 16 puzzle pilot does NOT constitute 64-128 heldout game proof. Must obtain TWIC's permission before public redistribution of its actual game records or substantial reproductions. The new puzzle ecology also requires a contest of how puzzle-solution labels and native bestmove correlate WITHOUT using labels to choose TT responses. Stop on invalid licensing, source drift or cold tests with explicit HOLD.
