# C3X Explain I9 — Transparent Admissibility-Aware Commentator

**Track:** Explanation Implementation  
**Authority:** implementation-only; cannot strengthen Track A science

## Goal

I9 turns the existing explanation stack into a directly usable commentator while exposing P17-style intervention-admissibility reasoning without hiding it behind a model score.

Pipeline:

`PGN → legal replay → MultiPV candidate evidence → verified tactics / board proxies → transparent intervention admissibility or abstention → optional C3X certificate → typed evidence graph → bounded realization → JSON + Markdown commentary`

## New evidence type

`intervention_admissibility`

- provenance: `CONVENTIONAL_HEURISTIC_COMMENTARY`
- authority: `c3x_transparent_preoutcome_susceptibility`
- carries:
  - ADMIT / ABSTAIN;
  - transparent family id;
  - exact score/rule/table trace;
  - feature values;
  - abstention reason;
  - explicit authority ceiling.

It never becomes `C3X_CAUSAL_CONTRAST`.

## CLI

```bash
python -m c3x_explain \
  --pgn game.pgn \
  --engine /path/to/uci-engine \
  --rating-band advanced \
  --susceptibility p17-packets.json \
  --certificate local-certificate.json \
  --json-out commentary.json \
  --markdown-out commentary.md
```

The engine, susceptibility packet, and certificate inputs are optional except for the PGN and JSON output. Without a susceptibility packet, the existing commentary behavior is unchanged.

## Black-box rule

The commentator may render a transparent P17 decision trace. It may not silently replace that trace with:
- a neural classifier;
- an LLM judgment;
- an opaque ensemble;
- a post-hoc surrogate.

Free-form LLM generation is not required for I9. The bounded renderer remains the authority surface.

## Human-utility boundary

I9 makes the commentator more inspectable and usable. It does not resolve the existing Explain-I8 human-utility HOLD.
