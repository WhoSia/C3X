# C3X 0.29-P35/R5 — Research-Director Origin, Evidence and Prior-Art Reaudit

Date: 2026-11-05 KST. **SCIENTIFIC PRIORITY DECISION, NOT A NEW NATIVE-ENGINE PASS.** This review cross-references original Drive C3X 1.md / 23.md / 28.md, latest exact Notion 0.29-P23/P24/P25/P27/P28/P29/P30/P31/P32/P33/P34/P35, primary original Drive literature, and current GitHub R5 harness. It is a targeted, evidence-led read, not a claim to have exhaustively re-read every C3X archive or full book.

## 1. The founding question was more ambitious than our recent instrumentation

Original August 14 2026 C3X 1.md asked why ordinary people cannot learn much from silent Stockfish moves, and why one move is *slightly* better than a genuine alternative. The goal is **contrastive chess explanation that is legal, consequence-sensitive, faithful and useful for transfer**, not simply tracing every machine instruction. Near-equal candidate comparison is an intentionally difficult central experimental task; do not discard it merely because it produces more rank sensitivity. Broader margin strata can be essential external controls and failure analysis, **not an automatic replacement of the founding target**.

Original October 31 C3X 0.29 Origin Return divided:
- **Track A**: action-conditioned strategic consequences across legal opponent replies; concrete rival forecast, independent rule/outcome validation, depth and engine transport.
- **Track B**: factual commentary correctness, coverage/abstention and blind human understanding/decision transfer.
- TT/SEE/NNUE mechanism is valuable only insofar as it supports specific source-faithfulness claims; engineering PASS does not prove chess-specific explanatory usefulness.

**PI decision: RETURN-TO-ORIGIN + RUN-ONE-BOUNDED-SOURCE-FALSIFIER.** Keep narrow P35 source dispatch if it identifies whether a neural evaluator can physically enter search, but cap instrument-only work. After one actual native, nonperturbing dispatch plus root-competition test, prioritize one externally checkable action-conditioned rival explanation over another instrumentation expansion.

## 2. Previously adjudicated negatives cannot disappear

1. Early local-motif/primitive transport: in original C3X 1.md, prior latent factor PAG_DF_01 failed prospective replication (e.g., heldout cosine 0.358 vs threshold 0.70); CPP_224 failed independent Candidates 5/8 versus 75% prespecified floor, and multiplicity-controlled canonical primitive set remained empty. Retain as previous-version-specific negatives, not claims about future NNUE activations.
2. 0.17 classifier 42/64 versus simple B0 53/64, and historical 0.25 305-scalar heldout Brier 0.205557725 versus trivial 0.205555556. These are particular old tasks/cohorts; not direct score comparisons to P34.
3. 0.27 actual SEE/capture-prune intervention game14 had a local native causal restoration, **not** proven chess-semantic mediation, not general 0.28 transport. 0.28 original 64-position frozen cohort was HOLD (case20 castling/right trace and original-family completeness).
4. P25: identical opponent UCI strings need not correspond to the same counterfactual across two different post-root positions. P27/P28: a plan like next-turn Nf3 is legal under all 20 opponent replies after either e4 or d4; plan availability cannot separate the choices or establish value.
5. P29: finite plan value V_Q, opportunity cost and independent predictive information, not universal plan existence, are the burden. P33: previous apparent response-gap result on game14/d5d3 at depth10 was retracted at depth11; depth-specific claims are mandatory.
6. P32/P34: simple material+eval JSON and especially one-line PV are **strong rivals**. P34 no format uniformly dominated under nominal equal requested nodes; output cardinalities differed. 4 exposed candidate roots from just 2 original games, all selected adaptively. 2/4 static rank reversals subsequently tabulated are postselected contrasts, NOT frequency evidence for a general neural mechanism.

## 3. Primary source competitor recheck

