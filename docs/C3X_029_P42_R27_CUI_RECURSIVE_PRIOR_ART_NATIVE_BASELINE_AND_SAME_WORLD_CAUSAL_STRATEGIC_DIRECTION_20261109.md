# C3X 0.29 — P42/R27: Prior-Art Implementation, Native Recursive Cui Tree, Independent 36-Leaf Court, and Scientific Direction Reset

2026-11-09 KST. This is a **reproduction-oriented method engineering / origin return** research unit, not a new C3X flagship positive result.

## Problem and prerequisite

C3X's hard question is NOT merely 'do non-PV replies matter?' (Cui et al. already explicitly address that) or 'can an LM verbalize tactics?' (Cui, BinProp and Queen substantially explore explanation). It is whether a **physically executed original source-engine search state** that causes a real root choice is connected to a **response-robust and independently valuable prospective plan in the EXACT SAME legal game state**.

R24 first froze source actions for 147 legal replies, then used 588 independent Berserk searches. R25 generic top3 single-opponent-layer, R26 source-policy-stress top3 disclosed mixed outcomes, extra source cost 7.46M nodes, no universal advantage. R27 answers the prior-art engineering deficit: implement actually recursive engine-ranked opponent branching, rather than relabeling R25's first-layer k3 proxy as a complete Cui method.

## Prior art original and exact boundaries

