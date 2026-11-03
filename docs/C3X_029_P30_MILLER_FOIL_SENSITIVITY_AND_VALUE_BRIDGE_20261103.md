# C3X 0.29-P30 — Foil Sensitivity, Verified Miller (2019), and the Value-Plan Research Bridge

Date: 2026-11-03. Scientific status: **primary-source reading + newly executed synthetic formal regressions + archival source reanalysis, NOT a new Stockfish competitive experiment.**

## Question and correction
The C3X founding question (C3X 1.md, 2026-08-14) explicitly asks why one plausible chess move is marginally preferable to another. P29 separated feasibility, utility and incremental predictive information. Tim Miller (2019), _Explanation in Artificial Intelligence: Insights from the Social Sciences_, _Artificial Intelligence_ 267, 1–38, DOI 10.1016/j.artint.2018.07.007, is now available in Research OS **10_PAPERS**.

Miller Section 1.2 identifies four themes from prior human explanation research: explanations are **contrastive**, **selective**, causal information may communicate better than unsupported numeric probabilities, and explanations are **social and contextual**. Section 2.3 distinguishes *fact* P from particular *foil* Q, and discusses that a purported cause common to both is often uninformative for that comparison. These are established explanations literature, **not** novelties of C3X.

The new C3X-specific empirical question is therefore whether a **predeclared, source-verifiable conditional plan consequence** can answer a concrete question 'Why chess move a rather than legal alternative b?' at a matched independent engine budget; when switching b to c, does the system accept, change or abstain appropriately? Mere differentiating labels do not imply positive strategic value.

## P30 foil countermodel (synthetic; not chess evaluation)
Three distinct counterfactual worlds share one ROOT source and one frozen plan predicate Q, each with own opponent reply universe.
- target a: Q guaranteed, finite minimax 0.10
- foil b: Q impossible on sampled complete declared reply domain, finite minimax -0.10
- foil c: Q guaranteed, finite minimax 0.20
Then 'Q is possible only after a' is relevant for a-versus-b (along with a separately validated value comparison), but false/non-discriminating for a-versus-c. A generic fixed narration of a that ignores the foil fails this test. These are artificial payoffs and caller-declared universes, **not observed Stockfish scores**.

## Executable test
- `tools/c3x_029_p30_foil_semantics.py`: inputs include frozen target and foil, same root and plan IDs, separate per-candidate legal reply sets and per-reply legal actions with Q and utility. Fails closed on untyped/unknown claims, missing reply universe or missing claimed verification. Computes finite V, V_Q, and emits either non-discriminating, no target plan, plan different but not value-separated, or value separation (DECLARED ONLY).
- `tools/test_c3x_029_p30_foil_semantics.py`: 10 synthetic adversarial cases, locally executed and all passed, including changing the foil, plan-value inversion, heldout declaration denied, fake legality flag, candidate identity mismatch and duplicate acts.
- **Important authority ceiling**: all root IDs, law verification fields, 'predeclared_before_outcome' flags and U values are **untrusted caller declarations**; code does not independently authenticate source SHA, actual chess legality, frozen timestamps or native engine score. It must not be used to advertise prospective superiority or causal mechanism.

## Archived actual chess source check: root-order sensitivity
Original authentic repository receipt `c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json` records historical 72 native SF16 patched O/F/Z runs on 12 independent *source-selected* Lichess standalone-FEN roots (not full original game histories), with 12 original-order baseline shams.
- 12 root reorders, 2/12 categorical bestmove changes, 8/12 score/bound changes, 11/12 node changes, 10/12 PV changes.
- Changed case 6: original c3a4, reordered e4d6; cp 45→13, nodes 64459→90055.
- Changed case 8: original e6h3, reordered h5g7; cp 66→40, nodes 63764→53106.
This is **archived evidence of source-engine search-order dependence**, not a fresh run, not proof of unstable marginality across depths and not evidence about plan-value explanation. The cases are outcome-exposed development and cannot be enrolled as new heldout.
Observation: an already existing contact result indicates root choice can be sensitive to the ordering instrument, so P30 eligibility should check preference stability across computational conditions, not merely one cp difference.

## Human evaluation question
A benchmark must specify fact/foil separately, preselect a strategy-relevant Q with clear observable consequence and judge both truth and informative contrast. To test usefulness, randomize on independently sourced games:
(A) score/PV only, (B) static concepts, (C) generic narrative, (D) foil-specific policy/value evidence.
Outcome is independently scored choice on new positions, plus reason transfer and calibrated confidence; do not use user preference or prose length as a proxy for learning. C3X has not run such a study.

## Reading/custody
New Miller PDF file ID 1b0Zqep9G93Mc-u-GFZ78gYXB6Oyhleke. Original bytes SHA-256 64e43e855beaa3026fba720392685109b9a4a67f115ab1b1c132bd41351eb7a6, 1,502,726 bytes, 38 pages, initial filename `1-s2.0-S0004370218305988-main.pdf`. Verified title, journal, DOI, cover render, and extracted relevant Sections 1.2, 2.3; renamed and moved without changing ID from Research OS 00_INTAKE to canonical 10_PAPERS, verified via readback. **This is a targeted paper reading, not a chapter-by-chapter exhaustive audit.**
Remaining exact-edition search misses: Bratman (1987), Lipton (2004), Halpern (2016), Pearl (2009). Search miss != confirmed global absence.
Other earlier 2026-11-03 00_INTAKE object `03_13_2026.pdf` is an unrelated Ravasio et al. biological proofreading article; not moved under C3X.

## Next empirical gate (not another evaluator-only court)
1. Acquire/freeze new complete history source games and game-independent split; preserve raw file hashes/private PGN rights.
2. For each stable near-equal move, lock specific foil(s), planned predicate Q, opponent legal reply domains, horizon and utility comparator **before outcome**.
3. Generate actual legal continuations with recovered Go engine. Verify via independent chess library and source checks where possible.
4. Score strong baseline at matched compute (full score/PV and generic concepts, executable BinProp or equivalent when possible); add foil-switch test and matched abstention.
5. Test factual statement truth, distinctive plan-consequence utility, game-macro paired predictive skill, reply perturbation, and blind human transfer separately.
Any P30 'better' claim without independent model comparisons remains HOLD.

## 2026-11-03 Remote regression verification
- GitHub Actions run 41613074762, URL https://github.com/WhoSia/C3X/actions/runs/41613074762, head SHA a324f65cd1b297e9c0a21aaf7b4db8e36bdc77b9, status completed, conclusion **success**. Verified through authenticated GitHub Actions run list and `fetch_workflow_run_jobs`.
- The four individual jobs/steps `P29 value probe regression`, `P29 value certificate regression`, `P29 incremental information regression`, `P30 foil intervention and value falsifier regression` all had status **success**, along with original public summary check. This closes CI invocation of the synthetic contracts, **not** real Stockfish validation, prospective preregistration proof, independent-game labels or explainability superiority.
