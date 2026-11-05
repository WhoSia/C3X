# C3X 0.29-P37/R4 — Eight October Event-Family Source Freeze, Actual Native Rival Forecast, Unfavorable Result and Root-Cause Audit

**2026-11-05 KST · Scientific verdict: SOURCE PRESEAL PASS / NATIVE THREE-RIVAL PILOT PASS / C3X-FINITE-PLAN VS PV FORECAST ADVANTAGE FAIL / COMPLETE HISTORICAL HELDOUT HOLD.** This is the first P37 eight-event forecast result, not a scientific claim that full C3X or Stockfish NNUE causal interpretability has failed.

## A. Original source custody BEFORE scoring

Eight separate event families from late October 2026 were precommitted in [P37/R1 design](C3X_029_P37_R1_EIGHT_LATE_OCT_EVENT_SOURCE_PRECOMMIT_20261105.md), commit `d8d84071c3dfe290e04dcbf064ca6b8dc733ba07`, **before PGN body/game selection or any engine outputs**. Eight Lichess official round PGN endpoints (Sahel, KazChess, Chinese League, Clutch Chess, Freiburger, Magdeburg, Garcia-Palacios, Greg Hjorth) were each downloaded twice; first/second raw bytes match; strict complete legality and >=60 halfmoves; deterministic lowest SHA256 full original mainline + metadata case rank, one case per event, fixed ply30. [Read-only source CI 41968008046](https://github.com/WhoSia/C3X/actions/runs/41968008046) **SUCCESS**, six source-only tests **PASS**. No source selected using engine value or human inspection of game outcomes; caveat that the original PGN itself contains finished game results in the ranking tags, so **engine-blind is NOT strictly independent of recorded game-result metadata**.

[Drive original ZIP](https://drive.google.com/file/d/1BuyLRFW8cXILGeePyPQnrkAVX-yoSjdS/view) SHA256 `3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191`, separately re-downloaded and byte checked. Frozen manifest member SHA256 `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`. All eight source PGNs are distinct; manually recalculated full-game UCI SHA against **40 earlier recorded games** (C3X 0.18 Oct16; C3X 0.20-C2 March16; P36 March8): zero collisions. Some historical C3X source-game/event registries remain unavailable or unaudited. **Never claim full historical decontamination or a certified confirmatory heldout yet.** The 2026-10 month-aggregate Lichess broadcast file was a 25-byte placeholder at source date, hence event round APIs, not another month recycling. No official upstream per-round checksum published; 2x fetch agreement is transport stability only and cannot substitute official independent source digest. **Source-date anomaly:** Clutch round metadata indicates 2026.10.25 but independent tournament reports place games 2026.10.27-29. Preserve this difference; date metadata accuracy HOLD.

## B. Two-job sealed predictor vs late reference

[Precommitted R2 prediction contract](C3X_029_P37_R2_PREOUTCOME_THREE_RIVAL_REPLY_FORECAST_AND_96K_COURT_20261105.md), commit `55ea37593d68411f2e30dbf4cf5e354d4f58b7db`, declared before any 24k scores. [Actual complete CI 41969173637](https://github.com/WhoSia/C3X/actions/runs/41969173637) has **both jobs SUCCESS**. In the first job, source manifest transformed to **prefix-only (30 historical plies) with actual future continuations removed before the first prediction**. Pristine Stockfish16 (git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, net SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`) ran one joint MultiPV2 24,000-node analysis per case. Three approaches each forecast **one legal opponent reply per candidate**, 16 candidate predictions maximum:
1. **SF16 + PV**: original shared 24k engine PV first response.
2. **Foil-aware simple JSON**: maximize opponent immediate material capture, then check, then lexical tie.
3. **C3X-inspired three-ply finite lawful plan heuristic**: pick adversarial legal response minimizing strongest own legal immediate recapture material after reply (source-lawful, consistent with P21/P29, **NOT** a trained/current full NNUE-C3X explanation system).

First job wrote immutable JSON, original SHA256 `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`, archive SHA `721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6`. [Drive immutable pre-referee forecast](https://drive.google.com/file/d/15l2pZseqxv42BZ6tD0c7B9zzyxsIbvBw/view) uploaded before the referee evidence was opened and re-downloaded SHA-verified.

Only after first job success did second, separate CI referee job open sealed predictions, verify the 8 cases and each frozen prefix from original R1 and compile Stockfish16 afresh. Per original 24k candidate it forced that candidate in a **separate** 96,000-node native reference and extracted the first opponent reply from PV. Also conducted 48k/96k unrestricted MultiPV2 root stability observations. [Drive immutable referee ZIP](https://drive.google.com/file/d/1OXTMXDZVTwL0OVzmX3776sy-9HCD4c78/view) archived SHA256 `3bd8d76602b51f0bbb8b5892452444c27bad19532bc542e58565c726f2d6f93b`, referee JSON SHA `d92c33d05fa506b1a84c222b57729f76a53a95970dd61ba38f67ea1ce3f700fa`, verified against fresh Drive download.

**Important:** The 96k forced-root response is a **same-engine, finite-search reference label**, not objective chess value or actual human continuation. It tends to favor same-engine PV forecasting; this is a legitimate engine-consistency pilot, NOT a general real-future chess consequence benchmark. All three rivals consumed same shared 24k Stockfish engine output and emitted same number of predictions, but **source-derived computational counts are not equal**: both simple JSON and C3X scanned **644 legal first-opponent replies** in total across 16 candidate worlds; the simple JSON expanded **zero** original-player legal continuations, whereas the C3X three-ply plan expanded **24,894 lawful own follow-up moves** (per world 1,061 to 2,342). These are Python legal-move enumeration counts, **not comparable to Stockfish search nodes**. CPU/total cost is NOT equal, and the additional chess-law expansion did NOT yield a 96k-reference reply forecast missed by PV.

## C. Independent re-adjudication corrected a missing reference label

Original referee output retained 16 candidate rows but **one 96k forced-root PV lacks an opponent reply** (Clutch Chess second root `c4a3`): reference `None`. It is neither model correct nor model incorrect and cannot be used as a negative label. Re-audit original frozen ZIPs, never rewrite raw labels, and report 15 evaluable / 1 undefined.

[Read-only independent audit script](../tools/c3x_029_p37_r3_sealed_reply_forecast_reaudit.py) plus [separate read-only CI 41969934262](https://github.com/WhoSia/C3X/actions/runs/41969934262) **SUCCESS** (original two ZIP and their member SHA256 pinned). [Drive original audited ZIP](https://drive.google.com/file/d/13CpPR3j74pExeXjlKSGQDFSKs6tqapHs/view), outer ZIP SHA256 `45c5c826e303e883308231a093bc3159a0ae4e311a98612445167175229e8eb4`, internal audit JSON SHA `2662a182d6405a3a8e0a60ee5f5ec37c60741266952b91b12068cb0f858dad1a`.

### Primary descriptive forecast results (15 with defined finite-depth label)

| Predictive method | Exact 96k root-forced PV reply | Incorrect of evaluable | Reference missing |
|---|---:|---:|---:|
| SF16 + PV | **11/15 (73.3%)** | 4 | 1 |
| Simple conditional JSON | **2/15 (13.3%)** | 13 | 1 |
| C3X lawful finite three-ply plan heuristic | **4/15 (26.7%)** | 11 | 1 |

**Matched exact source-level comparison PV vs C3X legal plan:** PV-only correct **7**, C3X-only correct **0**, both correct **4**, neither correct **4**, undefined reference **1**. **NO independent added reply-forecast information over SF16 PV was demonstrated by this C3X-inspired heuristic.** Do not claim full C3X NNUE theory rejected or a properly CPU-matched classifier test. The source/event sample is very small and cluster/selection/label limitations remain.

### Near-margin transport

Nominal near at 24k (strict gap <20cp): **4/8** game roots: Sahel (13cp), Chinese League (15cp), Magdeburg (13cp), Garcia-Palacios (18cp).

Only **Sahel** kept the *same two candidate UCI and same order* under separate 48k and 96k unrestricted native searches, with gaps **13→12→8cp**. In that near-stable one-game pair **SF16 PV 2/2**, simple JSON **0/2**, C3X legal plan **0/2** on defined referee replies. The other three 24k near pairs lost candidate identity, crossed <20cp boundary or changed ranking. **This is a source-exposed n=1 stabilized case**, not a population claim.

## D. PI decision and research scope

**PROMOTE as verified engineering/scientific observations:** 8 distinct source event-family one-game engine-free preselctions, exact source bytes and 40-previous-game overlap exclusion, genuine two-job forecast-before-reference chronology, SF16 native 24k/96k adjudication, strong PV baseline outperformance of simple two/three-ply nonneural heuristics *for larger-budget Stockfish reply prediction*, and severe near-margin instability in 3/4 nominal near cases. No favorable posthoc case replacement.

**HOLD:** exhaustive historical C3X game/event independent admission, human-chess-value independent adjudication, CPU-equated rival computation, genuine C3X neural causal mediation and explanation value, human-learning effect. Missing referee label is explicitly not scored.

**RESEARCH DECISION:** Do **not** proliferate more 3-ply material-name heuristics, nor select the one near-stable Sahel position as stand-alone evidence of a broad explanation theory. Next scientific court must predefine a **genuinely chess-valued, opponent-conditioned consequence Q**, verified by independent legal rules and/or independent engine families with explicitly separated data access, and compare a source-faithful C3X explanation agent to **SF16 PV, strong foil-aware JSON and abstention** under a common full cost contract. A low-depth static material tactic is insufficient to infer planning value. Consider all legal opponent replies for an identified hypothesis but audit the computational expense; no no-cost oracle for C3X alone. Only test NNUE internal concept mediation if chess-level incremental evidence justifies it.

## Governance

GitHub commits/authorship exclusively authenticated `WhoSia`; Actions only read/compute/upload-artifact and never commit, push, merge, tag or move refs (`github-actions[bot]` contributor forbidden). Notion semantic source of truth, Drive original immutable bytes, GitHub pre-registration/code/results index.
