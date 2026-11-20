# C3X 0.30 R30 — Re-audit of causal transport in the R29 TT-event panel

Date: 2026-11-21 KST. **This is a retrospective reanalysis of previously exposed R29 traces, not a fresh engine experiment, new independent cohort, or human outcome.** R29 remains the underlying experimental series. New code: [endpoint audit](../harness/c3x_030_r30_endpoint_audit.py), [six fail-closed tests](../harness/test_c3x_030_r30_endpoint_audit.py).

## Custody, exact inputs and execution

Re-downloaded the user-archived R29 native ZIP from [Drive](https://drive.google.com/file/d/11KYIlnfneW4Dg8YxKLYgs1LUbafnibO2/view); ZIP CRC check passed, and the internal SHA256SUMS entries for the two inputs matched:

- `unseen-logs/result.json` SHA-256 `e094e8706b90fc04dc2a1cec79e8baffd7c17ea330ad54952e29514b3e5b1828`.
- `abstentions.json` SHA-256 `d0539dc3cfc7db0f2d19db8c6744531c0dacc961682629fec0a6000d3767e976`.
- ZIP SHA-256 `f6ed3cfc7755cee49f6f13a4bc86ac116bd947dd963cc3465a7658ee5c5ff6e3`.

Run from the repository root with `PYTHONPATH=harness python harness/c3x_030_r30_endpoint_audit.py path/to/unseen-logs/result.json path/to/abstentions.json r30-audit.json`. The audit refuses mismatched sham/restoration, different pre-treatment read identity, masking more than one read, an event following the baseline producer, and an incomplete abstention denominator. It preserves an *unobserved* child comparison rather than misclassifying a stopped search as a negative result.

## Actual repeated-data ledger

The frozen TWIC 1663 sample contains **32 positions**. Selection admitted **22 positions** and **25 event interventions** (22 TT move hints, three TT value reads). Ten positions had no selected event under the original rule, including **both** depth-reversal positions. These are positions and interventions, **not 25 independent games**.

| Native endpoint from 25 matched interventions | Count | What this measures |
| --- | ---: | --- |
| Different first reply searched | 8 | Search-order/continuation difference |
| Different direct-child return | 9 | Only where both direct returns completed; **two further comparisons unobservable** |
| Different target-candidate `update` flag in that attempt | 1 | Local active-leader update; **not an exact root rank or final recommendation**; two further comparisons unobservable |
| Different final UCI recommendation | **2** | Total effect of the local intervention in a deterministic full run; not a proven chain through named intervening nodes |
| Different final public score **or bound label** | 7 | Do not subtract score values when one is an alpha-beta bound |
| Different *producer attempt identifier* | **6** | Treatment can change which depth/attempt produces the surviving public output |
| Original TT value cutoff removed | 3/3 | All three searched the position; none changed final choice or direct-child return |

The original R29 summary reported changes to the *full public UCI stream*. That metric is distinct from the seven changes to the final `score, bound, kind` triple and from the **two** changes to the final recommendation. A public-stream difference alone is not an explanation of the recommendation.

| Treatment location | Interventions | Direct-child return changed | Target-candidate update changed | Final move changed |
| --- | ---: | ---: | ---: | ---: |
| The original final-move producing attempt | 17 (14 move, 3 value) | 5 completed; 2 unobservable | 1 completed; 2 unobservable | **0** |
| An earlier attempt | 8 (all move) | 4 completed | 0 | **2** |

The table is descriptive and selected by the R29 nomination protocol; it does **not** estimate a general causal probability or show that earlier events are more influential than later events.

### Three discriminating witnesses

- **R29-018**: in original producer attempt 32, masking one move hint changed the direct-child return **224 → 223**, and the alternative Qd6's local candidate update flag **0 → 1**. Nevertheless final Qe7 and final `−68cp` survived. This proves that a local active-leader update is **not sufficient** for final output replacement. Its `−225 → −212` candidate values arose inside a search window; they cannot be treated as independently verified, exact candidate strengths.
- **R29-029**: mask in **attempt 8**, long before baseline producer **attempt 32**, changed a direct child **813 → 762**; recommendation changed **…axb4 → …Ne6**. The producer identifier changed **32 → 19**, with final public point `−252 → −255cp`. Therefore the restored versus masked run has a deterministic **total effect** on the eventual final recommendation, while the exact event-to-later-producer mediation chain remains open.
- **R29-030**: mask in **attempt 17**, before producer **attempt 28**, changed direct child **160 → 165**; final **Be2 → a3**, with producer attempt 28 retained but producer event ID changed. The final `−43cp` point became a `−46cp upper bound`. This is a final-choice effect, **not** a three-centipawn point-estimate change in objective value.

For comparison, six events changed producer attempt without necessarily changing the chosen move: R29-002, 004, 005, 019, 023 and 029. This establishes a distinct source of non-invariance even when `bestmove` is constant. Detailed per-arm return values are reproducible from the archived ZIP.

## Coverage and explanation constraints

| Reference stratum | Positions | Selected interventions | Unselected positions |
| --- | ---: | ---: | ---: |
| Close | 13 | 11 | 2 |
| Stable large gap | 7 | 5 | 4 |
| Depth reversal | 2 | **0** | **2** |
| Intermediate | 9 | 8 | 2 |
| Point unavailable | 1 | 1 | 0 |

The selection rule currently asks for a TT hint corresponding to the independent Berserk reply or a genuine producing-attempt value cutoff. The inability to select the two depth-reversal cases is an **event-coverage failure**, not evidence that no internal TT reads occurred. A source-observed-reply selector can be introduced, but its retrospective discovery must not count as prospective validation.

The original …Nd7/…a4 case is still a separate negative mediation witness: masking the named b4 hint changed a prior search order and final score, but not bestmove; masking the producer's stored lower bound induced fresh search returning the same bound and final move. The **board-legal b4 protection of the c5 bishop** comes from independent reply inspection. The engine event and board fact have not been shown to form one causal mechanism.

## Decision and next gate

1. Use the R29 panel as **development data**. Do not refit a heuristic and evaluate it again on the same 32 positions. Publish a deterministic new-cohort selector with original versus broader event-selection arms before seeing new outcomes.
2. At any true candidate/rank change, record the **baseline producer, intervention attempt, new producer, returned bound types, and causal ancestry**; no inference of an exact rank from a fail-high/fail-low result. Keep a 2×2 local value-hint factorial as a separate *proposal* until executable engine tests exist.
3. In the learner study retain A/PV, B/board counterfactual, C/B plus actual native evidence, but add a **length-matched B control**. Otherwise C−B mixes the information effect with extra reading. Measure first-choice and post-explanation judgments on new games, and track rejection of independently weak advice; no participant data exist.

This R30 record is a reproducible **evidence-quality repair** and does not advance 0.30 to a new version, replace the previously sealed 0.29 HOLD, or claim higher accuracy than Cui/Ling/Ng or Press/Golubev.

## Archived derived receipt

[Independent R30 retrospective audit package (JSON, analysis scripts, ten unit-test cases)](https://drive.google.com/file/d/1kgBthD6dNpsdLsEaP3LlZUNkEG1b5DUu/view), stored alongside the original R29 raw evidence. ZIP SHA-256 `3be613be88dcc5cdafa3e11e2b3916c8058d489475bdb259e2b7b6fe8fe4a8df`. Source inputs and their SHA seals remain recorded above; the package is a **derived retrospective audit**, not another engine test.
