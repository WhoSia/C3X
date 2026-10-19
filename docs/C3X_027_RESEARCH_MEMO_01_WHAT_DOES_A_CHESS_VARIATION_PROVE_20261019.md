# What Does a Chess Variation Prove? Quantifier Scope, Forced Outcomes, and Compact Evidence

*Research Memo 01 — C3X 0.27 · 2026-10-19 · bounded manuscript draft*

## Abstract
A chess variation establishes that one sequence of legal moves is possible. It does not, by itself, establish that the same result survives every legal reply. This distinction matters when an engine variation is turned into an explanation. We formulate outcome claims with an explicit horizon, opponent-response set, and quantifier order, then study two elementary certificate types: an existential witness and a universal-response proof. In a previously selected cohort of nine game positions (18 first-move states), a native chess-legal audit found that all 18 states refuted a strong claim requiring the opponent's most recently moved piece to be immediately capturable after every legal reply. Restricting the claim to opponent capture moves yielded 15 true and three false states. The only binary contrast between first moves occurred in a prior negative control, not in the selected development examples. We also construct a king-and-rook ending in which a specified move cannot force checkmate within one or two plies but can force it within three. A separate GitHub Actions run using python-chess reproduces this result under full legal move generation. The findings demonstrate a concrete separation between variation witnesses, claims quantified over replies, and finite-horizon forced outcomes. They do not establish which move is strategically superior, why an engine preferred it, or whether readers learn more from the certificates.

## 1. A line of play is not a strategy
A chess engine presents a principal variation as a sequence of alternating decisions. It is tempting to read such a sequence as if it explained why a move works. Yet a single sequence can omit a legal defensive move that changes the conclusion. To claim that a player can force a result, one must account for the opponent's freedom to choose a different reply.

We therefore treat an explanation as a question about a specified outcome, rather than as an interpretation of a displayed line. The question fixes an initial game state, a first move, a set of admissible opponent replies, a horizon, a result predicate, and the order in which players choose. The resulting claim might be existential ('there is a continuation') or adversarial ('for every reply, a response exists'). These statements have different proof requirements even when they refer to the same board.

## 2. Claims and finite evidence
Fix a finite legal game tree from a history-complete state h, a horizon H, and a target predicate q. Let E_H(q) say that some legal continuation reaches q within H plies. Let G_H(q) say that the claiming side can choose moves so that q is reached within H despite all eligible opponent choices. Provided that the legal tree is nonempty and the reachability semantics are identical, G_H(q) implies E_H(q). The reverse fails whenever an opponent has a reply preventing q. Reachability within H is monotone with H under fixed rules and terminal conventions; a statement about q being true at exactly ply H need not share that property.

A positive existential claim needs one verified line. A negative universal claim may be refuted by one eligible opponent move, followed by proof that no available response meets the stated target. A positive universal claim requires complete opponent-branch coverage, even if the final document displays only one response to each branch. Compressing a proof can reduce what is transmitted without reducing the work needed to establish that no branch was omitted.

## 3. Chess-legal recapture experiment
We reused a frozen set of nine chess game positions and two candidate first moves at each position. Their evaluator and depth repetitions are not independent chess states; the chess-legal denominator is 18. For each root move, the native P2-B verifier enumerated all legal opponent replies and checked whether the original player had an immediate legal move capturing the piece that had just moved.

The strongest property, quantified over all opponent replies, failed in all 18 states. Many legal quiet moves cannot be immediately captured. When the opponent-reply set was restricted to moves that themselves captured a piece, 15 states satisfied the corresponding universal recapture condition and three did not. No conditioning set was empty. Among nine first-move pairs, only position 99 distinguished the roots by this binary property. Position 99 belonged to the prior negative control for persistent search-ranking reversals. The originally salient development cases 42 and 43 did not separate.

One further accounting check prevents an attractive but unsupported inference. In position 99, one first move captures a rook and is then met by a queen capture; the alternative first move is followed by a rook capture and an immediate queen recapture. Along these specified lines, both yield zero net nominal rook material. The local availability of an immediate recapture therefore cannot by itself justify saying which initial move is better.

## 4. A checkmate claim with a first provable horizon
We constructed a king-and-rook ending: White has a king on b1 and rook on c4; Black has a king on a3; White moves first. The fixed first move Kc2 does not force checkmate within one or two plies. Black has one legal response, Ka2, after which Ra4 gives checkmate on White's second move. The first successful horizon for the fixed claim is therefore H=3 plies.

A restricted king-and-rook generator first checked the claim. We then ran a separate GitHub Actions workflow that installs python-chess and verifies legal chess moves independently. The workflow completed successfully. Its horizon-one, horizon-two, and horizon-three results for Kc2 were false, false, and true. The implementation visited 1, 2, and 13 edges respectively, and serialized the selected proof trees in 22, 48, and 67 bytes. These are measurements of one verifier and encoding, not lower bounds on the cost of proving the claim.

The same workflow checked the original 18 candidate moves under the full move generator. For the target of forced checkmate within three plies, the selected development moves in positions 42 and 43 all returned false. The former study cohort remains preselected; this new execution provides independent rule-engine verification, not an independent game sample.

## 5. What can now be explained?
A verified chess continuation can certify a concrete possibility. A response-complete proof can certify a bounded forced result. The two should not be conflated. They can also be very small in different ways: a single legal escape refutes a mate-in-one claim, while confirming mate-in-one requires showing that no legal escape exists. An explanation system may select a compact witness for a reader, but the omitted legality and branch-coverage obligations must remain verifiable.

The present evidence does not link these claims to Stockfish's internal decision mechanism, estimate strategic long-run value, or measure learning improvement. The next experiment should preregister the claim language on new games disjoint from the nine selected positions, include both conspicuous tactics and close first-move alternatives, and measure verifier expansion costs separately from complete certificate size. The scientific objective is not to make a variation sound convincing; it is to determine precisely which outcome the variation proves.

## Provenance and boundaries
Native P2-B user WSL run: P2B_PASS 144 72 18 36, raw uploaded JSON SHA256 e990188ad9da4f2035d70d9010448157f8a41fe14830904245e68164d2ae8f0c. GitHub Actions full-rule replay https://github.com/WhoSia/C3X/actions/runs/39207862972, completed success, output artifact ID 12165834677, 20 first-move cases and 60 horizon judgments. Input histories beyond FEN not supplied, so repetition-dependent adjudications are not addressed. No learner study was run.

## Internal referee attack and revision receipt
R1: 'The universal immediate capture property is trivial to refute through quiet moves; its rejection is not a deep chess principle.' ACCEPTED. The manuscript uses it as a diagnostic of quantifier scope, not as strategic discovery.
R2: 'These examples and 18 states are selected; the paper cannot claim generalization.' ACCEPTED. Source cohort is described as preselected, constructed KRK separately labeled, no independent heldout sample claimed.
R3: 'A 67-byte printout is not a minimal proof.' ACCEPTED. Manuscript says implementation-specific serialization, not an optimum.
R4: 'Why Stockfish chose a move was not studied.' ACCEPTED. Source mechanism and human utility expressly excluded.
Verdict: DRAFT-CLOSED as bounded Research Memo; paper submission and broad novelty claims HOLD pending independent data and prior-art audit.
