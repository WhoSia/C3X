# C3X 0.15 — P1 Source-Frozen Same-Law Context Subdivision, Operator Response Prediction & Native Trace Precommit (NOT EXECUTED)

**Governance:** 2026-10-09. C3X 0.15 formal research program OPEN by PI. This is a prospective P1 specification, not an outcome, discovered internal type, or new Notion page. The original P0 R1 is immutable; R2 is the selected source-only new-provider cohort. No TWIC engine outcome read by P0/P1 at this writing. The old procedural 4-game P1 holdout is **not** this P1 and remains sealed.

## Input locks and authority

- Authentic TWIC 1665 ZIP https://theweekinchess.com/zips/twic1665g.zip (publisher restricts use and redistribution). ZIP SHA256 `23097bbf152d9afed810890456027ce639719f7a4ef4c723898730d391b347b3`; internal PGN SHA256 `642f458c6ef8c5661e62a5f056ad225cabf29a4b12c65be0f834a1e60ad610a6`. Do **not** publicly rehost raw ZIP, raw PGN, or substantially reconstructive derivatives.
- Source-only TWIC R2 manifest SHA256 `1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534` from successful [read-only CI #37902655949](https://github.com/WhoSia/C3X/actions/runs/37902655949). Exactly 64 originally pinned root worlds and 64 game-distinct no-side-to-move-absolute-PIN controls, 128 distinct game traces and 128 exact six-field FENs. 11 distinct event headings, <=8 PIN worlds per event. At most one PIN world/game and control selected from separate games; within-event clusters are not statistically independent. Controls are defined as **no pinned object for side to move**, not assertion neither player's king has any pin.
- Previous TCEC S28/S29 original 100+100 game source replays excluded 32 overlapping positions during candidate search. Older C3X 0.13 P7-R1 source subset 29 legally reconstructable roots cross-checked with 0 exact/simplified board collisions. **No global historical C3X nonoverlap certificate**, because other historical PGNs were not exhausted. Hold full transport promotion until that bounded reference census.
- Record all game counts, event grouping, source header anomalies, top-game opening correlations, within-archive duplicate game hashes, six-field and four-field board-key leakage, and manifest-vs-replay equality. If any pre-engine source defect is found, keep prior SHA and apply transparent fail/repair with a new cohort version before any treated labels. No post-response substitutions.

## P1-S0 legal subdivision: 39 law signatures, only 10 replicated across events

This is a **chess-law stratification**, not engine-internal classes. For the 64 frozen PIN roots:
- 39 distinct five-field law signatures `(pinned_piece,pinner_piece,axis,legal pinned mobility,pinner capture)`.
- 29 signatures occur only once; reject a claim of within-subtype predictive replication for these.
- 10 signatures occur at least twice and span distinct tournament events, comprising **35 source-game roots** total. Five signatures occur at least three times across distinct events.
- Four historically repeated S29 law families prospectively available inside TWIC R2:
  - pawn pinned by queen along diagonal, ZERO pinned-piece legal mobility, cannot capture pinner: **6 worlds / 5 tournament events**;
  - pawn pinned by queen along file, NONZERO mobility, cannot capture pinner: **7 / 5**;
  - rook pinned by queen along diagonal, ZERO mobility, cannot capture pinner: **2 / 2**;
  - pawn pinned by rook along file, NONZERO mobility, cannot capture pinner: **3 / 3**.
These four families supply 18 PIN game worlds, not 18 independent mechanistic subtypes. Fix group membership from source law alone; never split a family by observed engine outputs, TT ordinal, unique FEN, or exact event ID.

## Candidate typed fiber and variable-time contract

For a pinned root object `(P,s)` and frozen search environment `e`:

`F(P,s,e)=[G,A,N,I,M,T]`

- `G`: game-law geometry and legal action limits, certified by PGN + independent chess library.
- `A`: explicit root operator opportunity (native no-go legal move/SEE/WeakQueen diagnostic, not organic execution).
- `N`: observed natural source-site activity with exact root-key/site granularity, distinct from whole-tree descendant activity.
- `I`: causal source-code treatment effects and armed-site counts. They are software-search effects, not proof a latent NNUE semantic category exists.
- `M`: measured **post-treatment** search divergence, TT producer-slot-consumer identity, alpha/beta window, stored/consumed bound, depth gap, history/LMR, PV and completedDepth. Use as mediator analysis endpoint, never covertly as prospective pre-treatment predictor.
- `T`: source/provider/engine/ecology transfer not earned merely by naming two chess providers. Source-disjointness, treatment invariance, and wider validity remain separate gates.

**Frozen pre-treatment predictors:** from original PGN/FEN only: five-field law vector, pinned king/piece/pinner squares as geometric ray lengths or categorical relationship (NOT exact square identities), total material piece count and type vector, coarse game phase, root legal move count, check state, legal pinned-piece moves, and root move time/ply bucket. Freeze finite bin boundaries and a fully specified feature schema prior to outcome readout. Tournament/event/player/game/FEN/raw SAN/PV/TT slot/actual treated node count are **not permitted as direct model features**. A source-pinned untreated OFF native trace could become an explicitly separately labeled SECONDARY predictor only if acquired and frozen before **treatment**; it cannot replace the primary chess-only prospective predictor. NNUE option/fallback must be observed and reported by route, not assumed.

## Outcomes and baselines to freeze before source intervention

1. **Primary mechanism endpoint** for 64 PIN worlds: whether precise original-root-object-conditioned SEE unmask changes Stockfish16 classical depth12 bestmove vs untouched OFF. This is **binary**, not tautologically equal to source firing.
2. **Secondary four-bit global endpoint**: bestmove response under four *distinct* global source arms `SEE_UNMASK/WQ_OWN/WQ_ENEMY/WQ_BOTH`, relative to the same pristine OFF. Bit order frozen exactly as 0.14. Do not merge the root-object SEE response into the four-bit signature; it is a separate fifth indicator with a different treatment definition.
3. **Mechanism/contact endpoints**: natural/explicit actual SEE/PIN and WeakQueen site fire, negative no-fire→unaltered full UCI, native legal move invariance, root vs descendant event identity, first differing site/window/TT bound and eventual PV/root preference.
4. **Sham/nonpin baseline cohort (64)**: if no side-to-move root pinned object exists, root-object-pinned treatment is ineligible and should have zero armed root-object effect. Nonpin samples are neither a mathematically perfect matched counterfactual nor evidence all other descendant pins are absent.

Predeclare competing predictors from past S29/S28 only: (B0) always no bestmove flip `0` / secondary always `0000`; (B1) five-feature law-only stratum majority with unseen class fallback B0; (C1) chess-only low-dimensional context conditional model with fixed source training and regularization chosen **before** TWIC labels. **At this P1 constitution, C1 coefficients/threshold/model artifact SHA are NOT YET SEALED: prohibit new TWIC outcome opening until that occurs.** Training can use prior revealed S29/S28 development worlds but must exclude R2 and other new-provider treated data. Explicitly label any planned use of older post-hoc S28 guarded outcomes and avoid pretending it was prior prescore blind.

**Evaluation design:** paired per-root comparisons for B0/B1/C1; report primary binary accuracy, balanced accuracy, sensitivity/specificity, log-loss/Brier (only for probabilistic outputs), and matched bootstrap uncertainty clustered first by event (11), with game and unique FEN as nested units. Repeated source 0.14 cold runs and each of four treatments on one position do NOT create fresh independent roots. Run (a) all 64 PIN worlds, (b) 35 same-law repeated support worlds; hold the 29 law singletons as sparse-support/OOD descriptive. Calculate exact four-bit match as secondary, never select winning evaluation metrics after labels. A prospective positive mechanistic contact case AND an actual negative/no-fire case must be documented. A failed 0000 comparison remains FAIL/HOLD rather than repair by post-outcome context feature invention. For claim promotion, show both meaningful superiority to B0 and event-cluster uncertainty; no claimed gain based on incidental event IDs.

## Stockfish16 native test gating and polyglot roles

- Exact unmodified SF16 upstream `sf_16` Git `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Reuse vetted 0.14 native C++ patch `tools/c3x_014_ROOT_PIN_object_only_SEE_unmask_patch.py` for target SEE. Build original and patched from exact source, compiler/flags pinned; origin root square+color+type+pinner+king guards are NOT permanent physical-piece lineage.
- Pristine OFF sham and no-fire/irrelevant-object controls, unchanged chess legal moves, two independent cold UCI processes with identical options `Use NNUE=false; depth12; Threads1; Hash16 MiB; MultiPV1`. Explicit source events and potential no-go opportunity measured separately. Any mismatch in baseline equivalence, no-fire invariance, cold technical repeats, legal game history, or root source object is a fail gate.
- Native trace attribution: per-event full position key, TT slot generation/full-key last writer, overwrite/age, writer site (MAIN_TERMINAL versus ProbCut etc.), consumed stored-depth/requested-depth difference, BOUND_EXACT/LOWER/UPPER, value normalization and alpha/beta window at writer and return. Root-object-conditioned search may first diverge at a descendant site; do not claim intervention on the root pin geometry itself.
- **C++** only original engine search semantics and trace. **Python/chess** source-law parser and orchestrator. **Rust** deterministic typed evidence/receipt compiler. **Go/TypeScript** independent interpreter or public explanation authority verifier. Each language must test a distinct failure mode; programming-language proliferation alone is not scientific novelty.
- CI may checkout/build/test/upload ephemeral artifacts with `contents:read/actions:read`; no workflows pushing or creating `github-actions[bot]` authored commits. New git commits made as human `WhoSia`. Preserve 0.14 original receipts and old procedural sealed P1 four-game holdout untouched.

## STOP / claims / publication

P1-S0 after this document: **SOURCE_REPEATED_LAW_SUPPORT_CERTIFIED, PREDICTOR_MODEL_UNSEALED, NO_FRESH_ENGINE_OUTCOME_OPENED**. Next allowed step is completely source-only model and coefficient/calibration freeze, historical source-overlap closure, then only the explicitly locked native comparisons. Don't declare C3X0.15 external *causal* transport, stable causal subtypes, NNUE learned pin concepts, or a paper acceptance without a new independent and auditable causal result. Publish honest negative results and case-specific computation explanation if the classification fails. Keep C3X 0.15 canonical source of truth in the existing one Notion Lab; no extra subpages.
