# C3X 0.30 D2 — Cerrado Reply Witness and En Passant

## Same-reply result

For case `04d52e451d89ee05`, the SHA-verified [R23](https://github.com/WhoSia/C3X/actions/runs/42558798075) all-reply unrestricted search and [R24 B2](https://github.com/WhoSia/C3X/actions/runs/42565712361) fixed own-policy aggregate both identify `g7f6` as the sole minimizing first reply to `e5f6` at depths 12 and 16. [R24 B1](https://github.com/WhoSia/C3X/actions/runs/42565383643) fixes `d2d4` after that reply. The [R25](https://github.com/WhoSia/C3X/actions/runs/42570536917) per-reply values recover both minima; [R26](https://github.com/WhoSia/C3X/actions/runs/42572119921) explicitly reuses those rows. R23 and B2 unrestricted searches report the same total node count, so treat them as archival corroboration and do not count them as independent replications.

| Berserk14 depth | Fixed d4 (cp) | Unrestricted (cp) | Fixed nodes | Unrestricted nodes |
| --- | ---: | ---: | ---: | ---: |
| 12 | −80 | −39 | 12132 | 24060 |
| 16 | −65 | −19 | 84754 | 220210 |

The minimizing reply did not change between these regimes. A within-reply search-condition difference accounts for the 46 cp change in the depth-16 minimum. Forced and unrestricted searches used unequal node counts. The historical unrestricted Berserk move/PV was not recovered from these archived outputs, so the 46 cp difference cannot be assigned to a named alternative.

## Chess witness

Legal replay from the published P1 board with python-chess 1.11.2 verified **16.Bxf6 gxf6 17.d4 cxd3 e.p. 18.exd3**. The double push does not bypass the c4 pawn. After the capture and recapture, White has an isolated d3 pawn. The line **17.d3 cxd3 18.exd3** reaches the exact same six-field FEN by an ordinary capture. This is a transposition for the compared lines, not an equality of available alternatives on the preceding ply.

[R27 J1](https://github.com/WhoSia/C3X/actions/runs/42581501872) independently judged three archived continuations from 17.d4 at depth 16 after White's 18th move: `...cxd3 e.p. exd3` −88, `...c6 e3` 0, and `...h6 e4` −11 cp. These are continuation scores at another evaluation point, distinct from the R25 first-own-action estimates. The sample is source-ranked and incomplete. The −88 line is the weakest of those three and supplies a concrete legal witness, not proof of unique cause.

[P1](https://github.com/WhoSia/C3X/actions/runs/42783144894) recorded Stockfish16 d8 choosing **17.Qc2 Rfd8 18.Qc3 e5**, −25 cp, after the same `gxf6`. The archived P1 first-reply MultiPV also has `17.e3` as a candidate from a different search context. Both are replay candidates. The central question is whether a delay of the d-pawn decision preserves useful continuations across plausible Black defenses, or whether a concrete tactical detail accounts for the observed values.

## Reproducibility and next experiment

Recomputed the evidence joins by case/root/reply and checked the original R23, R24 B1/B2, R25, R26 and R27 J1 JSON SHA-256 values against published receipts. Verified SAN, en passant legality and FEN equality on the P1 public board. Zero new engine calls. A targeted experiment still needs a fresh pinned Berserk14 executable with the original NNUE, full history, cold state and matched node budgets. Compare d4, d3, Qc2 and e3 from the same node, recording own first action and PV. Then separately compare Black replies to the competitive moves. Retain the Cerrado result as historical discovery and test any portability hypothesis on fresh games.
