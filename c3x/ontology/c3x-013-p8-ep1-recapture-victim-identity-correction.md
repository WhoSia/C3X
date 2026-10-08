# C3X 0.13 P8-EP1 — En Passant Victim-Identity Correction and Historical Tactical-Support Revision

**Status: PRE-AUDIT ENGINEERING REPAIR; NO NEW CHESS SCIENCE PASS.** Keep C3X 0.13 OPEN, 0.14 candidate only (no title).

The existing P7 root equivalence implementation checked whether the opponent's immediate legal capturing move *lands on* the just-moved piece's final square. This is incomplete in ordinary chess: on en passant, a pawn's legal capturing move ends on an EMPTY square adjacent to the just double-pushed pawn, yet removes that pawn from its different destination square. For example, original legal FEN 4k3/8/8/8/3p4/8/4P3/4K3 w - - 0 1 and White e2e4, Black d4e3 is a legal en-passant capture of the White pawn now on e4, although the capturing Black pawn lands on e3. The old direct-destination-only hazard returns no pawn recapture; a corrected hazard must count it.

Fix only the capture-victim-square geometry. For every immediate legal reply r, identify captured victim square: r.to_square for normal capture; for en passant r.to_square +(-8 if capturing side is WHITE else +8); count opponent attacker piece type iff captured victim square equals the newly moved piece destination. Preserve ordinary capture, promotion, check and source chess legality semantics. A test must show the old logic misses the EP victim and new logic counts one black pawn, while the initial FEN e2e4 has no such capturer. No mutation of chess engine scores or source cohort selection.

Before correcting old stage authority, run a **frozen-replay impact audit** against ORIGINAL unmodified Actions artifacts:
- P7-R1 run 37727746447: all 29 legal ply32 worlds and old exact tactic-support counts; recompute corrected census on identical stored chess FENs, report per-source changed root-pair support.
- P8-R1 run 37732629116: all original 32 broadcast ranks49–80 at plies32,64,80 with stored legal FEN, recompute corrected census per world.
- P7-R2 original 8 frozen tactic-filtered pairs and P8-R2 original 8 frozen pawn-birth-toggling pairs: recompute corrected root tactical signature for both candidates, count pairs originally admitted but now rejected; report specifically en-passant recapture root(s) and independent broadcast groups.
- Treat all affected old R2 engine preference numbers as real DESCRIPTIVE SCORES but *not valid tactical-matched experimental comparisons under revised P8-EP1 gate.* Do not delete old artifacts or replace pairs after knowing scores.

Define bugfix success as correct EP chess-rule recapture test and complete frozen replay impact receipt; it cannot confer causal concept explanation or 0.14 readiness. If no historical pair was affected, document a prospective safety correction rather than retroactively changing scientific results. If any pair was affected, apply scope-restricted revised scientific HOLD; preserve original source and run IDs.

P8 R4 reply-continuation study has already started using P8-R2 fixed pairs and should remain strictly retrospective development until EP impact adjudication.