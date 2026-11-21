# C3X 0.31 / P3-X4 — Two Histories, Third Winner: Cross-Root Computational Spillover in Bounded Chess Search

**2026-11-21 · Source-derived retrospective discovery; physically confirmed P2/P3 source experiments · no new native searches.**

## 0. Definition of the scientific result

The actual P2 source intervention targeted a **specific search return associated with a single named root candidate**. In all **14/128** original 32k-node P2-B2 final move flips, either the previous best root or the new best root was that target; these were **8 target displacements** and **6 target promotions**.

However, when P3-X2 imposed an explicit completed-depth cap, the original **signed same source event** in **P2-056-1** at depth cap 13 induced a different **third** root choice:

| Real physical source property | Actual original value |
| --- | --- |
| Original signed root candidate associated with the intervened descendant | **\`h5e2\`** |
| Original independent cold sham bestmove | **\`b8d8\`** |
| Futility-only arm final bestmove | **\`b8d8\`** |
| Futility + null suppressed arm final bestmove | **\`f5h3\`** |
| Requested \`go\` limits | depth 13, nodes 32,000 **or** depth 13, nodes 64,000 |
| Actual last public UCI completed depth in both arms | **13** |
| Real last reported nodes sham / treated | **24,504 / 24,287** |
| Original OPEN signature, targeted close flags, repeated cold sham/treatment | **All matched physical source controls** |
| Number of independent original source event/game units responsible for two reproductions | **ONE** (\`P2-056-1\`) |

At depth cap **14**, the same source event under both node-limit conditions instead moved the final bestmove from \`b8d8\` **to the targeted candidate \`h5e2\`**. At the original uncapped P2 32k-node horizon, \`P2-056-1\` also changed \`b8d8→h5e2\`.

**This matters:** the source intervention's final decision effect is not necessarily confined to promoting or demoting its named root candidate. In a bounded stateful search, changing the computation underneath root \(r\) can alter the winner between other roots. This is a **decision-level causal spillover counterexample to a single-root isolated score-change model**. It does not identify the particular TT/history/aspiration/iteration-budget pathway.

**Evidence:** [P2 original 640 genuine searches and 128 physical outcomes](C3X_031_P2_1669_B2_B3_PROSPECTIVE_SOURCE_TEST_RESULTS_20261121.md), [P3-X2 new 60 actual depth/node-horizon searches](C3X_031_P3_X2_DEPTH_NODE_HORIZON_RESULTS_20261121.md); source original outcome archives [P2-B2 Drive](https://drive.google.com/file/d/1e4kBfW_-HYbMF5a3imX2ab9XKfmmmyXw/view), [P3-X2 Drive](https://drive.google.com/file/d/1gmWlaw6xG-SzrBp0LSY33YqX0owSXLbZ/view). Original P2/B2 native result SHA256 \`be66a985016b4ceaae1379c64ee0f6347c3a2e8c4fd3660ceb394227ac237df1\`; original X2 JSON SHA256 \`3c90be5bd0803937a6c9aaf8e55e6b15443c0a5c4f9a71605e13af28cc4da085\`.

## 1. Minimal theorem — an isolated candidate cannot produce a third-root winner

For a finite set of legal root actions \(M\), a fixed target \(t\in M\), deterministic scores \(q_m^a\), a fixed total tie-break order, and action \(Y^a=\arg\max_{m\in M}(q_m^a,\text{tie priority})\), assume only the targeted score may depend on intervention \(a\):
\[
q_m^1=q_m^0\quad\forall m\ne t.
\]
Then
\[
Y^0\ne Y^1\;\Longrightarrow\;Y^0=t\;\lor\;Y^1=t.
\]

**Proof.** The relative ranking and tie-breaking of *all non-target* moves remains identical under the two interventions. If neither winner is \(t\), both must be the fixed highest-ranked non-target move. They therefore cannot differ. Contradiction.

The actual source intervention \(\operatorname{do}(\text{skip F}=1,\text{skip N}=1)\) at the signed \`h5e2\` child produced **\`b8d8→f5h3\`** at the same requested depth cap, with neither chosen root equal to \(t=\texttt{h5e2}\). Thus the simple fixed-all-other-root-score hypothesis is false **in these source settings**. At least one of its assumptions fails: other candidates' finite-budget estimated scores, actual root search schedule, internal state, ordering or tie-breaking cannot be modeled as constant independent values under this intervention. We have not measured which of those changed.

Counterexample avoidance: a new \`go depth 13\` across arms still uses **24,504 vs 24,287 actual nodes**. Equal nominal depth is *not* matched computational state; do not claim an equal-nodes proof or TT-mediated effect. The two node *caps* are two search-condition replications of **one** event, not two independent chess situations.

## 2. Two orthogonal histories — do not confuse game state with search state

**Game/rules history** \(H_{\text{game}}\): actual played move sequence; determines repetition claims and draw rules alongside placement, turn, castling, en-passant, halfmove counter. Merely matching FEN placement or four fields does not imply equal repetition/legal game-value context. This is related to the classical *Graph History Interaction* problem in game-tree search, and to Stockfish16's own rule50-associated TT cutoff guard. A semantic alias between two tournament/game histories may also defeat a naive "fresh game" sample.

**Computation history** \(H_{\text{search}}\): TT entries plus generation/age, history/continuation scoring, per-root iteration attempts, alpha–beta windows, search stack, actual node allocation, remaining runtime budget. These variables describe *how* a bounded engine evaluates the same full legal game history, not what the perfect-information chess game's mathematical value is.

Write the bounded deterministic search as
\[
Y=\pi(P,H_{\text{game}},H_{\text{search}},B;A),
\]
where \(P\) is the board/rules state, \(B\) is computational budget/horizon, and \(A\) is the targeted source gate. The exact decision process should be modeled as a **temporally unrolled** causal program, not a static "one value per root" table. A more operational decomposition is
\[
A_{\text{gate}}\to C_{\text{child return}}\to
 (S_{\text{TT writes}},S_{\text{history updates}},S_{\text{budget/ordering}})
 \to C_{\text{later root estimates}}\to Y.
\]
This is a **candidate graph**, not a verified causal graph for the individual mediator paths. Earlier observational R39 TT data covers *pre-gate* TT state only; it rules out an originally useful bound/move at the exact child in six incremental null cases, but says nothing conclusive about downstream TT writes elsewhere.

This two-history distinction also prevents an invalid "chess position is non-Markovian" claim: when **complete chess-rule history** is retained, the rules/game can be described with an appropriate Markov state. It is the **bounded searcher's board-only projection** that is insufficient to specify its computational decision.

## 3. Three kinds of transport must be evaluated separately

| Transport | Scientific input/intervention | Observable question | Existing C3X evidence | Valid claim level |
| --- | --- | --- | --- | --- |
| **Branch/source transport** | \`do(F,N)\` at exact R33 child gate | Does original final UCI winner change? | P2 14/128 valid flips; P3-X1 2×2 causal factorization (0,0,8,14) | Repeated original source total effect |
| **Computational-state transport** | Freeze or swap an *actual post-gate* TT/history/budget state at a signature-matched time | Does restored state block/restore a root change? | P3-X3 7/7 pre-gate observer parity; **no state restoration** | Mechanistic mediator **HOLD** |
| **Chess-plan transport** | Independent legal opponent reply branches and independent judge | Does a root decision retain strategic merit under future responses? | Previous R37 third winner overturned a naive original preference; none for new P2-X2 third root | Strategic superiority **HOLD** |
| **Human explanation transport** | Matched, consented learner explanations with blinded adjudication | Does source-grounded model improve understanding/decisions? | Protocols only, no real learner observations | Human benefit **HOLD** |

In Russell & Wefald (1991), *Principles of Metareasoning*, computations themselves can be evaluated as decisions under scarce resources. **C3X's currently measured quantity is not yet the value of computation**: the source intervention can change a move, but no independent downstream chess utility/cost function has been estimated. The observed \`b8d8→f5h3\` third winner is a compelling boundary case for *which computation affects which decision*, without claiming it is beneficial.

In Geiger et al. (2025), *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*, the validity of a high-level causal model depends on correspondence under interventions, not just observational prediction. That suggests treating \`root_is_target\`, \`TT_pre_gate\` or \`search_depth\` as **candidate abstraction variables** whose adequacy is tested by physically realizable interventions. Do not invent a "minimal sufficient state" by allowing \(\phi\) to encode the entire raw search trace, the output label, the game ID, or a post-treatment root choice; that would be a vacuous high-capacity decoder rather than explanatory compression.

**Primary references and non-duplication:**
- Russell & Wefald, *Principles of Metareasoning* (1991), DOI https://doi.org/10.1016/0004-3702(91)90015-C — established bounded rational metareasoning, **not C3X novelty**.
- Geiger et al., *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* (JMLR 26, 2025), https://www.jmlr.org/papers/v26/23-0058.html — generic causal abstraction/interchange and graded faithfulness are **established prior art**; original paper already in user-owned Research OS.
- Stockfish16 exact pinned [\`src/search.cpp\`](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/search.cpp) and [\`src/tt.cpp\`](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/tt.cpp) — native source of algorithm semantics; its \`TT.probe\` generation refresh means a *second* "observer" probe can itself change memory.
- *Graph History Interaction* sources include the 2004 AAAI paper *A General Solution to the Graph History Interaction Problem*, https://s.aaai.org/Papers/AAAI/2004/AAAI04-102.pdf; its game-history issue is related but **not equivalent** to the new cross-root finite-search result.

## 4. A falsifiable P3-X5 mechanism ladder (not yet executed)

The next true physical source study should **not** jump straight to copying a whole TT or calling source telemetry a causal mediation proof.

1. **First divergence ledger:** In the same original source event/iterative-depth window, monitor the actual **candidate return and public root attempt sequence** for \`P2-056-1\` under sham and FN. Identify the first root other than \`h5e2\` whose *actual source producer*, score bound or search timing diverges. Log before/after original \`go nodes\` consumption, exact attempt and root candidate IDs, no additional \`TT.probe\`. The exact original event, full legal move history, 32k/64k node caps and depth13/14 matrix are frozen in advance. Preserve no-contact and observer effect failures.
2. **One real mediator family at a time:** Only if source traces identify a state-write/read influence, physically freeze/swap a **single** post-gate TT entry or a narrow history/ordering slice at a defined checkpoint. Verify full original source key identity, TT entry age and bounds, paired restore and reverse-swap, source-root producer parity and complete node differences. If the restore prevents the third-winner transition, that is a candidate *mediated* effect within the instrumented scope; otherwise the candidate mediator is falsified for that case. Do not select one only because it produced success.
3. **Budget-only control:** Replicate the originally *reported* sham/treated node-work differences independently by fixing a more detailed actual stopping schedule. A \`go nodes\` limit is **not** an equality constraint on visited nodes or completed iterations; do not equate node caps with node-matched mediator controls.
4. **Third-root chess adjudication:** On the complete original position, compare actual \`b8d8\`, \`h5e2\` and \`f5h3\` under independent engines and legal opponent responses, with original move-count/draw-state carried over; allow an unseen **fourth** winner. This is not a follow-on of a previously victorious source move and should not presume a preferred strategic line.

**Acceptance limits:** The first-divergence ledger is observational mechanism discovery, not sufficient causal identification. Actual source manipulation must have before-frozen target signatures, cold-matched shams and reverse arms. The sample remains **one exposed game**, and neither 2 reproduced horizon conditions nor an abundance of trace rows creates independent-game statistical power. A later unseen cohort is needed for a general claim. Minimality of \(\phi\) additionally requires ablations and a complexity/cost constraint, otherwise the full trace trivially predicts itself.

## 5. Decision

**Scientific verdict:** \`PASS_ORIGINAL_SOURCE_DECISION_LEVEL_OFF_TARGET_COUNTEREXAMPLE / MECHANISM_FAMILY_UNIDENTIFIED\`.

This is a **newly articulated, directly falsifiable C3X research hypothesis** grounded in genuine native source results, **not a claim that the underlying causal abstraction, metareasoning or graph-history theory was newly invented here**. We now have a specific *third-root* counterexample to an overly local decision model, an explicit computational alternative set, and a concrete experiment that can separate path-level influence from post-source-state mediation. Preserve the contrary P2 target-anchored 14/14 cases together with P3 off-target 2/11 switch cells, not just the interesting anomaly.
