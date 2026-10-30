# C3X 0.29-P4 — Context-Indexed Explanations and Real-Chess Monotonic Falsifiers

**2026-10-31 | Research synthesis; theoretical proposition + independent recomputation from archived development evidence.** This increment DOES NOT claim a new native Stockfish run, causal path mediation, or demonstrated human concept transfer.

## The foundational explanatory separation

C3X's long-term ambition is an explanation that distinguishes:
1. **Chess-semantic reason** S(s,a,b; Q,R,H): how alternative root moves differ on a declared, legally checked predicate Q, opponent response set R and continuation horizon H;
2. **Engine-computational reason** M(s,c; I): why a particular engine with execution context c and physical intervention I selected a specific root move;
3. **Link** L: source- and execution-matched intervention-to-choice evidence that supports aligning M and S, NOT mere simultaneous observation;
4. **Human transfer** H: whether an explanation teaches transferable decisions on heldout chess positions (still unmeasured).

Source of truth in code/research hierarchy: prior 0.25 P13-R4 and P14-P6 native receipts, 0.27 P2B/P3 legally enumerated branches, and P11 preselected 9-case frozen manifest. Notion records are accepted as the historical working ledger; redundant source-level reauditing is not a research deliverable.

## Proposition 1: fixed board-only explanation cannot explain opposite engine decisions

Let x be the complete original legal chess state (board, rights, move counters and, where relevant, repetition history). Let c0 and c1 be distinct execution contexts or physically manipulated engine policies. Suppose the actual engine decisions differ at fixed x:

Y(x,c0)=a, Y(x,c1)=b, and a != b.

Then there is no deterministic choice predictor g(x) depending ONLY on x which equals both observed decisions. If a candidate explanation uses a fixed context-invariant abstract chess feature map Q(x,a), Q(x,b) and a fixed comparison rule F, then F(Q(x,a),Q(x,b)) similarly cannot correctly predict both decisions without some contextual argument or context-dependent change in evidence. Proof: identical function inputs must yield identical outputs, contradicting a != b. The theorem is about explaining the engine's *observed decision*, NOT about objective chess value or all semantic descriptive statements.

Concrete native development witness: 0.25 P14-P6 source-native exposed July-2026 case M6-28 on the SAME original chess position, SHAM bestmove f1d1, FIRST and UPPER physical TT intervention bestmove a1a5, LOWER intervention bestmove f1d1. Source: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-025-P14-P6-native-source-qbound-tie-cegar-20261012.json . This illustrates a dependence on engine execution context, not a newly measured AGI/chess improvement and not a path-specific TT->SEE causal effect. Exposed development only.

**Implication:** A generic explanation of chess move quality, even if factually true, is not a faithful explanation for every Stockfish selection. C3X should have two individually auditable outputs: 'chess outcome consequence' and 'engine execution-specific cause'. Report a bridge only when uniquely source-aligned evidence exists.

## Proposition 2: real development positions reject common one-scalar monotone stories

Input 1: P11_SOURCE_FROZEN_9_RESPONSES.json (post-P10-selected development cases, NOT heldout) from Drive https://drive.google.com/file/d/12sU-xAjtlwoj77IhdugRinCMi0-O_EZB/view . This independently records P10 FULL original winner at both depths 18 and 20 for cases 42 (d6f8) and 43 (a8e8). LOCKED winner differs; the point here is only to name the FULL winner, not to attribute P10 choice to native TT policy.

Input 2: original 0.27 P3 legal H2 certificate data C3X_027_P3_NATIVE_TREE_CLAIM_RESULTS.json (personal Library), generated from native-validated P2B exhaustive legal replies and with explicit limits on independent legality replay.

| Index | Candidate | FULL winner? | All legal opponent replies | Opponent capturing replies | Capture-response fraction | Conditional immediate recapture |
|---|---|---|---:|---:|---:|---|
| 42 | d6c5 | no | 38 | 1 | 1/38 = 2.632% | TRUE |
| 42 | d6f8 | YES | 40 | 1 | 1/40 = 2.500% | TRUE |
| 43 | a8e8 | YES | 36 | 3 | 3/36 = 8.333% | TRUE |
| 43 | d5f5 | no | 37 | 3 | 3/37 = 8.108% | TRUE |

Consequences under the stated two-case scope:
* Winner's opponent legal-reply count is HIGHER in case42 (40>38) but LOWER in case43 (36<37). Thus no globally fixed strictly increasing OR decreasing preference on opponent legal reply COUNT alone matches both winners.
* Winner's capturing-reply fraction is LOWER in case42 (1/40 < 1/38) and HIGHER in case43 (3/36 > 3/37). Thus a fixed strictly monotone preference on capture-response DENSITY alone cannot match both.
* Opponent capture-reply absolute counts are tied within each pair, and the qualitative conditional-recapture predicate is TRUE for both candidates in both positions. No strict tie-independent ranking can be derived from them alone. Counts/fractions enumerate legal opportunities, NOT empirical probabilities or opponent strength.
* 0.27 P3 full universal recapture claim is FALSE for all 18 root states; capture-conditioned claim TRUE in 15/18 states and FALSE in 3. Of the 9 compared source position pairs, the conditioned predicate distinguishes ONLY negative control index99, while development positives42/43 have identical TRUE/TRUE signatures. This refutes its use as a single-feature discriminator for those positives, **without** implying tactical recapture is generally irrelevant to chess.
* The capture-conditioned q covers just one of 38/40 all legal opponent replies in case42, or three of 36/37 in case43; this fraction is the logical quantification support size, NOT a probability and NOT a general explanation-strength score.

