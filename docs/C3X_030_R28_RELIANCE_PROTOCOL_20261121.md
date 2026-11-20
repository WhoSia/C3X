# C3X R28 — Explainable Stockfish under disagreement

## Purpose

Test whether a learner can use a faithful account of Stockfish's search to
accept warranted advice and question advice that fares poorly under an
independently implemented engine. This development run creates comparison
items and exercises scoring with synthetic inputs. A subsequent participant
study needs separate materials, sampling and assignment.

## Frozen before engine search

- Source: TWIC 1671, archive SHA-256
  `84ef391278c0dcf1b95a9d7732882d1e34377ad807608306812450b3b7aa62b8`.
- Manifest SHA-256
  `1cfb47753f18ea060e6ac7de6752e5ac80c8fe3d7f0e69e97678fae623de96cd`.
- 32 standard positions, one per normalized PGN event label. Age, section
  and rating labels can occur within the same tournament. Exclude the
  normalized labels used in the R26 cohort and R27 transfer exercises.
  Checkpoints 30, 41, 50, 61, 70 and 81 plies are assigned from the game
  digest. Retain the histories and deduplicate by game and board state.
- Recommendation: upstream Stockfish 16 at 32,000 requested nodes, one
  thread and 16 MiB hash. Alternative: the otherwise identical 8,000-node
  choice if distinct. Otherwise use the highest-ranked distinct move in a
  separately reset Stockfish depth-12 MultiPV 3 call.
- Judge: Berserk at commit `8ae895a6151695be4a50d4fb65b0c131659c513a`
  on each of the two child positions at depths 13 and 15, with one thread,
  16 MiB hash and a fresh hash per search. Express scores from the root
  mover's perspective. Label agreement if the two finite point differences
  (recommendation minus alternative) are both at least 25 cp, reversal if
  both are at most −25 cp, and unresolved otherwise. Mate, absent points
  and bounds remain unresolved.
- Stress check the first two manifest-order reversals and first two
  agreements if available. Enumerate every legal opponent reply after
  each root and use the minimum root-mover evaluation at leaf depths
  12 and 14, fixing the same nominal total horizon as the direct child
  searches. If a reply lacks a finite score or there are no replies,
  keep the check unresolved. The same judge supplies both readings.
- Score advice uptake among users who initially picked the alternative
  separately for supported and contradicted advice. Also retain outcomes
  for those who initially picked the recommendation, unresolved judgments
  and incomplete responses. Answer correctness on a fresh position is a
  different endpoint already represented by the R27 transfer items.
