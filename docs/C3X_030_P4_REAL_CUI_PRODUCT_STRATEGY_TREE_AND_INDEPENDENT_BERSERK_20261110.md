# C3X 0.30/P4 — Cui Two-Layer Strategy Tree in the Learner Product, Independently Refereed by Berserk

**Research date:** 2026-11-10 KST. **Scientific status: ACTUAL source Stockfish16 selection + ACTUAL distinct-source Berserk14 independent leaf court**, both successful read-only CI. This builds an actual educational-product component on P1/P2/P3 while continuing C3X 0.29/R27. It is not novel algorithm priority, not a full original benchmark replication, and not original Stockfish decision-source causal explanation.

## 1. Source-cited original research and continuity

1. [**Cui, Ling & Ng (2026), *Communicating Chess Strategies in Natural Language*, arXiv:2607.11486v1 — owned Google Drive full PDF**](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view). Its §4.1 constructs a partial strategy tree by keeping opponent **engine-ranked top k moves at opponent nodes**, and a player engine-best move at each following player node. k≤3 makes this tractable; the original work additionally studies conceptual keyword guidance, LLM verbalization and human/LLM downstream utility.
2. [**C3X 0.29/R27 existing true native two-opponent-layer k3 source implementation**](https://github.com/WhoSia/C3X/blob/main/harness/c3x_029_p42_r27_cui_recursive_k3_tree.py) and [**R27 independent Berserk court**](https://github.com/WhoSia/C3X/blob/main/harness/c3x_029_p42_r27_j1_cui_tree_independent_referee.py). Old experiments already constructed four roots × 3² paths over original exposed Sahel/Cerrado board histories, then independently evaluated original selected leaves with Berserk at depth12/16. **P4 is a product-generalization of a preexisting reproduction, not a scientific invention of this tree policy.**
3. [**Kim et al. (2024), Concept-Guided Chess Commentary — owned Drive original PDF**](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view): P2 7 exact board concepts for explaining differences. [**Hebbar et al. (2026), ACT-Eval — owned Drive original PDF**](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view): rule-based legality, capture and check checks. Original 2026-08-14 [C3X 1.md initial question held in Drive](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view): why Stockfish slightly prefers one move over a plausible alternative.

## 2. P4-A: real general FEN Stockfish source strategy tree

[**Product source algorithm**](../product/c3x_recursive_strategy.py) · [**7 standalone tests**](../product/test_c3x_recursive_strategy.py) · [**actual native read-only workflow #42790485394 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42790485394).

The newly reusable product module accepts `FEN + two distinct legal candidate UCI + k + source depth + original Stockfish UCI binary`. P4-A's frozen example is **the standard starting position**, independent of the historically exposed source cases. Root candidates `e2e4` vs `d2d4`. For each root, a depth8 source engine at each opponent node retains its **top k=2 opponent legal responses**, then source engine's single best own continuation, then repeats this for one further opponent ply plus one own continuation; **four actual opponent/own continuation plies AFTER the forced root**. This gives **2 roots × 2² branch paths = 8 genuinely searched complete source plans**.

Per root physical query accounting = **3 opponent MultiPV searches + 6 own-best searches = 9 native queries**; two roots **18** actual Stockfish searches. Source reported initial cumulative MultiPV per-query max node estimates 57,626 (e4) and 85,442 (d4), player nodes 71,093 (e4) and 121,729 (d4). MultiPV nodes are not a uniquely measured per-rank source expenditure. Python source-move legality and depth/nodes/PV guards prevent fabricating a line; early terminal branches are explicit and cannot be silently omitted.

Pinned official Stockfish16 classical commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, 1 thread, 16MB hash, NNUE disabled. **P4-A 42 previous and new tests pass**, original 8 legal leaf paths and identity contract verified.

**P4-A native source tree immutable JSON SHA256:**
`12889ac4239368b4c687a3ac7f3fb8fdff007bf03f04a31ace801d8ce2959f4e`.

Action artifact ID **13750388378**; ZIP sha256 `d53c06d28277baa79a9006295453b736267b4078d7c5813641cbfa562a9cbd48`.

First P4 source build [#42790446728 FAILED](https://github.com/WhoSia/C3X/actions/runs/42790446728) due to an incorrect commit-SHA transcription in new workflow, not a scientific negative. Explicit pinned correct 40-character original commit and SHA equality were restored; final #42790485394 is all green. No moving upstream `main` without pinning.

## 3. P4-B: source decisions frozen BEFORE independent judge

[**P4-B independent original Berserk actual source implementation**](../product/c3x_independent_strategy_judge.py) · [**6 referee tests**](../product/test_c3x_independent_strategy_judge.py) · [**actual independent native CI #42791282073 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42791282073).

A separate workflow first downloaded the exact P4-A source artifact and verified **raw JSON SHA256 `12889ac...`**, THEN checked out the entirely different **Berserk14** engine source SHA `8ae895a6151695be4a50d4fb65b0c131659c513a`, checked NNUE SHA256 `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`, compiled it, reconstructed **every legal 5-ply source plan**, and ran native Berserk at depths **10 and 12**: **8 frozen source leaves × 2 judges = 16 independent source-family chess searches**. All branch ranks and explicit path tuples are checked. The Berserk result is **NOT** allowed to reselect the Stockfish source opponent nodes.

| Root candidate | Independent Berserk depth | Min over only 4 source-selected paths | Max | Spread |
| --- | ---: | ---: | ---: | ---: |
| `e2e4` | 10 | −20cp | +66cp | 86cp |
| `e2e4` | 12 | **−19cp** | **+52cp** | **71cp** |
| `d2d4` | 10 | −21cp | +45cp | 66cp |
| `d2d4` | 12 | **+10cp** | **+18cp** | **8cp** |

All values are from **root mover's perspective** and **not a worst case over all legally possible opponent actions**. The depth12 observed `d2d4` paths have much lower spread than the `e2e4` paths, but this is *source-policy-conditioned leaf dispersion* in differing future worlds. Do not infer that d4 has a universally better contingent chess strategy or a user-facing explanation causal mechanism. The root analysis P3 used a different depth root score and is not a same-world matched leaf referee estimate.

Independent judge actual nodes at depth10: 61,652 (e4) + 47,915 (d4). Depth12: 150,430 (e4) + 189,907 (d4); **449,904 judge nodes total** across 16 native searches.

**P4-B final immutable independent report SHA256:** `f4543fa3dea84559658f09ce5be2501a81aacf213e119984b0778fcc59fb5a51`. Artifact ID **13750384467**, ZIP SHA256 `13d4903af361eb67f59766d12aea394b0d7c8714186d67bef0950a336e6b022d`. Original source tree SHA is embedded in the final judge report.

First independent judge workflow [#42790895723 FAILED](https://github.com/WhoSia/C3X/actions/runs/42790895723) before Berserk source download. A synthetic in-memory Python test changed a leaf that aliased a branch-path list and therefore caught a different fail-closed error than anticipated. Corrected test fixture with **JSON round-trip** to model actually serialized source artifact; **no source SHA gate or change to Berserk score computation** was relaxed. All **48 unit/regression tests** and 16 real judges pass in final #42791282073.

## 4. P4 in actual student-facing product UI

**Already implemented in product files:** [P4 source strategy endpoint in `c3x_local_web.py`](../product/c3x_local_web.py), [button and response region in `c3x_board.html`](../product/c3x_board.html), [actual nested tree renderer and API call in `c3x_board.js`](../product/c3x_board.js). The student now can click **'실제 Stockfish로 2단계 전략나무 확장'** after choosing two legal moves. The localhost-only HTTP POST `/api/strategy` accepts the same strict `FEN + move_a + move_b` inputs as P3, validates legal moves **BEFORE launching engine process**, and builds generic-position Stockfish source k2, depth8, two opponent layers on-demand. It renders candidate-specific opponent rank, first own response, second opponent rank, second own response, and complete UCI trace, with explicit partial-tree limitation.

**IMPORTANT:** P4-B's independent Berserk judgments belong to an archived original **starting-position** source tree SHA. The local P4 UI dynamically builds new source trees and must NOT display those original judge outcomes as though they independently validate any newly entered FEN. The UI reports current trees as **same-Stockfish-source-only**. Independent validation for arbitrary new FEN requires new frozen source artifact and a new independent judge run (or a suitable online isolated two-engine design).

Browser visual acceptance should be attributed **only** to a successfully completed actual Playwright CI run that clicks the P4 button; older green P3 visual QA did not include a second-layer tree.

## 5. C3X research constraints and next implementation direction

- Study window currently includes **2 initial source candidate roots and 8 source-selected descendant paths**. The eight paths share only two root decisions and four-ply generic source-induced responses, not 8 statistically independent games or a prospective trial.
- Source k2 is a purposeful **cost-limited product variant** of original Cui k≤3 and previous internal R27 k3, not the complete original published trained-language verbalizer, benchmark, or human performance test.
- Strong next direct product study: compare actual k2 vs k3 at matched search budgets; exact independent judge of source tree on fresh blinded real games, not the same old source-selected two boards; the iterative opponent all-replies coverage is unproved.
- C3X 0.29 program's real historic A+B+D+F original Stockfish **physical internal search intervention → final chosen root move → downstream same-world plan** is STILL HOLD; official pre-registered source cohort **7/8 HOLD** unchanged.
- External source method use follows scientific attribution and license requirements. GitHub is code and CI; Notion science verdict; Google Drive original PDF/data bytes only if verified stored, never asserted from Action artifacts.

## Drive 미보유 문헌

| Actually cited primary literature | Verified owned original full Google Drive PDF |
| --- | --- |
| Cui, Ling & Ng (2026), arXiv:2607.11486v1 | [보유](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) |
| Kim et al. (2024), CCC | [보유](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view) |
| Hebbar et al. (2026), ACT-Eval | [보유](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view) |

**추가 미보유 문헌 없음**. The source engine and independent judge may have separate license, network and release asset obligations, as already observed in current CI native builds.
