# C3X 0.31/P2 — Supplemental Full-Game and Four-Field Board-Key Historical Overlap Audit

**Scope:** an additional **source-identity audit** of the existing *already pre-selected* TWIC1669 A4 64-game, 25-family candidate sample against exact original historical PGN-derived archives. It was computed **after B1 source-only freezing** and does not change the B1 sample, 128 physical event IDs, model probabilities or any B2 treatment arm. Never use this overlap audit to retroactively retarget source interventions or claim the P2 sampling was more independent than was originally established before treatments.

**Original fixed candidate:** source-only [Drive sample and P1 model](https://drive.google.com/file/d/1gp4VtTTzoBbAc8bOcEiHy13M9zd0uFqf/view), candidate \`C3X_031_P2_TWIC1669_PRE_NATIVE_COHORT.json\` SHA256 \`8b7f5da799cc9610c7e4cb8347baa8b3b8bd74eb383939eac9fa91b527a8116d\`.

## Actual independent exact-key comparisons

All three earlier primary original research ZIPs were re-downloaded from the user-owned Drive, CRC validated, and the exact structured \`positions[*].game_sha256\` and four leading FEN fields were compared with **all** 64 selected new TWIC1669 original cases, not a post-outcome subset. The same \`game_sha256\` is the SHA256 of original UCI move-history text, and the same FEN key is the (placement, side, castling, en-passant) tuple; repeated historical FEN with different halfmove/repetition context remains a further possible issue.

| Earlier archived source | Original source ZIP SHA256 | Historical frozen game positions compared | Same full-game SHA | Same four-field board key |
| --- | --- | ---: | ---: | ---: |
| C3X 0.30 R28 TWIC1671 separate reliance development \`frozen.json\` | \`8701b5df266eb1835da558a95498008e05453d6c81d421f798d22edf6fe00aef\` | 32 | **0** | **0** |
| C3X 0.30 R30 TWIC1664 \`cohort.json\` | \`b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e\` | 32 | **0** | **0** |
| C3X 0.30 R33 TWIC1671 original native archive \`cohort.json\` | \`e72ba91c0ffdbbb075642f044706d356fca84b4fa257a3ebcb7755db5837d8bd\` | 64 | **0** | **0** |
| **Checked total** | Three actual original research archives | **128** | **0** | **0** |

Primary original archives: [R28 Drive](https://drive.google.com/file/d/15NQNIt4xgkK5EaBOrsgbA76ZAFkyMd24/view), [R30 Drive](https://drive.google.com/file/d/1BMSvffPHCzNQXpSjpQlxD9BihJwn8neM/view), [R33 Drive](https://drive.google.com/file/d/1C3RZRyibwCthOaoWOLYu4IZNzdGlPJg8/view). No original user data was deleted or rewritten.

## Scientific conclusion and denominator boundary

The A4 sample has **no exact full-game SHA or four-field board intersection with these 128 inspected earlier game records**, independently strengthening the source selection audit.

This does **not** establish exhaustive disjointness from the entire history: R26/R27 TWIC1670, R29 TWIC1663, all other original archives and differently named synonymous tournament series were **not** part of this particular full-game comparison. The 94 original blocked family names and nine interpretable aliases remain a separate conservative approximate barrier, not a full provenance proof. **Retain this limitation even if P2 intervention and predictor later look successful.**

This is a *supplementary source-overlap analysis only*, using no P2-B2 treatment label, model prediction fitting or new engine search. It neither contributes independent samples nor changes the frozen original 64 games/128 event slots.
