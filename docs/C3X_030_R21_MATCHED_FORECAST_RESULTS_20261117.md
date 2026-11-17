# C3X 0.30 R21 — Matching candidate pairs and replies

[Selection protocol](C3X_030_R21_STABLE_ROOT_SCREEN_PROTOCOL_20261117.md) · [selection freeze](../receipts/C3X_030_R21_SELECTION_FREEZE_20261117.json) · [pre-judge forecast freeze](../receipts/C3X_030_R21_FORECAST_FREEZE_20261117.json).

The official TCEC S28 Division P PGN contains 224 games. The selector blocked 452 historical first-12-ply prefixes from the four named inputs. Before reaching eight accepted pairs, it skipped 32 games for a prior or within-run opening prefix and screened 22 games. It reached 57 board previews. Of these, 34 had two preview entries but only one eligible score. Fifteen more pairs did not meet the signed budget-gap contract. Eight were admitted. Seven supplied two shared legal replies, giving 14 questions. This is a development sample with seven distinct games and seven distinct 12-ply openings.

| Reference | PV unrestricted rank | Public two-reply tree | Identical tree plus native trace |
| --- | ---: | ---: | ---: |
| Berserk depth 14 | 3/14 | 12/14 | 12/14 |
| Berserk depth 16 | 4/14 | 11/14 | 11/14 |
| Agreement at both depths | 3/13 | 11/13 | 11/13 |

Strict PV coverage was 1/14 (0 correct). Both source arms requested 48,000 nodes per candidate. In aggregate they consumed 672,504 PV nodes and 672,535 tree nodes. The native trace reported 17,866 root-candidate records in 28 complete leaf runs. Eight leaves had 422 events deeper than the last unbounded public report, and 16 events would update the root PV. Of those, 14 were at or below alpha and two were at or above beta. Zero passed the strict window. The R14 definition also admitted zero. Thus the supplementary trace arm made the same forecasts in all cases, and the experiment measures the benefit of conditioning the search on replies. It does not estimate gains when a usable trace update occurs.

Round 1.2 provides a counterexample to assuming the budget-screen rank transfers to each reply. The source's h4 led Qd2 by 13 and 9 cp in the two singleton searches. After …Qc7, Berserk depth 16 judged h4/Qd2 at +169/+88. After …Ne7 it judged +64/+144. The public tree recovered both directions. The wider [census](C3X_030_R21_COMMON_REPLY_CENSUS_RESULTS_20261117.md) tests the representativeness of these two replies.

One reference label changed with depth, and several stable point labels rest on small margins. The 13 agreement labels are conditional engine observations. The near-tie screen constrains only the Stockfish nominees and tested settings, and the forecast outcome is a reply-conditioned signed evaluation. It does not establish the best move against every opposing reply. The two questions per game are dependent. Source forecasts, selection, and judge results repeated byte for byte after stripping stdout time and NPS from the recorded tree runs.
