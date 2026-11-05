# C3X 0.29-P40/R1 — Why a Perfect Root Score and One PV Cannot Identify Response-Conditional Value

2026-11-05 KST. THEORETICAL RESEARCH UNIT. This is a small constructive non-identifiability lemma, not a novel general theorem in game theory and not an empirical Stockfish conclusion.

## Explicit identifiability target

Let the published engine summary S comprise, for each legal candidate root m, its exact minimax root value V(m) and ONE selected root→opponent→mover PV (deterministic lexicographic tie-breaking). Want to recover D(m,r)=max_u v(m,r,u) for OFF-PV opponent reply r and the value difference D(A,r_A)-D(B,r_B) under a separately justified response-alignment relation. The source chess positions after A/B generally have DIFFERENT legal reply sets; matching a literal UCI string across them is not valid response alignment.

## Constructive adversarial counterexample, two 3-ply perfect-information zero-sum trees

Two artificial games G0 and G1 share candidates A and B. Both r0 branches yield v=0. Both trees use r0 as the selected opponent minimax reply (tie order); lexical policy selects A root and r0/u0 continuation. In G0, alternative r1 values A=+2 and B=0. In G1, alternative r1 values A=0 and B=+2. Because opponent minimizes and r0 remains a worst opponent reply in both games, BOTH root exact values remain V(A)=V(B)=0, BOTH PV outputs remain identical, but the off-PV response-conditional A−B comparison flips sign (+2 versus −2). Thus no deterministic function of S can recover that contrast across both games. Note these are abstract finite trees; chess legal geometry may constrain which trees embed into actual boards, so the proof is limited to insufficiency of scalar+single-PV summaries in general, not a theorem that no chess explanation can infer more from a full chess position.

## Implication and severe boundary

This establishes a logical information gap, NOT that C3X automatically fills the gap or that Stockfish+PV loses on a concrete future chess-value prediction. Even a baseline given exact board, chess rules, source code or further engine budget can explore off-PV branches, so a real trial MUST compare matched computation and prediction cardinality. The construct needs only ONE unobserved opponent reply to flip a proposed explanation; full adversarial guarantees require all replies or a justified structure theorem. Reply r1 of A and r1 of B is a hypothetical correspondence and is NOT shared literal UCI by fiat in real chess.

## Measurable next research gate

Use archived P37 8-event candidate worlds and P39 16-world exact mobility certificates to quantify how often a response-conditional signal discriminates original candidates, how it aligns to the *separately archived* deeper SF16 96k root values, and whether it beats the trivial SF16 24k first candidate after including ties and compute cost. Historical data are fully exposed and same-engine, so report effect and uncertainty as exploratory negatives/diagnostics, not confirmation.

Scientific stop: abandon any claimed paper contribution based solely on the no-free-lunch toy proof or standalone legality/mobility proxies. C3X's hard objective remains counterfactually robust CHESS VALUE and source-mediated decision explanation across independent opponents, not proxy inflation.