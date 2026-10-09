# C3X 0.18 — P0/P1 Source-Level Writer Re-Decision and Same-Carrier Rescue Court

**2026-10-10; ADAPTIVE MECHANISM COURT, NOT ANOTHER INDEPENDENT JANUARY TEST.** Source cohort and all prior outcomes already examined. Original January blind-sixteen PGN SHA \`5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533\`. Complete earlier January pair outcomes SHA \`9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470\`. Full writer-epoch attrition source evidence SHA \`db5a780f463f88a87e222868a36c132aef4640020128210fb253d9a9bb323a88\`.

**Test source cases fixed here:** January game #2 STRICT (two source-selected root calls 4/5; physical writer target key64=10822490400377030283, slot0, epoch1). The same-source first V read led to an accepted payload rewrite of the same key+slot, epoch1→epoch2, writer_serial60→130. Test also game #6 BROAD (both selected reads survived, negative contrast). Never retarget to a successful source case.

## P0: TTEntry::save is the actual decision boundary

Stockfish16 commit \`68e1e9b3811e16cad014b590d7443b9063b3eb52\`. In frozen \`TTEntry::save(k,v,pv,b,d,m,ev)\`, **move preservation** and **payload replacement** are distinct paths. Record \`move_update=(m!=MOVE_NONE || key16(k)!=oldkey16)\` separately from \`would_payload_write=(b==BOUND_EXACT || key16(k)!=oldkey16 || d-DEPTH_OFFSET+2*pv>olddepth8-4)\`. Log input source request (k, value_to_tt-transformed v, b, d, pv, m, ev), old TT raw 10-byte snapshot, previous shadow full64 writer key/epoch/serial, root call/candidate, branch predicate bits, actual resulting payload, and writer serial after commit. Capture at most 40 matching proposals per cold process and mark censor. **No inference that an entry's numerical value equality proves writer identity.** Instrument the actual \`TTEntry::save\` condition, not guessed search calls. In baseline and V-first, verify that the candidate epoch1→epoch2 write is a true executed \`would_payload_write\` event (not merely a no-op save or move16-only update), and it occurs **after** the first V reader block and **before** second source root call's TT.probe. If false, the previously asserted causal story is HOLD.

## P1: two genuinely distinct writer versions counterfactuals

Use **the same** selected physical triple \`(key64,slot,epoch)\` and V FIRST / V BOTH event guard. Additional optional \`C3X018_P1_WRITE_POLICY\`:
- \`NONE\`: original source, no suppression or repair.
- \`SKIP\`: *after the targeted first V actual reader block*, **suppress precisely the first subsequent true TTEntry payload overwrite** at the same full64 key/slot whose previous physical slot epoch equals source selected epoch and whose newly proposed epoch is target+1. Record actual writer proposal and writer_skip; do not update move16 either for that suppressed save (explicitly different from normal no-payload save). A second writer attempt not matching the same original pre-epoch must be allowed.
- \`REINSTATE\`: permit the exact same first overwrite through Stockfish's original source \`TTEntry::save\` path, record its new physical writer epoch/serial and payload, then **immediately restore the old full raw TTEntry bytes and the corresponding shadow writer epoch/serial/snapshot** under a distinct logged \`writer_reinstate\` event. Preserve monotone global *write event* serial even though current resident writer ticket returns to the old resident state. This is a synthetic rescue of the old physical payload, not history playback or a real natural writer event. The counterfactual never writes unrelated slots.
- \`SHAM\`: same policy key but impossible full64 target; should not contact any matching resident and must equal V FIRST.
Store all original world F six-field UCI outcomes and root watcher TT probes, actual V reader blocks and physical last-writer snapshots in cold duplicate independent processes. Baseline F/OBS must reproduce original January six-field UCI; unfiltered first V must equal original January \`FIRST\` output. In \`BOTH\`, count first and second source reader V contacts under writer interventions and compare slot epochs at second root call (probe-level 64bit shadow full-key match, not native key16 hit alone).

### Exact fixed conditions

For source #2 STRICT test: F OBS, V FIRST, V BOTH, FIRST+SKIP, BOTH+SKIP, FIRST+REINSTATE, BOTH+REINSTATE, FIRST+SHAM (impossible full64 target); run each twice cold; allowed suppress/reinstate **at most one actual epoch+1 overwrite**. For case #6 BROAD test only F OBS, V BOTH and BOTH+SKIP, again twice cold; no success-case substitution. Always preserve every failed/partial-contact arm.

### Falsification gates (exploratory, declared before P0/P1 execution)

- **R0_SOURCE_SAVE_PREDICATE**: in #2 V FIRST, observed overwrite decision has exact Stockfish predicate and physically writes next epoch with full64 writer identity, between first actual V source block and second root call. Otherwise FAIL.
- **R1_SKIP_GATE_CONTACT**: #2 SKIP contacts *exactly one* qualified rewriter and leaves old resident writer epoch visible at next selected probe. Missing contact => NOT_TESTED, not restoration claim.
- **R2_REINSTATE_GATE_CONTACT**: #2 REINSTATE carries out one original accepted writer save, explicitly restores old raw entry+shadow payload and leaves old writer epoch visible to next selected probe. If only numerical value matches, FAIL.
- **R3_SECOND_READER_RECOVERY**: BOTH+SKIP or BOTH+REINSTATE physically recontacts the **second** selected source V evaluation reader that was lost in original BOTH. Zero => FAIL, irrespective of score/bestmove effect.
- **R4_SHAM_AND_BASELINE**: F OBS unchanged, impossible-target SHAM equals normal V FIRST and has zero writer contact.
- **R5_NEGATIVE_NO_REWRITE**: #6 BROAD, which originally had both source readers under V BOTH, should record no matching epoch+1 rewrite policy event; any relevant mismatch FAIL.
- **R6_NO_INFERENCE_BY_BESTMOVE**: report entire six-field UCI core and every TT V source reader, distinguish read restoration from categorical bestmove change; do not require a root bestmove flip.
- **R7_COLD_COMMIT**: same frozen Stockfish source and double cold deterministic executions, no trace censor, all paths and SHA artifacts retained; otherwise HOLD.

### Interpretation and strict limits

A skipped/reinstated write that restores second-reader contact shows that the original physical writer lifetime is a **conditional causal carrier** of that lost read, not that the original value was a sole natural mediator of final root bestmove. Counterfactual histories change the future search tree; same root-call number is not enough to guarantee equivalent recursive nodes. If SKIP and REINSTATE disagree, do not conflate store-event side effects, shadow serial age and byte restoration.

**Only after actual P0+P1 compile, execution and evidence receipts may a proposed 0.19 formal name be upgraded from a candidate to an opening recommendation.**