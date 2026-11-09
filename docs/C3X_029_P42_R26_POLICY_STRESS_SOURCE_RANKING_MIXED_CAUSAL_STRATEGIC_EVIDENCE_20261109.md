# C3X 0.29 — P42/R26: Policy-Conditioned Opponent Stress Ranking, Native Rival Test, and Falsifying Sahel Result

2026-11-09 KST. Mainline R26 B+E. **Scientific status: exploratory, mixed evidence, no superiority, no complete Cui strategy tree, no source-mediation claim.** This document inherits R24 and R25 original SHA receipts rather than re-litigating every previous native pass.

## Origin and falsifiable hypotheses

The founding C3X question is whether an original chess engine's computational preference for one move over a real alternative is causally explained by valuable response-robust **future strategy**. R26 studies just a B/E subquestion: does ranking opponent replies by estimated damage to an already committed source continuation plan expose adversarial weaknesses better than ranking replies by the opponent's general source-engine advantage?

R25 had observed four depth16 R24-frozen-plan top3-first-layer versus full-opponent-reply gaps **[+2, 0, 0, +14]cp**. The policy-stress method was conceived **after these observed errors**, so testing it on the same post-R22-selected two historical cases is exploratory *development*, not preregistered generalization.

Define candidate source move `m`, legal opponent reply `r`, and already R24-frozen source subsequent own move `u_S(s,m,r)`. Let `F_S^{(12)}(s,m,r,u_S)` be a classical SF16 depth12 centipawn estimate from original mover's perspective after `u_S`; this is a *source model proxy*, not the independent judge. The R26-V1 opponent first-layer selector ranks `r` by increasing `F_S^{(12)}`, choosing top3 per root. R25's comparator ranks opponent moves by an independent SF16 opponent-to-move MultiPV top3 at the preceding history. Both use the SOURCE family, never the Berserk judge for selection.

A possible rival explanation: rankings differ because of **search-horizon shifts / TT dynamics / changed budget**, not because one captures a distinct meaningful strategic vulnerability. Original source action `u_S` already comes from SF16 depth12 search and need not be minimax-consistent across fresh search horizons.

## Native source and referee execution

### V1 — 147 source queries, pre-judge frozen

