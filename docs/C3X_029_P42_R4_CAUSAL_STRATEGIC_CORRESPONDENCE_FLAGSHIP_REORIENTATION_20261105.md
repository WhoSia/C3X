# C3X 0.29-P42/R4 — Causal–Strategic Correspondence: the Central Research Problem

**2026-11-05 · PI research memorandum · theoretical research and historical source reconciliation, NOT a finished paper, native chess result, or proof of scientific novelty**

## 0. Non-negotiable reorientation

The goal is **not** an easier publication on evaluation metrics, legal response counting, checkmate horizons, generic low-regret plans, JSON prose, safety gates, or causal logging. Those are at most a few supporting pages in the flagship research. The hard question is:

> **Under what identifiable conditions does a specific internal computation of a search-based chess agent cause it to prefer a move *because of* a strategically meaningful difference in the counterfactual futures available after that move?**

“Because of” here must survive two distinct adversaries: (i) another computational route could have produced the same final move; (ii) a different chess predicate could be retrospectively attached to the selected move. Merely joining an engine trace to a chess-true claim is neither a causal mechanism nor a strategic explanation.

The historical results already constrain the question. In the September 2026 Game14 case, T=TT_FIRST reader suppression changed unrestricted Stockfish16 root b3a4→f3f4; conditional on T=1, bypassing precisely one actually reached capture_prune guard changed it back to b3a4 in two cold runs. The guard was selected after the root flip; it was reached in the treated search but **was not an equivalent naturally reached event in the untreated search**. No natural full mediator decomposition has been proved. In July root28, a real physical search intervention changed f1d1→a1a5 while both selected root positions had 25 legal replies and zero immediate captures/checks; arbitrarily chosen short-horizon tactics did not supply a reason. Original Memo03 and Memo02 are mandatory sources, not inventions of the present unit.

## 1. Two distinct spaces and a missing bridge

Let h be the exact *chess history* (not only a FEN), s(h) its legal position, and i a source-exact search intervention. The engine execution world contains a potentially changing computational DAG / dynamic event history

  C(h,i)=(TT receipts, eval/NNUE calls, SEE guards, searched branches, child-return scores, alpha/beta windows, ancestor assignments, root candidates, aspiration retries, output a(h,i)).

The chess world contains legal adversarial continuations and an independent, source-audited value oracle J:

  F(h,m)={all legal opponent replies and subsequent legal own continuations from h+m};

  V_J(h,m,r,u,...) = adjudicated conditional chess consequence with declared horizon and score bounds.

A **causal–strategic correspondence** is NOT simply a mapping of a code event to a label. It is a falsifiable relation B between (a) a *source-specific value-bearing decision difference* observed under controlled changes in C, (b) a *predeclared chess consequence property* on F, and (c) *transfer tests* preserving that relation when superficial piece coordinates, move notation, or irrelevant branch order change.

The central object to identify is therefore a causal–semantic bridge B, not a bag of motifs or a metric.

## 2. Historical three-arm experiment: what it can and cannot identify

Take T∈{0,1} as native TT_FIRST suppression and X∈{0,1} as the surgical guard bypass, with X=1 meaningful only for the treated, source-matched guard. Encode the final root move as binary A=0 for b3a4 and A=1 for f3f4 in THIS exposed comparison. The three physically observed worlds are:

| T | X | A | observed meaning |
| 0 | 0 | 0 | untreated source trace, guard event absent/not matched |
| 1 | 0 | 1 | physically suppressed TT and native guard skip |
| 1 | 1 | 0 | same TT suppression and one native bypass |

We **must not** identify a natural guard-value G(T=0) for the same source event: the event's existence itself changes with treatment. Such a G would be structurally undefined, not a measured “unpruned” value. Standard cross-world natural indirect effects cannot be computed by filling this off-support potential outcome with an arbitrary zero.

### Proposition: three-arm restoration does not identify unique natural mediation

Two abstract deterministic structural programs fit all three observed outcomes:

- Model U (guard-route): G = T(1-X); A=G. In this representation the target guard's skip is the sole effective cause of the root flip.
- Model V (parallel TT path + bypass compensation): G=T(1-X) is a recorded guard skip; H=T is a separate, value-bearing TT-induced search path; K=T X is a new compensatory descendant/writer/re-search effect generated when bypass is enabled; A=H(1-K). Here the natural T→root path need NOT pass through G. The guard bypass still causally restores the root by activating K.

Both produce exactly A(0,0)=0; A(1,0)=1; A(1,1)=0 and the same logged guard-skip G=0,1,0. Yet their claimed *natural TT→G→A mediation* differs.

This is an **identification counterexample about the available observation class**, not a claim that the actual Stockfish16 source implements model V. Since the observed guard event is treatment-dependent, ordinary fixed-mediator causal decompositions need additional support/assumptions. The observed local restoration remains real and important.

Proof: direct substitution into the two structural programs yields the three equalities; removing the structural link G→A in V changes no observed quantity. Therefore three-arm action and guard log data do not uniquely identify natural guard mediation.

### What would separate the models?

Do not respond by producing a longer correlation trace. Derive and intervene on **source exact value-bearing paths**:
- in the bypass run prove *actual entry* of the re-enabled candidate, its returned signed score and bound type, *actual adoption* into the parent score/alpha/bestValue, across ancestor states to a final unrestricted root-candidate comparison; account for aspiration re-search and transpositions.
- independently block or restore an identified descendant score/parent adoption while holding guard-bypass and TT interventions unchanged; verify the predicted root-vs-nonroot changes, including SHAM and non-contact controls.
- allow the result **MULTIPLE_PATHS_OR_COMPENSATION** if newly created TT writes or late re-search effects, rather than claiming a single natural mediation chain from the first visible guard.
- distinguish an *existence proof of an interventional path* from a *uniqueness claim* and a *natural mediation attribution*. The latter can be unidentifiable without strong modularity and path-specific assumptions.

## 3. A second nonidentification: chess-true discrimination is not semantic causation

For any two distinct legal chosen root moves m0 ≠ m1, the predicate q(h,m)=1[m=m0] perfectly distinguishes them. A square identity, “rook on a5”, or any outcome-relabelled move id likewise can be made accurate after seeing the result, even when the engine never evaluated that predicate. Therefore merely finding q(h,m0) ≠ q(h,m1) has no explanatory content.

A strategically relevant claim q must instead be selected **independently of the treatment's observed winner**, with a reason grounded in either:
1. a *source-traced value-bearing computation* that has independently checkable chess semantics (e.g., an actual exchange/defender consequence; NOT “SEE false implies prune” without original discovered-attack guard), or
2. a domain-justified opponent-response property whose counterexample distribution and value relevance are established without reading the engine choice labels.

For the flagship claim, require **interventional alignment**: modifying a chess-relevant contingency predicted to destroy q should alter the identified computation and chosen action *in a direction predicted before the experiment*. Mere conditional association between q and the chosen root is insufficient. This modification must be legal, history-sensitive and control confounds, since board edits can perturb many NNUE features simultaneously.

## 4. Proposed scientific hypotheses (all falsifiable; no result claimed)

**H1: computation-to-value path.** On independently selected near-tied chess decisions, local TT/SEE/NNUE perturbations at predeclared natural source sites change a traceable, bound-correct value comparison and unrestricted root choice. Competitor: root change explained by unrelated aspiration, order, TT state or alternative path. Failure if only root outcome changes with no actual value adoption or if a SHAM changes it similarly.

**H2: value-to-chess consequence alignment.** The value-bearing distinction of H1 is predictive of an independently judged, opponent-conditioned chess consequence q and its failure counterexamples, beyond a full Stockfish PV and strong Cui-style k=3 engine-backed partial strategy tree. Failure if mechanism labels are accurate but the chess consequence is unrelated, uninformative, contradicted, or selected after seeing outcomes.

**H3: counterfactual transport.** The same source/strategic relation predicts interventions and value shifts in previously unseen chess-game/event families with different move names/geometries; negative-controls include source contact without root flip, chess-consequence difference without source contact, and alternate engine family not sharing the same source representation. Failure if it works only on game14 postselection.

