# C3X Explanation Implementation I2 — Verified Tactical Evidence, Candidate-Contrast Routing & Graph Quality Packets

## Status

**CLOSED / PASS — IMPLEMENTATION AUTHORITY ONLY.**

Canonical implementation CI:
- workflow: `c3x-explanation-implementation`
- run: `36675851772`
- head: `f4fd05d2ae9c7c1cd08ec14b0da3d7333b62e1d8`
- unit: PASS
- pinned Stockfish smoke: PASS

## What I2 adds

I2 moves conventional commentary from generic engine prose toward a verifier-first chess evidence compiler.

### Verified tactical evidence

`c3x_explain/tactics.py` derives only board-verifiable properties:
- capture;
- castling;
- promotion;
- check;
- checkmate;
- moved-piece multi-attack against at least two valuable enemy pieces / king;
- newly created absolute pin to the enemy king.

Labels are deliberately narrower than informal tactical storytelling. For example, a verified `multi_attack` is not silently renamed a fork unless a later adapter earns that stronger semantic label.

### Candidate tactical contrast

For played move vs engine top alternative, I2 computes:
- tactical evidence for each move;
- shared tactical properties;
- played-only tactical properties;
- alternative-only tactical properties.

This creates an explicit contrast packet before prose generation.

### Commentary category routing

Each selected moment now carries a typed commentary plan assembled from evidence atoms:
- `causal_contrast`;
- `tactics`;
- `comparison`;
- `positional_proxy`;
- `material_context`.

The category router is downstream of evidence. It does not infer unsupported plans or motives.

### Graph quality packet

Every output graph reports:
- atom count;
- causal vs heuristic atom counts;
- provenance coverage;
- atom-ID traceability coverage;
- failed-firewall moment count;
- category coverage.

This separates generation quality from evidence integrity.

## Literature synthesis

I2 borrows engineering ideas without importing scientific authority:
- Jhamtani et al. 2018: pragmatic move-commentary context;
- Zang et al. 2019: commentary-category routing;
- Kim et al. 2025: expert/concept to language bridge;
- Wang et al. 2025 MATE: strategy/tactic candidate supervision;
- ChessQA 2025: multi-axis chess understanding evaluation;
- Tang et al. 2026: expert-to-language grounding;
- Dionisopoulos et al. 2026 and Parfenova 2026: move quality, fluency and reasoning faithfulness must be evaluated separately.

## Authority firewall

All I2 tactical and concept atoms remain `CONVENTIONAL_HEURISTIC_COMMENTARY` unless a specific C3X causal certificate is attached.

A verified checkmate, pin or multi-attack is a chess fact. It does **not** establish that the fact caused an engine preference.

Only `C3X_CAUSAL_CONTRAST` permits causal engine-decision wording.

## Next

I3 should add:
1. license/source-bearing commentary retrieval;
2. similar-position / motif retrieval packets;
3. retrieval-to-evidence-graph merging without authority escalation;
4. benchmark packets separated by Structural / Motif / Tactic / Position-Judgment / Semantic axes;
5. human-utility evaluation by rating band.
