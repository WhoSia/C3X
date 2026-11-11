# C3X 0.30/P8 — Six New Original Studies, Fritz Chess Saliency and Actual Stockfish16 Pawn-World Measurements

**2026-11-11 KST.** Same scientific C3X 0.30 research version, conversation C3X 32. P7 and 0.29/0.27 evidence are inherited, not rebranded. Results from this unit are a **small, manually designed, genuine native chess-engine demonstration**, not a reproduction of all Fritz & Fürnkranz original F1 annotations or 0.29 original engine decision event. Full original source→parent→root selection→future plan causal claim remains HOLD; new-event precommit remains 7/8 HOLD.

## 1. New uploaded primary sources: actual identity, reading and custody

Six PDF files were identified in Google Drive `00_INTAKE` by exact first pages and bibliographic contents; renamed as explicit edition/citation and moved in-place while keeping original file ID and PDF bytes.

| Primary work | Destination | Source PDF | Contribution and distinction |
| --- | --- | --- | --- |
| Fritz & Fürnkranz (2021), *Some Chess-Specific Improvements for Perturbation-Based Saliency Maps*, IEEE CoG | 10_PAPERS | [Original](https://drive.google.com/file/d/13orvM8vIILK80Uq9GlPC9QjHC0FD4BIe/view) | §VI-A inserts either white/black pawn on empty ranks 2–7, evaluates SARFA, takes the maximum; §VI-B discusses promotion, check, threatened/guarding and newly freed pieces. The article's evaluation limits off-action empty squares to three and uses expert annotations. These operations are **not** source-search causal interventions. |
| Pálsson & Björnsson (2024), *Empirical Evaluation of Concept Probing for Game-Playing Agents*, ECAI 2024 FAIA 392 | 10_PAPERS | [Original](https://drive.google.com/file/d/19v2rfaIoQi4Mk_0ckYaUelHswaNVxi_r/view) | Probe accuracy weakly correlates with task importance; compare ridge/LightGBM/NN probes and heldout self-play-derived Elo importance, plus **amnesic-like training-data exclusion**, not automatically an INLP representation intervention. |
| Baier & Kaisers (2020), *Explainable Search*, IJCAI-PRICAI XAI workshop | 10_PAPERS | [Original](https://drive.google.com/file/d/1Xkc4jhBDYNZtajV0LNPiR_Aehh5DX49T/view) | Explainable planning/search as an ongoing collaborative dialogue about possible futures, including trade-offs and summarization. Proposed research agenda, not a native Stockfish explanation proof. |
| Baier & Kaisers (2020-era manuscript, circulated for 2021 workshop), *Towards Explainable MCTS* | 10_PAPERS | [Original](https://drive.google.com/file/d/1w6GBaN-dr1-Ei3mFeco8SMIY4NYYPn8a/view) | Interactive branch summaries from MCTS. This is a different search family than C3X Stockfish16 alpha-beta; do not transfer empirical correctness automatically. |
| Lee, Wu, Dinan & Lewis (2022), *Improving Chess Commentaries by Combining Language Models with Symbolic Reasoning Engines*, **arXiv 2212.08195v1** | 10_PAPERS | [Original](https://drive.google.com/file/d/16YtM3PDpy_to1Crvwfl1YU4BqbxtCX8M/view) | Leela-derived control tags + controllable language generator, human judge preference; explicitly acknowledges remaining logical errors. Prior art to cite against P6 generated commentary; not an independent causal or educational-effect test. |
| Pálsson (Oct 2024), *Explaining Intelligent Game-Playing Agents*, Reykjavík University **PhD Dissertation** | **11_BOOKS** (thesis/book holding folder) | [Original dissertation](https://drive.google.com/file/d/1TZHIlLDUIpYii7WCb98PYwABNq2oQPKu/view) | A distinct doctoral dissertation on saliency, surrogates, concept probing, and search, including embedded prior papers. Not a sixth independent journal article; its Appendix A already contains *Evaluating Interpretability Methods for DNNs in Game-Playing Agents* full text — **remove this item from missing-content list**, even if no separately named PDF exists. |

**Citation provenance caveat:** Two Baier/Kaisers papers remain distinct research outputs even when close in date; the CWI file for `Towards Explainable MCTS` carries 2020 copyright text despite 2021 workshop circulation. The Pálsson 2024 doctoral dissertation is separate from its embedded article reprints and should not be double-counted as independent empirical observations.

## 2. P8 original Fritz mathematics integrated with inherited stable SARFA

- [Pure Python saliency evidence adapter](../harness/c3x_030_p8_fritz_empty_square_saliency.py) · [10 fail-closed tests](../harness/test_c3x_030_p8_fritz_empty_square_saliency.py). Actual [stdlib CI #42937299683 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42937299683).
- Original mathematical kernel inherited unchanged from [C3X R1 log-domain SARFA](../harness/c3x_030_r1_sarfa_logdomain.py); no unauthorized new attribution formula.
- **Contract:** two colors per candidate square, ranks 2–7, physical occupied/empty source check through an external chess-provenance gate, compatible forced-root action legal in every perturbation, same requested engine budget and exact compared action support. Incomplete two-color measurement is **UNKNOWN** rather than false zero. Numerical top three only for fully measured squares. Hard-coded move-square saliency floor is not admitted as physical evidence.
- Source record states exactly which legal paired Q values were supplied; adapter **does not check FEN itself** and does not create new engine data. This limitation is removed only for data created by the native runner below, which uses python-chess and records every corresponding FEN.

## 3. Genuine pinned Stockfish16 run: CI #42937724464 SUCCESS

- [Native source runner](../harness/c3x_030_p8_real_stockfish_empty_square_probe.py) · [Actual real-native CI #42937724464](https://github.com/WhoSia/C3X/actions/runs/42937724464).
- Pinned unmodified Stockfish16 source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `Use NNUE=False`, `Threads=1`, `Hash=16`. Python-chess 1.11.2 isolated in GitHub CI.
- Input **manually constructed legal** FEN `4k3/8/8/8/8/8/4P3/4K1N1 w - - 0 1`, three fixed forced root moves `g1f3`, `g1h3`, `e1f1`. Three **empty** squares `d4`, `e4`, `f4`, each with legal white and black inserted pawns. All perturbed FENs and each of three forced-root analyses are physically generated and checked. Engine analyses have identical **requested** `nodes=3000` cap, with actual nodes and depths recorded for each forced search. Do not claim identical actual search effort.
- **21 actual native forced searches**, total **63,037 actual nodes**, 3 complete two-color square pairs, 0 incomplete.
- `max[ S(white pawn), S(black pawn) ]` under the R1 log-domain SARFA kernel (temperature **100 cp**) ranked: `e4 = 0.3381522432300032`, `f4 = 0.12526991454025982`, `d4 = 0`. No human annotation F1, generalization or explanation efficacy measured.
- Original readback verified raw JSON SHA256 `dd819affa882d9f569f27a399d0b83494ee6cc6c8b1e882887450665caabf0f9`, CI ZIP archive SHA256 `9b5e4c11da5121443ca0c8ee393695167a84a1c7600cd88cfcb21b5b1673047b`.
- [Original P8 ZIP retained in Google Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/18IZCXfJelzn9pSDmz6SeHIteExN60PJ1/view) · [GitHub original run](https://github.com/WhoSia/C3X/actions/runs/42937724464).
- Previous P7 original Berserk reanalysis archive from #42929630715 was also finally uploaded successfully to [Google Drive sealed courts](https://drive.google.com/file/d/1IVpT4Zj1_NnUXAXutfUy5Hqgsouig_wG/view). Former gap is now closed.

**Interpretation:** a changed softmax preference under an artificial pawn insertion is conditional action-value sensitivity. It does **not** imply a square would have been encountered in the original search, or that this intervention changed the original natural root decision. No NNUE representation perturbation here; classical Stockfish demonstration only.

## 4. Research synthesis from actual primary sources

- **Fritz:** chess saliency requires considering negative space (empty-squares) and evaluation across position classes, but human importance labels, engine choice and completeness of possible continuations must be externally grounded. The 2021 publication reports experiments using tactical/strategic/endgame sets; our one manually designed board is not that benchmark.
- **Pálsson/Björnsson ECAI and 2024 thesis:** concept probe *decodability* is not behavioral importance; reported amnesic-like training exclusion is distinct from direct neuron ablation or causal original choice mediation. Therefore an NNUE activation probe high score is insufficient for C3X scientific claim.
- **Baier/Kaisers:** interactive plan explanation is a multi-step user-facing process. Distinguish tree summary quality from exact native engine source-search cause; don't transplant MCTS branch semantics to Stockfish alpha-beta.
- **Lee et al.:** symbolic-engine tags improve controllable language explanations over pure text models but still allow logical errors; our P6 ACT-Eval/replay factual gates remain necessary, yet correctness of commentary remains separate from learning benefit.

## 5. Next execution gates

1. Select original annotated **Fritz Bratko–Kopec and endgame sets**, license and citation audit, source-program code, freeze independent source board/action and expert labels. Compare occupied-piece-only SARFA with Fritz empty-square extension using precision, recall, F1; pair by same position and compute cluster confidence intervals. This is not yet executed.
2. Design explicit **without pawn perturbation / with both-color perturbation / king-check or lost-action exclusions** ablations with the actual engine. Measure search cost, depth variation, sensitivity to temperature, halfmove/FEN history and side-to-move.
3. Replicate Pálsson NNUE concept probe on verified native Stockfish NNUE checkpoints; use independent game-disjoint Chess960 holdout, then train/inference-performed concept importance counterfactuals. Source-search mediation remains separate.
4. Test claim-level correction with human readers; compare factual clause fidelity, response robustness, novice comprehension and decision improvement with blinded baselines.

## Only still unowned bibliography shortlist (Drive exact-title checked, not a corpus-wide absence proof)

| Priority | Original work not owned/identified as a separate accessible work | Why relevant |
| --- | --- | --- |
| 1 | Björnsson (2024), *Chess and Explainable AI*, ICGA Journal DOI 10.3233/ICG-240256 | Survey; P8 bibliography ancestry |
| 2 | Sadikov et al. (2007), *Automated Chess Tutor*, LNCS 4630 pp 13–25 DOI 10.1007/978-3-540-75538-8_2 | Early chess-tutoring explanatory baseline |
| 3 | Silva, Lelis & Bowling (2020), *Teaching Humans with Justifications of Monte Carlo Tree Search Decisions* | Human explanation and search teaching baseline, directly cited in Baier/Kaisers MCTS work |
| 4 | Elazar et al. (2021), *Amnesic Probing: Behavioral Explanation with Amnesic Counterfactuals*, TACL 9 160–175 DOI 10.1162/tacl_a_00359 | Intervention-style probe methodology and limitations |
| 5 | Kumar, Tan & Sharma (2022), *Probing Classifiers are Unreliable for Concept Removal and Detection*, NeurIPS 35 | Crucial strong counterexample to concept-probe removal claims |
| 6 | Bratko & Kopec (1982), *The Bratko-Kopec Experiment: A Comparison of Human and Computer Performance in Chess*, in *Advances in Computer Chess* pp 57–72 DOI 10.1016/B978-0-08-026898-9.50009-7 | Historic tactical/positional evaluation source, original publication not yet identified as held |
| 7 | Chakraborti et al. (2017), *Plan Explanations as Model Reconciliation: Moving Beyond Explanation as Soliloquy*, IJCAI 156–163 | Interactive explanation negotiation prior art |
| 8 | Tomlin, He & Klein (2022), *Understanding Game-Playing Agents with Natural Language Annotations*, ACL Short Papers 797–807 DOI 10.18653/v1/2022.acl-short.90 | Game-agent explanation language baselines |
| 9 | Kopec (1982), *Human and Machine Representations of Knowledge*, PhD Dissertation, Edinburgh | Human/computer concept representation, distinct **thesis** from Bratko–Kopec article |
| 10 | Demura & Kaneko (2024), *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA 46(2) DOI 10.3233/ICG-240255 | Weaker but complementary nonstationary initial-state training reference |

**Exclude as already owned by content**: Pálsson & Björnsson, *Evaluating Interpretability Methods for DNNs in Game-Playing Agents* appears as full original paper in **Appendix A of the newly held Pálsson PhD thesis** even if independent stand-alone PDF is not available; do not list it as missing. All six newly received originals above are owned and also excluded. 
