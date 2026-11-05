# C3X 0.29-P37/R1 — Eight Independent Late-October Tournament Families, Source-Only Admission Preregistration

**Pre-source commit: 2026-11-05 KST.** No tournament PGN move list, Stockfish score, model forecast or outcome has been inspected for the eight designated rounds before this commitment. Endpoint HTTP accessibility (headers from two rounds) and event pages have been confirmed; this is not move-content selection.

## Why this is not another monthly PGN recycling error

C3X README and GitHub code search showed **historical January–September 2026 Lichess broadcasts**, including March C2, April P0, May P1, June and July M6, August/September histories; P36 March 8-game intake overlapped an already sealed March C2 game and nominal near pairs were budget-unstable. The official October 2026 *monthly broadcast* entry is a **25-byte placeholder** on 2026-11-05; do not treat it as actual original game corpus. We instead fix eight specific **Lichess round-1 public broadcast PGN endpoints** for eight distinct named event families that began 2026-10-25 to 2026-10-30, after the previous monthly source archives. Copyright: Lichess broadcast game data CC BY-SA 4.0; retain source attribution and license.

**Eight pre-frozen event families, exactly one game from each** (no substitutions on failure):
1. 2026 Sahel International Chess Festival Open A — `https://lichess.org/api/broadcast/round/MR4eFoUH.pgn`
2. KazChess Masters Almaty 2026 — `https://lichess.org/api/broadcast/round/tZQNFMoC.pgn`
3. 2026 Chinese Chess League Division A round 7–11 — `https://lichess.org/api/broadcast/round/ZvY3jr6Q.pgn`
4. 2026 Clutch Chess: Champions Showdown — `https://lichess.org/api/broadcast/round/LVWRdrsl.pgn`
5. 1. Freiburger Bogoljubow Open A — `https://lichess.org/api/broadcast/round/lEQStSIp.pgn`
6. Magdeburg Open 2026 — `https://lichess.org/api/broadcast/round/TGKbOvjn.pgn`
7. I Cerrado Internacional de Ajedrez D. José Luis García-Palacios — `https://lichess.org/api/broadcast/round/3veI3mSx.pgn`
8. 2026 Greg Hjorth Open — `https://lichess.org/api/broadcast/round/GcyAs4TL.pgn`

Actual event-family independence between these **named tournaments** is a design assumption from separate names, times and tournament series; must compare source PGN Event/Site/players and previous selected event-family registries. Several events may have overlapping players, which is not itself duplicate games. If a single event's round does not yield a qualifying game, **HOLD entire eight**, no replacement event or round after observing outcomes.

## Source-only deterministic freeze contract

- Download each immutable endpoint twice on the same CI run, compare exact raw bytes SHA256, reject HTTP error/empty/truncated/HTML instead of PGN. Record raw SHA of each round, HTTP source URL, timestamp, provenance; two same-time downloads are *transport* parity, not official independent publisher checksum, so never claim upstream published SHA.
- Parse complete PGN with pinned `python-chess`, strict UTF-8 and a standard initial board only; reject parser errors, incomplete result, unrecognized variant, no Event, Date, White, Black, result, or fewer than **60 complete halfmoves**. Fixed board after **ply30** must be legal non-terminal.
- For **every event independently**, sort all eligible parsed games by SHA256(canonical headers Event/Date/Round/White/Black/Site/Result + full original mainline UCI SHA) ascending. Select rank **#1** from each event. Duplicate full-game UCI histories across events invalid; do not allow hidden fallbacks. This uses no engine or model output. Retain entire qualifying game history in private source manifest, with content hash; raw broadcast licensing attribution.
- Adjudication must verify no identical complete game SHA against historic **C3X C2 March16, P36 March8 and C3X 0.18 16** at a minimum, plus all historical source archives available and selected event titles if feasible. Check event date >=2026-10-25 and <=2026-11-05; if event PGN header dates or names contradict fixed sources, HOLD. Absence of matching code-search terms is not proof of exhaustive historical event novelty.
- Preserve raw eight source PGNs and one sealed manifest as read-only Actions artifact, then in private Drive BEFORE any SF16 search. If no historical inventory completeness, label `EXTERNAL_LATE_OCT_EVENT_FAMILY_PREOUTCOME_COHORT_WITH_HISTORY_GATE_PENDING` rather than “certified heldout.”

## After raw manifest is sealed

A separate pre-outcome contract must specify exactly **one** legal, action-conditioned chess consequence Q and matched information + computational resources. The primary near-tie cases must meet **two-candidate UCI identity stability + <20cp** at 24k,48k,96k, without cherry-picking. If zero survive, report zero and preserve entire denominator, not swap in a favorable case. Simpler Stockfish score+PV and conditional JSON are strong rivals and can abstain. Full C3X forecast only wins on independent correctly verified Q, not writing quality or available legal plans.

**No GitHub Actions bot authoring:** source-only Actions may only clone/check out, parse, hash and upload artifacts with contents:read; no commit/push/merge/tag/ref move; human `WhoSia` authors all repo changes. Notion science authority / Drive bytes / GitHub executable provenance.
