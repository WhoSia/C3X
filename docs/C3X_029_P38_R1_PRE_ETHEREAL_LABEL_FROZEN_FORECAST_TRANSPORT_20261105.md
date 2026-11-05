# C3X 0.29-P38/R1 — Cross-Engine Frozen-Reply Transport: PRE-REFEREE REGISTRATION

2026-11-05 KST. **This protocol is registered before any Ethereal referee output is observed.** Historical P37/R1 eight distinct late-October event families and P37/R2 original 24k prediction archives are IMMUTABLE. This is **post-Stockfish-label exploratory but pre-Ethereal-label**; it is not a new source-heldout or blind model development result.

## Existing prior evidence and strict claim ceiling

Original P37/R4 audit confirmed P37 predictions sealed before its **same-engine Stockfish16 96k reference**, which favored source-native PV: **PV 11/15, simple conditional JSON 2/15, finite three-ply C3X heuristic 4/15**, 1 missing reference; paired PV-only 7 and C3X-only 0. Only 1/4 of nominal near candidate pairs remained near and identical at 24k,48k,96k. Full historical 0.28+ event-family decontamination remains incomplete, 4/8 not semantically equivalent to independent heldout. C3X finite heuristic expended **24,894 law-legal own follow-up expansions**, while simpler JSON expanded none: CPU not equated. Do not erase previous negative.

**This is NOT a new C3X predictive model.** Rerun existing exact 16 frozen per-candidate predictions from the original P37/R2 PRE-REFEREE JSON, SHA256 `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`, source ZIP SHA `721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6`. No predictor gets new features, retuning, extra PV, additional source games or reference access.

## Independent referee / two budgets

Referee: **open-source chess engine Ethereal v12.75**, official `AndyGrant/Ethereal` GPL-3.0 repository `v12.75` tag, expected release commit prefix `b55ed96` (fail closed if mismatch). This historical handcrafted-evaluation engine is an independent codebase and evaluation family; it is older/weaker than SF16, and its reply is **another finite-search preference**, NOT chess truth, objective value, expert judgment or human-play ground truth. Compute Ethereal binary/source commit SHA256 as receipts; build unmodified source. Engine name must contain Ethereal, Threads=1, Hash=16; no neural license download or paid weights. We only run a read-only official GPLv3 build.

For EACH fixed P37 case and EACH of the two frozen root candidate moves, reconstruct exactly original legal 30-ply UCI prefix, verify candidate legal, then force it via `root_moves=[move]` under a fresh clean UCI engine context (one case-process per move+budget) using python-chess. Native limits **96,000 requested nodes and 192,000 requested nodes**; if either budget has no legal first opponent reply in the PV, referee label is `UNDEFINED`. If first opponent reply differs across budgets, mark `REFEREE_UNSTABLE`, exclude from the **stability-restricted** denominator but keep in the all-16 raw data. Do **not** choose more positions, substitute models, or tune the cutoff. Record full Ethereal first-PV, score and per-call nodes; UCI PV must be legal along source stack.

Primary descriptive comparisons, computed on identical *evaluable stable* candidate instances: one-hot exact first-opponent reply matches (i) Stockfish16 PV, (ii) simple one-ply conditional JSON, (iii) C3X three-ply legal plan. Report **all 16**, number stable/evaluable, one reference missing, paired per-event matrix, PV-only vs C3X-only, source/engine version hashes and historical same-engine results side by side. Secondary report Ethereal 96k label without stability filter for transparency. No conclusions from only nonabstaining favorable samples. Repeat if zero stable, honest `UNINFORMATIVE`.

**Engine source independence does not equal score/reference truth.** A change in PV forecast rankings across engines tests evaluator/code-family transfer and exposes self-referential labels but does not establish a useful opponent-proof chess strategy or counterfactual consequences. Different engine strengths and nodes are not equal compute: no equal-Elo, CPU equivalence or causal NNUE-mediation inference.

## No early access

Original frozen full source manifest from P37/R1 SHA256 `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`; old predictions must match all eight cases + candidate moves. Ethereal referee job may load SHA-verified source and prediction archives, but never edit prediction body; claim a valid out-of-family replay only when explicit archival chronology remains preserved. `github-actions[bot]` MUST NOT commit/push/merge/tag/move refs (read-only Actions). Drive original source bytes and generated referee raw bytes archived separately; Notion semantic verdict mandatory.

## Research decision

If PV wins also against Ethereal labels, the current cheap three-ply C3X baseline is an ineffective reply predictor. If C3X improves but only with much larger chess-law compute, **cost-adjusted advantage HOLD**, and if two depths disagree the reference itself is unstable. In all cases next step must move to a independently chess-law verifiable Q (e.g., actual forcing tactical consequence under adversarial replies), with stronger source-faithful rival, abstention and blind human utility separated. Do not proliferate more names/NNUE diagrams.
