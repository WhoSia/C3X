# C3X 0.25-P14-P10-P2 — Rival-Directed Search Allocation & Nonterminal Tactical Explanation

**Formal name:** Rival-Directed Search Allocation & Nonterminal Tactical Explanation: Budget-Matched Counterfactual Decisions, Local Re-search Value, Source-Calibrated Abstention & the 0.26 Evidence Gate.

**P2-P0 (2026-10-13): PROSPECTIVE DESIGN ONLY / NO NATIVE RESULT CLAIM.** The original SF16 baseline, prior negatives and disclosed examples are inherited, not reproduced. Predecessor: [P14-P10-P1](c3x-025-P14-P10-P1-nonmonotonic-search-economics-026-review-20261012.md); exact previous human head `c7391435e79d631861d4a9f6ab115f22acd78ed4`.

## Primitive question and rival theories

Can a strictly **pre-decision** measurement of competitive root moves identify which rival should receive extra original-Stockfish search at a fixed resource budget, thereby better predicting a **separately computed** deeper reference move, with honest coverage and cost? A mechanistic *why* additionally requires source-level evidence, not merely the winning root's score.

- H0: a direct untouched original SF16 fixed-node search, or equal per-rival extra search, performs as well as (or better than) any challenger-directed allocation.
- H1: a frozen close-score + challenger-volatility rule sometimes identifies a useful extra-search target and improves **paired held-out deeper-reference agreement** at comparable search effort.
- H2 (adversarial): more probes of a volatile challenger disproportionately amplify depth imbalance/TT effects, **making decisions worse**.
- Falsifier: equal or worse held-out reference agreement, budget imbalance, low eligible coverage, candidate-pool misses, instrumentation non-parity, or sensitivity to one opening/game destroys an optimization claim.

## Exact controlled operating surface: no Stockfish source edits

Official Stockfish 16 source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; engine binary built from that revision, Threads=1, Hash=16MB, Use NNUE=false, cold process per measurement, unchanged move generation and draw/repetition history via full `position startpos moves ...` or exact other presealed UCI position command.

UCI `go nodes N` and `go nodes N searchmoves m` request **nominal**, not proven exactly realized, budgets. Collect returned score/move, depth, `info nodes`, elapsed wall time and incomplete-depth caveat. Stockfish's UCI `searchmoves` restricts the root candidate, **not** the engine's deeper branching. All candidates must be legal and sourced from the pilot's PVs; no synthetic or outcome-based retargeting. Mate scores, truncated/missing root frames, inconsistent root move identity, bound-only values, missing/implausible node reporting, and illegal state => explicit ABSTAIN/TECHNICAL_HOLD. Never convert engine cp to certified minimax or multi-depth scores to a game-theoretic proof.

Fixed nominal total **12,000 search nodes per trial policy**:
- `PILOT`: original SF16, MultiPV=2, nominal **3,000** nodes; record two complete depth-specific rows and the preceding complete depth, both tied by UCI PV move identity.
- `UNIFORM`: shared frozen pilot, then fresh one-move restricted searches for leader and challenger, **4,500/4,500** nodes.
- `RIVAL`: pilot, then challenger/leader **5,850/3,150** nodes when trigger qualifies; otherwise **UNIFORM fallback with full denominator**, marked ABSTAIN_RIVAL.
- `LEADER_HEAVY` negative control: the reverse **3,150/5,850** when the same trigger qualifies, otherwise uniform.
- `DIRECT` strongest natural comparator: independent original SF16 MultiPV=1 **12,000** requested nodes, no pilot, no restricted root.
All per-trial process startup time is measured separately; sum of reported nodes is NOT necessarily exact actual nodes because the final interrupted depth may be unreported. If the recorded node-accounting envelope cannot justify budget matching, this trial is **RESOURCE_COMPARISON_HOLD**, never a cost PASS.

For the trigger, let final complete MultiPV rows yield leader `L` and challenger `R`, both exact centipawn scores. Let `g=cp(L)-cp(R)`. Qualify when `0<=g<=60`, previous complete depth has both *same move identities*, and either `|cp_d(R)-cp_(d-1)(R)| >= |cp_d(L)-cp_(d-1)(L)| + 20` **or** the leading move at the preceding depth differs from the current leader. If no qualification, record the reason and retain the uniform fallback. All constants fixed here **before seeing P2 native outcomes**; engineering changes require a new versioned prospective amendment and void the initial confirmatory label.

