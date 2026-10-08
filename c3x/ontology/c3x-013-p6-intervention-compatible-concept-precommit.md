# C3X 0.13 P6 — Intervention-Compatible Chess Concepts, Pawn-Structure Edit Grammar, Root-Pair Positivity, Matched Sham Controls & Factorial Engine–Budget–Continuation Falsification

**Status: PRECOMMIT OPEN / NO P6 ENGINE OUTCOME OR SCIENTIFIC PASS.**

## Why P5 forces a methodological change
P5 legal chess board facts passed, but the naive directional center occupancy reason failed in 2 of 3 testable development cases; isolated-pawn and passed-pawn predictions had one testable example each. No predicate cleared preregistered support gates. Old P15 board-edit grammar moves only non-king non-pawn pieces. Under that admissible grammar a pawn-based concept such as isolated or passed pawn count CANNOT generally be switched: claiming causal sufficiency from such an edit would violate the intervention's support conditions.

## Invariance lemma before experiment
Let PawnPositions(s) encode the color and square of every pawn. The isolated-pawn count and passed-pawn count from the current chess-concept code are functions only of PawnPositions(s). Therefore any old P15 one-non-pawn-piece edit fixing all pawns necessarily preserves **both** predicates, regardless of any engine score change. Furthermore, isolated-pawn counts depend on the set of occupied pawn files, so a noncapturing forward pawn move on its existing file also cannot toggle isolation. A capture may change pawn file but also changes material. Hence P6 must not pretend an ordinary one-piece or same-file pawn push can identify the isolated-pawn mediator. A material-preserving pawn trans-file relocation defines an **artificial FEN edit**, not a reachable one-move causal history; report that distinction without exception.

## New question
Does there exist a **chess-rule-valid and pair-preserving intervention family** that changes exactly the predeclared concept predicate C while keeping A/B legally comparable, and does that change have a reproducible contrast relative to a genuinely non-toggling matched sham across source groups, opponent continuations and engine/search regimes?

## Preregistered admissibility strata
1. PIECE stratum: P15-style one non-king/non-pawn relocation (reachable under occupancy-aware piece geometry); suited to central occupancy/coverage predicates, not to pawn isolation or passed status.
2. PAWN stratum: one pawn re-placement producing a position-valid board with unchanged material, kings, side-to-move, legal A and B, both root continuations legal and unchanged test perspective. This is an artificial chess-state intervention, NOT automatically a legal historical sequence. En-passant and FEN castling fields must be revalidated.
3. Every TARGET must actually toggle its frozen chess-rule predicate. Every SHAM must preserve the predicate, use same mover piece class, original color, and controlled relocation radius, and report attack-set, legal-move, pawn-file, king-safety and material collateral changes.
4. If a viable sham cannot be matched without collateral imbalance, do not identify the concept mediator: HOLD_NONIDENTIFIABLE.
5. Enforce prior all-world marginality/support using a separately frozen qualifying and measurement regime; do not borrow P5's 80k cold score to certify a new completed-depth12 edited world.
6. Freeze at least two alternative legal replies per root, including a search-plausible opponent reply and matched benign control, before source pair outcome. Replies after A and after B live in DIFFERENT successor positions; never assume identical UCI legality.
7. Two distinct engines, each with version, binary SHA, threads/hash, native score perspective, independent restarts and 8/12/16 completed-depth panels; compare preference orientation, not raw cross-engine cp differences.

## Falsifiers and hard stops
- No legal predicate-toggling matched target/sham pair, loss of root-pair support, mate/cp mixed scales, score-depth or repeat mismatch, opponent reply rescue, mismatched historical games, feature-label transfer between unrelated engines, or any semantic renderer treating descriptive P5 facts as proven cause.
- Unit of independent evidence is the source competition/event and unique game identity, NOT merely distinct Lichess broadcast pages. Never let multiple rounds of one Polish league count as independent ecologies.
- No post-outcome candidate replacement, optimizer-specific concept rescue or human-utility imputation.
- Never admit explanatory certificates to Explain I9 before an independently reviewed proof of specific engine- and context-bounded causal scope.

**Parent verdicts remain:** 0.12 scoped HOLD, 0.13 P5 predictive-support HOLD, P16 local-only, P23 FAIL, P24/P25 HOLD, I8 human utility HOLD. P6 currently provides a corrected experiment constitution, not results.