1. **Cui, Ling & Ng (2026)**, *Communicating Chess Strategies in Natural Language*, Findings of EMNLP 2026, [official paper](https://aclanthology.org/2026.findings-emnlp.1560/), arXiv [2607.11486](https://arxiv.org/abs/2607.11486): section 4.1 constructs partial engine strategy trees. At the solving player's turn, use the engine's best move; at the opponent's turn, keep the top k_strat opponent moves according to that opponent's engine ranking. The complete work also includes language verbalization, human/LLM players, and Tree-Expanded Puzzle Playing. **This R27 reproduces only the explicit recursive tree-construction rule over two opponent levels on historical chess roots.** NOT the complete Cui evaluation.
2. **Press & Golubev (2026)**, *Explaining Chess and Go in Natural Language*, [arXiv 2610.23166](https://arxiv.org/abs/2610.23166): BinProp derives reusable binary motif predicates by distinguishing favorable/unfavorable trajectories and tests *nearby negatives* differing late in a positive continuation. The direct lesson is that simply identifying correlated board motifs does not establish a reliable reason. Reproducing BinProp's LM motif discovery / 200k calibration corpus is a separate substantial project, not achieved here.
3. **Bhaskar, Cheng & Chen (2026)**, *Language Models that Play Chess and Explain Their Moves*, [arXiv 2610.03695](https://arxiv.org/abs/2610.03695): Queen couples a strong chess encoder and language decoder with iterative move/explanation distillation. A 4B-model training program is NOT a proportionate first baseline for source-physical C3X; its relevant control is explanation faithfulness rather than merely fluent prose.
4. **Parfenova (2026)**, *Do Chess Explanations Reflect Model Decisions?*, [arXiv 2609.22245](https://arxiv.org/abs/2609.22245): move hints, unmasked narratives, and decoder preferences can make explanations seem informative without proving that the text faithfully captures how a choice was made. A C3X explanation decoder should include masked-move and deliberately mismatched-explanation controls.
5. **Ciancarini & Pareschi (2026)**, *What Counts as Strategic Reasoning?* [arXiv 2609.18286](https://arxiv.org/abs/2609.18286): broader taxonomy warns against collapsing planning, explanation, selection and human utility into one measured dimension.

## R27 T1: physically real two-opponent-level recursive k3 source tree

- [Successful source-native read-only CI #42580681868](https://github.com/WhoSia/C3X/actions/runs/42580681868) using original Stockfish16 source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, NNUE OFF, depth12, `Threads=1`, `Hash=16` MB, Python3.12 / chess1.11.2 in CI (not Chat). Predecessor original source JSON and 147-response frozen policy SHA validated.
- Four existing **R22-postselected** historical root candidates Sahel `e5f4`, `e5c3`, Cerrado `e5f6`, `d1c2`.
- After each root: opponent source-ranked top3 -> solver's source best -> opponent source-ranked top3 -> solver's source best. Branching yields `3 * 3 = 9` four-ply-after-root leaf paths per root, **36 distinct paths** in total, **64 genuine engine analysis calls**: 4 opponent MultiPV + 12 own best per root, four roots. MultiPV reported nodes can be cumulative; the per-query max is explicitly not certified as physical source nodes.
- **12/12 first-layer own moves agree with the SHA-frozen R24 independently generated source own moves**; this is a repeatability/compatibility observation, not a proof of strategy semantics.
- Frozen R27 source JSON SHA256 `f41e96bbf598aa824e65467cd1f1c782674aa275460211ce02b68f6eff1d4d5e`, artifact ZIP SHA256 `ca0c9e13e6db9b68a62b8972d0a44b5721d09978681e2c3a5a18da3b6fe0df1c`, artifact ID 13656418574.
- Source harness: [recursive builder](../harness/c3x_029_p42_r27_cui_recursive_k3_tree.py) and [tests](../harness/test_c3x_029_p42_r27_cui_recursive_k3_tree.py). Two opponent levels are modeled, no judge leaks into branch selection.

## R27 J1: independent evaluation of ALL 36 source-frozen leaves

- Original J1 [run #42581202376](https://github.com/WhoSia/C3X/actions/runs/42581202376) failed twice due to HTTP **504** downloading the exact 25MB Berserk NNUE release asset. No referee observations were produced. Historical failed attempts are not erased.
- Verified release tag 14's **official GitHub API asset ID 428781485**, added first-party API route with canonical GitHub download fallback and retained **same exact required NNUE SHA** `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`; no unverified alternate model introduced.
- [Final J1 SUCCESS #42581501872](https://github.com/WhoSia/C3X/actions/runs/42581501872): original sealed R27 source tree SHA verified, 36 chess-legal source paths reconstructed with full original legal history, Berserk14 commit `8ae895a6151695be4a50d4fb65b0c131659c513a`, independent NNUE bytes verified. **72 native Berserk searches**: every one of 36 4-ply leaves at depth12 and 16. Judge did not re-rank source branches.
- Judge JSON SHA256 `9844ebb1cae67d1af82c19696c8037ab53ca46b602ea44cdd66fc02d32ee27b7`, artifact ZIP SHA256 `86b292b3e3bb7e12e5e27eb1b4bfecdfb654ccd8c7fe5ec419c84d95a98864ec`, artifact ID 13657212530.
- **Measured depth16, centipawns from original root mover's perspective:**

| Prior selected root | Single rank1/rank1 continuation value MINUS worst of all nine preselected paths, cp |
| --- | ---: |
| Sahel e5f4 | +7 |
| Sahel e5c3 | **+36** |
| Cerrado e5f6 | 0 |
| Cerrado d1c2 | +23 |

- Thus 3/4 historical roots admit at least one more damaging source-selected off-main-line continuation than just the two most engine-ranked opponent replies. **These are finite-depth same-horizon sampled differences; they are not exhaustive adversarial legal-game values.** The overall finding reinforces Cui's known methodological motivation; do NOT portray it as a new C3X strategic-science discovery.
- Reviewer caveats: source and judge node/wallclock budgets differ; original candidate roots selected after prior findings; 2 clustered games/4 roots, no prospective sample; true human-decoder usefulness not tested; R27 tree leaf after four plies is a different horizon than R24 first-own reply judgment after two plies; do NOT compare their cp raw minima as matched endpoints.
- Source-only artifact and separate judge artifact are both real CI successes and SHA-sealed, but a full original per-query engine I/O trace with provenance remains a different audit item.

## Argument-first: possible actual distinctive contribution

**Define an empirical triad of necessary obligations, on one and the same source state `s`:**

(A) Mechanistic intervention: a predeclared source computation `Z` is physically perturbed in paired/sham experiments and changes root competition or the unrestricted final choice, with original source instrumentation and bounded search-context matching.

(B) Prospective action-conditioned plan: extract source policy `pi(s,a,r)`, first with Cui-style recursive tree as a strong prior-art baseline; compare under **independent judge** over enough diverse opponent responses, matched end horizons, and declared node/time budgets. Use BinProp-like *nearby negative trajectories* as hard controls for spurious motif explanations.

(F) Joined representation: a source-observed, source-attributable property `H(s,a,r,pi)` must systematically change as the causal `Z` is altered, in the **same chess world** as the choice. An explanation should enable move recovery **after removing explicit move strings** and reject mismatched/foil narratives. Do not infer natural mediation from separate A/B events.

A possible study-specific target is a measured conditional association between original-source intervention and future-plan property, with independent judging, *not* a theorem that all engine reason is strategy. Apply sham and no-contact controls; treat fixed-search instabilities as an identification threat.

## RAVEL: implementation program ranked by information value, not easy-paper count

| Priority | Next method / experiment | Explicit admission gate |
| --- | --- | --- |
| 1 | Full *Cui strategy construction* is now available at two opponent layers. Extend it to a genuinely pre-outcome heldout cohort; optionally verify Tree-Expanded Puzzle Playing under the same API, but do not confuse two-level trees with full puzzle replication. | New full original PGN source bytes, legal history and exposure audit, true pre-declared candidate roots |
| 2 | BinProp-like matched positives/negatives and **nearby negatives** from same-horizon paths, with pre-registered chess predicates and heldout support. | Never use judge labels for source tree selection; separate concept discovery from evaluation; mask move identifiers |
| 3 | Same-world original SF16 native computational intervention and NNUE activation/source feature inspection on chosen C cohort root candidates. | Exact code-site/source event, controls, ancestor path, root candidate identities, faithful cost and state accounting |
| 4 | Human/LM executable explanation comparison (JSON, concept only, source tree, Cui verbalization, masked/mismatched) including Queen-type representational foil if feasible. | No fluency-only success: action-recoverability, true legal moves and independent outcome |
| HOLD | More k3 top1 improvements on the 4 old R22 historical roots, or calling any single-lane result a causal explanation paper. | New unexplored causal distinction required to resume |

**Conclusion:** A stronger baseline has been implemented and independently probed. Our distinctive science now requires using its validated *policy structure* as a controlled component in a SAME-STATE physical source–future-plan study. The obvious result that off-mainline chess matters belongs to prior art, not to C3X's novelty claim.

Research-custody rules: read-only Actions, no GitHub-Actions bot commits, version/SHA pinned binaries, Notion=scientific claim truth, Drive=original bytes only when explicitly present and verified.
