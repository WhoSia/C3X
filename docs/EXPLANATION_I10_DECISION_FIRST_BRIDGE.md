# C3X Explain I10-P0 — Decision-First Chess Judgment and Warrant-Bounded Commentary

**Formal research/implementation name:** Evidence-Grounded Chess Judgment & Contrastive Commentary: Typed Candidate Decisions, Causal–Semantic Warrant Boundaries, Human-Legible Contrast & Selective Abstention.

**2026-10-13: I10-P0 code and actual CI run #38331884555 verified (37 tests PASS but 0/4 original smoke judgments, 4/4 ABSTAIN); I10-P1 TWO independent-public-historic development cases actually executed with original SF16, CI #38332952446 40 tests PASS and 2/2 bounded judgments, ZERO original C3X causal certificates; details in [P1 native report](EXPLANATION_I10_P1_REAL_CHESS_RESULTS_AND_COMPARATOR_AUDIT.md). No empirical human benefit, trained neural decision model, Jev/Clef inference, actual Kim CCC competitor, or 0.26 science promotion.** User redirection: scientific semantic discoveries must demonstrate *why their distinction is needed* in an actual commentator/judgment system. Preserve RDRC as an engineering module, not the purpose of the C3X scientific mainline.

## Source genealogy (original academic PDFs first)

