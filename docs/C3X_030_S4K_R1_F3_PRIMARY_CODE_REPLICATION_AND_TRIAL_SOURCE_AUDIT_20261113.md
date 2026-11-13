# C3X 0.30 — S4-K/R1 & F3: Genuine Go-Epoch Causal Instrumentation and Primary-Code Prior-Art Synthesis

Date: 2026-11-13 KST. Conversation C3X 33, retained research version **0.30**. Provenance and claims are scoped. This file describes **executed native experiments** separately from **synthetic evaluation contract tests**.

## 1. Scientific state inherited and reverified

[S4-J original native CI #43354844857](https://github.com/WhoSia/C3X/actions/runs/43354844857): 48 real Stockfish16 searches, 576,619 nodes; 41 and 44 bounded target-ply1 TT early-cutoff log events in Sham / two-hit masking respectively; 25 shared **candidate** state fingerprints, 21 unique candidates and zero changed values among those 21. This does not prove mediator invariance: the source-site events were capped at 8 **per two-search process**, not per UCI go. Original binary, sham and zero controls from earlier runs had agreed; S4-J negative-control check passed. Independent [S4-J/R1 original-archive audit](https://github.com/WhoSia/C3X/actions/runs/43355260989) confirmed the original raw SHA and counts.

## 2. S4-K real-native source patch and execution

At exact original Stockfish16 source SHA (upstream commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`), the source-anchored modification now increments an epoch counter **at `MainThread::search()` entry corresponding to each UCI `go`**, resets the TT cutoff log ordinal for the new epoch, and records:
- `GO_BEGIN epoch=N cap_per_go=8`;
- each bounded actual source `return ttValue` at the frozen target key, with epoch, invocation ID/parent, TT key, search depth, alpha/beta, PV flag, cut-node flag, and returned score;
- `GO_END epoch=N source_cutoff_total=...`, using a count that **continues past 8**.

The source instrumentation does not change Stockfish TT state, alpha/beta windows or return values. Genuine native original-vs-same-binary sham checks check bestmove/depth/nodes/score/PV equality and fail closed; they are evidence of no observed outcome drift, not a mathematical proof of universal instrumentation noninterference. Two consecutive searches within each process keep warm TT state as the **original frozen experiment design** specified.

[S4-K actual native run #43357379268](https://github.com/WhoSia/C3X/actions/runs/43357379268) PASS: **48 fresh native searches, 576,619 actual search nodes, 9 synthetic contract tests PASS**, eight previously used *development* FENs from 4 researcher-authored legal-game histories, true upstream original / sham / two-hit mask conditions, two search trials per arm. No holdout positions evaluated.

Immutable original source result JSON SHA256: `0beb46fa6188563cc8259933af70fa091154732ecda3f3d6a1bbc0cab281449c`. [S4-K native raw original ZIP in Drive](https://drive.google.com/file/d/1xzgc7N3g8bbqlo16m322qdWzdFCd5hcV/view).

| Observable category | S4-J old per-process-cap logs | S4-K epoch-tagged and independently counted |
| --- | ---: | ---: |
| Sham TT target-key early cutoffs | 41 logged | **45 logged / 45 total at this source site** |
| Two-hit TT target-key early cutoffs | 44 logged | **48 logged / 48 total at this source site** |
| State fingerprints shared by Sham and two | 25 | **27** |
| Unique-in-both candidate state fingerprints | 21 | **24** |
| Ambiguous/repeated state fingerprints | 4 | **3** |
| Changed return among unique candidates | 0 | **0** |
| Root-bestmove change in two-hit vs Sham | 3/16 | **3/16** |

The S4-K 45/48 counts are *complete for this targeted ply-one TT early-cutoff return site in these runs only*, because source totals and recorded receipt counts are equal. The instrument does **not** capture all returns, all TT events, whole search trees, quiescence search or root-ancestor cross-run value mediation.

Trial-aware root-change locations: Italian ply10 changed in both trials, London ply8 in one trial. Neither had any unique matching TT early-cutoff candidate in S4-K (0/0). The changed root move may reflect distinct explored path, unobserved computation or different warmed TT state; the present dataset cannot identify the single causal intermediary.

## 3. Independent immutable source audit

[S4-K/R1 independently archived re-audit #43357888184](https://github.com/WhoSia/C3X/actions/runs/43357888184) PASS, **0 new searches**, six synthetic mutation-contract tests PASS. It downloaded the separate earlier S4-K original GitHub Actions artifact, enforced the precise original JSON SHA, recomputed every epoch's source totals, receipt ordinals, cross-arm candidate alignment, root-choice differences and aggregate statistics.

Reproduced: Sham 45/45; two 48/48; 27 common candidates, 24 uniquely matched candidates, 3 repeated ambiguities, zero unique-candidate value change, 3/16 root-choice changes. Report native-audit JSON SHA256 `916d4db22e4229e648d8819207cebe96cebf3f228c02ac2905217c68d99aa607`.

**Scientific verdict:** `PASS_SOURCE_SITE_AND_TRIAL_REAUDIT_ONLY`; **HOLD** full TT causal mediation, unseen game results, population generalization, explanation comparison, response-robust planning and the original 0.29 7/8 prospective cohort.

## 4. Primary papers and real source repositories reviewed

This round reviewed **actual public README/source/method files**, not merely secondary summaries. Exact DOI/publication versions and original PDF custody in the existing Drive were checked by title. A Drive file listing proves title-level custody; it is not a new full-text critical reading or authors' code-runtime reproduction.

| Source | Actual public implementation / original PDF custody | What C3X can learn | Critical non-equivalence |
| --- | --- | --- | --- |
| Puri et al., *Explain Your Move*, ICLR 2020, SARFA | [Original code `nikaashpuri/sarfa-saliency`](https://github.com/nikaashpuri/sarfa-saliency), `sarfa_saliency.py` examined; [owned original PDF](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view) | Specificity versus relevance (selected-action probability change, non-selected-action KL suppression), original-action contrast | SARFA saliency is not full native Stockfish TT-mediated source causality. Reference code uses direct exponentiation of Q-values; numerical stability, action-support matching and legal chess perturbation merit explicit checks. |
| Fritz & Fürnkranz 2021 chess-specific saliency improvements | [Publisher paper](https://ieee-cog.org/2021/assets/papers/paper_180.pdf), [owned original PDF](https://drive.google.com/file/d/13orvM8vIILK80Uq9GlPC9QjHC0FD4BIe/view) | Pins, rays, empty squares and chess semantic constraints should be evaluated as explanation failures; not just piece heatmaps | Perturbation saliency and changing engine root decisions measure different outcomes. Code reproduction not claimed in this round. |
| Press & Golubev, *Explaining Chess and Go in Natural Language*, arXiv:2610.23166v1 (Oct 2026), BinProp | [Author code `oripress/BinProp`](https://github.com/oripress/BinProp); `README.md`, `docs/method.md`, `docs/formats.md` directly read; [owned original PDF](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view) | Executable Boolean motifs; support fit `min(P(motif|positive), P(no motif|negative))`; hard nearby negatives; published heldout metric `min(positive_true, negative_false, nearby_negative_false)`; discovery and evaluation separation | Nearby negatives test a predicate's generalization; they do **not** establish internal source-level mediation. Its within-episode continuation-based heldout is not automatically independent games. Running generated motif code requires a real sandbox; no untrusted code executed here. |
| Spinnato 2025, *Towards Piece-by-Piece Explanations ... with SHAP* | [Author code `fspinna/chessplainer`](https://github.com/fspinna/chessplainer) README examined, [owned original PDF](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view) | Define per-piece local evaluation attribution, expensive coalition ablations; control the background, WDL transformation and node budget | Value attribution is not an explanation of *which move* Stockfish selected; removing pieces is not necessarily a legal continuation. |
| Hammersborg & Strümke 2024, Scientific Reports | [Article DOI](https://doi.org/10.1038/s41598-024-70701-2), [owned original PDF](https://drive.google.com/file/d/1unfOjjuXqlVwxzMHdtn_vq8MDSJBkFSN/view) | Strict information-flow identification for discrete board models as a demanding comparator | Their guarantee applies within the specific neural model information-flow intervention, not to Stockfish alpha-beta/TT whole decision source. |
| DeepMind *Amortized Planning with Large-Scale Transformers*, NeurIPS 2024 | [Author code `google-deepmind/searchless_chess`](https://github.com/google-deepmind/searchless_chess) README/source structure inspected | Explicit action-value, state-value and imitation targets; game-split and rank-correlation baselines | Distilled move quality and searchless policy do not prove explanatory faithfulness or native computation identity. |

## 5. Paper-aligned F3 Boolean concept comparator (IMPLEMENTED, not empirically benchmarked)

Added `harness/c3x_030_f3_binprop_comparator_contract.py`, `test_c3x_030_f3_binprop_comparator_contract.py` and a pinned python-chess GitHub CI workflow.

- Supports the documented BinProp episode pool sizes: 4 positive/4 negative support examples and 8 positive/8 negative/8 nearby-negative heldout examples. Checks that FENs are valid and board identities are not duplicated.
- Ranks positive-delta BinProp concepts by **support fit × discovery delta**, with published fit threshold 0.5 and deterministic fallback if no motif qualifies.
- Scores each selected Boolean concept by **minimum** of heldout positive true rate, negative false rate, and nearby-negative false rate; averages up to 3 concept scores.
- Treats Direct's published ranking policy as a separately frozen list, not a BinProp discovery delta requirement. C3X Boolean concepts are optional candidates, **not native TT event explanations**.
- Refuses to interpret numerical SARFA saliency, SHAP attributions or TT receipts as binary motif predictions. No new gameplay data, chess engine, LLM, external human judge or independent heldout labels are generated by this code.
- The flag `labels_are_external` is a *self-assertion* pending a separate independently audited SHA evidence chain; it is not proof that external labels actually exist or are independent.
- A paper's within-episode heldout continuation positions, even when positions differ, need not be *game-disjoint*. Avoid inflating paper replication into prospective population validity.

[F3 synthetic contract CI #43358343484](https://github.com/WhoSia/C3X/actions/runs/43358343484) **SUCCESS**. All evaluated inputs in the tests were generated synthetic legal chess positions. **Zero F3 empirical head-to-head comparisons and zero evidence of C3X superiority**.

## 6. Why this changes our next work

C3X now has three separate claim types that must not be conflated:

1. **Source-search causal path:** native TT hit treatment, actual physical mask, source return, parent/root event and cross-arm move choice; requires source-aligned counterfactual evidence (S4-L next).
2. **Executable concept validity:** predicates with heldout positives/negatives and nearby-negative contrast, as in BinProp; requires independent engine-labeled real positions and source provenance.
3. **Evaluation-attribution salience:** SARFA move choice and SHAP position value are distinct metrics; they require their original implementations and their own fidelity and human-evaluation baselines.

Proposed S4-L: target affected root branch across two truly tagged UCI trials, add explicit parent-return reason and qsearch boundary, measure unknown coverage, and preserve original/sham/trial counts. Then test whether an identified source path contributes additional information **beyond** a BinProp Boolean motif or SARFA feature map on the same independently sealed new game. No winner is declared unless that prospective paired test actually runs.

## 7. Evidence acceptance

PASS: archived S4-K source-site complete cutoff counts, per-go epochs, independent original SHA audit, real Stockfish controls.

IMPLEMENTED/SYNTHETIC ONLY: F3 exact Boolean motif episode and nearby-negative evaluation contract.

HOLD: full causal root mediation, 8-game S4-H2 unopened holdout, prior 0.29 7/8 missing-game gate, real F3 independent labels, human pedagogical outcomes, any claim of being better than another paper.

All source commits by WhoSia; GitHub Actions never writes repository commits.


## 8. Final verified archive custody and still-missing exact originals

- [S4-K/R1 separate source-byte audit ZIP (Drive)](https://drive.google.com/file/d/1jDGqKe9vCiQ-ZqnuFBb1X6aB9T5aUA8Y/view) preserves a successful 0-new-search SHA-pinned re-audit.
- [F3 Boolean motif contract CI ZIP (Drive)](https://drive.google.com/file/d/1N3MuayynxFz6m-L40EdeSxtm-1FZPJQc/view) preserves synthetic test source SHA and the explicit no-empirical-head-to-head statement. [F3 CI #43358343484](https://github.com/WhoSia/C3X/actions/runs/43358343484) completed SUCCESS with **10/10 tests**.
- [S4-K 48-search raw ZIP (Drive)](https://drive.google.com/file/d/1xzgc7N3g8bbqlo16m322qdWzdFCd5hcV/view) remains the original immutable evidence, not overwritten by the re-audit.

### Research OS literature inventory correction · 2026-11-13 KST

The section 4 papers are held in `10_PAPERS`, including [Ruoss et al. (2024), Amortized Planning with Large-Scale Transformers](https://drive.google.com/file/d/1UBwx4nKx6i12tiHmqYZpAow644_Ts63x/view), whose stored PDF identifies itself as arXiv v2 and carries the NeurIPS 2024 conference footer. [Herbeck & Barth (1996), An Explanation Tool for Chess Endgames Based on Rules](https://drive.google.com/file/d/1eNS8H3LVA36bGdlmg5kTin6MtI85MeeJ/view) was recovered by searching the first author's surname and verified from the ICCA Journal PDF, pp. 75–82. This corrects the previous negative title search.

| Exact work | Research OS status | Publisher record |
| --- | --- | --- |
| Björnsson (2024), *Chess and explainable AI* | Exact full text unconfirmed after title/DOI search | [ICGA Journal 46(2), 67–75](https://doi.org/10.3233/ICG-240256) |
| Kopec & Bratko (1982), *The Bratko-Kopec Experiment: A Comparison of Human and Computer Performance in Chess* | Exact chapter unconfirmed. The updated periodical article and Kopec dissertation are held. | [Advances in Computer Chess 3, 57–72](https://doi.org/10.1016/B978-0-08-026898-9.50009-7) |
| Demura & Kaneko (2024), *Initial state diversification for efficient AlphaZero-style training* | Exact full text unconfirmed after author/title/DOI search | [ICGA Journal 46(2), 40–66](https://doi.org/10.3233/ICG-240255) |

[Gadwal, Greer & McCalla (1993)](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view) is held as a manuscript. A separate copy of the [Applied Intelligence publisher version](https://doi.org/10.1007/BF00871938), pp. 207–224, was not confirmed. Inventory scope is the accessible Research OS files returned by targeted searches, with no PDFs acquired or moved.

**Reproducibility note:** The SHA-locked original 0.30/S4-H2 holdout and inherited 0.29 7/8 prospective HOLD remain sealed. The new S4-K experiment strictly reuses prior **development** cases only.
