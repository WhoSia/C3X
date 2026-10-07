# Executable Intervention Support Is Not Mechanism Transport
## Prospective Falsification, Regime Instability, and Authority-Safe Calibration in Chess-Engine Explanations

**C3X manuscript draft — P24 pre-outcome version**

> Status: active manuscript. P19–P23 results are sealed historical results. P24 is preregistered and open; no P24 calibration- or transfer-cohort FULL_CLASS outcome is reported here.

## Abstract

Mechanistic explanations of chess-engine preferences face two distinct transport problems: an intervention may be impossible to realize on a new position, and a realizable intervention may fail to reproduce the mechanism behavior learned elsewhere. We develop C3X, a prospective evidence architecture for near-equal chess-engine move preferences that separates these failures before generating causal-language explanations. Across a sequence of preregistered experiments, a one-dimensional engine-survival order failed prospectively and exhibited non-Ferrers engine×world interactions; class-level search interventions then showed heterogeneous mediation, while exact event addressability exceeded a frozen experimental budget. An outcome-blind structural quotient compressed 8,274–31,832 raw search events to 60–138 fibers per cell, but fresh parent mediator-class effects disappeared. A development activation field was therefore learned from pre-intervention BASE features. Its first held-out test could not open because routed-chain-realizable support fell below a frozen minimum. We then prospectively changed only the acquisition constitution: fresh worlds were selected under outcome-blind executable-support quotas, yielding 20 routed-chain-realizable positions and 100 engine×world×family cells across three event ecologies. With support now adequate and 20 positive activations observed, the frozen activation field still failed prospective transport (balanced accuracy 0.65 vs a preregistered 0.70 threshold; recall 0.60; specificity 0.70), with systematic overprediction of activation (predicted 0.36 vs observed 0.20) and strong source/engine heterogeneity. Thus executable intervention support and activation transport are empirically separable: solving the former did not rescue the latter. We preregister a source-identity-blind calibration extension that must fit on a fresh calibration cohort and transfer, after sealing, to matched-ecology events with disjoint source identities. In parallel, the deployed PGN explanation pipeline enforces the same evidence boundary as machine-readable abstention states, preventing implementation success from being promoted into scientific authority.

## 1. Introduction

A chess engine can prefer one legal move over another by a small margin while exposing thousands of internal search events along the path to that decision. Explaining such a preference requires more than identifying a correlated feature or replaying a principal variation. An explanation claim must survive at least four separable questions:

1. **measurement:** is the near-equal preference stable enough to study?
2. **intervention support:** can a frozen counterfactual manipulation actually be constructed and measured on the target world?
3. **mechanism activation:** when the manipulation is executable, does the proposed mediator class affect preference support at all?
4. **transport and authority:** does the learned activation law transfer to new engines/world ecologies strongly enough to authorize finer causal-language explanation?

C3X treats these as different evidence classes. This matters because a failed downstream test is otherwise ambiguous: the mechanism model may be wrong, or the target world may simply not support the intervention required to test it.

The central empirical result of the present manuscript is a prospective separation of those failure modes. In G10-P22, a frozen activation field could not be evaluated because executable routed-chain support collapsed below a preregistered minimum. G10-P23 prospectively repaired the support problem without consulting activation outcomes. After repair, the frozen field nevertheless failed. The result is therefore not merely another out-of-distribution accuracy drop: it is a controlled demonstration that **executable causal support is necessary but not sufficient for mechanism-activation transport** in this experimental system.

The current G10-P24 extension asks whether the remaining regime instability admits a low-dimensional calibration law. Crucially, event/source identity is prohibited as a predictor. Any calibration layer must be describable by reusable engine/ecology coordinates and must be frozen before a source-disjoint transfer cohort is opened.

### Contributions

This manuscript makes four bounded contributions.

**C1 — Evidence-class separation.** We operationalize executable intervention support as a prospectively measurable object distinct from mediator activation and downstream causal authority.

**C2 — Prospective negative result.** We show that an outcome-blind acquisition constitution can remove a frozen support bottleneck while leaving the frozen activation field falsified on 100 supported fresh cells.

**C3 — Failure-ladder identification.** Across P19–P23, scalar engine ordering, mediator class, event representation, parent-class activation, executable support, and activation transport are tested as distinct scientific objects rather than collapsed into one model fit.

