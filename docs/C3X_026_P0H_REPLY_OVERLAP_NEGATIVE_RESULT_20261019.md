# C3X 0.26 P0-H — Reply-Set Overlap Is Not a Strategic Reason

Status: source-derived descriptive negative finding, not new legal chess proof or causal identification.

## Question and dataset
Cross-compare the opponent's two *reported* best replies from each competing first root on the same index, evaluator and nominal depth, using existing P0-F HF1 JSON (whose P11 source SHA is 18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2). This is a MultiPV2 visibility-window comparison, not the set of all legal opponent responses. Two roots can share identical UCI moves but those moves occur on different post-root boards and are not necessarily the same chess plan.

## Examples, checked directly from uploaded P0-F JSON
- index42 CLASSICAL after Bc5 vs Bf8: d17 [e2g4,d2f4] vs [f2f4,e1d1]; d19 [e2g4,d2f4] vs [e1d1,f2f4]. Overlap **0/2 at both depths**. Persistent P10 inversion development case.
- index43 NNUE after Re8 vs Qf5: d17 [f1d1,f4d2] vs [f4d2,f4c7] overlap **1/2**; d19 [c1d1,f1d1] vs [f4d6,f4d2] overlap **0/2**. Persistent P10 inversion development case.
- index47 NNUE control Bxe5 vs Qxe5: d17 [c4d5,d1e2] vs [c4d5,d1e2] overlap **2/2**; d19 [c4d5,d1e2] vs [c4d5,d2f3] overlap **1/2**. Transient P10 inversion resolves by depth20.
- index99 CLASSICAL control Rxc2 vs Kg2: d17 [c6c2,c6d6] vs [c2d2,c2c5] overlap **0/2**; d19 [c6c2,e6g4] vs [c2d2,c2c5] overlap **0/2**. P10 locked depth20 cp tie; not a strict sustained inversion.

## Falsification consequence
Hypothesis that 'disjoint reported opponent top-two sets are a specific or sufficient explanation of *persistent root-order search inversions*' fails on these controls: 99 has disjoint observed replies just like 42. This does not rule out strategically meaningful differences between roots; it rules out using the coarse overlap observation as proof or identifying cause.

## Ontological correction
Distinguish (i) legal availability of a reply on each post-root board, (ii) top-two *reporting* by engine, (iii) same UCI coordinate move on two different boards, (iv) tactical/strategic consequence of that reply, (v) causal influence on engine root choice. Distinct measures and distinct types of witness. No inference across categories without intervention.

## Research priority
P0-G legal-response identity enumerator is committed as source at tools/C3X_026_P0G_WITNESS_SET_AUDIT.py, GitHub WhoSia commit 7425151301ff56f7a570b671e30fd9e21ad2fcb1; not yet native executed. Actual next discriminating test should pair concrete legal moves with *the consequence* they address (king threat, defended square, forced exchange, restricted pawn break), fixing opponent policy and short horizon and registering opposite predictions. Do not seek explanatory novelty from arbitrary summary statistics. No WSL or Stockfish required merely for this P0-H negative result. Keep 0.25 name and all historical negative evidence.
