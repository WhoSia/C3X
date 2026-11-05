# C3X 0.29-P42/R3 — Paper-Idea Court: Decision Reversals, Candidate Emergence, and Value-Preserving Explanations
Date: 2026-11-05 KST. **Research sketch, not a manuscript, discovery or new native empirical result.** Source-priority review of C3X Chat Archive 20–29, archival P8 and 0.27 reconciliation, P40–P42 and selected original Drive literature; public scholarly metadata cross-checked.

## 1. Three historically real anchor phenomena (do not rediscover as new experiments)
1. **C3X 0.20-B/C**: the failed initial first-child-return restoration (K4 0/4) was followed by a second-return restoration and a source-native alpha-threshold discontinuity at score -190 -> -189. Any causal explanation has to include the *actual* consumed branch, not the first interesting event.
2. **C3X 0.22/0.29-P8**: frozen 64 role outcomes have 10 root-choice flips; six switch to the other original O/F baseline, **four leave the two-baseline move support entirely**. Frozen exact-UCI forecast 38/64 against 54/64 no-change; O/F disagreement as pre-treatment risk marker, not necessary/sufficient general rule. Original P8 evidence: docs/C3X_029_P8_CANDIDATE_SUPPORT_FAILURE_AND_RISK_STRATIFICATION_20261031.md.
3. **C3X 0.27 September Game14**: native TT_FIRST changes unrestricted root bestmove b3a4 -> f3f4 and exactly one source-matched capture_prune guard bypass under TT_FIRST restores b3a4 in two cold runs (native run 39355504956). Historical post-selected localization, **not full natural TT->SEE->ancestor->root mediation, not prospective transport**. 0.28 planned 64-cohort has a historical castling-rights/identity gate HOLD.
4. **C3X 0.25 P14**: same board/TT key with different history can exhibit different search behavior; current-output sufficiency does not imply next-state transition sufficiency. History-aware abstractions and original rule 50/repetition behavior are essential, but generic Markov insufficiency is old knowledge.
5. **C3X P34/P40**: native NNUE/classical static order reversal exists in exposed games, not a causal neural feature-to-root bridge. P37 weak three-ply plan lost to strong PV, P40 score-bound correction favored 24k PV 5/5 identifiable. Preserve negative baselines.

## 2. Candidate paper A — priority mechanistic experiment
**Title:** *When Search Changes Its Mind: Source-Exact Decision Reversals, Candidate Emergence, and Causal Transmission in Chess Engines.*

**Scratch abstract (conditional future tense, NOT results):**
Modern search engines expose scores and principal variations, but such outputs do not establish why a move was selected. In historical Stockfish 16 interventions, local changes to transposition-table use and capture-pruning guards sometimes altered unrestricted root choice; four of ten altered decisions in one held historical cohort even selected moves outside both pre-observed root winners. We propose a source-exact causal-transmission protocol connecting intervention contact, branch activation, child return, ancestor value adoption, aspiration retrials, candidate set emergence, and final unrestricted root choice. On new event/game-disjoint data, the protocol would distinguish predicted decisions from posthoc reconstructions and test when localized manipulations transport beyond the original game. At present, only historical development effects are known, and no novel transport or fully mediated path has passed.

**Mandatory adversarial baselines:** vanilla trace correlates with winner; two-candidate switch; native Stockfish replay with SHAM; event-order/branch-matched negative controls; full-root vs forced-root modes; distinct source family if transfer claimed.

**Publishability gate:** pre-registered novel games with genuine legal histories, no outcomes used in source target selection, full native contact-to-root lineage, validated unrestricted root scores, predictive lift over strongest baseline with event-cluster uncertainty; replication under another independent environment where feasible. Fail if only bestmove flips or selected posthoc game14 effects.

## 3. Candidate paper B — speculative main chess-value question
**Title:** *From Viable Plans to Valuable Choices: Prospective Response-Conditional Certificates for Near-Tied Chess Decisions.*

**Scratch abstract:** A legal or low-regret continuation need not justify choosing its root move. We formulate distinct root quality Q(m), selective policy value W_P(m), and within-move regret R_P(m). We propose predictions of reply-conditioned future value sealed before independent reference evaluation, with calibrated abstention and rigorous baseline competition against Stockfish PV, Cui-style k=3 engine-backed strategy JSON, and BinProp-like near-negative concepts. The intended result is not more fluent commentary, but independently evaluated information beyond matched-resource source-engine baselines. The present research supplies synthetic logical limits and historical failures only; external chess-value judge and heldout advantage remain HOLD.

