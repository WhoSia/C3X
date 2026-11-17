# R20 P40 — A forced capture can carry an independent positional cost

[Protocol](C3X_030_R20_P40_INDEPENDENT_VALUE_PROTOCOL_20261117.md) · [frozen entries](../frozen/C3X_030_R20_P40_PLAN_ENTRIES_20261117.json) · [raw scores](https://drive.google.com/file/d/1HlDio9F50PkZpRtd71tMt35hZpa6MVGD/view).

| Case | Legal entries | Admits plan | Depth 10 open / admits | Depth 12 open / admits | Gap at depths 10 / 12 |
| --- | ---: | ---: | --- | --- | --- |
| 2.2 Rg1 …Rg8 | 40 | 2 | +91 / +91 | +116 / +116 | 0 / 0 |
| 2.2 Ke2 …Rg8 | 35 | 0 | +112 / unavailable | +112 / unavailable | undefined |
| 1.5 Qg5 …Qxa2 | 44 | 1 | +740 / +496 | +853 / +503 | 244 / 350 |

All 238 entry-depth searches yielded exact-depth point scores. They reproduced byte-for-byte in a second run. Scores are Berserk native cp from White's point of view. In 2.2 both maxima agree on Rxg8. In 1.5 the judge picks Nxa2 at both depths. That move captures Black's queen but lets Black move the named f6 knight with …Nd7. The only settled entry for the named knight is Qxf6. This cross-check reproduces the qualitative R19 zero/positive cost contrast under a different value signal.

The depth-budget experiment holds depth fixed per entry. Actual nodes vary by entry. Independent evaluation proceeds freely after the forced first move, so this pilot estimates the first-move restriction and leaves the value of enforcing all later plan choices open. The cases were selected for contrast after material results, and the 2.2 Ke2 branch has no defined restriction cost.
