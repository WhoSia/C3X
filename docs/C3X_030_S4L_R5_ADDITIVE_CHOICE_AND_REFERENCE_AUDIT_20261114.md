# C3X 0.30 S4-L/R5 — Additive Choice and Reference Audit

## R4 reanalysis

The input is the R4 replay result JSON (SHA256 6c4dbdc8d125db41597ef570da25b5d7d0bc3d813d19ffd19a99d323fbe58faa). No new engine calls. For each position, test whether scores Q_m(t,h)=a_m(t)+b_m(h) can make every observed winning move strictly highest on the 3x3 grid. Linear inequalities require a unit margin; scaling any strict fit on the finite grid preserves its winners and attains that margin. The candidate universe is all winners observed in that grid. All eight grids are feasible, including all three with both axes active. This is a descriptive existence test on categorical choices. It does not identify engine scores or validate the model on a new game.

Fitting only the sham row and column, using only their winners as candidates, yields sets for four masked-by-masked cells per position. Coverage 31/32, with 8 three-move sets (both Italian cases) and 24 singleton sets. The sole miss is London ply8 second/second: Nd2 is outside the anchor winner vocabulary (Ne5). Thus coverage reflects broad sets in both informative Italian cases and five constant cases, with a discovery failure in London. The procedure was designed after observing R4. An actual forecast must fix candidates before opening outcomes.

A strict two-move checkerboard A/B, B/A is infeasible. Summing the two A-over-B inequalities on the diagonal and the two B-over-A inequalities off diagonal cancels every score term and leaves an impossible positive margin. The implementation rejects that synthetic control. R4 one-hot mixed differences detect dependence of the selected move on both axes. R5 tests a stronger claim about what kind of score function could generate that dependence.

## Upstream SARFA replay

Pin author code at [32e5725](https://github.com/nikaashpuri/sarfa-saliency/blob/32e5725648498326d6a113e18d92dc7103402bc9/sarfa_saliency.py) and compare with [paper section 2](https://openreview.net/pdf/5cd12e00b50dbcef455a7afc34d173738a72e999.pdf) and C3X's log-domain kernel. The author function supplies perturbed actions as its first KL helper input, then uses entropy(original, perturbed). The paper uses perturbed || original. On 256 seeded shared-support fixtures, max absolute differences were 2.22e-16 for specificity, 0.2869798687 for relevance, and 0.1154904858 for saliency. Independently evaluating both KL directions with scipy reproduced the two relevance calculations to 3.34e-16. Existing C3X SARFA and BinProp contract suites passed 20/20 local tests. The SARFA replay uses synthetic scores and no human performance measure.

## Next discriminating experiment

Prespecify all legal root moves as the candidate universe, collect comparable candidate scores with a frozen search protocol, then test additive feasibility and rectangle contrasts on candidate score *gaps*. A forced-root score is a separate computation from an ordinary joint search, so preserve native root receipts and report bound censoring. Use a new game-disjoint set to evaluate coverage and sharpness of forecasts. A nonzero contrast on measured gaps would challenge score additivity at that measurement site. Chess strategy value still needs an independent evaluator.

[Prior art index](C3X_030_PRIOR_ART_IMPLEMENTATION_INDEX_20261114.md) · [Additive test](../harness/c3x_030_s4l_r5_additive_choice.py) · [SARFA comparator](../harness/c3x_030_s4l_r5_sarfa_reference.py) · [Run outputs](https://drive.google.com/file/d/1xOBBzPMS4_Z9enB0q7vZiANxWPlIMxS_/view). Output ZIP SHA256 d48336cde88be159f149c8871d6e733dd4c88efc3845003d519d8103dc1d68eb.
