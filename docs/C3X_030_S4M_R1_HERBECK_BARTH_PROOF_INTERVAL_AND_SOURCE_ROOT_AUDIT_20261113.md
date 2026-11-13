# C3X 0.30 — S4-M/R1: Herbeck–Barth Full-Text Audit, Proof-Carrying WDL Bounds and Real-Root Candidate Reassessment

**Date:** 2026-11-13 KST. **Chat:** C3X 33 (chat number, NOT version). **Research version:** C3X 0.30 unchanged. **Repository author:** WhoSia, never GitHub Actions[bot].

## I. Original primary-literature intake, preservation and critical reading

Newly supplied original primary text:

- Heinz M. Herbeck and Wilhelm Barth (1996), **“An Explanation Tool for Chess Endgames Based on Rules,”** *ICCA Journal* **19(2):75–82**, DOI [10.3233/ICG-1996-19202](https://doi.org/10.3233/ICG-1996-19202).
- Read full 8 pages, sections 1–8, including the printed Figures 1 and 2 and individual example studies. Scanned figures on article pp. 79–80 were visually inspected rather than inferred from messy extraction.
- Original **2,571,046-byte PDF** moved intact in Google Drive from `00_INTAKE — Literature Radar` to the canonical `10_PAPERS — Canonical Literature Commons` and normalized to `Herbeck & Barth (1996) — An Explanation Tool for Chess Endgames Based on Rules — ICCA Journal 19(2) 75-82.pdf`. **Original Drive ID unchanged:** [original primary full text](https://drive.google.com/file/d/1eNS8H3LVA36bGdlmg5kTin6MtI85MeeJ/view). It is no longer missing.

### Actual argument by section

**§2, Rule method and validation:** Expert-authored endgame rules assign intervals containing the true win/draw/loss outcome. The original authors combine intervals with modified α–β search to handle undecided positions. Their local rule-validation procedure compares rule intervals with search intervals, but the paper acknowledges that circular justification can be a risk if downstream premises are also wrong; termination/mate/stalemate and previously validated simpler endgames are intended to ground correctness. Their historical validation claim pertains to their specific endgame-rule systems, not arbitrary chess explanations.

**§3, PV method:** After iterative search, follow the principal variation until a decisive rule supports the root result. The Isenegger 1.Ke2 study illustrates why a visually tempting pawn advance can be inferior; the actual terminal reason is a rule supporting the result on the continuation. Draw explanations may require *two* separate reasons, one showing neither player can force a win, rather than one cherry-picked rule. Figured pawn-endgame positions are not automatically generalizable to middlegame positional explanations.

**§4, Collection method:** This is more relevant to C3X than the obvious PV interface. Figure 1 (printed p.80) explicitly labels lower-bound contributor sets **αR** and upper-bound contributor sets **βR** and backs them up across multiple continuations. At a minimax choice, a lower bound can be justified by a **witness** branch whereas a nontrivial upper bound must generally account for **all** legal responses. The authors already did bound-specific rule ancestry; claiming that C3X invented rule-tagged minimax or branch collection would be wrong.

**§5, Visual tree:** Explanation loses tree structure when collapsed into linear text. Their 1996 X-Windows/Motif interface exposed rule identity, backed-up rule sets, search intervals and alternative moves. C3X should preserve clickable or inspectable source-evidence branching instead of publishing only a fluent explanation.

**§6–7, expert-systems connection and conclusion:** Rule-generated explanation is a user-facing interpretive layer. It is not automatically a demonstration that a modern Stockfish NNUE score or transposition-table cache actually *caused* the selected bestmove. Human comprehension, causal fidelity and formal soundness require different validation criteria.

### Original C3X hypothesis after this audit (NOT claimed proven unique)

A **typed evidence-to-explanation ladder** could connect:
1. **Native computational observation** (Stockfish mask / cutoff / root update receipts): provenance of an *event*, but no WDL proof and no cross-run mediator identity.
2. **Formally valid bound** (terminal chess rule or independently verified inductive certificate): mathematical support for a win/draw/loss interval but *not necessarily* a native engine's actual reasoning.
3. **Cross-arm causal contribution**: requires counterfactual/source-specific child–ancestor–root value chain and verified negative controls.
4. **Response-robust strategic concept**: additionally requires legal counter-response evaluations beyond one PV, and independent labels.
5. **Human-understandable pedagogical value**: must be independently evaluated; not implied by explanation plausibility.

The bound-origin part is indebted to **Herbeck & Barth 1996** and **Barth & Barth 1992**; the proposed engineering synthesis applies independent source and counterfactual evidence gates. No novelty claim without systematic comparison.

## II. New proof-carrying WDL interval module (actual executable code and tests)

Files:

- [`harness/c3x_030_s4m_proof_carrying_intervals.py`](../harness/c3x_030_s4m_proof_carrying_intervals.py)
- [`harness/test_c3x_030_s4m_proof_carrying_intervals.py`](../harness/test_c3x_030_s4m_proof_carrying_intervals.py)
- [CI workflow](../.github/workflows/c3x-030-s4m-endgame-proofs.yml).

Let `[-1,0,+1]` represent loss/draw/win from **the current side to move**. If child `m` has verified interval `[ℓ_m,u_m]` from its next player's perspective, the parent move interval is `[-u_m,-ℓ_m]`. With all legal moves represented, parent interval bounds follow:

`L = max_m(-u_m)`, `U = max_m(-ℓ_m)`.

**Crucial:** An unverified or absent legal response is filled conservatively as `[-1,+1]`. Thus a single rigorously verified winning move can establish `[+1,+1]` (other branches may remain unknown); claiming a nontrivial upper bound or a draw can require **all** legal replies to be accounted for. The implementation tracks witness moves, missing legal moves, separate lower/upper explanation tags, and coverage flags.

**First strict gate:** only independently re-evaluated **actual legal terminal** states (checkmate, stalemate or insufficient material) can become accepted nontrivial child certificates. User-provided `verified: true`, Stockfish score/cutoff, or arbitrary synthetic labels **cannot** certify a WDL result. 50/75-move and repetition adjudications relying on absent history are not asserted. Future multi-ply recursion or external tablebase certification must be implemented separately rather than pretending the one-ply prototype is a complete KPKP solver.

Worked *legal* example: board after `1.f3 e5 2.g4`, with black to move, has legal `...Qh4#`. Its resulting child is provably lost for white (checkmated). One certified terminal witness gives the parent exact `[win,win]` even with all other legal black moves undisclosed. This proves a limited **chess outcome** statement; it does not say that C3X explained how Stockfish internally reasoned about that checkmate.

[First S4-M proof-contract CI #43361401823](https://github.com/WhoSia/C3X/actions/runs/43361401823) passed **13/13 regression tests** for genuine checkmate witness, partial coverage, stale/fake terminal proof, FEN legality and observational source-score isolation.

**Claims NOT made:** complete endgame retrograde proof, rule set validation over all legal positions, explanatory quality, TT causal mediation, game-split generalization, empirical comparison with the 1996 author program.

## III. Independent archived real S4-L root candidate matching

Existing [S4-L native run #43359776211](https://github.com/WhoSia/C3X/actions/runs/43359776211) had 48 actual Stockfish16 searches and **576,619 nodes** on 8 correlated development FENs from 4 researcher-authored games; **zero held-out games**. Sham versus two-hit targeted native TT masking changed bestmove in **3/16** trials. It logged 6,488/6,959 root candidate score events for Sham and 6,727/7,130 for two-hit, preserving five capped true `go` epochs per arm.

New [`c3x_030_s4m_r1_root_candidate_archive.py`](../harness/c3x_030_s4m_r1_root_candidate_archive.py) is an **independent audit** of the separately archived original JSON with fixed SHA `a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9`.

Cross-arm candidate matching is allowed only within the **same trial number**, using `(root_move_raw, depth, moveCount, alpha, beta)`. A state must occur exactly once in each **observed** trace. Same signature is not proof of identical TT state, search history or counterfactual invocation identity. Event ordinal is never used to join separate runs. Capped/unmatched traces are declared unknown.

Independent [S4-M/R1 CI #43361758729](https://github.com/WhoSia/C3X/actions/runs/43361758729) PASS: **9/9 contract tests**; ZERO fresh engine searches; recovered and byte-verified immutable original S4-L source archive.

| Descriptive native-source finding | Count |
| --- | ---: |
| Shared root state signatures across Sham/two-hit | **3,851** |
| Candidate signatures unique once per observed arm/trial | **3,782** |
| Repeated/ambiguous shared signatures | **69** |
| Candidate pairs with differing numeric root evaluation values | **7** |
| TT two-hit root bestmove changes | **3 / 16 trials** |
| Source trace pairs with at least one 512-receipt censoring | **5 / 16 trial-pairs** |

A descriptive, *post-hoc* 2×2 categorization of those **16 dependent trials**:
- Root changed & at least one observed candidate value differed: **3**.
- Root changed & no observed candidate value difference: **0**.
- Root unchanged & some observed candidate value differed: **3**.
- Root unchanged & no observed candidate value difference: **10**.

This is NOT a heldout prediction/recall score, not an externally validated significance test, and does not identify the source TT mask as mediator. All three root-changing trials were from Italian ply10 (2 trials) and London ply8 (1 trial); three other trials had an observed score contrast without root-choice change. In this small hand-built cohort, the contrast is descriptively neither equivalent to nor sufficient for changing the selected move.

The 7 differing values are observed at **matching signatures, not necessarily causally identical invocation states**; matching signatures omit TT table contents, excluded-move/search history and other state. Both the observed source and nonobservation have strict boundaries.

## IV. Updated exact original literature custody ledger

**Now owned:** Herbeck & Barth 1996 (entire 8-page ICCA Journal original, bytes kept, canonical Drive `10_PAPERS`). Thus it is **removed** from former missing-list.

**Still NOT CONFIRMED owned** by title-specific Drive original-asset search (related source texts do not count):

| Priority | Exact work | Evidence/availability |
| --- | --- | --- |
| P1 | **Barth & Barth (1992)**, *Validating a Range of Endgame Programs*, ICCA Journal 15(3):132–139, DOI [10.3233/ICG-1992-15303](https://doi.org/10.3233/ICG-1992-15303) | Direct methodological predecessor; publicly discoverable [publisher PDF landing endpoint](https://journals.sagepub.com/doi/pdf/10.3233/ICG-1992-15303?download=true) but full original bytes not found in Drive; author copy/library route |
| P1 | **Wilhelm Barth (1995)**, *Combining Knowledge and Search to Yield Infallible Endgame Programs: A Study of Passed Pawns in the KPKP Endgame*, ICCA Journal 18(3):148–159, [DBLP entry](https://dblp.org/rec/journals/icga/Barth95) | Claim of rule-system completeness and ancestor of 1996 rule tags; publisher/library/author copy |
| P1 | **Yngvi Björnsson (2024)**, *Chess and Explainable AI*, ICGA Journal 46(2):67–75, DOI [10.3233/ICG-240256](https://doi.org/10.3233/ICG-240256) | Direct review of chess XAI; Pálsson & Björnsson 2024 ECAI article in Drive is distinct |
| P2 | **Kopec & Bratko (1982)**, *The Bratko–Kopec Experiment*, in *Advances in Computer Chess 3*:57–72, DOI [10.1016/B978-0-08-026898-9.50009-7](https://doi.org/10.1016/B978-0-08-026898-9.50009-7) | Historic human-vs-computer chess analysis; owned periodical and Kopec dissertation are NOT this chapter |
| P3 | **Demura & Kaneko (2024)**, *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA Journal 46(2):40–66, DOI [10.3233/ICG-240255](https://doi.org/10.3233/ICG-240255) | Training diversity/generalization, less direct for native Stockfish mediation |

These are custody statuses for **exact original PDFs**, not statements that no version is accessible in the public web. No paper acquired through unauthorized channels. Do not request already-held SARFA, BinProp, Spinnato/SHAP, Fritz–Fürnkranz or Herbeck & Barth.

## V. Decision gates: what we do next, and what we must not claim

**PASS:**
- Canonicalized and actually read 1996 rule-based explanation primary text including figure logic;
- formally checkable legal-terminal WDL prototype and 13 regression tests;
- real-root source contrast from SHA-pinned original, 3,851/3,782/69/7/3 metrics reproduced by CI;
- source audit keeps 5 censored trial pairs explicitly and original S4-H2 8-game holdout unopened.

**HOLD:**
- Full KPKP rule-based interval proof (our prototype only checks terminal/mate states);
- Actual Stockfish TT mask → specific return → ancestor update → bestmove **counterfactual** mediation;
- Independent human-game cohort, explanation utility, prior-art superiority;
- Original C3X 0.29 prospective 7/8 gate.

**Next:** S4-N should introduce legal-state/root branch lineage and instrument only the affected branch's main-search and qsearch boundary, and require stronger paired state identity than `(move, depth, moveCount, alpha,beta)`. Separately F3 should compare **different explanation targets** without forcing SARFA saliency or SHAP piece scores into Boolean terminal certificates. Frame outputs in the five-tier evidence taxonomy above.

This turn deliberately opened **no heldout S4-H2 cases** and performed **no new Stockfish searches**; all new native findings are verified reanalyses of existing original source searches.
