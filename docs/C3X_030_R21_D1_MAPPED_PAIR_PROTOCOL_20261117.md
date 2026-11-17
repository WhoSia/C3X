# R21 D1 — Intervention on the first fixed candidate pair

Take the first numeric round with both frozen opponent replies from R21 selection, round 1.2. Replay its exact history. Allow only the two nominated roots h2h4 and e2d2, ordered by the selection record. Use Stockfish 16, one thread, 16 MiB TT, classical evaluation, and 24,000 requested nodes. Use a clean process for every search.

Discover the first actual ply-one TT hit, as in R20. Freeze the key and raw stderr digest before opening the matched arms. Use the same trace key in sham and one-hit mask, with the sham using the unused mask sentinel. Repeat both arms, check the same incoming hit, compare return and PV-edge ancestry in each arm, and report the final allowed root choice plus any bound qualifier. Report missing links explicitly. This tests computation on the actual stable pair from the reply study. It does not make the source-event projection or independent conditional reply evaluation a causal mediator.
