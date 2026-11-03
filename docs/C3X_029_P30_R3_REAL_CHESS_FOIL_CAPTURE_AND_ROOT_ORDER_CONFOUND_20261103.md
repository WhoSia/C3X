# C3X 0.29-P30/R3 — A Chess-True Contrast That Still Does Not Explain a Stable Preference

Date 2026-11-03. Source: original 0.16/0.17 public Lichess 12 standalone FEN frozen development and 0.17 historical Stockfish16 72 native root-order intervention receipt.

## Source case and provenance
Original per-case source FEN case 8:
`2k2r2/pp1rp2p/1bp1b1p1/4p1Pn/4P2P/1PP2P1B/P1K5/R1B2N1R b - -`
Original historically recorded bestmove `e6h3`; reorder condition bestmove `h5g7`. The archive reports original root cp=66, changed-condition root cp=40, original 63,764 nodes and altered-condition 53,106 nodes. Those CP figures are complete root scores for different search-order conditions, NOT same-run candidate-pair margins and NOT user-independent exact utility labels.
Source archive `c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json`; archived original GitHub Actions run 37948775813 is marked SUCCESS in the checked-in historical receipt. No new native Stockfish call in this P30 turn.

## New local independent Go chess-law execution
Original P22 recovered 2026-10-09 Go source ZIP was re-extracted; original six tests passed fresh. New tests:
- `p30_archived_root_foil_pair_legal_test.go`: case6 root has 33 legal moves, original `c3a4` and changed `e4d6` both legal; case8 root has 44 legal moves, original `e6h3` and changed `h5g7` both legal. PASS.
- `p30_factual_foil_capture_test.go`: before move, h3 holds WHITE bishop B. After legal `e6h3`, h3 holds BLACK bishop b; after legal `h5g7`, White bishop remains on h3. PASS.
- Entire original Go test package, now 8 tests (historical six + two new), PASS with GO111MODULE=off go test -count=1 *.go.
New tools only contain test cases; original Go source remains in original authenticated Drive ZIP and is not copied into public repo, so the test files require source to run and should not be wired into standalone Python-only CI.

## Why this matters to Miller P30
It is a true, candidate-specific original-board fact that `e6h3` takes the h3 bishop and `h5g7` does not. But the archived Stockfish root recommendation actually differs with native root-order manipulation. Thus board fact truth and contrastiveness **do not by themselves imply a stable choice explanation**. This is an ORIGINAL-SOURCE-BACKED negative example of possible explanatory non-sufficiency, not evidence that bishop capture is strategically inferior, that engine scores assigned a unique causal factor, or that a near-equal preference is calibrated.

The important claim is modest: do not elevate a chess-true concept to a robust 'why best' claim until it survives root stability and independent value/consequence checks. It illustrates the distinction among:
1. Chess-factual difference, verified by source independent Go rules.
2. Engine root preference stability under manipulation, here historically false in these 2 of 12 original exposed FEN roots.
3. Plan value guarantee, not evaluated.
4. Human understanding and learning transfer, not evaluated.

## Forward
Use case6 and case8 as DEVELOPMENT counterexamples when implementing foil-sensitive score+plan explanations. For independently defensible performance results select NEW full-PGN-history source games before seeing outcomes; verify candidate pairs, root-order and budget stability, and independently compare plan consequence against strong plan-JSON, Stockfish+PV, statics and BinProp where target semantics match. Do not migrate old samples into prospective heldout.
