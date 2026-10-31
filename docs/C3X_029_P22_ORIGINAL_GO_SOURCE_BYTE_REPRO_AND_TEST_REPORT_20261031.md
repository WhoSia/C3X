# C3X 0.29-P22 — Original Go Chess-Law Source Binary Custody and Local Re-execution
Date 2026-10-31. Actual source acquisition and test execution, not a mere design contract.

## Literal source and raw hash
Connected Drive object id 189VQpkW7R_HMl-FU0B0JQd-tUBr2h1nL, name C3X016_P2_LICHESS24_GO_SAN_TACTICAL_STRATEGY_SOURCE_ONLY_REPRO_20261009.zip, size 23533 bytes, metadata MIME application/zip. Fetched raw bytes into assistant container.
Local SHA256 of downloaded ZIP: baaa18716ad623f1d7af697370f067be7920982df3cc1bcdb3ea5309bbdb312e. Exact match to earlier published README hash.
ZIP lists 13 members, including 12 entries in MEMBER_SHA256.json; every one of the 12 member hashes independently rehashed and matched (12/12).
Go toolchain /usr/local/go/bin/go available locally. Extracted source and ran:
GO111MODULE=off go test -v *.go
PASS 6/6:
TestPerft, TestLegalityUnderCheckAndPin, TestEnPassantDiscoveredCheck, TestSANKnownLegalMoves, TestSANEnPassantAndPromotions, TestSANRejectFalseAndAmbiguous.
All completed in about 0.04 s for the Go test process. Do not infer broad engine correctness from six tests.

## Prior result read, NOT newly re-run original PGN
legality_and_motif_public.json directly extracted and independently hashed against archive manifest. It states games=24, fully_legal_games=24, legal_plies=2038, games_with_illegal_or_unsupported_SAN=0.
However this ZIP does not contain the original private selected_24_private_movetext.json nor original June 2026 Lichess PGN.zst. Therefore the exact original 2038-ply end-to-end source reconstruction is NOT newly reproduced, only source-code unit tests and historical result-byte custody.
Original source SHA in receipt 65905d611c0d78d90ab57cd9edd3821f4119b46c22b5489fd7e265a74c6767b3. Private game selection result SHA  b8f20954db952b75fe52255f6f5ed6d8906c8c059c63720a7639bc51f0d6e600. Do not confuse private selection with public 24-game selection receipt SHA 21e5b06c1da0708bc94400c92952feb1628eb12563c8e17fcce4cd036e6ffaf9.

## Backflow to research priorities
Original Go engine and checker tests are usable for legal-move replays; no need to reinvent chess rules once import/repro contracts defined. Stored results have provenance but not necessarily prospective game-disjoint candidate-pair evaluation. P20 FEN-only and P21 bounded chess-law results remain separate, neither is a same-run complete source game reproduction.
Priority next: get original source PGN or sealed sampled private SAN by authorized read, recompute 2038 legal plies with exact source; independently inspect Go legal move generator; freeze future new game cohort before labels; run actual P11-P19 against predeclared rivals and compute game-level risk coverage. Private raw SAN and licensed broadcast source are never committed publicly.

## Claim ceiling
RAW ZIP HASH VERIFIED; member HASH 12/12; GO UNIT TESTS 6/6; historical JSON confirmed present. FULL ORIGINAL SOURCE REPLAY HOLD; STOCKFISH PERFORMANCE AND COMPETING EXPLANATION BENCHMARK HOLD.
