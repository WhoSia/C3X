# C3X 0.15 — Causal Search-Window Provenance: Event-Localized Response Theory v0.3

**Research status, 2026-10-09:** An original **candidate formalization**, not an established subdiscipline or a claim of unexamined novelty. This extension integrates P2–P6 actual native source intervention results without modifying original blinded P1 B0/B1/C1 predictions. C3X 0.15 OPEN; 0.16 NOT OPEN.

## 1. Distinguish four interventions and three knowledge claims

- G intervention: changing the chess position or legality; NEVER done in C3X P2–P6, which preserve source-board history and legal moves.
- S intervention: change the original-root PIN-object branch in static exchange evaluation (SEE); in the SF16 source this excludes pinned recapturers in a hypothetical exchange, without unpinning legal pieces.
- R intervention: allow/suppress *all* otherwise eligible main/qsearch TT early returns after the first source PIN-SEE candidate (P5). This is broad, high-dose perturbation of search regime, and cannot identify a single physical TT read.
- E intervention: suppress *only one presealed physical full64-key TT early return* when writer sequence, writer class, stored bound/depth, TT slot, reader alpha/beta, depth, ply and node type all match in a run (P6-S1). Zero or missing matched events are documented exposure failures.

Three non-equivalent claims:
1. Observable causal program response under a declared surgery (bestmove/score/PV/nodes).
2. Event-level bounded return sensitivity in a versioned native execution.
3. Complete causal mediation of the original SEE effect by that TT event. P6 establishes examples of claim 2, NOT claim 3. The same root decision may depend on several substitutable or antagonistic paths.

## 2. A typed response signature over interventions

For game-root world w, engine environment theta and two source conditions S=0/1, let Y_{S,R}(w) be the deterministic completed-depth root bestmove when the TT early-return regime is R, with R=allow / broad-block. Define the **binary SEE intervention response**

  rho_R(w) := 1[Y_{1,R}(w) != Y_{0,R}(w)].

It is not correct to subtract bestmove UCI strings as numeric quantities; compare an explicit categorical equality predicate. The within-world response-regime interaction is

  eta_R(w) := rho_allow(w) - rho_broadblock(w), values in {-1,0,+1}.

P5 actual TWIC64:
  both response 5; only allow 6; only block 7; neither 46.
  sum rho_allow = 11; sum rho_block = 12;
  number of altered binary response identities = 6+7 = 13.

The **response support symmetric difference** is a new useful diagnostic:
  D_R := supp(rho_allow) XOR supp(rho_block).

Its cardinality does not equal |sum rho_allow - sum rho_block|; 13 vs 1 here. This is elementary set theory; novelty, if any, is its disciplined use in source-native chess operator phenotyping with preregistered interventions and independent source events.

## 3. Single-edge response and the exposure denominator

Let E_w be the first original OFF **actually taken** post-SEE-eligible TT early-return edge with full64-key-exact known physical writer; it is selected in P6-S0, before P6-S1 new treatments. E_w includes root identity, last writer source and sequence, 64-bit position key, TT physical slot index, stored bound/depth, consumer window, ply, depth and node type. E_w is null for exactly 13 of 64 original root worlds.

Set Y_{S,B(E_w)}(w) for blocking at most one event that exactly matches E_w in each native S search. Crucially, an edge can be **not visited or not matched** in a treatment arm. Let X_{S}(w) denote whether the exact block was actually delivered; if X_S(w)=0, do not pretend E_w was manipulated in that arm.

Observed P6-S1:
- 51 non-null frozen E_w, 13 null negatives.
- In OFF, 51/51 exact matched and suppressed one return.
- In SEE, 44/51 matched and suppressed; seven had **no equivalent reader exposure**. The 44 matches must not be conflated with 51 selected targets.
- On all 64 source roots, ordinary SEE response count =11 and one-return suppression SEE response count =11; the response set changes in exactly **two worlds**.
- World #2 changed from rho_allow=0 to rho_singleblock=1; world #29 changed from rho_allow=1 to rho_singleblock=0, with both exact edges matched in both SEE/OFF. In both cases the targeted OFF TT entry was qsearch-terminal, stored UPPER bound and depth 0 at consumer window alpha=130, beta=131, ply=4.
- Effectful worlds came from distinct original legal source games and have different TT fullkeys. The P2 result, binary model and candidate target manifest were unchanged.

This is evidence for **operational, bounded one-edge return influence** in those two executions. It does not establish a unique mediator of the natural SEE effect, nor exclude alternative TT or pruning paths.

## 4. A claim-authority lattice, not an all-or-nothing explanatory sentence

