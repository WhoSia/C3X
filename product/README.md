# C3X local chessboard — running research prototype (0.30/P3)

**Original user question:** [C3X 1.md, August 14 2026 (owned original Google Drive)](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view): explain *why* an engine slightly prefers move A over B in a way humans can understand. The UI is a local research-grade teaching prototype, not a hosted product, an official chess.com plug-in or proof that it improves human learning.

## Quick start in Linux or WSL2

```bash
git clone https://github.com/WhoSia/C3X.git
cd C3X
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'chess==1.11.2'

git clone https://github.com/official-stockfish/Stockfish.git /tmp/c3x-product-stockfish
git -C /tmp/c3x-product-stockfish checkout 68e1e9b3811e16cad014b590d7443b9063b3eb52
make -C /tmp/c3x-product-stockfish/src -j2 build ARCH=x86-64

python product/c3x_local_web.py \
  --stockfish /tmp/c3x-product-stockfish/src/stockfish \
  --port 8765
```

Open **http://127.0.0.1:8765** in a local browser. The program deliberately binds only to `127.0.0.1` and does not require an OpenAI key, model download, or network service after installation.

**Windows:** Use Python 3.12, `python -m pip install chess==1.11.2`, build or obtain a corresponding local UCI Stockfish executable, and start `python product/c3x_local_web.py --stockfish "C:\\path\\to\\stockfish.exe" --port 8765`. A locally supplied executable not independently built at the pinned upstream revision is **not guaranteed** to be the same Stockfish16 binary as tested in CI. WSL2 browser access to a WSL loopback listener depends on local networking configuration.

## How to use

Paste a valid nonterminal FEN and click **국면 불러오기**. The browser receives its authoritative legal move list from Python's chess rule engine. For **후보 A** choose the two squares on the board, then switch to **후보 B** and click its two squares, or select SAN/UCI from the lists. Click **실제 Stockfish로 두 수 비교하기**.

The interface shows both root-move scores at two engine depths, the A−B centipawn gap from the original mover perspective, at most 3 ranked opponent replies under each move, a fresh own continuation, and seven exactly defined board concept measurements. **Attributes equal for both candidates are hidden** in the comparative panel. You can download a UTF-8 Korean Markdown explanation or inspect source JSON.

The initial starting position's `e2e4` vs `d2d4` is a convenient integration example, not a claim that there is a robust small strategic preference between those moves.

## P4 — Two actual opponent layers and independent judge

