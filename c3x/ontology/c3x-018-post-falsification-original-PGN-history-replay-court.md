# C3X 0.18 — Post-External-Test History Replay Attack

Status: **ADAPTIVE SECONDARY EXPLORATORY COURT.** Do not call this an originally preregistered test.

The sealed 16-game October-2025 broadcast cohort contains every source game's full original mainline UCI moves. The completed [standalone-FEN native experiment #37982781383](https://github.com/WhoSia/C3X/actions/runs/37982781383) found a precommitted V root-choice impact in **0/16**, even with physical TT writer/reader source contact in 16/16. The initial failed run #37982333162 and the disclosed legal en-passant normalization are retained.

**New separate question:** Does Stockfish 16 select or search differently if we reach an identical board by replaying the game's *actual earlier moves* rather than entering `position fen <FEN4> 0 1`?

- Materialize each exact `position startpos moves <first original halfmove_count UCI moves>` from the same 16 immutable broadcast source records.
- Test O/F/Z first-move source intervention under native replay, Threads 1, Hash 16 MB, NNUE disabled, depth 12. Run each engine process cold twice.
- Assert O=Z six-field UCI output, source actor legal and root contact evidence. Preserve all 16 source identities and every failure.
- Compare exact final UCI tuple (bestmove, score, bound, nodes, PV) for replay vs the SHA-frozen standalone-FEN counterpart.
- Do not assert that the two workflows represent the exact same mathematical state: history, clock, repetition, and transposition tracking can legitimately differ.
- Report the proportion of bestmove changes and full-core changes across all 16. No exclusions based on changed or unchanged outcomes.
- This history-replay court is **post hoc and exploratory**, not confirmation of the original P1 conjecture. It does not retarget TT events or establish unique natural writer-reader mediation.

All source PGN moves and their source archive SHA are frozen in the separate engine-blind #37981820261 evidence artifact; use original filenames and hash checks, not a new sample.
