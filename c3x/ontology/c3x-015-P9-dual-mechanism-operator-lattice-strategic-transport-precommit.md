# C3X 0.15 P9 — Dual-Mechanism Court and Chess Concept Operator Lattice
## Precommitted research constitution, 2026-10-09

Status: P9 DESIGN PRECOMMITTED; P9 native outcomes NOT observed. C3X 0.15 OPEN; 0.16 NOT OPEN.

### 1. Central ambition and falsifiability
Discover whether law-level chess motifs and strategic plans have reproducible, source-specific computational contacts within actual search execution, and identify the conditions under which this contact changes competing root moves. Study conditions of failure and mechanism substitution as intensely as successful cases.

Never equate human motif labels with source-level operation, a source-level operation with causality, or a causal Stockfish result with neural concept representation. Prior alpha-beta, quiescence search, minimax, potential outcomes, strategic chess suites and debugging literature remain relevant prior art; any novelty concerns their inspectable synthesis in a runnable experimental measurement system. Preserve P1 C1 overall-accuracy FAIL 42/64 versus no-change B0 53/64.

### 2. Two independently meaningful cases with separate names
**CEFH — Check-Evasion Fail-High Gate, TWIC world #2.**
Preselected exact physical TT source target key 0x3dd7beae5d6596d5, ply4, stored UPPER and TT return14, reader window alpha130 beta131. On blocking that single early TT return, qsearch is in check, searches check-evasion native move391, child returns173, executes beta fail-high break and returns173. Both SEE arms report local target return173, but different final root moves: OFF d1e2, SEE ON d1d2. The local scalar is therefore NOT sufficient for root choice.

**RISR — Return-Invariant Search Reconfiguration, TWIC world #29.**
Preselected source key 0xf671dc20088633ad, ply4, UPPER return29, alpha130 beta131. On a single TT-return bypass, qsearch computes stand-pat29, considers three legal candidates including first child return -59 and eventually returns29. This recomputed value matches the original immediate TT return29, yet the OFF root can change from d1e2 to f3e5. Thus it is an experimentally meaningful **return-preserving but root-choice-changing** computational dissociation, NOT a useless negative case. The mediator may be TT rewriting, downstream reads, node/history state or root competition; none is assigned by fiat.

### 3. P9-A exact native two-case factorial (72 cold processes)
For each world (2), SEE arm (2), intervention (9), and cold independent repeat (2), execute original Stockfish 16 source commit 68e1e9b3811e16cad014b590d7443b9063b3eb52 with classical Use NNUE false, Threads1, Hash16MiB, MultiPV1, depth12. Do not replace target edges after outcomes. Two-case selection is AFTER prior P6 outcomes: this is targeted mechanism reconstruction rather than new provider-blind generalization.

The nine intervention regimes are:

I — original same TT early return, untouched; P7/P8 exact core-UCI sham.
V — original early return delivering reader alpha130 instead of stored score (existing P7), without qsearch continuation.
B — block exactly once the preselected TT early return (existing P7), enabling qsearch.
G — B plus suppress exactly one observed source-local CEFH beta break (world2 target fullkey+ply+check-evasion native move391+child score173+beta131). Keep original qsearch search semantics elsewhere. World29 MUST show null gate exposure; retain its no-hit negative-control result.
W — B plus suppress exactly one qsearch terminal TT WRITE at that exact source key/ply, preserving original target-local qsearch returned value. Tests whether the actual qsearch state write contributes to later root choice even without changing the delivered scalar.
L — B plus execute full qsearch continuation but clamp the one target-local qsearch return to the previously frozen original TT value (world2=14, world29=29). Earlier qsearch side effects remain, so isolate delivered scalar from computation side effects, without asserting these are natural independent mediators.
D129, D130, D131 — B plus at most one first target qsearch child return substitution to scores 129,130,131 at world29 child original -59 and matched move source ID729. These probes intentionally test decision boundary behavior, NOT valid chess evaluations. World2 is mandatory noncontact control for these arms.

Split the program as P9-A1 (I,V,B,G,W,L: 48 real native searches) and P9-A2 (D129/130/131: 24). Publish all 72 rows including nonfiring, failures, first source event and site-specific number of source-exposed interventions.

**Hard technical gates:** original P0 R2/P2/P6S0/P6S1/P7/P8 source SHA check; source target first-key/physical slot/writer/depth/bound/reader window equality; all I/V/B prior native score/PV/nodes/bestmove exactly reproduced; identical cold repeats; no changed chess legality; no engine outcome-dependent target reselection. A zero-exposure arm is retained as NO_CONTACT, never silently replaced.

**Outcome vector:** categorical root UCI, complete last PV/score/nodes, first reported root PV difference depth, target qsearch scalar and target branch path, qsearch TT writer and stored bound, whether downstream TT physical slot was read, alpha/beta frame transitions, elapsed search-event ordinal, exposure mask, and censoring. The categorical root move is NOT a real number. Binary SEE flip cannot encode which arm changed: P7 world2 already demonstrated opposite arm-local contrasts with equal binary results.

