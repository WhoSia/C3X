# C3X 0.25-P14-P9 — Source-Eligible Value Bounds & Bilateral Explanatory Warrants

**Formal title:** Source-Eligible Value Bounds & Bilateral Explanatory Warrants: Repetition-Typed TT Contracts, Counterexample-Validated Score Semantics, Query-Specific Search Refinement & Native Decision Certificates.

**2026-10-12 completed evidence:** [human WhoSia pre-experiment scientific registration `90e4d31f`](https://github.com/WhoSia/C3X/commit/90e4d31f42bdadc524c596bdeb68e7a7f570d450) → official pinned original Stockfish16 true native exhaustive legality/checkers test [#38219064407 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/38219064407) → distinct independently written packet verifier and deliberate tamper rejection [#38219379311 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/38219379311). R1 original native [#38218944628 FAIL](https://github.com/WhoSia/C3X/actions/runs/38218944628) was parser error when source `Checkers:` had no trailing space; corrected UCI parsing without changing registered FEN or game hypothesis. This stage obtained a **sound source-grounded immediate mate decision certificate** for one synthetically constructed developmental chess root. It did **NOT** prove true heuristic TT numeric bounds, safe TT optimization, full actual Stockfish K or measured Elo.

## 1. TT score eligibility requires typed semantics, not just writer provenance

P14-P8 verified actual same-run original `TTEntry::save` writer→qsearch early-return consumer matching full original key/raw value/bound/depth in eight observed events; P14-P7 gave two position-key contextual counterexamples. These physical observations justify statements about **which numeric TT record the original algorithm used**. They do not establish the legal-game utility value of that number. One has to distinguish:

- `PhysicalTTProvenance`: an original writer last overwrote an entry at a particular address, original lookup consumes same raw value; conditions/source-bound tag can be recorded.
- `ProceduralSearchBound`: a bound classification under specified Stockfish negamax, pruning/extension/null move, qsearch stand-pat, time/depth/window, 50-move/repetition and mate normalization source contracts. No claim that the value equals exact chess minimax.
- `VerifiedSemanticGamePredicate`: for example the terminal truth “after this legal move, the opponent is in check and has zero legal responses,” discharged by original actual legal-move generation and check detection. This is a **logical chess-rule proposition**, not a centipawn TT score.
- `VerifiedNumericalGameBound`: a source-sound quantitative bound of a separately defined node utility across all admissible future continuations/histories; **not yet available**.

Original `search.cpp` has a stand-pat `bestValue >= beta` branch that can store `BOUND_LOWER` **without enumerating moves**; original regular search also has ProbCut, null-move and reductions. Thus TT LOWER/UPPER are valuable *operational search contracts* but cannot be automatically promoted to universal finite-horizon or game-theoretic utility. The P14-P8 source writer/reader 8/8 matching makes a stronger physical explanation, **not** a game-value oracle. An accurately typed proof gate must refuse that conversion until a source-valid writer semantic rule with history/TT generation/window is independently established.

## 2. First real original Stockfish16 source-based bilateral root decision certificate

The precommitted **synthetic development** position: `7k/8/5KQ1/8/8/8/8/8 w - - 0 1`. Source git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads1, Hash16 MB, NNUE off, full fresh cold UCI sessions twice.

[Native certificate producer](https://github.com/WhoSia/C3X/blob/main/tools/c3x_025_P14_P9_original_native_mate1_bilateral.py) executes **unmodified official engine original `MoveList<LEGAL>`** via `go perft 1` to obtain ALL root legal moves and their legal successor reply counts. After *every* legal root move, the engine constructs the original actual successor position, reports original `Position::checkers()` via `d`, and `go perft 1` enumerates all immediately legal opponent responses. Define for original legal root move m:

`ImmediateMate(m) ↔ opponent_in_check(child(m)) ∧ |LegalOppReplies(child(m))|=0.`

This is a source-verified exact **terminal chess-rule predicate** at a fixed, explicitly stated one-ply query, not a probabilistic model, minimax cp prediction or TT-derived heuristic bound.

**Actual result:** root legal moves **23**, of which a **single original source-proven mate-in-one `g6g7` (Qg7#)**. The other **22** legal root moves are individually rejected as *immediate checkmate* via legal opponent continuation witness (when available) or verified stalemate-not-checkmate. Full universe checked. The actual original depth4 bestmove was also `g6g7` and belongs to the source-certified mate set. **No claim that all other 22 moves are strategically bad or losing**, only that none is immediate checkmate. The mate is a concrete winning terminal outcome in standard chess under the original legal rules and chosen FEN, not a general proof that TT search values at depth4 are semantically valid. R1 UCI empty checkers formatting bug left as technical failure; after correction the original FEN/preregistration remained identical, native #38219064407 PASS.

### The two legitimate directions of justification

Let `A_{<1}` denote the **complete original source-generated legal root moves** in this one fixed position and `P(m)` the immediate mate predicate. An observed source witness gives `∃m∈A_{<1}:P(m)`, namely `g6g7`. Complete enumeration of every `m∈A_{<1}`, checking all legal opponent replies and actual check state, gives `∀m≠g6g7:¬P(m)`. These are **positive/negative directions over the identical source-complete finite domain**; unlike unconstrained general-engine K, in this local query the original legal move set and terminal predicate are actually exhausted.

The usable Explanation Certificate has `source=original MoveList<LEGAL>`, complete root coverage, `g6g7` terminal witness, and 22 explicit negative statuses, plus a separate factual note that original engine chose the same move. The declared certificate **does not imply globally optimal practical engine search, all possible TT writes, or an exact numeric root-score ordering**. It answers a real and narrow chess question *correctly*.

## 3. Independent verifier, falsification and completeness

[Independent source packet court](https://github.com/WhoSia/C3X/blob/main/tools/c3x_025_P14_P9_independent_native_bilateral_verifier.mjs) re-reads actual native artifact instead of re-running or modifying engine, checks exact pinned source/FEN, **every one of 23 complete legal root labels**, every terminal `checkers + zero replies` classification, nonmate counterwitness type, uniqueness of `g6g7`, original selected UCI and precise limits. Six deliberate source packet tamper cases **all rejected**: falsely demote verified mate, forge a nonmate as mate, delete a candidate, erase an alternative's counterwitness, authorize a raw TT tag as semantic proof, and substitute an illegal original bestmove. This is an **independent proof-packet logic verifier** on data produced by original native legality, not an independent second chess move generator. [#38219379311 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/38219379311). Native derived ZIP about **1.4KB**, second proof ZIP about **1.2KB**; no full PGN or engine binary.

## 4. Formal expressive theory: qualified K, rather than “safe exclusion” alone

We now have a genuine original-chess example of **typed query-limited source completeness**:

- `K_mate1` is the finite collection of actually legal root moves and their original source-valid terminal response sets for THIS root, not all hidden Stockfish TT/search-machine states.
- A *positive* witness `g6g7` establishes an existential achievable outcome.
- *Negative* witnesses on the other 22, backed by exhaustive legal-response search, establish universal denial of the specific property `mate-in-one` over the alternative moves.
- The actual original engine decision `g6g7` and its reason as evidenced by a terminal proof can be stated separately; **causal claims about which internal TT return made it choose g6g7 remain unproved**.
- Additional research beyond exclusion: witness construction, candidate possibility ranking, source-faithful narrative, value-of-information for which rival to inspect next, and compute resources; none requires pretending that a TT cp estimate is exact.

This supports the theoretical architecture `K^-⊆K⊆K^+`, with witness underapproximations for *possibility* and source-sound complete overapproximations for *necessity/impossibility*. At this specific finite mate-in-one query, legal enumeration provides a source-complete answer. At the full root-value and hidden-history question, it does **not**: a source-generated finite mate1 certificate cannot be substituted as a TT utility bound. This is a sound piece of Explainable Stockfish, though terminal mate detection itself is classical chess rather than a new chess theorem.

## 5. 0.26 maturity re-evaluation after an actual positive working explanation producer

| Research gate | P14-P9 evidence | Status |
|---|---|---|
| Mathematical/TCS correctness | sound existential and exhaustive negative terminal cert on original legal candidate domain | **PASS on narrow terminal query only** |
| Real native correctness | original unmodified SF16, two cold complete source-legality enumerations, independent typed packet court | **PASS** |
| Non-vacuous invention | actual machine-readable source-grounded `why / why not` generator that certifies real selected root and exhaustively rejects other mate1 hypotheses | **PASS for explanatory artifact, narrow domain** |
| Nontrivial general source→TT value bound | actual TT writer's numeric bound lifted through history/stand-pat/pruning/alpha-beta to a genuinely comparable target quantity | **HOLD** |
| Safe search controller/cost tradeoff | implement proof-constrained source decision to save compute while preserving designated semantics on admissible states, control false certificates and overhead | **HOLD** |
| Chess strength | real paired clock/color-swapped independent match with uncertainty and ΔElo | **UNTESTED**, 0 games |

**Maturity judgement:** This is the FIRST **narrow** nonvacuous proof-carrying original Stockfish explanation and a legitimate sign that C3X's original three axes can meet. It would be misleading to immediately announce full `C3X 0.26 — Proof-Carrying Search-State Abstraction & Explainable Engine Control` because the *search-control* and *TT source-typed numeric bound* advertised by that name are unproved. **P14-P10 is the earliest CONDITIONAL graduation review**, only after a source-typed *nonterminal or composable bound* with independently validated state-history assumptions and a genuinely usable new controller or information-directed search mechanism, with negative cost/safety results kept. The research release 0.26 need not already have positive Elo, but an advertised stronger 0.26 chess **engine** does require genuine strength trials.

Recommended P14-P10 title: **`C3X 0.25-P14-P10 — History-Qualified TT Value Contracts & Search-Action Warrant Synthesis: Source-Level Bound Legitimacy, Constructive Rival Counterexamples, Proof-Carrying Re-search Control & the C3X 0.26 Graduation Court`**.

**Historical controls:** P14-P7 original same-key 94/100 two-actions, P14-P8 same exact FEN/key/rule50 but different repetition/draw/nodes; P14-P8 8/8 observed TT physical matches; all M3/M4/M5 negative results and M6 selective 19/19 versus M0 63/64 remain unchanged. Human WhoSia author and committer, read-only GitHub Actions, original SF16 GPLv3; the only synthetic FEN here is explicitly development, not held-out prediction or verified Elo improvement.
