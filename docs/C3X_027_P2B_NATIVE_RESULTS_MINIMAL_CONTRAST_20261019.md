# C3X 0.27 P2-B — Native Strict Recapture Results & Minimal Witnesses (2026-10-19)

**Source**: user-supplied `C3X_027_P2B_STRICT_RECAPTURE_H2.json` 765871 bytes; SHA256 `e990188ad9da4f2035d70d9010448157f8a41fe14830904245e68164d2ae8f0c`, `P2B_PASS 144 72 18 36`. Parsed **all** 72 arms, 36 pair comparisons; deduplicated by (index, first root) into 18 unique legal post-root states. All four evaluator/depth copies of each state's complete (reply, recapture list, capture flag) signatures agree. These are not 72 or 36 independent boards. Downstream reduced certificate file SHA256 `77cbaeb25368b36e3a9974e478831c526a97bdfb3cb06692947d48ad30f60c66`; 9246 bytes, locally generated, not certified by independent python-chess replay.

## Real native results
- Universal target: **0/18 PASS, 18/18 REFUTED**. For every legal reply r, immediately capture its just-moved piece is too strong; a legitimate quiet move is a counterexample in every observed state.
- Conditional classical recapture, restricting r to actual opponent capturing moves and requiring nonempty set: **15/18 PASS, 3/18 REFUTED, 0 EMPTY_CONDITION**. These are statuses of 18 **chess states**, not independent validation outcomes.

| index | First root A, legal/capture/targetable | First root B, legal/capture/targetable | Conditional status |
|---|---|---|---|
| 2 | f1e1 30/3/19 | g1g2 30/3/19 | PASS / PASS |
| 31 | a4f4 34/6/19 | a4h4 33/6/20 | REFUTED / REFUTED |
| 42 (development) | d6c5 38/1/13 | d6f8 40/1/14 | PASS / PASS |
| 43 (development) | a8e8 36/3/20 | d5f5 37/3/19 | PASS / PASS |
| 47 (negative) | c7e5 35/2/15 | f6e5 35/2/15 | PASS / PASS |
| 52 | d2b3 39/1/22 | g3h2 38/2/18 | PASS / PASS |
| 56 | a2a4 31/3/10 | b4b5 30/3/9 | PASS / PASS |
| 79 | c3e2 30/3/12 | f2f4 30/3/11 | PASS / PASS |
| 99 (negative) | d2c2 29/1/13 | h2g2 35/1/18 | REFUTED / PASS |

## Minimal factual contrast at index99 (conditional q only)
Original state FEN: `2r3k1/1p3p2/2q1b1p1/3p3p/1R1Q3P/1P2PBP1/2rR1P1K/8 w - - 0 28`.
- after White's `d2c2`, Black legal capture `c6c2` (the Black queen takes the White rook on c2); stored `recaptures=[]`. So the universal claim "every opponent capture can be immediately recaptured" is REFUTED.
- after White's `h2g2`, Black's only legal capturing move recorded is `c2d2` (Black rook captures the White rook on d2), which can be met by White `d4d2` (queen captures that Black rook). Since the capture-reply set is complete and has exactly one move, this is a positive finite certificate for the **specific conditional property** in the frozen horizon. The two states have different boards, so UCI-pattern identity is not a strategic equivalence.
- **Caution**: case99 was the **negative rank-flip control** (depth20 LOCKED cp tie, no strict persistent reversal), not a chess-strategy equivalence control. This chess-legal distinction does not show `h2g2` is better, more educational, or responsible for Stockfish's choices. The first root d2c2 itself captures an enemy rook, so these local opponent-recapture outcomes alone cannot rank the overall moves.

Index31: roots a4f4 and a4h4 both have capture-reply counterexample `a6b5` (capture true, `recaptures=[]`); no contrastive certificate under q. Development indices42/43 both PASS: current q fails to distinguish the target persistent P10 root-rank cases. Negative case47 both PASS.

## Scope and H*
This supports `H_rule=2 plies AFTER candidate first root` finite property conditional on capture-only opponent replies; it does **NOT** identify minimum explanation depth `H* = 2`. An H1/H0 property was not defined/falsified and game-history complete long-horizon persistence was not checked. Literal 'certificate minimization' is sound for index99 only relative to chess q and opponent's complete legal capture replies: single positive witness `c2d2 -> d4d2`, single negative refuter `c6c2` plus board/predicate/exhaustive legal move verification; need independent chess-library replay before claiming a standalone cryptographic proof. User-provided output already contains native legal enumeration, and exact source input SHA gates. Distinguish native report from independent rereplay.

## Human explanation candidate, not validated
'After moving the king (`h2g2`), if Black's rook captures the rook on d2 (`c2d2`), White can capture that rook with the queen (`d4d2`). By comparison, after `d2c2`, Black's queen may capture on c2 (`c6c2`), and an immediate capture of that queen on c2 is not available. This shows a difference in immediate recapture choices, not which first move is objectively stronger.'
**What-if question:** 'If Black instead makes a quiet move, does this certificate still establish the same claim?' No, the certificate's universal quantifier was explicitly restricted to opponent captures. Run independent learner study on heldout positions before claims of learning improvement.

## Scientific verdict
P2-B native success and concrete limited chess-structural witness: **PASS at software/legal-report level**. Hypothesis that conditional immediate recapture alone discriminates persistent P10 search inversion: **NOT SUPPORTED in selected development 42/43 and control99**, and may be anti-specific. H* identification, source-level search mechanism mediation and human transfer: **HOLD**.
