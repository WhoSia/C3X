# C3X 0.29 — P42/R30: Owned-Paper Close Reading, 00→10 Canonicalization, SARFA Native Reproduction and Decision-Stage Controls

**2026-11-10 KST. Status:** *Learn → Implement → Validate → Integrate*. This unit is intentionally **prior-art technique accumulation rather than novelty promotion**. Original C3X scientific objective remains SAME-WORLD native source-computation cause → final root chess action → independently valuable response-conditioned plan.

## I. Actual Research OS bibliography custody — three PDF originals moved, not copied

Original folder: [`00_INTAKE — Literature Radar`](https://drive.google.com/drive/folders/1MLtYh0pv8QUZDReYzRqjDrOjRkSJAD16), destination: [`10_PAPERS — Canonical Literature Commons`](https://drive.google.com/drive/folders/1D2M4LHcejREhlyp6vTd71xxLLx-6ldUP). The move preserves original Google Drive file IDs. Before each move, the PDF MIME type and source parent were explicitly fetched and confirmed; after each atomic metadata update, file name and new parent were directly fetched and verified.

| Original author/year, bibliographic identity | Original owned PDF URL, verified original version | New **canonical 10_PAPERS** filename | Notion in-depth method note |
| --- | --- | --- | --- |
| Puri, Verma, Gupta, Kayastha, Deshmukh, Krishnamurthy & Singh (2020), ICLR, *Explain Your Move: Understanding Agent Actions Using Specific and Relevant Feature Attribution* | [1912.12191v4 original](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view) | `Puri et al. (2020) — Explain Your Move - Understanding Agent Actions Using Specific and Relevant Feature Attribution — ICLR 2020 — arXiv 1912.12191v4.pdf` | [R30-A SARFA notes](https://app.notion.com/p/414ef561cf928193a8e5c398b40e7aeb) |
| Sandmann, Lapuschkin & Samek (2026), NeurIPS, *The Algorithm Is Not the Behavior: Learned Priors Override Look-Ahead in a Chess-Playing Neural Network* | [2508.21380v4 original](https://drive.google.com/file/d/1dAF7reY9DpwBlZFERxrF54qSNYOLbRi0/view) | `Sandmann, Lapuschkin & Samek (2026) — The Algorithm Is Not the Behavior - Learned Priors Override Look-Ahead in a Chess-Playing Neural Network — NeurIPS 2026 — arXiv 2508.21380v4.pdf` | [R30-B overrides notes](https://app.notion.com/p/414ef561cf9281258b04ddadd32f14b9) |
| Ciancarini & Pareschi (2026), *What Counts as Strategic Reasoning? A Systematic Mapping of Chess Research on Humans, Engines, and Language Models* | [2609.18286v1 original](https://drive.google.com/file/d/1OxYGSk2bmFD4Rdr0tXHJPAWT_w-wkMyF/view) | `Ciancarini & Pareschi (2026) — What Counts as Strategic Reasoning - A Systematic Mapping of Chess Research on Humans, Engines, and Language Models — arXiv 2609.18286v1.pdf` | [R30-C mapping notes](https://app.notion.com/p/414ef561cf9281059f54c2e64e08b710) |

**Important custody qualification:** This operation updated name/parent metadata only; original file IDs remained unchanged. We did not calculate or claim an original raw-byte PDF SHA-256, nor re-upload duplicate PDF bytes. These three are CONFIRMED **held**, reversing R28/R29's earlier false missing-in-Drive claims.

## II. SARFA original methods (Puri et al., primary PDF §2, formulas 1–4)

A perturbation must be evaluated over an identical fixed action set `A`, for a chosen action `a*` and comparable action values `Q(s,a)`, `Q(s',a)`. Softmax `P(a|s)` yields specificity `Delta=P(a*|s)-P(a*|s')`. Exclude `a*` and renormalize other actions `P_rem`; source paper uses `D_KL(P_rem(.|s') || P_rem(.|s))`, then relevance `K=1/(1+D_KL)`. For positive admitted delta, `SARFA=2*K*Delta/(K+Delta)`.

### R30-A: exact numerical method *kernel* (no chess engine)
- [Production-style stdlib implementation](../harness/c3x_029_p42_r30_sarfa_section2_kernel.py), [math boundary tests](../harness/test_c3x_029_p42_r30_sarfa_section2_kernel.py).
- Stable logit softmax, action-set equality and at least 3 candidate actions for nontrivial off-target comparison, missing/nonfinite value fail-closed, `original→perturbed` signed delta reported separately from nonnegative saliency, explicit Q scale/temperature, reversed-action and extreme-score tests.
- **[CI SUCCESS #42744629448](https://github.com/WhoSia/C3X/actions/runs/42744629448)**, 25 combined tests for R30 A/B/C. Synthetic sample kernel saliency `0.6238210773806936`. **This is pure synthetic test output, NOT an actual chess attribution, causal effect, or human performance.**
- More complete SARFA published system (original Chess/Go/Atari saliency benchmarks and chess human studies) NOT reproduced.

### R30-D: real original Stockfish16 piece-removal saliency *method* pilot
- [Real-source pilot harness](../harness/c3x_029_p42_r30_d_native_sarfa_piece_ablation.py), [chess legality and mock UCI engine regression tests](../harness/test_c3x_029_p42_r30_d_native_sarfa_piece_ablation.py).
- [Original pinned Stockfish16 native CI SUCCESS #42745545135](https://github.com/WhoSia/C3X/actions/runs/42745545135). Pinned source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `Use NNUE=false`, one thread, hash 16MB, depth10, `chess==1.11.2` isolated in GitHub Actions.
- Original historical two R23-adaptively selected games Sahel/Cerrado, each with both originally nominated alternative root moves PLUS a deterministic lowest-UCI third legal control. For each original position clear move-stack consistently in baseline and removed-piece variants, preserving static side/turn/EP/rights. Choose first three legally admissible nonking piece-removal squares not affecting any three candidate source or destination squares. Assert all three candidate moves remain legal in each variant. This **does not establish a reachable game state**, and discards original repetition history, which is why it is method rehearsal only.
- For every original and three perturbed states, perform *actual source engine forced-root search for each of three candidate actions*: **two games × (1+3 boards) × 3 actions = 24 genuinely executed native source queries, 256,560 native source search nodes**.
- Source-side original forced depth10 candidate vectors, cp from root mover view:
  - Sahel: `e5f4 +54`, `e5c3 +35`, third control `a1b1 -636`.
  - Cerrado: `e5f6 0`, `d1c2 -4`, third control `c1a1 -22`.
- For each removed piece compare original and perturbed candidate Q vectors using R30-A original mathematical SARFA kernel with **a disclosed, ARBITRARY 100cp softmax temperature**. Source centipawns are not calibrated RL Q-values or probabilities.
- **Failed native attempts remain:** [#42745152390](https://github.com/WhoSia/C3X/actions/runs/42745152390), [#42745310899](https://github.com/WhoSia/C3X/actions/runs/42745310899). The actual original engine returned **mate score at depth10 on a piece-deleted source board (forced `e5f4`)**, which must not be silently coerced to ordinary finite cp. The final experiment explicitly declares `MATE_SURROGATE_CP=10000`, uses this bounded, **arbitrary** numeric proxy for the SARFA method and **counts every mate conversion**. It is not objective minimax and the output value may be sensitive to this imposed conversion.
- Final output JSON SHA256 **`9e5aae7a1e87aa8823484cb01519e35473649214cc9371bc22e15ec2278828f2`**. Public GitHub artifact ZIP hash/name recorded in CI. Rights scan passed as a *content scan, not an actual legal license certification*. Original full private PGN not copied.
- The true scientific status is **REAL_ENGINE_PAPER_PERTURBATION_METHOD_PILOT**, NOT Leela logit lens, NOT source code physical alpha-beta intervention, NOT same-world causal mediation, NOT prospective cohort, NOT independent referee chess value.

## III. Sandmann et al. (2026) primary PDF — internal look-ahead ≠ decisive final behavior

Sandmann et al. use Leela's intermediate-layer policy logit lens, identify cases where the eventually correct puzzle move is represented before being overridden at the final policy head, and investigate this through steering. The original paper reports 23,601 solved and 8,648 forgotten puzzles in its analyzed subsets and a **71.7% recovery** of forgotten puzzles under a prior-directed steering condition (attributed entirely to the original authors). Caveats explicitly acknowledged by the authors: mechanism of the overriding prior remains incompletely described, causal testing concentrated on a single network, and stockfish concept proxies restricted to one-step position values.

### R30-B: staged source-action observation contract
- [Implementation](../harness/c3x_029_p42_r30_source_stage_override_diagnostic.py) and [regression](../harness/test_c3x_029_p42_r30_source_stage_override_diagnostic.py).
- Requires same state identifier, same explicit candidate support, intermediate and final score vectors, actually emitted final action, actual depth/source identity. Reports three different notions: intermediate score argmax, final score argmax and observed final action. Mismatch between the last two is reported and **never silently reconciled**.
- Verified on synthetic examples in [same CI #42744629448](https://github.com/WhoSia/C3X/actions/runs/42744629448). No original Leela network/activation, no trained logit lens, no native Stockfish stage intervention was produced by this synthetic harness.
- **C3X synthesis:** R20 Game14 had an R18–20 *intermediate* root competition perturbation but final depth12 action did not change. Sandmann establishes in another architecture why intermediate mechanism representation cannot automatically imply final action. The Leela and Stockfish mechanisms are NOT identical; the analogy motivates a strict check, not a borrowed proof.

## IV. Ciancarini & Pareschi (2026) mapping original and stricter evidence requirements

The original manuscript systematically codes **84 Core + 19 Context** study families; it uses explicit evidence definitions and cautions that mention of a capability is not a demonstration that the paper directly operationalized/tested it.

**Exact original §4.5 nine stages, corrected after explicit PDF reread:**
- R1 board representation/legality; R2 assessment; R3 candidate generation; R4 search/lookahead; R5 planning/foresight; **R6 evaluation/trade-offs; R7 decision/action selection; R8 explanation/verbalization; R9 reflection/calibration/metacognition**.
- **Historical original taxonomy bug:** the first R30 implementation mistakenly mapped R6 to action and R7 to explanation, shifting later stages. It passed initial synthetic tests but failed the primary-literature fidelity check. Corrected [exact mapping implementation](../harness/c3x_029_p42_r30_strategic_mapping_evidence_gate.py), [original nine-stage locked tests](../harness/test_c3x_029_p42_r30_strategic_mapping_evidence_gate.py), and [historical evidence ledger](../evidence/C3X_029_P42_R30_HISTORICAL_EVIDENCE_STAGE_ADMISSION.json), then reran read-only CI **SUCCESS #42744629448**.
- R20 source event: mechanism perturbed but final root action unchanged. R27: true source-constructed recursive Cui-style tree and independently judged leaves without physical source intervention. R29: labeled nearby-negative temporal-event contrasts and no identified final-action causal origin. The strict **same-world source cause + final root change + independent same-horizon future-plan value + prospective original-source** admission accepts **0/3**, and this is the correct scientific HOLD.
- This is an original 84-paper mapping-*inspired* schema with three source receipts, **not** replication of the original complete 84-paper dataset.

## V. Integrated engineering architecture and genuine next research

| Method donor | Implemented module | What it can do for C3X | Missing part |
| --- | --- | --- | --- |
| Cui original held [PDF](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) | R27 genuine source recursive 2-level k3 tree; 36 frozen legal paths, 72 Berserk value calls | Source and independent response-conditioned plan representation | Full paper puzzles/human verbalization, prospective cases |
| BinProp original held [PDF](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view) | R28–R29 matched nearby-negative and path-event check | Fail spurious chess motifs with shared prefix and independent labels | LM concept discovery, cross-game frozen new cohort |
| SARFA original held [PDF](https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view) | R30 A exact math + R30 D real source piece-removal | Assess perturbation effect specifically on nominated action vs off-target action vector | Meaningful valid perturbation, Q temperature calibration, source mediation |
| Sandmann original held [PDF](https://drive.google.com/file/d/1dAF7reY9DpwBlZFERxrF54qSNYOLbRi0/view) | R30 B observed action-stage consistency contract | Detect non-equivalence between internal preferred candidate and final actual choice | Actual Leela replication or source-native stage intervention |
| Ciancarini original held [PDF](https://drive.google.com/file/d/1OxYGSk2bmFD4Rdr0tXHJPAWT_w-wkMyF/view) | R30 C nine-stage evidence-gated schema | Distinguish representation, planning, selection, explanation and human effectiveness | 84 study families codebook reproduction |

**Prioritize cross-method integration over another feature-count chase:** Choose a genuinely new legally frozen same-world source position and candidate support; collect calibrated comparable root-action vectors from physically perturbed ORIGINAL search code, with sham/no-contact controls; verify whether internal preference plus mechanism change actually changes the final action; apply SARFA-like specificity to the paired source vectors, Cui branch tree and BinProp nearby negatives to independently judged matched-horizon futures; gate the actual scientific claim through Ciancarini mapping. **Do not** call current piece-removal method a legitimate chess source-level intervention. Original Nov 9 C0 future cohort remains exactly **7 of required 8, HOLD**; PGN raw byte Drive custody unverified. If no eight eligible finished official games exist, do not silently change the cutoff.

## VI. File/layout and GitHub researcher rights audit

- PDFs renamed/moved without overwrite or duplicate, same Drive file IDs, verified current `10_PAPERS` folder parent.
- Three detailed Notion literature reading notes created and updated as implementation arrived; canonical scientific report retained in GitHub; CI content-read only and human WhoSia commits, no `GitHub-Actions[bot]` write authors.
- No Chat-mode `python-chess` installation. CI-A/B/C uses only Python standard library, CI-D uses pinned chess 1.11.2 and compiled pinned original Stockfish binary.
- Counts from verified execution: A+B+C **25 synthetic unit tests passing**, D **7 chess/UCI mock contract tests passing**, **24 actual engine forced searches** in D; source/J comparisons from R24–R29 inherited only within their original measured scope.

## VII. Drive 미보유 원문 — 이번 R30 인용 범위

**없음.** All five directly cited methodological primary PDFs (three new 00→10 promotions plus preexisting owned Cui and BinProp) are actually available in Drive. No article cited here is being relabeled “missing” without checking `00`, `10_PAPERS`, and arXiv-version filenames.
