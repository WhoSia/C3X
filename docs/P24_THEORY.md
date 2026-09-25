# P24 theory note — from representation alignment to intervention-response law

P24 asks a narrower and harder question than ordinary representation similarity: **after aligning pre-intervention search states without looking at intervention outcomes, is there any quotient on which three different chess-engine architectures obey the same causal response law?**

## 1. What nearby literatures do

### Representation similarity
SVCCA/PWCCA/CKA/RSA compare internal representations under different invariance assumptions. The 2025 ACM Computing Surveys review makes the important distinction between representational similarity and functional similarity: either can agree while the other disagrees. C3X therefore treats search-state alignment only as a proposed coordinate map, never as causal validation.

Kornblith et al. (ICML 2019) also show why excessively transformation-invariant similarity can become uninformative in high-dimensional settings. P24 uses no learned invertible map and no outcome-optimized latent rotation.

### Multi-model alignment
Recent multi-way representation alignment work (2026) argues for a single shared universe for M>=3 models rather than O(M^2) pairwise maps. P24 borrows the *shared-universe* idea but not its neural-geometry objective. Our engines expose named mechanistic counters with different marginal scales, so the shared universe is an empirical-copula coordinate system: per-engine within-stratum ranks, then an engine-symmetric median and disagreement coordinates.

### Causal abstraction and distributed alignment
Geiger et al. formalize mechanistic interpretability as causal abstraction and use interventions to test whether a high-level model faithfully tracks a low-level system. Distributed Alignment Search relaxes neuron-wise alignment by finding distributed subspaces. P24 adopts the intervention-first standard but deliberately rejects a flexible learned alignment: the state map is frozen before selective outcomes exist.

This restraint is especially important after Sutter et al. (NeurIPS 2025): sufficiently expressive nonlinear alignment maps can make causal-abstraction tests vacuous. P24 therefore treats alignment capacity itself as part of the scientific constitution.

Pîslar, Magliacane & Geiger (CLeaR 2025) show that different inputs may genuinely invoke different computational states and that stronger high-level hypotheses trade coverage against faithfulness. P24's nested K=1/2/4/8 atlas is a prospective, non-outcome-trained analogue: it asks whether additional state resolution earns causal transport rather than assuming one global law.

Xia & Bareinboim (ICML 2025) show that lossy abstraction can violate abstract-invariance assumptions and require projected abstractions. P24 does not import their SCM construction directly, but takes the warning seriously: a coarse state quotient may erase effect-relevant architecture information. Architecture identity is therefore retained as an explicit candidate residual rather than silently projected away.

### Bisimulation and state abstraction
Classical bisimulation and Paige–Tarjan-style partition refinement define the coarsest stable quotient preserving labelled behaviour. DeepMDP, MICo and causal-bisimulation work in reinforcement learning similarly use behavioural equivalence to justify state compression. P24 adapts the principle to a finite intervention-response system: the actions are frozen memory-mask interventions and the observations are exact-world response fingerprints.

The resulting object is not claimed to be a full dynamical bisimulation of a chess engine. It is explicitly an **intervention-response bisimulation** over the P24 experimental algebra.

### Chess interpretability
AlphaZero work probes human chess concepts in learned representations, while later open-source chess XAI work controls information flow through neural chess models. Those are valuable but answer a different question. C3X works on persistent search-memory mechanisms in multiple classical engine architectures, applies source-level interventions, and adjudicates their consequences against exact chess worlds. It is therefore closer to causal reverse engineering of search than to concept probing or saliency.

## 2. P24's distinctive construction

For engine e, world x and named SHAM counters M_e(x), Q_e(x), define

- T_e(x) = M_e(x) + Q_e(x), total persistent-memory read activity;
- S_e(x) = Q_e(x)/(M_e(x)+Q_e(x)), qsearch share.

Within each material-family x side-to-move stratum, transform T_e and S_e to average-tie empirical ranks U^T_e and U^S_e. This discards architecture-specific marginal units while preserving within-engine order under monotone rescaling.

The shared atlas coordinates are

C_T(x) = median_e U^T_e(x),
C_S(x) = median_e U^S_e(x),
D_T(x) = max_e U^T_e(x) - min_e U^T_e(x),
D_S(x) = max_e U^S_e(x) - min_e U^S_e(x),
D_J(x) = (D_T(x)+D_S(x))/2.

