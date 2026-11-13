# C3X 0.30 — S4-M/R1: Herbeck–Barth Full-Text Audit, Proof-Carrying WDL Bounds and Real-Root Candidate Reassessment

**Date:** 2026-11-13 KST. **Chat:** C3X 33 (chat number, NOT version). **Research version:** C3X 0.30 unchanged. **Repository author:** WhoSia, never GitHub Actions[bot].

## I. Original primary-literature intake, preservation and critical reading

Newly supplied original primary text:

- Heinz M. Herbeck and Wilhelm Barth (1996), **“An Explanation Tool for Chess Endgames Based on Rules,”** *ICCA Journal* **19(2):75–82**, DOI [10.3233/ICG-1996-19202](https://doi.org/10.3233/ICG-1996-19202).
- Read full 8 pages, sections 1–8, including the printed Figures 1 and 2 and individual example studies. Scanned figures on article pp. 79–80 were visually inspected rather than inferred from messy extraction.
- Original **2,571,046-byte PDF**, independently SHA-256 checked as `0605423a1ba4d59836746aaf870b9418ce3f5876d91f3d039c1288287f1079f7`, moved intact in Google Drive from `00_INTAKE — Literature Radar` to the canonical `10_PAPERS — Canonical Literature Commons` and normalized to `Herbeck & Barth (1996) — An Explanation Tool for Chess Endgames Based on Rules — ICCA Journal 19(2) 75-82.pdf`. **Original Drive ID unchanged:** [original primary full text](https://drive.google.com/file/d/1eNS8H3LVA36bGdlmg5kTin6MtI85MeeJ/view). It is no longer missing.

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

**Historical inventory at S4-M/R1.** See §VII for the two originals filed later that day and the updated list.

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

## VI. Final custody and follow-up status (same-day update)

- [S4-M real legal terminal witness + strict tests CI #43362175794 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/43362175794): original separately archived [Drive ZIP](https://drive.google.com/file/d/130LM_rMeNlC_4r1oE_8iKukeduKQlXRW/view). The explicit Fool's Mate source proof has **30 legal candidate moves**, only one certified `d8h4` terminal witness, 29 unknown alternative moves, and exact WDL win interval without inventing complete branch coverage.
- [S4-M/R1 latest independent root contrast CI #43362096970 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/43362096970): 9 tests, zero new native searches, and independently reconstructed original roots and the 3/0/3/10 descriptive contingency table; [Drive SHA-audited raw ZIP](https://drive.google.com/file/d/1rPQVqtd-_Qr7AXWrGJYel7lUDY_26x8H/view).
- Archived original 1996 PDF original bytes SHA `0605423a1ba4d59836746aaf870b9418ce3f5876d91f3d039c1288287f1079f7`. This is the file SHA, distinct from Google Drive ID and any repository document commit SHA.
- No assertion of native Stockfish root-choice mediation, full KPKP rule correctness, independent F3 method superiority or heldout results. Research version remains 0.30.


## VII. Barth & Barth 1992 and Barth 1995 intake and S4-M/R2

Both journal originals are now held in `10_PAPERS`. The move kept each Drive ID and used metadata only. Page counts and SHA-256 values below were computed from the downloaded files after filing.

| Original | PDF pages | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [Barth & Barth 1992, ICCA 15(3), 132–139](https://drive.google.com/file/d/1DlWDHgboXe_t2Z8EstHlh7q5_JuuqQS6/view) | 8 | 1,197,486 | `f6fb1a622faf71358824538cfbb33b82d7143ec2641d3a8cb3687646d2738e8d` |
| [Barth 1995, ICCA 18(3), 148–159](https://drive.google.com/file/d/1R-nUeOHXyrZ_iHrNJohRQPYfP09ofJDb/view) | 12 | 3,627,582 | `625f94a07026d9b20d80f45eeda9dce933976914915b01931ac98c74b96cbc78` |

### What the two papers establish

- **1992, §§2.3, 3.5 and 4.1–4.4.** For a rule interval R, validation seeks a search interval A contained in R. Disjoint intervals expose an inconsistency. A shared evaluation rule can propagate a false win around a drawn cycle when the scale is plain WDL. On the refined scale, traversal of a reversible cycle makes the returned winning bound strictly weaker. Terminal positions and validated endgame transitions ground the check. The paper also distinguishes a move that guarantees progress from one that reaches the next irreversible event in the fewest plies.
- **1995, §2 and Figure 1 (p. 150).** Six rules use conservative applicability conditions. The promotion-race rule checks more than the pawn ranks. Check on promotion, skewers, king interference and the geometry of a queen versus a pawn can change the outcome. The Réti rule must account for king moves that simultaneously support the friendly pawn and close in on the enemy pawn.
- **1995, §3 and Table 1.** In Réti's study, the program initially bounds Kg7 by [loss, draw]. Establishing the draw takes up to 13 plies in the deepest branch. Table 1 compares the historical program with Mephisto Genius 3, using a material-value threshold as a proxy for when the latter has solved a win. Those timings describe the authors' setup and use different criteria for declaring a result.
- **1996, §§3–4.** Herbeck and Barth add principal-variation and multiple-branch explanations over those bounds. C3X's question is whether an independently verifiable explanation can also be linked to the path actually taken by Stockfish under an intervention.

### Executable progress check

The [verifier](../harness/c3x_030_s4m_r2_progress_certificate.py) checks a finite game graph with a fixed prospective winner. A rank of zero requires a supplied winning terminal. At a winner node at least one successor must have a strictly smaller rank. At an opponent node every successor must have a strictly smaller rank. Induction bounds the plies to a winning terminal by the root rank. This abstracts the cycle issue in the 1992 paper. Ranks here count plies to a supplied winning terminal, while the historical refined scale can also end a segment at a winning irreversible move.

The regression suite demonstrates a two-state cycle satisfying local +1 WDL equations with no winning terminal. It also distinguishes a cycle the winner can avoid from a reply the opponent may force. An independent bounded-reachability calculation agrees on 1,800 starts across 900 enumerated synthetic graphs. Four local tests passed. [CI run](https://github.com/WhoSia/C3X/actions/runs/43367837978).

The verifier takes graph edges and terminal labels as inputs. A chess integration needs independently replayed legal moves, terminal adjudication, and complete opponent reply sets. A pawn move that only changes material or resets a clock cannot be accepted as a winning terminal. Réti (1995 Diagram 1) and the promotion-race counterexample (Table 1, position X) are candidate development cases. Native S4-N lineage and the S4-H2 holdout remain open.

### Current exact-text inventory

The two 1992/1995 rows above are now resolved. The remaining original-text gaps are Björnsson 2024, Kopec & Bratko 1982, and Demura & Kaneko 2024. Two newly identified technical reports are TU Wien Institutsbericht 34 (Barth & Barth 1991) and 36 (Barth 1994). The short ICCA records for those technical reports establish bibliographic leads. The full reports were not found by the Drive title search.


## VIII. S4-M/R3 · Notice identity and a local tablebase comparison

### Source custody

| PDF received | What the pages contain | SHA-256 |
| --- | --- | --- |
| [Barth & Barth 1991](https://drive.google.com/file/d/12rAcb1dQ1-SQ8V9Ql1TTZZ8dbdFDgc0H/view) | ICCA 14(4), p. 209, one page containing a quotation from the abstract of the 38-page TU Wien Report 34 | `2789c0e57fda6405e2c9ad0e42b64da9874dfd28e42c5a10cd1f25de6b58d39b` |
| [Barth 1994](https://drive.google.com/file/d/11OnINES2n3fifb_qT6Mvtehk_UbRcT4U/view) | ICCA 17(1), pp. 35–36, two scanned pages containing the editorial paraphrase of Report 36's abstract on p. 35 | `076a01b4d649e011cf56da44c6f93e8f7e26d8401f9c29cfd2c2f956bd497d7a` |

Both are filed in `10_PAPERS` as ICCA notices with the same file IDs. The original TU Wien reports remain unconfirmed. The 1991 notice describes the knowledge–search–lookup tradeoff. The 1994 notice reports KPKP validation and a rule inspired by Réti. The validation procedure and the rule's operational conditions are studied from the held 1992 and 1995 full journal articles.

### Experiment

[Audit code](../harness/c3x_030_s4m_r3_kpkp.py) compares a simple baseline with local Syzygy lookup. The baseline maximizes the difference between the two pawns' remaining single pushes to promotion, ignoring king geometry, attacks, obstruction and checks. These two published positions are deliberately selected development counterexamples. The baseline is a new diagnostic and represents neither the six-rule Barth program nor Mephisto.

| Position | All legal root moves | Pawn-distance choice | Replies to that choice |
| --- | --- | --- | --- |
| Réti 1921, Barth 1995 Diagram 1 | Kg7 draws. Kg8, Kh7 and c7 lose. | c7 | Kb7 wins for Black. The five other legal replies win for White. |
| Barth 1995 Table 1, position X | All eight draw. | e7 | f4 draws. The five other legal replies win for White. |

The audit replayed all 12 legal root moves and all 12 legal replies after the two baseline choices. It checked that the maximum child WDL matches each probed root WDL, and that the minimum reply WDL matches each probed baseline move WDL, always from the root player's perspective. Syzygy WDL uses the stored table convention at a zero halfmove clock. The experiment reports only -2, 0, and +2 and starts from FENs with no preceding history. It uses two SHA-pinned WDL tables from python-chess commit `3516d7c6c0879af724c2855fac5a304a4ef40949` and queries them locally. The comparison does not compute optimal mate distance, rebuild retrograde tables, validate the historical solver, or test Stockfish causality.

The decisive information for the Réti move ranking is a single defensive reply to c7. In position X, the baseline still picks a WDL-optimal move, but it assigns an advantage that cannot guarantee a win. A further comparison can measure the cost of finding a decisive refutation and the number of branches a human must inspect. Local tablebase WDL is a direct oracle for this finite domain. The historical rules still supply candidate concepts and are a useful explanation baseline. C3X can test whether its explanations remain faithful when the strongest opposing reply is substituted for a plausible alternative.

[Successful CI run](https://github.com/WhoSia/C3X/actions/runs/43368644473) reproduced the local JSON SHA-256 `662c633cf1fa9aa300c36ee69c364638f7f24e649d243b1e0417f2e0ee16d00e`. [Archived JSON](https://drive.google.com/file/d/1nBDd1ShL0YZbnxGI_HJ5kD6OeZwXmhub/view?usp=drivesdk).


## IX. S4-M/R4 · Contrastive promotion replies

The [audit](../harness/c3x_030_s4m_r4_reply_contrast.py) reuses the two R3 development positions, replaying every legal Black reply to c7 or e7, White's immediate queen promotion, and every legal Black defense after promotion. Four WDL table files are SHA-pinned. All 12 queen promotions preserve the tablebase WDL of their parent position. The minima of all 58 legal defenses, grouped by promotion branch, agree with the promoted positions' WDL from White's perspective.

| Branch | Mechanism supported by the replay | White WDL |
| --- | --- | --- |
| Réti, c7 Kb7 c8=Q+ | Kxc8 is legal and leaves a winning king-and-pawn ending for Black. Kb7 alone among the six replies attacks c8 before promotion. | Loss |
| Réti, c7 h4 c8=Q+ | The promotion also gives check here. No legal immediate queen capture exists and every legal Black defense leaves a White win. | Win |
| Position X, e7 f4 e8=Q | The queen cannot be captured immediately. Among Black's four legal defenses only f3 preserves the draw. | Draw |
| Position X, e7 Ke1 e8=Q+ | This promotion gives check and every legal Black defense leaves a White win. | Win |

Across these selected branches the descriptive check-by-win counts are 3 (check/win), 1 (check/nonwin), 7 (no check/win), and 1 (no check/nonwin). Immediate queen capture identifies the losing Réti branch. It misses the drawing position X branch. The pawn advance f4 is relevant in position X because the subsequent advance f3 preserves the draw against the queen. A supplementary local probe after f3 found 22 drawing White moves and two losing ones among 24 legal moves. This probe is additional exploratory work outside the archived 58-reply audit.

The research implication is to evaluate explanations against outcome-changing legal alternatives at the same parent and require the claimed mechanism to survive replay. These fixtures establish counterexamples to check-only and capture-only explanations. They do not estimate human utility, generalization, or Stockfish causal mediation.

[CI](https://github.com/WhoSia/C3X/actions/runs/43380193627) and [Drive JSON](https://drive.google.com/file/d/118iCKtLk1muf0ZCF2DKls5Q7M982a_Z1/view) agree with local SHA-256 `d6d5defac5cb20638b96deb17b6f329dd9a0e1e7ac7b563d44d9f82f9e575ca7`.

The fresh Intake copy of the 1991 file (Drive ID `1OxaMgowTdUFoZklB9QNUfuH9jROYcYuV`) matches the SHA-256 of the previously filed one-page ICCA notice. The original TU Wien report remains unconfirmed.


## X. S4-M/R5 · Outcome collisions within matched legal replies

The [audit](../harness/c3x_030_s4m_r5_explanation_collisions.py) generates two cohorts of 256 locally legal KPKP board states with Black to move and a White pawn on rank 7. Generation selects boards using geometry and move legality before any table lookup. The analysis covers Black replies that leave the same straight White queen promotion legal. It excludes R3 historical cases and their board symmetries, and deduplicates within and across cohorts by horizontal reflection. The two fixed-seed cohorts cover Black pawn ranks 4–6 and 2–3. The second cohort and additional counterplay features were explored during this round.

Within each parent, compare pairs of eligible Black replies with different Syzygy WDL after White promotes. A collision occurs when the feature vector is identical across such a pair. The first cohort has 1,742 eligible replies, 35 mixed-outcome parents, and 193 outcome-changing pairs. The advanced-pawn cohort has 1,596 eligible replies, 152 mixed-outcome parents, and 1,151 outcome-changing pairs.

| Nested explanation features | Ranks 4–6 collisions | Ranks 2–3 collisions |
| --- | ---: | ---: |
| Promotion gives check | 85 / 193 | 498 / 1151 |
| Add immediate queen capture | 8 / 193 | 437 / 1151 |
| Add remaining Black pawn pushes | 0 / 193 | 190 / 1151 |
| Add both king-to-Black-pawn distances | 0 / 193 | 57 / 1151 |
| Add immediate legal Black promotion and White attack on Black promotion square | 0 / 193 | 52 / 1151 |

For FEN `8/P7/8/8/1k3K2/8/p7/8 b - - 0 1`, the seven features coincide after either Kc3 or Kc4 and White's a8=Q. After Kc3, Black's Kb2 is the sole drawing continuation among 12 legal moves. After Kc4, Kb2 is unavailable and all 11 legal defenses lose. The audit replays these moves and probes all 23 defenses. The case was selected after observing the stress cohort. The result motivates explanations that retain the opponent's concrete resource and a legal contrast in which that resource disappears.

Adding features can mechanically split buckets. Collision counts are descriptive and the pairs share parents. The experiment establishes counterexamples to feature sufficiency on these boards. It neither estimates performance on human games nor identifies a Stockfish internal causal mechanism. The comparison covers the stipulated queen promotion and the stored Syzygy WDL convention. Board legality checks do not reconstruct game histories. The S4-H2 holdout is outside this experiment.

[CI replay](https://github.com/WhoSia/C3X/actions/runs/43381335802) · [Full Drive JSON](https://drive.google.com/file/d/1DNwNUy3gBASDvJCmIw8cKzh4uzPlHb16/view). Local and Drive readback SHA-256 `72412de28a0ecc89b08a846fb9575b0d1063b3efd4bcc3b7d5d8d707f0161282`.

The current intake listing and targeted C3X title search surfaced the existing one-page 1991 ICCA notice duplicate. Its SHA-256 was checked again. No new C3X original was identified in the reviewed intake results.
