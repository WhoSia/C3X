# C3X 0.18 — December 2025 Independent Writer Age, TT Bound, Search Ply & Root-Owner Court

**PRE-OUTCOME protocol freeze.** Filed **before downloading or scoring the 2025-12 games**. Previous October 16 and November 12 are development/evidence, not December holdout successes.

## Source-only blind sample

Use Lichess 2025-12 broadcast PGN (`https://database.lichess.org/broadcast/lichess_db_broadcast_2025-12.pgn.zst`; CC BY-SA 4.0), independently of any engine output. For the first **512 eligible** standard valid games with >=70 full mainline halfmoves and >=3 legal moves at chosen original board, form SHA256 of sorted-json(game headers, full original UCI mainline). Select the **12 lowest unique game SHAs**; before-ply `30 + int(first8_sha_hex,16)%15`. Reject any FEN4 matching the original 12 / October16 / November12 cohorts; preserve all rejects and original game histories. Exact source blob SHA256, raw .zst SHA256, sample metadata and all original UCI moves must be retained before engine CI. Exclude on legal pre-outcome criteria only.

## Frozen native implementation and measurement

Stockfish16 source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; depths **12 only** (avoid post-hoc depth selection), 1 thread, Hash16, MultiPV1, Use NNUE false. Canonical legal en-passant and **authentic original halfmove/fullmove** from the frozen original game prefix, FEN replay into cold engines. O/F/Z root sort, Z=no-contact. Two cold repeats of O/F/Z and passive F discovery. Source-exact TT writer→reader observer records full64 key, physical slot, slot-local write epoch, unique in-process global writer serial, raw saved TT (value, eval, move, depth, bound), current in-process write serial on read, `writer_age_writes = current_serial - last_writer_serial`, actual root call ID, root move native integer, recursive search ply and remaining search depth. **Writer age is intervening accepted write-event count, not milliseconds, wall-clock age, generation count or number of distinct writes to that slot.** Do not infer a globally stable TT event ID across cold arms.

Enumerate **at most first 256 eligible** bound-conditioned **evaluation correction readers** in the *passive* F run. If there are more than 256, emit `DISCOVERY_CENSORED` in the manifest, not a complete census. For each of 8 fixed selectors, choose first qualifying reader **from the passive stream alone**, before any V treatment output. Do not replace unavailable selectors with the next different category or exclude cases; ineligibles count in all denominators.

## Eight fixed source-role selectors

1. `young`: writer age 0–8 inclusive.
2. `old`: writer age >=64.
3. `lower`: TT raw bound exactly BOUND_LOWER=2.
4. `upper`: TT raw bound exactly BOUND_UPPER=1.
5. `shallow`: reader search ply <=2.
6. `deep`: reader search ply >=4.
7. `original_root`: reader's actually attributed root candidate equals the preserved original-game played move native integer, root_call>0.
8. `other_root`: reader's attributed root candidate differs from that move and is nonzero, root_call>0.

These are **marginal selectors**; a source reader may simultaneously be old, deep, lower and other_root. Never treat the eight cells as statistically independent. `root_move` is root ancestry **within that cold search call**, not physical TT ownership or an identity across treatment arms. Bound class `EXACT=3` is neither LOWER-only nor UPPER-only.

## Treatments and falsifiers

Each eligible target is `(full64key, physical TT cluster slot, slot write epoch)`; V suppresses **the actual value-as-evaluation consumer** at this selected physical target, not other TT reads/writes. Two cold treatment repeats and exact source value witness on every claimed reader. Impossible full64 key decoy + O=Z baseline remain exact no-contact controls. Record final UCI core, bestmove categorical response, touched source write serial/age/bound/ply/root ancestry; allow V nonfire => NOT_FIRED not a negative effect. No cross-arm identity claim from counter equality.

**Prospective risk tests:**
- **D1_OLD_ROOT**: >=1 of 12 *old* category interventions actually fires AND changes final bestmove. Otherwise FAIL, including no eligible.
- **D2_DEEP_ROOT**: >=1 of 12 *deep* category interventions actually fires AND changes final bestmove. Otherwise FAIL, including no eligible.
- **D3_BOUND_ROOT**: >=1 of 24 (12×{lower,upper}) bound-category interventions actually fires AND changes final bestmove; otherwise FAIL.
- **D4_OWNER_CONTRAST**: for >=1 game, both original_root and other_root categories fire, and their binary bestmove-change indicators differ. Otherwise FAIL.
- **D5_SOURCE_INTEGRITY**: 100% of claimed selected reader events have a preceding full64 matched physical last writer raw-payload ticket and age>=0. Any mismatch FAIL-CLOSED; no read contacts => NOT_TESTED.
- **D6_NO_CONTACT**: O/Z six-field UCI exactly equal across all games, impossible-key V decoy exactly equals F with 0 actual suppression.
- **D7_COMPLETE_DENOMINATOR**: exactly 12 game records and 8 category records per game, all failures/ineligibles retained.

A categorical bestmove effect is not a natural mediation uniqueness proof; a successful ordinal selector from November cannot rescue October P1 failure. Site categories overlap and predictions are **designed to fail if root effects do not transport**. No manuscript freeze.

## Research authority

A local C++ witness establishes actual source contact and saved payload identity. An effect on final bestmove under V establishes a *selective intervention response* at one search site. Neither establishes an algorithm-independent concept relation, fully isolated causal mediation, nor game-history cross-ecology portability.