- [R26-V1 original source run #42571598631](https://github.com/WhoSia/C3X/actions/runs/42571598631): SUCCESS, pinned original unmodified Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads1, Hash16MB, NNUE OFF. Python3.12 + `chess==1.11.2` only in Actions; no Chat-runtime package installation.
- Before any R26 independent referee call, the run revalidated R24's SHA-pinned 147 source-next-own actions, analyzed each `s,m,r,u_S`, recorded **147 actual source searches / 7,462,570 actual source nodes**, and ranked 12 reply selections across four roots. Source-only JSON SHA256 `32db0d0dd880ba9ea9684ae039679cc610c1a204e0caae5f4ea52f53df18eec8`.
- Historical case roots R22-adaptively selected; R25 failures already known at R26 method-design time. V1 is **not blind prospective selection**, even though Berserk values do not enter the ranking computations.

### V2 — selective genuinely independent rejudge

- [R26-V2 original native SUCCESS #42572119921](https://github.com/WhoSia/C3X/actions/runs/42572119921), pinned Berserk14 commit `8ae895a6151695be4a50d4fb65b0c131659c513a`, NNUE SHA256 `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`, nominal referee depths 12/16, free versus forced pre-frozen source own actions, actual nodes recorded by each search.
- Reused **24 independently executed R25-E2 search outcomes** for selected replies overlapping the pre-existing SHA-frozen R25 ranking; executed only **24 NEW genuine Berserk searches** for the remaining selected replies. New+reused = 48 evaluated modes, across 12 first-layer selections. The R25-E2 JSON was SHA `b18c7488edc66454a9cd79f54e7f072b2bbb9dddb56a0f1a87349bde4ec4440b`; R24-B2 all-response aggregate SHA `2fd30e135a1d4f4575b71cd263f01fdd363659fe3f05b6cafc653dc98646e365`.
- V2 JSON SHA256 `d173585284362cf7310ebb4ff0ad4ac64c633616c39f76957001632d1f69070d`. Exact same source history/case/root/policy, original source SHA and judge net SHA validated. Prior R26 V2 synthetic fixture failures retained; the final native run tests and all steps were SUCCESS.
- Selection and judgment occur in **separate successful CI runs**. Original PGN, private full histories and modified binaries are not publicly uploaded.

## Genuine result: policy-aware improves one historical root but worsens another

Depth16 Berserk worst original-mover cp under the already frozen R24 own continuation policy:

| Historical exposed event | Root move | Full legal opponent replies (R24) | Generic source opponent top3 (R25) | Policy-conditioned source top3 (R26) | R26 minus R25 |
| --- | --- | ---: | ---: | ---: | ---: |
| Sahel | e5f4 | +64 | +66 | **+76** | +10 |
| Sahel | e5c3 | +62 | +62 | +63 | +1 |
| Cerrado | e5f6 | -65 | -65 | -65 | 0 |
| Cerrado | d1c2 | -36 | -22 | **-36** | -14 |

For a sampled first-reply minimum, **smaller** means the selector exposed a more damaging opponent response. In Cerrado `d1c2`, R26 exactly recovers the full-reply worst -36cp while R25 missed it by 14cp; at Sahel `e5f4`, R26's min +76cp misses the full +64 by 12cp, versus R25's +66 by only 2cp. Two of four root candidates are thus worse than R25 under R26 (one identical, one better). This **falsifies a uniform advantage claim** for this source-policy stress ranking on the observed historical set. The results are *not* a prospective generalization test and not a claim that a new method strictly dominates Cui.

Depth12 frozen-policy comparisons (full / generic / policy):
- Sahel e5f4: +62 / +67 / +69.
- Sahel e5c3: +68 / +68 / +80.
- Cerrado e5f6: -80 / -80 / -80.
- Cerrado d1c2: -40 / -29 / -40.

Depth16 unrestricted judge own action (full / generic / policy):
- Sahel e5f4: +73 / +74 / +74.
- Sahel e5c3: +71 / +71 / +71.
- Cerrado e5f6: -19 / -19 / -19.
- Cerrado d1c2: -36 / -28 / -36.

As a mathematically trivial **union control**, `min(generic k3 minimum, policy k3 minimum)` captures [66,62,-65,-36]cp at depth16 frozen-policy, leaving only a +2cp Sahel e5f4 gap to the full universe. This is NOT a cost-matched improvement; taking a union increases selected branches (six duplicated replies across the 12+12 selections, 18 nonduplicate root-relative reply selections) and incurs the additional V1 source ranking cost. Since scores were obtained in separate finite-search runs, treat that union as a bounded exploratory replay outcome, not an exact minimax proof.

## Scientific criticism and hard boundary

1. Source-policy stress selection evaluated **ALL 147 first replies** with additional 7.46 million source nodes. Any improved worst-reply coverage over source MultiPV k3 is *not* yet a fair cost-efficiency gain. Directly querying a high-cost source for all replies undermines the compression objective unless it can be amortized, reused or distilled.
2. R25/R26 mixed-source comparison uses independent Berserk finite-depth search across runs, possible TT/search-order/node differences, and no equal-node/equal-time adjudication. Numerical subset-minimum inequalities require same value function per candidate; only replay-consistent observed finite estimates are claimed.
3. There are two adaptive historical games, four clustered roots. Source scores and judge scores do not equal true minimax, nor human strategy explanation quality.
4. Cui, Ling & Ng's original [Drive PDF](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) describes recursive engine-ranked partial strategy trees and downstream verbalization utility. R26 still tests **only the first opponent layer**. BinProp and Queen are not implemented as full rival comparators.
5. C3X A (Game14 classical source cycle/TT), B (these Oct games), D (older P34 static NNUE) belong to different worlds. No original source NNUE-feature root action mediation or same-world causal-to-semantic join is shown.

## RAVEL / BFS–DFS routing

**RETAIN:** Reliable new negative mechanism test: source-policy-conditioned first-reply ranking can both recover a missing damaging reply and miss a different damaging reply; cost is substantial.

**KILL/NARROW:** Any assertion that merely evaluating states after the frozen own move automatically improves adversarial top3 branch selection. This R26 version does not uniformly improve coverage and does not beat a fair full-tree rival.

**NEXT HIGH-INFORMATION EXPERIMENT:** Compare rankings on genuinely unseen frozen positions; importantly, remove the need for all-147 extra source searches with a cheap source-computation proxy or amortized ranker, *then* compare fixed source node/time budgets against generic opponent MultiPV and recursive Cui. For a pure full-reply guarantee, neither top3 is sufficient. Distinguish source ranking shift, policy execution weakness, and the physical source event that actually changes an original root decision in the same chess world. Rotate to C source-intake and A/D once concrete real new position available.

**Progress criterion:** Learned a real failure of an attractive policy ranking method, captured a new contrasting Cerrado source-policy weakness, avoided false promotion and reused 24 judge searches. Do not create additional R27 metric stages just to optimize these four historical roots.
