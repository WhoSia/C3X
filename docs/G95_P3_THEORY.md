# C3X 0.7.0-G9.5-P3 — Causal-Field Failure Decomposition and Prefix-Topology Reconstitution

## 1. Explanandum lock

P2 did not fail because its discovery field was poorly fit. It failed in the stronger place that matters: a prospectively minimal, target-blind scoped field that perfectly separated 192 discovery probes produced eight contradictions and one mixed context cell on new positions.

P3 asks:

> Which kind of causally available pre-intervention structure must be represented for an exact TT-use fiber's ROOT_CHANGE law to transport beyond the contexts on which it was discovered?

The P2 contradictions are **development-only failure witnesses**. They may motivate schema families, frozen rival controls and diagnostic tooling, but they have zero confirmatory authority in P3.

## 2. Strong pre-intervention semantics: event-prefix availability

P3 strengthens the meaning of pre-intervention context. It is not enough that a quantity was measured from the baseline run before the counterfactual replay. A primary context coordinate must also be available **at or before the candidate event in the unablated parent trace**.

Therefore primary P3 cells may use:
- board state known before search;
- parent-search summary fixed before the singleton counterfactual;
- the candidate event's own attributes;
- prior semantic-use events up to the candidate ordinal;
- equality relations between the candidate TT key and **earlier** TT uses.

They may not use:
- the next semantic-use event after the candidate;
- future same-key recurrence;
- symmetric trace windows containing post-candidate events;
- any counterfactual output.

The raw TT key is used transiently only for equality tests. It is never serialized into a profile or field identity.

This is a causal-availability firewall against conditioning on baseline descendants of the very event whose intervention effect is being explained.

## 3. No cardinality race

P3 does not enumerate arbitrary supersets of the P2 basis until one passes. It freezes five semantically distinct primary schema families before fresh P3 outcomes:

1. **P2_BASE** — parent search depth, exact-signature occurrence, trace quartile.
2. **TT_LOCAL** — P2_BASE + event window relation, bound class, payload sign.
3. **TEMPORAL_LOCAL** — P2_BASE + immediately previous semantic class, gap to previous same-class use, previous-scope→current-scope transition.
4. **KEY_REUSE_TOPOLOGY** — P2_BASE + same-key prefix reuse count, gap to previous same-key use, previous-scope→current-scope transition.
5. **MINIMAL_HYBRID** — P2_BASE + previous same-class gap, same-key prefix reuse count, window relation.

Engine name, FEN, position hash, raw TT key, exact address and learned world identifiers remain forbidden primary coordinates.

## 4. Development-derived legacy surface rivals

A post-P2 analysis asked a deliberately dangerous question: if we ignore transport discipline and search only the existing P2 surface vocabulary, how many coordinates are required to make the pooled 384 P2 discovery+held-out records collision-free?

No subset of cardinality 0–4 sufficed. Two cardinality-5 subsets did:

- **LEGACY_SURFACE_5A** = board center + board development + event depth + event occurrence + event ordinal.
- **LEGACY_SURFACE_5B** = board development + event depth + event occurrence + event ordinal + parent score.

These are frozen into P3 as **development-derived rivals only**. Fresh P3 discovery computes their collision/compression/support metrics so the topology proposal faces a real rival: perhaps topology is unnecessary and a larger legacy surface already works.

They are never eligible for:
- primary schema selection;
- engine-specific schema selection;
- P3 support gates;
- a PASS verdict.

A strong fresh result is therefore not “some representation fit.” It must distinguish the prospectively motivated topology family from a post-hoc legacy-capacity control.

## 5. Fresh authority split

P3 uses a new source split from the pinned Stockfish Books commit:
- fresh reconstitution: `6mvs_+90_+99.epd`;
- held-out regime: `8mvs_big_+80_+109.epd`.

All P1/P2 position hashes are excluded. Positions are selected outcome-blind by SHA-256(FEN). Both arms use Stockfish 19, Berserk and Ethereal under the inherited P2 execution envelope.

The fresh discovery arm, not P2, selects the primary schema. Held-out profiles are generated separately from target packets, and target-blind scope is sealed before target opening.