**C4 — Authority-safe implementation.** The same evidence states route deployed PGN explanations: unsupported or scientifically unverified states suppress causal-certificate surface claims rather than merely attaching a warning label.

We do **not** claim to invent causal transportability, positivity, domain adaptation, probability calibration, mechanistic interpretability, or chess-engine instrumentation. Those literatures provide methodological donors. The narrow novelty is the prospective coupling of outcome-blind executable-support acquisition, mechanism-activation transport testing, source-memorization-resistant calibration, and machine-readable explanation authority.

## 2. Formal evidence hierarchy

Let (x) denote a chess world (position plus frozen experimental context), (e) an engine, and (f) a mediator family such as MOVE_ORDER or CUTOFF.

### 2.1 Preference-support endpoint

For each frozen near-equal move pair, the experimental system records whether the pairwise preference-support relation survives under a specified engine intervention.

### 2.2 Executable support

Define

[
R(e,x,f)=1
]

iff the frozen pair is active and the frozen intervention router yields a deterministic, legal, measurable TARGET/SUBSET/SHAM chain for family (f), using only pre-outcome information.

(R=0) is an **experimental-support abstention**, not a negative mechanism outcome.

### 2.3 Parent-class activation

Conditional on (R=1), define

[
A(e,x,f)=1
]

iff the frozen FULL_CLASS intervention changes preference support relative to BASE.

Thus (A=0) means the class intervention was executable but did not activate on that world.

### 2.4 Calibration transport

P24 introduces a calibrated activation probability

[
p_	heta(A=1mid z(e,x,f),R=1),
]

where (z) may include frozen R1 output, engine identity, time-control class, field-structure class, and BASE-only features. Source/event identity, player identity, post-intervention outputs, and Q0 outcomes are forbidden.

### 2.5 Local Q0 mediator authority

Q0 fiber evidence may be queried only downstream of adequate parent-class transport authority. A locally identifiable fiber cannot bootstrap its own parent activation authority.

The authority chain is therefore

[
	ext{world}ightarrow	ext{pair}ightarrow Rightarrow Aightarrow Cightarrow Q0.
]

Failure upstream blocks authority downstream.

## 3. Prospective experimental sequence

### 3.1 P19 — scalar order falsification

P19 prospectively tested the frozen engine-survival inclusion hypothesis across Stockfish 19, Berserk, and Ethereal. Exact nesting failed on fresh worlds, and order-free Ferrers diagnostics found incomparable engine neighborhoods. This ruled out a single globally nested engine-survival geometry as the governing representation for the tested tensor.

### 3.2 P20 — class-level multidimensional mediation, exact-event HOLD

P20 directly instrumented move-order, cutoff, evaluation-reuse, and reduction classes. Across 74 BASE rows there were zero BASE identity mismatches. Frozen interventions produced support changes in 12 NO_MOVE, 9 NO_CUTOFF, 8 NO_REDUCTION, and 6 NO_EVAL cells, including collapse and reversal of P19 obstruction witnesses.

However, exact-event address spaces were too large for the prospectively frozen 2,048-address budget. Across eight Phase-C cells the raw address universe ranged from 8,274 to 31,832 events. All addresses were repeatable; the failure was combinatorial rather than measurement drift. P20 therefore closed HOLD rather than increasing its budget after observing the counts.

### 3.3 P21 — outcome-blind quotient compression, fresh parent-effect extinction

P21 prospectively replaced raw event identity with an intervention-stable structural quotient. On the sealed P20 cells, Q0 compressed 8,274–31,832 raw events to 60–138 fibers per cell, a compression of approximately 99.1–99.6%. Development interventions localized positive Q0 mediator fibers in five cells across both P19 obstruction families.

Fresh validation then supplied 32 carrier cells with zero BASE identity/stability failures. Yet the decisive BASE/FULL_CLASS endpoint observed **0 class effects in 32/32 cells**. Because the parent effect was absent, fresh Q0 transport was unadjudicable. P21 closed HOLD without rerunning the fiber branch to search for positives.

### 3.4 P22 — development activation field, held-out support collapse

P22 reframed the unresolved object: not *which* local fiber mediates an already active class, but *whether the mediator class activates at all*.

On 180 development rows (21 positives, 159 negatives), the frozen rival ladder produced leave-one-ecology-out scores:

