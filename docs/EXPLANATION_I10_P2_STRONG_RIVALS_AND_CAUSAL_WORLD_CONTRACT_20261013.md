# C3X Explain I10-P2 — Mechanism-Identifiable Chess Explanations under Strong Commentary Rivals

**Stage**: COMPETITIVE_PRIOR_ART_AUDIT + ORIGINAL_CERTIFICATE_BOUNDARY_TRIAL PREREGISTRATION; 2026-10-13. **Research aim**: find a *defensible narrowly superior scientific result*, NOT rhetorically proclaim overall superiority to every model. Prepared *before* P2 original historical certificate audit run. No source-causal generalization, human advantage, Queen-strength or 0.26 release claimed.

## 0. Corrected 2026 frontier and original source ranks

Ablating only POSTECH's CCC is scientifically inadequate. These are distinct evidence competitors, not all runnable using one simple environment.

| Original work, verified source | What they already establish | Challenge for C3X and fair comparator |
|---|---|---|
| Jhamtani et al., ACL 2018, [full paper](https://aclanthology.org/P18-1154/) | 298K commentary pairs, pragmatic category/style conditioning and human fluency evaluation | C3X cannot claim prose generation itself novel; implement historically fair NLG/PGN baseline |
| Zang, Yu & Wan, ACL 2019, [full paper](https://aclanthology.org/P19-1597/) | neural chess engine-conditioned NLG, categories including **comparison and planning** | Rival pair comparison is NOT novel; test source-native mechanism, not mere 2-PV display |
| Feng et al., NeurIPS 2023, [original Drive](https://drive.google.com/file/d/1DrVnETseRKZ2oaYioMOols-T6zMuB0XA/view) | trained ChessGPT joint policy/language and evaluation | Need actually runnable model, not just typed interface |
| Kim et al., NAACL 2025, [original Drive](https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view), [official code](https://github.com/ml-postech/concept-guided-chess-commentary) | concept-guided CCC with human/GCC evaluation | Same engine evidence, equal language budgets; compare grounded falsifiable claims with credible human raters |
| Cui, Ling & Ng, 2026, [**full original Drive**](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view) arXiv:2607.11486 | actual engine partial-strategy-tree + language, **beyond-main-line opponent replies**, human/LLM player comprehension evaluations, limitations of concept-only and LLM-as-judge | Multiple branches and human benefit are NOT novel. Need source-event causal **replay/admissibility** over an exact pair, with counterfactual tests |
| Bhaskar, Cheng & Chen, **Queen**, 2026-10-02 [arXiv:2610.03695](https://arxiv.org/abs/2610.03695), [project](https://queen-project.github.io/) | 4B chess-expert encoder+LM with iterative candidate-rollout distillation, reported ~2697 Elo and fluent explanations; language-model coherence eval shows weaknesses | Elo/fluency/brain-like plans are **stronger than present I10**; compete on independently checkable **causal attribution to original executable**, not Elo. Original Queen source PDF not yet in Drive as of scan |
| Dionisopoulos, Majamaki & Ammanabrolu, ICML 2026 [PMLR](https://proceedings.mlr.press/v306/dionisopoulos26a.html) | real chess move performance vs reasoning faithfulness divergence under SFT/RL; trajectory SFT can improve fidelity | Language reasoning fidelity alone NOT a new C3X insight. Exact source intervention and mechanism-specific authority is proposed extension |
| Parfenova 2026 [Drive](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view) | move-hint masked explanation faithfulness controls and puzzle tests | Use masked response, spurious-token and mismatched explanation controls |
| Schut et al. **PNAS 2025** [original publisher](https://www.pnas.org/doi/10.1073/pnas.2406675122) | discovered teachable AlphaZero concepts with preliminary **grandmaster human learning transfer** | Human knowledge transfer is NOT novel; C3X must test an *additional, source-mechanism-grounded and transferable chess concept* beyond this |
| Spinnato 2025 [Drive](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view) | chess-piece SHAP counterfactual attribution to engine evaluations | 'counterfactual board changes' NOT intrinsically novel; contrast selected *source control-flow events*, not nonlegal piece ablation; explicitly preserve validity and preselected edit family |
| Hammersborg & Strümke, Scientific Reports 2024 [journal](https://www.nature.com/articles/s41598-024-70701-2) | open-chess-model information-flow **guarantee** | source-faithful guarantee itself NOT universally novel; distinguish claim domain (exact chess engine and event intervention, not neural input attribution) |
| Méndez et al., IST 2023 [Drive](https://drive.google.com/file/d/1jMrLzQEycFkCMIUSL2iLT1NdR1Td3ros/view) | chess-engine metamorphic testing and behavioral inconsistencies | Chess intervention & response testing NOT invented by C3X; add search-event source identity and explanation-consequence relation |
| Bhatlapenumarthi et al., **IEEE Access 2026** [publisher](https://ieeexplore.ieee.org/document/11658383), [authors' KibitzAI code](https://github.com/Pranav-Bhatlapenumarthi/KibitzAI) | Stockfish + PPO labeler + LLM narration, metrics/historical games | Compare current supervised human-facing system, not merely old ACL systems |
| Ciancarini & Pareschi 2026 [arXiv:2609.18286](https://arxiv.org/abs/2609.18286) | maps 84 chess strategic-reasoning study families and notes grounded explanation/human-AI collaboration gaps | Conceptual novelty must not be claimed on gap identification alone |
| **Jev / typed choice RLCD**: original [Tang & Zheng](https://drive.google.com/file/d/13cg7JKtrPH0K3j6QgTuIaA3d2Zitz5WV/view), [Deußer et al.](https://drive.google.com/file/d/1nyhsNdWIb2IBp8aX1jSUZzWpHWgCtoCK/view), [Gao & Wang](https://drive.google.com/file/d/1FIO-xUrgBYbcgy9FbPalf14zsGKz6Y-P/view) 2026 | typed candidate probabilities, efficient scoring, selective risk and per-rationale calibrated objectives | Decision schema/calibration alone has no chess mechanism validity. No calibrated weights or demonstrated target transfer yet |

The **unavailable** full original PDFs for Queen, IEEE 2026 and ICML 2026 were not found by exact-title/DOI scans of Drive this stage; **web publisher abstracts and official project pages** used instead, never falsely described as original Drive full-text readings. Other listed original Drive documents were fetched and read when expressly so indicated.

## 1. A defensible independent core contribution, not hand-waving

Let (B) be complete chess position+history; (E) engine binary/source revision/config; (r=(a,b)) actually legal rival pair; (Z) an exact chess-engine internal event identified by executable source, e.g., qsearch TT numeric-bound early-return; (I) a *fully specified admissible source or chess-board intervention*; and (D_E(B;r,Z,I)) the observed restricted preference and relevant event-level trace. The explanation target is **not** the best move in chess or human cognition, but a bounded effect of a mechanism in one engine/config/context.

We propose one distinctive evaluation artifact: an **Evidence–Mechanism–Language Contract (EMLC)** containing `(engine identity, exact board/repetition/history, original rival pair, intervention family, touched source locus, observed outcomes, independence limits, chess-semantic claim, proof/witness ID, allowed wording, abstention)`.

Candidate claim: A source-event intervention can (under some predeclared sampled cases) *causally switch* the original engine's rank/decision while a conventional narrative and static initial position cannot independently certify the search event as the source of that choice. This requires the **same executable original engine**, independently replayed source-defined event, controls, and a source authorizer. A pair of source traces with identical public board/score/PV but differing causal event applicability would provide a particularly strong nonidentifiability witness; **no such empirical indistinguishable pair is asserted without actual matching trace data**.

**Information-theoretic conditional proposition (not empirical novelty yet):** If two equiprobable engine worlds have the same complete inputs visible to a baseline `O(w0)=O(w1)` but different intervention-dependent source labels `Y(w0)!=Y(w1)`, every deterministic predictor based *only* on O must err on at least one world, and balanced accuracy ≤ 1/2; conditioning on a source-level distinguishing witness *may* overcome this bound. This is a generic identifiability observation, NOT original theorem or evidence any actual C3X pair meets its premises. Novelty would require constructing valid original-engine worlds and showing human-meaningful consequences that strong rivals miss.

## 2. Authentic P16 certificate research-only check (pre-results)

Use the repo's actual `c3x/certificates/g95-p16-local-minimal-full-bridge.json` **unchanged** (approved code/filename not altered). Scientific stage `0.7.0-G9.5-P16`, original engine **Ethereal**, local-only certificate ID `398eca8d6adf00525e6d5bf7`. Exact B0 FEN `r1bqk2r/pp2bppp/2nppn2/8/2PP4/2N2NP1/PP3PBP/R1BQK2R b KQkq - 0 1`, legal pair `d6d5` vs `e8g8`; TARGET queen d8→c7, SUBSET queen d8→d7, SHAM d8→d7 and recorded source event/behavior cells. Preserve *both* chess-board observational and source-event trace effects without conflation. Local minimality pertains to frozen admissible edit/chain family, not globally unique chess cause.

**Critical admission limit:** public I9/I10 `c3x/ontology/c3x-012-causal-certificate-trust.json` has `approved: []`; do **NOT** modify it or slip P16 into user-facing public CLI, nor attach an Ethereal-origin certificate to a Stockfish16 analysis. Instead create an independent **research-only derived interpretation** that checks source file identity, board legality, certificate scope, and returns **NOT_PUBLICLY_ADMITTED**, `source_causal_heritage=LOCAL_ONLY`, `concept_label=None`, `human_utility=None`. Tampered pair/engine/world provenance must fail closed. Merely reproducing an old local certificate is not new independent evidence.

## 3. Fair strong-rival experiment needed for actual superiority

**Equal-information comparison** (A all see same FEN, SAN/history, same engine ID/score, same bounded original PV, same token length, same LLM for wording): original I9; score+PV+LLM; CCC expert-concept+LLM; Cui branch-aware strategy+LLM; Queen *when accessible*, and EMLC with **source data removed**. C3X must NOT be declared superior merely because it alone sees extra trace information.

**Evidence-added intervention comparison** separately evaluates *value of genuine source data*: EMLC full original trace vs EMLC shuffled/false proof IDs, name-swapped pair, sham-vs-true source controls, wrong-engine source certificates, and explanation with only extra tokens. Use precommitted at least 32 source-disjoint nonterminal positions with frozen all candidates; report per-mechanism family raw denominators and don't pool correlated roots as independent cases. Each baseline may **ABSTAIN** instead of guessing a hidden cause. Give source trace to every competitor in an additional **equal-information plus trace** track to test whether C3X's *reasoning method* adds value, rather than mere privileged access.

**Outcomes distinct**:
- Source-causal atom precision/recall only where an independent source-native intervention judge supplies admissible labels.
- Root preference behavior and chess legality vs independent strong engine, not conflated with mechanism causation.
- Lie/tamper acceptance false positives, exact proof ID fidelity, context/engine-boundary abstentions.
- Strategy/reply understanding after move-name masking and independent unseen reply; blinded human raters, stratify by rating.
- Language quality, brevity, explanation selection; no single blended score hides failure axes.
- Engineering runtimes, request nodes, reported actual nodes and wall-clock separately.
- Probability calibration only for a real trained score head with independent test sets. No Jev/Clef performance claim from typed JSON.

**Primary falsifier:** under equal original evidence plus trace, strong CCC/Queen/Cui with an appropriately bounded verifier achieves the same source-mechanism precision, refusal and downstream understanding as C3X; then C3X architecture alone has no demonstrated incremental scientific value. Opposite possibility: C3X proves locally causal but humans cannot understand/use it, in which case scientific mechanism authority survives but human-transfer thesis fails. No universal superiority claim.

## 4. Stage gates

P2-P0 prereg and donor literature updated, P2-P1 research-only genuine P16 court planned. User's previously archived P14 source qsearch cutoff experiment is a different **Stockfish** operator family and cannot be swapped into **Ethereal** P16 certificates. No new `0.26` label or original-engine natural TT→SEE mediation claim can be made from a bridge demo. RDRC remains industrial-engineering support, not the scientific explanatory contribution.

Status `I10_P2_COMPETITOR_AUDIT_COMPILED; ORIGINAL_P16_CERT_RESEARCH_ONLY_PENDING; ALL_BENCHMARK_SUPERIORITY_HOLD; 0_26_HOLD`.
