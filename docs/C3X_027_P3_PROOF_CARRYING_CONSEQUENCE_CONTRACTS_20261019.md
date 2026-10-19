# C3X 0.27 — P3: Proof-Carrying Consequence Contracts and Explanation Delegation

2026-10-19. Official title unchanged: C3X 0.27 — Counterfactual Consequence Geometry: Strategic Distinction, Continuation Fibers, Causal Witnesses & the Persistence of Chess Decisions.

## The central repositioning
P2-B index99 commentary was a *sample of a small legal certificate*, not the research endpoint. C3X must characterize chess-state result claims and their quantifier semantics across (a) completely obvious tactical cases, (b) ambiguous strategic cases, (c) near-equal first-root moves; avoid selecting only difficult near-equal cases. Later LLM can choose, compress, express and scaffold correct facts but must not invent stronger evidence than the certified contract.

## Defined research object
A **proof-carrying consequence contract** C=(h,a,P,H,Phi,Q,T) specifies source position with relevant full historical state h, legal root a, an explicit opponent response family P, a bounded future horizon H, a decidable chess outcome predicate Phi, alternating game-tree quantifier rule Q, and terminal conventions T. Status is certified TRUE, certified FALSE, or UNKNOWN. Comparison between roots a,b must separately identify whether it compares (i) legal opportunity, (ii) forced guarantee, (iii) simple material outcome on selected lines, (iv) source-engine mechanism, or (v) human comprehension; no automatic implication.

A universal robust result requires coverage of **all** allowed opponent branches, not just a saved PV. An existential tactical counterexample may require only a verified legal line. For 'for every opponent move there is an own defense' claim, negative certificate must show one legal opponent move and failure of every legal own defense. The certificate must be independently checkable relative to the original h/P/H/Phi/Q/T. At longer H terminal states, draws and repetition demand a full history or explicit limited semantics.

## Discovery proposal: certificate-frontier rather than one magic depth
The research should examine a set of admissible certificates indexed by:
(1) legal ply horizon H, (2) declared opponent-response coverage or policy P, (3) verified claim language Phi/Q, (4) computational verification cost C_cpu, (5) independently checkable certificate size C_proof, and (6) explanatory burden C_human (measured only empirically).
These are different dimensions, not one 'XAI depth'. Minimal horizons may be undefined and different predicates can have incomparable minimal certificates. Define a partial order on certificates only **for the same claim, source state and admissible policy**. An earlier failure of a fixed-H predicate does not in general prove its failure for other H. Do not call the frontier a metric space absent a proven metric.

## Why this emerged from native evidence
- P2-A weak 'any capture exists after selected reported replies' failed to distinguish 42/43 and negative controls.
- P2-B entire legal opponent tree at H=2: all-reply immediately-capture-just-moved-piece universal 0/18, opponent-capture-conditioned immediate recapture 15/18; only selected control99 distinguishes rivals in binary PASS/FAIL. This does NOT establish a general relation to persistent P10 bestmove rank inversion.
- P2-D first-root-inclusive rook material ledger: case99 Rxc2 +5, ...Qxc2 -5 yields 0; rival Kg2 +0, ...Rxd2 -5, Qxd2 +5 yields 0 on these **specific local branches**. Same nominal material ≠ equal game states or strategy. This illustrates that proof obligations change with the intended claim.
- Theoretical inference, not observed fact: a human-facing explanation system should first choose a claim meaningful for the user's question, then request an adequate legal certificate. Blindly taking the smallest proof of an arbitrary q is not adequate.

## P3 research program
P3-A develop a compact hierarchy/lattice of claim semantics and proven implication/nonimplication edges: existence, option preservation, capture reply robustness, guaranteed material, forced mating/defense, nonrepeatable positional feature, mechanism-mediated preference. A proof of an implication needs matching conditioning sets, quantifier order and terminal meaning. Explicit counterexamples from cases31/42/43/47/99.
P3-B deliberately source **obvious** verified positions (forced recapture, mate-in-one, basic undefended capture, one legal reply) and **hard** near-equal positions from independent games, matched to the same claim vocabulary. Do not treat a constructed testboard as independent natural game data. Pre-register negative controls and heldout event/game splits.
P3-C implement exhaustive claim checker for small branching/horizon or a sound proof-carrying selective search for larger H. A short/attractive PV is not full universal proof. Unknown on resource exhaustion.
P3-D compose a *claim compiler* for an eventual LLM: user question -> explicit target Phi/Q/P/H -> independently verified certificate -> natural-language commentary with bounded claims -> factual audit (counterexample questions). The LLM is a **renderer and conditional claim proposer**, not the source of chess legality authority.
P3-E evaluate human comprehension on novel heldout counterfactual questions against score/PV-only and prose-only controls; measure transfer and calibration. No human effectiveness results presently.

## Scientific limits and adversarial controls
Do not collapse (i) invariant game-state feature, (ii) advantage, (iii) original Stockfish causal mechanism, (iv) transferable strategic explanation. A proof of a local tactical result is not a proof of why Stockfish selected that root. Case99 remains **negative search inversion control**, not a game-theoretic no-strategy control. P2-B WSL legally validated; P2-D uses simple piece material accounting on native move lists; no full search or human trial. 
Compute should be driven by specific falsifiable claim rather than generating large features or exhausting WSL resources. Preserve historic versions and failures, WhoSia author/committer, no new branches.
