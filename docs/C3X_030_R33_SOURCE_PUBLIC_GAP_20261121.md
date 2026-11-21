# C3X 0.30 R33 — Source/GUI Evidence Gap and the limits of local causal explanation

**Research classification:** retrospective cross-cohort *reanalysis* of already published R29/R30 native engine experiments, not a new Stockfish run or a prospective generalization test. Latest source-mechanism extension: [R32 Bc6 carryover](https://github.com/WhoSia/C3X/blob/research/c3x-r32-bc6-carryover/docs/C3X_030_R32_BC6_RESULTS_20261121.md). This report audits where the visible UCI score/PV is insufficient, and where a true local intervention still cannot explain the final decision or its chess merit.

## Evidence custody and gates

Original raw sources, downloaded again from user Research OS:

| Source | SHA-256 ZIP | Manifest files independently rehashed | Positions |
| --- | --- | ---: | ---: |
| [R29 TWIC 1663](https://drive.google.com/file/d/11KYIlnfneW4Dg8YxKLYgs1LUbafnibO2/view) | `f6ed3cfc7755cee49f6f13a4bc86ac116bd947dd963cc3465a7658ee5c5ff6e3` | 300 | 32 |
| [R30 TWIC 1664](https://drive.google.com/file/d/1BMSvffPHCzNQXpSjpQlxD9BihJwn8neM/view) | `b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e` | 262 | 32 |

Both ZIP CRC checks and listed per-file SHA-256 matches passed. Every selected event had an exactly matched `sham → mask → restore` receipt; the script verifies physical read identity before masking, root candidate windows, final UCI `bestmove`, terminal score type, bound and last public value, and score/PV restoration. Missing, stopped or nonmatching child probes remain unobserved rather than negative.

A **public-score/PV trajectory** here means, for each emitted UCI `info depth` line, `(depth, multipv, score kind, value, upper/lower/exact bound, full PV moves)` and terminal bestmove. It intentionally excludes nodes, time, seldepth, hashfull, nps and other GUI-visible metadata. Thus *score/PV unchanged* does not mean the entire GUI or UCI stream is unchanged.

## Main observations

| Verified endpoint | R29 | R30 | Combined |
| --- | ---: | ---: | ---: |
| Frozen positions | 32 | 32 | **64** |
| Positions with selected events | 22 | 29 | **51** |
| Selected physical TT interventions | 25 | 32 | **57** |
| Complete directly observed child-return change | 9 | 19 | **28** |
| Direct-child comparison stopped/unobservable | 2 | 0 | **2** |
| Child changed but public score/PV trajectory + final move remained identical | 2 | 13 | **15** |
| Entire public score/PV trajectory + final move identical | 16 | 25 | **41** |
| Local candidate leader `update` flag flipped at the same alpha | 1 | 1 | **2** |
| Final `bestmove` changed | 2 | 1 | **3** |
| Original producing *attempt number* changed | 6 | 5 | **11** |
| Producer **attempt or event ID** changed | 7 | 6 | **13** |

**Key falsifications:**

1. **“No visible score/PV change ⇒ no computation change” is false in this trace collection.** Fifteen of the 28 completed changed-child returns retained *every* public depth-score-bound-PV line and the same final move, despite a single native TT read being removed and restored. These are specific interventions, not 15 independent games; no population prevalence is implied. R30 contributes 13/19, R29 2/9. That contrast is descriptive and reflects different selectors/cohorts, not a controlled field effect.
2. **“A local candidate becomes or ceases to be the leader ⇒ the engine changes its recommended move” is false.** R29-018 changed the Qd6 local update from 0→1 at the same alpha, while final Qe7 survived. R30-028 changed the h7g6 candidate update from 1→0 at the same alpha, while final d7f6 survived. Both are concrete negative root-transport witnesses.
3. **“An event-caused final move flip ⇒ the replacement move is strategically superior” is unsupported.** R29-029 flipped a5b4→d8e6, R29-030 f1e2→a2a3, R30-017 e2f3→e2d3. In all three, the original *reference candidate pair* was labeled **unresolved** by the independent Berserk depth comparisons; moreover R30-017's new winner `e2d3` was **not one of the two independently judged reference moves**. It must be separately judged before assigning even an independent relative value to that third move.
4. **“The directly observed child-return value is the final candidate score” is false as a general inference.** For instance, R30-028 had a reduced-child report that did not equal the later root candidate record, and its changed root update still did not reach the final output. Alpha–beta upper/lower bounds are *not* comparable point estimates.

### Signed cross-endpoint examples

| Position | Actual native intervention endpoint | Public/root endpoint | What an explanation may claim |
| --- | --- | --- | --- |
| R29-006 / R29-021 | Verified changed child return | All depth-score-PV lines identical, same final move | The selected TT read changed a computed return; *not* the recommendation |
| R30-001, -002, -004, -006, -007, -009, -010, -014, -019, -021, -023, -025, -032 | Verified changed child return | Same public depth-score-PV trajectory and final move | Native logs provide additional evidence beyond the public score and PV alone |
| R29-018 | Qd6's same-alpha local `update` flipped 0→1 | Final Qe7 | Local leader update is not sufficient for a final recommendation switch |
| R30-028 | Target update flipped 1→0 | Final d7f6 | Changed local competition can have zero final-move effect |
| R29-029 / -030 | TT read changed a child return; final move switched | Final winner in original candidate pair | Deterministic total effect observed, mediation and objective chess benefit not established |
| R30-017 | TT read changed child return; final winner switched | Qf3→Qd3, a **third** move beyond independently judged pair | Do not invent a judge result for Qd3; evaluate the third candidate separately |

These cases supplement R32: **R32 also demonstrates the converse shape**, namely a preserved Kg7 PV return of 1952 alongside a changed *later* root winner through the singular search threshold, a nested g5 futility/null-move branch and subsequent state reuse. Source explanations therefore need a causal evidence graph with explicit unknown transport links, rather than treating a PV score as a sufficient statistic for the search.

## Why this matters to Explainable Stockfish

The **explanandum** is *why this actual engine execution recommended this move over the relevant alternatives*, under the specified exact move history, binary, NNUE, budget, and search state. The user-facing **chess justification** (a threat or plan that survives unseen replies) is a separate claim. We should support five evidence levels independently:

1. **Reported:** root move, score *and whether bounded*, PV, budget, game history.
2. **Observed:** specific native event and its child's return, matching physical read and replay.
3. **Intervened:** one named event removed/restored with same-prefix controls, plus local change.
4. **Transported:** changed root candidate/producer with signed tracing; final-choice total effect must not be conflated with the whole mediation chain.
5. **Externally usable:** independent judge of *all actual candidate moves*, board-level threat/plan predicates, and blinded human transfer outcomes on unseen replies.

A successful explanation need not always reach level five, but it must *not silently claim it has*. When public PV stays fixed, a native panel can give an additional mechanistic observation; whether this improves a learner's choice under novel replies remains unmeasured. These are R33's *model requirements*, not human results.

## Future held-out gates (separate R33/R34 native work already completed)

The independently executed [R33 TWIC1671 native panel](https://github.com/WhoSia/C3X/blob/7787590a595fbb225fde7d80e8a60b98b8a798d2/docs/C3X_030_R33_FRESH_TWIC1671_GATE_PANEL_RESULTS_20261121.md) contains 128 selected early-return events on 64 frozen new positions. Its [R34 equal-depth follow-up](https://github.com/WhoSia/C3X/blob/abe5c039a57fc173fe75430ce50345bd99776f37/docs/C3X_030_R34_EQUAL_DEPTH_DIAGNOSIS_20261121.md) tested 11 changed-choice events, with eight persisting at the originally completed fixed depth. Those are **separate experimental findings and were not created or counted by this R29/R30 cross-cohort audit**. The present gates apply to a future held-out cohort, not to the already completed R34.

**Selection and abstention first.** Acquire a previously unused PGN issue/event outside TWIC1663 (R29), TWIC1664 (R30), TWIC1671 (the independently completed native R33), the exposed R32 fixture, and R34's retrospective diagnostic cases. Freeze the archive hash, FEN+history, 32k budget, engine/NNUE checksums, and full denominator. Select cases without peeking at mask effects, including close, large, rank-reversing and unavailable-score strata, and record every event-selection miss.

**Mechanism and negative controls.** Within exact source attempts, test source-observed TT reads, stored score/bound/depth, singular threshold, nested futile/null gates, and any subsequent state update *only when a physical target is present*. Require untouched native runs, sham, one-read mask, restored read, logging-only parity and repeated stdout/stderr. Include a group where direct children change and the final choice stays constant. Test a **same-child-value, different-future-choice** witness like R32, but regard historical discovery as developmental.

**Whole chess comparison.** Run an independent engine on every *actual* root winner including any third move; keep bound labels separate, adjudicate robustly across multiple legal opponent replies and at two referee depths; give human-facing plans only after legal board checks. R30-017 should be an explicit third-candidate check, not silently scored from Qf3-versus-a3 data.

**Learning transfer.** Use the existing R31 randomized A/B/C/D learner packet, record a pre-explanation choice, lock matched length and required reading time, hide the source panel during test, and ask for the threat and correct conditional plan under both same-game and independent-game opponent replies. Compare B vs C for the incremental effect of true source provenance and C vs D for native vs public computational evidence. There are no participant data from R33.

## Reproduction

```sh
PYTHONPATH=harness python harness/r33_cross_cohort.py \
  R29-native-unseen.zip R30-twic1664.zip r33-evidence.json
PYTHONPATH=harness C3X_R29_ZIP=R29-native-unseen.zip \
  C3X_R30_ZIP=R30-twic1664.zip python -m unittest -v tests.test_r33_cross_cohort
```

The report counts **only** the original 57 interventions in 51 selected positions; it does not double-count the repeated executions or R32's development tests. Source archive identity and every row-level evidence gate are reproducible from the separate, SHA-sealed R33 derived JSON and test package.
