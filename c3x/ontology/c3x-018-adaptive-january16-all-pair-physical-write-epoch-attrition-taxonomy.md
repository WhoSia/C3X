# C3X 0.18 — Full January Source TT Probe, Writer Epoch and Consumer-Attrition Taxonomy

**Status: ADAPTIVE ALL-SAMPLE SOURCE DIAGNOSIS AFTER THE PROSPECTIVE JANUARY J2/J3/J4 FAIL.** Frozen January full game source SHA 5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533 and previously sealed source-pair native experiment SHA 9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470. Source rule selection unchanged. Do not claim independent hypothesis confirmation.

## Fixed denominator and intervention

For **all 31 preregistered STRICT/BROAD eligible selector arms among all 16 January games** (25 distinct physical game-target-call pairs; six selected twice under both selectors), compare cold duplicated:
- F/OBS native source with passive probe watcher for the selected full64 TT key at the selected *second* root call,
- F/V-BOTH with exact original two-call, original physical triple, original role-specific age/bound/ply/window/root-candidate filters,
- Retain source O/F/Z baseline and first/second interventions as originally frozen artifacts, not reselect.

The independent original engine output, actual number of blocked V readers, and source candidate root-call handles must match the frozen previous court. A side-effect in passive instrumentation or nonrepeatable cold run is technical HOLD.

## Source stage and witness

Frozen Stockfish16 source and P4, native TT full64 shadow writer serial and slot-local write epoch, main/qsearch TT.probe, and read-only watcher bound to the passive selected key and second root-call handle. Record native TT-probe hit, physical slot, full64 shadow writer key, shadow epoch and last accepted writer serial, raw value/eval/bound/depth, search ply and alpha-beta. Each watcher capped 64 records/process and does not alter TT state.

Before source outcomes, these **mutually exclusive primary diagnostics** are fixed for second root calls where the joint intervention did not block a second source reader:
1. **NO_TT_KEY_PROBE**: the second root search window entered, but full64 key was not probed there.
2. **TT_KEY_PROBE_ONLY_MISS**: exact key was probed but all probes returned native miss.
3. **KEY16_HIT_WRONG_FULL64_SHADOW**: at least one key hit but no probe had matching full64 shadow writer key, so native key16 hit is not reliable full-key writer identity.
4. **SAME_KEY_DIFFERENT_PHYSICAL_EPOCH**: a probe of exact key/slot with full64 shadow matching, but actual slot epoch differs from selected original epoch.
5. **SAME_CARRIER_BUT_EVAL_CONSUMER_INELIGIBLE**: source original full64 key/slot/epoch still exists at a probe, but bound-qualified TT score-as-evaluation consumer wasn't eligible (or event guard no longer matched).
6. **OTHER_COMPLEX_MULTIPROBE**: mixed or unclassifiable 64-probe stream; retain all original records and explain individually.

If the joint intervention blocks both nominated consumers, label **DUAL_READER_ACTUAL_CONTACT** rather than attrition. A hit/epoch change is not proof that every recursion node is identical between arms.

## Risky adaptive predictions

- **TAX1_EPOCH_CHURN_PREDOMINANCE**: at least 15 of 29 previous one-block arms are explained by same-key different physical epoch, else FAIL.
- **TAX2_FULL_KEY_MATCH**: all claimed same-key-epoch routes have full64 matching source writer shadows; else FAIL.
- **TAX3_HISTORICAL_OUTCOME_NONINTERFERENCE**: native F and pair UCI cores exactly match all original 31 role arms, and double cold results stable; else technical HOLD.
- **TAX4_DENOMINATOR**: all original 31 role-arm targets retained and all 16 games represented; no failures hidden.

This is explanatory analysis on *already observed* negative transport cases; positive TAX1 does not rescue failed independent J2/J3/J4. It will support a more precise next-cohort writer-version stability requirement, predeclared before any new holdout outcomes.
