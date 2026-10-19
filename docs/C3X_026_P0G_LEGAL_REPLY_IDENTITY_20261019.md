# C3X 0.26 — P0-G: Legal-Response Identity Before Strategic Explanation

Status: preregistered observational analysis script, syntax-checked; native python-chess execution pending. No fresh Stockfish execution.

## Direction audit
P0-F HF1 source-verified 144/72/36 PASS. Development positive index42: Black Bc5 vs Bf8, opponent 38 vs40 legal moves; index43 Re8 vs Qf5, 36 vs37; control index47 Bxe5 vs Qxe5 35 vs35; **control index99 Rxc2 vs Kg2 29 vs35, and 0 vs1 checking moves**. 9 distinct boards only, repeated across evaluator and nominal depth. These are counts of the immediate opponent's opportunities, not intrinsic chess move values; control99 has larger differences than both development examples. Therefore a 'larger legal count contrast explains persistent P10 rank inversion' claim fails even as a specific diagnostic separation of this selected cohort.

## Scientific question
A pair of equal-size legal-move sets can have wholly different members; unequal-size sets can retain all relevant defensive moves. Which concrete legal reply moves exist only after one candidate root move? Observe and retain UCI witnesses, intersection, difference and Jaccard similarity for (all legal responses, legal checking moves, captures). Do NOT treat same UCI coordinates as semantically equivalent strategic actions on different board states; do NOT call them threats or causes.

## Implementation
`C3X_026_P0G_WITNESS_SET_AUDIT.py` takes original P11 SHA-protected 144-row JSONL, validates cold-pair repeat, source full FEN after each legal first root via `Board.fen(en_passant='fen')`, enumerates *all* immediate legal opponent moves with python-chess, contrasts fixed root pairs and verifies that legal-move sets are invariant to the engine evaluator and nominal depth for the same board. Print `P0G_PASS 144 72 36` only on success. Read-only, no engine. Script SHA256 `037364878936a8ec4437d9c1098e9c1c2195f52874c400dc1d6c98a6c450aaae`. Syntax tested, actual native run pending.

## Competing accounts
H_count: simple root-conditional count separates lasting P10 inversion from controls (not supported by P0-F control99).
H_identity: explicit opponent-response identities and tactical reply type could reveal a falsifiable difference (open; requires interpretation beyond UCI set identity).
H_search: no chess-response descriptor alone mediates search root ranking; protocol-sensitive computational path (open).
H_null: legal-response distinctions fail explanatory transfer (open).

Follow-on scientific gate: interpret concrete chess reply UCI moves and their tactical relevance with a legal second-ply witness and material/king exposure. Keep 47/99 in every comparison; do not tune a post-outcome classifier to four selected cases and claim validation. If no discriminating reason survives, ABSTAIN. Need independent case/game/event cohort and human test before asserting a general chess explanation.

## Custody
P0-F HF1 input JSON backed in Drive: https://drive.google.com/file/d/1IzvbLySKqxVgS4byi4laAdI5vXMkEVSl/view ; code lineage Drive: https://drive.google.com/file/d/1PG8RHZw3yWuUER4aVirNeQQdxr_PQfZ-/view . Add P0-G script and actual output to Drive primary custody upon export, with content SHA/readback. C3X 0.25 original title unchanged; C3X 0.26 official title unchanged. BOT_CONTRIBUTION_ZERO.
