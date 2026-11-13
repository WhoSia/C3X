# C3X 0.30 — Cerrado Queen Pair and Reply-Conditioned Plan Audit

2026-11-13 KST. Previously exposed development positions only.

## Method

[Search harness](../experiments/c3x_030_cerrado_queen_pair.py). [Raw UCI-derived JSONL and replay recipe](https://drive.google.com/file/d/1HNwraPDfVV7vMhGO017QGQqHEXdyyyDX/view), ZIP SHA256 `93b18f7056c42ba17b71ee71a9e9f743c20987f3b81c22b0610ad70f63046a7a`. Stockfish 15.1 (Debian bookworm 15.1-4, embedded NNUE), 1 thread, 32 MiB hash, ucinewgame between queries. All scores are White POV. Equal requested node limits permit different actual node counts. A UCI exact score here means a non-bound score from a finite search. At a cap, a newer reported bound can follow an earlier exact score. Both are retained where available. No holdout was opened.

## Pair screen

After 16.Bxf6 gxf6 from FEN `1r3rk1/2pq1ppp/4pn2/1b2B3/2p5/6P1/3PPPBP/2RQ1RK1 w - - 1 16`, separately force each candidate.

| Requested nodes | Qc2 | Qe1 | Qa4 | Qb3 |
| ---: | ---: | ---: | ---: | ---: |
| 50k | -80 | -69 | -549 | -675 |
| 200k | -80 | -107 | -555 | -674 |
| 1M | -72 | -78 | -588 | -693 |
| 4M | -67 | -71 | -581 | -749 |

Table shows last non-bound PV scores in the original root run. The cap-aware replay at 4M reports newer lower bounds -65 and -72 for Qc2 and Qe1, respectively. Their ordering is unresolved. Qa4 loses its queen to Bxa4 and Qb3 to cxb3 in the engine's principal lines.

## Reply tests

A 120k-node-cap sweep evaluated 31 legal replies per candidate, each freely and with d4 forced when legal (28 each), 118 recorded rows. 60 last matching PV rows carry a bound. An exploratory 1M-node-cap recheck on eight common replies returned 32 non-bound rows under the original exact-PV parser. Free minus forced d4 is positive in all 16 matched comparisons (Qc2 range 91–636 cp, Qe1 range 91–362 cp).

| Reply | Qc2 free / d4 | Qe1 free / d4 |
| --- | ---: | ---: |
| Rfd8 | -64 / -427 | -59 / -421 |
| Rb6 | -69 / -173 | -83 / -174 |
| Kg7 | -51 / -162 | -57 / -219 |
| c6 | -56 / -174 | -72 / -183 |
| Ba4 | +153 / -483 | +157 / -82 |
| c3 | +36 / -55 | +65 / -56 |
| c5 | -31 / -301 | -31 / -371 |
| Rbd8 | 0 / -393 | -48 / -370 |

- Immediate d4 explanation rejected for this pair over these eight replies. After c3 d4 Qxd4 Qxc3 Qxc3 Rxc3 both roots reach identical FEN `1r3rk1/2p2p1p/4pp2/1b6/8/2R3P1/4PPBP/5RK1 b - - 0 20`. The halfmove clock reset by captures also matches. No claim about unrestricted later d4 plans.
- After Ba4, d4 allows Bxc2 after Qc2, while free play finds Qxc4 for Qc2 and Rxc4 for Qe1. The local difference is real and the free-play estimates are similar. This does not establish a general Qc2 advantage.
- Qc3 (after Qc2) and Rc2 (after Qe1) appeared in strong-reply PVs, so we separately forced those proposed continuations across seven replies. After Ba4 the fixed continuations score 0/-558, although free play finds +153/+157. A single follow-up fails to represent the adaptable plan. Seven of the 14 forced-continuation last PV rows carry bounds; the Ba4 witnesses are non-bound.

## Transfer check

The already exposed P1 World 1 development FEN `r1bqr1k1/pp3pp1/2p5/4Q3/2P5/8/PP3PPP/R1B2RK1 w - - 1 16` has Qf4/Qc3 scores +58/+64 at 200k and +59/+65 at 1M, with 40 legal replies per candidate. In the 120k sweep, after Qd3 the Qc3 queen can capture on d3 (Qf4 +66, Qc3 +690), while after Bf5 the Qf4 queen can capture on f5 (Qf4 +469, Qc3 upper bound +55). Pairing the defense identifies local and direction-reversing geometric effects that the root gap alone cannot summarize. The 80 reply rows include 29 bounded values. This is a retrospective check of the protocol on a second development position.

Decision: preserve the matched-reply comparison and the free-versus-forced control. The data do not justify a stable Cerrado root preference or a causal mechanism of Stockfish choice. A prospective test needs a concrete goal that can be reached by more than one own continuation and independently selected strong replies.
