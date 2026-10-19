# C3X 0.26 P0-I — Counterfactual Consequence Fibers and Distinction Survival

## Why not import a human-choice theory?
The project's original question is **why this chess move rather than its near-equal legal rival**, not how a human subject internally values a position. The data are chess states, legal trajectories and algorithm-controlled reporting. Start from those mathematical objects; human understanding comes later as independent validation.

## Formal research proposal (not a discovered law)
Fix an initial chess state with **full prior history** h, rival legal first moves a,b, response policy family P, horizon H, and observable chess predicates V. Define a bounded continuation *fiber* F(h,a;P,H,V) as the set of V-projected legally realizable subsequent action–state histories subject to P. A descriptive distinction witness is (p,t) for a preregistered predicate p and intervention/response t that leads to divergent outcomes; attach its legal move sequence, state and horizon. Do **not** identify chess advantage merely from set inequality, or infer algorithmic causation without a separate search intervention.

A 'survival profile' D_H may represent which distinctions remain observable through H under P and V; do **not** assume D_H is monotone in H. Branches can diverge, reunite at one state, and diverge again under different policies or unrecorded repetition histories. Require explicit proof before defining any quotient equivalence over projected states; equal FEN4 or FEN6 is a weaker relation than history-equivalent games.

## Immediate theoretical negative results
1. Mobility-count collapse: two post-root positions can both offer 35 legal opponent moves (P0-F idx47), yet this says nothing about identities or tactical outcomes.
2. Large count mismatch not characteristic of a persistent search inversion: idx99 negative control has 29 versus35 legal opponent moves (and 0 vs1 available check), greater gap than development idx42 38/40, idx43 36/37.
3. MultiPV2 reporting disjointness is not characteristic either: idx42 CLASSICAL and idx99 CLASSICAL each have 0/2 observed shared opponent replies at both depths; idx99 does not meet P10 strict sustained reversal criterion.
4. Source-valid P0 full-state replay gave **within-root 13/72 board+turn and FEN4 recurrence, only 8/72 FEN6 recurrence; cross-root FEN6 4/36**. In idx42 classical Bf8, depth17 four FEN4 checkpoints but zero FEN6; depth19 FEN6 two checkpoints. Thus mere same board appearance is not history-complete consequence equivalence.

These results rule out *sufficiency* of these coarse descriptors for labeling the specific P10 phenomenon in the selected cases; they do not establish a unique novel affordance law or chess-optimal move.

## Identifiability principle
For a fixed finite experiment set T, two rival causal/strategic accounts indistinguishable on all registered observations have no identified preferred explanation in this experiment. Define the smallest **legal witness certificate** subject to a declared vocabulary and policy rather than smallest persuasive prose. Explicit abstention is an admissible output.

## Computational development and outcome
A standard-library-only, read-only P0-I audit combines two pre-existing validated artifacts and tests exact source SHA, counts, invariant root descriptors across evaluator/depth, and top-two reply overlap as a finite observational quotient. It was ACTUALLY EXECUTED in assistant's current container and returned **P0I_PASS 144 72 9 36**. Script SHA256 `103fb2dcc9829cd77c109250c3b7925413aa046a21d40535280901312f4d6fa7`; JSON SHA256 `c062e43bf7c8689dd8642a0b9f381b3f9a85bb248281f5097229b0bc9eb81e30`. It does not replay chess moves itself; its inputs are independent previous WSL legal replay and P0-F outputs, with recorded limitations. No new Stockfish or WSL run.

## Next scientific gate (theory first, execution second)
P0-J should select **specific action–state consequence predicates**, such as which exact defending move neutralizes which immediate legal threat at H=2, and what intervention would invert that relation. Include selected controls 47 and99. Prefer a small legal two-ply certificate over a large list of scalar metrics. Hold off on any engine causal claim until the search protocol has its own falsifying intervention. New case/game/event heldout must stay separate from P10 outcome-selected development cohort. Keep historic C3X 0.25 unchanged, official C3X 0.26 title unchanged, BOT_CONTRIBUTION_ZERO.
