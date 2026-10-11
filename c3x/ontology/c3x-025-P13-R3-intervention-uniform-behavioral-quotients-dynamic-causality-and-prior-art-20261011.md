# C3X 0.25-P13-R3 — Intervention-Uniform Behavioral Quotients and the Dynamics Missing from Static Chess-State Explanations

**2026-10-11 · Mathematical continuation after P13-R3 native source experiment.** A mathematically elementary theorem is used here as an explicit engineering constraint, not promoted as a novel theorem or as empirical evidence.

## 1. Three levels of abstraction

Let S denote source-level full engine states, π:S→B a reported chess-state projection, U a *predeclared* family of policies/interventions with common valid input domain, and f_u:S→M a deterministic final action under intervention u and fixed budget/seed/scheduling regime. For finite S define the intervention response signature R_U(s)=(f_u(s)) indexed by u∈U.

**Static intervention-uniform factorization:** each f_u factors through π iff R_U is constant on every π-fiber. Proof is direct application of the single-function factorization lemma for each intervention. The smallest observable response partition is the kernel of R_U (not necessarily a computable or mechanistically interpretable feature). Enlarging U can only refine this kernel. If k response signatures occur within a public π-fiber, exact response-vector recovery needs ≥ceil(log₂ k) supplemental fixed-width bits.

This does **not** mean that fixing the signature explains *how* TT/SEE decisions occurred, nor does it identify an indirect causal effect. In particular, the policies/interventions must be defined on comparable full states; differences across mechanisms should not be mislabeled fixed-policy hidden-state collisions.

## 2. A stricter dynamic target

A state abstraction sufficient for one final UCI outcome can be inadequate for iterative deepening, repeated TT updates, or future counterfactual operations. Introduce source-native transitions T_u:S→S. For a deterministic abstract transition \bar T_u to exist with π∘T_u = \bar T_u∘π, it is necessary and sufficient that π-equivalent states remain π-equivalent after every T_u. This is a transition-congruence requirement, stronger than action-only factorization. For nondeterministic/scheduled transitions the appropriate relation requires a simulation/bisimulation-style successor condition instead of a single function equation.

If π forgets TT generation or per-field writer epoch, it may preserve *current action* while failing *future replacement behavior*: P4/P7 abstract and native TT generation findings supply candidate tests, not a general Stockfish proof of the dynamic condition.

## 3. Direct prior-art collision from existing canonical PDFs

- [Cousot & Cousot (1977), Abstract Interpretation](https://drive.google.com/file/d/1hZfipMMYFSwpOVx4ZuhAIvkzt4jDptIl/view): lattice-based sound abstractions permit conservative *sets* of outcomes. Our always-sound fallback is G(b)={f(s): π(s)=b}; singleton exactness is a stronger property.
- [Sangiorgi (2008), An Introduction to Bisimulation and Coinduction](https://drive.google.com/file/d/1ZuGSU7hLjJK47Sb2-mU-2b9OSuOeGDaT/view): equivalence of terminal outcomes can fail to be preserved under surrounding execution context. C3X must explicitly demand context/intervention preservation before treating one UCI as general behavioral equivalence.
- [Geiger et al. (2025), Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability](https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view): causal abstraction under mechanism transformation, intervention algebras and path-level interventions offer the appropriate rival framework. A dynamic trace certificate alone does not satisfy the intervention-alignment requirements.

**Original contribution not established:** the factorization/bisimulation/abstraction principles are not claimed as novel. The C3X-specific research possibility is linking a pinned real engine's field-sensitive memory authoring, dynamic call-value propagation, original SEE guards and counterfactual root behavior under auditable source interventions.

## 4. Native source evidence limits (actual R3)

Original SF16 P13-R3 [native CI #38141149946](https://github.com/WhoSia/C3X/actions/runs/38141149946) passed. At the selected actual qsearch move-recursion site, recorded 24 actual direct child TT score returns whose negated values were assigned into the original parent's value variable, with 24 matched parent bestValue writes among bounded native events. Original/observer/observer-off UCI b1c3, 8,657 nodes parity. Previous P12 24 source writer-linked TT return→direct caller facts also reproduce in that workflow, but the 24 P13 q events have **not** all been cross-joined to those first-24 writer evidence tags within the same individual run. P11 SEE 24 guards/10 continues and root update20 are not the same proven causal ancestry.

Next: independently parse original P11 serial→P12 exited child ID→P13 q assignment→bestValue within one cold engine run. Expand coverage to main search, re-search and root candidate only where source sites are uniquely pinned. Require full causal control and rival-path exclusion for P14; TT performance/chess strength and genuinely unseen M5 remain separate P15/E7 courts.

**RAVEL:** CORE = intervention-preserving description of search-state information. P13 native source is enabling with a demonstrated first correct child-value edge; P14/P15 force direct return to the black-box behavioral explanandum. Do not count instrumented operators or abstract theorem elegance as engine performance or genuine forecast success.
