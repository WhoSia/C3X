# C3X 0.30 R21 — A reply majority and a worst-reply preference can differ

[Protocol](C3X_030_R21_COMMON_REPLY_CENSUS_PROTOCOL_20261117.md) · [frozen replies](../receipts/C3X_030_R21_COMMON_REPLY_FREEZE_20261117.json).

For round 1.2, the legal Black reply sets after h4 and Qd2 contain the same 50 moves, all nonterminal in each branch. Fresh Berserk depth-12 and depth-14 searches return a finite point for all 200 position-depth pairs.

| Result across both depths | Replies |
| --- | ---: |
| h4 has the higher White evaluation at both depths | 17 |
| Qd2 has the higher White evaluation at both depths | 23 |
| Direction changes across depths | 10 |

The individual minimum across all 50 shared replies favors h4 at both depths. At depth 12 the minima are +46 versus −62 cp. At depth 14 they are +68 versus −54. The reply giving Qd2 its minimum is …Bb4 at both depths. This is an example where the number of replies favoring a move and protection against its worst reply favor different moves. These are depth-limited engine evaluations of all Black replies one move later, and the equal count treats each legal reply once.

The nominated …Ne7 and …Qc7 illustrate both directions. After …Ne7, the depth-14 principal variations initially differ with Bd2 after h4 and Ne4 after Qd2. After …Qc7, both candidate lines start with b3, while their scores still diverge. These are legal starting points for a strategic interpretation. An explanation of the value gap still needs a board predicate tested across alternatives.

The common-reply census was chosen after seeing the first two results, so it is an exposed diagnostic on one game. The independently adjudicated direction changes in 10 replies also caution against relying on one depth when drafting explanations.
