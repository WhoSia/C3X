# C3X 0.19 — Two Noninterchangeable Sufficient States: Native Engine Transition and Analyst-Targeted Intervention

**Status:** mechanism interpretation after [native orthogonal factorial](../receipts/c3x-019-P0-orthogonal-TT-payload-shadow-and-native-eval-use-20261010.json); a local source-inspection result plus a single adaptive empirical illustration, **NOT** a new universal law of chess or all engines.

## Definition: local native TT evaluation branch

Freeze full native search state E at the instant of the original Stockfish16 TT value-as-evaluation conditional, including the Position and complete TT raw packed entry, ttHit, decoded TT value, native static evaluation, PvNode, current alpha/beta, depth and stack/control-flow predicates. The actual main-search source condition is: cached value must be non-NONE and the stored TT bound must support substituting that value in the evaluation comparison. Only when the original assignment of eval=ttValue executes does the engine actually use the cached search value as the evaluation estimate. The quiescence counterpart assigns bestValue=ttValue. These are source-control-flow facts, not claims of root-bestmove mediation.

Call U(E) the boolean of that *actual original assignment* in the absence of the C3X experimental V suppression. Note that the stock packed TTEntry holds key16, depth8, generation/bound bits, move16, value16, eval16. **It has no full64 last-writer key, no slot-local write epoch and no globally accepted-writer serial.** Those last three are C3X observability sidecars.

## Definition: analyst-selected physical old-version gate

Let L be the independent full64 shadow writer log and q=(key64, slot, old epoch) a selected physical provenance target. The C3X V gate chooses whether to suppress a TT candidate by G(E,L,q,c), with c including root-call, candidate, ply, bound, writer age and window width. The source implementation **explicitly tests L.epoch**.

A source V reader_block means G=1 and the selected assignment is prevented: it is not an observation of U=1 in that arm. An intervention that changes only L may change G but should not be treated as changing the native packed TTEntry bytes.

## Local functional non-equivalence

Within unchanged native E, alternate valid analytical writer shadow versions L1 and L2 cannot alter the native original TT use *decision* by themselves, because the original SF16 branch does not consult the C3X sidecar. But L1 and L2 can alter the experimental gate G and thus **change the result of the V-controlled engine**, because V has an extra shadow-dependent predicate. This is an instrumentation-dependent distinction, not an invariant claim over dynamic search trajectories or scheduling. In particular, an invalid SHADOW_ONLY shadow/payload mismatch is solely a destructive measurement test.

## Native observational verification — January game 2

Prior first V intervention causes a real source TTEntry::save overwrite, physical shadow writer epoch1→2 and raw depth0→1 while value=-89, LOWER bound and static eval=-284 remain equal. Under NONE in the new second root call, the V old-epoch gate is silent while source-post-assignment native evaluation use executes once. Under SHADOW_ONLY, old-epoch V reader_block reappears despite raw depth1 and mismatched analytical writer snapshot. Under BYTES_ONLY, old depth0 returns but the V old-epoch gate is silent. When the second call is allowed to run, all five treatment states execute the native source assignment once. Source native 10-arm controls and two cold process repeats all PASS.

Therefore native TT score usage and physical writer-age-targeted suppression have **different quotient state requirements**. A sufficient equivalence class for merely addressing an old analytical gate is not necessarily sufficient for native value semantics; conversely a new writer version can still provide identical native score use. Neither quotient alone identifies an explanation for final bestmove.

## Phase-methodological gates

1. Separate **physical last writer** identification, **native read/use** identification, and **final root choice effect**; do not silently substitute one for another.
2. Retain full64 shadow/TT payload integrity checks for source writer identity, but do not impose last-writer-version equality as a requirement for native TT use.
3. Preserve failures including prospective January J2/J3/J4 and old unbounded P1 R5.
4. A meaningful 0.19 law needs new blinded source data, true assignment-level witnesses, writer-version interventions and noninterference controls. The adaptive January full-31 survival diagnostic is descriptive and may fail; no retargeting permitted.
5. Always name selection truncation (first 2048 source TT readers) and role-arm overlap before inferring prevalence.
