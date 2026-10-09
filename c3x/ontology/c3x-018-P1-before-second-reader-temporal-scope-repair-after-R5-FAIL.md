# C3X 0.18 P0/P1 Follow-up — Rescue Writer Gate Must Precede the Selected Second Reader

**Adaptive refinement after first P0/P1 native CI #37995253598.** Preserve first native R5 **FAIL** permanently. Its "negative" game6 had no physical writer change before selected second reader call11, but an unrelated accepted save proposal in root call15 of the same old key/slot/epoch was suppressed by the original unbounded-after-first policy. The old R5 thus failed legitimately: the writer actuator was too broad in time.

**Revised causal treatment contract before re-running:** Keep exactly the old full64 key/slot/epoch for frozen January games #2 STRICT (root calls 4/5) and #6 BROAD (root calls 10/11), unchanged source cohort and source-pair targets. Same cold depth12 SF16 source and TTEntry layout. First actual source V reader block must occur; writer suppression/reinstatement can fire at most once, only when previous TT slot epoch matches selected old writer **and** the current source root call is between the first and *second* nominated call inclusive. A save in root call15 of game6 cannot affect the already-past second reader and must not be targeted.

The **only** new source guard is \`C3X018_P1_LAST_CALL=<selected-second-root-call>\`, tested after true overwrite predicate and actual first reader contact. Normal OBS, V FIRST, V BOTH, no-target SHAM and original source P0 logging preserved. All complete UCI results for passive and unmodified V must equal the original SHA-pinned January evidence and first P0/P1 CI. Duplicate cold runs every arm.

## Fixed outcomes / falsifiers
- **G1_GAME2_TIMED_WRITER:** exact real depth-driven overwrite selected after first V at root call4, BEFORE second call5. SKIP and REINSTATE each contact one correct source write and restore old full64 physical writer epoch1 and serial60 at second call5's TT.probe; BOTH/second source TT V evaluation read actually recovers.
- **G2_GAME6_PRESECOND_SHAM:** both game6 original readers remain fired, and SKIP no longer suppresses any save through its second selected root call11, regardless of future rootcall15 save proposals.
- **G3_NATIVE_NO_DRIFT:** all original passive source F and unmodified FIRST/BOTH UCI and native TT read events equal previous source results; all new arms cold repeat exactly, source fingerprint attached.
- **G4_NO_OVERREACH:** skip/reinstate only one eligible true overwrite before/equal second source root call, with P0 exact predicate bits logged.
- **G5_ROOT_SCOPE:** same key/slot/epoch and both original source root-call handles unchanged. Any other source calls or keys in proposal logs cannot become an alternate intervention.
- **G6_DISCLOSURE:** earlier R5 FAIL from #37995253598 not converted to a previous PASS; this is a later *refined operator*, not independent new-game confirmation.

Do **not** assert rescue of final categorical bestmove or natural mediation if source UCI remains unchanged. Retain all technical failures and separate this adaptive P1 operator from original January J2/J3/J4 independent FAIL.