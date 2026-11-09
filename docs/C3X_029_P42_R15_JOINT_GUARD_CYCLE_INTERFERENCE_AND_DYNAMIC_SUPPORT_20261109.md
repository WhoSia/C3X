# C3X 0.29–P42/R15 — Interference and Dynamic Support in Joint Game14 Source Interventions

Date: 2026-11-09 KST. **Prerecorded interpretation before final R15 native output.** The manuscript target remains causal computation ↔ genuinely valuable adversarial chess futures. This is a necessary mechanistic discrimination, not a standalone metrics paper.

## Validated original background: R12–R14 (not repeated experiments)

- R12 original B TT_FIRST: event ordinals 30,31,32,33 were the preselected first-33 cycle-alpha calls whose neutralization would change the immediate alpha/beta cutoff. **Only event 33** restored b3a4 when its neutral draw was physically applied once per native engine process. (A `cold()` call launches two actual engine subprocesses.)
- R13 actual original source event33 precedes first observable B/B33 root-depth boundary divergence at depth9. Chronological precedence is a *necessary consistency check*, not proof of a complete causal writer→reader path.
- [R14 original Game14 C vs B33 native #42182313883](https://github.com/WhoSia/C3X/actions/runs/42182313883): R14 successfully recreated actual original legacy C capture-prune bypass and B33 on one unchanged pinned engine source. **Both** restore b3a4 and have matching depth1–9 root leader/score, but their search states are not equal. In verified physical R14 artifact, depth9 B=(leader1373,score−74,average−70); C=(1112,−89,−79); B33=(1112,−89,−80). They first differ from each other at depth9 (in average). One physical C guard source action is explicitly different from the B33 source guard's unchanged outcome. R14 original artifact #13485682589 downloaded and independently SHA-256 examined: ZIP `ff89d26d75f7f50a4899a94e2fd00636971b009c8eb258e1b03edfd0cfcb4d44`, member JSON `1c80ef5d518da090d6d264263ae8d99db3d9e451abe5ebd522937f902162e51f`. No private chess position information published.

**Key unresolved question**: Does one original dynamic cycle decision explain the root restoration under original C guard intervention, or can two interventions reach an outwardly similar root through different descendant search state trajectories?

## Pre-specified R15 factorial collision

Keep original A, B, original C and B33 physical source controls exactly as in R14 (same source SHA, legal historical game14, same cold physical double-play). Then challenge **C+B33** in additional new native TT_FIRST searches:
- Freeze original C capture-prune event by the already established four-field source identity (native position key, root call, move and threshold). This identity is held private.
- Also request source cycle `C3X042_R12_TARGET_ORDINAL=33` once per actual engine subprocess.
- Verify that each physical subprocess actually hit and re-enabled the exact original C guard and actually neutralized the 33rd cycle-alpha event. Verify original TT_FIRST reader, two native engine processes per cold, the two cold repeats, source completeness and root-depth support.

**Critical distinction**: The dynamic 33rd cycle event under C+B33 need **not** have the source identity of B's original event33. The guard intervention may change the search before reaching event33. The court deliberately checks equality of all 33 preintervention original B source identities, original alpha/beta and required one-event return mutation. If that strict match fails, it records **dynamic-support drift** instead of inventing the equivalence of the two physical events.

Expected outcome interpretations:
1. Both physical interventions occur, root remains b3a4: **empirical robustness of restored choice under joint source changes**, not unique common mediation.
2. Both occur, root reverts to f3f4: **source-level interference/nonadditivity**; neither single-intervention restoration implies double restoration. Not proof of paradox or strategic inferiority.
3. Both occur, a third move wins: **dynamic candidate-set emergence**; binary classification is not enough.
4. One original physical intervention never occurs or root cold repeats fail: **HOLD**.
5. Dynamic event33 identity changes relative to the baseline B prefix: report the joint root outcome and **flag source-support mismatch**; do not call it the same original event, and do not claim natural mediator comparison.

This is a development Game14, with classical Stockfish16 (NNUE OFF) and postselected target. It cannot establish a new prospective game cohort or the chess reason for the final move. The result may be decisive in invalidating a mistaken single-mechanism narrative, not automatically in establishing a new unique one.

## Executable and provenance

- [R15 same-engine combined native court](../harness/c3x_029_p42_r15_original_guard_plus_event33_interaction_court.py)
- [R15 adversarial contract regressions](../harness/test_c3x_029_p42_r15_original_guard_plus_event33_interaction_court.py)
- [R15 source-locked read-only workflow](../.github/workflows/c3x-029-p42-r15-native-guard-plus-event33.yml), original immutable StageA and pinned Stockfish16.
- Raw source keys, windows, complete game state and logs remain private, only aggregate public verdict and license uploaded. GitHub authored by WhoSia, Actions contents:read, no bot commits.

**Evidence ceiling:** An observed convergent root at depth9 is not proof of a common natural causal path. Any transition to the main C3X strategic part must separately define true adversarial future `F(h,m)`, independent value judge `J`, and verify that the source-consumed calculation faithfully tracks that future across alternative opponents; not enough to show internal alpha-beta branch differences.
