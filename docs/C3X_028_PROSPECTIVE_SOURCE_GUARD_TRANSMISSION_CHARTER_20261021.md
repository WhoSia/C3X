# C3X 0.28 — Prospective Causal Transport Across Independent Chess Positions: Source-Exact Search Interventions, Guard-Level Mechanisms, Ancestor-State Transmission & Reproducible Cohort Validation
**Official canonical title: C3X 0.28 — Prospective Causal Transport Across Independent Chess Positions: Source-Exact Search Interventions, Guard-Level Mechanisms, Ancestor-State Transmission & Reproducible Cohort Validation**

**Status: FORMALLY OPEN — DESIGN PROMOTION ONLY (2026-10-21).** Empirical promotion is HOLD until the independently frozen cohort and original native execution receipts exist. The September Game14 mechanism remains a distinct unresolved 0.27 validation axis.

## Boundary of 0.27
September Game14 is post-outcome selected. Historical OBS b3a4, TT-FIRST f3f4, and TT-FIRST with one source-exact capture guard bypass b3a4 in two cold replays support local interventional reversibility, not natural unique TT-to-SEE-to-root mediation.
G4-G9 require actual native logs. GitHub code commits, unit tests, or green badges do not substitute for verified compile, original input SHA, A/B/C cold replay and native frame evidence. Historical C3b 0.24 files remain untouched.

## 0.28 prospective question
In a newly frozen game-disjoint cohort, how frequently does a physical TT-FIRST treatment activate a genuinely skipped capture-prune guard, and how often does a predeclared one-event bypass alter final root choice?
Target: 64 independent legally collected chess-game positions, chosen engine-blind before any Stockfish outcome, with all negative and censored cases retained. An optional follow-on tranche of 64 requires a new prior preseal.

## WSL intake and source custody
Record raw PGN byte SHA256, source, date and rights. Store originals privately. Deduplicate against all past C3X sources using canonical game IDs and hashes; uncertain duplicates are HOLD. Select one legal position per game with a deterministic rule and locked seed. Preserve exact code and Python/chess versions. Save source-only selection SHA, cohort counts and explicit exclusions before any engine experiment. Public artifacts exclude private FENs, raw TT keys, full licensed PGNs, personal names, and modified GPL engine binaries.

## Treatment declaration before looking at root results
A = OBS; B = physical TT-FIRST source-reader suppression; C = B plus at most one genuine executed capture-prune continuation bypass chosen by a deterministic source-event rule PREDECLARED for all games.
Do not select C targets using whether B changed bestmove. Record guard absent, depth-continue, discovered-attack-retain and ambiguous cases separately; SEE false is not itself proof of skip.
Specify source-priority (STRICT-only distinct from STRICT-else-BROAD), first event tie-breaking, thread count, engine SHA, cold reset, depth, Hash, FEN clocks and move order in the next data freeze. Keep denominators separate.

## Predeclared endpoints
E1: verified source guard -> do_move -> child search entry -> child return -> parent candidate consumption, using frame and key identity.
E2: E1 -> each observed ancestor return -> root candidate and iterative-depth competition. Trace gaps or frame mismatch are HOLD. B-to-C bestmove change is primary categorical outcome; restoration to A is secondary. Natural mediation and chess strength are NOT measured endpoints.
Publish N sourced, N legal, N disjoint, TT eligible, physical TT contact, guard observed, guard truly skipped, C eligible, bypass contacted, cold-parity, E1, E2, root changed, A restored, plus losses with reasons.

## Release gate
DESIGN PROMOTION: this protocol + engine-blind WSL intake and strict tests land on main with no branch or bot attribution.
EMPIRICAL PROMOTION: independently frozen cohort, auditable SHAs, native run logs and negative controls, E1/E2 verdicts and uncertainty intervals. No automatic empirical claims from this charter.

## Open engineering obligations
Correct native C3b source log -> process-separated JSON normalization (frame pointers cannot be compared across cold processes). Verify the pinned Stockfish16 return anchors, source-patch compile and instrumented-versus-uninstrumented A/B/C parity. Retain bounded log censor flags. Check output of native Actions, not merely code success. Extend rootMoves/alpha-beta/aspiration state only after local parent and ancestor transport is established.