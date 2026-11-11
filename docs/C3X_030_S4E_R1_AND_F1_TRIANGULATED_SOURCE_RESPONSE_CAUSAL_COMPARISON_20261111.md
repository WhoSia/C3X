# C3X 0.30 — S4E Native Invocation Graph, S4E/R1 Original Negamax Value-Edge Audit and F1 Method-Fusion Research Decision

**Date:** 2026-11-11 KST. **Version retained:** C3X 0.30; conversation C3X 32. Decision D1 original Stockfish TT-event→ancestor→root causality remains the primary research priority. Method fusion is a comparative hypothesis requiring head-to-head benchmark, NOT an already superior method.

## I. S4E real source-native invocation identity and original noninterference

Pinned real original Stockfish16 source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Strict source-anchored C++ patch [`harness/c3x_030_p11s4e_invocation_patch.py`](../harness/c3x_030_p11s4e_invocation_patch.py) adds per-process/thread search invocation IDs, parent IDs, bounded TT-hit logs at SHA-frozen ply1 key, normal-return values, RAII scope-exit records even on early search returns, and root candidate move/value with last completed main-search child ID. It does not alter TT hit, TT entry, bestmove or value and does not log qsearch. Scope-exit events on early returns have `value_known=0`, so do not assert early-return value transmission. Log stream capped at 240 events/process; missing source events are not proof they did not happen. A 'last child' marker is NOT automatically proof it directly supplied the root candidate score.

