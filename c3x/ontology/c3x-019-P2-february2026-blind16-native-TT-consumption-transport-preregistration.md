# C3X 0.19 P2 — February 2026 Blind16 Writer-Version Reuse vs Native TT Consumer Transport

**PREREGISTERED before February 2026 PGN download or any February native engine outcome. Date 2026-10-10.** This experiment is a NEW game-month holdout for a mechanism first identified adaptively in January. Earlier January prospective J2/J3/J4 root-flip forecasts remain permanently FAIL.

## Source-only independent cohort selection

Download the original public Lichess broadcast February 2026 compressed PGN archive from https://database.lichess.org/broadcast/lichess_db_broadcast_2026-02.pgn.zst. Record archive SHA. The *engine-free* legal game script examines no more than the first 20,000 PGNs and selects first 512 unique eligible standard games with at least 70 halfmoves, legal nonpromotion root move and ≥3 legal root moves, at source ply = 30 + (first8 SHA hex mod 15). Game fingerprint = SHA256(canonical sorted game headers and entire UCI mainline). Sort first 512 eligible games by SHA; select first **16**. Exclude FEN4 overlap with initial P4 cohort and October 2025, November 2025, December 2025, January 2026 independent sources. Preserve source PGN references, full original game UCI mainline and original half/fullmove clock context. No chess engine at cohort selection stage, no replacing selected games after any engine outcome.

## Frozen engine and event pair selectors (UNMODIFIED from January)

Stockfish16 exact commit 68e1e9b3811e16cad014b590d7443b9063b3eb52, Threads=1, Hash=16MB, NNUE OFF, depth12, original six-field FEN, source root P4 played-first variant F, sham O/Z. Passive observation of first 2048 real native TT value-as-eval candidate reader events; cap reached means CENSORED. From the original PASSIVE SOURCE only, take first pair of actual bound-qualified source readers of **same physical full64 key/slot/epoch/write-serial, same source root candidate, distinct root-call IDs**, within TWO unmodified January definitions:
- STRICT: LOWER bound, global accepted write-age >=64, ply1, narrow source window beta-alpha<=2.
- BROAD: LOWER bound, age>=32, ply1–2, window beta-alpha<=16.

For each game/selector preserve NO_ELIGIBLE_PAIR in all denominators, no retargeting. Source root-call IDs are handles derived by rule, not hardcoded numbers. Cold duplicate FIRST-only and BOTH source V treatment, and watch at selected second root call: (1) source old-writer-epoch V-gate reader_block, (2) *actual native* TT value-as-eval assignment, and (3) *actual native* main/quiescence TT early cutoff return. Probe source full64 key/slot/shadow version/TT raw depth,value,bound,eval plus search window. Preserve every source branch event and censor state. Double cold repeat and exact original O/F/Z controls. Do not equate native first TT hit or a shadow-targeted V gate with native score use.

## Prospective risky predictions — fixed before February

**F19.1 ELIGIBLE_STRUCTURE:** at least 12 of 16 games have a STRICT source pair in first 2048; fewer is FAIL.
**F19.2 OLD_TARGET_ATTRITION:** among all eligible STRICT/BROAD role arms, at least 12 have BOTH treatment that blocks the first source V reader but no longer blocks the second selected old-epoch V reader, while an actual native TT probe still reaches selected key at its second root-call handle. Fewer is FAIL.
**F19.3 NATIVE_VALUE_SURVIVAL:** among those F19.2 arms, at least 70% execute either actual TT score-as-eval assignment or an actual TT cutoff return for the selected full64 key and second root call. Less is FAIL (if denominator zero, FAIL NOT_TESTED).
**F19.4 DUAL_USE_TAXONOMY:** >=1 of F19.2 source arms demonstrates native early TT cutoff rather than evaluation assignment. Zero FAIL. This is intentionally risky after one January instance.
**F19.5 ROOT_CHOICE_NONTRANSPORT:** <=2 F19.2 source role arms change categorical bestmove relative to frozen source F. More is FAIL. This tests the limited root-choice relevance boundary.
**F19.6 SOURCE_PROVENANCE:** all actual native-use statements have live full64 writer shadow matching key and pass cold six-field-UCI/O=Z/no-contact controls, and all 16 source games and selector denominator records survive. Otherwise technical HOLD/FAIL-CLOSED.

### Interpretive rules

A prospective F19.3 PASS supports source-functional TT value use despite writer-version reidentification under THIS SF16 search contract; it is not a universal chess law and says nothing about a specific cached numerical score causing the final move. Original January sample had 29/29 role arms that retained real TT use despite losing old-epoch V target (28 eval substitutions, one cutoff). Feb is the first planned independent check of this new reading, not a resurrection of J2/J3/J4. Source selection should be archived and SHA-frozen before any native results. Any failed forecast remains failed even if later thresholds are retuned for new tests.

## Future engine-crossing HOLD

No second-engine TT equality is assumed. Mapping a different engine's native cache entry, TT key collision policy, evaluation cache semantics, bound-value substitution and cutoff must happen before cross-engine transfer predictions. Claim physical state-space comparability only after source-level mapping and negative controls.
