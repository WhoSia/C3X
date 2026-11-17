# C3X 0.30 S4-L/R13 and S4-M/R2 — Reply scope and the Wilkins rook test

2026-11-17 KST. The [source Harvest](C3X_030_WILKINS_EXPLANATION_HARVEST_20261117.md) identifies historical reply-dependent plan structures. The two analyses below test chess consequences at different scopes.

## S4-M/R2 — Check the published diagrams

Figures 1 and 2 in Wilkins, *Causality Analysis in Chess*, printed p. 212, differ by the black bishop on a4. Both diagrams have Black to move. Transcribe the pieces and use no castling or en-passant rights. The printed diagrams do not give a full historical move stack, so this is a diagram analysis with synthetic move counters. With each candidate black rook move from g5, enumerate legal moves using bounded mate minimax. White needs a single mating continuation after each defense and Black can select any legal defense. Report the shortest forced mate distance from White's next turn. A dash means no forced mate within five plies (three White turns).

| Black move | Figure 1 | Figure 2 |
| --- | ---: | ---: |
| ...Rc5 | 3 plies | 5 plies |
| ...Rd5 | 3 plies | 5 plies |
| ...Re5 | 3 plies | — |
| ...Rf5 | 3 plies | 5 plies |

In Figure 2 after ...Re5, White's Rb8+ gives Black both ...Be8 and ...Re8. Against ...Be8, the a4 bishop covers e8 by arriving there while the rook on e5 can recapture on e8. The legal continuation Rb8+ Be8 Rxe8+ Rxe8 shows how the defended interposition changes the refutation. In the ...Rc5 row, ...Be8 instead permits Rxe8# and the longest defense from Rb8+ is ...Rc8. The difference reproduces the need to recheck ...Re5 within this small horizon. It does not replay historical PARADISE code or decide the game-theoretic outcome of the ...Re5 position. [Five-page source](https://drive.google.com/file/d/1f1WsplBoN99OjD03kw6mqjQUZhvIKPzl/view) · [Bounded legal replay](../harness/c3x_030_s4m_r2_wilkins_countercausal.py).

## S4-L/R13 — Compare legal reply scopes at three reference depths

Keep the eight R11 game histories and candidates sealed. For each ordered pair \(a,b\), let \(R_a,R_b\) be the legal replies and \(u_x(r)\) be the fixed-depth Berserk value from the original mover's perspective after the forced reply. Measure the sign of the separate minima \(\min_{R_a}u_a-\min_{R_b}u_b\), the gap between minima on the shared reply set and the full distribution of \(u_a(r)-u_b(r)\) on shared UCI replies. Coordinate equality provides the matching key. It does not imply that the tactic or purpose of the move is identical. Drop the corresponding point for missing judge values, stale depths and bound-only reports.

Keeping the original referee binary and network fixed, a fresh depth-16 pass used **508 legal-reply searches and 135,372,152 reported engine nodes**. Depths 12 and 14 reuse R11. At each depth all 508 branch-specific scores were complete and in ordinary cp and there were 240 shared reply coordinates across the eight pairs. A fresh Berserk process replayed round 3.4 at depth 16, reproducing all 68 branch records and 14,985,601 reported nodes.

| Berserk depth | Pairs with both signs among common replies | Pairs where restricting minima to common replies changed the full gap |
| ---: | ---: | ---: |
| 12 | 8/8 | 0/8 |
| 14 | 7/8 | 0/8 |
| 16 | 8/8 | 0/8 |

At depth 16 on round **3.4**, Rad1 beat Rae1 on 26 of 34 common replies and lost on eight. The unrestricted worst-reply comparison instead favored Rae1 by 8 cp. Both sets of legal replies are equal in this round. The disagreement comes from which reply supplies each candidate's minimum and the size of the gaps, not from missing legal moves. Across depths 12, 14 and 16 the unrestricted ranking changes sign at least once in **four of eight** positions. The direction on R12's seven nominated shared replies changes at least once in **three of seven**. Round 3.1 retains ...exf6 as the minimizing reply after both candidate moves at every depth, while the candidate gap goes +15, −12, +2 cp. Thus referee-depth sensitivity remains after matching the reply.

Round 3.1 is the one case with unequal legal reply inventories. Its candidate-specific extra replies leave the minimum unchanged at all three depths. That is a sample result: in the unit counterexample a favorable shared comparison fails over the full domain when an exclusive refutation exists.

For a nonempty shared set \(C\), \(\min_C(u_a-u_b)\le\min_Cu_a-\min_Cu_b\le\max_C(u_a-u_b)\). Taking a favorable single reply gives no lower bound on the whole expression. An explanation claiming reply-robust strategic advantage therefore needs a declared reply scope and a separate test of the intended chess goal. This retrospective measurement uses one reused event and a deeper pass of the same independent engine. No native trace forecaster or human learning outcome was measured.

## Reproduce

R11 [archive](https://drive.google.com/file/d/1BQPYBC6FVyF_wlj71UvJ6lJAFf4Wq5jd/view). Use the same pinned Berserk binary and NNUE. The R13 [archive](https://drive.google.com/file/d/13QJXyg-oJaZFkH8eoLR4FMOe4L9ojmoo/view) holds the new referee output, all three scope judgments and the diagram replay, alongside a member hash manifest. Archive SHA-256 `09433d1c1342c4a641b3955be3e6e6f2de215cbacc39e1fa9982e93462443891`.

```bash
python harness/c3x_030_s4l_r11_allocation.py judge PATH_TO_BERSERK r11-cohort.json --net PATH_TO_NNUE --depth 16 > r13-judge16.json
python harness/c3x_030_s4l_r13_reply_scope.py r11-cohort.json r13-judge16.json
python harness/c3x_030_s4m_r2_wilkins_countercausal.py
```

The bounded diagram test and the TCEC scope audit concern chess consequences. They prepare separate targets for the prospectively matched same-tree trace/no-trace comparison. R13 is neither a human study nor a source intervention.
