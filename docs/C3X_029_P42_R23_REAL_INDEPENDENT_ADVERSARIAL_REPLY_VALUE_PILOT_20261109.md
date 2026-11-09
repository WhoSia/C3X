# C3X 0.29-P42/R23 — First Real Independent Chess-Value Falsification: All Legal Opponent Replies

Date: 2026-11-09 KST. **Native run registered before its referee outcomes; this is a deliberately post-R22-selected DEVELOPMENT experiment, not confirmatory data.** Flagship remains source-causal root choice × robust actual chess future × independent heldout transport.

## Why this is not another easy proxy study

The earlier P40/P42 lesson: a low *within-root* regret does not explain why one root move beats another, and an explanation of a legal continuation does not establish value across adversarial responses. The older historical P37 three-ply C3X-inspired heuristic lost to Stockfish PV on independently observed human replies (1/6 versus 4/6). Strong Cui k=3 partial-tree strategy and BinProp foil/contrast remain required baselines if C3X ever claims excellence.

BFS technical experiments concluded:
- R21/B actual source-native Berserk14 SHA-pinned UCI/NNUE network built and evaluated all original frozen 16 candidate roots with *requested* 48k/96k nodes. **ZERO 8 pairs passed the 90%-actual-node accounting gate.** These scores are scientific HOLD; original failure and receipt immutable.
- R22/B separately preregistered *fixed depth12 and depth16*, with actual node usage retained, and all 8 original two-root pairs passed native depth and UCI legality gates. This does **not** give equal actual budgets or chess truth. R22 source #42558024015 [native SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42558024015), ZIP/member SHA sealed in R21/R22 manifest. In the already exposed eight-event material, depth16 absolute margin ordered Sahel **0cp**, Cerrado **6cp**, next >=52cp. Sahel depth12 margin 4cp; Cerrado depth12 24cp with **root ranking reversed between depth12 and depth16** (so even independent finite-depth move preference is unstable near tie). These two are developmental high-discrimination test cases ONLY.

## Exact R23 pre-native-outcome protocol

