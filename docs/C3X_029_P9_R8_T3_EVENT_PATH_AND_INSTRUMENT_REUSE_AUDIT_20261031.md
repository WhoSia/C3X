# C3X 0.29-P9-R8 — T3 Event-Level Restoration and Instrumentation Reuse Audit

2026-10-31. Read original T3, C3a, C3b and posthoc R3 harness source and native receipts. ARCHIVAL STATIC CODE/RECEIPT AUDIT ONLY. No private artifact downloaded, no Stockfish binary executed, no per-event replay.

## Crucial recovered experiment
The missing follow-up WAS ALREADY DONE in 0.24-P2-R3: c3x/receipts/c3x-024-P2-R3-source-root-candidate-reached-but-not-final-and-May11-partial-20261011.json.
Among two development positions x 4 native worlds: 4 SEE-guard continue; 2 fully traced source-to-root candidate paths which LOST final bestmove (May game2 O/STRICT, sham TT0/TT1); 2 partial paths (May game11 F/STRICT SEE_FLIP TT0/TT1). Zero fully traced root candidate matching final bestmove. This is actual historical source evidence, not a new run.

## Code-level audit and reuse
1. T3 entry: harness/c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court.py. ELIGIBLE locks (11,F,STRICT) and (2,O,STRICT). T3_FIELDS includes key64/parent_key64, t1_path, root_call, root_move, move, site, threshold, ply/depth/alpha/beta/PV/qsearch/rule50/occupied, original SEE Boolean. Both SHAM worlds checked BEFORE active mutation, then SEE-alone and joint; physical writer/reader and cold exact replay required.
2. Rebuild script: tools/c3x_023_P1_R2_T3_native_repro_build.sh pins Stockfish16 SHA 68e1e9b3811e16cad014b590d7443b9063b52 and layers original TT, SEE, source actor and T3 precise boolean actuator patches, then builds locally. Need protect existing source hashes; not a trivial mix-and-match new overlay.
3. C3a: harness/c3x_024_P2_exact_native_descendant_source_certificate_court.py verifies exact SEE guard->DO_MOVE->CHILD_ENTERED->CHILD_RETURNED sequence and native parent/child keys; a guard CONTINUE has a distinct one-event certificate rather than a missing-path error. 2 cold runs and exact T3 (bestmove,nodes,cp) noninterference checked.
4. C3b: harness/c3x_024_P2_R2_actual_ancestor_root_survival_court.py has explicit sequence checks for ANCESTOR_SNAPSHOT, CHILD_VALUE_RETURNED, PARENT_CANDIDATE_VALUE, FRAME_RETURN, ROOT_FRAME_RETURN. Full certificate is limited to matched same-rootcall events, and does NOT flag winner causality.
5. R3: harness/c3x_024_P2_R3_root_candidate_survival_and_partial_ancestry_diag.py maps encoded native root move to legal UCI, compares with final bestmove; original receipt confirms 2 reached-but-lost, 2 partial, 4 continue.
6. 0.25 P13-R4 patch tools/c3x_025_P13_R4_original_writer_to_q_assignment_overlay.py depends on exact P8->P11->P12 source patch chain; it observes the qsearch recursive child assignment and qsearch bestValue event, not arbitrary Main/LMR/PV. It is NOT plug-compatible with complex 0.23 T3 C++ patch stack without an anchor and reversibility audit. It ran at public starting board depth7, not May game2.

## Exact missing distinction
For May game2 O/STRICT, sham path reached a ROOT CANDIDATE and LOST. Joint TT1+SEEflip selected b1b4, yet its targeted guard was ACTUAL_CONTINUE (not the same exact C3a pass path). Therefore the hypothesis 'the fully traced guard child becomes winning b1b4' is NOT SUPPORTED by the actual source certificate. Direct joint outcome is valid, but its decisive candidate state must be sought on another source-aligned path.

For May game11 F/STRICT, the two SEE_FLIP partial footprints stop after ply2 FRAME_RETURN without a higher-parent candidate edge. No promotion to root, no assertion that downstream propagation did not occur.

## Reuse decision
READY archival reuse: T3 presealed target identity, TT full64 contact, T3 cold controls, C3a guard/child status, C3b root-candidate path classifier, R3 lost-vs-won legal UCI comparison.
CONDITIONAL source port: P13 qsearch score assignment (different patch base, only qsearch direct recursive TT child) and any root scoring/aspiration instrument. Requires correct engine source code anchor, exact reverse-to-original checks, original baseline bestmove/nodes/score parity, TT and SEE target unmodified, full event-censorship counters.
NOT ALLOWED: combine public P13 startpos events with May T3 root ancestry; call an observed path a uniquely mediated effect; assume guard CONTINUE implies that selected move was never searched by other routes.

## Specific new experiment gate
Choose May game2 O STRICT, predeclare competitor: (i) altered root candidate processing or complete search in joint world versus (ii) already-searched candidate wins via bound/score/window/carryover difference. Observe root-candidate `b1b4` search-start, completion, value/score bound, aspiration attempt, RootMove update under all 4 native arm worlds; take game11 negative, maintain identical 0.23 original source and protected May board. Distinguish potentially overlapping mechanisms per-depth, not full-execution mutually exclusive.
If private native event artifacts inaccessible, mark ACCESS HOLD, not NO_EVENT. New code must not redisclose full PGN/player metadata/private keys/modified binary.

## Scientific scope
Historical evidence recovery and code compatibility audit only; no new native result, not a novel causal theorem. Heldout M2/M3 failures and source licensing unchanged.
