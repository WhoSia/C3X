# C3X 0.29-P35/R2 — Origin Strategy Audit: Near-Tie Selection Bias, Strongest Prior Art, Broader Chess Mechanisms

**2026-11-04 KST.** This is an actual literature read and a mathematical **toy-model result**, not a fresh native Stockfish causal/NNUE intervention. Preserve P34 historical empirical state and P35/R1 design status.

## A. PI judgment: why the early near-tie focus was both useful and insufficient

The original choice of nearly tied root candidates was a defensible **experimental contrast** in a crowded explanatory-chess literature: it controls some gross material/tactical differences and produces falsifiable comparisons. The strategic error would be to elevate this convenient sampling stratum into the **exclusive explanandum**. Strategic value, causal representations and future plans also exist in larger value gaps and positions with diverse tactical/positional mechanisms. Conditioning exclusively on small observed gap risks selecting noise-unstable positions and underrepresenting robust, large-effect mechanisms.

**Decision:** RETAIN near ties as one preregistered stratum, OPEN intermediate and wide contrasts, and treat representational mechanism / legally valid future value / source-level search mediation as the cross-stratum research target. Never claim near ties to be inherently deep, novel or unbiased.

## B. Direct original PDF prior-art challenge (Drive first)

1. **Poupart (2024), _Contrastive Sparse Autoencoders for Interpreting Planning of Chess-Playing Agents_**, original user Drive PDF [ID 1jX9SqJCjdOSqmQ0f0r41L8YXJQCL567Q](https://drive.google.com/file/d/1jX9SqJCjdOSqmQ0f0r41L8YXJQCL567Q/view). The paper explicitly contrasts optimal versus suboptimal multi-step trajectories, studies Leela Chess Zero hidden representations with CSAE, proposes interpretable planning concepts, an automated taxonomy and sanity checks. **Therefore the claim 'first contrastive discovery of chess plans inside neural agents' is preempted.** Its section 5.1 notes SAE quality, human interpretation and contrastive interpretation issues. C3X must distinguish its target as specifically *Stockfish16 source-native NNUE accumulator/value and alpha-beta search ancestry*, not just using a different model brand. These deeper causal claims remain future evidence requirements, not established novelty.
2. **Schut et al. (2025), _Bridging the Human–AI Knowledge Gap through Concept Discovery and Transfer in AlphaZero_**, original user Drive [ID 1Mg4vfb2t-MIr6juCAzCC1qdv8sq1f8uj](https://drive.google.com/file/d/1Mg4vfb2t-MIr6juCAzCC1qdv8sq1f8uj/view). Discovers concepts via internal vectors, novelty and teachability filters and preliminary tests with four grandmasters. **C3X cannot claim first discovery or teaching of chess concepts from an agent.** Four-person study supports a limited proof-of-concept, not unrestricted generalization.
3. **Karvonen (2024), _Emergent World Models and Latent Variable Estimation in Chess-Playing Language Models_**, original user Drive [ID 1hx92z2vh0abRvszBV4JacLjWemnrHVGX](https://drive.google.com/file/d/1hx92z2vh0abRvszBV4JacLjWemnrHVGX/view). Chess-language-model board-state and skill representations validated with activation interventions; different system, but defeats broad 'first chess hidden world model' slogans.
4. **Geiger et al. (2025), _Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability_**, original JMLR user Drive [ID 1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK](https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view). Faithful causal abstraction requires interventions and a well-scoped mapping between levels. C3X's static score comparison and network heatmaps are not yet such an abstraction.
5. **Nasu (2018), _NNUE: Efficiently Updatable Neural-Network-based Evaluation Functions for Computer Shogi_**, user Drive English translation [ID 1zAxUc2M9AOplr3UFbKUrQ5PLcA-dLOwj](https://drive.google.com/file/d/1zAxUc2M9AOplr3UFbKUrQ5PLcA-dLOwj/view). The source makes efficiency, incremental update and coupling with minimax explicit; those mechanisms are not our inventions. Stockfish16 pinned implementation must be inspected directly before translating concepts from shogi / modern networks.
6. **Stockfish documentation** [NNUE architecture](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html), [historical architecture](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue_architecture_history.html). Historical versions differ materially; NEVER substitute current SFNN network descriptions for pinned Stockfish16 feature indices or net weights. Stockfish16.1 removed the classical evaluation and Use NNUE option; P34's **Stockfish16** classical-vs-NNUE experimental contrast cannot be silently rerun on 16.1+ ([official 16.1 release](https://stockfishchess.org/blog/2024/stockfish-16-1/)).

## C. A small but useful formal sensitivity result

Assume a fixed true signed contrast `Delta = V(a)-V(b)` in centipawns and two independently estimated per-move values with errors `epsilon_a, epsilon_b ~ iid Normal(0, sigma^2)`. For any nonzero Delta, the probability that a noisy observed difference reverses its true sign is

`P(reverse | Delta, sigma) = Phi(-abs(Delta)/(sqrt(2)*sigma)) = 0.5*erfc(abs(Delta)/(2*sigma)).`

This is a *demonstration under assumptions*, not actual Stockfish uncertainty. As `abs(Delta)` approaches zero, this probability tends toward 0.5. Thus selecting exclusively near-tie worlds can amplify **ranking instability**, even when their strategic mechanisms are not intrinsically hard. In addition, conditioning on an **observed** small gap differs from conditioning on a true gap, inducing selection effects that this unconditional formula does NOT quantify.

For hypothetical `sigma=20 cp` per move: gaps `5,10,20,50,100 cp` yield reverse probabilities approximately `0.429842, 0.361837, 0.239750, 0.038550, 0.000203`. These are mathematical values, not empirical Stockfish estimates. Code [margin audit](../tools/c3x_029_p35_r2_margin_audit.py) and [five local tests](../tools/test_c3x_029_p35_r2_margin_audit.py) were executed in a local Python sandbox: **5/5 PASS**. Server/CI native runs not claimed.

## D. Preregistered diversity-aware falsifier

Include score-gap strata: `near [0,20) cp`, `intermediate [20,100) cp`, `wide [100,+inf) cp`, all defined from a frozen pre-selection reference/evaluation. Thresholds are **design defaults**, not scientifically calibrated chess laws. Also cross-classify by material/tactical/strategic conflict and NNUE-vs-classical rank (concordant, reversed). Complete original-game identity disjointness is mandatory across development and heldout; game, not derived position, is the independence unit. Report each stratum's source games, candidate coverage, legal validation, baseline score, source mechanism diagnostics and uncertainty. Allow null/negative outcomes; do not require large-gap cases to help C3X.

**Fatal tests:**
- If relevant NNUE source activation mechanisms occur just as often across wide and intermediate gaps as near ties, the thesis that near ties uniquely expose them is rejected.
- If read-only NNUE measurements fail cold reproducibility or original-engine parity, do not proceed to named concept inference.
- If internal interventions shift evaluator score but not appropriately conditioned source-native root decision, do not promote source-to-choice mediation.
- If Stockfish+PV / already known chess concepts cover the same future outcomes at equal budget, C3X explanation superiority is rejected for that scope.

## E. Immediate execution boundary and governance

P35/R1 repository contract stays authoritative for source-trace methods. P35/R2 is **literature + mathematical toy + locally tested design validator**, not a 12-board cold replay. Native P35/R3 cold replay awaits pinned SF16 executable/network and authenticated original P34 ZIP loading. No 16.1 substitution. GitHub human actor/committer only; GitHub Actions is read-only compute and artifacts, NEVER `github-actions[bot]` repository authorship.

No newly introduced PDF is Drive-missing in this bounded search; **missing evidence** remains independent NNUE source activation evidence and disjoint chess-game replication rather than missing papers.