- Source origin: same P37 original pre-P38 frozen eight October-2026 different event-family game histories, source member SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`; original P37 forecasts sealed earlier SHA `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`. Source rebuilt with chess.Board from original 30 UCI plies, legal candidate roots and complete history (including repetition and castling rights).
- R22 dependency input SHA locked: `be4de0811ff7d8b29f9b79a0008757dd6c456f3be0cb87e32940bba0ba23ddaa`. Select *exactly two lowest-depth16-root-pair-margin cases* `1e65fcf3b7a93b9b` (Sahel) and `04d52e451d89ee05` (Cerrado). Reject other outcome-based replacement. Selection itself occurs AFTER R22 values and is NOT prospective.
- Reference: independently developed Berserk14 source commit `8ae895a6151695be4a50d4fb65b0c131659c513a`, NNUE network SHA `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`; one thread, 16MB hash, separate game reset per root-reply evaluation. At depths 12 and 16, run **every legal first opponent response** after each frozen root, not just the reply in PV or C3X's plan. Actual nodes vary by case, tracked per candidate; do not call the budget equal.
- For original root mover perspective, extract only fully legal, non-mate, non-bound, depth-reached scores from native UCI. For each root m, report `min_r V_{Berserk,depth}(s,m,r)` ONLY if EVERY legal opponent response obtains a qualified finite value. If any terminal/mate/shallow/PV missing, return HOLD full-universe low regret, not optimistic sampled best/worst.
- Compare which complete independent minimizing opponent response falls in the *originally frozen* `stockfish_pv`, `simple_json`, or `c3x_legal_plan` reply predictions; report counts and resource consumptions. The latter is a deliberately limited earlier three-ply heuristic, not a complete C3X mechanistic explainer. No claim of matched generation cost or superiority over Cui/BinProp.
- Do not infer actual human reply, full response-conditioned own policy, strategic plan value or global optimality from this one-reply minimum. Finite judge strength and inter-depth disagreement remain explicit, and root comparisons are only two frozen candidates, not all legal root moves. This is a falsification-first preliminary external-value landscape, not a paper.

[Native source program](../harness/c3x_029_p42_r23_independent_all_opponent_reply_value_court.py), [8 adversarial tests](../harness/test_c3x_029_p42_r23_independent_all_opponent_reply_value_court.py), [read-only original source+native Berserk workflow](../.github/workflows/c3x-029-p42-r23-independent-all-legal-replies.yml), launched [#42558798075](https://github.com/WhoSia/C3X/actions/runs/42558798075). Source history/raw PGN, FEN and engine binary remain private; publish only aggregate per-case UCI reply and cost/coverage. GitHub commits WhoSia only; GitHub Actions contents:read, no bot commits.

## What actually advances the flagship after R23

Even full first-reply coverage under a separate finite engine is NOT the original hard paper: next require prospectively frozen strong response-conditional *own plans*, their score intervals against the independent judge, root-wide candidate closure, and a causal measurement that the *same* source-engine internal computation representing that plan actually influenced its own root move. Game14 causal dataset and these different 8 frozen P37 event games are separate data; never pretend their outcome labels coincide. Independent held-out episode cohort needs source-level new bytes and leakage gate; NNUE-on mechanism remains separate.


## 2026-11-09 — Genuine original independent opponent-reply exhaustive native outcome

[Native R23 run #42558798075](https://github.com/WhoSia/C3X/actions/runs/42558798075) **SUCCESS**. The published artifact was independently downloaded and parsed. The *exact* original ZIP (artifact #13649000299) SHA256 is `94a6db7fa68ee6aaf49e897cc4b3f3382b6c60e08d75ed927c9e354eec8eed73`; member `C3X042_R23_BERSERK14_FULL_LEGAL_REPLY_VALUE.json` SHA256 is `03ca8ca863c71e15c0d8bbd42903232a9b32448b27cd5b1fa52dec416d996bae`. [Human-authored sealed evidence](../evidence/C3X_029_P42_R23_NATIVE_147_LEGAL_REPLIES_294_INDEPENDENT_SEARCHES_RECEIPT_20261109.json).

The actual post-root legal opponent reply counts were **40,40,32,35**: 147 distinct root-conditioned chess legal replies, with separate depth12 and depth16 search for each, **294 actual independent Berserk14 UCI analyses**. Real consumed nodes were 5,577,343 at depth12 and 36,609,590 at depth16: 42,186,933 total, **unequal node counts by root and reply**. All four root candidates had complete legal first-reply coverage with source-validated finite values at both depths.

| Historical source/root | Legal first replies | Worst actual Berserk reply at depth12 | Worst at depth16 | Independent min score at depth16 (root mover cp) |
|---|---:|---|---|---:|
| Sahel `e5f4` | 40 | d8d3 | f7f6 | +73 |
| Sahel `e5c3` | 40 | c8f5 | c8f5 | +71 |
| Cerrado `e5f6` | 32 | g7f6 | g7f6 | −19 |
| Cerrado `d1c2` | 35 | f6g4 | f6e8 | −36 |

The independent referee's root-mover value after the *worst legal first reply* differs by only 2cp between the two exposed Sahel candidates, versus 17cp between Cerrado candidates at this finite depth. But root-wide move search support is not closed; other legal *root* actions were not evaluated, and a two-ply finite-engine landscape is not an exact objective full-minimax proof.

**Critical depth-dependent strategic target effect:** Sahel e5f4 and Cerrado d1c2 both change their referee-worst legal opponent reply between depth12 and depth16. This makes any proposed plan 'robust to the opponent's best reply' sensitive to independent judge precision and score uncertainty, not a self-certifying qualitative claim.

**Original frozen prediction negative/limited result at depth16 (only four exposed roots):** Stockfish24k PV predicted 2 of the 4 independent worst replies; shallow three-ply C3X-inspired material heuristic predicted 2 of 4; simple JSON predicted 1 of 4. These methods had **unequal original compute/reply cardinality**; n=4 roots clustered into only two AFTER-R22-selected historical event games. No superiority claim, no statistical independence, no complete C3X agent and no strong Cui/BinProp rivals. At depth12 the PV's observed worst-reply hit was 3/4, demonstrating additional label sensitivity. Preserve original P37 human-PV superiority, not selective favorable R23 anecdote.

The original independent referee source/net/git tag were byte verified and its complete legal board history replayed, no human continuation or raw broadcast PGN was inferred. This is a **real value-bearing pilot, not a valid final strategic explanation paper**: need future plans across *response-conditioned own moves* selected BEFORE reference labels, independent family judge bounds, equal actual-cost or frontier, stronger rivals, global root support, same-position source-level natural-selection mediator and a genuinely new holdout. Retain the endogenous case selection in the receipt (R22 score margins used to choose Sahel and Cerrado); never promote this as prospective replication.

## PI breadth rotation after this DFS

A (mechanism) has genuine historical exact native evidence but local-to-final mechanism remains unproved. B (chess consequence) now has an actual independent judge executable and **full first-opponent reply landscapes** with heterogeneous cost, no valid winning explanation. C (cohort transport) proved only 0 exact FEN4 collisions between two historical samples, and October broadcast official monthly compressed archive remains unavailable as of Nov9. D (neural static) now has authentic original Stockfish16 same-board evaluator traces with 7/12 white-side sign disagreements, not feature causation. The next *balanced* cycle should (i) freeze a truly new event-disjoint source cohort when licensed bytes are available, (ii) complete a **strong** typed reply-conditioned plan/Cui/BinProp experiment with independent J and calibrated abstention, (iii) test neural feature or search mechanism interventions on the **same future-chess property**, not simply add more Game14 ordinal probes.
