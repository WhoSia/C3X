# C3X 0.29-P9-R17 — Candidate Score Provenance Is a Necessary Scientific Gate

2026-10-31. Research question: under the historical 0.23-T3 source intervention, why did the combined TT×SEE arm select b1b4, and what native evidence could discriminate root entry, bound/rank, or ordering alternatives?

## Result of this audit
The original published T3 receipt gives only final bestmove, one reported cp and total nodes for each of four different engine executions. It does NOT give a comparable, matched b1b4-v-e1g1 root-candidate exact score or certified bound. Existing 0.15-P10 separates child-return from root stored score. Therefore a root-bound inequality is NOT a causal answer unless a native collector certifies which score object was measured.

tools/c3x_029_p9_r17_native_candidate_score_semantics.py is a prerequisite evidence-admission prototype for R15's purely mathematical interval comparator. It requires origin, search-window provenance, explicit certified interval semantics and POV, and completed candidate search. The tool only checks DECLARED provenance. It cannot verify original Stockfish logs or program semantics and returns ADMITTED_PROVENANCE_DECLARATION_ONLY at most. tests/test... includes rejection of terminal UCI score, raw fail-soft unverified bound, no window, unfinished search and missing evidence metadata.

A numerical lower/upper pair can be sound only for a specified common root estimand and validated window/score semantics. In particular, two different modified search executions cannot be used as the two candidates of a single sorted list. This gate avoids the false inference that reported final cp (-8,-8,+1,-4 across arms) yields the internal b1b4 superiority margin.

## Execution state
GitHub source+test files and read-only regression workflow were committed. Local full-repo checkout attempted but network DNS prevented fetching GitHub: no local Python unit-test run on repo source, no new engine execution, no original four-arm parity claim, no new causal mediation.
Existing historical T3 case2 joint-only result is development-selected; case11 SEE gate negative remains part of the contrast. Native source was not relinked after code changes; no new results may be called PASS.

## Correct next steps
1. Obtain/verify actual CI workflow run result and logs; commit metadata alone does not prove a successful run.
2. Restore original licensed May source and exact pinned source/engine patches with checksum and cold replay in a permitted execution environment.
3. Only if baseline parity holds, add read-only per-candidate observer with correctly derived root window, score provenance, completed search and bound/type, aspiration retries and root promotion, then verify observer noninterference.
4. Repeat original game2 case and game11 negative controls before source-disjoint prospective replication.
5. Preserve empirical evidence grades and missingness: PASS source-confirmed; HOLD censored, unavailable, or ambiguous; never infer no search from a missing trace.

Scientific verdict R17: new hypothesis-specific evidence gate implemented, actual b1b4 mechanism remains UNIDENTIFIED. Literature background from original Google Drive Knuth/Moore 1975, Marsland 1986, Russell/Wefald 1991, Avin/Shpitser/Pearl 2005 previously held and reviewed; no newly confirmed missing source.
