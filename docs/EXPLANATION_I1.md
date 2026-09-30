# C3X Explanation Implementation I1 — Concept Proxy, Rating-Band Salience & Renderer Contract

I1 moves the implementation track from a generic evidence spine toward an actual teaching/commentary system without allowing the language layer to become an authority source.

## Conservative chess concept layer

The current adapters deliberately expose **exact board-derived proxies** rather than unearned semantic labels:

- center-control count;
- center occupancy count;
- minor pieces remaining on home squares;
- doubled-pawn file count;
- isolated-pawn count;
- passed-pawn count;
- king-shield pawn proxy;
- open-file count.

For a played move and the engine's top alternative, I1 computes the snapshot after each move and emits only non-zero played-minus-alternative deltas.

A delta such as `own_center_control_count +1` is a board fact. It is **not** automatically a statement that central control caused the preference.

## Rating-band salience

| Band | Default threshold |
|---|---:|
| beginner | 80 cp |
| intermediate | 50 cp |
| advanced | 25 cp |
| expert | 15 cp |

Forcing/irreversible verified facts and available C3X causal certificates remain eligible regardless of rating band.

The band changes *what deserves explanation*, not the underlying engine evidence.

## Renderer boundary

`c3x/ontology/explanation-renderer-contract-v1.json` defines the contract for any future LLM/NLG renderer.

The renderer:
1. sees the typed explanation graph, not unrestricted engine internals;
2. maps substantive prose back to evidence atoms;
3. may use causal wording only for `C3X_CAUSAL_CONTRAST`;
4. must preserve move identity, evaluation direction, uncertainty and provenance;
5. must abstain rather than fill evidence gaps.

This design directly implements the Track-B faithfulness boundary: fluent language is downstream of evidence.

## Authority

I1 remains implementation-only. Board proxies, engine rankings and natural-language usefulness do not alter any Track-A scientific verdict.
