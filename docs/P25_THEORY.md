# C3X G9.4-P25 — Architecture-indexed laws, budget-indexed atlases, and descriptor morphisms

## 1. Problem opened by P24

P24 established a negative but constructive result. Let `A` be the admitted engine-architecture set and let `Z` be a prospectively frozen, outcome-blind search-state quotient. For the frozen intervention algebra `I`, no tested quotient level produced a universal response law

`L : Z × I → Y`

that was architecture-free across Stockfish 19, Berserk and Ethereal. The admissible object became a family

`{L_a : Z × I → Y | a ∈ A}`.

P25 asks whether this architecture index is stable under replication, whether `Z` itself is stable under search budget, and whether the family `{L_a}` factors through a smaller, source-grounded architecture descriptor.

## 2. The search-budget axis

For a world `x`, engine `a`, and SHAM node budget `b`, let `T(a,x,b)` be named pre-intervention telemetry. P24's alignment operator is retained without outcome optimization:

`T(a,x,b) → empirical copula within family×side → engine-symmetric consensus/disagreement coordinates → Q_b(x)`.

`Q_b` is then refined into balanced nested quotients `K=1,2,4,8`.

P25 freezes

`B = {40k, 80k, 160k, 300k}`

before any selective P25 outcome is opened. The inherited canonical atlas remains `Q_80k`; selective source interventions are executed at `300k` nodes.

This distinction matters. P25 does **not** yet estimate a complete causal field `L_{a,b}` at every budget. It measures the observational state maps `Q_b` at four budgets and replicates the causal law family using the inherited `Q_80k → intervention@300k` constitution.

## 3. Budget stability is an empirical property, not a naming convention

If a state label is to behave like a robust mechanistic kind, changing the amount of search should not arbitrarily reassign worlds to unrelated states. P25 therefore measures pairwise coordinate drift, label agreement, and adjusted Rand index across the four frozen budgets.

The fine atlas is not budget invariant. Selected prospective readouts are:

| budgets | K2 agreement | K4 agreement | K8 agreement | K8 ARI |
|---|---:|---:|---:|---:|
| 40k ↔ 80k | 0.875 | 0.708 | 0.490 | 0.207 |
| 80k ↔ 160k | 0.891 | 0.750 | 0.565 | 0.274 |
| 160k ↔ 300k | 0.906 | 0.750 | 0.531 | 0.247 |
| 40k ↔ 300k | 0.802 | 0.578 | 0.331 | 0.103 |
| 80k ↔ 300k | 0.833 | 0.648 | 0.440 | 0.159 |

No stability threshold was introduced after seeing these values. The legitimate conclusion is therefore descriptive but consequential: **coarse atlas structure is more persistent than the fine K8 identity, and K8 cannot be treated as budget-free without an additional transport construction.**

## 4. Fresh architecture-index replication

P25 constitutes 384 fresh exact worlds at generation offset `620000`, disjoint from the P20–P24 world populations. On the canonical 80k atlas, the frozen P20 intervention algebra is executed at 300k nodes.

The P24 architecture-index result replicates:

- architecture-free K8 states: `0/8`;
- universal strict architecture invariance: false at `K=1,2,4,8`;
- universal conditional naturality: false at `K=1,2,4,8`;
- strict cells: `0` at every quotient level;
- natural cells: `0` at every quotient level;
- at K8, each of Stockfish 19, Berserk and Ethereal realizes `8` distinct state-conditioned response-law signatures.

Thus the architecture index is not an artifact of the particular P24 world sample.

## 5. Descriptor morphisms

Engine identity is scientifically unsatisfying if it is only a name. P25 therefore freezes a source-grounded descriptor map before selective outcomes:

`φ : A → D`.

The candidate coordinates are:

1. transposition-table indexing family;
2. whether a successful probe refreshes age/generation state;
3. whether probe returns a replacement handle directly;
4. whether evaluation and move information are packed together.

Shared properties such as the admitted search family, NNUE evaluation family, three-entry TT buckets, 10-byte entries, 32-byte buckets and shared qsearch TT are not eligible to explain between-engine variation because they do not vary over the admitted engine set.

For a coordinate subset `S`, let `π_S ∘ φ` be the projected descriptor. Let `~_L` be equality of the complete frozen K8 law signature. P25 calls `S` descriptively sufficient exactly when

