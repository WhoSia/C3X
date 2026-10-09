# C3X 0.15 — Tactical–Strategic Operator Atlas (TSOA), Version 0.1

**Status:** MECHANISM TAXONOMY PROPOSED; P2/P3/P4 results descriptive and fully disclosed. P5 is a separately preregistered post-disclosure factorial experiment. No 0.16 transition. No new tactical or neural concept claimed merely because an operator class receives a name.

## 0. Formal aim: not a synonym dictionary, a decomposition of source execution

A chess word (pin, discovered attack, exchange, weak queen, positional pressure) is neither an SF16 source function nor a learned NNUE feature. We require a typed, falsifiable relation from original source-law world `w` through a concrete source-code site `u` and a fixed search environment `theta` to output `Y`.

- Chess-law classification: `G(w,s)`, legality of the pinned piece, slider, king and lawful replies.
- Search-local contact: `C_u(w;theta)`, whether operator `u` is actually eligible, executed and can change its return value. An event counter is **exposure**, not proof of effect.
- Interventional sensitivity: `I_u(w;theta) = 1[Y(do(u)) != Y(OFF)]`; measure score/PV/nodes separately, no assumption that flips are monotone with wider source-site sets.
- Mechanism ancestry: `M_u`, typed post-treatment search-frame/TT-bounded observations followed by separate direct necessity/sufficiency interventions.
- External transport: `T_{D->D'}(u)`, not licensed by matching tactics labels alone.

Define an operator's *empirical fiber signature* as a vector of actual outcome/trace contrasts over a fully named bounded cohort, runtime, and intervention family. It is an artifact of that intervention grammar and dataset, not a latent ontological species.

## 1. Source-native strata of 'pin' in Stockfish 16 classical

| Stratum | Native SF16 location / observation | Chess-level interpretation | Causal claim limit |
|---|---|---|---|
| L0 legal geometry | `Position::legal`, `blockers_for_king`, `aligned` | Royal pin limits available legal moves | Source chess-law relation, not learned representation |
| L1 exchange eligibility | `Position::see_ge`, `stmAttackers &= ~blockers_for_king(stm)` | A pinned recapturer is excluded by SEE | P2 manipulates one guarded root-object bit in hypothetical SEE |
| L2 classical evaluators | `evaluate.cpp` mobility area and `WeakQueen` blocker | Distributed long-range mobility / queen vulnerability | Classical route only; distinct own/enemy blockers |
| L3 selective-search gates | main/qsearch SEE-based prune, futility, LMR, move ordering | Whether an exchange or reply gets deeper calculation | Contingent on search state and current alpha–beta |
| L4 TT physical memory | `TTEntry::save`, `TranspositionTable::probe`, MAIN/QS early return | Save and reuse search-bound information | Key, slot, writer, bound, depth, window all required |
| L5 root competition | aspiration windows, iterative deepening, PV / bestmove | Practical preference among root alternatives | Root-selection changes may be downstream of unrelated descendants |
| L6 neural route | `Use NNUE=true`, NNUE/PSQ fallback | Different evaluator state | NOT identified in classical `Use NNUE=false` P2–P5 |

Do not call L0 strategic and L1 tactical by definition. The same piece configuration contributes to both, depending on time horizon, move ordering and which source site is activated. `Tactic` and `strategy` are *hypotheses on dynamical persistence and locality*, not binary SF16 source labels.

## 2. Observed P2/P4 funnel — a descriptive chain, not a mediation proof

TWIC 1665 R2 frozen original 64 pinned root worlds, Stockfish16 classical depth12:

- Source-guarded SEE was actually exposed in **51/64**.
- A differing search-frame entry within first 4096 post-eligible entries was observed in **35/64**; nine had a root bestmove change, 26 did not.
- A differing recorded TT event within the first 2048 source-conditioned TT observations was recorded in **30/64**; seven had a bestmove change and 23 did not.
- Overall P2 root bestmove changed in **11/64**; all 11 had source contact, **nine** had a first 4096-frame disagreement, **seven** had an early TT event mismatch. Two root flips were beyond search-entry observation cap; four beyond TT record cap or otherwise unregistered.
- Among the 64: 13 no-fire/no-frame/no-TT/no-root-flip; 14 fired but no observed frame/TT/root-flip; two fired and flipped without observed frame/TT mismatch; three frame-different/no-TT/no-flip; two frame-different/no-TT/flip; 23 frame+TT different/no-flip; seven frame+TT different/flip.
- All **30/30** earliest observed TT mismatch cases had **different full position keys** (rather than same-position changed bound). Thus a simple same-position TT-bound-first attribution is unsupported.

