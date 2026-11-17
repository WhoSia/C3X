# C3X 0.30 S4-L/R11 — Leaf budget lowers gap error across two Berserk depths

2026-11-17 KST. [Design](C3X_030_S4L_R11_REPLY_ALLOCATION_PROTOCOL_20261117.md) · [Pre-judge forecast seal](../receipts/C3X_030_S4L_R11_PREJUDGE_20261117.json) · [R10](C3X_030_S4L_R10_REPLY_TRANSPORT_RESULTS_20261117.md).

## Scope and execution

Official TCEC S29 League 2 [PGN](https://github.com/TCEC-Chess/tcecgames/blob/3dd69a40b3cf6ccc74144df7411ef4e8e2140286/master-archive/TCEC_Season_29_-_League_2.pgn), 264 games. Eight admitted histories use distinct 12-ply prefixes and share none with the eight admitted Division P cases in R10. The two events are from one season. No earlier sealed cohort opened. All 16 admitted candidates have complete legal Berserk adjudication at both depths, all minimum/forecast points are ordinary cp, and all eight cases qualify for the fixed paired metrics. The ordinal mate rule is exercised by boundary checks, not used to change any observed paired result.

The arms had 48k requested nodes per candidate. Total reported nodes across 16 candidates were 768,616 PV, 768,726 tree 24k+3×8k and 768,615 tree 12k+3×12k. Candidate discovery differed between the trees in 7/16 positions (same full list for 9, overlap of two moves for 5, overlap of one for 2). This identifies the tested allocation policy as a whole. The terminal-only unbounded rule yielded 0/8 pairs for each arm. The declared endpoint using the last unbounded report within each budget yielded 8/8 for each. Berserk ran 508 legal-reply searches per depth, using 19,870,583 nodes at depth 12 and 54,571,293 at depth 14.

## Paired verdict

| Berserk depth | Metric | PV | 24k+3×8k tree | 12k+3×12k tree |
| --- | --- | ---: | ---: | ---: |
| 12, primary | Candidate order | 3/8 | 3/8 | 3/8 |
| 12, primary | Exact minimizing reply | 7/16 | 6/16 | 7/16 |
| 12, primary | Mean absolute gap error, cp | 44.500 | 48.125 | 42.375 |
| 14, sensitivity | Candidate order | 3/8 | 5/8 | 5/8 |
| 14, sensitivity | Exact minimizing reply | 7/16 | 5/16 | 7/16 |
| 14, sensitivity | Mean absolute gap error, cp | 35.750 | 39.875 | 35.375 |

The leaf-heavier allocation reduced gap error versus the R10 allocation in 7/8 games at depth 12 and 6/8 at depth 14. It beat PV on gap error in 5/8 games at each depth with one tie, but the aggregate depth-14 difference was only 0.375 cp. These are paired descriptive results on this event and an error measure across two different engine cp scales. Candidate-order counts were unchanged between tree allocations at both referee depths. The exact number of correct directions depends on referee depth: the judge reverses its own signs on rounds 3.1 and 3.2. R10's exploratory tree advantage on exact opponent reply did not recur against PV in this event.

## Failure isolation

At depth 12 the 24k discovery contained a minimizing reply in 10/16 candidates and selected one in 6/16. The 12k discovery contained one in 9/16 and selected one in 7/16. At depth 14 both discovered one in 9/16; they selected it in 5/16 and 7/16 respectively. Rescoring the discovered subsets with the Berserk values gave both trees 6/8 correct candidate signs at depth 12 and 7/8 at depth 14. That is a diagnostic using judge labels, not forecast performance. Some failures therefore remain even with judge values on the sampled replies, while additional failures occur in the Stockfish evaluation of those replies.

Round 3.1 illustrates independent variation in the ruler. The minimizing response after Bxf6 and Nxf6+ is …exf6 at both depths. The Berserk candidate gap changes from +15 cp at depth 12 to −12 cp at 14. Both trees name the right response to both moves and forecast Nxf6+; the reference sign changes independently of which reply was found. Conversely, round 1.5 was nominated at a 24-cp gap, yet the exhaustive reference gap was 179 cp at depth 12 and 146 cp at depth 14. This reinforces the distinction between a source-nominated close pair and a reference-stable close pair.

## Next gate

Keep 12k+3×12k as the budget comparator for a new cohort and retain the old R10 and PV arms. A fixed-reply follow-up should vary leaf depth on an identical candidate set to isolate valuation from shifts in discovered candidates. Require depth-stable judge rankings in a separately reported stratum, with selection fixed before outcomes. This experiment supports lower gap error versus the old tree in League 2, with no candidate-order improvement from reallocation at either depth. General tree superiority and cross-game transport of R9's internal mechanism remain open.

## Reproduction

Use the [runner](../harness/c3x_030_s4l_r11_allocation.py) in select, predict and judge stages and the [paired scorer](../harness/c3x_030_s4l_r11_score.py). Pass the R10 cohort via `--exclude` during selection. Judge arguments include its pinned network and the specified depth. The [depth comparison](../harness/c3x_030_s4l_r11_compare_depths.py) takes the paired scorer outputs in depth 12, depth 14 order. The new source and reused R10 cohort are verified by SHA-256 by the selector. R11 cohort and forecasts reproduced byte-for-byte. R10 selection also reproduces after the input generalization. Existing receipt tests passed 25/25.

The full primary depth-12 judge pass also reproduced byte-for-byte in a fresh engine process. [Evidence hashes](../receipts/C3X_030_S4L_R11_EVIDENCE_20261117.json) · [Drive raw archive](https://drive.google.com/file/d/1BQPYBC6FVyF_wlj71UvJ6lJAFf4Wq5jd/view). Archive SHA-256 `67e197849c2f603fc9ee86831f265f620316eea0b941f96426a31605bd314ef8`, independently verified after upload.