**Mechanism court hypotheses:**
- H-G: the case2 beta break gate has no impact on final chosen move under the specified cold P9 intervention, despite the local break having fired. Failure to reject is useful.
- H-W: blocking the single qsearch TT write in case29 leaves the original B final move unchanged. Any root change is a positive source-specific write intervention effect, not automatic proof of all TT natural mediation.
- H-L: when qsearch body runs yet final transmitted scalar equals the original TT value, the root response still changes in case29. If it does, scalar-only mediation is falsified under L; if it does not, the side effects measured here were insufficient under the tested treatment.
- H-D: the local candidate child score threshold probes do not create a change in target path at alpha/beta crossing. Publish even if they fail to contact or produce only numerical shifts.
- H-transport: no cross-source generalization is assumed.

### 4. P9-B chess concept and operator ontology — 5 levels, NOT PIN-ONLY
L0 LEGAL GEOMETRY: pin, ray occlusion, check, king safety constraints, discovered attack geometry, legal check evasions. Independent legal move validator. Labels based only on geometry do not establish any tactic.
L1 TACTICAL SEQUENCE: absolute and relative pins, skewer, interference, deflection, decoy, removal of defender, clearance, discovered attack, fork, overload, zwischenzug, exchange sacrifice, mating net, promotion. Require actual candidate move and legal defense sequence; geometric hints are tagged CANDIDATE until counterdefense analysis.
L2 LONGER-TERM STRATEGY: king safety/activity, pawn weaknesses and structure, passed pawn races, space, outposts, open files and diagonals, center control, initiative, seventh rank invasion, minor-piece imbalance, prophylaxis, simplification/trade transition. Require alternative plans across several depths or positions; a one-node tactical event cannot be promoted to strategic evidence.
L3 SOURCE OPERATORS: SEE, move ordering, qsearch futility, stand-pat, alpha/beta boundary, TT writer/reader/bound/depth, pruning and extensions, HCE vs NNUE evaluator, iterative aspiration/root competition. Record compiled C++ source location and native event ID.
L4 CAUSAL EVIDENCE/TRANSPORT: legal certified / source observed / exact matched intervention / external heldout confirmed / ambiguous / refuted. Separate chess truth from game-engine behavior and human coaching value.

Use typed multi-label event hypergraphs, never a forced single exclusive motif type. One position can have pin + skewer threat + overload + initiative simultaneously. Edges never automatically promote from OBSERVED to CAUSAL when a downstream move changes.

### 5. P9-C STS strategy contact and independent authentic PGN
The exact source file STS1-STS15_LAN_v3.epd was recovered from Research OS generic 00_INTAKE and moved to C3X's strategic/tactical source folder. Source is 288513 bytes, SHA256 d7a33ae6cf2fb5f3f18ef1b904cca07dce2cd0458edcf60644f59d4d9e28c07b, 1500 EPD lines across 15 sections of 100. Categories include Undermine; Open Files and Diagonals; Knight Outposts; Square Vacancy; Bishop vs Knight; Recapturing; Offer of Simplification; Pawn Advancement; Simplification; King Activity; Center Control; Pawn Play in the Center; and 7th Rank. Do NOT guess definitions of abbreviations AKPC and AT. Its bm/c0 fields are annotated test preferences, not a certified chess oracle.

Preregister source-only EPD parser, duplicate 4-field board FEN audit, per-section game-independent grouping, legal recommended moves, and section-balanced heldout splits BEFORE using bm/c0 score labels as training or target leakage. Then run actual engine motif contact controls using original source code/TT effects, and a disjoint authentic new-provider PGN. STS isolated EPD has no complete match history and cannot serve as a replacement for TWIC game-history source. No selection solely on whether engines already changed root moves.

Source-origin stress axes for stage P9-C/D: different actual game provider, search depth8/12/16/20, TT hash16/64, cold vs warm, HCE and NNUE, engine source version and second engine family. Pre-register per-axis claim and abstain if comparable native operator absent. Claim no universal tactical ontology from a two-case effect.

### 6. P9-D typed evaluation / falsification
The P1 failure remains the prospective baseline. New motif/operator predictions must outperform full no-change, law-only, static operator, and search-context baselines on future frozen independent contexts; class imbalance must be addressed using both overall accuracy and balanced accuracy/recall/precision. Report all failure types. Prior art includes classic search theory, game strategies, tactical motif corpora, instrumentation, and causal inference; CSWP proposes an auditable combination, not a pre-existing proof of an entirely new discipline.

### 7. Custody, author and history
Original TWIC 1665 raw ZIP discovered in generic Research OS 00_INTAKE, SHA256 23097bbf152d9afed810890456027ce639719f7a4ef4c723898730d391b347b3; inner twic1665.pgn SHA256 642f458c6ef8c5661e62a5f056ad225cabf29a4b12c65be0f834a1e60ad610a6. Moved by ID to private C3X/01_SOURCE_ACCRUAL_RAW/TWIC_1665_PRIVATE_ORIGINAL. Not hosted on public GitHub due TWIC publisher use restriction. Three Lichess monthly .pgn.zst, STS original and G8 court ZIP similarly moved from generic intake, preserving IDs. GitHub commits must be authored/committed by WhoSia, Actions are read-only experiments; Notion single Lab holds scientific evolving conclusions.

**Current verdict**: P9_PRECOMMIT_CONSTITUTION_ONLY; NO_P9_NATIVE_RESULT_YET; TWIC_ORIGINAL_RAW_PRIVATE_DRIVE_SHA_PASS; STRATEGY_STS1500_PRESENT; ORIGINAL_P1_C1_ACC_FAIL_PRESERVED; COMPLETE_TT_MEDIATION_HOLD; C3X0.16_NOT_OPEN.
