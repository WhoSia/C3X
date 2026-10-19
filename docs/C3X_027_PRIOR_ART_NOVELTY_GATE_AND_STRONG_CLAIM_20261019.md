# C3X 0.27 — Prior-Art Collision and Novelty Gate for Research Memo 01

Date: 2026-10-19. Status: INITIAL PRIOR-ART TRIAGE, not systematic literature review.

## Verdict
The existing Memo 01 thesis ('one PV is not a universal proof', 'exists vs force', elementary finite chess certificate, verifier node count different from printed witness bytes) is correct but not publishably novel by itself. Game-tree quantification and adversarial search are established, proof-carrying explanations and counterfactual faithfulness literature exist, and chess explanations/teacher transfer have strong modern baselines. Do not claim first discovery of quantifier-sound chess explanations or of a minimal horizon. Memo 01 remains a methods-focused research memo, not a mature innovation claim.

## External references checked
- Bjornsson (2024), Chess and explainable AI, ICGA Journal 46(2), DOI 10.3233/ICG-240256, existing review of chess XAI and human-understandable rationales.
- Hammersborg and Strumke (2024), Information based explanation methods for deep learning agents—with applications on large open-source chess models, Scientific Reports 14:20174, DOI 10.1038/s41598-024-70701-2. Models' actually used information is central and strict guarantees studied; avoid advertising generic 'guarantee' as new.
- Schut et al. (2025), Bridging the human-AI knowledge gap through concept discovery and transfer in AlphaZero, PNAS 122(13) e2406675122, DOI 10.1073/pnas.2406675122. Finds AI-unique teachable concepts and tests on four grandmasters; unprecedented educational success cannot be asserted without stronger baseline.
- Barthelemy (2025), Chess variation entropy and engine relevance for humans, arXiv:2505.03251, complexity of PV and relevance for human players. Branch counts alone not sufficient novelty.
- Parfenova (2026), Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness, arXiv:2609.22245. Linguistic consistency, correctness and model decision fidelity must be independently discriminated; publication status must be rechecked before formal citation.
- Levene (2023), The phenomenon of decision oscillation: A new consequence of pathology in game trees, DOI 10.1111/coin.12570. Depth sensitivity and instability not a new phenomenon.
- Nanduri (2025), Explainable Chess AI: A Browser Extension for Move Explanation and Analysis in Real-Time Chess Interfaces, masters thesis. Stockfish+LLM tactical rationale pipelines already explored; LLM wrapper alone not novel.

## Specific novelty paths (hypotheses, not findings)
A. **Causally sufficient source-to-consequence certificate**: connect an intervention in actual Stockfish source (TT score read, SEE effect, qsearch and returned value) to a changed root candidate and a chess outcome property that persists after all legally relevant defenses. Must distinguish source contact from child value assignment, candidate reranking and actual root selection. Previous 0.19 K4 0/4 final restoration and 0.25 TT returns-without-value-mediation are informative negatives. Test on prospectively held-out engine positions and interventions; do not call this achieved.
B. **Proof obligation compiler with selective soundness**: user/LLM proposes a predicate with explicit response set and horizon, verifier returns certified true/false/unknown, and a compact independently checkable certificate. Novelty requires a nontrivial algorithmic improvement or guarantee over established AND-OR proof/disproof search, SAT/SMT, tablebase, model checking, proof-number search. Literal minimax relabeling is insufficient.
C. **Learning transfer conditioned on causal and legal fidelity**: randomized reader studies compare certified source-aligned explanations, certified but noncausal explanations, PV-only baselines, plausible LLM explanations; test unseen transfer. Existing Schut human-transfer study and 2026 faithfulness results make this a demanding bar.

## Experimental preregistration constraints
- Prospectively freeze claim and negative controls before looking at heldout games.
- Keep separately: chess-rule truth, model decision causal mediation, human transfer.
- New disjoint game source provenance, full move history when draw/repetition claims used.
- UNKNOWN on bound exhaustion; never promote certificate-serialization byte count into complexity lower bound.
- Compare to classical AND-OR game solving, proof-number search, tablebases and concept-discovery baselines; source-specific citation audit pending.
- Prefer a single falsifiable strong central thesis over three overlapping weak papers.
- Write manuscript fragments throughout: claim -> attack -> revise before new experiments, as Research OS active WRITING 3.0 requires.

## Next targeted question
Does any *verified* source-level Stockfish intervention change the final root choice on a heldout position AND does the corresponding chess consequence contract differ in a way that explains the change? At present no such full chain is demonstrated. Seek strongest source custody from 0.25 native M6 1/64 root-choice flip without extrapolating beyond one selected sample.
