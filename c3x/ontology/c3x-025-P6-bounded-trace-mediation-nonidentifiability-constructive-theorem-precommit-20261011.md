# C3X 0.25-P6 — Bounded-Trace Causal Mediation Non-Identifiability

**Status: FORMAL FINITE-STRUCTURAL COUNTEREXAMPLE ONLY, 2026-10-11.** This is a theorem about limited observational projections, not new biological/physics knowledge, native Chess/Stockfish correctness, or proof of an observed July2025 natural TT→SEE path. The older 0.25-P0 P1 P2 P3 exposed data and P4/P5 executable transition-system witnesses motivate the problem; do not fit new M5 or rename July as unexposed.

## Construction A: one TT intervention, same bounded observed trace, different mediation

Let `T∈{0,1}` be verified native TT FIRST policy assignment; `H∈{0,1}` an **unobserved later-than-prefix** change to the SEE *event activation / branch occurrence* (NOT the Boolean of `see_ge` on identical arguments); `C=1` denote a fixed witnessed first32 common SEE prefix; `Y∈{0,1}` observed final root bestmove flip relative to untreated sham. Our observational projection is `π=(T,C,Y)`, plus a constant physical contact source certificate. The original source TT value use and source exact node state are not in this projection.

Two *different* structural deterministic models:
- **Direct world `D`:** `H(T)=0`, `Y(T,h)=T`. TT reaches the root via some mechanism other than H.
- **SEE-activation world `M`:** `H(T)=T`, `Y(T,h)=h`. TT reaches the root via an as-yet-unobserved late SEE branch.

Both models yield exactly the same observable `π(T)=(T,1,T)` at **both** intervention policies, including observed root flip under T=1. But their controlled intervention at `T=1, do(H:=0)` differs: `Y_D=1`, `Y_M=0`. Their natural indirect contrast `Y(1,H(1))-Y(1,H(0))` equals 0 and +1 respectively. Therefore `π` **does not identify a unique causal TT→SEE→root mediation mechanism**.

## Construction B: even null final bestmove shift cannot refute mediation

- **No-effect world `N`:** `H(T)=0`, `Y(T,h)=0`.
- **Compensated world `X`:** `H(T)=T`, `Y(T,h)=T XOR h` (two opposing structural influences exactly cancel in the natural run).

Both have `π(T)=(T,1,0)` for both policies. But `Y_X(1,H_X(1))=0` versus `Y_X(1,H_X(0))=1`, giving natural indirect contrast −1; N has 0. A treated root that remains stable is **not** positive evidence that no intermediate branch changed.

These are **logical possibility constructions**; they may fail to correspond to a physically realizable Stockfish execution. Their purpose is identifying **which additional fields or operator interventions are necessary to distinguish mechanisms**, not asserting that any July case realizes X or M.

## Executable protocol preregistered before construction run

1. Enumerate both binary TT policies `T=0,1` for every source world and report complete observational projections. Require equality between D/M and N/X independently.
2. Compute and compare controlled mediator interventions `do(H=0)` at T=1 and the natural indirect contrast; require disparity despite observational equivalence.
3. Independently enumerate all `do(H=0/1)` × TT policies and show divergence at **some** controlled intervention, separating observational indistinguishability from causal equivalence.
4. For all four structural models, require `H` represent a **late SEE activation** not an illegal change to Stockfish native deterministic `see_ge` outputs at identical arguments. The witnessed prefix is fixed and truncated; it does not reveal H.
5. Emit only synthetic small JSON plus negative-control tests. A user-facing future conclusion must explicitly distinguish `FORMAL_NONIDENTIFICATION_OF_OBSERVATION_SCHEMA` from an empirical demonstration of `NATURAL_TT_SEE_MEDIATION`. Do not turn a p-value, simulated witness or small prior case into causal proof.

## Consequences for the two-axis program

**Microscopic theory:** declare observations into an information preorder: adding source temporal TT semantics, complete computational state, untruncated SEE event activation, executed guard decision, parent returned values and root candidate competition can shrink the equivalence class of compatible causal histories. No unique path may be claimed until rival structural histories consistent with observations are excluded under justified experimental assumptions.

**Theory of implementation:** source loggers and certificate checkers must carry an explicit **observed-field coverage**, censor flags, exact node identity and a typed reason for `HOLD_NON_IDENTIFIED`. An implementation that outputs `natural_mediation_proven=true` based only on E0+bounded SEE prefix+E6 final output fails this theorem. To investigate real mediation, perform a source-identical, preregistered, physically executed appropriate mediator intervention at unique matched native state with proven branch/contact and cold replay; compare natural operator changes separately from forced branch/SEE Boolean actions.

**Research guards:** August/September/July cases already exposed; earlier native P2 28/28/8 bounded shared SEE source events (all prefix censored) are not mediator identification. Future engine TT policy improvement requires actual performance/strength evidence and not these SCM countermodels. Human WhoSia Git provenance, source-rights and prior negative ledger remain intact.
