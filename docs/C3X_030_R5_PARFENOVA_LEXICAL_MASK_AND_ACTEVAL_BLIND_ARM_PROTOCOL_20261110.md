# C3X 0.30/R5 — Parfenova Move-Masking and ACT-Eval-Grounded Control Protocol

**Verified 2026-11-10 KST.** **Implemented and executed a source-chess grounded protocol preparation, NOT the original 200-puzzle decoder-based explanation-faithfulness study.** The purpose is to build reproducible, label-isolated experiment inputs before using any real language decoder.

## I. Owned original full paper and exact methodological donor

[Angelina Parfenova (2026), *Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness*, arXiv 2609.22245v1, **original Google Drive PDF**](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view).

The original paper evaluates **200 Lichess endgame puzzles**, tests recovery of **generated move versus separate reference move**, and compares (i) FEN-only, (ii) explanation-only, (iii) FEN plus unmasked explanation, (iv) FEN plus maximal masked explanation, (v) FEN plus another puzzle's random explanation. The real paper includes **independently queried decoders and all-legal next-token preference scoring**. Its strict masking removes explicit UCI/SAN, coordinates, piece-square references, promotion and direct move phrases. Its finding that visible generated-move information can improve generated-move recovery does NOT establish reference move correctness or internal causal reasoning.

Second original method [Hebbar et al. (2026) ACT-Eval PDF in Drive](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) motivates independent chess-tool validation of factual claims. R4 exact checker already compiled/tested, no LLM used.

## II. R5 actual reusable implementation

[Parfenova-inspired five-arm input builder](../harness/c3x_030_r5_parfenova_move_mask_control_protocol.py) · [13 tests incl. blind-exports](../harness/test_c3x_030_r5_parfenova_move_mask_control_protocol.py) · [read-only CI](../.github/workflows/c3x-030-r5-parfenova-mask-controls.yml).

Source original archived P37 SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`, original pre-reference predictions `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051` are both byte verified in isolated CI. Two already-exposed game histories, four genuine nominated candidate root moves, complete legal original board reconstructions. For each root, use R4 ACT-Eval deterministic checker to validate move capture and check before generating the description.

An **artificial synthetic template** with explicit UCI and SAN serves as a positive lexical-leakage upper-bound; a conservative regex replaces UCI/SAN, coordinates, numbered moves, promotion words and piece-square move phrases. Source-programmatically generated templated chess text is NOT an existing model's independently generated chess explanation. This is a **limited lexical approximation** of the original maximal masking, not proof of no semantic or indirect move leakage.

All five original-paper inspired conditions have been represented as **20 protocol packets** (four root-world candidate instances × five conditions), and other-game texts are used for unrelated foil packets (not randomized sampling of an actual real explanation corpus). The five condition labels are `fen_only`, `explanation_only`, `fen_plus_unmasked`, `fen_plus_strict_masked`, `fen_plus_unrelated_foil`.

**Critical discovered design leak + repaired:** Initially the audit JSON contained both target UCI/SAN and the model input arms; passing the complete record as decoder prompt would leak target labels across arms and invalidate the experiment. R5 then added `blind_decoder_batches` and the required `--decoder-dir`, producing **five separate decoder-only arm JSON files** whose entries have strictly `fen` and `explanation` fields, with NO candidate UCI, source event ID, cross-arm shared IDs or reference values. These must be passed in **isolated decoder calls with no cross-arm context**. The truth-bearing original JSON is a separate scientific **audit artifact**; it must **never** be shown to a decoder. This is an engineering negative control, not an empirical decoder test.

## III. Observed CI receipts

- [Initial R5 #42755312403 — SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42755312403): 22 suite tests (R5 first 11 + R4 11), P37 SHA gates, 4 candidates × 5 arm packets = 20; no decoder or source engine.
- [Intermediate change #42755482606 — FAILED, preserved](https://github.com/WhoSia/C3X/actions/runs/42755482606): when the program first required `--decoder-dir`, the workflow had not yet been updated to supply it; CLI correctly rejected missing mandatory argument. The release workflow was repaired to pass an explicit path and export all per-arm files. Do not rewrite the history as if the failed run had passed.
- [**Final R5 #42755543672 — SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42755543672): **24** regression tests (new blind export and malicious masking injection tests added, plus R4 fact checker), original SHA gates, 20 packets, five separate blind decoder-only JSON outputs and scientific truth-bearing audit. Rights content scan performed. No Chat python-chess install; pinned `chess==1.11.2` on isolated GitHub Actions.
- Audit JSON SHA256 (full truth manifest) remains directly identifiable by original run; five blind outputs have individual SHA256 checks:
  - `explanation_only`: `71497e2bdbb7e240eaf1cb6a29e1bf3d8d4e19ce0e0a9fe02e9e9bafece5aea5`
  - `fen_only`: `3709dd687f468170af80446f7ebe853b51328a866161c572597b96abf0504bbc`
  - `fen_plus_strict_masked`: `178a33cfbe5b722d54aa7fb22de4d440bbc06df5d079465bea7188aab2db4de8`
  - `fen_plus_unmasked`: `9a245d1066fa05f4822d34e0c5208851e09f746d9099375b205198b50191d4f6`
  - `fen_plus_unrelated_foil`: `20ab9f46fca00b1f6fdb2f0483b8554f0c6bb7aba6dc37be4484528f4233795e`
- Final archive artifact ID `13735083135`, ZIP SHA256 `e019640a754e8e4189931d039bd08ba7adc39582dcb5d8d53efe8697e87a9976`. **There is no measured move-recovery rate or reference-move accuracy here.**

## IV. Exact limitation and next necessary true replication

To reproduce Parfenova's behavioral experiments rather than just the input format, first **acquire original puzzle benchmark or transparently specified independent comparable source**, freeze puzzle targets and independently generated explanations, choose and pin a real decoder and a distinct scorer, test masked/unmasked/FEN-only/explanation-only/random-text arms **in isolated and randomized decoder contexts**, report separate recovery for generated versus reference moves, all-legal scoring, calibration and null/error rates. Untested natural-language indirect clues must be audited; regex itself is neither proof of blindness nor faithful decision explanation. Independent chess source root mechanism and same-world causal plan are still HOLD.

C3X 0.29's precommitted new 8-game source gate remains exactly **7 of 8 eligible, HOLD**. No source raw-byte Drive custody established by these tests.

## Drive 미보유 문헌

None among Parfenova and Hebbar ACT-Eval: both original source PDFs are confirmed held in Drive. Original 200-puzzle case data and trained model weights are **not** verified as held and must be checked separately before claiming full experiment replication.
