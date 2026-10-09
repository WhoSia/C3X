# C3X 0.15 — CSWP Theory v0.2: Interventional Bound-Provenance and Identifiability Court

Formal research name: **Causal Search-Window Provenance (CSWP)**.
Date: 2026-10-09. Status **PROPOSED THEORY / TESTABLE, NOT PROVEN AS A UNIVERSALLY NOVEL DISCIPLINE**. Supersedes only the *theoretical proposal*, not the empirical P0–P3 receipts or frozen predictions.

## 1. Prior-art priority is contested, not assumed

Traditional alpha-beta pruning is classical (Knuth & Moore 1975). The deeper relationship between transposition tables, solution trees, repeated narrow-window searches, and proof-like minimax bounds is **already developed** in Stockman (1979) and Plaat, Schaeffer, Pijls & de Bruin (1996), *Best-first fixed-depth minimax algorithms* (Artificial Intelligence 87:255–293, DOI 10.1016/0004-3702(95)00126-3), including the observation that SSS* can be implemented with alpha-beta + TT and the MTD(f) window framework. Proof-number search (Allis et al 1994) also predates us. Program dynamic slicing and causal debugging predate us. A generic "TT encodes search evidence" or "alpha-beta cutoffs form a proof structure" is **NOT a C3X novelty claim**.

Our narrower research hypothesis is that a software-engine *source-site intervention* can be connected via a typed, empirically audited **physical-TT writer→reader plus αβ bound provenance** to the actual change in a complete search's root candidate selection, while also carrying an explicit negative-control and explanation-authority certificate. Whether this *integration* is globally new still requires a focused prior-art collision review.

## 2. Formal objects and intended category of explanation

Let an engine-configuration state be
  x=(P,H,\rho,S,d,\alpha,\beta,T,F,W,\theta)
with board/history, root-candidate state, search stack, depth and current bounds,
physical TT state, operator-fire events F, evaluator/PSQ route W, exact build theta.

For source intervention j, define operational semantics E[j], deterministic trace
  tau_j=(s_0,e_0,s_1,e_1,...,s_n),
  Y_j=bestmove(E[j],s_0).
A trace event is of a **type**:
  Law, SeeCandidate, SeeActualFired, NodeEnter, EvalRoute,
  WindowUpdated, TtFieldWrite, TtMoveOnlyWrite, TtSlotReplaced,
  TtRead, TtCutoff, MoveOrder, SearchReturn, RootSelection.

Each physical TT event has typed fields:
  position_key64, pointer/cluster/offset, write_sequence, generation, full_key_exact,
  writer_class, original_storage_bound, original_storage_depth,
  reader_requested_depth, reader_alpha, reader_beta, reader_return_value,
  read_role, eligibility/cutoff_taken.
The original SF16 low16 key is NOT enough to establish true writer identity.

Define empirical root-object operational fiber:
  F(P,p,e)=[G,A,N,I,M,T].
G=chess-law pin state; A=explicit operator opportunity; N=natural source-site calls;
I=per-operator intervention response; M=post-treatment path/TT/window mediator evidence;
T=transport across independently checked sources/engine families.
These are typed observational and intervention coordinates, NOT six independently
stored NNUE concepts.

## 3. Four separate propositions and falsifiers

**Proposition CSWP-1 — deterministic prefix equality (conditional).**
If E[0] and E[j] have identical fully specified initial states, all transitions are
deterministic and equal outside a treated site, and instrumentation is semantically
inert, then no semantic transition can differ before the first modified instruction
that is exercised. This follows from induction, not a new fundamental theorem.
Falsify operational attribution if a complete trace differs earlier.

**Proposition CSWP-2 — nonmonotonic effects and unknown mediator.**
For source-site intervention sets A subset B, the effect indicator
  1[Y_A != Y_0]
is in general not monotone in A. A cancellation counterexample suffices even in a
two-move stateless evaluator; observed S29/S28 global-SEE versus guarded-root SEE
nonmonotonicity is NOT automatically TT or αβ mediation.

**Proposition CSWP-3 — witness state is weaker than explanation causation.**
A TT read occurs, or its writer is traced, or its recorded bound is in an alpha-beta
window, does **not** entail that this TT record was necessary for final bestmove.
Construct counterexample: two independent root branches both guarantee the same
preferred move even when the traced TT record is removed. Therefore any strong
causal explanation must state an intervention language and do a selective replay.
A typed time-unrolled edge only licenses observational ancestry.

