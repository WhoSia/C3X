# C3X 0.31/P2-L1 — R26 Historical Source-Family Collision and Post-Hoc 112-Event Sensitivity

**2026-11-21. Evidence:** original publisher-source/R26/P2 byte-identical reinspection and actual derived data recomputation. **Scientific classification:** `POSTOUTCOME_HISTORICAL_EXPOSURE_SENSITIVITY`, **no new native engine searches**. **Decision:** original prospective P2 primary analysis must remain unchanged and **negative**, but the previous wording implying full separation from *every* C3X historical event family was too strong.

## Previously missing ancestry: R26 already used TWIC1670

The [original R26 first-stage receipt](../receipts/C3X_030_R26_TT_PREOUTCOME_20261117.json) identifies **the exact same** original publisher ZIP `twic1670g.zip`, SHA256 `6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf` and PGN member `bb166b4813aca824d4455ee51d0bbe3be75405586b310639c3eedfe02a32b77d`, and holds **16 prior TWIC1670 game ordinals + complete-game history hashes**.

The P2 sample freeze checked overlap against R33/P1 and 78 historically excluded event families. It selected 64 *distinct* legal source games under an outcome-blind rule. But R26's precise selected TWIC1670 **event-family names** were not individually included in the published P2 family exclusion comparison. Hence `new TWIC1670 issue relative to P1` did not imply `new publisher source compared with all C3X work`.

This independent L1 audit retrieved the **original actual** TWIC1670 PGN, reconstructed all **8,391 original Event headers in publisher game order**, re-read the R26 selected ordinals and full hashes, and cross-compared the unchanged private P2 64-game sample and the actual P2 **128 physically treated** cases. Normalization used the same NFC/trim/casefold rule as P2's original freeze, not a new outcome-dependent alias map.

**Exactly two source tournament families previously represented in R26 were selected in P2**:

| Previous R26 family | P2 selected original game IDs | Games | Physical source events | Final bestmove flips |
| --- | --- | ---: | ---: | ---: |
| FIDE World Open U20 Rapid | P2-013, -030, -047, -064 | 4 | 8 | 0 |
| World Girls U20 Blitz | P2-003, -020, -037, -054 | 4 | 8 | 0 |
| **Total source-family overlap** | **8 previously unexcluded game slots** | **8** | **16** | **0** |

**Crucial distinction:** P2's 64 selected complete-game histories have **zero identical SHA256 history hashes** to R26's 16 sampled TWIC1670 games. P2 thereby still contains different **games**, but it is not **fully previous-event-family-independent**.

## Actual primary P2 vs post hoc exact-family exclusion

No source-game or event was removed from the immutable original primary P2 receipt, and nothing was refitted. The exclusion is a **secondary post-outcome sensitivity** defined from historical provenance. Same frozen P1 M0/M1/M2 probabilities, source-selected targets, shams and original experimental results.

| Scope | Original primary P2 | Excluding 2 exact previously seen R26 event families |
| --- | ---: | ---: |
| Games | 64 | 56 |
| Physical source-target events | 128 | 112 |
| Original normalized tournament families | 17 | 15 |
| True final bestmove flips | **7** | **7** |
| M0 Brier ↓ | 0.05288425 | 0.05930383 |
| M1 public Brier ↓ | 0.05493915 | 0.05891932 |
| M2 source pre-open Brier ↓ | **0.06216502** | **0.06015073** |
| M0 average precision ↑ | 0.0546875 | 0.0625000 |
| M1 average precision ↑ | 0.1336846 | 0.1708333 |
| M2 average precision ↑ | 0.1511781 | 0.2125218 |
| M2 binary threshold 0.5 actual flip hits | 0/7 | **0/7** |

Model gain is defined as **Brier(baseline) − Brier(M2)**. Positive favors M2. At the original P2 primary denominator, `M1−M2 = −0.00722587`, `M0−M2 = −0.00928077`. After removing the 16 exact R26-family-overlapping events:

- `Brier(M1)−Brier(M2) = −0.00123141`; family-resampled 2,000-draw 95% interval **[−0.01206165,+0.00872826]**.
- `Brier(M0)−Brier(M2) = −0.00084691`; family-resampled 2,000-draw 95% interval **[−0.01536298,+0.01386837]**.

The R26-exposed families contained **two of P2's four M2 false-positive high-risk predictions** (both in P2-020), so the negative Brier point disadvantage was attenuated under exclusion. The remaining two false positives and all seven true flips persist. Confidence intervals cross zero in both comparisons; **it is not justified to claim statistically established model harm**. However, the P1/P2 fixed scientific gate requiring improvement ≥+0.01 and positive lower uncertainty bounds is still clearly unmet. **`NEGATIVE_PROSPECTIVE_TRANSPORT` remains the primary verdict** and the secondary sensitivity shows no evidence that hidden prior exact-family collisions alone caused that failure.

## What is *not* proved by this audit

1. This compares **exact normalized event header families**, not the identity of a broader umbrella tournament across rapid/blitz/women sub-events. Those can share people/venue/information but have distinct original Event headers. A separate, explicitly labeled **conservative umbrella-family sensitivity** is justified and must not be conflated with this literal-header test.
2. R26's 16 TWIC1670 sampled games were audited, **not the entirety of all past C3X game-by-game source histories**. Thus a universal disjointness claim remains HOLD.
3. All seven P2 root flips remain genuine physical source interventions in distinct later game histories; none becomes a claim of strategic chess improvement, exact TT/history mediation or human explanation benefit.
4. This audit did **not** run native Stockfish again, did **not** modify previously frozen M2 model predictions, and did **not** re-designate an exposed data subset as a blind replication.

## Code and material custody

- [Source-auditing executable](../harness/c3x_031_p2_l1_historical_family_audit.py) rehashes all three original binary/JSON sources and verifies actual R26 ordinals, full game hashes, actual P2 treated source IDs, probabilities, and original P2 Brier labels.
- [Eleven real-input integrity and deliberately corrupted negative tests](../tests/test_c3x_031_p2_l1_historical_family_audit.py); [read-only workflow](../.github/workflows/c3x-031-p2-l1-r26-lineage.yml).
- [Actual GitHub Actions PASS #44878967544](https://github.com/WhoSia/C3X/actions/runs/44878967544), 11 tests. Derived original JSON SHA256 `174adfe4963c27f6c55ad35f403a59249cb3356eb21dbfea41b4372b7a8d7e7e`; ZIP SHA256 `2c05b36d6ee1e4c716c6f4390d971cd2866f82235eca624f1af0a723ba38244a`.
- [Drive original L1 derived evidence ZIP](https://drive.google.com/file/d/1Iz_ZKRDFn3p-oF9PPE29JHvTf_AJvT_2/view), uploaded and subsequently re-fetched with identical SHA and intact CRC.
- Publisher original PGN source is protected in [C3X Drive custody](https://drive.google.com/file/d/1aYTJF5WYCP-GkWndWrdot20xeA5eVf3H/view), not exposed as a GitHub source-data file.

**Higher-level finding:** The same **raw source archive** can supply genuinely different games without supplying fully new **experiment families**. A future C3X scientific denominator should seal the three independent identity axes — publisher bytes, full legal game hash, and independently normalized event-family/umbrella taxonomy — and explicitly abstain wherever historical overlap cannot be audited.