Original, inspected in user's Drive:
1. **Kim, Goh, Hwang, Cho & Ok**, `Bridging the Gap between Expert and Language Models: Concept-guided Chess Commentary Generation and Evaluation` (arXiv 2410.20811v2; NAACL 2025), [Drive original](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view). Their CCC maps expert concept information to language generation and reports human/model comparisons. This establishes a serious **concept+LLM baseline**; concept guidance is not original to C3X. Avoid using a generated fluent rationale as proof of original engine causation.
2. **Parfenova**, `Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness` (arXiv 2609.22245v1), [Drive original](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view). Her chess experiment separates explanation action-recoverability, correctness, and internal causal faithfulness; masking and random-comment controls are important. Directly motivates move-masking and unsupported-reason adversaries.
3. Related Drive originals: Ahdritz et al. (2024), `Distinguishing the Knowable from the Unknowable with Language Models` [Drive](https://drive.google.com/file/d/17Kpk3N1iT3HbKqdA1rBnHvibMaxyAgkT/view); Wen et al. (2025) abstention survey [Drive](https://drive.google.com/file/d/1BUnV_x1E0_OtyoeBOq5-_sL85ApCJH2j/view); these are donors, not novel C3X theorems.

Additional directly read Drive foundations (not Jev/Clef-origin papers):
- **Hendrickx, Perini, Van der Plas, Meert & Davis (2024), _Machine Learning with a Reject Option: A Survey_** (Machine Learning 113:3073–3110, DOI 10.1007/s10994-024-06534-x), [Drive original](https://drive.google.com/file/d/1vNRBOpmqlgZwEIqMZv3zXuWa02vLUETw/view). Distinguishes ambiguity vs novelty rejection and evaluates *risk vs coverage*; existing selective decision theory precedes Jev. In I10 an evidence-missing ABSTAIN is initially a **rule-based guard**, not a trained risk-optimal rejector.
- **Angelopoulos, Bates, Candès, Jordan & Lei (2025), _Learn Then Test: Calibrating Predictive Algorithms to Achieve Risk Control_** (Annals of Applied Statistics 19(2):1641–1662; DOI 10.1214/24-AOAS1998), [Drive original](https://drive.google.com/file/d/1OC0CSHbj6DeFNeNiop81QDUHc9pduzTy/view). Finite-sample risk control is based on calibration data and multiple testing, **not** on merely printing a confidence-looking decimal; I10 presently claims no risk guarantee or fitted threshold.

Three Jev-related decision-model papers **NOW VERIFIED BY DIRECT ORIGINAL-PDF FETCH** from user's Drive (2026-10-13), citation-name normalized and file IDs/bytes preserved in `10_PAPERS — Canonical Literature Commons`: **Tang & Zheng (2026)**, `Typed Decision Models: An Early Evidence Audit and Evaluation Checklist` [Drive arXiv 2609.32160v1](https://drive.google.com/file/d/13cg7JKtrPH0K3j6QgTuIaA3d2Zitz5WV/view) (28-paper early review, no automatic TDM accuracy superiority); **Deußer, Sparrenberg & Sifa (2026)**, `Evaluating and Benchmarking the System One Model Jev` [Drive arXiv 2609.37647v1](https://drive.google.com/file/d/1nyhsNdWIb2IBp8aX1jSUZzWpHWgCtoCK/view) (37 datasets, 346,009 real Jev 1.13.0 requests, calibration/accuracy contingent on task and baseline); **Gao & Wang (2026)**, `OpenJev-RLCD: A Working RLCD Implementation` [Drive arXiv 2609.38850v1](https://drive.google.com/file/d/1FIO-xUrgBYbcgy9FbPalf14zsGKz6Y-P/view) (per-rationale strictly proper scoring vs mixture variance bonus; calibrate then reinforce, independent validation in C3X NOT done). **Cloudflare Clef** [official Oct 1 2026 developer post](https://blog.cloudflare.com/clef-decision-models/): typed schema choice and score heads, frozen Qwen backbones + LoRA, label-smoothed CE/Brier/RLCD claimed by vendor. No verified peer-reviewed first-party technical paper equivalent to the blog. Jev TypeSafe closed weights: no assumption of exact internal mechanism. A typed output is *not* automatically more accurate, calibrated, or faithful. Code below does NOT claim to recreate those models.

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

## Runnable opt-in I10 evidence-judgment example

Existing I9 default remains unchanged; supplying the new flags also writes a separate typed judgment:

```bash
python -m c3x_explain --pgn local-authorized-game.pgn \
  --engine /path/to/verified-stockfish --disable-nnue \
  --nodes 5000 --multipv 3 \
  --json-out explanation.json --markdown-out explanation.md \
  --judgment-out decision.json --judgment-markdown decision.md
```

At a verified nonterminal legal position, the opt-in layer can report e.g. *engine prefers candidate A over candidate B by an observed cp gap*, together with legacy atom IDs and **actual legally replayed SAN continuations for each candidate** when the source PVs exist. It reports whether the first opponent reply appears in each source candidate PV; this **does not** establish an inevitable refutation or a true chess value bound. If the actual played move is NOT one of the two comparable candidates, the decision-first layer abstains rather than replacing the user's question with a discussion of two OTHER top moves. If there is no comparable second candidate, no exact cp, unequal depth, bound-only score, invalid source PV, failed legal/provenance check, or missing certificate, the corresponding claim is withheld. A missing response line is never filled by the LLM.

No independent native I10 CI results are asserted until the GitHub workflow and derived JSON are actually read back. No new content from an LLM may be released as a verified causal claim without a separate sentence-level attribution verifier. A trained neural typed-choice model and its probabilities are later implementation experiments, not already present in the I10-P0 code.

## Falsifiable evaluation protocol — no model-calibration promises

Before any held-out labels, freeze game-disjoint nonterminal positions, candidate pair and search budgets. Baselines: original I9 commentary; Kim-style concept-guided LLM; Stockfish-root-score-only; same language model without C3X certificate; C3X with valid certificate vs randomized/mismatched/revoked certificate. All prompts, labels and response lengths presealed. Independent annotators rate tactical correctness, move/alternative causal specificity, unsupported facts, action recoverability *after move-name masking*, and whether they can select the best reply in a NEW situation. Separately report coverage vs risk, abstentions, class balance and calibration **only if a real probabilistic model is trained and independently calibrated**. Explicit null hypothesis: C3X added source semantics produces no measurable benefit over strong donor baseline. Human I8 closed protocol remains HOLD until real participants; do not simulate fake annotators.

## Release limits

I10-P0 may show *usable typed decisions*, not trained neural judgment, calibrated confidence, human utility, better chess play or upgraded G10 causal science. The original I9 authority firewall remains the sole renderer. RDRC P14-P10-P2 remains engineering/industrial optimization, unrelated to explaining the chess choice unless a specific intervention proves the linkage. Keep **WhoSia-only authors and committers**, `permissions: contents: read` on Actions, no bot writeback; store minimal artifacts with no third-party PGN or binary redistribution.