| Rival | LOEO score |
|---|---:|
| R0 boundary only | 0.4822 |
| R1 boundary + family load | **0.5892** |
| R2 context gated | 0.6006 |
| R3 engine conditional | 0.5892 |

Under the preregistered incremental-complexity rule, R1 was selected. The transparent rule used BASE-only coordinates:

- if BASE maximum gap (>74.5) cp: INACTIVE;
- if gap (le30.5) cp: ACTIVE iff candidate-side event imbalance (>0.19);
- if (30.5<) gap (le74.5) cp: ACTIVE iff family target-event count (>1926.5).

A held-out ecology then passed world and pair qualification: 32 positions, 11 admitted positions, 58 active engine-family cells. But deterministic routed-chain construction left only 28 profile cells, below the frozen minimum of 36. No held-out FULL_CLASS outcome was opened. P22 therefore closed HOLD upstream of outcome adjudication.

### 3.5 P23 — support repaired, activation transport falsified

P23 changed the acquisition constitution rather than the activation rule. Fresh worlds were harvested under a cyclic, outcome-blind routed-chain-support design. The first quota-satisfying prefix occurred at cycle 23.

The support seal contained:

| Quantity | P23 result |
|---|---:|
| Fresh candidate worlds | 144 |
| Routed-chain-realizable positions | 20 |
| Engine×world×family cells | 100 |
| Prague cells | 34 |
| Biel cells | 36 |
| Saint Louis Rapid cells | 30 |
| Max/min source ratio | 1.20 |
| Engines | Stockfish 19, Berserk, Ethereal |

At support seal, activation predictions, FULL_CLASS outcomes, and Q0 outcomes were all unopened.

The frozen P22 R1 field was then applied and sealed. It predicted ACTIVE in 36% of cells. Only afterward were fresh FULL_CLASS outcomes opened.

## 4. P23 primary results

Among the 100 support-sealed cells, 20 activated and 80 did not. BASE identity failures were zero.

| Metric | Result | Frozen gate |
|---|---:|---:|
| TP | 12 | — |
| TN | 56 | — |
| FP | 24 | — |
| FN | 8 | — |
| Balanced accuracy | **0.650** | **≥0.700** |
| Positive recall | 0.600 | ≥0.500 |
| Negative specificity | 0.700 | ≥0.700 |

The prospective primary verdict was **FAIL_P23_ACTIVATION_TRANSPORT**.

Source-level balanced accuracy was heterogeneous:

| Source | n | positives | BA | Recall | Specificity |
|---|---:|---:|---:|---:|---:|
| Biel Open Masters 2026 | 36 | 11 | **0.764** | 0.727 | 0.800 |
| Prague Masters 2026 | 34 | 4 | 0.567 | 0.500 | 0.633 |
| Saint Louis Rapid 2026 | 30 | 5 | 0.540 | 0.400 | 0.680 |

Only Biel passed the frozen per-source BA ≥0.60 robustness threshold, whereas two sources were required.

### 4.1 Post-primary diagnostic, no rescue authority

Post-primary analysis was explicitly demoted to diagnostic-only authority. The observed activation rate was 0.20 versus a predicted ACTIVE rate of 0.36, an offset of −0.16.

Engine-level BA was:

- Stockfish 19: 0.717;
- Berserk: 0.534;
- Ethereal: 0.745.

MOVE_ORDER and CUTOFF each had aggregate BA 0.65, providing no global family-specific rescue.

The diagnostic therefore identifies source/ecology and engine-conditioned regime instability as live successor objects, but it cannot upgrade P23's primary FAIL.

## 5. What P23 identifies

P22 and P23 form a controlled two-stage contrast.

In P22:

[
	ext{support inadequate}Rightarrow 	ext{activation transport unadjudicable}.
]

In P23:

[
	ext{support adequate} land 	ext{positive activations present} land 	ext{frozen field fails}.
]

Therefore the P23 failure cannot be attributed to the specific routed-chain support deficiency that blocked P22.

The result supports a bounded statement:

> On the prospectively acquired P23 target population, executable intervention support was not sufficient to make the frozen P22 activation law transport.

It does not establish that executable support is irrelevant, that no activation law exists, or that the tested ecologies exhaust chess.

## 6. P24 preregistered calibration-transfer experiment

