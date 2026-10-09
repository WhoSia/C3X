# C3X 0.15 — CSWP v0.4: Categorical Potential-Outcome Fibers and Response-Projection Nonidentifiability

**Research status:** Original falsifiable extension of the C3X Causal Search-Window Provenance program. PI-approved C3X 0.15 remains OPEN; C3X 0.16 NOT OPEN. Source-specific post-P6 mechanism-reconstruction result, not a new universal chess law or proof of full TT mediation. Do not overwrite P1 context-model primary-accuracy FAIL.

## 1. P7 makes the old binary response encoding formally insufficient

For a frozen original chess-game root \(w\), a versioned SF16 build and a legal PIN-object source intervention \(S\in\{0,1\}\), define distinct single-TT-return interventions \(R\in\{I,V,B\}\):
- \(I\): original full64-key, exact writer-matched TT return, returning the native stored search value unchanged.
- \(V\): same matched TT read/return with exactly ONE value substitution \(\text{ttValue}\mapsto\alpha\) at the same consumer call site. This preserves the early-return control flow but modifies the number propagated. For P7's observed one-point fail-low window \((130,131)\), original UPPER bound tags and 14/29 stored-return values are recorded; it does not assert exact minimax soundness of the substituted 130.
- \(B\): suppress that one exact matched TT return and run the original continuing qsearch code. This *changes control flow*, unlike \(V\).

Let the *categorical potential-outcome matrix* be
\[
Y_w=\bigl(Y_{s,r}(w)\bigr)_{s\in\{0,1\},r\in\{I,V,B\}},
\]
where each \(Y_{s,r}\) is the completed-depth selected root UCI move. This is not a scalar score and not an NNUE latent vector.

The old 0/1 phenotype projects each column to
\[
\rho_r(w)=\mathbf1\bigl\{Y_{0,r}(w)\neq Y_{1,r}(w)\bigr\}.
\]
The projection \(\pi:Y_w\mapsto(\rho_I,\rho_V,\rho_B)\) is **not injective**, even for a deterministic source engine under exact replay.

## 2. Proposition — response-projection nonidentifiability (elementary, precise)

**Proposition CSWP-P7.1:** Knowing only \(\rho_V(w)=\rho_B(w)=1\) does not determine which SEE arm changed its root move relative to \(I\), and in general it does not determine the execution pathway or even the direction of a categorical outcome substitution.

**Proof by actual native counterexample:** In preselected TWIC original world #2 (P7 run 37918227188):
\[
 (Y_{0,I},Y_{1,I})=(d1e2,d1e2),\\
 (Y_{0,V},Y_{1,V})=(d1d2,d1e2),\\
 (Y_{0,B},Y_{1,B})=(d1e2,d1d2).
\]
Both \(\rho_V\) and \(\rho_B\) equal one. Nevertheless \(V\) changes only the SEE-OFF root choice, while \(B\) changes only the SEE-ON root choice. So the two source treatments **agree in binary phenotype while disagreeing in arm-local causal contrast**. The noninjectivity also follows abstractly by elementary set theory; C3X claims empirical demonstration in original-source SF16, not invention of categorical counterfactual logic.

For world #29, the result is a different pattern:
\[
 (Y_{0,I},Y_{1,I})=(d1e2,f3e5),\\
 (Y_{0,V},Y_{1,V})=(f3e5,f3e5),\\
 (Y_{0,B},Y_{1,B})=(f3e5,f3e5).
\]
Here \(V\) and \(B\) agree in BOTH categorical bestmoves, but this still does not identify an identical internal mechanism: two distinct source instructions can arrive at the same root move by different TT/search trajectories.

## 3. Revised measurement ontology and conditional invariants

For each experiment, publish **at least**:
1. Original legal source-game identity, exact root FEN SHA and intervention target full64 TT physical writer/consumer signature, with phase-specific precommits.
2. Original-categorical potential outcomes \(Y_{s,r}\) for every arm, rather than binary flip indicator only.
3. Arm-local effect vectors \(D_{s,r}=\mathbf1[Y_{s,r}\neq Y_{s,I}]\). For world #2: \((D_{0,V},D_{1,V})=(1,0)\), \((D_{0,B},D_{1,B})=(0,1)\). For world #29: both \(V\) and \(B\) have \((1,0)\).
4. Explicit operator exposure: original TT writer, QSEARCH_TERMINAL tag, BOUND_UPPER, stored depth 0, alpha 130/beta 131, original native return value (world #2: 14; world #29: 29), replacement alpha 130, exact matched-return delivery counts one each in value-only arms.
5. Numeric final score/PV/nodes, no-fire shams and search/path event traces, not just bestmove. Numeric differences do NOT automatically identify a unique mediated path.
6. Source-program semantic identity and cold replay. P7 24 native runs on 2 source-game worlds (12 arm/cold pairs), all identity and block arms exactly match prior P6 source-native evidence. These are NOT 24 independent positions.

**Original candidate distinction:** The CSWP *operational fiber* is a **typed, multi-intervention, categorical, provenance-bearing object**, not a synonym for one human tactic or a bucket of binary reaction masks. Its diagnostic scope depends on the intervention language and original engine source. "Strategy" requires robustness under search/horizon/evaluator perturbations, which is NOT established by P7.

## 4. Why the full alpha-beta/TT causal story is still incomplete

P7 narrows one fork:
- \(\operatorname{do}(V)\): alter the numeric TT-return content while still taking the original shortcut.
- \(\operatorname{do}(B)\): remove that shortcut, allowing ordinary qsearch continuation.

World #2's opposite arm-local effects show that **even matching binary response does not prove the same mediating path**. The next experiment should trace qsearch continuation's actual stand-pat, tactical captures, alpha/beta updates, and the return path, *before* root competition, then apply yet narrower source perturbations of a selected qsearch update/cutoff. Demonstrate deterministic common prefix and event read/write causality; do not infer a natural indirect effect from P7's outcome table.

## 5. Verifiable evidence, restrictions, and prior art

- P7 original source C++ intervention run: https://github.com/WhoSia/C3X/actions/runs/37918227188
- P7 canonical actual native court receipt: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P7-single-TT-score-vs-continuation-two-world-24native-20261009.json
- Source patch: https://github.com/WhoSia/C3X/blob/main/tools/c3x_015_P7_exact_TT_return_alpha_vs_qsearch_continue_patch.py
- C3X P6 original source-frozen TT return targets were selected on 64 worlds BEFORE P6 treatment outcomes; P7 world choice #2/#29 is **after P6 outcome disclosure**, so is *post-hoc mechanism contact*, not pre-score blind new-provider experiment.
- The old P1 classifier C1 overall accuracy 42/64 versus B0 53/64 FAILED. Nothing in P7 rescues that primary prediction.
- Ancient alpha-beta search, formal potential outcomes, causal attribution, typed effect signatures, and source slicing all have substantial prior work. The originality to test is the empirical combined **source-native chess operator matrix + physical TT provenance + claims ceiling**; do not assert CSWP-P7.1 is a newly discovered mathematical theorem.

**Evidence tier:** P7_BOUNDED_SOURCE_SOFTWARE_COUNTERFACTUAL_PASS; P7_CAT_RESPONSE_PROJECTION_NONINJECTIVITY_DEMONSTRATED_IN_TWO_WORLDS; COMPLETE_QSEARCH_ALPHA_BETA_MEDIATION_HOLD; EXTERNAL_ENGINE_TRANSPORT_HOLD; NNUE_LEARNED_LATENT_HOLD.
