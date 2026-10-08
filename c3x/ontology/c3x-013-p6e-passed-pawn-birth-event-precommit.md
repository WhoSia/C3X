# C3X 0.13 P6-E — Passed-Pawn Birth Events as Blocker-Set Transitions

State: exploratory after P6-T reports zero own-side passed activation among 210 quiet pawn pushes. Same P5 frozen 16 Lichess broadcast groups only; no source replacement or outcome-adaptive event selection.

Let B_c(s,p) be the set of *opponent* pawn squares strictly ahead of own pawn p in the same/adjacent files. The coded passed predicate is exactly 1[B_c(s,p) is empty]. A newly passed pawn is therefore a change B_before nonempty -> B_after empty for a persistent pawn identity, even when the source move was made by some other piece. Record the actual before/after blocker square lists and UCI move for every such birth in each fully legal frozen game.

Classify the board-level event reason without interpreting engine search:
- PAWN_ADVANCE_THRESHOLD: the newly passed pawn advanced over its last opponent pawn's rank;
- BLOCKER_CAPTURED: an opponent pawn was removed from the relevant forward band by capture (possible even if a knight or bishop made the move);
- OPPONENT_PAWN_MOVED_OUT_OF_BAND: a blocker advanced past the pawn's rank;
- MIXED / OTHER: more than one of these changes or uncategorized condition; must remain auditable, no forced label.
Maintain source game and ply, color, before/after pawn location, capture/en-passant/promotion type, original FEN hashes, and blocker sets. No opponent pawn status activation may be treated as an independent game.

Measure BOTH sides; report all games, every source HOLD and denominator. Group recurring events by their BroadcastName and unique GameURL; not independent provider ecologies.

This is a structural exact chess-rule mechanism for a **board fact** (when a pawn becomes passed), not a proved source of engine move preference, human strategy, or move-understanding benefit. 0.14 not opened by this observation.