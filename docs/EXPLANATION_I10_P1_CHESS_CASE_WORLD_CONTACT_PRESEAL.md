# C3X Explain I10-P1 — Real-Chess Rival Explanations: Source-Native Candidate Comparators, Hard Negative Controls, Evidence-Authority Limits

**Human Git prospective DEVELOPMENT preseal, 2026-10-13.** This is a productive **implementation** evaluation of publicly disclosed, preselected chess episodes and explicitly **not** a fresh causal certificate, externally judged pedagogical outcome, C3X 0.26 promotion, nor independent random sample. Authored before I10-P1 native case script/CI. Keep failed results.

## Predecessor actual evidence, not assumed success

I10-P0 workflow [GitHub run 38331884555](https://github.com/WhoSia/C3X/actions/runs/38331884555), original SF16 SHA `68e1e9b3811e16cad014b590d7443b9063b3eb52`: **SUCCESS 37/37 unit tests and original engine build; 0/4 judged, 4/4 abstained in non-genuine-quality mini-PGN smoke**. These are valid abstentions, not decision competence. Exactly one real engine caller and the optional no-engine run were tested. Never suppress this negative denominator in favor of cherry-picked positive cases.

## Three first-party PDFs, NOW actually acquired and fetched from the user's Google Drive

1. **Tang & Zheng**, `Typed Decision Models: An Early Evidence Audit and Evaluation Checklist` (arXiv **2609.32160v1**, 26 Sep 2026), [Drive](https://drive.google.com/file/d/13cg7JKtrPH0K3j6QgTuIaA3d2Zitz5WV/view); TDM typed readout does not by itself demonstrate independent accuracy advantage; 28-paper *early* map and 14-item checklist; vendor Jev mechanism closed.
2. **Deußer, Sparrenberg & Sifa**, `Evaluating and Benchmarking the System One Model Jev` (arXiv **2609.37647v1**, 29 Sep 2026), [Drive](https://drive.google.com/file/d/1nyhsNdWIb2IBp8aX1jSUZzWpHWgCtoCK/view); Jev 1.13.0 across 37 datasets/346,009 requests, comparative label probability scoring/calibration and selective prediction; calibration/accuracy claims remain task-bound.
3. **Gao & Wang**, `OpenJev-RLCD: A Working RLCD Implementation` (arXiv **2609.38850v1**, 30 Sep 2026), [Drive](https://drive.google.com/file/d/1FIO-xUrgBYbcgy9FbPalf14zsGKz6Y-P/view); per-rationale proper-score objective and `J(E_r u)=E_r J(u)+Var_r(u)` for shifted negated Brier, calibrate-then-reinforce, with task-specific risk–coverage results. Do NOT infer source-grounded causal faithfulness from proper calibration alone; a perfectly calibrated probability for a surrogate target still does not establish factual chess value or why Stockfish chose the move.

**Prior-art triangulation:** Kim et al. concept-guided chess commentary (NAACL2025, [Drive](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view)); Parfenova 2026 masked move-recoverability caveats ([Drive](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view)); Hendrickx et al. reject-option survey ([Drive](https://drive.google.com/file/d/1vNRBOpmqlgZwEIqMZv3zXuWa02vLUETw/view)); Angelopoulos et al. learn-then-test ([Drive](https://drive.google.com/file/d/1OC0CSHbj6DeFNeNiop81QDUHc9pduzTy/view)).

## Development-only actual historical chess cases fixed BEFORE native results

- **PRIMARY nonterminal, strategically nontrivial:** `Kasparov–Topalov, Wijk aan Zee 1999, White move 24.Rxd4` (rook sacrifice; actual opponent `24...cxd4`). [Public factual move-scoreboard](https://www.chess.com/blog/Eshwar360/the-best-chess-game-of-all-time-garry-kasparov-vs-veselin-topalov-1999) and [independent PGN transcription](https://github.com/kerry-huang-nyu/chessRobot/blob/main/kasparov_topalov_1999.pgn). Public record confirms actual SAN, not its objective optimality. Some low-depth engines have been reported to favor alternatives; that possibility is exactly an **adversarial** evaluation, never a retroactively assigned failure of chess truth.
- **SECONDARY chess-strategy case:** `Morphy–Duke of Brunswick/Count Isouard, Paris 1858, White move 12.O-O-O`, a developing/defensive-active castle with attack coordination, NOT the trivial forced 16.Qb8+ or the final mate. [Public factual game score](https://rookhabit.com/en/games/morphy-opera-1858).
- These two cases are correlated historic self-selected examples, **not** independently sampled games. The actual historical move is the fixed explanation target. If root engine does not rank it first, DO NOT silently replace the target.

## Frozen source-first procedure (development pilot)

- Replay public historic SAN score to original exact full game-history board before focal White move; legal-check the focal move and the next recorded opponent response when present.
- Original Stockfish16 pinned SHA `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads1 Hash16 MB NNUE OFF, one process for each focal study; record actual engine ID/config.
- An **independent scout** `go depth 9`, MultiPV=3 supplies the strongest **other legal** root, not author-selected after seeing paired outcomes. The rival is frozen by this source scout *before* next tests. Report candidate ranks and how much actual historical move matches scout leader. This is development, no held-out claims.
- Then perform a **single root-restricted two-candidate original-engine search** with `go depth 12`, MultiPV=2 and `root_moves=[played,rival]`. Assert the two distinct legal candidates and depth-12 comparability; report actual nodes, time, PV, whether forced reply observed, exact cp, mate/bound flags. Full-scout bestmove `!=` root-restricted pair result conceptually: no global optimum claims or token confidence.
- Original I9 commentary for that exact public PGN, using the **same pinned SF16 source/settings** (per-ply nodes 4,000); focus only the original played-move moment. This is the **actual old baseline**.
- Two grounded, non-LLM comparator summaries from the same source root contrast: `ENGINE_SCORE_ONLY` (score and PV), `CONCEPT_AND_PV_PROXY` (chess.concepts and verified board tactics, `not an actual independently run Kim CCC`), `C3X_I10` (same engine evidence plus provenance, scope, abstention; causal claim only with separate authenticated exact-source certificate). This is a matched **capability/claim-ceiling comparison**, not demonstrated superiority to a trained LLM or actual CCC model. Explicitly mark actual CCC/LLM and independent human results as UNRUN/HOLD.
- Negative control: drop/mismatch the original played move or corrupt one PV, or inject unsupported C3X certificate, require FAIL/ABSTAIN for stronger claims. Existing I10 native P0 0/4 is preserved.
- Report authority fields: *observed original engine ranking*, *legality-replayed PV*, *human chess concept heuristic*, *C3X source-causal authority absent/present*. No equivalence among them.

## Falsifiers and failure accounting

If either historic PGN cannot legally replay, original engine command fails, candidate comparator depth differs, score is mate/bound-only, PV invalid, or I10 can produce claims without the exact original move and source-linked evidence, the study is **HOLD or ABSTAIN**, not silently replaced with a cleaner after-the-fact example. If I9 original explanation is no less informative/correct, record zero demonstrated benefit. If neither C3X causal certificate matches this exact pair, `NEW_CAUSAL_SEMANTIC_INFORMATION_DEMONSTRATED=FALSE`. A single developed pair cannot show population-level model calibration or human utility.

**Freeze verdict:** `I10_P1_PROSPECTIVE_DEVELOPMENT_CASES_SEALED / NATIVE_UNSEEN / HUMAN_BENEFIT_HOLD / 0_26_HOLD`.
