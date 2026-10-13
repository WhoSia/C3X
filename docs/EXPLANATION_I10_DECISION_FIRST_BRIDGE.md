# C3X Explain I10-P0 — Decision-First Chess Judgment and Warrant-Bounded Commentary

**Formal research/implementation name:** Evidence-Grounded Chess Judgment & Contrastive Commentary: Typed Candidate Decisions, Causal–Semantic Warrant Boundaries, Human-Legible Contrast & Selective Abstention.

**2026-10-13: DESIGN + IMPLEMENTATION PILOT; no empirical human benefit, no trained neural decision model, no Jev/Clef API call, no 0.26 science promotion.** User redirection: scientific semantic discoveries must demonstrate *why their distinction is needed* in an actual commentator/judgment system. Preserve RDRC as an engineering module, not the purpose of the C3X scientific mainline.

## Source genealogy (original academic PDFs first)

Original, inspected in user's Drive:
1. **Kim, Goh, Hwang, Cho & Ok**, `Bridging the Gap between Expert and Language Models: Concept-guided Chess Commentary Generation and Evaluation` (arXiv 2410.20811v2; NAACL 2025), [Drive original](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view). Their CCC maps expert concept information to language generation and reports human/model comparisons. This establishes a serious **concept+LLM baseline**; concept guidance is not original to C3X. Avoid using a generated fluent rationale as proof of original engine causation.
2. **Parfenova**, `Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness` (arXiv 2609.22245v1), [Drive original](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view). Her chess experiment separates explanation action-recoverability, correctness, and internal causal faithfulness; masking and random-comment controls are important. Directly motivates move-masking and unsupported-reason adversaries.
3. Related Drive originals: Ahdritz et al. (2024), `Distinguishing the Knowable from the Unknowable with Language Models` [Drive](https://drive.google.com/file/d/17Kpk3N1iT3HbKqdA1rBnHvibMaxyAgkT/view); Wen et al. (2025) abstention survey [Drive](https://drive.google.com/file/d/1BUnV_x1E0_OtyoeBOq5-_sL85ApCJH2j/view); these are donors, not novel C3X theorems.

New 2026 typed decision model works **Drive not found (indexed title/ID search only)**, so online verified, not claimed read as Drive original: `Typed Decision Models: An Early Evidence Audit and Evaluation Checklist` [arXiv 2609.32160](https://arxiv.org/abs/2609.32160), `Evaluating and Benchmarking the System One Model Jev` [arXiv 2609.37647](https://arxiv.org/abs/2609.37647), `OpenJev-RLCD: A Working RLCD Implementation` [arXiv 2609.38850](https://arxiv.org/abs/2609.38850). **Cloudflare Clef** [official Oct 1 2026 developer post](https://blog.cloudflare.com/clef-decision-models/): typed schema choice and score heads, frozen Qwen backbones + LoRA, label-smoothed CE/Brier/RLCD claimed by vendor. No verified peer-reviewed first-party technical paper equivalent to the blog. Jev TypeSafe closed weights: no assumption of exact internal mechanism. A typed output is *not* automatically more accurate, calibrated, or faithful. Code below does NOT claim to recreate those models.

## Concrete original-science question

For a nonterminal, genuinely competitive chess choice between two legal moves, does evidence-typed engine preference plus independently admitted C3X causal source evidence yield a better explanation of **why A rather than B** than (a) generic Stockfish+LLM commentary or (b) concept-guided CCC? Distinguish:
- **Physical execution / descriptive preference**: actual source move ranking at this stated evaluation budget.
- **Board-grounded tactical / strategic concepts**: useful interpretation, neither source causation nor proven strategic necessity.
- **Locally evidenced C3X intervention**: only exact admitted certificate and enabled authority route, never automatically objective chess best move.
- **Uncertainty / coverage**: lack of a second comparable legal candidate, truncated PV, inconsistent depth, mate-score ambiguity, failed firewall, unknown provenance -> abstain, not hallucinate.
- **Ground truth**: independent high-budget reference, optionally independent different-engine & human chess annotators, neither generated explanation nor low-depth Stockfish ranking treated as absolute ground truth.

## I10-P0 initial operational kernel and test intent

Run existing `c3x_explain` I9 PGN pipeline **without altering any historical explanation atom**. A new postprocessed `c3x_explain/judgment.py` returns *typed* `engine_snapshot_preference`, rival, candidate evidence/trace IDs, visible authorization ceilings, and `ABSTAIN_*` reason. It accepts only two distinct candidates with comparable completed depth, finite ordinary cp and validated I9 firewall / realization; decline to manufacture calibrated probabilities or claims of objective best play. A candidate score comparison **is not** a causal explanation. If an original C3X certificate exists, link its atom/provenance only where the original I9 graph independently admits it; do not raise its authority.

Add CLI opt-in `--judgment-out` JSON for this judgment packet and `--judgment-markdown` for a constrained standalone **judgment-first decision note**. Existing default PGN JSON/Markdown output and verified I9 renderer stay backward-compatible. No automatic LLM inference, vendor key, telemetry, new GP corpora, or claim that free-form text has passed existing I7 firewall. External LLM realization may be designed only as a later strictly governed service.

## Falsifiable evaluation protocol — no model-calibration promises

Before any held-out labels, freeze game-disjoint nonterminal positions, candidate pair and search budgets. Baselines: original I9 commentary; Kim-style concept-guided LLM; Stockfish-root-score-only; same language model without C3X certificate; C3X with valid certificate vs randomized/mismatched/revoked certificate. All prompts, labels and response lengths presealed. Independent annotators rate tactical correctness, move/alternative causal specificity, unsupported facts, action recoverability *after move-name masking*, and whether they can select the best reply in a NEW situation. Separately report coverage vs risk, abstentions, class balance and calibration **only if a real probabilistic model is trained and independently calibrated**. Explicit null hypothesis: C3X added source semantics produces no measurable benefit over strong donor baseline. Human I8 closed protocol remains HOLD until real participants; do not simulate fake annotators.

## Release limits

I10-P0 may show *usable typed decisions*, not trained neural judgment, calibrated confidence, human utility, better chess play or upgraded G10 causal science. The original I9 authority firewall remains the sole renderer. RDRC P14-P10-P2 remains engineering/industrial optimization, unrelated to explaining the chess choice unless a specific intervention proves the linkage. Keep **WhoSia-only authors and committers**, `permissions: contents: read` on Actions, no bot writeback; store minimal artifacts with no third-party PGN or binary redistribution.
