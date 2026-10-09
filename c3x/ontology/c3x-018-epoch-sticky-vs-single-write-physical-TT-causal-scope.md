# C3X 0.18 — Physical TT Writer×Reader Court: Exact Event vs Epoch-Sticky Class

Status: REPAIR COURT IN PROGRESS / scientifically OPEN. Frozen SF16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`.

## The first native factorial is *not* one-write mediation evidence

Native run [#37975111237](https://github.com/WhoSia/C3X/actions/runs/37975111237) SUCCEEDED and its source/result evidence ZIP SHA-256 was `162f2473821eeccdf09c5a6a9c2afdf0b5895c754cc4dd795fe7bfcbda0170f7`. Its W arm was an **epoch-sticky intervention**: after suppressing a writer, the slot-local write epoch did not increment, leaving later attempts at the same key/slot/epoch eligible for repeated suppression. The source reported **23 writer-block contacts in case #6** and **74 in case #8**, not one physical writer event. Neither result may be described as a *single writer's natural necessity*.

- #6 F bestmove `e4d6`; W `e4d6`, R `e4d6`. W affected score/nodes, R did not change reported UCI core.
- #8 F bestmove `h5g7`; W `e6h3`, R `h5g7`. W affected score/nodes and returned the historical O bestmove, but **74 writes were blocked**. R fired exactly one relevant qsearch consumption block but no measured depth12 core changed.
- In both, WR had W contact and zero R contact, so the combined arm does not identify a writer→reader interaction.
- Under OBS, #6 F had 8,969 consumed cutoff branches, #8 F had 5,009, with a matching full-key writer witness in the shadow table at these observed branches. This supports *physical provenance at the instrumented branch only*, not exhaustive TT usage or unique causal mediation.

## The repair

Source code revision [`30416965`](https://github.com/WhoSia/C3X/commit/304169650b6ee91ca73284749c2b7cd078f48424) adds a resettable `writer_blocked_once` gate: W/WR now suppress only the **first source-exact matching payload-write attempt** per cold engine process. Independent run [#37975353863](https://github.com/WhoSia/C3X/actions/runs/37975353863) must be checked before promoting any one-write result.

Added falsification controls [`1509954f`](https://github.com/WhoSia/C3X/commit/1509954ffcb498d29c6be902896122a76362717c): an impossible 64-bit-key decoy (W and R), cold repeated, must show zero contact and exact F-arm final UCI tuple. The target was selected by a predeclared first F-only, exact full-key cutoff-consumer rule *using the same experimental data*. It remains exploratory.

## Non-identifications retained even after single-event W PASS

1. A writer may be followed by other writers at the same physical slot; after suppression the *new* epoch ordinal may designate another physical event. Event identity is not guaranteed across arms simply by equal counter values.
2. W suppresses the entire accepted `save()` call, including potential move16 update, not solely TT score/bound. An output change is not proof the score path alone mediated it.
3. A blocked qsearch early cutoff need not change the final root choice; other TT uses (move ordering, static eval, ProbCut, depth decisions) remain possible mediators.
4. Selected #6/#8 were historical bestmove flips; the TT candidate was selected within treated F. No independent pre-registration across new games; no full process generalization.
5. A successful rescue of one output or candidate return would prove a local replacement capability, not an exclusive natural writer→reader path.
6. Frozen standalone FEN loses prior game repetition history.

## Suggested next attack

After the source-exact W/R/WR + impossible-key controls pass, identify **first divergence in a TT writer-consumer path whose read is actually applied**, then preregister its independent replay and operator contact on a fresh split before claiming necessary mediation. Seek exact entry-payload rescue and matched unrelated-writer controls, but do not smuggle them into the first factorial verdict.
