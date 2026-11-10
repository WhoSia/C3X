# C3X 0.29 — P42/R28: Drive-Original Literature, BinProp Nearby-Negative Reproduction Slice, and Official Future-Source HOLD

**Evidence date:** 2026-11-10 KST. **No new C3X superiority or prospective result is promoted.** Source selection R24/R27 and reference labels R27 J1 were sealed before this unit. The true new scientific content is a negative methodological audit of simple predefined concepts on same-prefix reply branches, plus a real precommitted future source census.

## I. Original Research OS/Drive literature first — verified actual owned PDFs

The first authoritative reading priority is the user's original byte-held literature shelf, not arXiv web links. Drive search and **readable full-text extraction** of these PDFs were directly confirmed on 2026-11-10:

| Author / paper (original v1 where specified) | Original Google Drive PDF | Method relevant to C3X | Current C3X implementation ceiling |
| --- | --- | --- | --- |
| Cui, Ling & Ng (2026), *Communicating Chess Strategies in Natural Language*, arXiv:2607.11486v1 | [Drive source PDF](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) | Opponent ranked top-k recursive partial chess policy tree, verbalization and TEPP human/LM evaluation | R27 original source reproduces recursive tree selection for two opponent layers ONLY |
| Press & Golubev (2026), *Explaining Chess and Go in Natural Language* (BinProp), arXiv:2610.23166v1 | [Drive source PDF](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view) | Binary chess motifs selected for discrimination; **nearby negatives retain positive trajectory early moves but replace a later move with a disadvantageous one**, reducing brittle spurious motifs | R28 applies eight manually predefined board predicates to 12 same-prefix pairs, NOT LM motif search, 200k corpus, or the original full metric |
| Bhaskar, Cheng & Chen (2026), *Language Models that Play Chess and Explain Their Moves* (QUEEN), arXiv:2610.03695v1 | [Drive source PDF](https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view) | Silent expert chess encoder + language decoder, iterative candidate move explanation distillation | Architecture/evaluation donor only; no 4B training done |
| Parfenova (2026), *Do Chess Explanations Reflect Model Decisions?*, arXiv:2609.22245v1 | [Drive source PDF](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view) | Move-name masking, move recovery, plausible mismatched explanation controls, and token preferences | Future masking/foil control; no complete decoder evaluation yet |
| Spinnato (2025), *Towards Piece-by-Piece Explanations for Chess Positions with SHAP* | [Drive source PDF](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view) | Original piece-based static attribution contrast to stronger dynamic causal origin | Not yet replicated |
| Hebbar, Sheng, Oh & Viswanath (2026), *Hallucinations on the Board* (ACT-Eval), arXiv:2608.04240v1 | [Drive source PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) | Tool-based factual audit of chess explanations | Future legal/claim evidence verifier, not implemented here |

**Citation protocol now adopted:** Before a new reference enters C3X academic text, search Drive by **arXiv ID, original title, surname, file folder**, read the owned original if accessible, embed its exact Drive file URL and version, and distinguish what is implemented. If absent from Drive search, retain external locator only as secondary and place an explicit non-held row in the table at the **end**. Drive search index hit from citation inside another PDF/chat archive is NOT evidence that the cited primary PDF itself is held.

## II. R28-M1: original BinProp nearby-negative insight implemented as an explicitly incomplete fixed-predicate test

