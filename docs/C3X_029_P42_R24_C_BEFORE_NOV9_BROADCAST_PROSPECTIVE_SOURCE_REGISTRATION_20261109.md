# C3X 0.29-P42/R24-C — Before-Game Frozen New-Event Source Cohort (NOT YET ACQUIRED)

2026-11-09 KST. C-axis breadth commitment. This is a true **pre-source-event** target registration, not a claim a game was recorded, read, evaluated or became a clean holdout.

## 1. Actual official current source and the absence of monthly October bytes

Official Lichess broadcast database at `https://database.lichess.org/broadcast/`, checked November 9, 2026, still lists `lichess_db_broadcast_2026-10.pgn` as a **25-byte placeholder** and no equivalent genuine `2026-10.pgn.zst`; the latest full official broadcast compressed month is September 2026. The 25-byte placeholder is NOT a dataset; do not pretend October official monthly PGN was secured. Separate historical P37 October eight-event source artifacts remain valid but **already exposed**.

A new official November broadcast round is **precommitted now**:
`https://lichess.org/broadcast/lag-dm-2026/round-3/sbfCtgNj`.
Lichess's calendar states November 9, 2026 round 3 starting 17:30 Europe/Stockholm (Nov10 01:30 Korea); the source link and game selection were written at roughly November 9 14:xx Korea, BEFORE that round's scheduled start. Official broadcast PGN is licensed Creative Commons BY-SA 4.0. Do not claim scheduled play has occurred, games are complete or original bytes have been obtained.

## 2. Completely outcome-blind ingestion and selection

New [source-only deterministic freeze parser](../tools/c3x_029_p42_r24_future_broadcast_blind_cohort_freeze.py) must be run on **exact original complete official PGN bytes AFTER the round**:
1. SHA256-seal original raw PGN and verify correct source URL/round ID externally. No 25-byte placeholders, .zst or ZIP disguised as raw PGN.
2. Parse original move trees using `python-chess`. Admit only standard chess from initial position, unbroken legal entire mainline and final `1-0`, `0-1`, or `1/2-1/2`; source games must have at least 60 plies. Explicitly record all rejected game counts.
3. Choose **first 8** unique complete legal games sorted lexicographically by SHA256 of their *complete canonical UCI mainline*; this deterministic rule is committed BEFORE the event and cannot be replaced after seeing engine scores.
4. Freeze the complete first **30 plies** of each selected game and its full source-position FEN4/complete source game hash **privately**, with root legal move universe; public source receipt includes only original-byte SHA, complete counts and game hash identifiers, no player names, source PGN/FEN or private full history.
5. Before calling ANY engine, compare selected full canonical UCI game IDs and source-position FEN4 against **ALL accessible historical archives** (Sept16, Oct8, any other prior uploaded project games). Existing `R21-C` proves merely zero FEN4 collisions for two limited historic sets; **it does not certify every past source/game/event**.
6. Freeze candidate root selection from a source-only specified policy BEFORE independent referee, then pre-register full reply-conditioned plans and strong rivals BEFORE judge. If game count or exposure check fails, **HOLD**, not substitute an attractive case.

Source raw byte custody on Google Drive and durable release/license receipt need physical verification after successful acquisition; no claim Drive original currently archived.

## 3. Exact currently implemented state, not projected work

- [Future source selector](../tools/c3x_029_p42_r24_future_broadcast_blind_cohort_freeze.py) implemented and human-committed BEFORE games.
- [Ten synthetic negative tests](../tools/test_c3x_029_p42_r24_future_broadcast_blind_cohort_freeze.py), source-not-yet-acquired [read-only contract CI](../.github/workflows/c3x-029-p42-r24-C-pre-source-cohort-contract.yml).
- First CI attempts `#42566157520`, `#42566290843`, `#42566385280` exposed **synthetic fixture defects**, not failed chess-source empirical experiments; preserved. They were corrected without changing event URL, score-independent game selection or source freeze policy. Latest test run must be inspected separately before claiming PASS.
- Current new November source bytes, complete legal games, final chosen 8, event-disjointness across entire prior corpus, independent judgement and source NNUE mechanics: **NOT YET OBSERVED / HOLD**.
- Entire prior R24-B Sahel/Cerrado pilot is still post-R22-selected and **cannot be promoted** by pretending its archived samples are new source.

## 4. Why this matters scientifically

C3X already has a physically demonstrated classical-eval Game14 source-cause/policy response under local vs broad intervention (A-axis) and now a truly pre-judged SF16-conditioned plan independently scored against adversarial legal replies in two *exposed* October cases (B-axis). These are **different chess positions** and cannot be multiplied into a single causal–strategic explanation. To test the full hypothesis, the next genuinely novel source case needs to be committed BEFORE any event/engine labels, then native root decisions and *the same future-contingent property* must be tested on **that exact case**, with independent referee, matched-cost or frontier and strong Cui k3/BinProp baselines. Event selection must be independent of post-outcome labels.

The one-round source URL is an opening cohort, not a magical validation. Holdout status additionally needs a full exposure registry, source consistency, multiple event-family coverage and meaningful independent engine judgement.