P24 asks whether the P23 regime instability is repairable by a low-dimensional, reusable calibration law rather than source memorization.

### 6.1 Two-cohort design

Before either cohort's FULL_CLASS outcomes are used for modeling, P24 must freeze:

- three **calibration sources** spanning classical closed/round-robin, classical open/Swiss, and rapid open/round-robin;
- three **transfer sources** with disjoint source identities but matched ecology descriptors.

Each cohort independently must satisfy the P23-style executable-support gates:

- at least 3 sources and all 3 frozen ecology classes;
- at least 18 routed-chain-realizable positions;
- at least 54 engine×world×family cells;
- at least 12 cells per source;
- at least 2 engines;
- max/min source-cell ratio ≤2.0.

Failure of either support gate yields HOLD before calibration-transfer outcomes are interpreted.

### 6.2 Source-memorization firewall

Forbidden predictors include tournament/source/broadcast identity, player identity, event-specific intercepts, post-intervention scores/PVs/WDL, and Q0 outcome.

Allowed coordinates are:

- frozen R1 output;
- engine identity;
- time-control class;
- field-structure class;
- frozen BASE-only features.

### 6.3 Candidate ladder

The frozen candidate family is:

- C0_GLOBAL: R1 only;
- C1_ENGINE: R1 + engine;
- C2_ECOLOGY: R1 + time-control + field structure;
- C3_ENGINE_ECOLOGY: R1 + engine + time-control + field structure.

All candidates use penalized logistic recalibration. L2 penalty grid is ({0.1,1,10}). Threshold grid is ({0.20,0.25,0.30,0.35,0.40,0.45,0.50}).

On the calibration cohort, candidate+penalty pairs are ranked by leave-one-source-out log loss. All pairs within 0.01 of the best form the admissible simplicity set. The lowest-complexity represented candidate is selected; within that candidate, the minimum-log-loss penalty wins, with exact ties resolved toward the larger penalty. The classification threshold maximizes held-out BA, breaking ties upward. Candidate, penalty, coefficients, and threshold are then sealed.

### 6.4 Fair transfer comparator

Probability calibration is compared against **C0_GLOBAL fitted on the same calibration cohort**, not raw binary R1 outputs.

This distinction yields two scientifically different positive verdicts:

- **PASS_ECOLOGY_ENGINE_TRANSPORT:** a non-C0 model is selected, beats C0 on transfer log loss and Brier score, and clears all discrimination/source gates.
- **PASS_GLOBAL_RECALIBRATION_ONLY:** C0 is selected and clears the discrimination/source gates. Calibration transport is restored without evidence that ecology/engine terms add transferable information.

Primary discrimination gates remain BA ≥0.70, recall ≥0.50, specificity ≥0.70, plus BA ≥0.60 in at least two transfer sources containing both classes.

### 6.5 P23-only development audit

Before P24 fresh outcomes, we ran a diagnostic-only source-blind audit on the sealed P23 data. Source identity was excluded.

Leave-one-source-out log loss:

| Candidate | L2 | Log loss |
|---|---:|---:|
| C0_GLOBAL | 1.0 | **0.525903** |
| C2_ECOLOGY | 10.0 | 0.526762 |
| C0_GLOBAL | 10.0 | 0.527081 |
| C0_GLOBAL | 0.1 | 0.528988 |
| C2_ECOLOGY | 1.0 | 0.531313 |
| C3_ENGINE_ECOLOGY | 10.0 | 0.531896 |
| C1_ENGINE | 10.0 | 0.532349 |

The minimum-complexity rule would choose C0_GLOBAL on P23 development data. These coefficients are forbidden from P24 transfer adjudication. This audit is scientifically useful because it prevents the P24 narrative from assuming that visible subset heterogeneity automatically implies a transferable ecology/engine calibration law.

## 7. Authority-safe PGN explanation implementation

The science and product tracks share evidence states but not authority creation.

The explanation implementation recognizes machine-readable states including:

- SUPPORTED;
- ABSTAIN_CHAIN_REALIZABILITY_UNAVAILABLE;
- ABSTAIN_PARENT_CLASS_INACTIVE;
- ABSTAIN_ACTIVATION_SCOPE_UNCERTAIN;
- ABSTAIN_ECOLOGY_CALIBRATION_UNVERIFIED.

