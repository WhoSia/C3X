# C3X 0.22-P1 — Prospective Root-Choice Court and Paper-A Evidence Review

**2026-10-10 · Closed April16 P1 observational/synthetic-native court · C3X 0.22 ACTIVE**

## Research thesis

C3X 0.22 examines the *native computer search process* and the *legal chess action-space* on parallel but separately controlled scales: full64 TT writer–reader provenance, controlled first-reader suppression, initial root-order treatments, and precomputed standard-chess move affordances. The endpoint is the final categorical legal bestmove at cold depth12. Any claim about *why the search values a particular tactical feature* requires additional source-exact chess operator interventions, not merely matching a motif description.

## Independent experimental design and precommit

- Pre-April, pre-native forecast locked at [P0 contract](c3x-022-P0-april2026-independent-ecology-source-and-prospective-forecast-precommit.md).
- Official original Lichess broadcast archive April2026 SHA256 97b036f3a3639ae3be59c1508b1e18c76ac1b2e8fada4587d1b5c5a93c438d5d.
- Exactly 16 engine-blind April games from first512 eligible, seven historical source FEN exclusions; April source SHA 0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93.
- Exact 486 legal move decision-primitive profiles frozen **before native** (SHA 95b3d8857bad9147d5d655dcbe5d0e31300c57833bd6d04a8a905f278ac67986).
- Original Stockfish16 commit 68e1e9b3811e16cad014b590d7443b9063b52, one thread, 16MB hash, NNUE false, depth12. Independent cold engines each role; O natural original root order vs F original game-played legal move rotated to first; STRICT/BROAD physical TT selectors each independently and passively constructed within its **own** order, using unchanged C3X 0.18 January rules.
- Actual full64 physical first-reader block, writer provenance, exact UCI, source-aligned initial return, and chess move legality cross-check. ZERO/decoy/OZ/observation controls all remain equal where required.
- Technical run #38045865240 failed in a **noneligible role log expression** (missing optional field); fail-closed, no scientific verdict issued. Logger fixed with a safe optional-field read, then full success run [#38045977655](https://github.com/WhoSia/C3X/actions/runs/38045977655). Source and predictions unchanged, so this repair does not respecify the hypothesis.

## Main independent results

| Registered hypothesis | Registered measurable claim | April result | Verdict |
|---|---|---|---|
| H22-ORDER | >=1 of 16 distinct O/F games has different final bestmove | Game IDs **3, 13** = 2/16 | **PASS** |
| H22-NATIVE | >=1 distinct game with delivered source-first TT reader suppression changes final bestmove in O or F | Game IDs **3, 15** = 2/16; 60/64 physically contacted role cells | **PASS** |
| H22-CONTEXT | Set of affected games in natural O not equal set affected in rotated F | O set **{3}**, F set **{15}** | **PASS** |

There are **60 eligible and actually contacted role cells of 64**, but each game's STRICT/BROAD roles are nested and may target identical physical memory. Effect denominators and confidence uncertainty should therefore be defined at 16 games, not 64 independent trials. The 2/16 rate is 12.5%; a descriptive binomial Wilson 95% interval would be approximately **3.5%–36.0%**, not a strong population estimate because source selection is not randomized over all chess positions.

Raw signed source events, control UCI, source physical full64 and binary SHA are preserved in [native result receipt](../receipts/c3x-022-P1-april16-prospective-native-order-TT-forecast-20261010.json). Native ZIP SHA fef0e988139b8644f88e97f194c56fa47fbb79e9b1c236cb9a91e887bbc63ba8; 24/24 member SHA validation PASS.

## New causal contrast A: April game 3

Board at source: 2rq1rk1/1p1nbpp1/p3p2p/2pp4/P4P2/1P1PPQ2/1BP1N1PP/R4RK1 b - -.

- Natural O final bestmove **d8b6** (black queen), score 0cp, 62,350 nodes.
- Played-first F final bestmove **e7f6** (black bishop), score 0cp, 51,897 nodes.
- Natural O+STRICT actual first physical TT reader suppression final bestmove **e7f6**, 8cp, 75,013 nodes.
- First recorded source-aligned return changes **+1 → 0**, with alpha +9 and beta +29, candidate index7/depth7. Both returns are below alpha (SAME_GATE at first aligned difference); the eventual final root selection changes later in the search process.
- Pre-native chess features: queen d8b6 leaves **42** immediate legal white replies, bishop e7f6 leaves **41**; after e7f6 white can immediately capture the moved bishop with **b2f6**. Neither root move creates a directly recorded pin addition/removal.