## 6. Fresh schema selection

For each frozen primary schema family define

`K_s(r) = (F0(r), C_s(r))`.

A primary schema is discovery-admissible only when:
- ROOT_CHANGE collisions = 0;
- compression ≥ 0.15;
- at least 24 records lie in cells spanning at least two discovery positions;
- at least 12 records lie in cells spanning at least two engines;
- both target labels occur.

The support court requires at least:
- 96 fired records;
- 2 ROOT_CHANGE=true records;
- 24 ROOT_CHANGE=false records.

Selection is deterministic: minimum number of coordinates added beyond P2_BASE, then frozen family rank, then lexical schema ID.

The legacy-surface rivals are evaluated by the same fresh metrics but excluded from this selector.

## 7. Engine-conditional geometry

The same primary schema-family census is computed separately for each engine. Engine-specific fields are descriptive and cannot replace the cross-engine primary field.

If all three engine-specific fields transport prospectively while the cross-engine field fails, P3 may support an **engine-conditional field family with a cross-engine gluing obstruction**. Engine names remain comparison indices, not context coordinates.

## 8. Counterexample-guided diagnosis without rescue

`c3x-field-p3 diagnose` may open targets only after verification. It reports contradiction clusters and their engine/position/cell provenance. It cannot:
- modify a schema;
- promote a coordinate;
- alter a threshold;
- re-run primary selection.

Counterexamples are evidence for the *next* constitution, not an escape hatch for the current one.

## 9. Deterministic explanation-service API

P3 adds a deterministic service, not an LLM.

Endpoints:
- `GET /health`
- `POST /v1/query`
- `POST /v1/explain`
- `POST /v1/diagnose`

The service consumes the same profile and field schemas as the research court. Explanations are fixed-template/AST outputs grounded in certificate facts.

The service has two explicit abstention modes:
- `ABSTAIN_UNSEEN_CONTEXT` — a global field exists, but the requested cell was unseen;
- `ABSTAIN_NO_GLOBAL_FIELD` — fresh discovery licensed no global primary field.

No model weights, prompt model or external LLM are required. A future MCP, agent, skill, GUI or LLM narrator may wrap the deterministic service, but it cannot expand scientific authority or replace the certificate core.

## 10. Literature positioning

P3 treats prior work as constraints rather than as authority overrides.

- **Invariant prediction**: discovery-set fit is not transport authority; stability must survive environment change.
- **Pearl–Bareinboim transportability**: source/target differences must be explicit.
- **Duarte–Solus context-specific causal models**: context-indexed causal structure is a legitimate object rather than an embarrassment to a failed global law.
- **Lee–Yannakakis state identification**: discriminating response sequences motivate state refinement by observable experimental distinctions.
- **CEGAR**: counterexamples can guide the next bounded abstraction, but P3 adds a fresh-evidence firewall so the same counterexample cannot certify its own repair.
- **Sutter et al.**: context/representation capacity is part of the hypothesis; unrestricted rescue destroys falsifiability.
- **Yao et al.**: invariance is an identification constraint, not automatic causal semantics.
- **C3X P23–P26**: architecture and search budget already behaved as law indices under earlier intervention families.

## 11. Claim ceiling

A P3 PASS may establish transport of one frozen prefix-topology-aware ROOT_CHANGE field over the new source split and execution envelope. It does not establish:
- a unique true causal context;
- arbitrary-position or arbitrary-engine transport;
- raw TT-key identity as causal;
- architecture descriptors as causes;
- cognition, intent or human chess concepts.

Fresh success of a development-derived legacy rival is descriptive only. Abstention remains a boundary of authority, not non-causality.

## 12. Implementation principle

The research object and product object share one contract:

`instrumented engine → exact-event replay → F0 fiber → event-prefix context profile → frozen schema field → CERTIFIED / ABSTAIN / CONTRADICTED → deterministic explanation / diagnosis`.

P3 counts as engineering success only if an external user can reproduce this path from the released toolkit/service without a hidden notebook, model, prompt or manual adjudication.
