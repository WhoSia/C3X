# C3X 0.31/P1 — Source-State Forecast Baselines: First Event-Family-Heldout Development Result

**Status:** original R33 archive rehashed locally; the 128-event derivative and fixed model rerun **PASS in read-only GitHub CI**. **Scientific gate: `HOLD_NO_PRETREATMENT_SOURCE_STATE_GAIN`.** No newly executed Stockfish searches, prospective game families, causal mediator identification or learner outcomes were created in this P1.

**Code:** [original source ZIP extractor](../harness/c3x_031_p1_extract.py), [fixed family-heldout predictor](../harness/c3x_031_p1_forecast.py), [11 real-input/tamper tests](../tests/test_c3x_031_p1_forecast.py). [Actual successful CI #44868739681](https://github.com/WhoSia/C3X/actions/runs/44868739681) · [original family-heldout result ZIP in Drive](https://drive.google.com/file/d/1K8ITS3QswfaCypY1ZPcPTDao4TLdOLMx/view).

## Source identity and custody

- Historical 0.30 R33 TWIC 1671 original [native ZIP in Drive](https://drive.google.com/file/d/1C3RZRyibwCthOaoWOLYu4IZNzdGlPJg8/view), exact ZIP SHA256 `e72ba91c0ffdbbb075642f044706d356fca84b4fa257a3ebcb7755db5837d8bd`; source ZIP CRC good and **all 1,414 SHA256SUMS entries** independently recomputed this turn.
- Original source cohort SHA256 `51bf007c7941afe29007ee295378a3ff701d014d649bc40682ba65db6be765a4`, discovery SHA `a65f4aea903d4fed86cba4cddb480acbd4f93241ace849784342332ce46cbdeb`, replay SHA `367f7bf4e3993312f41bdccaeb59caf77f97f28c0609d18144513d55e55cad9b`.
- Exactly **64 distinct original complete-game histories**, with **two signed physically reached pre-intervention events per game**, across **16 actual tournament event families**, yielding **128** contrast rows: futility+null early-return suppression vs normal source search for each signed target. Of 128, **11** changed the final `bestmove`, partitioned **4** null-ineligible, **7** null-eligible.
- [Frozen human-inspectable 128-row pre-treatment TSV](../frozen/C3X_031_P1_R33_128_PRETREATMENT_ROWS_20261121.tsv), SHA256 `6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba`. Derived larger JSON SHA `e96aff554f6cc90c4e7426df2ad8c2237737c2016115ea8608485ba9a1449e95`. Only aggregate/numerical information is committed, not source PGNs.
- CI reran the predictor on frozen TSV and verified its SHA; source ZIP was **not** downloaded and rehashed within GitHub CI. Local extractor audited the original bytes and all selected physically matched source events before creating TSV.
- Original P1 archive's last public score types: 34 exact/unbounded, **23 upper bounds** and **7 lower bounds** among games. This forced prefit *P1-A1* input schema amendment to include bound flags; we did not treat upper/lower scores as exact chess values or silently drop 60 target rows.

## Prediction estimand and models

For an event chosen from untouched physical reads, `y=1` iff masking **both** early-return paths changes the eventual finite-budget source engine recommended first move. This is a *source-sensitivity effect label*, not a chess-strength label.

| Model | Allowed predictors |
| --- | --- |
| M0 | Training-family-only smoothed overall event flip frequency |
| M1 | Original untreated public completed depth, bound-labeled published cp threshold, PV length |
| M2 | M1 + untouched physical target depth, ply, futility slack, search progress in nodes, attempt ordinal, null eligibility and whether the event's root branch equals original final recommendation |

16 fully separated tournament-family folds, 64 games each present in one fold, with no case/game/family identifiers allowed as model predictors. Identical regularized logistic learner for M1/M2, train-fold-only normalization, fixed `ridge=0.02`, `iterations=900`, `step=0.10`, family-cluster bootstrap `N=2000`, seed `310121`. See [locked protocol and explicit bound amendment](C3X_031_P1_PREOUTCOME_STATE_FORECAST_PROTOCOL_20261121.md). M2 does **not** include treatment child return or end-of-search results.

## Actual out-of-family results

| Metric | M0 prior | M1 public baseline | M2 native pre-event |
| --- | ---: | ---: | ---: |
| Brier ↓ | **0.0798229** | 0.0808690 | **0.0775887** |
| Log loss ↓ | 0.3010110 | 0.3096985 | **0.2696384** |
| Average precision ↑ | 0.0687281 | 0.1443075 | **0.2125826** |
| Events predicted positive at 0.5 | 0 | 0 | 1 |
| True flip recall at 0.5 | 0/11 | 0/11 | **0/11** |

**M2 minus alternatives is not a validated improvement:** difference `Brier(M1)-Brier(M2) = +0.0032803`, family cluster bootstrap 95% interval **[-0.0067906,+0.0108735]**; `Brier(M0)-Brier(M2)=+0.0022342`, interval **[-0.0094194,+0.0138883]**. Both violate the predeclared improvement threshold **≥0.01** and both confidence intervals cross 0. AP and log loss improving on already exposed developer data does not override the gate.

The single >0.5 M2 prediction was **R33-061, null-eligible event** (`p≈0.5983`), which actually **did not** change the final move. Two of the eleven true flips had very low predicted probability: **R33-036 null-ineligible `p≈0.0107`** (rank 110/128) and **R33-002 null-eligible `p≈0.0238`** (rank 84/128). These are **explicit falsifying diagnostic cases for an overstrong pre-treatment state sufficiency claim**. They were identified after the model result and must not be used to reselect or refit this P1 cohort.

## Interpretation and architectural decision

The physical source fields may contain **ranking information** missing from public output on these historical 128 rows, but the improvement is not sufficiently robust, and a strict 0.5 classifier misses every true flip. The counterexamples prohibit interpreting `phi = (public, event depth, ply, slack, nodes, attempt, eligibility, branch link)` as an intervention-stable *sufficient* state.

A stronger reduced representation may need the actual **TT write/read payload**, move-order/history snapshot and exact search-budget transition *before* a specified downstream source decision, and the quantity of information needed may depend on root menu and search window. This is a mechanistic hypothesis, **not** a result established by the predictor.

**Next separate causal gate:** P2 must fix unseen game families and feature schema before observing any new native intervention results, compare M0/M1/M2 without refitting to test outcomes, retain all no-contact events and normal shams, and only afterward consider state transplant. P1 is closed as a reproducible **retrospective negative threshold test**, not a win for minimal causal compression.

## Exact reproduction and provenance limits

```bash
python harness/c3x_031_p1_extract.py R33-original.zip p1-full-feature.json
PYTHONPATH=harness python -m unittest -v tests.test_c3x_031_p1_forecast
python harness/c3x_031_p1_forecast.py \
  frozen/C3X_031_P1_R33_128_PRETREATMENT_ROWS_20261121.tsv \
  p1-out-of-family-results.json
```

The original full-data extractor produces the full machine-readable records from original ZIP; TSV is a compact, numeric-only projection with exact row SHA for CI. The compact-table transformer is deterministic: assign each original `family` its rank (1..16) in lexicographically sorted distinct family names; keep all other numeric columns and the physical `R33-nnn-0/1` row ID in the stated header order.

**Byte seals:** GitHub original P1 result JSON SHA256 `42496c17e858f4b3074640b04f4d3a123631fcb9e146e25d376ef2fc2b322db7`; GitHub Actions result ZIP SHA256 `2b4c77a42d32c810118aeebd3c59e7551c47021a88bca56d93f4a74ae890c9ef`. The original ZIP uploaded to C3X Drive results folder and re-downloaded with the same SHA and intact CRC.
