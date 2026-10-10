# C3X 0.22-P2 — TWIC / Lichess Exact-UCI Forecast Falsification & Root-Depth Chess Microstructure

**RESEARCH CLOSURE • 2026-10-10 • C3X 0.22 ACTIVE • scientific exact-UCI forecast verdict: FAIL on TWIC.**

The full P2 design was frozen before any new FIRST physical TT-reader suppression on 32 independent chess positions selected in two new ecologies, following the explicitly distinct Stage A and Stage B workflows. The trial did not select new records after seeing causal outcomes, did not alter any original TWIC source games to "rescue" model accuracy, and does not interpret predictable nochange cells as a positive mechanism victory.

## Reproducible protocol and exact artifacts

- [Pre-source/pre-engine P2 study contract](c3x-022-P2-TWIC-Lichess-puzzles-exact-move-forecast-precommit.md).
- TWIC issue1656 tournament PGN ZIP (internal analysis only, no public redistribution) source SHA `2970ae7fb943cf67d535ca89489e0bd4e57ec0d1375b4b5220e5946777a04df7`; Lichess puzzle official CC0 compressed snapshot SHA `76335bfa7d7c4a7f93c1366d81549e53951ebb79dd43d34904cab8f22d962f8d`. Exactly 16 disjoint source positions in each ecology, total 32. Eight historical-cohort FEN4 exclusions.
- Engine-free source JSON SHA `ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554` and pre-engine `1,056` chess legal action microstructure profiles SHA `b3b4a29788c1f9dc2b4d491cd60d44ad8e6530d3d66be5d77039a6fd59cc958d`.
- Stage A cold native O/F+source discovery, **no TT reader suppression**, [CI #38047696668](https://github.com/WhoSia/C3X/actions/runs/38047696668) SUCCESS, SHA `0258edda1182ff21f4764e015548125e43978b504e36fa6d7c99a0f235a74fcd`. All exact UCI predictions across 128 potential game×order×STRICT/BROAD role cells [committed into Git before Stage B](../forecasts/c3x-022-P2-TWIC-puzzle32-exact-UCI-preregistered-stageA-20261010.json), commit `1abc7c82f753c3d7c3c540ee3426dfb790e26d22`.
- Stage B real C++ first physical TT reader suppression, writer full64/slot/epoch/rootcall validated, ZERO+impossible-target source controls and cold twice per source. [CI #38047992462](https://github.com/WhoSia/C3X/actions/runs/38047992462) **technical SUCCESS**. Native raw JSON SHA `f8c9210cfb9f158d038e70045a1839c3ecebb487781dbc59ce9615b2491a1899`; ZIP SHA `a1dc3b7c31aecd10c0fc5d24e72a9d841dddb7a3e65e5303a73ba8d27efef037`; **24/24** member SHA PASS.
- Post-outcome **retrospective, NOT predictor refitting** [legal-chess-root-depth Audit CI #38048395017](https://github.com/WhoSia/C3X/actions/runs/38048395017) SUCCESS: join raw outcomes with pre-native legal moves, record the observed 12-depth root leader divergence; derived SHA `f5766e87288d1c4e9d6fcb6155b277045ee75cb2866909b2e856e254549c67f8`, 2/2 member SHA PASS. [Full native falsification receipt](../receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json).

## Primary exact-root-choice decision

Stage A rule **CROSS_ORDER_RESTORATION_V1** is literal and vulnerable: when O/F baseline bestmoves differ, predict O+FIRST = F baseline and F+FIRST = O baseline; when equal predict unchanged, with specific game IDs and full UCI moves for every source-eligible role.

| Result, contacted roles | TWIC tournament PGNs | Lichess online puzzles |
|---|---:|---:|
| Chosen source positions | 16 | 16 |
| Native physical first reader actually blocked | 64/64 | 28/28 |
| Root-order O vs F baseline bestmove disagreement | 8/16 | 0/16 |
| Source-role final bestmove flips | 10 | 0 |
| Distinct games with at least one TT-block bestmove flip | **4/16, games 1,4,7,10** | **0/16** |
| Literal exact-UCI predictions correct | **38/64 = 59.375%** | **28/28 = 100%** |
| Nochange-majority exact-UCI baseline correct | **54/64 = 84.375%** | **28/28 = 100%** |
| Predicted-positive confusion | TP10, FP22, FN0, TN32 | TP0, FP0, FN0, TN28 |
| Positive-flip prediction precision / recall | **0.3125 / 1** | No positives, not defined |
| True changed-root cases with exact new UCI correctly predicted | **6/10** | 0/0 |
| Scientific verdict | **FAIL: exact UCI rule worse than trivial nochange control** | **No positive prediction tested: null-effect control only** |

TWIC **8/16 distinct games** have at least one wrong exact move forecast (game IDs 1,3,4,7,10,12,13,14) even though only four distinct games actually flip under intervention. This reveals false-positive root-order reversion claims in unflipped games. Counts of 64 TWIC source roles are correlated within 16 games; do not treat 64 as independent game trials or compute unwarranted p-values. Lichess has fewer full64 physical source eligible arms and zero actual final-choice switches. Its noflip 28/28 agreement is **not** evidence of positive causal forecasting because the same result is obtained by the trivial no-change majority predictor.

## Three-mechanism counterexamples, source exact and chess grounded

### TWIC game4 — queen capture versus a third queen move

Source is a Standard Chess board from TWIC 1656's Kavala Open. Natural O first chooses **b5c3**, played-first F chooses **c2c8**. The latter is a **queen capturing on c8 and giving check**, followed by only **5** legal replies; immediate legal capture of the queen on c8 includes **b7c8**. O's knight relocation **b5c3** leaves **34** opponent legal replies and is capturable by **c8c3**.

Physically suppressing first TT consumer in **O** (both STRICT/BROAD) produces **c2c8**, matching cross-order prediction. But suppressing it in **F** (both selectors) produces **c2d1**, a QUIET queen relocation leaving **36** opponent legal replies, rather than predicted **b5c3**. First observed root-leader divergence: O depths **11,12** versus F depths **9,10,12**. These three legal choices differ below the named pin/skewer vocabulary: immediate capture/check, return-response fan, legal recapture at destination and source-specific piece→square attack relation. This shows non-reversion with observable depth transmission, **not** proof that SF16 used any one chess primitive as a unique valuation cause.

### TWIC game10 — rook versus rook versus a third pawn capture

From TWIC 1656 British Major Open: baseline O bestmove **f8f7** (black rook), baseline F **a8e8** (different black rook). O+FIRST (both roles) chooses **f4g3**, a black pawn capturing white on g3 with opponent legal recaptures **f2g3** and **h2g3**; the two rook relocations each leave 39 white legal replies while the pawn capture leaves 40. Stage A predicted O+FIRST **a8e8** and is wrong. F+FIRST (STRICT) chooses **f8f7**, which does restore O baseline. Earliest altered leader at depth **6** in O and F, but the sequence is not monotone: O divergent depths **6,8,10,11,12**, F **6,7,8,10,12**. Do not assert a source-aligned continuous causal root-call chain beyond divergence without C++ actor traces.

### TWIC game7 — final-depth-only root switch

Baseline F **a7a5** (black pawn) and native FIRST **d8d7** (black queen) as predicted by original O. The entire logged root-leader trajectory differs **only at depth 12**. Both leave 42 immediate legal opponent replies, but piece/square attack-edge gains/losses differ sharply (pawn +3/−1 versus queen +20/−13). A priori "which named tactic" labels miss where in *native* iterative search the decision becomes distinct.

### TWIC game1 — same response count but different threats

F baseline **e1d1** (white rook relocation) and F+FIRST **g3e2** (white knight relocation), correctly predicted by O baseline. Both leave **44** legal Black replies, but after rook e1d1, black can capture the moved rook via **d8d1** whereas after knight g3e2 no immediate legal destination capture is recorded. Native root leaders separate at depths **8–12**.

## Scope and paper route

P2 is a more stringent, correctly failed transfer test following C3X0.22-P1's April **3/3 weaker existence hypotheses PASS**. They concern different claims, and a failure of P2 is not to be backfilled into April's earlier completed tests.

Useful contributions even given P2 FAIL:
1. Standardized pre-native freezing of board-level chess decision primitives across tournament PGNs and online forced puzzle problems.
2. Source exact full64 TT reader intervention under independent O and F ordering, with real contact dose and sham controls.
3. First independent cross-ecology **falsification** of exact move predictions and source-specific counterexamples including a *third chosen move* not supported by simple reversion.
4. Frozen 12-depth per-case native root leader differentiation (not unique mediation proof), including terminal puzzle source without fabricated TT or depth trace.
5. Dataset provenance/licensing separation and honest heldout role/game grouping.

**Paper A** — "When Search Order Changes the Move: Source-Exact Transposition-Table Interventions in Alpha–Beta Chess Search" — now has strong *methodology and falsification* case material, but an adequate **successful held-out exact-move explanatory predictor has not yet been developed**. The near-term potential manuscript should lead with the native causal falsification method and accurate counterexample boundaries, not claim solved engine explanation or broadly transferable bestmove law.

### Next proposed 0.22-P2-R1 title

**C3X 0.22-P2-R1 — Path-Dependent Candidate Emergence & Search-State Causal Transmission: Source-Matched Root Survivor Histories, TT Value-Use/Cutoff Rivalry, SEE–Recapture Microstructure Interventions & New-Ecology Exact-Move Forecasts**

Training/development cases can include TWIC issue1656 game4/10 and previous March/April cases. New held-out benchmark must choose an *unseen* different TWIC issue and/or separate distinct games (obey original TWIC rights) with fixed game-level denominators and before-outcome signed per-cell UCI forecasts. Puzzle track should stratify mate/forced-line versus non-mate puzzles, not hide 36/64 NO_ELIGIBLE source roles or report 0 flips as a successful positive-prediction result. New source-level mediator hypotheses must separate: first TT block, physical writer/reader, actual TT score assignment/cutoff, root candidate update, aspiration retry, SEE legal exchange constraints, and end-of-depth root leader. The chess-board relation comparison is an independent explanatory hypothesis until an operation-specific causal ablation proves contact.

**Historical F19.5, K4 (0/4), Jan J2/J3/J4 and failed PAG/CPP224 remain negative.**
