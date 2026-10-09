# C3X 0.18 — Physical Target–Event Congruence and Source-Role Mediation

**Status:** ADAPTIVE FORMALIZATION AFTER THE DECEMBER TWELVE-GAME PROSPECTIVE COURT. Do not relabel the original preregistered D1. All forward claims must be tested on data selected after this formulation.

## Primitive objects and distinction

Fix a cold native chess engine process, root order policy, full game-state input, search depth and one actual TT writer `w`. A physical target triple is

`q = (full_64bit_Zobrist_key, TT_cluster_slot_index, slot_local_successful_write_epoch)`.

In a baseline observation, the bound-qualified search-score-as-evaluation reader visits of that physical target form an ordered set `R(q) = (r_1, r_2, ..., r_m)`. Each *event* has a source property vector `z(r) = (last_writer_serial, current_writer_serial, write_age_count, raw_bound, recursive_ply, root_candidate_native_move, root_call, window_alpha, window_beta, site)`. The key and slot identify the *carrier*; the read event identifies the *consumption occurrence*. They are not the same mathematical object.

For any predeclared property `P`, a selector `S_P` picks the first **passively observed** event `r_P` with `P(z(r_P))`. The original `V_q` actuator uses only `q`; it suppresses the next qualifying reader of that triple, potentially *before* `r_P`.

Define the **Physical-Target/Actual-Event Congruence Gate**:

`Congruent(P,q) = 1` only when the first actually suppressed source reader under `V_q` matches the selected passive event's causal role at the same source root call, recursive ply, bound class, and accepted-write age, with earlier prefix nondisrupted. Full64 writer identity, payload integrity and no shadow race remain mandatory. Numeric root-call counter equality is a necessary but not alone sufficient source-event equivalence after branch divergence.

**Conditional source-role attribution theorem (measurement logic, not a new chess law).** If a property-selected event `r_P` and the first actually suppressed event `r^*` differ, and the actuator cannot exclude `r^*`, then a categorical root outcome difference under `V_q` proves only that **intervening on the selected physical carrier** changed the outcome. It does NOT identify the specific role property `P(z(r_P))` as causally responsible. This is a non-identifiability statement under the existing actuator, not an assertion about all conceivable interventions.

Counterexample: the December #11 source `old` selector picks accepted-write age **90** at root call **9**; same full64-key/slot/epoch was first read at age **18**, root call **5**. The original V intervention changes bestmove **b2b3 → c1f4** but suppresses the earlier *age18* reader. Consequently `D1_OLD_ROOT=PASS` **as literally preregistered target-selection prediction**, while "**an aged 90-write-later reader directly caused the bestmove flip**" has status **NOT IDENTIFIED**.

The same mismatch affected **7/96** original December selector arms, all in the `old` category. Some physical triple interventions suppressed more than one reader site. All 12 December passive discovery streams reached their record limit of 256; no source-complete census or selection-rate inference follows.

## Two independent notions of time

- `write_age_count(r)=current_global_successful_save_serial - last_physical_writer_serial`: exact number of later accepted successful TTEntry payload writes in the cold, single-thread process. Zero is possible. It is *not* elapsed seconds, wall-clock age, slot local generation or number of distinct physical replacements.
- `read_event_ordinal(r)`: passive-order rank among bound-qualified value-as-evaluation consumers recorded until the fixed census limit. This is neither TT writer age nor search ply nor causal distance.

Neither statistic is a substitute for (i) source bound orientation, (ii) position search ply, (iii) root candidate ancestry, or (iv) downstream root competition margin.

## Source-matched intervention and anti-laundering gates

An **event-specific** intervention requires predicates beyond physical triple:
`V_{q,a,c,m,p,b}` where `a` is minimum accepted-write age, `c` source root call, `m` root candidate, `p` search ply and `b` TT bound. An actual source contact and matching full64 last-writer snapshot must be observed **at that event**. If not, result is NOT_FIRED/NOT_TESTED, not root-impact FAIL. If a physical triple is read earlier, it must be left unaffected by the age/call guard.

Adaptive case #11 event-specific re-experiment is declared **after inspecting outcomes** in [source protocol](c3x-018-adaptive-case11-old-reader-target-collision-disambiguation.md). It does not restore the prior independent D1 as a mechanistic age-90 result.

## Next independent holdout logic

For any *future* unobserved cohort, predeclare both event properties and actuator predicates, plus a **first-contact congruence requirement** for each category. Include `NO_MATCH` and `CENSORED` in the original denominator and never substitute a different root or write-age group after outcome inspection. If selecting among overlapping categories, count physical targets and causal interventions uniquely and disclose dependence. Naturally mediated TT search-to-root law remains **HOLD**.

Sources: [December preregistered native trial](../receipts/c3x-018-december-role-target-earlier-reader-collision-audit-20261010.json); [exact #1 root alpha screening](../receipts/c3x-018-case1-exact-root-alpha-screening-20261010.json).
