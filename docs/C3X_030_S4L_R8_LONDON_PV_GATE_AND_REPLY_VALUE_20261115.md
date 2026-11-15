# C3X 0.30 S4-L/R8 — London PV re-search and independent reply value

2026-11-15 KST. The test uses only the exposed London ply8 development history. [R7](C3X_030_S4L_R7_ROOT_CANDIDATE_SET_RESULTS_20261115.md).

## 1. The Nd2 PV gate matters in the full-menu state

The two menus differ at the very first root edge: with a3 it is searched first and returns −59, while without it a4 returns −104. Bxd6 then reaches +1 in both. For depth-8 runs, iterations 2–7 agree on the ordered shared-root receipt fields (move, value, alpha, beta, adjusted depth), ignoring a3 and process-local IDs. This comparison does not assert equality of hidden state or child search. On the first iteration-8 aspiration attempt, the second examined move, Nd2, yields +6 (full) and 0 (minus a3) in separate null-window calls at alpha 0, beta 10 and root adjusted depth 6. This leads to a PV re-search only in the full control.

Interchange those null-window values immediately before the PV predicate, leaving preceding child computation in place. Sham and identity controls reproduce all archived UCI tuples. Twenty-six Stockfish searches including donor setup per pass, 267,388 reported nodes, identical normalized replay in fresh processes.

| Menu | Sham | Interchange | Depth 8 and 12k requested nodes |
| --- | --- | --- | --- |
| Full | Nd2, +6 probe, actual PV return +14 in the first aspiration attempt | Force 0. The PV re-search is skipped | Ne5 in both |
| Full minus a3 | Ne5, 0 probe | Force +6. The resulting PV re-search returns 0 in that attempt | Ne5 in both |

At the reached source site, the +6 probe is necessary relative to the 0 substitution for the observed full-menu choice; a positive gate input is insufficient in the reduced menu. The two arms can have different state before the gate. This isolates one asymmetric local dependency and leaves the path from a3 to the discrepant PV result open. Units in this table are internal, not UCI cp.

## 2. Independent evaluator checks the exact same legal history

Berserk 14 at `8ae895a6151695be4a50d4fb65b0c131659c513a`, network SHA-256 `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`. One thread and 16 MiB hash, new game per call, preserve complete move history. Exhaust all 35 legal Black replies after Nd2 and 32 after Ne5. In each grid include two free-response evaluations per candidate, one per stopping level. At 48k/96k requested nodes, just 29 of 134 forced-reply reports passed the existing 90% node-floor receipt check. Treat this as sparse comparable coverage. Separately run fixed-depth 10/12, retaining each arm's actual nodes and requiring the reported depth. 138 searches per grid and all 134 depth-grid forced replies and four free evaluations are eligible and unbounded; fixed-depth normalized replay matches byte-for-byte. Values are White-perspective cp in Berserk's scale.

| Depth | Free after Nd2 | Free after Ne5 | Minimum over replies after Nd2 | Minimum over replies after Ne5 |
| --- | ---: | ---: | ---: | ---: |
| 10 | +13 | +11 | 0 (Bxf4 or O-O) | +23 (a6) |
| 12 | +6 | +4 | +3 (O-O) | +1 (O-O) |

At equal depth the free and forced designs can disagree because the forced runs start after the reply, with their own search state and a different effective horizon from the common root. At depth 12 the minimum difference is 2 cp and its sign changes between depths. Comparing common reply identities individually gives Nd2 higher at 10/32 and 9/32 replies at depths 10/12, respectively, with no ties. Ne5 permits neither Bxf4, e5 nor Kd7 here, so a shared-reply comparison omits actual differences between the two legal response sets. Local causal evidence does not license a stable strategic preference. No sealed cases used.

## 3. Research unit and next discriminant

The current Research OS Method Shelf, Runtime Bootstrap, RAVEL and Drive-first custody texts were checked with C3X governance, two-track constitution and the C3X 28/33 archive. Complete research questions before aggregating: R8 conducts a reciprocal native intervention and a separate independent reply-value test. Preserve the sparse node-budget result. For the next source test, replay a PV-only return intervention at the native gate while measuring the changed path, then compare its predictions on new game histories against reply-tree and PV baselines. The stable-engine and strategic claims require their own evidence.

The baseline R4 binary SHA-256 is `3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb`. Apply the [R8 overlay](../harness/c3x_030_s4l_r8_london_probe_patch.py) to the exact R4 search source and rebuild as in R4. Patched Stockfish binary SHA-256 `66e33016b614c5c5ca8edcdf982fc122c7962c1af29e8b272426ec6ddca79d6d`, Berserk binary SHA-256 `93b5d5f0e48b2952490949f83dc750a6715dbac9e9e245be14318c1db3d01a23`. [Native runner](../harness/c3x_030_s4l_r8_london_probe.py) · [Reply runner](../harness/c3x_030_s4l_r8_london_replies.py). Existing root and independent-receipt tests passed 25/25.

[Verified raw capsule](https://drive.google.com/file/d/1lbeZKwXTQpVxKgm3c0ovOElV4XMTfoqF/view). ZIP SHA-256 `474ad798081831e2b26ea1d50cbdf1cffc9454b16db9aec8b48096f2acd23f0b`, independently read back from Drive. Stockfish normalized SHA-256 `9896f8b7278fe85fcc3c71931ce80fd8cb83cc9484630d8a69c878cab7c1e893`; fixed-depth Berserk normalized SHA-256 `85c24f99224ad081f889589705f3bb87ce0ce67228461f890e0fd7480840838c`.
