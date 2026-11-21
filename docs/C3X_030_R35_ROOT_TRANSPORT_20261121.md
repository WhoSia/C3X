# C3X 0.30 R35 — Two different native gate changes converge on the same root choice

**Classification:** new *retrospective* candidate-level analysis of previously recorded [R34 fixed-depth source logs](https://github.com/WhoSia/C3X/blob/abe5c039a57fc173fe75430ce50345bd99776f37/docs/C3X_030_R34_EQUAL_DEPTH_DIAGNOSIS_20261121.md). No new Stockfish execution, independent board engine score, or human data in this R35 audit. R34's 90 searches remain the original experimental provenance. This R35 work provides a signed matched-window link that R34 had identified as the next unresolved analysis.

## Source and controls

[Archived R34 raw ZIP](https://drive.google.com/file/d/1P9wTTfrFpVxslSH3gDl9KuWG0XZt6JB4/view) SHA-256: `c4f01a19665e7bb8781316e4f1a13d9a91c2cf4b0bf35eea5d962851c53f697a`. Verified ZIP CRC, rehashed **185** listed file entries from `SHA256SUMS`, repeated both controls and interventions. Two independent `-0/-1` recorded replays matched at each of the expected root and target events. Focus: R33-040, original fixed depth 12, **43 root moves** in each original attempt-24 record.

## Event-side difference (not a claim about board value)

| Feature | Null-ineligible stratum | Null-eligible stratum |
| --- | --- | --- |
| Physical event | No. **32**, attempt **20**, root `a5c7` (Qxc7) | No. **102**, attempt **24**, root `d4b3` (Nb3) |
| Original → intervention local return | `401 → 952` | `528 → 454` |
| Gate | Futility early return suppressed; one reply searched | Futility and null early returns suppressed; two replies searched |
| Same original final recommendation | `h2h3` (h3) | `h2h3` (h3) |
| Same intervened final recommendation | `a5c7` (Qxc7) | `a5c7` (Qxc7) |

Physical target *open* event fields were identical across the paired runs before the intervention. The event occurred in a different root branch and, in one stratum, four attempts before the decisive common-window comparison. Thus neither event was a direct evaluation of the eventual h3 root candidate.

## Where the root preference visibly changed

Both root search logs include **attempt 24, iteration 12, search window [367, 407]**, so compare at the *same* alpha and beta, rather than treating scores from the later aspiration retry as interchangeable.

| Root candidate in attempt 24 | Ordinary value, leader update | Null-ineligible mask | Null-eligible mask |
| --- | --- | --- | --- |
| First candidate `d4b3` (Nb3) | 367, 1 | 365, 1 | 362, 1 |
| Second candidate `a5c7` (Qxc7) | 366, 0 | 367, 0 | 367, 0 |
| Third candidate `h2h3` (h3) | **392, 1** | **363, 0** | **367, 0** |
| Attempt-24 returned move/value | **h3 / 392** | **Nb3 / 367** | **Nb3 / 367** |
| Next attempt | None | **25, [341, 387]** | **25, [341, 387]** |
| Attempt-25 returned move/value | Not run | **Qxc7 / 375** | **Qxc7 / 371** |

In both treatments, `h3` lost the local active-leader `update` at the **same 367 lower threshold**, while an additional aspiration attempt became necessary and produced Qxc7. This is a concrete, matched-window *root-competition witness* downstream of the manipulated event. The first changed candidate's numerical return occurred even earlier at Nb3 (count 1, both worlds); do not report h3 as the first changed candidate. Furthermore the two treated runs have different node counts; matching the alpha-beta window is **not** a claim that the intermediate search states are identical.

No subtraction in this table is a calibrated measure of strategic centipawn advantage. The value 367 at the lower edge of an aspiration window can be a bound-limited return, not an exact candidate strength. The independent board preference and the causal mechanism of the event-to-root *mediator* remain unproven.

## Mechanistic interpretation and counterexample

The instrumented native local early return is *causally manipulated* within a matched event and the next observed h3 root update and ultimate recommendation change in the full replay. The **total effect** is supported. The existence of two source-branch routes to the same terminal preference is incompatible with an explanation that simply identifies the final move's PV as the sole source of its selection. Nevertheless the precise transport channel (intervening TT write/read, main-history, stack heuristics, node allocation or interaction) is **not** singled out by this audit.

R32 already showed a nested g5 window that opened or suppressed 43.b5 while leaving Kg7's PV return unchanged. R35 offers a complementary mechanism: in *new* TWIC 1671 positions, separately nominated early returns ultimately change the *same* later root h3 candidate update in the same aspiration window. These results are linked by a general **decision-state dependence**, not by assuming a common exact search operator or verified board plan.

## The higher-level Explainable Stockfish decision

1. **Trace a producer rather than explain a number:** identify the physical event, its immediate target, the first comparable downstream root candidate, the changed attempt sequence and the terminal engine move. The indicator `update` is local and should not be called a proof of exact move ranking.
2. **Prove mediation selectively:** R35's next native experiment should log potential write/read chains and move-order/history updates from event 32 (attempt 20) and event 102 (attempt 24) to the h3 call in attempt 24. A state-replay intervention must be designed against a fixed pre-treatment checkpoint and must not silently alter node allocation or copy cached bounds from incompatible attempts.
3. **Restore the chess and learner legs:** Referee-evaluate the actual Qxc7 and h3 candidates under multiple *legal opponent replies* at two depths, verify a board-level claim and counterexample, and test whether displaying the true traced source mechanism improves *new-reply prediction* beyond equal-length board-only and public-PV explanations. None of these has yet been established for this position.

**Scope:** This is one exposed game / two correlated interventions, not an independent two-case generalization or a new engine benchmark. Do not increment a win count merely because both treatments end in Qxc7. This audit supplements the parallel [R33 source-public-gap historical cross-cohort audit](https://github.com/WhoSia/C3X/tree/research/c3x-r33-source-public-gap) (R29+R30); those 57 historical events are also not independent of one another. [Full R33 new-game gate-panel](https://github.com/WhoSia/C3X/blob/7787590a595fbb225fde7d80e8a60b98b8a798d2/docs/C3X_030_R33_FRESH_TWIC1671_GATE_PANEL_RESULTS_20261121.md) and [R34 fixed-depth follow-up](https://github.com/WhoSia/C3X/blob/abe5c039a57fc173fe75430ce50345bd99776f37/docs/C3X_030_R34_EQUAL_DEPTH_DIAGNOSIS_20261121.md) remain the native experimental records.

## Reproduce

```sh
PYTHONPATH=harness python harness/c3x_030_r35_root_lineage.py R34-fixed-depth.zip r35-root.json
C3X_R34_ZIP=R34-fixed-depth.zip PYTHONPATH=harness python -m unittest -v tests.test_c3x_030_r35_root_lineage
```

The Python parser verifies all 185 manifest files, the two source-gate locations and returns, all 43 attempt-24 candidates in each replay, the unchanged alpha-beta window, the h3 update transition, the aspiration retry and final Qxc7. Five local regression tests pass.
