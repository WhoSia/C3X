# C3X 0.29-P33/R2 — Rechecking 203 Exhaustive First Replies at Depth 11

Date: 2026-11-04 KST. **Actual official unmodified Stockfish 16 search completed SUCCESS** at [GitHub Actions run 41771745191](https://github.com/WhoSia/C3X/actions/runs/41771745191). This is archived, adaptively selected, source-exposed development data, not independent generalization or solved chess minimax.

## Grounded original-data provenance and implementation

The same original C3X 0.18 October 2025 independent 16-source-game UCI archive was reused: frozen JSON SHA256 `6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c`, originally GitHub Actions 37981820261. The previously executed P32 16-game native JSON exact SHA256 `8e9ed5104156887221696a79416c69060dc3fa8beb48c02142337591b25efc8b` was verified before rerunning P33. Stockfish16 official pinned git commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` (Threads 1, Hash 16MB, Use NNUE false), unchanged. Entire original-game prefixes were replayed; every legal first opponent reply enumerated, then independently evaluated with original history preserved at remaining search depth 11, compared with the P33 depth10 all-legal run and previous P32 depth12 top3 MultiPV list.

The adaptive focal original cases were 6,10,14; two root moves per game; 34+40+37+32+28+32 = **203** legal first-response branches; no sampled reply set. Output is a depth-limited *estimate* after each forced response, not a solved minimax bound. Nominal reply-after depth11 and prior post-root depth12 do NOT make search strategies, aspiration windows or multiPV scores identical.

## Full source-verified minimum table

| Case | Candidate root | Legal first opponent replies | Post-reply depth10 minimum (cp, root mover POV) | Post-reply depth11 minimum (cp, root mover POV) | Was depth11 argmin in prior P32 top3? |
|---|---|---:|---|---|---|
| 6 | `c5c6` | 34 | `b7a8` +91 | `b7a8` +90 | YES |
| 6 | `d3b5` | 40 | `e8f8` +120 | `e8f8` +122 | YES |
| 10 | `e8f7` | 37 | `e3e4` +45 | **`f1e1` +35** | **NO** |
| 10 | `e5f4` | 32 | `e3f4` -17 | `g3f4` -8 | YES |
| 14 | `c2c3` | 28 | `e7f6` +25 | **`c8e6` +35** | **NO** |
| 14 | `d5d3` | 32 | **`b5b4` -13** | `c8e6` -17 | YES |

Depth11 result for original #10 root `e8f7`: earlier P32 top3 `e3e4`, `f1f2`, `f1h1`; all-legal lowest is **`f1e1` +35cp**, absent from top3; original played `e3e4` evaluates +58cp under the depth11 forced-reply procedure. This difference is NOT an independently verified regret theorem for human play.

Depth11 result for original #14 root `c2c3`: earlier P32 top3 `g7g6`, `e7f6`, `e7h4`; all-legal lowest is **`c8e6` +35cp**, absent. The actual source next human reply `d8d7` is still outside the P32 top3 and evaluates +45cp after forced reply. Search horizon matters to whether selected responses cover an estimated worst action.

Depth10 apparent case #14 foil `d5d3` worst-outside-shortlist `b5b4` (-13cp) **DOES NOT SURVIVE** depth11: at depth11 `c8e6` (-17cp), which was already in P32 top3, is minimum; `b5b4` improves to -4cp. Thus DO NOT elevate a stable particular opponent refutation claim from the earlier P33 result.

## Strategic interpretation

- P32 established a real strategy-valued counterpoint: capturing a knight with `...Bxf4` was not necessarily the best available root move when the opponent can recapture with different legal pieces. P33 verified all 32 legal responses of that root, including `e3f4`, `f3f4`, `g3f4`, and the immediate material balance after recapture is -10cp for Black under N=320/B=330. This is material-accounting truth, not a unique search-choice cause.
- P33-R2 demonstrates both false confidence possible from limited top3 enumeration and **instability of argmin under depth changes**. A robust policy guarantee requires a declared legal response set, horizon, evaluation oracle and stability analysis. No physical TT mediator has been tested in the P32/P33 unmodified engine runs; refer to historical 0.27 TT-FIRST source-contact experiments separately.
- Existing baseline Stockfish+PV and an ordinary plan JSON are extremely competitive. P32 actual next-human-reply exact agreement was 8/16 for one-PV and 9/16 for simple JSON; top3 coverage 13/16 includes THREE predictions, a non-comparable prediction-set size. None is a paper-level method improvement.
- Appropriate next research: compare equal search budget and game-disjoint prospective outcomes, avoid multiplying authority gates. Chess choice-causal internal tests and plan-value tests must remain separate.

## Source paths, logs and retained custody

- Engine implementation `harness/c3x_029_p33_all_legal_reply_surface_native.py`, tests `tools/test_c3x_029_p33_all_legal_reply_surface.py`, CI `.github/workflows/c3x-029-p33-all-legal-opponent-replies.yml`.
- Depth10 initial native run [41771220648](https://github.com/WhoSia/C3X/actions/runs/41771220648); depth11 nominal-horizon follow-up [41771745191](https://github.com/WhoSia/C3X/actions/runs/41771745191).
- Authenticated Google Drive permanent source archive [original full UCI games](https://drive.google.com/file/d/1vn6-CY3uwv4PjaqQbQURhWzEhsxY22NV/view), depth10 ZIP [P33](https://drive.google.com/file/d/1CYSCMdseH0B-DWnGHJS6SCl7T32qmIz8/view), depth11 ZIP [P33 R2](https://drive.google.com/file/d/1Xkr4nRQB1dGjr7HMdvM0gYEQthkW4Faq/view).
- CI only executed programs and uploaded result artifacts; GitHub Actions bot did not author any source commits.
