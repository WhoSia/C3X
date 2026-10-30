# C3X 0.29-P5 — Explanations as Proof-Carrying Contingent Strategies

**2026-10-31 | New theoretical integration of archived C3X 0.27 P3 full-branch witnesses and 0.25 P14 intervention evidence.** Not a fresh chess-engine measurement or a proved chess-strength advantage.

## 1. From explanations of static facts to executable contingent knowledge

Let s be a complete original legal chess state, a a proposed root move, and R(s,a) a **declared** opponent response domain: all legal replies, all captures, or some precommitted response policy. For an opponent reply r, let T(s,a,r) be all legal next actions available to the original mover. For a declared chess-semantic property P and finite horizon two plies after the root, the following is a *constructive* robustness claim:

  for every r in R(s,a), there exists t in T(s,a,r) such that P(s after a,r,t).

Because R and T are finite, this has the equivalent Skolem-policy form: there is a contingent response policy pi with pi(r) in T(s,a,r) for every r, such that P(s after a,r,pi(r)) holds for every r. A complete proof certificate is the domain R, the mapping pi, exact legal replay data, and property checks.

The policy mapping is **not** the engine's natural search PV, and is not a human move recommendation or proof of optimal play. In particular, a conditional policy over only capture replies has no claim about all legal replies. Reject vacuous empty-domain 'robustness' or explicitly label terminal-state treatment.

**Existing concrete reuse:** 0.27 P3 native-branch-logic adapter already materializes a response-to-recapture witness mapping for each capture-conditioned positive root, using source P2B full legal opponent reply enumerations. Hence the concept of a constructive contingent certificate was latent in 0.27; 0.29's genuine improvement is formalizing *multi-reason common witness* and contrasting explanation transfer, not pretending to invent the prior policy data.

## 2. Witness-coherence theorem and minimal refuter

For chess properties P and Q on the same two-ply reachable state, the claims

  [forall r exists t P(r,t)] AND [forall r exists t Q(r,t)]

DO NOT in general imply

  forall r exists t [P(r,t) AND Q(r,t)].

Finite countermodel: opponent replies R={r0}, legal own continuations T(r0)={t1,t2}, P(r0,t1)=true and P(r0,t2)=false, while Q(r0,t1)=false and Q(r0,t2)=true. Each property has its own successful contingent policy, but there is no *single* response move satisfying their conjunction.

Conversely, a common-witness certificate for P AND Q immediately implies a certificate for P and one for Q by projection. This is a predicate-logic property, NOT a newly discovered chess theorem; its significance is that an explanation generator that concatenates separately verified strategic reasons can produce an impossible joint recommendation.

Correct single-policy requirement:

  exists pi forall r [P(s,a,r,pi(r)) AND Q(s,a,r,pi(r))]

NOT independently selecting unrelated witness mappings pi_P and pi_Q.

If the explanation is about separate *available options* rather than one simultaneous action, say so explicitly; then separate existential certificates can be honest. The quantified meaning of the explanation controls the proof obligation.

## 3. Contrastive and context-indexed certificates

A robust certificate for candidate a is not automatically contrastive: to claim 'a rather than b because of P', additionally prove the declared predicate or common-policy claim FALSE or relevantly weaker under b, with an explicit legal opponent refuter. A negative counterexample may be a single opponent reply r*, whereas a positive proof needs the full R-domain policy pi.

The eventual explanatory object E(s,c;a,b) carries:
- **Semantic contingent certificate S:** full source state, declared legal opponent domain, horizon, chess properties, a witnessed response policy for their conjunction, and competitor refuters.
- **Mechanism result M:** source-exact native engine intervention I and decision Y(s,c,I), including P13-R4 exact scope and P14 source-root evidence, plus explicit censoring.
- **Earned joint link J:** identical source-root identity and actual within-run path correspondence if and only if observed; never infer natural TT -> SEE -> root mediation from two distinct experiments or chess truths.
- **Transfer H:** results on presealed new games and controlled human understanding, still pending.

This separation is forced in part by 0.25 P14-P6 actual same-position SHAM f1d1 and TT-score-intervention a1a5: semantic legal chess outcome features are fixed across the two treatments, while the actual engine decision differs. Board-only semantic claims cannot be universally faithful descriptions of both software choices.

## 4. Archived empirical constraints that shape P5

The complete 0.27 P3 archive contains 18 original chess root-state certificates and 9 rival pairs. Unconditional immediate recapture exists after **every** legal opponent reply in NONE of the 18 states. The capture-conditioned claim holds in 15/18 but is not a contrastive discriminator for positive cases42/43 (both rivals true), and only distinguishes negative control99. In case42 this conditional response policy has exactly one capture-response branch for each rival despite 38/40 total legal opponent replies. Consequently that proof must not be advertised as robust all-reply chess strategy.

0.27 P3 itself already reports the correct limits: strict immediate recapture is not material advantage or a true explanatory reason for root choice, H2 cannot establish minimal explanatory horizon, and full game/repetition source matters for some properties.

## 5. Next experiment, without redundant archives or validators

1. **Concept family first:** preregister 2 or 3 human-readable, nonvacuous chess properties (e.g., survives forcing checks, preserves a tactical resource, protects king exposure at H2-H4), with a single common-response policy proof obligation when explaining them conjunctively. The current P2B reply/recapture source can evaluate only the subset of those properties that it records; mark others UNKNOWN rather than overclaim.
2. **Development witness study:** use original 0.27 18 root states, retain negative cases47/99, and report strategy policies, counterexamples, equivalent explanations, witness-policy complexity, and nontriviality. Never tune explanation vocabulary after looking at the labels and then call that a test.
3. **Causal alignment:** reuse real P13-R4 QSearch parent assignments and P14-P6 root flip; seek the first SAME-ROOT native intervention whose changed move and a complete semantic contingent certificate can both be shown, without concatenating unrelated observed paths. Main/LMR/PV remains separately unproven.
4. **Human insight hypothesis:** a *compressed* contingent rule ("if the opponent attacks this pinned piece, move ...; otherwise ...") might teach more transferable chess judgment than a static move score. Test on independent games against score/PV and fluent-explanation baselines; compression or plausibility is not fidelity without checked coverage.
5. **Confirmatory cohort custody:** frozen September64 is unchanged; index20 castling-rights anomaly and partial historical source exclusions keep prospective freeze HOLD. The July28 source is development/exposed, not a new confirmation.

**Scientific status:** formal constructive-strategy and witness-coherence propositions established; actual full-legal chess data from 0.27 reused; proposed joint semantic+mechanism+human integration and new human transfer unmeasured. Repo author human only, no bot writeback.
