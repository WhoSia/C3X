# C3X 0.30 — Adaptive Goal Test and Direction Audit

2026-11-13 KST. Development case, no native engine searches or holdout access in this run.

The [C3X 1 charter](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view) starts with the learner's question about why a move is slightly better than an alternative. Its 0.2 design distinguishes near superiority from search noise. The [preceding audit](C3X_030_CERRADO_QUEEN_PAIR_AUDIT_20261113.md) makes Cerrado an unresolved-rank negative control. Local tactical reversals in World 1 diagnose response dependence. Stable marginal superiority and learner benefit require separate evidence.

## Bounded chess test

From the preceding Cerrado FEN and 16.Bxf6 gxf6, track the black pawn initially on c4 across each legal reply to 17.Qc2, Qe1, e3 and h3. Enumerate all legal White first moves. For each, require the outcome against every legal Black response, allowing White's second move to depend on Black's first response. At the deadline after Black's reply to White's last move, require the original c4-pawn to be captured. In the guarded arm additionally require White-minus-Black material to be at least its pre-candidate value of -1, using pawn 1, minors 3, rook 5 and queen 9. This is a material guard and a local goal, with no positional or engine score claim. Earlier terminal positions are scored on the same predicate. No claims about automatic draw or repetition in the bounded tree.

| Candidate | Legal replies | Capture, 1 White move | Guarded, 1 | Guarded, 2 |
| --- | ---: | ---: | ---: | ---: |
| Qc2 | 31 | 31 | 2 | 6 |
| Qe1 | 31 | 31 | 2 | 7 |
| e3 | 31 | 31 | 0 | 7 |
| h3 | 31 | 31 | 1 | 6 |

At two White moves the guarded goal succeeds for both queen moves after Ba4 via Qxc4/Rxc4, and after c3 via dxc3 for both, with Rxc3 also admitted for Qe1. Neither succeeds after Rfd8 or Rb6, prominent defenses in the prior engine search. The 6–7 count provides no candidate-specific advantage against those defenses. Six reply states were independently replayed with uncached enumeration. 124 root-reply rows were checked against a separate one-move run and guarded results were verified as subsets of unguarded results.

[Code](../experiments/c3x_030_cerrado_adaptive_goal.py) · [raw outputs and cross-check](https://drive.google.com/file/d/14q0roZDQFl0kUBGbFNC4kB3CaXEgdDn5/view). ZIP SHA256 `14eac6e326881b75395bc9c3acc7ba0c34a8db1794d4db6e7731616789635226`. python-chess chess 1.11.2, module SHA256 `1fde6a8e932508d14b31f6a584497b49c2969fc3c7cdc675347f819f0d667a5b`.

## Direction verdict

- Retain outcome-defined adaptive plans and matched replies. The current implementation verifies reachability of a declared outcome. Total reply coverage should be accompanied by explicit strong-reply witnesses.
- Close Cerrado as a calibration and falsification case for the tested immediate d4 and short pawn-removal explanations. Its root order remains unresolved. Native engine instrumentation can address a separate computation-level claim once a chess-level contrast has been identified.
- Next empirical gate: select newly sourced games by a frozen ranking-agreement rule across budgets and two engines, preserving game-disjoint evaluation. Predeclare a concrete outcome, positive and negative witnesses, and a stop for ranking instability. Compare an outcome-conditioned policy with static features and principal-variation commentary on the same cases. A learner-facing endpoint is successful choice or forecast on a new defense. Generalization, learning benefit and engine-choice causality remain open.