These are *nested observation-window* categories; `TT_not_observed` does not mean no TT effect. Source exposure / frame difference / TT difference / root preference **must not be multiplied as though independent events**. Cold repeats and 4 arms do not add original independent positions.

## 3. Specific same-law contrasts established empirically

Of 39 frozen source chess-law pin signatures, 10 occur at least twice (35 source-game roots). Four have both responsive and unresponsive roots:

- PAWN–BISHOP DIAGONAL, zero lawful pinned-piece moves: **3 flips / 6**, branch contacts 6/6.
- PAWN–QUEEN DIAGONAL, zero mobility: **3 / 6**, branch contacts 6/6.
- PAWN–QUEEN FILE, nonzero lawful mobility: **1 / 7**, branch contacts 7/7.
- PAWN–ROOK FILE, nonzero lawful mobility: **1 / 3**, branch contacts 3/3.

This provides bounded source-law heterogeneity, not internal 'four different pin neurons'. Other replicated categories are 0/no flip with small denominators; no exact class superiority or transport generalization follows. Observed responsive world counts by axis: diagonal 7/30, file 4/20, rank 0/14. These are subject to event/game source confounding and contact differences.

## 4. Search-operator context is not a chess 'style'

A strategic claim (e.g. long-term pressure) should require robust preference under declared perturbations of search horizon, hash size, move-order seed and evaluator routing (classical vs NNUE), as well as source-game context. A tactical claim should trace precise original legal replies, local forced sequence / SEE exposure and actual pruning consequences.

Neither robustness nor local force is established merely by using the terms 'mobility' and 'SEE'. A necessary refinement is to record for each native search:
1. original chess-law layer and legal tactical options,
2. operator root versus descendant location and actual effect,
3. first source-semantic divergence and current search frame,
4. first TT writer/reader and α–β eligibility,
5. root move preference and its stability under search-context perturbations.

The P4 regime is observational. P5's four-cell counterfactual varies SEE unmask `S` and post-first-candidate TT early-return availability `R`, holding all 64 roots; its outcome interaction diagnoses whether practical sensitivity depends on allowing TT returns, **not** whether one particular TT writer caused a root move.

## 5. Proposed theorem program and falsification

**Typed intervention locality:** Under a complete deterministic search state and a semantically inert instrument, the two programs cannot differ before the first affected source instruction. Ordinary induction; do not claim original mathematical discovery.

**Nonmonotone intervention:** Smaller interventions can cause bestmove changes that broader interventions do not; causal inference must not assume inclusion-monotonicity. P2/P4 source branch contacts do not imply downstream response.

**Search-bound authority:** `BOUND_LOWER/UPPER/EXACT` is algorithm-relative for actual selective Stockfish; no proof of true perfect-chess minimax value without matching assumptions.

**Mechanism equivalence:** Two source interventions may be observationally equivalent on one finite benchmark but incompatible on another search horizon/provider. Empirical equivalence needs `(D,theta,intervention language,outcomes,observer coverage)` in its type.

**Claim ladder:** proof of a source-branch change / proof of one TT read-and-bound ancestry / proof of that event's counterfactual necessity / robust chess-tactical explanation / neural representation are strictly separate gates. If one fails, `ABSTAIN` at the higher tier.

## 6. Continuing within 0.15

P5 four-cell source×TT-return factorial is an intervention on a *broad search regime* after source eligibility. Run standard sham and cold equality first. P6 should target one exact full-key physical TT writer/reader event with counterfactual replay; P7 should compare deterministic depth/Hash/NNUE route and separately source-local WeakQueen/mobility behavior; P8 should verify repeated-law cases on a second non-TCEC source. None of these is open until its contract is frozen and actual native results follow. No need to name or enter 0.16 yet.

**Verdict:** C3X015_STRATEGIC_TACTICAL_OPERATOR_ATLAS_V0.1_PROPOSED / TWIC_CROSS_PROVIDER_SEE_SOFTWARE_EFFECT_PASS / P1_C1_PRIMARY_ACCURACY_VS_0000_FAIL / TT_WARPK_READ_PROVENANCE_SCOPED_PASS / SINGLE_EVENT_TT_CAUSAL_NECESSITY_HOLD / TRUE_CHESS_STRATEGIC_INVARIANTS_HOLD / NNUE_LATENT_NOT_IDENTIFIED.
