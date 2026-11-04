# C3X 0.29-P31/R2 — Output-Stable Search-Trace Changes: Partial Identification from Archived Native Data

Date 2026-11-04. **This is a derived numerical implication of a historical Stockfish16 experiment plus primary-source reading, not a fresh native execution.**

## Source reading, versions and custody

Qin, Wang, Wang, Wei & Shen (2026), *Evaluating and Explaining Prompt Sensitivity of LLMs Using Interactions*, Proceedings of the 43rd ICML, PMLR 306. Abstract: coarse output consistency may coexist with changed internal interactions; interaction-based prompt sensitivity (IPS) examined 50 open-source LLMs, discussing influence of supervised finetuning, model size, architecture and few-shot examples. This is **LLM prompt research**, not empirical evidence about Stockfish's TT, root-search causal mediators or chess concept novelty.

Newly acquired published PDF in 00_INTAKE:
- Published ICML PMLR PDF ID: 1Z8c292JoDteom1HRYPP7N6meV6ENAe77, raw SHA256 3110dc69405cd209bf2668d6c551afc069410e3164012efb8d12802562b08f3d, 46 pages, 8,245,543 bytes.
- Existing arXiv v1 preprint ID: 1HK-iuEjv7Hv6qBaDN3xf5uDnBoXqPle1, SHA256 b04432a6f14597a720f62eb294cc63ab40acced13e5d98a8942f77947e5d17cc, 46 pages, 8,206,204 bytes.
- Compared extracted text page by page. **One page differs (PDF page 1): arXiv v1 first-page identifier only**. Hence NOT an identical byte duplicate; largely same scientific text, distinct version provenance.
- Promoted published paper unchanged-ID to canonical **10_PAPERS** and normalized name `Qin et al. (2026) — Evaluating and Explaining Prompt Sensitivity of LLMs Using Interactions — ICML PMLR 306.pdf`. Moved existing arXiv edition to **90_SOURCE_VERSIONS** under its preserved preprint name, retaining its original ID and bytes, verifying both destinations via Drive metadata. No deletion.

## Sharp bound from original C3X source result

Public original **archival** native root-order experiment receipt `c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json` reports:
- n=12 source-position development roots; categorical bestmove changed=2, therefore unchanged=10;
- PV changed=10;
- nodes changed=11;
- score_or_bound changed=8.

Without **case-level cross-tabulations**, the Fréchet intersection bounds for events A and B over n fixed units are
`max(0, |A|+|B|-n) <= |A ∩ B| <= min(|A|,|B|)`.
Taking A="bestmove unchanged", this entails these *sharp count intervals*:

| Trace property changed while final bestmove unchanged | Lower bound | Upper bound |
|---|---:|---:|
| PV changed | 8 | 10 |
| Node count changed | 9 | 10 |
| Score or bound changed | 6 | 8 |

The lower bounds are **logically entailed by archive aggregate counts**; actual joint cross-tab counts may be higher and are not reconstructed here. These categories overlap; do not add counts or claim independence. Root order was manipulated within original source study; no new chess engine execution or independent prospective data here. Same bestmove + different search traces does **NOT identify which trace change caused the choice**, nor imply any strategic Q changed.

## New code

- `tools/c3x_029_p31_native_trace_overlap_bounds.py` loads the original receipt file and computes sharp intersection count bounds, validating integer types and upper/lower constraints.
- `tools/test_c3x_029_p31_native_trace_overlap_bounds.py` checks exact source receipt, algebraic boundaries and invalid data. Registered for actual GitHub Actions execution in `.github/workflows/c3x-029-p9-public-receipt-regression.yml`.

## Scientific use

This brings concrete historical Stockfish evidence to the question generated after reading Sloman (2005), Halpern (2016), Pearl (2009), and Qin et al. (2026): **Do final-choice-invariant interventions imply stable causal explanations?** No: stable observed outputs do not even imply stable traces. But merely finding changed traces does not identify explanations; for a specific plan-value claim require a causal intervention and independent strategy-value factual verification. A subsequent mechanistic study needs case-resolved TT/writer/reply/score traces, not just binary summaries.

## Next action

Recover the full case-level archived root-order logs where available; compute exact paired cross-tabs rather than bounds. Then formulate a source-anchored negative and positive control with genuine Q policy, not automatically transfer LLM IPS concepts to chess engines. For a new performance claim, acquire new complete original game histories and game-independent heldout.

## Authenticated remote CI result (2026-11-04)
- GitHub Actions run [41767455345](https://github.com/WhoSia/C3X/actions/runs/41767455345), head SHA 5945b023da3b3c878ec72a2b9c10c66ec524b192: status **completed**, conclusion **success**. Authenticated run jobs show specifically `P31 original native archive trace-overlap bounds` step **success**, with P29 and P30 regression steps likewise success. This verifies parsing of the original public 0.17 archived receipt and formal six-case tests, NOT new Stockfish process execution or causal identification.
