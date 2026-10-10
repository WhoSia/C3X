# C3X 0.24-P2-R3 — Source-Matched Root Candidate Survival & Partial Ancestry Diagnostics

**Status: POST-C3b DESCRIPTIVE FOLLOW-UP PRECOMMIT / DEVELOPMENT ONLY.** Source May #11 F/STRICT and #2 O/STRICT, same 8 TT×SEE arms; all previously exposed. Original C3b native run #38079737780 produced 2 full ancestor→root, 2 partial and 4 actual continue. This is not a fresh confirmatory study.

Before R3 run freeze:
- Reuse original C3b native observer, source SHA, T3 strict 2-case preseal and historical T3 exact-byte parity; no source-value intervention beyond original sham/flip, 2 cold runs per arm.
- Convert frozen root context source `root_move` native integer into legal UCI using pinned SF16 move encoding against the **source-only original legal board**; 1:1 mapping required.
- Compare that candidate UCI to the same cold-run terminal depth12 exact bestmove. Report `REACHED_ROOT_AND_FINAL_LEADER`, `REACHED_ROOT_BUT_NOT_FINAL_LEADER`, `C3B_PARTIAL_ROOT_LINK_HOLD`, `GUARD_CONTINUE_CONTROL`. Only FULL C3b chain may support a source-linked candidate classification. A guard-pruned descendant and final root selection are different causal objects; never treat root equality as proof the descendant was searched.
- For partial May #11, report **bounded source event vocabulary and ply only** (not FEN, private key, full path, player). This is posthoc fault localization, not relabeling a missing edge as PASS.
- Public: game ID, four arm statuses, matched/not final, event type/ply footprint, aggregate counts, source-rights and internal full-private SHA. No original PGN, player identities, full original UCI move lines, raw native parent keys, modified Stockfish GPLv3 binary or TWIC material.
- Root source candidate equals final bestmove is an observed equality, not source-uniqueness, natural TT→SEE mediation or held-out M3 skill. Preserve C3b original 2 full/2 partial/4 pruned outcomes irrespective R3 observations.

No new source cohort extraction, no September treatment; P3 128 source-only Git-sealed forecasts remain separate. GitHub Actions `contents: read`, human WhoSia commits only.