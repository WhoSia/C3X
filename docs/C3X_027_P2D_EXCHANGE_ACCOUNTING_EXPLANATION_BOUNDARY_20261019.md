# C3X 0.27 P2-D — Immediate Exchange Accounting and Explanation-Validity Boundary

Date: 2026-10-19. Source: user-uploaded real native P2-B JSON SHA256 `e990188ad9da4f2035d70d9010448157f8a41fe14830904245e68164d2ae8f0c`, 765,871 bytes; source P11 SHA256 `18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2`. Independent standard-library, chess-board/FEN **material** ledger, reusing previously native-validated legal recapture lists; no new Stockfish and no independent python-chess replay in this assistant runtime.

## Experimental question
Does a conditional legal *immediate recapture* distinction imply material advantage when the first root move's own capture is included? The P2-B 99 control supplies a decisive falsifying example for a naive conversion: yes, legal recapture capability differs, but the two recorded immediate exchange paths both have net zero nominal piece points.

For each of 18 unique post-root chess states, parse original starting FEN pieces, advance the first root, restrict the opponent to reported P2-B **full legal opponent capture** replies, and account for original captured piece; advance opponent capture; advance each P2-B legal immediate recapture; compute material tokens for the original root-moving side (pawn1 knight3 bishop3 rook5 queen9). The new P2-D derived JSON at `C3X_027_P2D_EXCHANGE_LEDGER.json` SHA256 `6148972195a2a988439f03f005f3ae4dacbe12f60b5935937a7ca99e5358810f` contains all 18 unique states and complete opponent-capture witnesses. Terminal chess evaluation, downstream black followups, positional scoring, checkmates, ties, repetition history, rook-pair equivalence and legal new continuations beyond the stored witness are all OUT OF SCOPE. En passant and castling are excluded from simple material parse; P2-B source knows legal capture flags.

## Actual results, case 99
Original FEN `2r3k1/1p3p2/2q1b1p1/3p3p/1R1Q3P/1P2PBP1/2rR1P1K/8 w - - 0 28`.
- First legal white rook move `d2c2` **captures black rook c2**: immediate material +5. Black queen `c6c2` captures white rook on c2: -5. No direct white capture of black queen c2 in next move. Net simple material 0 through these steps.
- Rival white king move `h2g2` captures nothing (0). Black rook `c2d2` captures White rook on d2: -5. White queen `d4d2` immediately captures Black rook on d2: +5. Net simple material 0 through these steps.
- This is not equivalence of resulting positions, or equal strength of the two roots, or best play by Black; comparing a chosen local line each is a bounded teaching example only.
- P2-B q_recapture conditional on opponent capture: first root d2c2 REFUTED, second h2g2 PASS. Therefore (q_{recapture}) distinguishes rival actions yet does not discriminate simple material result on these selected branches. Overinterpreting an isolated q as causal advantage would be an unfaithful explanation.

## Additional native-supported structural cases
Index31 roots a4f4 and a4h4 both have 6 opponent capture replies including `a6b5` and `c3b5` where the captured White rook cannot be immediately recaptured; both remain REFUTED.
Index42 d6c5/d6f8: 1 opponent capture each, all immediately recapturable; both PASS.
Index43 a8e8/d5f5: 3 opponent captures each, all immediately recapturable; both PASS.
Index47 negative c7e5/f6e5 both first capture White rook and both have 2 opponent capture replies all immediately recapturable, both PASS.
Hence current (q) does not distinguish P10 persistent-inversion development 42/43; the sole conditional distinction 99 lies in search-inversion negative control. Avoid promoting cherry-picked q.

## C3X principle: two floors of explanations
1. **Legal affordance floor:** is move t legal and targets the recently moved enemy piece? P2-B finite all-legal response certificates.
2. **Consequence floor:** what changes after first move, opponent capture, and own reply? P2-D nominal material ledger is only a first, intentionally weak consequence projection.
Further strategic floor must test outstanding threats, continuations, defensive forcing and adversarial choices; engine mechanism floor remains source intervention; human benefit must be tested on new unseen games.

A future minimal explanatory certificate cannot drop the captured material on the FIRST ROOT; otherwise it can give a false explanation even if all post-root recapture branches are legally enumerated. A material-neutral line may still have strong positional consequences. A 'proof' of material equivalence across all opponent options requires quantifiers over those options, not a pair of chosen lines. Current P2-D demonstrates a counterexample to a careless explanation transformation but **not a mathematical nonexistence theorem for strategic reasons**.

## Human-facing prototype (not learner-validated)
'Rxc2 captures a rook immediately; Black's queen can then capture that rook. Kg2 captures nothing, but after Black's rook takes on d2, White's queen can capture it. Under these *specific* local sequences, both exchanges break even in rook points. That does not show the moves are equally good: the remaining threats differ.'
Challenge learner on a **different** board which move already collects material at its first ply, not only which reply is a recapture. Compare baseline evaluation+PV vs certificate-grounded statement and what-if tests on game-disjoint heldout data.

No new engine run and no learner participants; H* and long-horizon property remain HOLD. Exact 0.27 official name remains unchanged; historical C3X 0.25/0.26 preserved. Drive raw upload is still pending and cannot be claimed.
