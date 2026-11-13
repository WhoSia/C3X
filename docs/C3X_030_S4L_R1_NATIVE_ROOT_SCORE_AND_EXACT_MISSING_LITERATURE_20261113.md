# C3X 0.30 — S4-L/R1 Root Score Source Receipts, Independent Audit, and Exact Missing-Primary Literature

Date: 2026-11-13 KST. Conversation **C3X 33**, research version **C3X 0.30 unchanged**.

## Inherited question

S4-J/K showed 3/16 source TT two-hit-root bestmove changes on 8 development FENs (4 researcher-authored game histories), but all uniquely shared TT-early-return candidate states had identical return values. This did **not** disprove a TT-to-root mediator: those source logs captured only a single targeted TT-return path, not the complete root score updating process.

## New S4-L native experiment — actual Stockfish16, not simulated data

The anchored source patch [`c3x_030_s4l_root_score_patch.py`](../harness/c3x_030_s4l_root_score_patch.py) augments the pinned Stockfish16 upstream commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` with **read-only** events immediately before each root `RootMove& rm` score update:

- Actual `root_move_raw`, root child `value`, prior `bestValue`, `alpha`, `beta`, `depth`, `moveCount`, and predicates `value > bestValue` and `moveCount==1 || value>alpha`.
- Source ID for actual UCI `go` epoch (1 or 2), with root receipt limit **512 per epoch**, while the separately counted **actual root-score event total** continues after the receipt limit.
- Existing S4-K target-key TT early `return ttValue` source totals are preserved; no claim that root score and TT mask refer to the same invocation merely because they occurred in the same trial.

The new strict [`c3x_030_s4l_root_receipt_court.py`](../harness/c3x_030_s4l_root_receipt_court.py) rejects malformed epoch boundaries, fake root best-update predicates, invalid alpha-beta windows, fabricated receipt counts, and missing events.

### Native evidence

[S4-L GitHub Actions #43359776211 — SUCCESS](https://github.com/WhoSia/C3X/actions/runs/43359776211).

- **48 new real engine searches**, **576,619 native nodes**, **6/6 synthetic source-contract tests PASS**.
- True original Stockfish16 versus same-binary sham versus same-binary two-hit physical target TT masking; 8 FEN snapshots from 4 already-inspected researcher-authored development games; two consecutive 12,000-node-budget UCI `go` searches for each arm. Same pre-registered original S4-H2/R2 target TT keys; the **8-game holdout was not touched**.
- Original–sham comparison was identical across bestmove, depth, nodes, score, PV. Two-hit versus sham changed bestmove **3/16 times** (Italian ply10 twice; London ply8 once). Controls and original frozen protocol remain intact.
- Original native output JSON SHA-256: `a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9`.
- [Drive raw original native ZIP](https://drive.google.com/file/d/1MD0D9GEr_MA3Qqce8Z_wBogYjGMM02jb/view).

| Actual root score update-site observations | Sham | Two-hit |
| --- | ---: | ---: |
| Total root evaluations encountered at source | **6,959** | **7,130** |
| Fully logged score receipts | 6,488 | 6,727 |
| Not individually logged because of 512 per-go cap | **471** | **403** |
| Saturated UCI go epochs (of 16 each arm) | 5 | 5 |
| Logged `value > bestValue` predicates true | 365 | 383 |
| Independently counted targeted TT early returns | 45 | 48 |

**Interpretation:** TT intervention changes root-level search event *counts* in this fixed development setup. There are 171 additional root score-processing events in the two-hit condition, but these are not 171 independent effects and are **not** evidence that the targeted TT entry itself was the causal intermediary in the observed root changes. The separate engine runs cannot be aligned by event ordinal, and their root move identity, depth/window, warmed TT history and branch context require an additional state-level matching protocol.

### Failures and reproducibility

First source-anchor CI [#43359619719](https://github.com/WhoSia/C3X/actions/runs/43359619719) failed in tests because it required an obsolete uninstrumented `RootMove` source site. A second interrupted patch attempt [#43359748390](https://github.com/WhoSia/C3X/actions/runs/43359748390) exposed accidental literal `\\n` text in the generated patch file; corrected the source bytes and obtained the successful CI. Both failure records are preserved, not deleted.

[S4-L/R1 independent original-archive audit #43360178653 — SUCCESS](https://github.com/WhoSia/C3X/actions/runs/43360178653): **0 new engine searches**, 7 synthetic fraud/regression tests pass. Earlier separately archived original JSON is SHA-verified, all per-epoch real score totals, 512 receipt caps, value-update predicate flags and root-choice results recomputed. Independent re-audit raw JSON SHA256 `b6cef23e215ac4994dc08b665a9e3a38e07dab923f5bf46a15fa80586efa30c3`; [Drive R1 audit ZIP](https://drive.google.com/file/d/1p6EpfDp4JW8WTSO5fp4vyd2s2nOQwDz-/view).

## Scientific verdict

- PASS: actual source-native root score update **events and exact per-go event totals**, source TT cutoff counts, original–sham noninterference, independently re-audited original bytes.
- HOLD: the specific TT masked invocation returning value across *different arms*, true child→ancestor/root *counterfactual* mediation, root score event alignment, independent 8-game holdout, prior C3X 0.29 7/8 prospective cohort, comparison with SARFA/SHAP/BinProp/human tutor.
- Next S4-M: first **separate native epoch-trial logs from transient TT state**, then reconstruct candidate matching root move with depth/window, do not use ordinal cross-arm. Include root-branch bestmove rank changes, unknown non-logged events and qsearch boundaries. Consider raising receipt cap only when profiling confirms read-only logging preserves original–sham numerical outcomes. Do not promote mediation until intervention, return, parent update and root decision differences are causally supported.

## Exact original publication inventory — still **NOT confirmed owned** in Drive

The titles/volumes below are confirmed on publishers/bibliographies, but a targeted 2026-11-13 Google Drive search found **related works, NOT these exact original full texts**.

| Priority | Exact primary original | Bibliographic locator and legitimate routes | Drive custody verdict |
| --- | --- | --- | --- |
| P1 | Herbeck, H. & Barth, W. (1996), *An Explanation Tool for Chess Endgames Based on Rules* | ICGA Journal **19(2), 75–82**, DOI **10.3233/ICG-1996-19202**, publisher [issue](https://journals.sagepub.com/toc/icga/19/2); author manuscript / institutional interlibrary loan / publisher subscription | NOT CONFIRMED (other endgame explanation works present) |
| P1 | Björnsson, Y. (2024), *Chess and Explainable AI* | ICGA Journal **46(2), 67–75**, DOI **10.3233/ICG-240256**, [publisher](https://journals.sagepub.com/doi/10.3233/ICG-240256); institution / author archive / library | NOT CONFIRMED (Pálsson & Björnsson ECAI 2024 and Pálsson PhD ARE OWNED but are distinct) |
| P2 | Kopec, D. & Bratko, I. (1982), *The Bratko-Kopec Experiment: A Comparison of Human and Computer Performance in Chess* | *Advances in Computer Chess 3* (ed. Clarke), Pergamon, **57–72**, ISBN 0-08-026898-6, DOI **10.1016/B978-0-08-026898-9.50009-7**, [publisher abstract](https://www.sciencedirect.com/science/article/abs/pii/B9780080268989500097); library/ILL | NOT CONFIRMED (owned periodical test summary and Kopec 1982 PhD are different works) |
| P3 | Demura, Y. & Kaneko, T. (2024), *Initial State Diversification for Efficient AlphaZero-Style Training* | ICGA Journal **46(2), 40–66**, DOI **10.3233/ICG-240255**, [publisher](https://journals.sagepub.com/doi/10.3233/ICG-240255); author archive / institutional library | NOT CONFIRMED (topic is **training diversity**, indirectly relevant to representative cohort design, not directly to chess move explanation) |

Exact publisher DOI confirmed online, but publisher abstracts are not full texts. The publisher offers access, not proof that rights/bytes were acquired. The Google Drive search result is not a cryptographically complete Drive census; this is precise **unverified exact original custody**. No unauthorized publisher text was copied.

**Already held (do not request):** Puri et al. SARFA, Fritz & Fürnkranz 2021, Press & Golubev 2026 BinProp, Spinnato 2025 chess SHAP, Hammersborg & Strümke 2024. Gadwal, Greer & McCalla (1993) **author manuscript HELD**; typeset publisher collation still pending.

C3X 0.30 is unchanged. All repository writes performed under `WhoSia`; CI configured read-only and does not commit.