For an abstaining state, an otherwise valid causal certificate is suppressed from the surface explanation. The implementation can therefore reduce or preserve authority but cannot create scientific authority.

This matters for P24: before prospective transfer success, a calibration packet cannot silently turn a P23-failed activation scope into a causal explanation.

## 8. Relation to prior work

C3X draws on several established methodological traditions.

**Transportability and selection diagrams.** Pearl and Bareinboim formalized when causal relations learned in one population may be transported to another under explicit structural differences. C3X borrows the discipline of separating selection/transport assumptions from observed performance; it does not claim to generalize that theory.

**Positivity and overlap.** Causal inference requires adequate support for the contrasts being estimated. C3X's executable-support object is narrower and operational: support means that a frozen chess intervention chain can actually be constructed and measured on a target engine-world-family cell.

**Outcome-blind design.** P23 and P24 use design information available before the target causal endpoint is opened. This is used to separate acquisition from outcome-conditioned rescue.

**Causal interpretability.** Recent work emphasizes that interventions do not automatically license causal generalization and that mechanistic causal claims depend on explicit identification assumptions. C3X operationalizes this concern in a bounded engine domain by carrying authority states through to the deployed explanation surface.

## 9. Identification assumptions and limitations

1. **Operational endpoint.** FULL_CLASS activation is an engine-intervention endpoint, not human cognition or chess truth.
2. **Conditional target population.** Results concern (R=1) executable-support-qualified cells, not all chess positions.
3. **Coarse ecology descriptors.** Time control and field structure cannot block every source-specific difference. Source-disjoint transfer is evidence for descriptor transport, not universal invariance.
4. **Engine implementation dependence.** Stockfish, Berserk, and Ethereal expose different search implementations; the intervention grammar is aligned operationally, not assumed ontologically identical.
5. **Finite fresh ecologies.** P23 used three event sources; P24 will use six additional source identities if all support gates pass.
6. **Sequential theory development.** P20–P24 are prospective stage by stage, but their questions arise from earlier failures. Claims must therefore distinguish preregistered within-stage tests from cross-stage theory evolution.
7. **Negative results are binding.** P19 FAIL, P20/P21/P22 HOLD, and P23 FAIL are not overwritten by successor models.

## 10. Discussion

The sequence suggests a general design principle for mechanism claims in complex search systems: **intervention realizability, mechanism activation, and mechanism transport should not be treated as one prediction task**.

The P23 result is especially informative because it removes a concrete alternative explanation for P22. Once the executable-support bottleneck was prospectively repaired, the same frozen field encountered enough positive activations to be adjudicable and still failed. This turns “insufficient support” from a generic excuse into a separately measured variable.

P24 creates a harder falsification. If a source-blind calibration layer transfers, the result would support a compact regime law over the executable-support target population. If only C0_GLOBAL transfers, the earlier source heterogeneity will have been descriptively real but unnecessary for transferable correction. If P24 fails, regime instability survives both support control and prospective low-dimensional recalibration, sharply lowering the authority ceiling for parent-class activation and keeping Q0 local.

Either outcome is useful because the experiment is designed to distinguish them before the transfer outcomes are opened.

## 11. Current paper status

Sealed results through P23 are ready for a conventional Results section.

P24 remains open and pre-outcome. The paper must not fill P24 Results until all of the following occur in order:

1. six exact source identities are frozen;
2. calibration and transfer cohorts independently pass executable-support gates;
3. calibration-cohort outcomes open;
4. candidate, penalty, coefficients, and threshold are frozen;
5. transfer outcomes open exactly once;
6. the preregistered adjudicator emits the P24 verdict.

Until then, the manuscript reports P24 only as a preregistered successor experiment.

## References — working list

- Pearl, J., & Bareinboim, E. Transportability of causal and statistical relations: A formal approach.
- Westreich, D., & Cole, S. R. Invited commentary: positivity in practice.
- Manski, C. F. Monotone treatment response.
- Geiger, A. et al. Causal abstraction / causal-model-based interpretability work.
- Joshi, N. et al. *Position: Causality Is Key for Interpretability Claims to Generalise*. ICML 2026.
- Lin, Y., & Liu, Y. *Mechanistic Interpretability Must Disclose Identification Assumptions for Causal Claims*. 2026.
- C3X P19–P24 constitutions, machine receipts, and human-authored repository history, WhoSia/C3X.
