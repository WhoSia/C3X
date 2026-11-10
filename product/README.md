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

## Developer tests

```bash
PYTHONPATH=product python -m unittest -v \
  test_c3x_explain_two_moves \
  test_c3x_concept_contrast \
  test_c3x_local_web \\
  test_c3x_recursive_strategy \\
  test_c3x_independent_strategy_judge

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