No intervention response appears in these definitions.

A deterministic balanced refinement tree then produces nested quotients:

1. K1: one state;
2. K2: split each 24-cell stratum 12/12 by C_S;
3. K4: split each K2 block 6/6 by C_T;
4. K8: split each K4 block 3/3 by D_J.

Candidate SHA is the only tie-break. Thus every family-side stratum has exact support at every level, and K8 still leaves six cells per material family after combining sides — enough to reuse the inherited P20 square analysis without changing its support geometry.

## 3. What counts as success

For every quotient level K, state z, ontological square q and engine e, compute the inherited response fingerprint

L_e(z,q) = (curvature class, dominant intervention coordinate, dominant sign).

Three increasingly demanding questions are then separated:

1. **state relevance:** does refining z change L_e within an engine?
2. **conditional transport:** at fixed z, do engines satisfy the inherited P20 compatibility relation?
3. **strict architecture invariance:** at fixed z, are all three full fingerprints identical?

At K8, define a finite response machine whose nodes are (engine, state) and whose observation is the ordered HEAVY/MINOR fingerprint pair. Exact equality induces the coarsest intervention-response equivalence partition. If engine identity still splits aligned states, architecture is not a nuisance coordinate removable by this atlas.

The strongest negative endpoint is deliberately bounded: `FROZEN_ATLAS_QUOTIENT_REFINEMENT_CEILING_REACHED` means that none of the prospectively frozen K=1/2/4/8 quotients produces universal transport. It does **not** mean that no conceivable representation could ever align the engines.

## 4. Engineering constitution

P24 intentionally uses a small polyglot stack with role separation:

- **Rust**: deterministic empirical-copula alignment, nested atlas construction, cardinality invariants and state receipts. This is the scientific kernel: typed, fast, reproducible and easy to audit.
- **Python + python-chess**: exact-world constitution, engine orchestration and scientific adjudication. Python remains appropriate where chess semantics and experiment composition matter more than systems-level guarantees.
- **JavaScript (ESM)**: independent receipt/schema verification and human-readable report generation. It is not allowed to define the scientific partition.
- **C++** remains welcome for independent numerical certificates or engine-adjacent work, but P24 does not add C++ merely for language diversity.
- **Kotlin** is intentionally absent from the scientific critical path until a JVM-native service/UI or long-lived orchestration role justifies it.

The repository should look like a serious open-source research system, not a collection of one-off scripts: stable protocol files, a reusable Rust core, explicit schemas/receipts, reproducible workflows, clear provenance boundaries, and negative results preserved as first-class artifacts.

## 5. Literature anchors

- Raghu et al., *SVCCA: Singular Vector Canonical Correlation Analysis for Deep Learning Dynamics and Interpretability* (NeurIPS 2017).
- Morcos, Raghu & Bengio, *Insights on representational similarity in neural networks with canonical correlation* (NeurIPS 2018).
- Kornblith et al., *Similarity of Neural Network Representations Revisited* (ICML 2019).
- Klabunde et al., *Similarity of Neural Network Models: A Survey of Functional and Representational Measures* (ACM Computing Surveys, 2025).
- Geiger et al., *Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations* (CLeaR 2024).
- Geiger et al., *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* (JMLR 2025).
- Pîslar, Magliacane & Geiger, *Combining Causal Models for More Accurate Abstractions of Neural Networks* (CLeaR 2025).
- Sutter et al., *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* (NeurIPS 2025).
- Xia & Bareinboim, *Causal Abstraction Inference under Lossy Representations* (ICML 2025).
- Achara et al., *Multi-Way Representation Alignment* (2026 preprint / ICML-era work).
- Gelada et al., *DeepMDP* (ICML 2019); Castro et al., *MICo* (NeurIPS 2021); Wang et al., *Building Minimal and Reusable Causal State Abstractions for Reinforcement Learning* (AAAI 2024).
- Paige & Tarjan, *Three Partition Refinement Algorithms* (SIAM J. Comput. 1987).
- McGrath et al., *Acquisition of Chess Knowledge in AlphaZero* (PNAS 2022).
- Hammersborg & Strümke, *Information based explanation methods for deep learning agents—with applications on large open-source chess models* (Scientific Reports 2024).