**Proposition CSWP-4 — mediation NON-identification from two traces.**
Suppose only (treatment A, observed intermediary B, output Y) is recorded. Two
structural models can agree on all observed deterministic runs but disagree about
Y under do(B=b'). Example for observed A=B=Y in {0,1}: Model 1 B=A,Y=B;
Model 2 B=A,Y=A. Both have indistinguishable (A,B,Y) observations, yet
manipulating B affects Y only in Model 1. Thus *even perfect source-to-TT
trace alignment cannot establish TT but-for mediation without an additional
TT-specific intervention or justified structural assumptions*.
This is a standard identifiability counterexample adapted to the engine, not
a claim of newly discovered causal theory.

## 4. What a source-window explanation certificate can assert

Certificate K is a typed structure
  K=(S,P0,Delta,Prelude,Gamma,Window,Controls,Counterfactual,Authority).

- S = bytes and legal source history, all cryptographic locks.
- P0 = frozen prediction and its negative-baseline comparison.
- Delta = exact source patch, first eligible and first EFFECTIVE execution event.
- Prelude = stable semantic common prefix to Delta; note rolling hashes alone aren't proofs.
- Gamma = aligned search-event, physical TT write/read, root candidate genealogy.
- Window = active alpha/beta at *actual decision*, not merely frame entry.
- Controls = original build vs passive OFF, no-fire/no-pin, cold repeat.
- Counterfactual = TT-specific or source-specific controlled perturbation and result.
- Authority = one tier among {LEGALITY_ONLY, SOURCE_SOFTWARE_CAUSAL,
  SOURCE_TO_SEARCH_PATH, TT_WINDOW_MEDIATOR,
  NEW_SOURCE_PREDICTIVE_TRANSPORT, LEARNED_NEURAL_FEATURE}.
  Each tier has positive and negative explicit admission gates.
If any required field is missing: ABSTAIN at that tier.

## 5. Earlier empirical data as hard limitations

C3X 0.14 earlier first-TT-return work linked full physical keys, writer classes,
stored depth and bound at first return. This does not itself identify how a later
root-object SEE code intervention first changes the TT solution tree.

TWIC 0.15 P2 (run 37906181077): 512 real SF16 processes, source guarded SEE fired
51/64, root bestmove changed 11/64, 64 no-pin sham controls equal. Frozen C1
accuracy 42/64 versus always-no-flip 53/64 **FAIL**; balanced classification
and 10/11 responder sensitivity are exploratory diagnostic signals.

TWIC 0.15 P3 (run 37907535134) bounded 64 subsequent search entries identified
a first path/window mismatch 20/64; P3-R2 (run 37908021714) expanded to 4096
postcandidate entries and found 35/64 first mismatches: 34 initial position/path
differences and one first same-position alpha/beta or depth mismatch. 9/11 true
root bestmove responders were observed within 4096; two remained right-censored.
This is **not** a TT mediation success result.

P4 experiment: native physical TT last-writer+bound and read/window tracer,
still POST-P2-OUTCOME, must be compiled with exact original OFF equivalence and
source-frozen roots; before results it has NO empirical PASS. If it succeeds,
it upgrades event provenance only; TT causal mediation requires a subsequent
intervention on the identified TT read or a common-prefix replay.

## 6. Research to create a defensible new contribution

A. A formal source-transformation/trace semantics and a mechanically checked
certificate verifier (Rust or Go independent of Python selection).
B. Genuine source-site patch and passive-control native equivalence.
C. TT physical-slot writer→consumer reconstruction with bounds and alpha-beta
window at the actual read/return.
D. Evidence of necessity/sufficiency from controlled TT mediator perturbation,
not merely path correlation.
E. Presealed external-source prediction beating a prior trivial baseline.
F. Multiple chess concepts (pin first, later passed pawn, overloaded piece,
discovered attack) under a source-only law grammar, negative controls, other engines.
G. A user-facing chess explanation that ABSTAINS when mediator evidence fails.

An academic result may be valuable even if E fails: document the impossibility,
underidentification or model inability, rather than retrofitting the feature set.

**Theory status:** CSWP_V0.2_FORMAL_PROPOSAL / CLASSICAL_TT_SOLUTION_TREE_COLLISION_ACKNOWLEDGED /
OBSERVED_TT_ANCESTRY_NOT_CAUSAL_MEDIATION / INDEPENDENT_TT_TREATMENT_REQUIRED /
FROZEN_C1_PRIMARY_SUPERIORITY_FAIL / FIRST_PATH_IN_4096_SCOPED_PASS /
OTHER_ENGINE_NNUE_AND_GENERAL_ONTOLOGY_HOLD.

## References/links

- Knuth & Moore, 1975, DOI 10.1016/0004-3702(75)90019-3.
- Stockman, 1979, DOI 10.1016/0004-3702(79)90016-X.
- Plaat, Schaeffer, Pijls & de Bruin, 1996, DOI 10.1016/0004-3702(95)00126-3.
- Allis, van der Meulen & van den Herik, 1994, DOI 10.1016/0004-3702(94)90004-3.
- Björnsson, 2024, DOI 10.3233/ICG-240256.
- SF16 original 68e1e9b3811e16cad014b590d7443b9063b3eb52 and C3X P2/P3/P3-R2 receipts.
