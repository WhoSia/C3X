# C3X 0.27 — P2: Explanation-Horizon Discovery and Human-Usable Evidence

Status 2026-10-19: **theoretical program and preregistration**, NOT a verified chess law or human-learning result.

## Initial problem
C3X started from the near-equal move comparison problem: why this legal move rather than a rival, and can people learn from the difference? A fixed Stockfish depth is a search budget, not an explanation depth or an evidence certificate. Available P10/P11/P0-P0F evidence: 9 outcome-selected boards, 144 P11 response rows (72 cold pairs), 36 root/evaluator/depth comparisons; P0 finite-PV intersections 13/72 FEN4 vs 8/72 FEN6; P0F actual legal replies on 42 Classical roots 38 and 40 while only two opponent replies are displayed at a time. Do not read nominal d17/19 as number of complete opponent-move plies in a proof.

## Three separate horizon variables
- d_engine: nominal iterative-search depth with source-specific reductions/extensions, TT and window-dependent censoring. Not equal to a fixed legal plies guarantee.
- H_rule: chess-ply horizon under which a predicate q is tested by exhaustive legal quantification; only a truly exhaustive, game-history-correct witness supports a universal claim for all replies at H_rule.
- H_explain: minimal declared move-horizon sufficient to convey a bounded, specific consequence contrast to a learner; this is a human-communication design quantity, and usefulness requires a separate transfer experiment.
Do not collapse these three into one scalar. A sampled PV can suggest H_rule but does not certify it.

## Novel proposal: Evidence Horizon Profile (EHP)
For history h, rival roots a/b, chess predicate q, explicit opponent-response policy P and horizon H, define a truth status in {TRUE_COMPLETE, FALSE_COUNTEREXAMPLE, UNKNOWN}. The status depends on a *quantified game-tree claim*, not on a single engine PV. For H=2, U(a,q) = forall legal opponent r exists legal own response t : q(state after a,r,t). To distinguish a from b on this property require U(a,q) TRUE_COMPLETE and U(b,q) FALSE_COUNTEREXAMPLE (or symmetric), with exactly-replayable legal witnesses and a counterexample complete for its inner existential. A single line is at most existential. Terminals and historical repetition rules must be handled explicitly.

Define empirical EHP(h,a,b,q,P,H) as a sequence of status transitions as H grows. No theorem that TRUE at H implies TRUE at H+1 for arbitrary q: without time-consistent reachability and predicate semantics, horizon monotonicity can fail. **Minimal sufficient horizon** H* only exists when a qualifying TRUE-vs-FALSE certification appears within registered Hmax. If none appears => UNKNOWN/NO_CERTIFICATE_WITHIN_BUDGET, not 'no reason exists'. A second notion, stability span, tests how long the exact declared contrast holds, not the time when a PV first shows it.

Potential XAI method grafts, each constrained by chess:
1. Counterfactual explanation: compare legal first roots plus a *feasible legal continuation/refuter*. No arbitrary removal of a piece from the board and claim it describes the original game.
2. Necessity/sufficiency ablation: remove or neutralize a *named predicate* using a legal chess intervention, with shams and negative controls. Legal causally matched interventions may be unavailable; report that.
3. Attribution: rank candidate structural predicates for discovery only; do not convert saliency/SHAP weights or move-frequency into engine/search causation without source-level controls.
4. Insertion/deletion robustness: test if deleting each statement from a commentary changes answer to a heldout 'what if' question; do not confuse language ablation with changing a board state.
5. Witness compression: minimize a legal certificate by stripping unnecessary moves, predicates and opponent policies while preserving its quantified proof obligations. This is relative to vocabulary/horizon, not an absolute unique cause.

## Design: P2-A through human bridge
A. Build q vocabulary from earlier chess microstructure: pin-legal move release, recapture admissibility, actual check defense, protected pawn break, repetition-aware draw availability. First choose ONE q and freeze its actual legal adjudication.
B. On original P11 states use full board history where available; otherwise explicitly bar repetition claims. Use 42/43 discovery and 47/99 negative *ranking* controls (they may still differ in real chess outcomes).
C. Bounded H=1/2/3/4 complete legal replay with proofs, short-circuit counterexample where mathematically sound. Distinguish node/computation cap from UNKNOWN; do not mark fail when timed out.
D. On an untouched **game/event disjoint** heldout sample freeze q/Hmax and interpretations before unsealing.
E. Build two-layer explanation: chess expert certificate (FEN/history, PV/branch, refuter, status, H) and learner commentary (one primary contrast, one line each side, conditional applicability, 1 'what if' question). Unlike prose fluency, assess whether a reader can distinguish next unseen near-equal choices.
F. Blinded human or structured learner test: C3X certificate-informed explanation versus score+PV-only, generic engine LLM commentary and no explanation; assess unseen-choice accuracy, counterfactual transfer, comprehension, calibration and time. No claim of superior human understanding before empirical outcomes.

## Existing research adjacency (external, not validations of C3X)
- XAI necessity/sufficiency via perturbation: Chen et al., ICML 2024 https://proceedings.mlr.press/v235/chen24d.html
- Feature deletion/insertion caution: Wang & Wang, ICML 2024 https://proceedings.mlr.press/v235/wang24br.html
- Faithfulness survey: https://direct.mit.edu/coli/article/50/2/657/119158/Towards-Faithful-Model-Explanation-in-NLP-A-Survey
- Chess explanation fidelity warning: Parfenova 2026 https://arxiv.org/abs/2609.22245 (preprint; treat as preliminary)
- Chess XAI and explanation needs: Bjornsson 2024 https://journals.sagepub.com/doi/10.3233/ICG-240256

## Falsifiers
If q is trivially true for both roots, or alternative opponent replies defeat the claimed universal condition, do not promote the contrast. If no bounded H* under fixed q/P/Hmax, abstain. If a certificate fails on source-disjoint cases, no general rule promotion. If learners improve in fluency ratings but not heldout transfer versus baselines, pedagogical claim not supported. Engine mechanism attribution requires separate Stockfish source intervention, not explanation-pruning effects.

Version title stays: C3X 0.27 — Counterfactual Consequence Geometry: Strategic Distinction, Continuation Fibers, Causal Witnesses & the Persistence of Chess Decisions. Historical 0.25, 0.26 immutable. Research leads implementation; no forced WSL, code persisted Drive/GitHub and Notion, WhoSia-only commit.