Native source FEN set: **three previously studied S4B development boards** (Queen's Gambit ply4, Sicilian Najdorf ply4, English ply4) with exact target keys selected *before* S4E from S4B immutable original JSON SHA256 `081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300`. Threads1, Hash16MiB, Skill20, NNUE=false, UCI_LimitStrength=false, `go nodes 12000`. Original vs separate compiled read-only instrumented binary, two consecutive searches per FEN/engine: **12 actual new native searches, 144,166 measured native nodes**; bestmove, score, actual nodes, depth and PV all match baseline in every pair (**0 differences**). **No physical TT intervention in S4E.**

[**S4E actual native CI SUCCESS #42991754182**](https://github.com/WhoSia/C3X/actions/runs/42991754182), eight synthetic/fail-closed patch and event tests. [Original native runner](../harness/c3x_030_p11s4e_invocation_court.py), source JSON byte SHA256 `36f2087fc522e5f223ce6ea0072815b8501327e9192dcbc3529a1aae6aac2e4d`. CI ZIP SHA256 `840e85d5eeed18dda07e8c5a51a87ce721db1fa21c797a7f52cb9782148ef586`. [**S4E 12-search original evidence ZIP sealed in Drive**](https://drive.google.com/file/d/1IonE9bWPW0h-_SiBu0KF_S9R2LOSa8rX/view).

Original capped visible observation counts for each FEN (aggregating two logged UCI searches, 240 maximum recorded events/process):

| Known chess FEN | Target TT probes | Same-invocation normal returns | Same-invocation scope exits | Bounded root candidates | Noninterference |
| --- | ---: | ---: | ---: | ---: | --- |
| Queen's Gambit ply4 | 7 | 5 | 7 | 221 | PASS |
| Sicilian Najdorf ply4 | 7 | 4 | 7 | 222 | PASS |
| English ply4 | 11 | 8 | 11 | 210 | PASS |

As the logger is globally capped in each process, **these counts are lower bounds on the real number of executed search events**, not complete tree summaries.

## II. S4E/R1 SHA-locked reanalysis of the REAL original source results — 14 signed value-flow matches

To go beyond raw move-code overlap, a **separate original-proof audit** [`harness/c3x_030_p11s4e_r1_original_return_audit.py`](../harness/c3x_030_p11s4e_r1_original_return_audit.py) downloads the exact S4E native original from prior workflow and first verifies source raw JSON SHA `36f2087...`. On the real observed event stream, accept a value-flow match only if:

1. The **same actual invocation ID** carries a ply1 `TT.probe hit=1` and a `normal_return` event.
2. The child's `parent ID` is the root-candidate event's `id`, and root-candidate's `child_last` matches that exact child's ID.
3. Physical event order `probe < normal_return < root_candidate` within the real logged stream is respected.
4. The numerical negamax relation `root_candidate.value == -child_normal_return.value` holds exactly. Any contradiction causes **HOLD**, rather than a synthetic or interpreted 'match'.

All conditions passed for **14 observed native events** in the previously sealed S4E 12-search source receipt: Queen's Gambit **5**, Sicilian Najdorf **4**, English **5**. This is stronger than raw move equality: it is **observational evidence of actual child return values reaching candidate root score logic on the normal-return pathway under tested source runtime**. It is **NOT evidence** that a TT hit *caused* the child return value, nor of exhaustive ancestor-node mediation, nor of a new TT intervention in the R1 auditor.

[**S4E/R1 independent CI SUCCESS #42992698684**](https://github.com/WhoSia/C3X/actions/runs/42992698684), five synthetic adversarial checks (parent mismatch, sign mismatch, temporal order, non-hit). **0 new native searches**. Derived JSON SHA256 `e010eafaeaef20e902d4cbb9d48e63a83ef5d8bd5f964ae27633ce20506a7f79`, original audit ZIP SHA256 `03d9041741853e27943b88fbecec5c0c086917ea65f46967d66b654a620cffc9`. [R1 original read-only audit ZIP in Drive](https://drive.google.com/file/d/1OIDP762_b9ZjvjOQc9LtEWYDn-YEl_gN/view).

**Scientific decision:** Pass an *observed signed-return value-edge* for these 14 logged events, **do not promote TT causal mediation or independent confirmation**. A future same-binary masked vs sham source trace is needed to prove the TT hit changes this actual returned value and parent/root choice, with no postselected root events. Early exits/qsearch remain missing and source log caps can hide relevant paths. This work uses the previously observed three developmental FENs (no new games).

## III. F1: a precise fusion hypothesis, not a fabricated 'better than the paper' result

Research direction: **Triangulated Source–Response–Causal explanation (TSRC)**. Treat three distinct types of explanation evidence as separate necessary gates for strong causal-strategic claims:

1. **SARFA prior art**: selected-action perturbation saliency (Puri et al.); fixed action support and source native evidence, but *saliency alone does not prove native source mechanism*.
2. **Response robustness prior art**: Cui-inspired legal conditional strategy tree, separately source-pinned opponent replies and **independent Berserk** leaf value, without calling k sampled opponent replies all possible adversarial responses.
3. **Native physical causality**: same-source-engine target-vs-sham actual TT source intervention with event/return/root linkage *and* its failure/abstention gates; a single present TT hit or original score prediction is insufficient.

Proposed rule **does not invent an arbitrary favorable weighted sum**. `claim = sarfa_positive AND independent_response_verified AND native_event_to_root_certified`; missing any evidence produces **ABSTAIN**, not false or a fabricated number. This is a conservative **claim admission** system, not necessarily a stronger chess player or higher-coverage explanation generator. A conjunction can trivially reduce false positives by abstaining and therefore must be compared on **coverage, false claims, precision, recall and grouped independent-game F1 simultaneously**, rather than cherry-picking precision.

[**F1 concrete comparison/audit code**](../harness/c3x_030_p11f1_evidence_fusion_audit.py) and [seven adversarial unit tests](../harness/test_c3x_030_p11f1_evidence_fusion_audit.py) now implement the same-case four-method comparison:
- `sarfa_only`
- `response_only`
- `native_only`
- `three_gate_fusion`

Tests require truly **independent labels**, a **different source-vs-independent judge engine**, SHA evidence references, common chess cases, disjoint complete-game development/holdout splits, and **preregistered** holdout before outcomes. Unknown evidence `None` yields abstention unless another gate explicitly fails. Metrics are split by development/holdout, including abstentions, coverage, TP/FP/FN/TN, precision/recall/F1 on nonabstained records. Do not mislabel any unit test as empirical paper competition.

[**F1 synthetic CI SUCCESS #42992260169**](https://github.com/WhoSia/C3X/actions/runs/42992260169), seven tests PASS. **0 new native chess searches, 0 human-blind or original-paper head-to-head runs under F1**. Status: **COMPARATIVE METHOD CONTRACT READY; SUPERIORITY CLAIM HOLD**.

### Precommitted head-to-head benchmark design to execute later, not performed yet

For a future valid **'better than the paper'** claim, preregister source and evaluation protocols **before** chess outcome selection, e.g. freeze complete 12 independently sourced games, diverse early/middle/end FEN positions and legal move histories with deterministic rules, separate tuning cohort and unseen holdout; no selecting only positive S4E cases. Run all four methods on **identical positions, action candidates, source search budgets, opponent reply support, different fixed independent Berserk judge budgets, and the same blinded independently adjudicated semantic labels**.

Use **game ID** as resampling unit because FEN snapshots from one game are correlated; report raw paired differences, grouped bootstrap intervals with small-sample caveats, per-root false causal claim rate, actual nodes/time cost, coverage at fixed risk, and recall/precision on the same nonabstained support where interpretable. Comparison to original papers' reported baselines requires **faithful original experimental protocol and input populations**, not only our locally implemented counterparts. Prefer Pareto analysis: if fusion improves factual trust but covers far fewer positions, report tradeoff and do not assert universal superiority. Strong human chess tutoring impact also needs a learner study, separate from computational grounding.

**Current likely null:** native full ancestor→root causality is not certified in S4E; this gate should legitimately abstain. Fabricating a positive fusion result from the 14 observed arithmetic links would undermine D1.

## IV. Implementation next decision and explicit HOLDs

**Next P11/S4G** (not executed): instrument *all relevant actual return pathways* including TT early cutoff/qsearch, attach unique per-invocation IDs to immediate child search calls and parent's value updates (not just `child_last`), and run **same compiled instrumented binary** with 0/1/2/many key-hit suppressions and sham, on the **same frozen source history**. Each accepted causal chain must show targeted physical source event, changed child's returned evaluation, changed parent's actual computation, and changed root candidate/rank or explicitly no root change, all with true invocation IDs. Retain source SHA and search node budgets. Then proceed to independent preregistered new-game cohorts to validate. Historic C3X 0.29 prospective 7/8 **HOLD** unchanged.

Do not broaden product UX or claim the entire original Puri/Cui/QUEEN research reproduced; F1 remains a hypothesis to benchmark.

## V. Literature custody

No new PDFs were added during S4E/F1; earlier newly owned [Gadwal et al. (1993) author manuscript](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view) remains held at `10_PAPERS`, Springer typeset edition unverified. Exact still-unheld full originals: Björnsson (2024), Bratko & Kopec (1982) original chapter, Herbeck & Barth (1996), Demura & Kaneko (2024). Only lawful author manuscripts and library access routes should be pursued.
