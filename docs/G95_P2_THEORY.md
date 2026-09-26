# C3X 0.7.0-G9.5-P2 — Context-Indexed Causal Fiber Field

## 1. Return to the P1 counterexample

P1 replaced hand-designed structural quotients with an intervention-response fiber. The coarsest admissible fiber, F0, preserved the binding Stockfish singleton witness and was locally congruent inside all six fresh engine-worlds. Yet one F0 class changed causal meaning across contexts:

`F0|MAIN|MOVE_ORDER_SEED|1|-1|4`

contained both ROOT_CHANGE=true and ROOT_CHANGE=false members, including a reversal within Berserk across two fresh positions. Therefore neither F0 alone nor engine identity alone is a transportable causal kind.

P2 asks a stronger question:

> What is the smallest prospectively measurable pre-intervention context that makes the causal meaning of an otherwise identical intervention-response fiber transportable?

The phrase "pre-intervention" is binding. A context coordinate may be measured from the chess position, the unablated parent search, the candidate event as it exists in that parent trace, or source-grounded architecture semantics. It may not be computed from the singleton intervention's root response.

## 2. Field rather than universal class

For an exact event record r, let:

- `F(r)` be the frozen P1 F0 intervention-response fiber;
- `C(r)` be a vector of pre-intervention context coordinates;
- `Y(r) ∈ {0,1}` be ROOT_CHANGE after singleton exact-event removal.

For a subset S of context coordinates, define the context-indexed cell

`K_S(r) = (F(r), C_S(r))`.

S is discovery-congruent when:

`K_S(r_i) = K_S(r_j) ⇒ Y(r_i) = Y(r_j)`

for every fired discovery pair.

This is deliberately stronger and simpler than fitting a probabilistic predictor. P2 asks whether equal context-indexed fibers are intervention-response congruent under the tested query.

A discovered field is partial:

`L_S : F × C_S ⇀ {0,1}`.

If a held-out cell was never seen in discovery, the implementation returns `ABSTAIN_UNSEEN_CONTEXT`; it does not extrapolate a label.

## 3. Relation to prior work

P2 borrows a discipline, not a theorem, from several literatures.

- **Invariant prediction:** if an adequate conditioning set has been found, the target relation should remain stable across environments. C3X uses exact deterministic ROOT_CHANGE congruence instead of a fitted conditional distribution.
- **Transportability:** cross-environment transfer needs explicit assumptions about which mechanisms differ and which remain shared. C3X treats the context basis as an empirical licensing condition, not as a guarantee inferred from environment names.
- **Multiple versions of treatment:** the same coarse intervention label can hide causally distinct versions. P1's same-F0/different-ROOT_CHANGE witness is a mechanistic analogue: a fiber label is not sufficient until relevant context is represented.
- **Context-specific causal models:** a causal relation may be valid only inside a context rather than globally. P2 therefore targets a field of local causal laws, not another universal quotient.
- **Causal abstraction / non-linear representation dilemma:** unrestricted alignment can become vacuous. P2 freezes a small hand-auditable coordinate vocabulary and bounded basis cardinality before P2 outcomes.
- **P23–P26 return-to-origin:** prior C3X work found pre-intervention search-state modulation and architecture-indexed law families. P2 imports their geometry as candidate context—not their earlier outcomes.

## 4. Frozen context vocabulary

### 4.1 Portable board coordinates

These are computed with python-chess from the FEN and do not use engine output.

1. `board_legal_bucket`: legal move count in `0–20 / 21–30 / 31–40 / 41+`.
2. `board_center_bucket`: occupied squares among d4/e4/d5/e5 in `0 / 1 / 2+`.
3. `board_development_bucket`: non-pawn pieces displaced from orthodox home squares in `0–2 / 3–5 / 6+`.
4. `board_castling_bucket`: castling rights currently available to side-to-move in `0 / 1 / 2`.

### 4.2 Portable parent-search coordinates

These are measured from the unablated parent search and P32 semantic-use trace.

5. `parent_score_bucket`: mate− / cp≤−150 / −149..−50 / −49..49 / 50..149 / ≥150 / mate+.
6. `parent_depth_bucket`: `≤8 / 9–12 / 13–16 / 17+`.
7. `parent_activity_bucket`: catalogued semantic-use events in `≤63 / 64–255 / 256–1023 / 1024+`.
8. `parent_qshare_bucket`: QSEARCH share in `0 / (0,.1] / (.1,.3] / >.3`.
9. `parent_class_balance`: sign of MOVE_ORDER_SEED count minus all evaluation-reuse counts.

The last three are a direct return to P24's activity/share/imbalance geometry, now defined over exact semantic-use traces.

### 4.3 Portable event-local coordinates

These describe the candidate before singleton removal.

10. `event_depth_bucket`: `≤0 / 1–4 / 5–8 / 9–12 / 13–16 / 17+`.
11. `event_occ_bucket`: exact-signature occurrence `1 / 2 / 3+`.
12. `event_ordinal_bucket`: candidate ordinal quartile in the parent semantic-use trace.
13. `event_window_relation`: TT value `≤alpha / between / ≥beta`.
14. `event_move_presence`: whether a nonzero TT move is present.
15. `event_payload_sign`: negative / zero / positive.

