# C3X 0.26 P0-F — Legal Opportunities, Witnesses, and Abstention
Status: THEORETICAL CONTRACT + LOCAL VALIDATOR PREPARED, **NOT EXECUTED**. C3X 0.26's official name is unchanged.

## Research lineage
Original C3X asks why one chess move rather than a close rival; 0.2 affordance/LDF/persistence and external failures, 0.3 competing explanations, then 0.25 P10–P12 engine-search and chess-legal audit remain independent and historically preserved. A change in engine reporting is not a chess-theoretic cause.

## Restricted operational test
For legal root a at s, the opponent-to-move legal actions L_1(s,a) and original-side responses L_1(s,a,r) after a legal opponent reply r are observed. Compare counts of legal moves, legal checking moves, captures, pawn moves, promotions, and checks where the checking piece is not immediately legally capturable at its destination. These are **one-ply legal counts only**, not a strategic safety measure, a reason, or proof of superiority. Opponent to move after root; original mover to move after first reply. Depth17/19 root-state counts must agree as a validity invariant.

Observed development: P10 outcome-selected 42/Classical Bf8 vs Bc5 and 43/NNUE Re8 vs Qf5. Negative controls 47/NNUE (transient reversal), 99/Classical (locked tie). Source P11 SHA256 18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2, 144 rows/72 repeat pairs, no new Stockfish calls. Prior P0 FEN6 convergence within roots 8/72 (vs board+turn 13/72); history-sensitive repetition remains untested.

**Decision boundaries:** if controls show same feature patterns, report NO_DISCRIMINATING_REASON_IDENTIFIED. If development observations separate, report only DEVELOPMENT_SEPARATION, never validated strategy. Counts erase move identities and policy valuation, so both differences and nulls are insufficient to establish chess strategy. Future causal authority needs specific legal intervention witnesses discriminating rival search-path and chess-affordance accounts, source-disjoint testing and ultimately human transfer controls.

## Run
Local read-only P0-F script prepared and syntax checked. Because current assistant container lacks python-chess and network installation failed, **scientific execution remains pending WSL** with existing python-chess 1.11.2. Run on unchanged P11 JSONL, output only into local_input folder. Do not interpret unexecuted features as findings. No new branch, human WhoSia commit only, read-only CI/bot zero.
