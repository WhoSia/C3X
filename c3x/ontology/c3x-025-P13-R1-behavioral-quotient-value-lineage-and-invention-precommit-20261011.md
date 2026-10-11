# C3X 0.25-P13-R1 — Behavioral Quotient, Native Value-Lineage & Independently Testable Engine Invention

**PRE-NATIVE DESIGN AND EXECUTABLE ABSTRACT SPECIMEN · 2026-10-11.** Parent: C3X 0.25 P13–P15 program. The three scientific axes are separate evidence domains, not one inflated success label.

## I. Mathematical result
Fix an engine policy, exact stopping budget, seed/scheduling conditions, and full machine state S. Let π map S to the public chess state B, and f:S→M denote deterministic final selected UCI action. A deterministic explanation g:B→M with f=g∘π exists iff f is constant on each π-fiber. Necessity: apply g to equal images. Sufficiency: define g(b)=f(s) for any representative of π⁻¹(b); constancy makes the definition independent of the representative. For a fiber containing k distinct actions, exact action recovery from supplementary finite labels needs at least k labels, or ceil(log2 k) bits for fixed-width coding. This does not reconstruct the full engine trace.

The checked C++ finite construction enumerates 32 toy state-policy worlds: board2 × history2 × TT generation2 × writer epoch2 × policy2. Fixed policy 0 has four conflicting public-state fibers (two actions each), requiring one more bit for deterministic exact action reconstruction; fixed policy 1 does not, and full-state projection factors. **These are toy model facts, not proof that Stockfish 16 realizes the same fiber under fixed policy.** TT intervention changing policy cannot be miscounted as a within-policy counterexample.

## II. Source implementation and current evidence ceiling
P11: 24 actual TT score returns tied to full64 original writer, SEE 24 native guards with 10 executed continue-prunes, root score changes20. P12: 24/24 actual direct C++ caller frames after TT return. Neither established actual parent assignment, bestValue competition, same-descendant SEE or terminal root mediation. The new C++ reference certificate strictly rejects missing value assignment, mismatched negamax sign, fabricated parent ID, and inference of natural SEE mediation from an observationally complete path.

**Actual P13 native status remains HOLD.** Next source experiment must use pinned original SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52, exact SHA gates, reversible C++ instrumentation and cold identical UCI/nodes/depth. Preselected native site classes: qsearch recursion, LMR scout, main non-PV full search, PV re-search, ProbCut qsearch. Instrument direct child returned score at the original call expression, actual negated assignment at parent, child/parent/root unique IDs, alpha/beta/depth and actual bestValue/update use. Label all uninstrumented sites CENSORED_SITE; record absent contact as HOLD rather than as no effect.

## III. Cross-source generalization and invention
P14 must separately intervene on original TT score consumption, move-order hints, generation refresh and replacement; distinguish exact search-state matched SEE descendants from merely coincident events and admit interventions that fail. P15 must separately report nodes/time/memory and opening-paired color-swapped engine strength with preregistered stopping, sufficient independent sources and confidence intervals; no present Elo gain. Any M5 model requires genuinely unseen sources, disjointness checks and all literal original UCI predictions sealed in human Git before physical FIRST.

Historical scientific negatives are immutable: September M3-v2 448/501 vs M0 449/501; July M4 915/1012 vs M0 916/1012. These exposed datasets cannot become M5 holdouts.

**C++ test status:** local GNU C++17 strict -Wall -Wextra -Werror -pedantic -O2 succeeded, 32/32 model enumeration and negative certificate controls passed. **Verdict:** ABSTRACT_EXECUTABLE_PASS / P13_NATIVE_HOLD / P14_NATURAL_MEDIATION_HOLD / P15_STRENGTH_UNMEASURED. No claims beyond provenance. Actions read-only; Git history human WhoSia only.
