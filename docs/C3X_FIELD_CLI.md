# C3X Context-Indexed Causal Field CLI

## What this tool is

`c3x-field` is the executable surface of C3X G9.5. It does not predict chess moves and it does not infer a universal engine mechanism. It answers a narrower question:

> Given an exact TT-use event's frozen intervention-response fiber and a prospectively measured pre-intervention context, is the event's ROOT_CHANGE explanation licensed by a field discovered on prior intervention evidence?

The tool keeps three states distinct:

- **CERTIFIED_ROOT_CHANGE / CERTIFIED_NO_ROOT_CHANGE** — the profile lands in a previously discovered context-indexed fiber cell.
- **ABSTAIN_UNSEEN_CONTEXT** — the profile is outside the demonstrated field.
- **CONTRADICTED_CONTEXT_CELL** — held-out intervention evidence falsifies the cell's transported label.

Abstention is not evidence of non-causality.

## Stable commands

### Discover a field

```bash
c3x-field discover \
  --constitution constitution.json \
  --input discovery-input.json \
  --out field.json
```

The discovery packet contains exact-event F0 fibers, frozen context profiles, and ROOT_CHANGE labels from an authorized discovery intervention set. The command enumerates the prospectively frozen portable basis family and emits all minimum-cardinality admissible bases.

### Scope a field without targets

```bash
c3x-field scope \
  --discovery field.json \
  --profiles heldout-profiles.json \
  --out scope.json
```

Held-out profiles contain **no ROOT_CHANGE or counterfactual move/score/WDL/PV fields**. Among already-minimal discovery bases, scope selection uses only target-blind coverage.

### Verify after target opening

```bash
c3x-field verify \
  --scope scope.json \
  --targets heldout-targets.json \
  --out verification.json
```

This opens the sealed held-out target packet only after scope selection. Covered contradictions falsify transport; unseen cells remain abstentions.

### Query a particular discovered basis

```bash
c3x-field query \
  --discovery field.json \
  --basis 'P:parent_qshare_bucket+event_depth_bucket' \
  --profiles new-profiles.json \
  --out query.json
```

The basis ID must be one of the discovery-minimal portable bases.

## Chess-aware profile front end

`tools/c3x-context.py` materializes the frozen pre-intervention profile from:

- FEN;
- unablated parent semantic receipt;
- unablated P32 semantic-use trace;
- exact event ID and F0 fiber;
- source-grounded architecture descriptor.

It must be run **before** opening the singleton intervention target result.

## Context constitution

Primary portable coordinates are grouped into:

- board geometry;
- parent-search state;
- event-local TT-use state.

Engine name, FEN, position hash, full key, exact address, ROOT_CHANGE, counterfactual semantics, learned embeddings, and post-outcome thresholds are forbidden as primary context coordinates.

Architecture descriptors exist only as a secondary diagnostic lane. They cannot rescue a failed portable field into a primary transport PASS.

## Packet boundary

The G9.5-P2 workflow physically separates held-out evidence into:

1. **profile artifacts** — F0 + pre-intervention context only;
2. **target artifacts** — ROOT_CHANGE and counterfactual root/PV facts.

The scope job does not download target artifacts. This is an execution firewall, not a prose promise.

## Scientific authority

A field certificate is conditional on the frozen:

- engine source commits;
- opening-book source and selected positions;
- TT history procedure;
- Threads=1 / Hash=1 MiB;
- 20k prime + 3×20k decoy history;
- 80k-node measurement search;
- exact-event intervention semantics;
- ROOT_CHANGE query.

Do not reinterpret a certificate as a universal event ontology, chess-strategy explanation, cognition claim, or prevalence estimate.