`π_S(φ(a)) = π_S(φ(a'))  ⇒  L_a ~_L L_a'`

for every admitted pair `a,a'`.

Equivalently, the partition induced by `S` must refine the observed law-equivalence partition.

## 6. Minimality result and why it is not yet compression

The observed law-equivalence partition is

`{{Stockfish19}, {Berserk}, {Ethereal}}`.

No single frozen descriptor coordinate is sufficient. The minimal sufficient cardinality is `2`, with three admissible pairs:

- `{indexing_family, eval_move_packed_together}`;
- `{probe_refreshes_age_on_hit, eval_move_packed_together}`;
- `{probe_returns_replacement_handle, eval_move_packed_together}`.

However, every sufficient pair still induces three singleton engine classes. Therefore P25 earns **finite-set descriptor factorization** but **no nontrivial law-family compression**.

This distinction is central. A two-coordinate key that merely identifies each of three engines is not yet a mechanistic low-dimensional law. It is a smaller vocabulary for the observed separation, not a population-level causal model of architecture.

## 7. Identification ceiling

With only three heterogeneous engines, many descriptor systems can separate all observed laws. P25 therefore does not claim that either member of a sufficient pair causes the law difference. Nor does it claim that the four frozen coordinates are complete.

A stronger identification programme requires at least one of:

- additional architectures that create repeated descriptor values with different engine identities;
- prospective architecture variants that alter one descriptor while preserving neighboring mechanisms;
- within-lineage source interventions that directly manipulate a descriptor candidate;
- held-out engines whose law signatures are predicted from descriptors before their outcomes are opened.

This is the natural bridge from descriptive morphism to causal architecture coordinate.

## 8. The architecture × budget product space

P25 forces a refinement of the P24 ontology. The future object should not be written simply as `L_a(z)`, because the state map itself depends on budget. A more honest starting object is

`Q_b : X → Z_b`

and

`L_a^(b0→b*) : Z_b0 × I → Y`,

where `b0` is the budget used to constitute the state and `b*` is the selective intervention budget.

The next theoretical question is whether there exists a cross-budget correspondence

`τ_{b→b'} : Z_b → Z_b'`

under which architecture-indexed laws commute approximately or exactly. If not, architecture and budget jointly index the causal law field.

## 9. Relation to adjacent literature

C3X is adjacent to, but deliberately distinct from, several active research programmes:

- causal abstraction and interchange-intervention work asks when a lower-level system implements a higher-level causal model;
- representation-alignment work studies correspondences between model spaces and warns that overly expressive maps can make mechanistic equivalence vacuous;
- causal representation learning and invariance methods seek representations that preserve causal or environment-stable structure;
- state-abstraction and bisimulation work asks when states can be merged without changing relevant dynamics or values.

P25's distinctive constitution is the combination of **source-level mechanism intervention, exact-world chess adjudication, outcome-blind representation freeze, explicit alignment-capacity ceiling, cross-architecture replication, search-budget perturbation, and source-descriptor factorization**. Priority claims should still be made only after a dedicated systematic review.

Useful comparison points include Geiger et al., *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* (JMLR 2025); Yao et al., *Unifying Causal Representation Learning with the Invariance Principle* (ICLR 2025); Sutter et al., *The Non-Linear Representation Dilemma* (NeurIPS 2025); and Xia & Bareinboim, *Causal Abstraction Inference under Lossy Representations* (ICML 2025).

## 10. Executable-theory consequence

P25 also changes the research method. `c3x-lawgen` compiles a typed ontology specification into a constitution, execution matrix and claim lattice. The scientific authority relation is intentionally two-way:

`theory → generator constraints → experiment`

and

`implementation failure / counterexample → exposed hidden assumption → theory revision`.

The generator does not decide what is true. It makes it harder for the experiment to silently become a different experiment after outcomes are visible.

## 11. Closure

P25 closes as:

`FRESH_ARCHITECTURE_INDEX_REPLICATED__FINE_ATLAS_BUDGET_NONINVARIANCE_MEASURED__TWO_COORDINATE_DESCRIPTOR_SEPARATION__NO_NONTRIVIAL_LAW_FAMILY_COMPRESSION`

The next object is therefore not a single universal search-state law. It is an **architecture × search-budget indexed causal-law field**, together with an explicit question of whether cross-budget state correspondences and architecture descriptors can make that field factor through a smaller mechanism space.