Root result from candidate-restricted searches is a **descriptive heuristic** (larger exact cp, tie → initial leader), not proof of best play. Equal/higher nominal nodes is not a guaranteed fair comparison of algorithmic wall work. Monitor original `bestmove`, PV root and score class for unexpected behavior; reject mixed side-to-move/mate/bound semantics.

## Source-separated evaluation and admissibility

**Phase A engineering development:** reuse only the four previously disclosed P14-P10 opening roots ENGLISH6/FRENCH8/ITALIAN8/CARO_KANN8. Their results are exposed, strongly correlated, and NEVER prospective research validation or a reason to fit thresholds. No "12 independent data points" error.

**Phase B prospective validation (not opened at P0):** identify and freeze at least 32 independent *game-disjoint* legally reconstructable nonterminal positions from rights-authorized raw material before any P2 pilot or reference outcomes are read. Seal (position/history, source IDs, game IDs, dedup, rights, engine SHA/config, policy constants, statistical criteria) in human-authored Git. Avoid existing exposed M3/M4/M5/M6 and previous four development openings for confirmatory scoring; group by game, not candidate arm or cold repeat. If authorized blind source is missing, HOLD without substitution based on measured outcomes.

**Reference:** separate unchanged original SF16 cold run `go nodes 200000`, MultiPV=1, independently collected AFTER phase-B seal and after policy freeze. This is only a **high-budget same-engine proxy**, not objective chess truth or independent engine validation. Preserve reference bestmove and exact effort; record root move outside pilot pair as `CANDIDATE_POOL_MISS` (count as a nonagreement for restricted policies). A separate independent engine/human adjudication is an additional authority layer, not silently replaced by this proxy.

**Primary ITT outcome:** game-weighted all-sealed-position difference `1[policy decision=reference] - 1[DIRECT decision=reference]`, with nontriggered RIVAL fallback and technical invalids separately counted, never favorable denominators; report paired discordance matrix, exact uncertainty (paired sign/McNemar) and source/game stratification. Compare RIVAL vs UNIFORM and LEADER_HEAVY (not only vs DIRECT), plus actual reported-node and measured wall costs. Report triggered-subset analysis as secondary selection-biased diagnostic, NEVER as sole success.

**P2 advance gate:** produce a working tool whose decisions vary under pre-specified rival evidence; source/observer noninterference on unchanged SF16; independent exact-source execution and recorded negative controls; prospective Phase B with bounded honest resource comparison and meaningful relative decision/reference benefit or successful prediction of a specified nonterminal root contrast. A point estimate alone is NOT a robust generalization claim; do not promise statistical power at 32 games. In the absence of an independent reference quality gain or experimentally verified explanation, **0.26 remains HOLD**. Engine-strength/Elo needs separately controlled paired-color real games and statistical evidence.

## Typed evidentiary distinctions, stop and repairs

`PilotRootScores` → candidate allocation **heuristic**; `ObservedRestrictedSearch` → real restricted source result; `ReferenceAgreement` → *proxy* decision quality; `SourceCausalMechanism` requires original C++ writer→reader→parent/branch root causal link; `VerifiedChessValue` requires separate legal game-theoretic proof. No implicit casts.

STOP on unexpected source rights, invalid FEN/history, author/committer not `WhoSia`, any Actions write permission/bot authored commit, missing eligibility data, or incomparable reported search efforts. Repair parsers/build/timeouts without peeking at confirmatory labels; if experiment constants change, new preregistration and label exploratory. Preserve every FAIL, noncontact, candidate-pool miss and negative; no binary or third-party PGN redistribution. Actions may compute, never author history (`permissions: contents: read`).

**Execution decision:** first implement deterministic candidate policy, falsifying unit fixtures, then a bounded native four-position smoke test only when executable machinery is ready. Preserve original P14-P10-P1: one disclosed July intervention had 7456→4380 nodes AND a bestmove change; the new four-opening native source TT cutoff interventions yielded 0/12 node reductions and 0/12 choice flips; neither establishes a useful prospective search allocator.

**Current verdict:** `P2_P0_PREREGISTERED_NOT_EXECUTED / RDRC_DESIGNED / 0_26_HOLD`.
