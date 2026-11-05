# C3X 0.29-P36 — Historical March Cohort Overlap and MultiPV Budget-Stability Adjudication

Date 2026-11-05 KST. **Posthoc evidence re-audit of actual archived native outputs; NO explanatory superiority claim.** Full reproducible JSON audit is provided as an external conversation artifact `C3X_P36_HISTORICAL_OVERLAP_AND_BUDGET_AUDIT_20261105.json`, not yet byte-archived to Drive.

## Source authority and historical contamination

P36-R2 original 2026-03 PGN SHA256 `1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc`, exact original source manifest from [native read-only run 41957706609](https://github.com/WhoSia/C3X/actions/runs/41957706609). The same source was held in C3X Drive as of 2026-10-17, and, **more critically**, C3X-0.20-C2 had already engine-blind-selected 16 full March games in [source run 38038059013](https://github.com/WhoSia/C3X/actions/runs/38038059013), repository [historical receipt](../c3x/receipts/c3x-020-C2-march2026-enginefree-16-source-freeze-20261010.json). New P36-R2 freeze eight source games were selected differently, under new SHA-ranked selector. Exact original full-game UCI histories were compared by independent SHA256 calculation. **One exact full-game duplicate** occurs: new case `00f04cd20636fdc2`, game SHA `6eed60605065179e845cc00c29e3fbf378d9befbfff9b5ff3c1b891eb139606b`. Thus **P36 eight-game dataset is NOT eight source-novel games**. The original 0.28 64 and other historical family exclusion remains incomplete. Do not retrospectively delete the duplicate to improve results. Source-month disjointness and event independence are NOT established.

## Actual P36-R3 24k source-native screening: full denominator retained

Eight untouched Stockfish16 MultiPV=2 source games (the P36-R3 successful native rerun produced `P36_R3_MARCH8_NATIVE_MULTIPV2_SCORE_SCREEN.json`), all selected at original ply30 BEFORE engine screening:

| Case | 24k PV1 / PV2 | PV score gap | Classification |
|---|---|---:|---|
| `00090c4e53df5b2d` | e1c1/f1g2 | 83cp | intermediate |
| `00470a57672750d1` | f2f4/d2c4 | 9cp | nominal near |
| `00846ac66ee43492` | e2d2/e2e3 | 63cp | intermediate |
| `00f04cd20636fdc2` | c3b2/h2h4 | **-16cp signed** | **reported PV order discordant; also historically repeated full game** |
| `01662a4d51803d33` | d4d5/e2f1 | 76cp | intermediate |
| `01af9df4f5e8e39f` | f3f4/e2c1 | 10cp | nominal near |
| `01f4ddb70d4011c6` | c3b5/b1c1 | 22cp | intermediate |
| `02154be9fa2cf21d` | d2d3/d4c5 | 576cp | wide |

Rank-score discordance must remain recorded, not silently sorted or grouped as an ordinary stable 16cp near pair.

## Repeated native budget test 24k/48k/96k — crucial negative

New archived `P36_R4_MARCH8_48K_96K_NATIVE_STABILITY.json` (16 additional native SF16 processes) shows BOTH predeclared 24k nominal near cases **FAIL** the stronger condition `same two candidates / consistent winner / <20cp across all budgets`:
- `00470a57672750d1`: f2f4 vs d2c4 remain the same two candidates; gap **9→28→42cp** at 24k,48k,96k. Fails the near margin condition in both additional budgets.
- `01af9df4f5e8e39f`: gap **10→15→27cp**, but second candidate **e2c1→e2g3** by 48k and remains e2g3 at 96k. Fails candidate-identity stability; near condition also fails at 96k.

**Critical nuance:** this disproves only that these two *particular* 24k near pairs satisfy the prespecified cross-budget near-stability criterion. It does **not** disprove near-equal chess reasoning as an important scientific research target. Other cases can enter or leave the near stratum at different nodes (e.g. `01662a4d51803d33` 76→99→9cp). Multiple trials are finite-node observations, not oracle objective chess value.

## PI decision: retain true scientific question, reject promotion of these two cases

- **FAIL**: P36's two nominal 24k near pairs as *budget-stable near pairs*. Zero certified stable near cases under this gate, not a measure of prevalence.
- **HOLD**: game-disjoint independent confirmation (one game overlaps C3X 0.20-C2), event-family independence, historical 0.28 registry exclusion, and model-vs-strong-PV explanatory advantage.
- **NEXT**: use this source as a method-development negative-control receipt (explicitly labeled). A truly fresh **event/game-disjoint** source and a source-only frozen selector must precede any new engine-score screening. Do not filter these eight posthoc to claim success. Predeclare the minimum near-margin stability requirement and include a strong no-explanation/abstain model as a viable competitor.
- **No more NNUE instrumentation proliferation** until the chess-facing forecast court has admissible targets.

Research OS: Notion semantic authority, Drive bytes, GitHub executable/research record. Human `WhoSia` commits; GitHub Actions only read/compute/artifact, no `github-actions[bot]` commits/pushes/ref changes.
