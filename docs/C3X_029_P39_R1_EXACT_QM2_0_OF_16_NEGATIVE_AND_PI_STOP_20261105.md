# C3X 0.29-P39/R1 — Rule-Complete Adversarial Q_M2 Actual Negative Result

**2026-11-05 KST. Actual original-source native read-only chess-law computation PASS. Q_M2 positive prevalence 0/16. METHOD-DEVELOPMENT ONLY / P39 heldout explanatory superiority NOT TESTED.**

## Preregistered definition and chronology

Prelabel pre-registration human GitHub commit 9b69473922f98fc02230fc06d3ab2d72d3066b36 fixed Q_M2(s,m): immediate mate after m OR for every legal opponent first reply r exists legal mover reply u that checkmates immediately. First original source P37 cohort and both previously exposed Stockfish24k candidate UCI per game preserved: eight separate previously exposed events, two frozen moves each, total 16 worlds. No model generated new predictions; old C3X plan models not scored on these labels.

## Verified original result

[Read-only original GitHub Actions run 41987784245](https://github.com/WhoSia/C3X/actions/runs/41987784245) **SUCCESS**, including six formal synthetic tests, pinned source/prediction JSON SHA gate, full 30-ply source legal-history + FEN + candidate checks, production rule complete labels and independent certificate replay, artifact upload. Original archived ZIP SHA256 `10c43294dae6a67af5b5ce4a19c397a16c4cb01725f5009031fbc41b34ba3531`. SHA members from original archived manifest.

Actual verdict **Q true 0, Q false 16, technical hold 0**. Every negative has a concrete legal opponent first reply after the selected root and the **complete set** of legal mover responses after that refuting opponent move, checked none produces checkmate. Importantly the negative requires only ONE such counterexample rather than enumerating every opponent reply; thus we do NOT misstate this as 16 searches exhausting every opponent response. The positive branch, if it existed, would require all opponent replies to have a checking-mate witness. No candidate root was substituted, no scoring discarded.

## Strategic failure and scope

This Q is a well-defined and independently chess-rule-verifiable tactical statement, and its negative is mathematically meaningful. But in the P37 frozen midgame sample it is uniformly FALSE and therefore **cannot rank alternative moves or discriminate a near-equal strategic preference**. This does not disprove general mate-in-two certificate methods, let alone C3X's long-horizon planning question; it means this outcome Q fails to be informative in these preexisting 16 worlds. Do not retrospectively mine other tactical tasks on these same positions and call the result prospective.

**PI verdict: NO-PROMOTION / GO-BACK-TO-HARD-QUESTION.** Next chess-level goal is a nontrivial independent-horizon opponent-conditioned strategic value question over multiple opponent replies, with a pinned reference, no model information leakage, game/event-heldout and fully cost-accounted strong Stockfish PV baseline. Hard tactical rules can serve as high-confidence calibration controls but must not become the central explanandum simply because they are easy to verify. The existing Ethereal v12.75 cross-engine branch P38 was TECHNICAL-HOLD and STOP under source registered gates; do not silently revive it.

## Evidence and custody

[GitHub preregistration](https://github.com/WhoSia/C3X/blob/main/docs/C3X_029_P39_R1_QM2_EXACT_LEGAL_ADVERSARIAL_CERTIFICATE_PREOUTCOME_20261105.md). [Executable exact legal verifier](https://github.com/WhoSia/C3X/blob/main/tools/c3x_029_p39_r1_exact_mate2_legal_certificate.py). [Verifier tests](https://github.com/WhoSia/C3X/blob/main/tools/test_c3x_029_p39_r1_exact_mate2_legal_certificate.py). [Read-only GitHub Actions workflow](https://github.com/WhoSia/C3X/blob/main/.github/workflows/c3x-029-p39-r1-rule-complete-mate2.yml). [Drive immutable original ZIP](https://drive.google.com/file/d/1vYyXyCAFlQ-ggB_qMXVty1uIcLJQtAGv/view).

Original previous P37 human-reply audit and its PV 4/6 vs C3X 1/6 remain independent research receipts; no rewriting past errors or negative labels. All commit authors WhoSia, GitHub Actions contents:read only, never github-actions[bot] author/push/merge/tag/ref changes; Notion scientific semantic source, Drive raw evidence, GitHub executable source.