**H4: explanation as faithful human-useful abstraction.** Only after H1–H3, compare an artifact that explicitly exposes the limited causal–strategic relation against equal-resource strong branching JSON and engine PV for player counterfactual choice quality and calibrated uncertainty. Failure if fluent prose does not transfer useful information; do not rely on human preference ratings alone.

H1–H4 form a prospective research program, not a claim they must all succeed or a hidden redefinition of success. H4 is a downstream consequence, not the core proof.

## 5. Prior-art collision and novelty honesty

- Geiger et al, JMLR 2025 *Causal Abstraction*: intervention algebras, transformations, graded faithfulness and mechanistic interpretablity. Generic “causal abstraction”, “intervention” or patching is not a new C3X theorem. C3X would need new *source-executable, adversarial-game-specific* identification/evidence.
- Jenner et al 2024 *Evidence of Learned Look-Ahead*: neural future moves and causal interventions in Leela. C3X cannot claim existence of chess lookahead novelty.
- Cui, Ling & Ng 2026: engine-backed response-conditioned strategy trees, non-mainline evaluation and human use. C3X cannot claim response branching or teaching novelty.
- Press & Golubev 2026 BinProp: contrastive motifs and nearby negatives. C3X cannot claim contrastive chess concepts as new.
- P42/R1/R2: regret algebra and stricter evidence gates are needed as **short supporting preliminaries**, not paper contributions.
- Sandmann et al 2026 v4 original remains a bounded Drive gap; do not quote contested percentages until exact original inspected.

Novel claim **only if empirically proven**: a prospectively transported, source-exact, adversarially robust relation between *which computation causally decided a move* and *which future chess consequence gives that choice strategic meaning*. This is a conjectured research frontier, not yet established novelty versus all possible work.

## 6. Concretely resumed experiment, not another surrogate

**Game14 source spine first (development, exposed):** reuse source-locked Sept Game14 history and original single-guard target from Memo03, not newly selected convenient moves. Preserve 0.27 source event/TT policy and original native code. Add only the missing child-entry/return + ancestor adoption + root-candidate trace to the original source branch witness, using source event identity and full histories; compare three arms with two or more cold replays and controls. Mark any alternative causal path/candidate or score-bound uncertainty, not silently skip it.

**Prospective decisive cohort next:** fix engine source, candidate sampling, event-matching policy, semantic property-selection algorithm, alternative null models and episode/game/event exclusion before running interventions. Collect actual negative outcomes at fixed denominators. Run the actual native executable, not a synthetic matrix as a substitute. For q, test legally realizable opponent responses and strong source-independent value J with honest search-cost/score bounds. Report calibration/abstentions, no foregone conclusion.

**What not to do:** write an easy 3-ply-regret paper and call the flagship solved; do not substitute mobility, mate-in-two, immediate capture, square occupancy, verbal explanation quality, or ever-expanding test-gate code for strategic semantic mediation. These can appear as diagnostics or adversarial controls **only**.

## 7. Current verdict and research version

This memo identifies a *missing identifiability condition* and presents an explicit illustrative SCM equivalence construction. It is a research-level problem formulation and negative logical lemma; not a novel theorem independently against existing SCM literature, not proof of the corresponding chess neural mechanism, and not a publishable empirical result. C3X 0.29-P42/R4, with flagship work **HOLD** until source-native mediating values, meaningful chess outcomes, and prospective independent transport are established.

References: [C3X 0.27 Memo03](../docs/C3X_027_MEMO03_SOURCE_EXACT_CAPTURE_GUARD_CAUSAL_REVERSAL_20261020.md), [C3X 0.27 Memo02](../docs/C3X_027_MEMO_02_ROOT_CHOICE_WITHOUT_IMMEDIATE_TACTIC_EXPLANATION_20261019.md), [0.27 recovery](C3X_029_027_ARCHIVE_RECONCILIATION_AND_REAL_SCIENTIFIC_FRONTIER_20261031.md), [P42/R1](C3X_029_P42_R1_REGRET_NONIDENTIFICATION_AND_FAIRNESS_AUDIT_20261105.md), [P42/R3](C3X_029_P42_R3_PAPER_IDEA_COURT_MECHANISM_VALUE_AND_SUPPORT_20261105.md).