Meaning: FIRST source-physical TT suppression can erase a natural O-vs-F root-order difference. This is a genuine same-board search-state effect, not automatically evidence that the bishop's capturability is why the TT intervention changed the move.

## New causal contrast B: April game 15

Board at source: 2r1r1k1/1bq2p1p/pp1p1npb/2nPp3/P1P5/2R2N1P/1P1N1PPB/1B1QR1K1 b - -.

- O baseline final bestmove = F baseline bestmove = **b6b5**, 66cp / 99cp, respectively.
- Played-first F+BROAD actual first physical TT reader suppression chooses **a6a5**, 36cp and 62,628 nodes. Original F was 44,403 nodes.
- First source-aligned return **0 → +191** with alpha +255 and beta +283, candidate index2/depth5; both returns below alpha (SAME_GATE).
- Pre-native chess features: after b6b5, white has **41** legal replies and can capture b5 with either **a4b5** or **c4b5**. After a6a5, white has **38** legal replies and no immediate legal capture of the moved pawn's destination square. Both are ordinary black pawn moves, no pin-gain/loss signature.

Meaning: Unlike the March case pattern where F+FIRST had returned to original O, here FIRST TT suppression produces a **third final legal move not selected in either baseline O or F**. That is a direct falsifying case against a blanket “TT suppression merely removes root-order bias” account.

## Auxiliary control: game 13

O natural bestmove **a7a6** (−86cp), F played-first bestmove **d8d7** (−82cp). Both selected O/F FIRST TT interventions leave their final categorical choices unchanged. This separates a root-order-sensitive game from a game sensitive to the selected physical first-reader intervention.

## Scientific judgment and falsification front

The prospective three-claim PASS supports a **reproducible and order-sensitive search-memory phenomenon in disjoint April games**. It does not yet provide a per-game predictive classifier that says “game 3 will flip” or “TT intervention makes exactly move e7f6”; the risky forecasts were *existential*, not specific-game forecasts. It does not prove the selected chess primitive feature is consumed as a causal motive in Stockfish's internal scoring.

The first source-aligned return events for **both** flipped April games are SAME_GATE. This is a reason to prioritize deeper source-path mediation (aspiration retries, root candidate life history, TT score vs move ordering, repetition and cutoff guards), rather than fitting another universal instant-alpha-threshold rule. C3X0.20's within-case one-centipawn sharp alpha gate remains valid for its specific February adaptive setting.

## Manuscript A plan

Provisional paper title: **When Search Order Changes the Move: Source-Exact Transposition-Table Interventions in Alpha–Beta Chess Search**.

- **Research contribution 1:** independently reconstructed physical memory writer–reader interventions under distinct root-order histories, with full64/slot/epoch contact and no-contact control.
- **Research contribution 2:** distinct April heldout cohort precommit and explicit separate verdicts rather than outcome-defined success; 3/3 pilot-level forecasts PASS.
- **Research contribution 3:** pre-engine-snapshot legal chess action primitives used to describe the differences between candidate moves without inventing named tactical mediators.
- **Unresolved:** robust per-game forecast, broad 64–128 new-game replication, native source-path transmission accounting beyond first aligned return, within-source randomization/multiple engine comparisons, test-time sensitivity to depth/hash/NNUE, uncertainty calibration, competing explainable-search prior art.

Bibliographic checkpoints: Björnsson (2024), *Chess and Explainable AI* (DOI 10.3233/ICG-240256); Hammersborg & Strümke (2024), *Information based explanation methods for deep learning agents—with applications on large open-source chess models* (DOI 10.1038/s41598-024-70701-2); Baier & Kaisers (2020), *Explainable Search*. The full-text competitive review remains pending. Do not assert peer-review or accepted novelty from this pilot.

## Suggested next phase

**C3X 0.22-P2 — Prospective Move-Specific Causal Forecasts & Multi-Depth Search-State Transmission: Held-Out Game Ranking, Source-Aligned Root Survival, Response-Contingent Legal Affordance Tests & Native TT Mechanism Ablation**.

A correct next advance must predict **which** games and **which** final legal moves will change *before* they are inspected, with calibrated controls and an independently frozen 64–128 game source. Reserve March/April games for model development, not test-set reuse. Preserve original F19.5, K4, January J2–J4 and CPP224/PAG failures. No paper is submitted or accepted.