Evidence tier L0: legally reconstructed independent source game and SHA-locked environment.
L1: untouched engine, passive OFF and treatment show exact nonfired controls and repeatable native root outcome.
L2: first source eligibility, observed source operation and aligned bounded search-frame alpha-beta windows.
L3: physical TT producer/reader provenance with fullkey, writer, bound/depth and observed window — recorded ancestry, not causal necessity.
L4: predeclared specific exact-event return counterfactual is delivered and changes output, with same-source sham, cold restart, exposure denominator. This is what P6 validates for 2 source worlds. Other worlds may be L3/ABSTAIN.
L5: a natural direct/indirect mediation or explanation of a winning chess tactic, requiring controlled alternatives, support for independent mediator interventions, and coherent causal pathway; NOT identified.
L6: independent NNUE latent concept or transfer across engine families and time horizons, requiring feature intervention/transport; NOT identified.

Each tier has separate evidence prerequisites; obtaining L4 under a specific surgery does not entail L5. This is a partial order of **claim licenses**, not a scalar claim that every explanation progresses equally.

## 5. A useful falsifiable criterion: operator-context noncommutativity

For source intervention S and TT return operation B(E), the categorical root-choice differences may depend on order and context. However 'noncommutativity' must be defined as a contrast between explicit versioned executed programs, not inferred from a single value of a commutator between bestmove labels. A precommitted two-factor paired experiment with matchable event identity tests whether

  1[Y_{1,allow} != Y_{0,allow}] != 1[Y_{1,B(E)} != Y_{0,B(E)}].

Worlds 2 and 29 are concrete TRUE witnesses. **Do not** generalize it to a mathematical theorem about every alpha-beta engine or to learned pin concepts. A future exact search trace must localize the first *effective* SEE value change and map paths to first return suppression for causal ancestry.

## 6. Why strategy and tactics should be decomposed along programs, not words

The causal object of interest is the operator stack:
 L0 legality -> L1 SEE recapture pruning -> L2 classical mobility / WeakQueen -> L3 move-order / LMR / futility -> L4 TT last writer / bound / cutoff -> L5 aspiration / root competition -> L6 NNUE evaluation route (untested).

A human word such as 'pin' can span several of these. A 'tactical' claim needs local original legal replies, source branch, search consequence and a counterfactual certificate. A 'strategic' claim should require horizon/engine-setting invariance, mobility/value routing and repeated-game source stability. Neither can be inferred from one depth12 classical run.

In particular SF16 still supports classical Use NNUE=false, whereas the project must version-lock future engine-family tests: newer Stockfish revisions removed the original classical evaluator. Cross-engine route comparison without naming exact revision is invalid. P2–P6 supply strong source-search examples but no latent neural feature identification.

## 7. Known prior art and gaps

Knuth and Moore (1975) established analysis of alpha-beta pruning. Plaat, Schaeffer, Pijls and de Bruin (1996) explored TT solution trees and null-window alpha-beta; the existence of TT/alpha-beta interactions is therefore not new. Software dynamic slicing and counterfactual program analysis predate C3X. The proposed distinctive contribution is *precisely source-versioned engine-operator surgery, physical TT writer–reader continuity, unit-level response-support changes, constrained explanation claim licensing and explicit negative exposure*. Systematic closest-prior-art review is still required.

## 8. Next experiments under C3X 0.15, not 0.16

P7A: native qsearch-bound event family refinement: stratify MAIN_TERMINAL versus QSEARCH_TERMINAL, LOWER versus UPPER, true writer->consumer key match and original legal tactic. Do not choose cases only because they yielded a positive change; use all 64 and expose null edges.
P7B: position-local WeakQueen own/enemy-blocker source interventions with OFF/sham/no-fire guards, source identity and actual WQ routing. Compare exact same-law PIN groups and SEE.
P7C: depth10/12/14, Hash16/64 and classical/NNUE routes; measure tactical stability and strategic horizon invariants, not just raw bestmove cross-run agreement.
P7D: typed Rust verifier of source/target/output SHA with interval constraints and no bot-authored GitHub commits.

**Judgment:** C3X_0.15_OPEN / P2_512_NATIVE_SEE_EFFECT_PASS / P1_C1_PRIMARY_ACCURACY_FAIL / P4_SOURCE_WINDOW_TT_PROVENANCE_PASS / P5_512_NATIVE_BROAD_POLICY_INTERACTION_PASS / P6S0_128_NATIVE_OFF_TARGET_PRESEAL_PASS / P6S1_512_NATIVE_EXACT_ONE_TT_EDGE_CAUSAL_SENSITIVITY_TWO_ROOTS_PASS / NATURAL_MEDIATION_HOLD / NNUE_LATENT_HOLD / C3X_0.16_NOT_OPEN.
