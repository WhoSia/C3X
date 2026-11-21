# C3X 0.31/P1-L — Causal-Abstraction Prior Art, Vacuity Falsifier, and the Search-State Boundary

**2026-11-21, source status:** original owned Research OS primary PDFs checked by authenticated Drive read, including first-page abstract and chapter schema. Historical original research follows earlier C3X 0.29/0.30 mechanisms, which are not retroactively renamed. This is a literature-and-methodology audit, NOT a new native Stockfish study or proof of originality.

## Verified owned original PDFs, not missing sources

| Original bibliographic identification | User-owned original primary PDF | Verified method/relevance |
| --- | --- | --- |
| **Geiger, Ibeling, Zur et al. (2025)**, *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*, JMLR 26(83), 1–64 | [Original Google Drive PDF](https://drive.google.com/file/d/1i_i_cFFv6vqYHaBOgKK9AbuprPtj8v91/view) | §2.2 intervention algebras; §2.3 exact transformations with interventionals; §2.4 approximate transformations; §2.5 interchange interventions; §3.2 graded faithfulness. Official [JMLR entry](https://www.jmlr.org/papers/v26/23-0058.html). User Drive also has a filename-marked **duplicate** of the same bibliographic source, not a new distinct paper. |
| **Sutter, Minder, Hofmann & Pimentel (2025)**, *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* | [Original Google Drive PDF](https://drive.google.com/file/d/1e4SKpJ4yaYETPCadT-NxOwAat-XuF-Yw/view) | Shows that overly expressive mappings can yield uninformative or vacuous causal abstractions and even perfect interchange accuracy on untrained models. A 'perfect alignment' score alone is not explanatory validity. |
| **Lorenz & Tull (2026)**, *Causal and Compositional Abstraction*, arXiv:2602.16612v1 | [Original Google Drive PDF](https://drive.google.com/file/d/1oyyHY8seKsjrgtdNLqXykVUYilNmflm_/view) | Unifies Q–τ consistency, interchange and constructive abstractions through natural transformations and distinguishes component-level and query-level mappings. In particular, a lower-level event-label predictor is not equivalent to a mediator-preserving mechanism abstraction. |

**Custody:** The source originals were already in Drive; do not add them to missing-literature inventories or duplicate originals in GitHub. Avoid claiming every proof/theorem in the 64-page Geiger paper has been rederived: this is a targeted reading of the original opening, contents, central claims and relevant sections, not a proof-by-proof replication.

## What prior art changes about C3X 0.31

The high-level expression “intervention-stable state abstraction” is **not a new theoretical invention by C3X**. Geiger et al. (2025) already frame low-to-high mechanism transformations and approximate interventional agreement; Lorenz & Tull (2026) provide a still broader compositional approach. A generic formula or philosophical claim that abstracted mechanisms should commute under interventions has substantial direct prior art. We may reuse that framework with attribution; it is **not** a novelty claim.

Sutter et al. (2025) supply a more severe *falsification pressure*: a richly expressive readout may encode the final engine answer, and an arbitrarily complex decoder can make almost any state look causally faithful on the observed cohort. If P1's public-plus-event fields fail to meet even the retrospective source-sensitivity threshold, simply adding all TT cells and full trace bytes is not progress unless it improves **game-disjoint, intervention-heldout** fidelity relative to its description length and calibrated abstention.

A search engine is not a feed-forward neural network. The primary C3X opportunity is to instantiate such abstract interventions on **real legal chess histories, budget-limited stateful alpha-beta search, dynamically mutated TT/history and root choice**, and to test **physical** source-state restores with correctness constraints. A telemetry-only classifier, source-contact checker, or generic FEN-only referee is insufficient for that claim.

## New comparison contract (testable; not yet fulfilled)

For fixed full game history and engine state context `c`, let:
- `T_L(sigma,i)` be a **physically executed** source-search continuation under an admissible low-level intervention `i`, including actual root move, bound-labeled score, and cost;
- `alpha(sigma)` be a **low-dimensional, interpretable** candidate abstraction of the original pre-intervention state;
- `T_H(alpha(sigma), omega(i))` the abstraction's predeclared high-level response, with `omega` a specified mapping of physical interventions, not a label fit after seeing the engine result.

Then an operational commuting discrepancy can be **defined for this project** as

`D_c(i) = d( alpha_obs[T_L(sigma,i)], T_H(alpha(sigma),omega(i)) )`

where `alpha_obs` extracts the *declared comparable output* (e.g. root first-move contrast), not arbitrary post hoc trace features. This is an *adaptation* of established interventional abstraction theory, not a new mathematical theorem.

A **nonvacuous** scientific victory requires:
1. `alpha` and `omega` frozen before encountering intervention labels on a new game/event family;
2. legal checkpoint reachability and physically contacted intervention receipts, plus sham, restore and impossible-target controls;
3. source-state-description cost/coverage tracked, including explicit abstention on undefined/uncertain bound comparisons;
4. measurable held-out accuracy improvement beyond `public-only` and `full-event-feature logistic` P1 baselines at comparable input/cost;
5. at least one *source-level necessity/sufficiency test of a specified mediator* rather than predicting from correlated pre-event features;
6. separate, independent chess-future and human study gates, neither assumed from 1–5.

The proposed “minimal” state cannot be a mathematical minimum unless the candidate representation class, code/bit budget, intervention set and output metric have been pre-specified. For initial P2, measure **sparse feature count, information footprint, calibration, coverage and prospective predictive contrast**, and explicitly avoid optimality/minimality claims.

## P1 negative result as a design filter

R33 64 games/128 source events yielded 11 final choice flips. P1's full original-data verification and 16-event-family-heldout retrospective model comparison:
- M0 prevalence: Brier 0.0798229.
- M1 untreated public depth/score-bound/PV: Brier 0.0808690.
- M2 M1 + seven pre-event physical parameters: Brier 0.0775887.
- M1→M2 gain +0.0032803 with 95% game-family clustered interval crossing zero and the predeclared +0.01 gate failing; threshold 0.5 recall **0/11**.

Thus neither pre-event feature correlation nor any theoretical causal-abstraction literature licenses C3X to promote `phi=M2` as a causally sufficient state. The P1 HOLD is **an empirically identified failure of a simple candidate representation under the chosen criterion**, not a disproof that any useful abstraction exists.

## Research decision

**0.31/P2** should primarily falsify the *portability* of the fixed M0/M1/M2 baselines on genuinely unseen original game families **without tuning them after inspecting outcomes**. **0.31/P3** should then physically test whether a candidate compact TT/history/budget state mediates matched root contrasts. For every proposed abstraction, compare fidelity vs complexity; require a held-out failure to be expressible as a concrete counterexample, not hidden by fitting an unrestricted decoder.

**No claimed new mathematics or superiority to Geiger/Sutter/Lorenz.** The possible novel contribution lies in a **verified source-native chess search implementation, a stateful causal-sufficiency falsifier, a full-history conditional adversarial reply validator and a separate learning contrast**, if experimentally successful.
