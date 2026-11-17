# C3X 0.30 S4-L/R14 — Same-search added root trace

2026-11-17 KST. Prospective engineering pilot on TCEC S29 League 1. R13 showed that fixed-reply candidate rank, rank across all common replies, and rank under separate worst replies are different outcomes. R14 targets fixed-reply rank and asks whether root-search records add information beyond the public output of the exact same search. This is an engine prediction test.

## Select and freeze

Use the official League 1 PGN, Git commit 3dd69a40b3cf6ccc74144df7411ef4e8e2140286, blob 058e8b4238a7b1da30d2815e198dc43cf8f80c3f, SHA-256 1c06ef681343b833d2b76e7b89d3f7b669d916f8e714a084e2bb01ba84d19899. Use R10's first eight compound-round games with admissible MultiPV near pairs (24/32/40 plies, 48k requested nodes, gap at most 30 cp), excluding the opening prefixes in both pinned R10 and R11 cohorts. Select one question per admitted game. Find the first reply in the first candidate's Stockfish MultiPV=3 discovery (12k requested nodes) that is legal after both candidates. Drop the question if no such reply exists or either forced leaf is already terminal. No replacements.

## Same-search controls and prediction

Use the R4 Stockfish 16 instrumentation binary at SHA-256 3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb (`Threads=1`, `Hash=16`, `Use NNUE=false`). Run one fresh process per forced leaf at 12k requested nodes, MultiPV=1. The public tree and augmented trace forecasts are projections from the same two executions, each with identical node count and search options by construction.

1. Public tree uses the last ordinary unbounded public UCI score on each forced leaf.
2. Public-last control uses the final ordinary UCI score even when marked as a bound. Treat it as a prediction only and report bound receipt count.
3. Augmented trace starts from public tree. If the complete per-go root trace contains a strictly in-window root score in an iteration strictly deeper than the maximum public UCI score depth on that leaf, use the final such event in the deepest available iteration. Require the PV-update marker and ordinary score magnitude. Convert the internal value to cp using pinned SF16 UCI normalization 328 and truncation toward zero. Use the public tree value on leaves without a qualifying trace value. If a public baseline value is missing, both primary arms abstain.

Store the source event when used, raw UCI transcripts, exact game histories and predictions. Hash the question, source and derived prediction files and commit the freeze before any Berserk search. Score first-candidate minus second-candidate, using ternary sign with exact ties. Clearly report coverage, changed predictions, and wins/losses versus public tree on the same judged questions.

## Independent reference and ceiling

Berserk 14 uses the existing pinned binary and network, fresh search for each fixed forced leaf. Depth 16 is primary, depth 18 is sensitivity. Judge only an unbounded ordinary fixed-depth result. A favorable answer shows incremental information for this rule on these games. A zero or negative answer also informs rule choice. This pilot does not test engine mechanism causality, achievement of a named strategic goal, or human comprehension. Keep plan predictions and engine-rank predictions as separate experimental outcomes.