**Formal elementary lemma (NOT claimed novel):** Let v_r(m)=max_{u legal} V_J(smru), w_r(m)=max_{u permitted in P} V_J(smru), assume all opponent replies covered and at least one legal planned action per reply. Q(m)=min_r v_r; W_P(m)=min_r w_r; R_P(m)=max_r(v_r-w_r). Then
  Q(m)-R_P(m) <= W_P(m) <= Q(m).
Consequently Q(a)-R_P(a)>Q(b) certifies (inside the same exact finite J model) that the precommitted policy under a exceeds the unrestricted optimal worst-response value under b. For a **global** root preference, compare against ALL other legal root moves; the missing-third-candidate gap invalidates pairwise global claims. With interval scores, replace lower/upper bounds conservatively; finite J is not objective chess truth. Proof: v_r-R<=w_r<=v_r pointwise, take minima.

**Synthetic verification:** 20,000 deterministic pseudorandom three-candidate worlds of two opponent responses and four own actions were arithmetically checked; 0 failures of 0<=Q-W<=R or pairwise guarantee. Pairwise condition Q(a)-R(a)>Q(b) held in 1,854 worlds, yet 940 also had third candidate Q(c)>W_P(a), illustrating the *candidate-support closure* requirement. This is synthetic checking, NOT a statistical sample or novel mathematical theorem.

**Falsifier:** a single source-legal reply under a verified independent J with regret robustly above preregistered epsilon refutes universal low regret. Conversely absence of such a counterexample on a sampled subset cannot certify all-response quality. A success against weak JSON without success against Cui-style branch baseline does not count as novelty.

## 4. Candidate paper C — conceptual/explanation-faithfulness, heavy prior-art collision
**Title:** *A Move Is Not Its Reason: Three Independent Courts for Chess Explanation Faithfulness.*

Three claims separated: move quality, prospective plan quality, causal decision mechanism. A fluently valid rationale can fail any of the three. Parfenova 2026 already tests explanation influence on move behavior; Cui 2026 already tests response-conditioned human use; ACT-Eval checks factual explanation atoms; BinProp checks nearby negatives; Geiger 2025 formalizes causal abstraction. Without actual new registered natural-selection interventions plus independently judged future-value predictions, this is a **review/framework**, not flagship original experiment.

## 5. Candidate paper D — theoretical CS side branch, not flagship
**Title:** *History-Refined Abstractions of Alpha–Beta Search: From Observable Choice to Transition Sufficiency.*

Use 0.25 P14 same-TT-key/different-state cases to test what extra state distinguishes same current decision but different next computational transition. Need formal abstraction soundness for real source semantics, CEGAR proof with heterogeneous clocks/history and prospective neural policy improvements if claiming engineering impact. Generic hidden-state/Markov-counterexample alone is neither new nor evidence of stronger engine. Original prior techniques require rigorous novelty audit.

## 6. Priority and decision
- A: strongest **historical native causal evidence**; strong if prospective transport succeeds, risk of postselection and prior mechanistic search literature.
- B: strongest potential connection to **chess meaning and decision quality**, but baseline and independent J gate currently unpassed.
- C: dependent on A+B; most crowded adjacent prior art.
- D: theoretical backup, should not evade chess-value challenge.

**Provisional research program:** A and B as independent falsifiable tracks, attempt convergence only if a *same* heldout position/contrast supports both: high-quality source-predicted future value *and* a fully established natural-selection mediation trace. Do not conflate a local manipulated result with natural mediation; preserve negative forecasts.

## 7. Literature/version caution
Cui, Ling & Ng 2026, *Communicating Chess Strategies in Natural Language* (Drive original 19zqCJXM631qasR9uIyg4GuBZxIBO7czw); Press & Golubev 2026, *Explaining Chess and Go in Natural Language* (1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6); Jenner et al 2024, *Evidence of Learned Look-Ahead* (13QG6G_Ir67Q87Tkb1J9MOMn-TN4Zh63p) checked against original extracted text. Sandmann/Lapuschkin/Samek 2026 arXiv:2508.21380 latest source versions conflict among cached abstracts: arXiv stale v3 61.7% vs alternative v4 representation 71.7%; **do not quote a recovery percentage as settled without obtaining primary exact v4 PDF and page/figure context**. The exact latest v4 remains missing in the bounded Drive primary-source register; high priority. Parfenova 2026 BlackboxNLP and Ruoss ChessBench 2024 are already prior art.

## 8. Research OS
GitHub = code/notes; Notion = interpreted meaning; Drive = raw bytes. WhoSia author/committer only; no github-actions[bot] writes. This R3 is **historical retrieval + mathematics + tentative paper sketches**, NOT a new original chess cohort, independent judge or native CI success. Paper promotion remains HOLD. Next: source-verified Game14 event spine and full-root candidate support before a costly novel cohort.
