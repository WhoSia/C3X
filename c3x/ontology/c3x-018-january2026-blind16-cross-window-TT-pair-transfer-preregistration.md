# C3X 0.18 → 0.19 Gate — Cross-Window TT Reader Pair Transfer, January 2026 (PRE-OUTCOME)

**Pre-registration time:** 2026-10-10 Korea. **Do not harvest the new January PGN or run engines until this commit is recorded.** Historical case #11 of December 2025 was exhaustively mined: the 32 intervention masks on one physical writer yielded the finite categorical formula `x13(x11 OR x12)`. That formula is DEVELOPMENT evidence and never an independent test success.

## Source-only external holdout

Public Lichess 2026-01 broadcast PGN `https://database.lichess.org/broadcast/lichess_db_broadcast_2026-01.pgn.zst`. First 512 legally eligible, standard games with ≥70 plies and ≥3 legal root moves; SHA256 of canonical sorted JSON(original game headers, full mainline UCI moves); select **16 games** by lowest full SHA. Original board is the state immediately before ply `30 + (first 8 hex SHA mod 15)`. Exclude overlapping board/FEN4 with prior original 12 and October 2025 16, November 2025 12 and December 2025 12. Verify legality and preserve full PGN game sequence; record all exclusion counts. **No Stockfish during source selection**. Both raw compressed archive hash and frozen source manifest hash must be captured before any target search.

## Frozen engine, real source-level features

SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, cold standalone original six-field chess FEN, authentic halfmove/fullmove clocks, one thread, Hash16MB, MultiPV1, Use NNUE=false, depth12, legal EP normalization, original played legal move forced front only in F. Two cold exact process runs for all arms.

Passive F enumeration **capped at first 2048** actual bound-qualified TT *value-as-better-evaluation* consumer events, in source print order. A census exactly at cap is **CENSORED**, not exhaustive. Source witness fields must include full64 key, cluster slot0..2, slot write epoch, accepted-write global writer serial, current accepted writer serial, `age=current-write-serial - writer-serial`, raw writer payload (value, bound, depth, static eval, move), recursion ply, local search window alpha/beta, effective TT score, source root-call ID and root candidate native move. Source `root_call` is *only an ephemeral within-process handle used by the physical intervention*; the **selection rule does not contain predetermined root-call numbers**.

Form all candidate unordered pairs of source-positive actual readers of the **same** `(full64,slot,epoch,writer_serial)`, with same nonzero root candidate native move and **distinct** actual root-call IDs. Must be TT `raw_bound=LOWER(2)`, equal accepted full64 writer snapshot and `beta>alpha` for both. Pairs may not be created from outcomes; deterministic order: sort by maximum reader event index, then minimum index, then full64/slot/epoch, then two root-call IDs. Take only the FIRST qualifying pair under each selector. If none, status `NO_ELIGIBLE_PAIR` and **do not substitute**.

Two prospectively different source-role selectors:

- **STRICT:** both consumers have `writer_age_writes≥64`, `ply=1`, `beta-alpha≤2` (narrow fail-low/PVS windows), `raw_bound=2`, same TT writer payload, same root candidate and different source root calls. These are abstract conditions matching the role pattern of the December minimal pair, but no root-call numbers, chess squares, hash keys, or scores are reused.
- **BROAD:** both have `writer_age_writes≥32`, `1≤ply≤2`, `beta-alpha≤16`, `raw_bound=2`, same writer/carrier and candidate but distinct root-call handles. This is separately labeled a lower-specificity transport test **declared before January outcomes**, not a post-failure relaxation of STRICT.

Only two target pairs maximum per game (one strict, one broad), potentially the *same* physical triple and source pair. Include exactly 16×2 selector records in the denominator. A pair may share carrier with earlier eligible reader events. Event-specific V must guard actual **age threshold, root candidate, raw bound, ply, window width, source pair call handles and physical carrier**, and must record every source **reader_block**. Preserve same observed local writer raw payload proof in V, with actual selected root calls verified. A treatment that does not contact all two nominated calls is `PAIR_NOT_REALIZED`, not a root-effect negative.

## Fixed intervention arms per selected pair

Baseline F/OBS, F/V first-call only, F/V second-call only, F/V **both** calls, F/V zero-call sham (plus O=Z root no-contact and impossible full64 decoy). Each selected arm is doubled cold. Evaluate **categorical bestmove** and separate full six-field UCI core. Baseline and passive discovery must be exactly equal; positive source gate contact and physical shadow writer payload equality are prerequisites, not evidence of root causality.

Explicitly record actual writer-serial age and search windows under intervention, as the search trajectory can diverge; don't infer cross-arm identity solely from within-arm call ID equality.

## Prospective predictions — deliberately risky

- **J1_STRICT_ELIGIBILITY:** at least one of sixteen sources has a STRICT pair within first 2048 source-positive events; zero => **FAIL**.
- **J2_STRICT_GROUP_ROOT:** at least one STRICT pair in the fixed sixteen actually fires both nominated source calls and changes final bestmove under V-both; none => **FAIL**, including no eligibility.
- **J3_STRICT_MINIMAL_INTERACTION:** among STRICT pairs, at least one physically realized two-call treatment changes bestmove while both single-call interventions do not. None => **FAIL**.
- **J4_BROAD_TRANSFER:** at least one BROAD pair physically realized under both-call V changes final bestmove; none => **FAIL**.
- **J5_SOURCE_WRITER_EVENT_CONGRUENCE:** all claimed interventions have matched preceding physical full64 last writer and unchanged raw TT payload; every reader_block obeys selected calls, age, bound, ply and narrow-window predicate. Violations => **FAIL-CLOSED**.
- **J6_NEGATIVE_CONTROL:** all O/Z entire UCI cores identical, impossible full64 decoy and empty mask no-contact with F exact core; any violation => **FAIL-CLOSED**.
- **J7_DENOMINATOR:** exactly sixteen source-game records and two selector records each, regardless eligibility; any loss => **HOLD**, no candidate replacement.
- **J8_TEST_NONINTERFERENCE:** passive profiling F produces exact native six-field UCI as F OBS (and cold repeat); deviation => **FAIL-CLOSED**.

A PASS only validates a finite conditional source intervention transport under SF16; it does not establish a natural TT causal pathway or an engine-independent chess semantic explanation. Each J1–J4 FAIL is a scientific falsification, not a CI failure; CI may succeed with false hypotheses.

## Reverse-engineering side products (nonselective)

For every source game preserve the first 2048 reader events and distributions of writer age, bound, ply, window width and root ownership; rate of repeated physical carriers; number of potential writer-preserving across-window pair candidates; root window_enter/exit and after_sort traces with truncation flags; per-arm actual TT reader_block and full candidate score/alpha margin. **These diagnostics are descriptive, not permission to retarget J1–J4 after outcomes.**