Fetched original Research OS Drive PDFs:
- Press & Golubev 2026 BinProp: nearby-negative, actual engine-grounded concept discovery and cross-game explanatory evaluation; much of 'contrastive concept extraction' is already occupied.
- Hebbar et al. 2026 ACT-Eval: 325 position-move cases, 125 expert-gold, atomic chess claim audit, factual/coverage distinction. Strong Track-B factual correctness competitor.
- Bhaskar/Cheng/Chen 2026 QUEEN: 4B domain-adapted chess playing and explanatory LLM with distillation and downstream analysis. C3X must not claim novelty of machine-reasoning commentary or expert-competitive explanatory chess alone.
- Poupart 2024 contrastive sparse autoencoder chess planning analysis on Leela: multi-step trajectory contrast and latent planning concept analysis are prior art.
- Schut et al. 2025 PNAS: AlphaZero concept novelty/teachability and small expert study are prior art.

**Narrow potential novelty**: Stockfish16 source-indexed, legal full-history *neural evaluator → exact search dispatch → ancestor/root choice* with an independent, selectively useful *near-equal foil prediction*. Neither causal chain nor human benefit has yet passed.

All five original PDFs are already held in authenticated Drive. **Bounded checked missing count = 0**, not global coverage guarantee.

## 4. Critical newly discovered live code-design limitation

Reviewed exact current [P35 R5 harness](../harness/c3x_029_p35_r5_search_route_court.py). It launches `go searchmoves {root} nodes 24000` with **one and only one permitted root move**. Therefore agreement of `bestmove` across vanilla/probed binaries is **trivially forced by legal candidate restriction**; it is not evidence of naturally matching root-choice policy or mediation. Only score, PV, nodes and real Eval::evaluate dispatch across a forced-root subtree can be scrutinized, subject to instrumentation parity.

The pinned official SF16 `Eval::trace` resets thread optimism/bestValue; direct static traces are not search-context leaf scores. Even if `Eval::evaluate` chooses NNUE, a search-context optimism/blending/discounting difference remains unmeasured in P34 direct static traces.

**Repair** (single targeted execution): same two original game-root positions, compare untouched vs instrumented with `go searchmoves a b nodes 24000` for game10 `e8f7 e5f4` and game14 `c2c3 d5d3`, and additionally unrestricted full-legal-root search as a MANDATORY separate arm for claims about natural root choice (P9 already found a third candidate emerging beyond a two-root policy). Match exact full history, source/net/binary provenance, hash/threads/node budget; require bestmove, score, PV and node parity **in a competition with at least two allowed legal root moves**. Then report actual evaluator dispatch. This still does not prove leaf→root intervention; do not overclaim.

**Execution status verification:** GitHub commit and source inspection established that R4 cold replay and R5 native dispatch workflows are authored. The accessible GitHub combined-status query returned no statuses; live workflow completion and PASS were **not established** by these tools. Source code tests reported in prior stages are distinct from authenticated native stockfish results. Preserve HOLD.

## 5. Hypothesis and budget reset

- H1 (chess-facing): a foil-sensitive, legal, action-conditioned consequence forecast adds independent information beyond Stockfish score+PV and a simple foil-aware JSON at **matched compute and matched prediction capacity**. FAIL if neither heldout forecast accuracy nor selective coverage improves.
- H2 (mechanistic): SF16 neural evaluation difference physically enters some actually executed search evaluations and, in a predeclared case, causes a changed parent/root choice under a source-verified intervention. H2 independent of H1.
- H3 (human): factual, understandable, selective C3X explanation improves blinded transfer/prediction compared with simpler explanation. Requires independent human evaluation, not prose attractiveness.

No point in a claimed hidden chess concept unless its transfer, mechanism and relevance to H1/H3 withstand strong rival controls. **Stop the P35 instrumentation track** if the two-root competition gate repeatedly fails parity, cannot demonstrate a meaningful source-executed neural effect, or consumes further cycles without chess-level discrimination. One source-identity/dispatch verification cycle is authorized; additional mini-version proliferation is not.

## 6. Operating doctrine

Notion: scientific authority; Drive: original bytes; GitHub: code. Original adverse receipts and negative controls are never retroactively overwritten. GitHub Actions compute and upload read-only artifacts only; `github-actions[bot]` is permanently prohibited from commit/push/merge/tag/ref mutations. A green test, a Git commit, a math toy or a beautiful mechanism diagram is not an independently useful chess explanation.
