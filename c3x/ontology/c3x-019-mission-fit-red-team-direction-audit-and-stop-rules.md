# C3X 0.19 — Mission-Fit Red Team: Research Direction, Drift Risks and Stop Rules

**Phase audit 2026-10-10, before February native outcomes.** The goal remains C3X: explain, in a falsifiable and eventually communicable way, how counterfactual differences in a chess engine's search lead to a DIFFERENT final root choice. Source search-memory provenance is an instrument toward that goal, not the primary product.

## What is established, what is not

**Established with source/cold runs:** Stockfish16 frozen physical TT write-epoch tracing, actual source save guard, first-reader intervention causing a later physical writer version overwrite, selective restoration of an old-version V targeting condition, exact January 31-arm remeasurements where 28/29 stale-tag selected later nodes executed a real TT score-as-eval assignment and the final case executed an actual TT main-cutoff return. The unrescued engine often still consumes the TT numerical score.

**Not established:** exclusive natural TT-mediated root-bestmove shift, path-invariant two-node modularity, ability to transport the December one-source AND-OR bestmove law to new games, equivalence of source procedural root-call IDs across perturbed searches, or engine-independent laws of chess explanation.

**Hard negative facts that remain:** January prospective J2/J3/J4 bestmove predictions FAIL; December prospective deep-reader prediction D2 FAIL; P1 original unbounded writer-selector negative control R5 FAIL. Post-hoc conditional machinery cannot edit these historical statuses.

## Main traps

1. **Observer-target tautology (observed and reproduced):** A V reader_block depends on our shadow epoch and is not the native engine's own reading event. SHADOW_ONLY reverses old-epoch gate status with no TTEntry byte restoration. Required repair: always obtain post-assignment or actual cutoff return witnesses separately, and use deliberate raw/shadow mismatch controls.
2. **Proxy multiplication:** Treating TT epoch, accepted writer serial, node depth, root call, alpha margin and final score as ever-richer correlates may produce impressive but untestable models. Required repair: one risky forecast on an independent cohort for each new mechanism, else retain exploratory label.
3. **Outcome-driven target selection and researcher degrees of freedom:** Never select a new source reader within the same 16 games after a predicted failure; record NO_PAIR, NO_CONTACT, CENSORED and held cases in denominators. Duplicate STRICT/BROAD physical cases may not be counted as independent.
4. **Researcher-induced control-flow:** Logging, write suppression, old TTEntry reinstatement and sidecar manipulation are artificial transformations; cold UCI noninterference and contact evidence are necessary, not sufficient. Identical full final UCI under alternate instrumentation is a control, not a mechanical causal pathway proof.
5. **Mission drift:** A beautiful source-level cache-version result without a root candidate competition, negative control, or human-understandable explanatory criterion is systems reverse engineering, not yet C3X chess-choice explanation. The TT writer-identity project should be tagged as **instrument validation** until it predicts something about final search/root outcomes.

## Operational decision gates

**Gate G-A:** If independent February value-survival forecast F19.3 passes, classify writer-epoch change as potentially **semantically equivalent for native TT score use**, not destroyed native consumption. Focus C3X's core theory on changes in TT bound/depth, pruning/early-cutoff, alpha-beta windows, root candidate competition and true final choice.

**Gate G-B:** If F19.3 fails, preserve failure; distinguish genuine missing probe, different key, TT miss, bound ineligibility and TT early cutoff through exact source native return traces. Do not retarget.

**Gate G-C:** A root-choice explanation requires (i) an independently selected previously unrevealed game, (ii) an intervention on source physical search control, (iii) observed source-local branch/value change, (iv) downstream root competition crossing, (v) same output under negative controls, and (vi) an alternative mechanism explicitly falsified. None of those stages may be silently substituted by an old-version V gate.

**Gate G-D:** Second-engine structural transport requires comparing actual native TT/cache semantics and source branches; do not start with the assumption that another engine implements SF16's TT value-as-eval override.

**Phase strategy:** keep 0.19 active for provenance measurement and failures, but make source findings serve the C3X final chess explanation goal. Retire a TT-only physical-epoch root causal law from the center of the program if independent root-level effect is repeatedly absent. Preserve the resulting theory of measurement identifiability as a genuine methodological result, not as a substitute for the original question.
