# C3X 0.30/P7 — Five Original Chess Papers, Probe-OOD Court and Real P4-B Receipt Reanalysis

**2026-11-11 KST.** Evidence class: five original PDFs read and archived with same Drive IDs; two stdlib-only audit modules with actual CI; one successful **read-only reanalysis** of previously executed original Berserk14 16-search artifact. **No new native engine searches or trained concept probes** in this research unit. Older 0.29 same-world source→choice→future-strategy mediation and prospective 7/8 cohort remain HOLD.

## 1. Original PDFs actually owned/read and normalized

Five independent original PDF identities were verified by text, not filename alone, renamed by metadata and moved `00_INTAKE→10_PAPERS`, preserving original Drive ID and bytes:

| Study | Original PDF, held in Drive | Version and relevant method |
| --- | --- | --- |
| Pálsson & Björnsson (2023), IJCAI-23 pp. 4864–4872, *Unveiling Concepts Learned by a World-Class Chess-Playing Agent* | [source](https://drive.google.com/file/d/16yo6d9HdDeQb5PPZkB4wTbCNaZHD9AYO/view) | 100k Lc0 training positions used as sampled source; original NNUE/classical static evaluation and probe/surrogate comparisons; **not** evidence of engine root-decision mediation |
| Lomasov et al. (2025), *Exploring Human-AI Conceptual Alignment through the Prism of Chess*, NeurIPS Creative AI Track | [source](https://drive.google.com/file/d/1XT9sx64x3rZFWe-Lws9Kv5aIKZ6am14t/view) | 270M transformer concept probes by layer; classical STS and 240 manually labeled Chess960 positions for six concepts; **not** an NNUE intervention or a Stockfish experimental cohort |
| Hammersborg & Strümke, *Reinforcement Learning in an Adaptable Chess Environment for Detecting Human-understandable Concepts* | [original arXiv 2211.05500v1](https://drive.google.com/file/d/149LSvVfjKhonbp8foaZdsrOM7KeO9n0Q/view) | Uploaded text explicitly says submitted to IFAC; file is original **2022 v1 manuscript**, do not mislabel the PDF as final 2023 journal bytes. Smaller board configurations and accessible concept probe demonstrations |
| Wang et al. (2025), *Explore the Reasoning Capability of LLMs in the Chess Testbed*, NAACL Short Papers pp. 611–622 | [source](https://drive.google.com/file/d/1BiU2pPqgq47Reay1R2CR0sfuW_z_5qt2/view) | MATE-1M chess candidate positions plus strategy/tactical text; model chess move accuracy, not a pedagogical learning randomized trial |
| Eisma, Koerts & de Winter (2024), *Turing Tests in Chess: An Experiment Revealing the Role of Human Subjectivity*, CHBR 16, 100496 | [source](https://drive.google.com/file/d/1xIfLDSkUo0vdoI_s-96M2Du6GvIXzfuQ/view) | 24 participants, 8 blitz games each versus human/Maia/weak and strong Stockfish; human-likeness judgment **not** validated chess explanation teaching efficacy |

Notion original-paper reading ledger: [P7 record](https://app.notion.com/p/415ef561cf92810ba419edd25a015b7f).

## 2. Real P7 code and actual CI outcomes

**Existing P4-B frozen-source Berserk judge audit**:
- [P7 source](../product/c3x_p7_independent_judge_audit.py) · [8 synthetic tests](../product/test_c3x_p7_independent_judge_audit.py) · [real read-only stdlib CI #42928991732 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42928991732).
- Input from **original P4-B CI #42791282073**, artifact ID **13750384467**, source JSON exact SHA256 **f4543fa3dea84559658f09ce5be2501a81aacf213e119984b0778fcc59fb5a51**. Source tree remains as originally selected; never relabel a tested leaf as an exhaustive opponent worst case.
- [Real frozen P4-B read-only reanalysis CI **#42929630715 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42929630715). It downloads original full archive using workflow read permission, finds exactly one original file with the frozen **raw SHA**, then runs independent P7 parser on the original JSON; zero new engine queries. Original filename **P4_BERSERK_INDEPENDENT_EIGHT_LEAVES_SIXTEEN_SEARCHES.json**.
- Exact newly computed P7 audit output SHA256 **479bafa381fb300c253efa41ba60874ea98e59974279f496b4a2cc2295fa48c8**. Uploaded separate audit artifact from reanalysis run.
- At depths10→12, e4 chosen four-leaf minimum **−20→−19 cp**, d4 chosen four-leaf minimum **−21→+10 cp**, P7 depth12 min-margin e4 minus d4 **−29cp** (different first moves/futures; do NOT interpret as mathematically universal best/worst move). Four-leaf spans at depth12 e4=71cp, d4=8cp; selected ranges overlap. Native node counts e4 depth10=61,652, depth12=150,430; d4 depth10=47,915, depth12=189,907. Sum **449,904** across inherited original searches. No new native nodes from the P7 audit.
- For e4 the depth10 and depth12 argmin follow the same specific source path. For d4 depth10 unique argmin is included in depth12's **three tied argmin paths**. P7 guards tie handling and flags where the sets are disjoint.

**Concept probe and OOD receipt court (Pálsson/Lomasov-inspired)**:
- [P7 stdlib analysis](../harness/c3x_030_p7_concept_probe_ood_audit.py) · [nine synthetic contract tests](../harness/test_c3x_030_p7_concept_probe_ood_audit.py) · [CI #42929298023 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42929298023).
- Input requires per-concept train/test rows with game-disjoint splits and externally supplied 64-character position SHA fingerprints, standard-training only, independent standard and Chess960 evaluation, binary labels and heldout predicted probability. Rejects test probabilities outside [0,1], duplicate per-concept positions, absent class support or domain, training labels smuggled as confidence predictions. Computes train-prevalence baseline, accuracy, balanced accuracy, Brier, domain differences. No model training or inference in this unit, and game-group checks rely on provenance of externally provided game IDs. **It is a specification/verification harness, not an observed replicating experiment.**
- Further before serious probe publication: include canonical FEN+history hash for robust cross-split duplicate detection, independently verify chess concept labels, group bootstrap/error intervals, Chess960-legal input semantics, independent model checkpoint SHA, same-cost and same-state comparisons; then actually train NNUE activation probes and run interventions.

### P7 revised position-identity gate — 2026-11-11
[Position SHA cross-split audit](../harness/c3x_030_p7_concept_probe_ood_audit.py) now requires an externally computed `position_sha256` on each concept row and rejects any position fingerprint appearing in both train/test, even if adversarially renamed game IDs differ. [Nine real synthetic tests, CI #42930998989 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42930998989). The earlier [#42930693439 FAILED](https://github.com/WhoSia/C3X/actions/runs/42930693439) had old fixtures missing the new mandatory fingerprint; corrected tests without weakening the audit. This check prevents reuse of **identical provided hashes**, not fabrication of hashes, semantic board aliases, or history-sensitive equivalence; genuine canonical FEN+history verification is needed before calling this a scientific data split.

**Next original paper identified in bibliography (not owned by Drive search):** Pálsson & Björnsson (2024), *Empirical Evaluation of Concept Probing for Game-Playing Agents*, ECAI 2024, 874–881, DOI [10.3233/FAIA240574](https://doi.org/10.3233/FAIA240574). Its empirical study motivates separate probe decodability from claimed importance/causality. Also missing: Pálsson (2024) doctoral thesis *Explaining Intelligent Game-Playing Agents*, Reykjavík University (independent thesis asset; check overlap with individual articles before acquiring).

## 3. Scientific boundary

`Probe-decoding` establishes that labeled concepts are predictable from a representation. `Feature attribution` explains output sensitivity under a specified perturbation. Neither is necessarily original source code search-event causality, root first-move causality, future response-robust plan value, nor human learning efficacy. C3X scientific master [0.30](C3X_030_MECHANISTIC_STRATEGY_RECONSTRUCTION_MASTER_20261110.md) and historical Game14 retain their separate worlds, negative results and 7/8 HOLD.

## 4. Next reproducible studies

1. Acquire predeclared unseen position/game cohort; implement **actual** original Stockfish16 NNUE activation extraction and correct legal concept labels. Fit probes with game-group-disjoint cross-validation and independent Chess960 holdout; publish baseline, calibration, and untrained random labels as strict controls.
2. Compete Cui k2 vs k3 with measured actual source-search cost, **new** independently frozen Berserk judgments, independent engines and all-reply coverage caveats. Reuse frozen k2 **only as historical**, never as fresh k3 validation.
3. Connect verified concept-to-state features to legal conditional plan branches and ACT-Eval explanation facts; independently judge an explanation's correctness and learner decision benefit.
4. To promote the full flagship claim, demonstrate exact source event → parent/ancestor → native root selection → independently validated future strategy **in one world** with physical interventions and a prospective cohort.

## Missing primary literature (not owned/verified in Drive)

- Björnsson (2024), *Chess and Explainable AI*, ICGA Journal 46(2), 67–75, [DOI 10.3233/ICG-240256](https://doi.org/10.3233/ICG-240256).
- Pálsson & Björnsson (**2022 publication**, ACG 2021 event), *Evaluating Interpretability Methods for DNNs in Game-Playing Agents*, LNCS 13262, 71–81, [DOI 10.1007/978-3-031-11488-5_7](https://doi.org/10.1007/978-3-031-11488-5_7).
- Sadikov, Možina, Guid, Krivec & Bratko (CG 2006, revised proceedings 2007), *Automated Chess Tutor*, LNCS 4630, 13–25, [DOI 10.1007/978-3-540-75538-8_2](https://doi.org/10.1007/978-3-540-75538-8_2).
- Demura & Kaneko (2024), *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA Journal 46(2), 40–66, [DOI 10.3233/ICG-240255](https://doi.org/10.3233/ICG-240255).

These four exact paper titles/versions were not found in connected Drive original PDF searches; the corpus-wide absence is not proved. Do not list any of the five newly read/canonicalized articles as missing.
