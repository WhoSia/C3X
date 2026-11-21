# C3X 0.31/P2 — First Genuine New-Game Native Transport: Negative State-Probability Transfer with Real Source Causality

**Date:** 2026-11-21. **C3X 0.31 scientific verdict:** `NEGATIVE_PROSPECTIVE_TRANSPORT` for the **P1-frozen M2 pre-intervention source-state predictor**. **Positive but separate:** physical Stockfish16 early-return interventions changed final `bestmove` in seven selected new issue cases. **Crucial limitation:** six of those seven changed the completed search depth under the same 32,000-node budget. `P2_NATIVE_SOURCE_TOTAL_EFFECT_IN_FINITE_BUDGET` does not imply strategic value, intermediate TT/history mediation, or a minimally sufficient state.

## 1. Original-world identity and outcome-blind freeze

- New publisher original: **Mark Crowther, The Week in Chess, issue 1670 (2026-11-09)**; original ZIP SHA256 `6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf`, [stored original Drive ZIP](https://drive.google.com/file/d/1aYTJF5WYCP-GkWndWrdot20xeA5eVf3H/view). 8,391 publisher game headers; 8,328 legal standard nonempty; 45 duplicate full history hashes, 63 empty.
- Existing exposed R33 TWIC1671 training: 64 games from 16 event families and earlier 78 family exclusions. P2 rejected 30 of 47 TWIC1670 event headers as historically used/excluded families. 17 candidate family names had 2,326 raw records. Selected 64 legal nonterminal game histories across those 17 under a deterministic round robin, **before new source native outcomes**. Pre-treatment full-history JSON SHA256 `2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4`, [Drive custody](https://drive.google.com/file/d/1Aj02UgRoHYw6sKqPjwOmtDETfTnESpe8/view).
- Selected sample shared **zero full-game hashes, zero four-field FEN checkpoint identities, zero original normalized event header families** with the 64 archived R33 games. **Do not promote** that claim to disjointness against *every* historical individual C3X game in archives not fully enumerated.
- Frozen unrefitted P1 training model: SHA256 `f27a89fd15efa3f35738ba8cf2a6d1243c8336268e4661c653bbd1e6c0bfee23`, source P1 TSV SHA256 `6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba`. P1 input has 11 known final flips across 128 old source events. M0 train-only prevalence `11.5/129`; M1 untouched public score **with bound flag**, depth and PV length; M2 M1 plus source OPEN event depth, ply, futility margin, nodes, attempt, null eligibility and event branch-versus-untreated final-bestmove flag. The last one is learned from the completed untreated baseline search; it is **pre-intervention**, but **not available online at the instant of the source OPEN event**. Do not market this predictor as a realtime source-event state predictor.
- P2 engine: official Stockfish16 `sf_16` commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, restored R27–R33 patches, patched binary SHA256 `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1`, pre-R33 reference SHA `78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb`, NNUE SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`. [Original source-build native CI](https://github.com/WhoSia/C3X/actions/runs/44872473600).

## 2. Prospective gate: all 128 source contacts frozen before any treatment

[Untouched physical-source observation CI #44872579316](https://github.com/WhoSia/C3X/actions/runs/44872579316) executed 64 positions × three distinct source conditions = **192 new native searches**: R31 pre-R33 baseline, R33 observer-disabled, R33 observer-only. All **64/64** original public UCI trajectories and native root-source receipts matched. Every game produced both null-ineligible and null-eligible minimum-slack physical source OPEN events under the frozen R33 selection rule: **128/128 observed physical target identities**. Predictions from frozen P1 M0/M1/M2 were serialized **before any P2 treated move or returned value**.

Exact private frozen pre-treatment source JSON SHA256 `17915c7d9ae56dd950cd026d07a4917a414213415ea3b28af256b305eb8ad146`; before-treatment events and forecast ZIP [Drive](https://drive.google.com/file/d/1xAoyKx1vqYASkf5wviz5SINWmfMylLal/view), raw source-only 384 UCI/stderr log files [Drive](https://drive.google.com/file/d/1u2LMtCmQiViGZk7wfhKd3XmHvbaADtz7/view). The immutable [SHA-bound machine-readable pre-treatment consent-free freeze](../frozen/C3X_031_P2_SOURCE_TARGETS_BEFORE_TREATMENT_20261121.json) was committed *before* executing intervention treatment, preventing postoutcome case reselection.

Before results, M2 assigned probability >=0.5 to **four** events, with predicted probabilities ranging from approx 0.0013 to 0.8291. A prior-to-outcome input-shift check showed P2 mean public CP numeric +79.86 vs P1 +3.34 (0.45 training standard deviations) and source attempt 24.91 vs 28.16 (-0.38 training SDs). The CP values can be upper/lower bounds, not calibrated point estimates, and mean shift says nothing conclusive about distribution equality.

## 3. Genuine targeted new native intervention — execution receipts

[Native treatment and sham CI #44872920835](https://github.com/WhoSia/C3X/actions/runs/44872920835) executed **576** distinct native engine searches, each fresh executable state:

- 64 game-wise irrelevant-target sham searches, with futility+null flags set but `TARGET=0`; **64/64** reproduced original complete normalized public UCI trajectory and bestmove.
- Every one of 128 pre-frozen actually contacted source events: `futility_only` and `both_off`, each twice in a cold source process = **512 treated runs**. All **256 treatment-arm paired cold replays** agreed on event, public UCI, root best producer and recorded outputs. No hidden re-selection and **0** target absence/stopped/unobserved.
- Original 512 treated-run UCI and stderr comprise **1,024 text files**, plus 128 sham stdout/stderr files = **1,152 byte-preserved original logs**. Original P2 treatment JSON SHA256 `69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f`.

[Original all-event treatment ZIP, Drive](https://drive.google.com/file/d/1G7zGJTP2PMiNqx-6cjNc3s6QBqLhV5mq/view) SHA256 `8edbe62265eed343683adf0ae6cb982a02f25d8db3e6ea7e586e4ab5e1581e5a`. [Full native logs, Drive](https://drive.google.com/file/d/18h5eLTe89lQJY7_fwePwIau9jUNiGedw/view) ZIP SHA `53343092d93be11dd0bdba6dca53d669fb202749f94a5b5073d884bf77dccaaf`. [Count-complete public original court, Drive](https://drive.google.com/file/d/1cBtHquwipy6tceYRw1rPkPp0dYiFs1rY/view).

## 4. New-game causal-source effects: different root result ≠ stable-strategy improvement

| Original source stratum / intervention | Immediate child returns changed from untouched baseline | Final `bestmove` changed |
| --- | ---: | ---: |
| Null-ineligible, futility-only | 46/64 | **3/64** |
| Null-ineligible, both-off | 46/64 | **3/64**, **exactly the same** null-ineligible arm outcome |
| Null-eligible, futility-only | 54/64 | **0/64** |
| Null-eligible, futility+null both-off | 60/64 | **4/64** |

A physical **early child return change is not a sufficient final-root-choice change**: most changed direct event returns do not flip the bestmove. On the null-eligible stratum, the additional null suppression was necessary for the *four observed final changes in this experiment*, but this is a total-effect interaction in the given search conditions, not evidence that a particular TT write or history value uniquely mediated it. In the null-ineligible stratum the extra null flag was a **64/64 valid no-op negative control**.

Exactly **seven** distinct source interventions changed a recommended move across **seven distinct games, seven original event-family labels** and **six pre-specified broader event families**. **Only one of seven retained the same originally completed depth** under the 32k-node limit; the other six changed depth completion. Hence *only one* source-experiment root flip is a same-completed-depth candidate for immediate mechanism follow-up; the remaining six require independent fixed-depth controls before within-iteration strategy or preference claims.

| New source | Gate | Untouched UCI → treated UCI | Untouched depth → treated completed depth | P1-frozen M2 flip risk |
| --- | --- | --- | --- | ---: |
| P2-008 | Null-eligible | `e2c4 → g3e4` | **13 → 13** | 0.06835 |
| P2-027 | Null-eligible | `g2g3 → f1f2` | 11 → 10 | 0.48516 |
| P2-028 | Null-ineligible | `d4e5 → f4e5` | 16 → 15 | 0.01082 |
| P2-034 | Null-eligible | `c4d3 → c4c2` | 12 → 11 | 0.07436 |
| P2-035 | Null-ineligible | `e5f3 → f2f3` | 12 → 10 | 0.27517 |
| P2-043 | Null-eligible | `f3d2 → c1b2` | 11 → 9 | 0.47577 |
| P2-055 | Null-ineligible | `d2d1 → d3b5` | 17 → 13 | 0.00832 |

This is no proof that any new treated candidate is objectively better; no independent judge or human comprehension trial was run in P2. The P2-008 source intervention is same completed depth, **not necessarily the same work/budget or root search window**.

## 5. P2 genuine unseen-game forecast test — primary negative

The P1-trained and **never P2-refitted** model predictions were checked against all 128 actual P2 new-game source effects.

| Metric (128 source events, 7 flips) | M0 P1 smoothed prevalence | M1 published depth/score-bound/PV | M2 M1 + untouched physically observed source fields |
| --- | ---: | ---: | ---: |
| Brier score ↓ | **0.0528843** | 0.0549392 | **0.0621650 (worse)** |
| Log loss ↓ | **0.2204728** | 0.2384984 | 0.2438026 |
| Tie-aware average precision ↑ | 0.0546875 | 0.1336846 | **0.1511781** |
| p >=0.5 reported positive | 0 | 0 | 4 |
| True positive detected at p >=0.5 | 0/7 | 0/7 | **0/7** |

Model M2's Brier **gain** over M1 is `-0.00722587` (negative means worsened); over M0 `-0.00928077`. The original **17-event-family** clustered 2,000-replicate 95% intervals are:

- `Brier(M1)-Brier(M2)`: **[-0.0230442, +0.0053356]**.
- `Brier(M0)-Brier(M2)`: **[-0.0309083, +0.0088065]**.

Both fail the predeclared minimum improvement **+0.01** and lower interval >0 requirement. An AP improvement does not rescue a Brier negative when the decision criterion was prospectively frozen. The only four M2 predictions >=0.5 were **P2-012-1, P2-019-1, P2-020-0 and P2-020-1; all four were real nonflips**. Model M2 missed all seven actual flips at its fixed binary threshold, including P2-028-0 `p≈0.01082` and P2-055-0 `p≈0.00832`.

**Formal scientific verdict: `NEGATIVE_PROSPECTIVE_TRANSPORT`.** This falsifies the claim that **this particular simple state feature set** is an adequate intervention-stable prediction abstraction under the registered P2 metric; it does not prove no compressed source-state abstraction exists.

## 6. Independently reproduced from 1,152 original native logs

Separate source implementation [P2 independent court](../harness/c3x_031_p2_independent_court.py) re-read all 1,152 original UCI and stderr files, checked the 512 treatment stderr SHA hashes and matching UCI, exact original target OPEN signatures, 64 sham full-UCI identities, all seven root-choice changes, depth completion, source-reply counts, null-ineligible sham property and frozen before-treatment probabilities. It recomputed Brier/log loss and **tie-grouped** AP independently, plus the primary original 17-family cluster CI.

[Independent actual CI #44873709342](https://github.com/WhoSia/C3X/actions/runs/44873709342): **8 tests PASS** including deliberate corrupted forecast, sham, source target and model SHA negatives. Original independent derived JSON SHA `cb1292fefd4b1b7df88a859ed784704395392de9f7dc2a36f5bebec5608ed7e7`; source GHA artifact ZIP `12f05f1d79527c09896ae363665ccce1df5789ee885bbaa2ba5444509c5fd02e`; [Drive derived court](https://drive.google.com/file/d/15XpAxFydkOdjunnVjiSoU_LFf114D4jt/view). **This court ran zero additional native searches; it is a true independent derived analysis of the original 576.**

Before seeing P2 treated outcomes, we separately registered in [C3X 0.31 Notion](https://app.notion.com/p/41fef561cf9281ae8a62d4c153f11c01) a secondary grouping that merges obvious same-tournament rapid/blitz/women pairs. The **12-macrofamily** sensitivity gives broader 95% intervals:

- M1−M2: **[-0.0260282, +0.0046627]**.
- M0−M2: **[-0.0351478, +0.0106507]**.

The negative central estimates persist; neither secondary interval excludes zero. This is a *sensitivity analysis*, not a posthoc replacement for the primary registered 17-family court. Those 17 exact family names are not necessarily 17 statistically independent tournaments because some rapid/blitz arms share participant pools.

## 7. Decision: revise the research object, not the score threshold

The completed first true new-game transport test shows that *source event contact* and *forecast sufficiency* must be kept apart. The R33-style physical gate can reproducibly change Stockfish choices on truly new local game contexts; however, the P1-fitted limited feature vector is not even robustly calibrated enough to detect those flips. It does not identify TT/value/depth/bound writes or restored ancestor state. Source root choice still does not establish chess move merit.

**Next mechanistic stages**:

1. **P2-D1 equal-depth controls** on all seven post-outcome source-changed events, declared as *exploratory conditional diagnosis* (not a fresh primary cohort). At least a control and identical intervened gate at each **original completed depth** and optionally at treatment-completed depth; compare original exact pre-treatment source signatures, completed depth, bestmove and node counts. If target disappears under fixed depth or source controls diverge, report HOLD.
2. **P3 causal state intervention** prioritize the only same-depth naturally observed flip **P2-008-1** and predeclared high/low risk cases separately (P2-020-1, P2-019-1, P2-012-1, P2-027-1 vs P2-055-1, P2-021-0, P2-063-0, P2-047-0). These P3 risk-based diagnostic cases were selected *before* observing P2 treatment outcomes in Notion. Do not count multiple site strata from one game as independent games. Capture exact TT store/read chains, main history, branch ordering and remaining budget; test same-prefix necessary/sufficient restoration under sham.
3. **P4 chess reply and human** only after real independent legal-reply and learner observations. Earlier R37 one FEN-only judge did not identify source mediator or teaching benefit.

**Status:** P2 **completed native prospective source experiment**, primary predictive transport **NEGATIVE**, checkpoint mediator **HOLD**, game-disjoint generalization bounded to frozen P2 selection, **chess strategy/HUMAN transfer HOLD**. Preserve original nulls and do not optimize M2 post-outcome then claim the same sample was held out.

## Historical-source ancestry correction — P2-L1 (2026-11-21)

**Post-outcome historical exposure audit; does not alter the frozen P2 primary 128-event sample or its negative prospective transport verdict.** The original R26 C3X research also used publisher **TWIC1670**, with the exact same publisher ZIP and PGN hashes. [R26 original historical source receipt](../receipts/C3X_030_R26_TT_PREOUTCOME_20261117.json) lists 16 previously selected game histories and their original source game ordinals. The [P2-L1 original-source reanalysis](C3X_031_P2_L1_R26_SOURCE_FAMILY_EXPOSURE_RESULTS_20261121.md) checked all 8,391 original PGN event headers against the P2 source histories and all 128 physically treated P2 cases.

Two P2 normalized exact tournament event families had also been used by R26: `fide world open u20 rapid` and `world girls u20 blitz`. They account for **eight** P2 selected games / **16** treated events / **zero** final bestmove flips. None of the 64 P2 selected **whole game-history hashes** was identical to the R26 16 selected histories. Thus P2 remains a *new-game* intervention dataset but is **not disjoint from every earlier C3X event-header family or from every earlier publisher source**. The earlier R33-only family disjointness claim remains valid with its specifically stated R33 denominator.

On the **post-hoc** remaining 56 P2 games / 112 events, all original **seven** flips persist; frozen M2 Brier `0.0601507` still exceeds M1 `0.0589193` and M0 `0.0593038`. The M1−M2 gain is `−0.0012314` with 95% family-resampled interval `[−0.0120617,+0.0087283]`. A 0.01-gain confirmatory gate remains unmet, while this interval does **not** establish statistically significant model harm. The 16-event removal is a secondary exposure sensitivity, not a replacement prospective trial. [Original 11-test read-only CI #44878967544](https://github.com/WhoSia/C3X/actions/runs/44878967544) · [Drive L1 results](https://drive.google.com/file/d/1Iz_ZKRDFn3p-oF9PPE29JHvTf_AJvT_2/view).

**Additional limitation:** These two are *exact event-header* overlaps; rapid/blitz or women/open subevent names may belong to broader event families. Historical macro-event exposure requires a separate, appropriately labeled analysis before claiming an all-prior-family-blind cohort. No 0.30/0.31 source experiment, game selection, model coefficient or raw result was changed by this correction.

## Later macrofamily source-history qualification — P2-L2

Original [P2-L1 exact header overlap](C3X_031_P2_L1_R26_SOURCE_FAMILY_EXPOSURE_RESULTS_20261121.md) was extended by [P2-L2](C3X_031_P2_L2_MACRO_EVENT_EXPOSURE_SENSITIVITY_20261121.md) using the **already registered** secondary `PREDECLARED_MACRO` mapping from the original P2 independent court. With R26-exposed macro-family rapid/blitz variants removed **after observing** P2 outcomes, **48 games / 96 events / 6 root flips** remain. The frozen M2 model's Brier score is `0.0550385` versus M1 `0.0564605` (gain **+0.0014220**, 95% macrofamily-bootstrap interval **[-0.0047731,+0.0064239]**). This is a point-estimate sign reversal compared with the exact-header L1 sensitivity, **not** positive confirmation: the predeclared +0.01 and nonzero lower confidence-limit gate still fails.

The P2-028 source event is within an R26-exposed **FIDE World Open U20 rapid/blitz macrofamily** despite its full-game and literal Event-header uniqueness; it may support within-search mechanism diagnosis but not independent macrofamily transport. Further broader name alias exclusion is a clearly hypothetical postoutcome scenario and does not certify tournament identity. **All P2 original 64 histories/128 native targets and the negative primary verdict remain unchanged**; L1/L2 are additional scientific claim-scope corrections rather than replacement analyses. [Actual read-only CI #44879488680](https://github.com/WhoSia/C3X/actions/runs/44879488680) · [Drive result ZIP](https://drive.google.com/file/d/1TYzgiI4s1_c8Vfz7ZKtxM1BBApaIn9bJ/view).
