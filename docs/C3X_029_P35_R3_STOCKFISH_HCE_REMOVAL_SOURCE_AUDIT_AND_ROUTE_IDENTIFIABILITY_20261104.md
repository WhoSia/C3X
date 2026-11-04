# C3X 0.29-P35/R3 — Why Stockfish Removed HCE: Original-Commit Audit and Evaluation-Route Identifiability

Date 2026-11-04 KST. **Source-audited research, actual locally tested safety code; NOT a newly executed Stockfish16 search or 12-board cold replay.**

## 1. Developer's original primary source

Original removal commit: [official-stockfish/Stockfish@af110e02ec96cdb46cf84c68252a1da15a902395](https://github.com/official-stockfish/Stockfish/commit/af110e02ec96cdb46cf84c68252a1da15a902395), committed 2023-07-11, titled *Remove classical evaluation*. The developer explains:

- Classical was kept largely frozen for five releases after NNUE arrived. Its hoped-for contributions as NNUE input or search improvement had not materialized.
- Classical contributed little to overall strength but remained a **fast substitute** in positions effectively decided by large material differences; the speed advantage could offset its inferior evaluation accuracy locally.
- Removing it removed roughly **25% of source code** and ongoing maintenance/integration burden.
- This was an **accepted strength cost**, not a free strength improvement. Original 100,000-game tests of deletion (change minus parent), including uncertainty: STC **-2.35 ± 1.1 Elo (95%)**; LTC **-1.74 ± 1.0 Elo (95%)**; VLTC SMP **-1.70 ± 0.9 Elo (95%)**.
- The original developer suggested fast low-cost neural evaluation could supplant this role. This is the actual historical motivation for our research into the evaluation-speed/precision regime; do not characterize HCE deletion as universally better at the time.

Official [Stockfish16.1 release, 2024-02-24](https://stockfishchess.org/blog/2024/stockfish-16-1/) introduces HCE removal, new NNUE architectures and **Dual NNUE** (smaller second network for easily decided positions). It reports **up to +27 Elo relative to SF16 as a complete release**; this *cannot* be attributed to HCE removal, which in isolation incurred a small negative test result.

The [original 2023 developer discussion](https://github.com/official-stockfish/Stockfish/discussions/4678) includes objection to accepting a negative Elo simplification and clarifies that quick classical evaluation in high-PSQ scenarios was a speed trade-off, not proof neural evaluation intrinsically failed in those positions.

## 2. Major methodological consequence for C3X

P34 original code/source [SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`](https://github.com/official-stockfish/Stockfish/tree/68e1e9b3811e16cad014b590d7443b9063b3eb52) has *two distinct comparisons*:

1. `Eval::trace` can report raw classical and raw NNUE scores on the **same reachable board**, even when `Use NNUE=true`; this measures a model-valuation disagreement, not necessarily the actual evaluation path consumed by search.
2. Actual `evaluate()` uses a source-dependent routing decision; P34 notes `bool useClassical = !useNNUE || abs(psq) > 2048;`. With NNUE enabled, sufficiently large PSQ can invoke classical. Thus a raw NNUE rank reversal does **not** prove that the neural network's preference was physically consumed at a parent or root.

**New P35 target:** For each P34 original legal-history board, measure (a) direct model-evaluation discrepancy, (b) actual evaluation dispatch probability conditional on material/PSQ and search state, and (c) source-identical evaluated leaf contributions and verified ancestor relay. Without (b)+(c), static scores are potential explanations, not actual mediators.

## 3. Strong negative and positive controls

- Compare **SF16 HCE vs SF16 NNUE** under exactly pinned original source/network, using UCI `Use NNUE` toggles, but instrument actual `evaluate()` branches. The toggle is a regime intervention, **not a single-feature causal intervention**: search, cutoff and evaluated nodes will diverge.
- Compare **SF16 NNUE vs SF16.1 NNUE** only as a historical *version bundle* (net architectures, parameters, code and search all changed); NEVER call this a controlled causal test of HCE removal.
- Use original deletion parent and child commits as a **historically narrower code-diff comparison**, subject to strict source/network/compilation and actual search budget verification; still do not claim isolated neural feature effects.
- Label 'high-PSQ fast fallback' hypothesis separately from 'NNUE learns chess concepts'. Source efficiency and strength do not identify chess-semantic computation.
- Audit the actual source-selected evaluation route at each evaluated node. The 12 printed `eval` outputs are not a frequency sample of leaf eval routing.

## 4. New executable pre-experiment gate

- [Evaluator version / UCI capability gate](../tools/c3x_029_p35_r3_evaluator_lineage_gate.py) rejects `Stockfish 16.1` as classical-vs-neural same-source evidence and rejects absent `Use NNUE` toggle even if provenance override requested.
- [8 local unit tests](../tools/test_c3x_029_p35_r3_evaluator_lineage_gate.py) executed using Python stdlib unittest: **8/8 PASS**. They cover exact 16 option detection, 16.1 rejection, missing toggle, invalid handshakes, invalid arms, version confounding, incomplete provenance and no false mediation attribution.
- These tests do NOT execute Stockfish, verify binary/net SHA or prove P34 replay; `UCI_CAPABILITY_GATE_PASS_NOT_SOURCE_SHA_PASS` deliberately preserves that boundary.

## 5. Next research protocol

**P35/R4 evaluator-routing provenance** (high scientific priority):

1. Rehydrate original P34 12-board archive via authenticated Drive byte transfer; verify raw ZIP SHA256 `2b426b81c97d1483581e398c7a300b221a39ebe6d9e5e0194bec4d3f2885547e`, source history JSON hash and exact SF16 source+net+binary.
2. Cold repeat search-free `eval` and direct `NNUE::trace`, preserve original full UCI move histories, expected rounded scores plus raw integer outputs.
3. Implement **read-only source routing logs** for every actual evaluation: exact PSQ, `Use NNUE` setting, route (HCE/NNUE), evaluated board identity, thread/root/parent call IDs, and original output. Verify exact bestmove/nodes parity with uninstrumented source.
4. Explicitly classify `...Kf7,Re1` and `...Kf7,e4` route events in real search. If raw neural valuations differ yet neither neural score reaches relevant decision ancestors, **FAIL** an NNUE-mediation claim.
5. Treat source/NNUE feature channels only after routing identification. Then test robust across near/intermediate/wide value margins, with game-disjoint cohorts.

## PI Judgment

**RUN-FATAL-TEST, NO PREMATURE NNUE CONCEPT PROMOTION**. Historical HCE removal provides an excellent negative control because a developer-accepted strength sacrifice (~2 Elo) removed an alternative score route while preserving the pursuit of strength. It does not establish what the NNUE represents. Novelty must come from identifying source-executed representational mechanisms that genuinely change decisions and explain independently observed chess consequences.

## No bot history

New commits are created through the authenticated `WhoSia` user. GitHub Actions may compute/report artifacts only, never commit, push, merge, tag or move refs. `github-actions[bot]` contribution forbidden.