**[Actual native historical-artifact replay SUCCESS #42739498233](https://github.com/WhoSia/C3X/actions/runs/42739498233)**. Python 3.12 with `chess==1.11.2` ONLY in isolated GitHub runner. No Stockfish/Berserk search this unit. The R27 genuine source tree JSON SHA `f41e96bbf598aa824e65467cd1f1c782674aa275460211ce02b68f6eff1d4d5e`, R27 J1 independent judge JSON SHA `9844ebb1cae67d1af82c19696c8037ab53ca46b602ea44cdd66fc02d32ee27b7`, full historical game source and prediction receipt SHA all verified again before score join.

- R27 tree has **4 roots × 3 first opponent branches × 3 second opponent branches = 36 four-ply leaf histories**.
- Each first opponent response + first own move is an identical legal prefix for 3 alternate second opponent/own continuations, hence **12 groups of 3**. Within each group the depth16 independent Berserk **highest original-mover-cp** leaf is an exploratory positive, the lowest is its **nearby negative**. All 12 had measured ≥10cp score gap. Labels come from the frozen judge, but the **eight features were hardcoded before the new feature evaluation** and never fit to the new scores.
- Eight human-coded state predicates, root-player perspective: material ahead, material not behind, bishop pair, rook on open file, rook on semi-open file, passed pawn, opponent king currently in check, and still having a queen. A weak positive-true/negative-false separation tests whether a motif holds in a good leaf but not a matched poor leaf.
- Observed 12-pair separation counts: **rook on open file 3; bishop pair 2; material ahead 1; the other 5 each 0**.
- JSON SHA256 `c8768b6ac02e62548a61e87f18bfa4d9406136316da9ae81ee296867aa2433e4`. Code [audit](../harness/c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit.py), [contract tests](../harness/test_c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit.py).

**NEGATIVE SCIENTIFIC INTERPRETATION:** These coarse, piece/board-level static predicates fail to distinguish most of the actual independently valued matched continuation pairs in this small historical sample. This is NOT a refutation of BinProp's original LM-discovered, evaluated concepts. It suggests we should investigate *temporally evolving, source-computationally observable plan properties* rather than endless manual static-feature enumeration.

## III. R28-M2: deliberate tiny cross-game model selection and exposure warning

**[Pure-stdlib CI SUCCESS #42739855842](https://github.com/WhoSia/C3X/actions/runs/42739855842)**: no chess package or engine installed. Source M1 SHA checked before execution. In each direction learn a single feature and orientation by maximizing matched-pair separations on 6 groups from one historical event; evaluate the frozen rule on the other 6 groups. Features and labels were already known before this study and both historical events selected adaptively — **this is diagnostic, not a fresh independent holdout**.

| Train event | Selected fixed feature | Train separation / six | Other event separation / six |
| --- | --- | ---: | ---: |
| Cerrado | Bishop pair | 2/6 | **0/6** |
| Sahel | Rook on open file | 2/6 | **1/6** |

Source JSON SHA `e70cd19635878aba4ddf785afc4903b283a96f145200fdb1256975c4e79155df`. Code [pure stdlib transport](../harness/c3x_029_p42_r28_m2_nearby_negative_cross_game_transfer.py) and [seven tamper/anti-leakage tests](../harness/test_c3x_029_p42_r28_m2_nearby_negative_cross_game_transfer.py).

**NO p-values, no generalized performance inference**, only a tested reason not to over-invest in brittle frozen hand-authored motifs on these two worlds. There is no evidence that the original engine's computation represented or used the predicates to choose the original candidate root. Same-world causal-semantic mediation is STILL HOLD.

## IV. R28-C0: authentic previously precommitted November 9 Lichess source, scientifically proper HOLD

The R24 previously preregistered official source [Lag dm 2026, Round3, Lichess](https://lichess.org/broadcast/lag-dm-2026/round-3/sbfCtgNj), identifier `sbfCtgNj`, with eight final legal standard games ≥60 plies sorted by SHA256 of the entire canonical mainline UCI and first 30 plies position frozen before engine inspection. The original rule MUST NOT be revised after observing outcomes.

Lichess's [official API](https://lichess-org.github.io/api/) documents `GET /api/broadcast/round/{broadcastRoundId}.pgn`; R28 executed the corresponding precommitted round URL from a GitHub Actions source-only runner, not from Chat and without any engine analysis.

**[Actual original official HTTPS PGN acquisition and strict freeze #42740235638](https://github.com/WhoSia/C3X/actions/runs/42740235638)**:
- Raw response **52,773 bytes**, SHA256 **`e1e2e7cb87055b48e89854c12a40d9dcecfe1a514e678768280ab24c76b5a2ff`** (observed runner output).
- Original R24 strict legal and result/source provenance selector admitted **only 7 eligible complete games**, whereas **8 are required** by frozen rule. Thus source freeze stage intentionally **FAILED/HOLD** `HOLD_TOO_FEW_COMPLETE_STANDARD_LICENSED_GAMES 7 7`.
- The raw bytes remained in an ephemeral GitHub runner and were NOT uploaded to the public GitHub artifact. Public artifact contains source fetch SHA receipt, legal census/status, and original rule. **Drive raw-byte custody is NOT established.**
- This run is NOT a prospective eight-game cohort, NOT success of a future transfer test, and NOT evidence that official round has finished; PGN can continue to change while a broadcast is live. Preserve raw SHA and acquisition time to distinguish versions.
- Source-only workflow [R28-C0](../.github/workflows/c3x-029-p42-r28-C0-official-future-source-only.yml) can recheck the exact same registered round, but must retain target eight and all other declared rules. Archive original raw to Drive (authenticated receipt + verified SHA) before any later promotion, and audit complete past source exposure.

## V. RAVEL scientific decision

**RETAIN**: actual copied/verified Drive papers, source-only separated native prior-art tree, real independent fixed leaf judgments, original BinProp-inspired *nearby negative* falsification idea, clean source-first future round provenance record. No local Chat python-chess installations.

**REJECT**: equating eight coarse static motifs with a full BinProp replica; equating two exposed games with prospective generalization; changing 8-game freeze to 7 after observing official source; calling 7 games a completed source freeze; claiming Drive custody from a runner SHA; assuming a nominal-depth cp score is a true minimax value.

**NEXT**:
1. Source C: Recheck original same round after completion, no retroactive protocol change. Preserve raw bytes on Drive, confirm original-source URL/census/PGN and archive collision exclusion prior to engine/judge labels. If round never has eight eligible games, precommitted cohort fails — record failure; use a DISTINCT genuinely preregistered next round, not a silent substitution.
2. B/E: Use full Cui-style two-opponent-level source strategy and BinProp-inspired *temporal, counterfactual matched trajectory* concept probes, but only on new positions with heldout concepts, not endless tuning on Sahel/Cerrado.
3. A/D/F: On that exact original full legal history, link measured source search/NNUE activation and a causally intervened original root choice to the independently judged frozen future-plan property. Sham, non-contact and original alternative root controls are obligatory.

## VI. Drive 미보유 문헌 표 — 색인 검색 기준

| Candidate previously cited | Search terms checked | Verified present original PDF? | Resolution |
| --- | --- | --- | --- |
| SARFA (arXiv:1912.12191) | `SARFA`, `1912.12191` | **Not found in Drive index**; search results were *mentions inside other PDFs*, not original SARFA PDF | **Drive 미확보(색인 검색 기준)**; obtain original before substantive academic source claims |
| Sandmann et al. (arXiv:2508.21380v4) | `Sandmann`, `2508.21380` | **Not found in Drive index**; only research chat mentions / unrelated PDFs | **Drive 미확보(색인 검색 기준)** |
| Ciancarini & Pareschi (arXiv:2609.18286) | `Ciancarini`, `Pareschi`, `2609.18286` | **Not found in Drive index**; only embedded mentions / unrelated PDFs | **Drive 미확보(색인 검색 기준)**; verify bibliographic identity before citing further |

