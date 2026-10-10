# Paper prospectus — Native Search Memory and the Support of Tactical Computation

**Research proposal, 2026-10-11. This is NOT a completed, submitted, or accepted paper.**

**Proposed title:** *When Search Memory Changes Which Tactics Are Computed: Source-Exact Counterfactual Tests of Transposition Tables and Static Exchange Evaluation in Stockfish 16*

## Question

Can a native chess engine's search-memory causal effects on exact move choice be explained by source-identified tactical calculations, rather than by simply assigning human names to motifs such as pins, exchanges or discovered attacks?

## Candidate claim to test, not a universal result

Physically suppressing one source-verified TT first consumer changes the *support of observed SEE evaluations* in some descendant search paths, while many originally identical native source events survive. A controlled source-exact intervention at one common SEE pruning event may fail to affect the terminal bestmove. Therefore a trace match, static motif annotation and a later SEE call are not sufficient to prove natural mediation of a TT-induced choice.

## What the present evidence actually supports

- Independent source-first licensed cohort: 16 Lichess May2026 broadcasts (CC BY-SA 4.0) plus 16 disjoint nonmate Lichess CC0 puzzles. SHA-frozen before native intervention; 248 literal exact UCI forecasts sealed in Git. Of 124 eligible original TT first-reader source interventions, all 124 physically fired; only seven role arms changed bestmove, representing four broadcast games. Old cross-order M1 111/124 exact versus M0 nochange 117/124: negative replication.
- Strict causal-source tracking: Original physical full64 TT writer, slot, epoch, rootcall and first consumer; actual native value-as-eval and cutoff separately from probe hits. Frozen single-thread Stockfish16, 16MB Hash, depth12, NNUE off, cold duplicates.
- Source SEE: Four actual main and qsearch native SEE sites instrumented with exact original chess ancestor key vector and measured call-state fields, including ply, depth, live alpha/beta, PV, rule50 and defined input occupancy.
- T1: 21 same measured-state SEE events across four of six post-outcome development games AFTER actual original TT use and counterfactual first-reader block; 62 matched records preceded those selected TT source events. Two observed prefixes censored.
- T2: One preregistered exact-source qsearch-pruning SEE call was physically Boolean-inverted once in each TT-original and TT-FIRST arm. Both interventions contacted exactly the same source predicate; there was no additional terminal bestmove effect. Five source game cells were ineligible or censored and remained HOLD.
- R3: In first32 observable post-source SEE event prefixes, 21 same full measured-state events, 25 original-only and 41 TT-FIRST-only. Two cases censored; among four uncensored cases, four original-only versus twenty TT-FIRST-only. This is evidence of observed search frontier asymmetry, **not** proof of global SEE event disappearance or natural mediation.
- Chess source boundary: A direct opponent legal destination recapture count of the chosen root move differed in only one of six counterfactual comparisons. Pseudo-attacks are not legal response proofs; Stockfish SEE occupied Bitboard argument is OUTPUT and potentially unassigned after early return.

## Main methodological contribution worth testing

A six-gate native causal court: **(1)** immutable source-first chess data, **(2)** actual physical TT first-consumer contact, **(3)** source call chronology, **(4)** exact measured same chess/search-state identity, **(5)** actual native SEE pruning operator dose or branch-admission intervention, **(6)** source-root candidate survival and exact-UCI terminal outcome. Missing contact, censored trace, divergent search state and a true negative effect remain distinct statuses. This can improve on explanations that only match a named tactic or compare principal variations.

## Limits preventing a strong paper claim today

The six deep-source cases were selected after R1 outcomes, and one valid T2 SEE actuator case is too small to establish a general law. Four distinct changed games in the original broadcast stratum cannot be converted into seven statistically independent games. Search-state telemetry does not exhaust all Stack/TT/repetition/history variables. The first32 event cap prevents claims about globally absent branches. An unchanged terminal bestmove after one source intervention is a valid negative, not a proof that SEE has no causal effects. No new positive M3 predictor has survived a fully prospective source test.

## Minimum additional evidence for a submission-worthy manuscript

**A. Parent search branching:** Source-record one monotonic native event serial across TT value use, first-reader block, actual search parent admission/pruning and downstream SEE consumer. Identify the earliest source-aligned parent whose branch choice differs across actual TT treatment.

**B. Source-specific branch restoration:** Preseal one exact parent decision identity and test original, TT-only, branch-only and combined interventions with cold and sham controls. Observe a true branch contact before inferring downstream SEE activation, candidate survival or final UCI.

**C. Actual chess microstructure:** Reconstruct the *descendant chess position* from a proof-carrying original legal move path and distinguish opposing legal recaptures, defenders, geometric attack edges and pinned-piece move legality. Do not infer descendant exchange geometry from root-only FENs.

**D. Independent falsification:** Freeze a new licensed ecology and literal game-specific exact-UCI M3 predictions before any corresponding first-reader treatment. Report negative transfers, matched controls and game-cluster-aware denominators.

## Scientific and publication integrity

Keep original source SHA, Git precommit history, unaltered M1/M2 FAIL results, all HOLD cases and source instrumentation. Official broadcast original game records have CC BY-SA 4.0 obligations, puzzles CC0, modified Stockfish binary GPLv3 conditions. Source rights and code provenance must be separated; no complete original PGNs, private player metadata or modified GPL binary were uploaded in new T1/T2/R3 public evidence artifacts.

**Evidence links:** [T1 source exact-state receipt](../receipts/c3x-023-P1-R2-T1-exact-native-SEE-search-window-equality-20261011.json), [T2 single-site negative intervention](../receipts/c3x-023-P1-R2-T2-one-source-native-SEE-by-TT-first-intervention-negative-20261011.json), [R3 native event frontier](../receipts/c3x-023-P1-R3-native-SEE-frontier-and-legal-recapture-20261011.json).