The product now has a second optional button: **실제 Stockfish로 2단계 전략나무 확장**. It calls the new native `POST /api/strategy` route for the FEN and two currently selected legal UCI moves, using **k=2 source-ranked opponent replies at each of two layers**, one source engine-best own answer for each. The interface shows each ranked opponent reaction, the response, the next opponent's ranked reaction, another response, and exact legal UCI path. This makes the originally [Cui et al. 2026 partial strategy tree original held in Drive](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) executable for arbitrary valid positions; it is **not** the original paper's LLM verbalizer or human study. Older [C3X 0.29/R27](https://github.com/WhoSia/C3X/blob/main/harness/c3x_029_p42_r27_cui_recursive_k3_tree.py) contains the more expensive original-source k3 two-layer tree previously implemented.

**Verified actual evidence:**
- [Original source k2 2-layer Stockfish16 8-leaf CI SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42790485394), 42 tests and **18 source engine calls**, exact tree JSON SHA `12889ac4239368b4c687a3ac7f3fb8fdff007bf03f04a31ace801d8ce2959f4e`.
- [Independent Berserk14 exact SHA-frozen source 16-search CI SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42791282073), 48 tests, original separately compiled Berserk source and original NNUE SHA verified. It judged only **those eight frozen source leaf paths** at two depths. The output is **not** a generic judge API for new user positions.
- [Real Chromium browser click-to-recursive-tree acceptance SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42791810831), 38 tests, actual P4 button click after e4/d4 selection, **8 actual source paths visible** in UI, desktop/mobile screenshots, Markdown actual download, browser JS exceptions 0.

[Full scientific P4 report](../docs/C3X_030_P4_REAL_CUI_PRODUCT_STRATEGY_TREE_AND_INDEPENDENT_BERSERK_20261110.md).

**Research boundaries:** The browser's new tree is same-Stockfish-source-only; no opponent-reply exhaustive minimax, no live independent judge, and no proof why the original engine made its final decision. Those claims need different experiments.

## P5 — Martin mirror invariance audit for actual root-move value gaps

[**Martin et al. (2025) original full PDF held in Drive**](https://drive.google.com/file/d/1bMl15sK_8G0h9GbuJehObn9zj8RoKKX7/view). In the web app, after selecting legal root moves A and B, click **원본·대칭 국면 12회 실제 재검색**. The local server then runs exact original Stockfish forced-root searches at depths **8/10/12**, original FEN and `board.mirror()` with UCI mirror-mapped positions, each candidate separately. The browser displays original gap `V(A)-V(B)`, mirrored gap, signed change and whether signs disagree. Same semantic player's POV is respected, including black/white swap. **Mirror discrepancies in finite-depth chess search are NOT automatic proof of engine bugs or true causal explanation failures.** No chosen confidence cutoff fabricated.

[**Real original source P5 native 24-search CI SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42922314048), two fixed illustrative positions × 2 candidate moves × 2 mirrors × three depths, 58 product unit tests, SHA-fixed JSON `ab6fec99e3b19e94b2b58e56e6605f4278ff84e74c04e2485326c723c50753b0`. [P5 full original-paper audit](../docs/C3X_030_P5_MARTIN_METAMORPHIC_GAP_STABILITY_AND_WIDER_DRIVE_PRIOR_ART_20261111.md).

## P6 — Eight chess-replay-proven Korean source strategy sentences

Inspired by [**Shivkumar et al. (2026) chess structured-annotation source in Drive**](https://drive.google.com/file/d/1BOP1Qx7kApbNWKCf7KbKbowPrTTTP6IR/view), [**QUEEN chess-language model paper owned Drive**](https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view) and [**Cui original strategy tree Drive**](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view). When clicking the **2단계 전략나무 확장** button, the actual server replays all P4 tree moves using the current FEN, validates every SAN and UCI against the source engine's tree, and generates **8 Korean conditional chess plans** (`if opponent X, own best Y; if reply Z, own followup W`). The UI now distinguishes `source-tree-candidate` and `source-annotation-candidate` panels and offers a **수순 재생으로 검증한 한국어 전략 설명 저장** button.

[**P6 frozen original source evidence CI SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42923308179), 68 regression tests and eight actually source-replay-verified Korean sentences, original JSON SHA `e8f84cab90b1e499e17c6a5746d9264f665741ee8ceb32a4d88bf0f3af5cef03`; Markdown SHA `b55102a0f9ab6abc2be9cc4e9b073cb47637bab6de9a83f72cfe05ed21e8c656`. [**Actual Chromium native P5+P6 browser acceptance SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42923800891), 40 tests, two candidate chessboard clicks, P4 source tree, **eight displayed real UCI/SAN-grounded Korean annotations**, **browser-downloaded Markdown byte-equal to the original frozen P6 CI file**, new P5 mirror gap table, real desktop/mobile screenshots, zero browser exceptions. [P6 research report](../docs/C3X_030_P6_REPLAY_VERIFIED_KOREAN_STRATEGY_COMMENTARY_AND_PRIOR_ART_20261111.md).

**Honest limitation:** P6 is a **deterministic annotation and rendering stage**, NOT an implementation of original QUEEN neural model, original Shivkumar PPO+LLM annotation engine, or original Cui full TEPP user study; it does not infer original Stockfish source search causality or prove independent quality in a new unknown user position.

## Developer tests

```bash
PYTHONPATH=product python -m unittest -v \
  test_c3x_explain_two_moves \
  test_c3x_concept_contrast \
  test_c3x_local_web \\
  test_c3x_recursive_strategy \\
  test_c3x_independent_strategy_judge \\
  test_c3x_metamorphic_gap_audit \\
  test_c3x_evidence_strategy_commentary

node --check product/c3x_board.js
```

[Full native GitHub Actions verified P3 workflow](https://github.com/WhoSia/C3X/actions/runs/42787312373): actual original upstream Stockfish source compile + 35 passing tests + localhost HTTP from FEN to engine search and concept projection + actual Korean report. **This is not a visual/browser acceptance** unless the separate P3-V Playwright workflow also passes.

## Technical boundaries

- **Rule-exact:** input legality, SAN, immediate capture/check, board feature definitions.
- **Native source-measured:** Stockfish16 classical depth8/depth10 forced root moves and three depth8 opponent MultiPV responses. There is **no** complete opponent universe or independent engine referee.
- **Concepts:** inspired by [Kim et al. (2024) original CCC PDF in Drive](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view). The seven measures are deterministic own material, passed pawns, pawn islands, attack targets, undefended attack-graph pieces, king-neighborhood attacked squares and opponent immediate legal move counts. This is NOT their pretrained predictor.
- **Response contingent:** inspired by [Cui, Ling & Ng (2026) original strategy tree paper in Drive](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view), but NOT a complete recursive strategy tree or human utility benchmark.
- **Chess rules claims:** inspired by [Hebbar et al. (2026) ACT-Eval owned Drive PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view), not ACT-Eval's original full dataset or language claim extractor.
- **Never promoted:** Original Stockfish internal physical decision causal attribution; Chess.com superiority; Maia-2's human move predictions. All remain **HOLD**.

The browser downloads are generated by **the local C3X server**, and the only exposed HTTP routes are HTML, JS, health, exact legal move enumeration and two-move analysis. Do not expose this experimental server on the public internet.
