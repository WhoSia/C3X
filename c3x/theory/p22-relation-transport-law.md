# C3X G9.4-P22 — Relation-conditioned intervention-response transport

## 1. Scientific target
P22 does not ask whether four chess engines contain the same implementation. It asks whether a deliberately coarser intervention-response object survives a change of implementation **after** the nuisance exposure distribution has been prospectively balanced.

For world `x`, relation class `r`, engine `e`, and native intervention `i_e`, let

`Y_e(x,i_e)`

be the exact-world response induced by the intervention. The response is recorded at three nested resolutions: root action, fine exact-world value `(WDL, precise DTZ)`, and robust WDL.

Each engine has a native intervention alphabet `I_e`. P22 never assumes these alphabets are identical. Instead it declares a **partial** map

`phi_e : I_e -> A`

into abstract intervention roles `A = {MAIN_MEMORY, QSEARCH_MEMORY}`. A missing map is a structural zero, not an observed zero effect.

The relation-level law is

`L(e,r) = F({Y_e(x,i_e) : x in Omega_r, i_e in dom(phi_e)})`,

where `F` is the frozen response-geometry compiler inherited from the P20/P21 square construction. Transport is evidence that `L(e,r)` is preserved across declared engines on a prospectively constituted support `Omega*`; it is not evidence that their caches, source code, or internal states are literally identical.

## 2. Why P21 held
P21 selected each material-by-side stratum by distance to one global exposure center. That objective can make every selected point individually typical while leaving the two pooled relation classes systematically different. Formally,

`min sum_i ||z_i - mu||^2`

does not imply

`max_j |SMD_j(HEAVY,MINOR)| <= delta`.

The post-HOLD diagnostic established only design feasibility; it did not authorize a P21 result. P22 therefore changes the **design objective**, not the gate.

## 3. Prospective design as constrained support construction
The core design fixes 16 quotas: eight material vertices times two sides, six selected worlds in every quota. Let `s_i in {0,1}` indicate selection. The admissible set is

`S = {s : sum_{i in stratum k} s_i = 6 for every k}`.

For the nine frozen SHAM exposure coordinates `z_j`, define selected-sample absolute standardized mean difference between the two relation classes as `D_j(s)`. The primary design target is

`D_max(s) = max_j D_j(s)`.

The authorization constraint remains

`D_max(s) <= 0.50`.

P22 searches `S` directly. It does not estimate a propensity score, infer a treatment effect, or use selective intervention outcomes. The borrowing from matching theory is architectural: **design first, outcomes later; balance is a constraint/objective in its own right**.

The deterministic Rust matcher uses the lexicographic objective

1. minimize `D_max`;
2. minimize mean `D_j`;
3. minimize maximum absolute log selected-sample variance ratio;
4. minimize the sorted selected-SHA vector.

Sixty-four deterministic initializations are followed by within-stratum best-improvement swaps. This is a search algorithm, not a proof that no feasible subset exists. Therefore failure to reach 0.50 yields `BALANCE_FEASIBILITY_HOLD`, never `NO_COMMON_SUPPORT_THEOREM`.

## 4. Independent certification
Selection and certification are separated across implementations.

- **Rust** chooses the subset from SHAM-only TSV.
- **C++** independently recomputes quotas, SMDs, variance ratios, and the hard gate.
- **R** independently recomputes the same statistical quantities but has no selection authority.
- **JavaScript** verifies the preseal/receipt invariants and forbids a selective run when any certificate disagrees.
- **Python** remains the world/UCI/receipt orchestration layer because `python-chess` is useful there; it does not own the balance decision.

Agreement across languages is not itself scientific evidence. Its role is software-fault separation.

## 5. Transport versus abstraction
Pearl–Bareinboim transportability motivates explicit source/target differences: a causal relation does not transport merely because distributions look similar. For C3X, engine identity is treated as an environment change and native intervention semantics are part of the environment specification.

Rubenstein-style exact transformations and the Rischel–Weichwald/Lorenz–Tull abstraction line motivate a stricter question: can an engine-specific intervention be mapped to a higher-level query while preserving intervention-response behavior? P22 treats `phi_e` as partial because forcing every engine into one intervention alphabet would manufacture homology.

This yields a useful distinction:

- **distributional comparability**: balanced `Z_e(x)` under SHAM;
- **interventional consistency**: mapped interventions preserve the declared response law;
- **architectural identity**: not claimed.

## 6. Invariance as a falsification principle
Peters–Bühlmann–Meinshausen use invariance across environments as a causal signal. P22 borrows the logic but not their estimator. The engine family supplies heterogeneous environments; the candidate relation law earns authority only if it survives those changes under the frozen intervention semantics and balanced support.

Failure is localized:

- balance failure -> design authority failure;
- HEAVY replication failure -> relation-law failure;
- MINOR convergence -> P20 boundary failure;
- Inanis carrier disagreement -> broader persistent-memory rival failure;
- missing native channel -> abstraction-map boundary, not effect failure.

## 7. Chess-specific interpretability boundary
Jenner et al. show that causal interventions can reveal learned look-ahead inside Leela's policy network, but their puzzle filtering also illustrates that mechanism evidence can be highly conditional on the selected state distribution. P22 therefore treats state constitution as part of explanation authority rather than as an incidental benchmark detail.

C3X differs from activation patching: its interventions operate on search-engine persistent-memory semantics and its outcomes are exact-world action/value changes. The shared methodological commitment is that a mechanism claim must survive intervention, not merely probing or attribution.

## 8. Promotion ladder
P22 can at most promote the following sequence:

`fresh effect -> balanced relation law -> cross-engine relation transport -> partial cross-architecture abstraction candidate`.

It cannot jump directly to a universal mechanism law. A future universalization attempt would require additional architectures, independently mapped intervention alphabets, new world families, and composition tests showing that the proposed abstraction remains meaningful when intervention mappings are chained.

## 9. Long-range C3X direction
The long-range object is an **intervention-preserving quotient over heterogeneous search systems**: the coarsest explanatory state/relation structure that preserves the counterfactual distinctions actually licensed by experiments.

The intended endpoint is not a vocabulary of engine anecdotes. It is a theory that can answer:

1. which micro-mechanisms are equivalent for a declared explanatory query;
2. which architecture changes preserve that equivalence;
3. where the abstraction map becomes undefined;
4. what minimal intervention basis distinguishes rival mechanism classes;
5. how approximation/transport error composes across engine and representation morphisms.

P22 is one prospective step toward that theory: it removes a known design confound before asking the transport question again.
