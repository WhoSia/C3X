# C3X 0.19 — Formal Name Proposal & Opening Gates

**STATUS: PROPOSED / NOT YET ACTIVATED.** This is a formal phase-transition recommendation based on completed C3X 0.18 P0/P1 source experiments, not a new independent finding. Do not silently rename the active historical phase without explicit adoption.

## Recommended formal title

**C3X 0.19 — Endogenous Search-Memory Rewriting & Counterfactual Lineage Preservation: Versioned Transposition-Table Writers, Selective Consumer Restoration, Search-Window Path Dependence & Independent-Ecology Falsification**

## Why this phase boundary exists

At C3X 0.18 P0, real SF16 \`TTEntry::save\` was instrumented in the original compiler source. In January case #2, the first selected bound-qualified TT value-as-evaluation reader was blocked at root call4; the very next accepted true-payload write to the same full64 key/cluster slot had \`BOUND_EXACT=false\`, \`key16_mismatch=false\`, but \`new effective depth > old stored depth - 4\` TRUE. It changed physical writer epoch1 →2 and accepted global writer serial60→130, while raw stored \`value=-89\`, \`bound=LOWER\` and static \`eval=-284\` were numerically unchanged. Thus equality of TT value is insufficient for writer identity.

At P1, source-exact \`SKIP\` of *the single true source overwrite after first actual V contact and before the nominated second reader*, and source-exact \`REINSTATE\` of the original 10-byte TTEntry plus shadow writer epoch/serial **after** a real original save, both restored the old writer (epoch1, serial60) at the rootcall5 TT probe. Under the original F/V-BOTH source policy, two bound-value-evaluation reader gates fired at rootcalls4 and5 instead of just rootcall4. The final bestmove remained \`e1e4\`; nodes rose from 73369 to 73370 under rescued BOTH. In separate January game6, the temporally bounded operator left both original source readers intact and did not suppress an unrelated later write.

The original **unbounded** P1 negative-control prediction R5 FAILED because it suppressed a save at rootcall15 after both monitored consumers. That original failure is preserved. After a separately declared before-second-call temporal scope refinement, [native rerun #37995543334](https://github.com/WhoSia/C3X/actions/runs/37995543334) passed all R0–R7 under the revised operator. [P0/P1 SHA receipt](../receipts/c3x-018-P0P1-exact-save-predicate-and-temporally-scoped-writer-rescue-20261010.json).

The earlier **prospective independent January** TT pair bestmove effects J2/J3/J4 remain **FAIL**. A conditional rescue of one physical read is an important source-memory causal result; it is NOT an independently transported root-bestmove mechanism.

## Mathematical primitive to carry into 0.19

Let a source writer event \`W_t(q)\` assign a physical resident memory version \`V_t(q) = (full64 key, physical slot, epoch, accepted global serial, depth, bound, value, static eval, move)\` for TT carrier \`q\`. Reader eligibility \`E_{r}(V_t,alpha,beta,ply,root)\` depends on **both** this resident version and current search state. The search intervention \`I_1\` on an earlier reader may itself change the later endogenous writer event \`W_{t+1}\`. Consequently **the physical target selected under the passive arm need not survive into a counterfactual second read**, even if the raw numerical TT value is unchanged.

**Minimal identified local chain in case #2:**

\`actual first V gate → depth-driven TTEntry::save acceptance → epoch1→2 writer replacement → loss of original physical-target second V contact\`;

\`first V gate + SKIP/REINSTATE one timed write → old resident writer restored → second V contact restored\`.

This is an **intervention-conditional memory carrier lineage**, not a universal theorem of root-choice mediation.

## Proposed 0.19 opening work packages

**P0.19-A — Source State Sufficient Quotient:** Derive the minimal physically observable tuple needed to predict whether a TT value-as-evaluation reader survives a hypothetical earlier intervention, with failure contracts for missing full64 writer, ambiguous key16 hit, data races, sidecar drift and patch-induced I/O interference.

**P0.19-B — Write-Decision Causal Court:** Distinguish true accepted payload overwrite, key16 collision, move-only refresh, effective-depth improvement, and bound-exact override at each concrete save call. Source-precommit event signatures, writer version conservation/reinstatement and independent negative controls.

**P0.19-C — Multi-Reader Counterfactual Transport:** Across root-window pairs, test three distinct counterfactuals: source score suppression only, version-preserving writer suppression, and old-resident reinstatement. Evaluate local TT consumer restoration, full UCI transcript/search effort and categorical bestmove **separately**. Treat each source root call number as procedural, not invariant across perturbed trees.

**P0.19-D — New Blind Month and Cross-Engine Boundary:** Freeze source-only **February 2026** Lichess PGN (or another never-touched dataset) *after* formal predicates and risk thresholds are fixed; retain all missing eligible events and failures. Independently inspect an engine whose TT writer and cached eval roles are not identical to SF16, never assume source-role equivalence. The prior Ethereal cached-static-eval bestmove forecast failed and remains failed.

## Opening/closing authority gates

0.19 may start upon acceptance of this name and the observed P0/P1 mechanisms. It **must not claim** that 0.18 has proved natural TT mediation, universal search-memory dynamics or an independent-engine root-choice law. Before an eventual 0.19 theory freeze require (i) a new blinded cohort, (ii) two or more independent physical writer-version rescue sites, (iii) writer→reader identity valid under interventions, (iv) negative and destructive controls, and (v) explicit success/FAIL/HOLD for every prospectively registered claim.
