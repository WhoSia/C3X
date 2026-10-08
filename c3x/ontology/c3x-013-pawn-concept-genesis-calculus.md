# C3X 0.13 — Pawn-Concept Genesis Calculus (P6 Mathematics)

Status: deductive account of the *existing coded chess predicates* plus actual-development witnesses; no new causal engine explanation.

## 1. Exact finite geometry
Use file f=0..7 and rank r=0..7. Let n_{c,f}(s) be number of pawns of color c on file f; out-of-range n=0. The implemented pawn-isolation count is
I_c(s) = sum_f n_{c,f}(s) * 1[n_{c,f-1}=0 and n_{c,f+1}=0].
An isolated FILE is not an isolated PAWN: if two same-color pawns are doubled on an isolated file, I counts two.

For a pawn p=(f,r) of color c, set direction d_c=+1 for White and -1 for Black, and define its forward blocker set
B_c(s,p) = { q in enemy pawns : |file(q)-f| <= 1 and d_c*(rank(q)-r) > 0 }.
The coded predicate is Passed_c(s,p)=1[B_c(s,p) is empty].
For white, define threshold T_white(f)=max rank among enemy pawns in f-1,f,f+1 (or -infinity if none). Then passed iff r>=T_white.
For black, T_black(f)=min rank among enemy pawns in those files (or +infinity if none). Then passed iff r<=T_black.

## 2. Exact conditional invariance theorem
Under a legal non-capturing, non-promoting PAWN PUSH of color c by k ranks (k=1 or 2), all same-color pawn FILE counts are fixed. Hence Delta I_c=0. With enemy pawn squares fixed, the moved pawn's B_c cannot acquire a NEW blocker, and every unmoved own pawn retains its B_c. Thus 0<=Delta P_c<=1. Opponent pawns can only LOSE (not gain) the moved pawn as a forward blocker, so Delta P_opponent>=0. Both colors can gain a passed pawn from one single move. This is a theorem about coded static predicates, not a theorem that the move is strategically good.

Promotion is excluded: a7a8q deletes the pawn and can reduce both I and P. Pawn captures/en-passant and nonpawn moves capturing a pawn are also outside the theorem. A nonpawn edit fixing ALL pawn squares preserves both counts; a legal nonpawn move that captures an opposing pawn does not satisfy that premise.

## 3. Pawn-concept birth events
For any persistent pawn identity mapped from pre-state to post-state, a new passed-pawn BIRTH occurs exactly when B_before is nonempty and B_after is empty. This has finite, auditable witnesses:
- CAPTURED_BLOCKER: an enemy pawn in B_before was removed by the move;
- PAWN_CROSSED_THRESHOLD: the pawn moves across the final blocker rank;
- OPPONENT_BLOCKER_MOVED_OUT: the blocker pawn moved past the forward boundary;
- MIXED: several mechanisms coexist in one chess move.
This certificate proves a BOARD FACT genesis only. It neither identifies a cause of the engine's root preference nor establishes a human-level chess concept's explanatory usefulness.

## 4. Why a scalar pawn count is not causally sufficient
Let F(s) be the vector of all measured chess predicates and let legal root moves a,b induce D=F(s_after_a)-F(s_after_b). Any engine score gap y=V_e(s,a;budget)-V_e(s,b;budget) observed with D_C !=0 and nuisance D_N !=0 is underdetermined by an additive surrogate y=beta_C*D_C + beta_N^T*D_N. Repeating the SAME D with deeper searches gives precision about engine y(depth), not independent chess-feature interventions or a full-rank design.

Actual P6 synthetic legal pawn tests demonstrated:
- PASSED_BOUNDARY: own passed +1, ALSO opponent passed +1 and own center control -1; Stockfish root gap -345/-538/-595cp at depth 8/12/16.
- ISOLATION_CAPTURE: own isolated +2, PLUS center and opponent passed/status changes; root gap +70/+140/+124cp. Both 2/2 exact repeated in each depth regime.
All legal example scores are **CONFOUNDED_CONCEPT_HOLD**, not evidence that passing is bad or isolation is good.

## 5. Real game source lock and selection warning
The same outcome-frozen 16 Lichess broadcast groups provide 15 fully parsable games; 1 960 game remains HOLD. A P6-T post-P5 developmental audit of 210 noncapturing, nonpromoting pawn pushes found 0 own-side passed births, 1 opponent-side birth and zero invariant violations. At ply32 only 1/14 surviving games contains any passed pawn, whereas at ply80 all 5/5 longer surviving games do. The latter is conditional on game duration, NOT an independent late-game prevalence estimate.

P6-E now audits births by blocker sets rather than counting snapshots; the real-game birth count must be interpreted by independent event/game group (multiple births in one game are repeated events), and any preference-causal claim still requires targeted root controls.

**Stage decision:** this is a promising pivot from scalar chess-concept labels to *typed concept genesis* (predicate + legal transition + blocker witness + controlled root preference), but it remains 0.13 methodology. An eventual 0.14 needs prospective engine/continuation transport and an independently falsified mechanism alternative, not the mathematical vocabulary alone.