No claim about all possible chess strategy features, combinations, nonlinear rules, move strength, or independent prospective generalization follows from these two cases. This is a narrow real-data falsification of simple storytelling heuristics.

## 0.29 research formulation: explanatory faithfulness as contextual correspondence

Explain observed decision as E(x,c,a,b) = (S(x,a,b), M(x,c), L(x,c,S,M), uncertainty). The bridge L must be earned; do not claim a natural indirect effect without independent identifiability assumptions.

Proposed hierarchy of outputs:
- **DESCRIPTIVE TRUE:** S predicate proved for one candidate on a precise legal-response support.
- **CONTRASTIVE:** predicate/qualified certificate differs between alternatives in same root.
- **DECISION RELEVANT:** context-indexed physical engine intervention changes/keeps actual root choice with predeclared timing and censorship; possible even when S has no contrast.
- **ALIGNED:** source-matched within-run mechanism trace and explicit semantic continuation certificate pertain to the SAME root move, opponent policy, and intervention comparison, with exclusion of alternative explanation leaks where possible.
- **TRANSFERRED:** independent new legal chess positions and human comprehension gains; not yet achieved.

Failure of the simple q is a useful negative result: avoid post-hoc reengineering an impressive-sounding predicate to force 42/43 to match. Next predeclare an interpretable bounded concept vocabulary (threat preservation, forcing checks, material-exchange safety and king exposure) and define exactly what chess rules and horizon license each. Use previous 0.27 P2B states as DEVELOPMENT, and preserve controls 47/99. Some concepts require deeper legal exploration beyond already-enumerated P2B reply/recapture lists: explicitly mark UNKNOWN and collect minimal additional traces, not invent outcome labels.

For native M: reuse 0.25 P13-R4's real QSearch TT-score parent assignments (24), publicly joined Q-parent bestValue (18), and P14-P6 real root change. Do not rerun its original experiment for bookkeeping. Separate that evidence from still-unproved single-chain TT->SEE->final root E2 and main/LMR/PV branch coverage.

**Promotion:** C3X 0.29 remains formally OPEN as mathematical/explanatory model development. These are real explanatory non-identifiability and two-case feature rejection results, not a universal chess explanation or AGI-level performance claim. July28 is outcome-exposed. September64 confirmatory HOLD (index20 castling rights and historical disjointness). GitHub authorship must remain human; never use bot commits.

## Corollary: obstruction to an interventionally faithful board-only causal abstraction

Let the low-level deterministic engine be L, the board-semantic abstraction be z=alpha(x) and an abstract explanation be a fixed deterministic rule h(z). Under TT treatment I, the original legal board x and all legal continuation sets are unchanged; only source execution changes. If the native root action changes between I=SHAM and I=UPPER, a diagram demanding h(alpha(x))=Y_L(x,I) for BOTH I values cannot commute. Its left inputs are equal while its demanded right outputs differ. This is a specific *intervention-faithfulness obstruction*, not a failure of chess semantics and not a proof that all causal abstractions are impossible.

A high-level model can potentially remove the obstruction by conditioning its mechanism state or transition on the intervention I and relevant source-derived events (TT bound, search window, actual return, ancestor consumption, root candidate competition). Merely adding a label I is necessary for distinguishing these two outcomes but is **not sufficient** to prove an accurate causal abstraction outside this observed exposed case. A single fixed x where two deterministic outcomes are witnessed requires at least two distinguishable high-level context states if both outputs must be reproduced; this connects to older 0.25 dynamic behavioral quotient work and should not be presented as a new general information-theory theorem.

Reference: Geiger et al. (2025), *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*, archived Drive original https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view ; use its interventional-comparability framing, not a claim the source proves this C3X-specific data result. Actual physical counterexample comes from cited P14-P6 Stockfish16 native receipt.

### Falsifiable next protocol (no existing native success inferred)

For each same pinned legal root x, freeze rival candidates A,B and a predeclared set of software interventions I, and report: native decision Y(x,I), causal path status (P13-R4 Q-direct / Main-LMR-PV UNKNOWN, E1/E2), semantic chess proof statuses for A and B, and whether a learned high-level model can predict the *difference* Y(x,I0) vs Y(x,I1) out of sample. Score failures and abstentions; compare a chess-only model h(alpha(x)) to intervention-aware h(alpha(x),I,z_native). Split heldout by real source games/provider/time, not randomly by derived arm. This is a research design, not a completed model.