### 4.4 Secondary architecture coordinates

These are the P25 source-grounded descriptors, not engine names:

- `arch_indexing_family`
- `arch_probe_refreshes_age`
- `arch_probe_returns_replacement_handle`
- `arch_eval_move_packed`

Architecture coordinates are excluded from the primary portable-basis search. They form a secondary diagnostic lane only. At most one architecture coordinate may enter a diagnostic basis, and at least one portable coordinate must also be present. This prevents "engine identity by another name" from becoming the main result.

## 5. Discovery and minimality

Fresh discovery uses eight hash-selected positions from the pinned Stockfish Books `4mvs_+90_+99.epd`, excluding the two P1 positions. Each is executed on Stockfish 19, Berserk, and Ethereal with eight prospectively selected exact events.

The event sampler is pre-intervention and source-balanced:

1. group parent events by `scope × semantic class × ply bucket`;
2. sort each stratum by exact address ID;
3. round-robin strata in lexical order;
4. stop after eight distinct events.

No ROOT_CHANGE result enters candidate selection.

A discovery support court must observe at least:

- 96 fired exact-event records;
- 2 ROOT_CHANGE=true records;
- 24 ROOT_CHANGE=false records.

Otherwise P2 closes as support-limited rather than inventing a richer context map.

Every portable coordinate subset of cardinality 0→3 is enumerated. A subset is admissible only if:

- discovery target collisions = 0;
- compression ≥ 0.20;
- at least 24 records belong to cells spanning ≥2 discovery positions;
- at least 12 records belong to cells spanning ≥2 engines;
- both target labels occur in the discovery support.

The minimum cardinality is binding. **All** minimum-cardinality admissible bases are retained; non-uniqueness is reported rather than hidden.

If no portable basis passes, a secondary architecture-indexed search up to total cardinality four is run for diagnosis only.

## 6. Target-blind held-out scope calibration

Held-out positions come from a different pinned book, `8mvs_+90_+99.epd`, again eight hash-selected positions × three engines.

The held-out singleton interventions are executed once. Each job emits two separately named artifacts:

1. a **profile packet** containing F0 plus pre-intervention context, but no ROOT_CHANGE, bestmove, score, WDL or counterfactual PV;
2. a **target packet** containing the sealed root-response facts.

The scope-selection job receives only profile packets.

Among the discovery-minimal portable bases, the primary basis is selected by:

1. maximum number of held-out records whose context-indexed cell exists in the discovery field;
2. maximum number of covered engines;
3. maximum number of covered held-out positions;
4. lexical basis ID tie-break.

This step may use held-out covariates and F0 diagnostics, but not held-out target outcomes.

Before target opening, the selected basis must prospectively cover:

- at least 25% of fired held-out profiles;
- all three engines;
- at least four of eight held-out positions;
- at least one discovery-predicted positive held-out profile.

Otherwise the court emits `HOLDOUT_SCOPE_INSUFFICIENT`.

## 7. Held-out transport gate

After the scope seal, the target packets may be opened.

The selected field earns held-out transport only if:

- every covered held-out record agrees with its discovery field label;
- no covered context-indexed fiber contains both target labels;
- the frozen coverage gate was already satisfied before targets were opened.

Unseen signatures remain abstentions and are not counted as prediction errors.

This distinction is intentional:

- **collision** falsifies the proposed context basis;
- **abstention** marks a boundary of demonstrated authority.

## 8. Engine-specific research lane

Using the same discovery records, P2 also computes minimal portable bases independently for Stockfish, Berserk, and Ethereal. These engine-specific bases are descriptive comparison objects.

Questions include:

- Do all three engines need the same dynamic context dimensions?
- Does one architecture require event-local context while another requires world/search-state context?
- Does the cross-engine field require a strict superset of every within-engine basis?
- Do P25 source descriptors explain residual differences once dynamic context is conditioned on?

No engine-specific result can replace the cross-engine held-out gate.

## 9. The implementation object

P2 materializes a reusable tool rather than only a court-specific script.

`c3x-field` is a typed Rust CLI with three stable operations:

- `discover`: enumerate frozen context bases and emit minimal-basis certificates;
- `scope`: apply a discovery field to redacted new profiles and emit prediction/abstention coverage without target access;
- `verify`: join a sealed scope certificate to later-opened targets and emit transport/collision certificates.

`tools/c3x-context.py` is the chess-aware front end. It computes the frozen board/search/event context packet from FEN + parent trace + exact event, and exposes the same packet schema used by the research court.

The intended external workflow is therefore:

`instrumented engine → exact-event replay → F0 lineage fiber → pre-context packet → c3x-field → CERTIFIED / ABSTAIN / COLLISION → bounded explanation`.

## 10. Claim ceiling

P2 may establish a finite, query-specific, context-indexed causal field over the frozen books, engines, search history and node budget. It may not claim:

- that the selected coordinates are the unique true causal context variables;
- transport to arbitrary chess positions, engine versions or search budgets;
- that architecture descriptors cause any residual difference;
- that an abstained event is non-causal;
- strategy, cognition, human intent, or population prevalence.

A successful P2 field is a reusable **certificate system for where an exact-event causal explanation is licensed**, not a universal theory of chess-engine causation.
