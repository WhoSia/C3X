# C3X 0.16 — Independent Lichess Game-Law and Non-Pin Motif Audit (P2)

This is **working Go code and tests**, available in the authenticated [C3X P2 Drive source archive](https://drive.google.com/file/d/189VQpkW7R_HMl-FU0B0JQd-tUBr2h1nL/view), SHA-256 `baaa18716ad623f1d7af697370f067be7920982df3cc1bcdb3ea5309bbdb312e`. This GitHub directory is an entry point; avoid duplicating third-party raw PGN or historic source ZIPs.

Use the archived files `engine.go`, `engine_test.go`, `main.go`, `motif_core.go`, `strategy.go`, `san_test.go`, `freeze_lch_broadcast_sourceonly.py`, and `audit_twic_game_identity_overlap.py`.

### Reproduce privately

Use the **original** Lichess June 2026 broadcast PGN.zst (source SHA `65905d611c0d78d90ab57cd9edd3821f4119b46c22b5489fd7e265a74c6767b3`), source-frozen before engine outcomes. The Python selector first chooses 24 distinct Event-tag games using only GameURL SHA, then extracts mainline SAN to a **private local file**. Do not upload the selected game's raw SAN movetext to public GitHub.

Run `GO111MODULE=off go test -v *.go` in the unpacked source directory, then:

```sh
GO111MODULE=off go run engine.go main.go motif_core.go strategy.go \
  -input selected_24_private_movetext.json -output legality_and_motif_public.json
python audit_twic_game_identity_overlap.py
```

Actual local result: **6 Go tests pass; 24/24 legal Lichess mainline histories; 2038 plies**. Real legally played move geometry: 74 new value-ordered slider X-ray rays over 73 plies, 17 defender interference geometries and 136 possible defender-removal geometries; open-file and king-shelter proxies also counted. For TWIC1665 5,766 original game headers, 62 have no move sequence, 5,704 have source moves; 0 whole-history or 30-ply prefix matches with the 24 selected Lichess games.

**SCIENTIFIC CLAIM CEILING:** source move-legality and geometric opportunities, not tactically winning motifs, strategic value, source-native Stockfish nonpin operator mediation, full FEN disjointness, or independent-chess-law library certification of every position. Prior C3X 0.15 prospective accuracy FAIL remains.

[Public audit source receipt](../../c3x/receipts/c3x-016-P2-24-independent-Lichess-legality-multimotif-source-geometry-20261009.json) · [Physical TT P3 native outcome](../../c3x/receipts/c3x-016-P3-32native-physical-TT-writer-reader-2x2-exact-court-20261009.json).
