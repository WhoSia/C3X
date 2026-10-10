# C3X 0.23-P1-R2-T2 — Presealed Exact Native SEE Site Actuation × Physical TT First Reader

**2026-10-11 KST. Written BEFORE ANY T2 exact native SEE actuator is enabled. Status: AUTHORISED DEVELOPMENT EXPERIMENT ONLY.**

## Immutable gate inputs

P1-R2-T1 read-only native source search-state CI `38063680310`, source SHA `0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61`, Stage A SHA `fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442`, private six-case full experimental JSON SHA **`1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb`**, and public artifact ZIP SHA `fb0a2c209807970a6021f35f85e3a8f3b9027c977adb1bd552c7cc34126bb383`.

Read-only T1 found 21 native SEE events across 4/6 development cases with exact `full ordered ancestor key vector + source ply/depth/alpha/beta/PV/rule50/initial occupancy + board key/native move/site/threshold` matched and occurring after actual watched native TT score use and its counterfactual physical reader block. **Two T1 cases are censored HOLD**. No original SEE return naturally changed; matching a measured search-state tuple is NOT a whole Stack/TT computational-state equality proof.

## Target selection ALGORITHM frozen before first native forced SEE result

Select exactly one target per each of the six immutable May2026 post-R1 developmental cells `(1,O,STRICT), (8,O,BROAD), (11,F,STRICT), (12,F,STRICT), (2,O,STRICT), (3,O,STRICT)`. For each case:
1. Reproduce T1 read-only original+TT FIRST experimental JSON **byte-for-byte**, verify SHA **1975a515...** with the newly compiled T2-capable but actuator-OFF source. Fail-stop `T1_REPLAY_DRIFT` if mismatch.
2. Read only T1's pre-frozen `SEE_native_search_state_comparison.first_two_full_computational_match_candidates`, in its preexisting chronological source ordering. **Choose FIRST** of those two candidates whose original source SEE `site` is strictly `quiet_prune`, `qsearch_prune`, or `qsearch_futility`. `capture_prune` is ineligible because Stockfish has additional discovered-attack guards and a potentially uninitialized `occupied` SEE output.
3. No further scan, no alternative site after failure, no selecting for observed flip, and no using post-T2 bestmove to choose eligibility. If neither first-two candidate is eligible or T1 reports `HOLD_CENSORED`, target status `NO_PRESEALED_PRUNING_TARGET` / `HOLD_CENSORED` respectively; **DO NOT TREAT** it.
4. Each target must be packaged with original `rootcall,rootmove,full64 key,parent key,full path EXACT hex string,native move,SEE site/threshold,ply/depth/alpha/beta/PV/rule50/input occupancy` plus actual source original SEE Boolean. The exact source tuple is a deterministic replay-derived record, committed by this *selection code rule* before output is seen. It is stored only in private GitHub Actions runner; public report includes selected case count, site counts and digest, not source-derived raw chess game FEN.
5. The C++ actuator *must compare every target field* (including path vector and source search window), and delivers **exactly one** Boolean complement at the **same source event**; all subsequent native SEE calls remain original. A `TARGET_NOT_REACHED` or ambiguity is **NO_CONTACT**, not a counterfactual result; never flip the first *different* SEE call.

## Controlled 2 × 2 and necessary controls

At each eligible target, evaluate four single-thread cold-twice native Stockfish16 arms:
- `T0/S0`: TT original, SEE original, exact-site actuator OFF (must match frozen T1 baseline UCI).
- `T1/S0`: selected physical TT FIRST reader suppressed, SEE original (must match T1 treated UCI).
- `T0/S1`: TT original, only this source-matched SEE Boolean inverted once.
- `T1/S1`: TT physical FIRST reader suppressed, *same exact* SEE source event inverted once.

All four source arms must use identical original chess FEN clock, UCI root order and TT source specification. Validate genuine physical writer→reader and original root candidate in both TT=1 arms, ensure no unintended TT blocks in TT=0 arms, validate exact native SEE `original/delivered`, site and source tuple for both S=1 arms, verify 2 cold clones bit-for-bit, and record final exact UCI, root-search depth leaders, source SEE fork site before branching, real native TT original score-use vs actual cutoff separately.

**Primary observed categorical contrast:** `bestmove(T1,S1) != bestmove(T1,S0)` and `bestmove(T0,S1)!=bestmove(T0,S0)`; one or both arm events NO_CONTACT ⇒ no valid 2×2 for that game. No natural indirect effect is numerically identified by intervention on a deterministic SEE function. The intended result is *controlled source-site intervention sensitivity* and whether TT path suppression changes downstream response to identical SEE branch perturbation, with cases grouped at game level. If no final choice difference, report a genuine negative effect.

## Boundary and release

All six games were identified after R1 changed-move results: **development only**, not independent heldout nor exact-move prediction success. M0 117/124 > M1 111/124 on new independent 32 remains a negative M1 result. Source rights: only Lichess May2026 broadcast CC BY-SA 4.0 and original CC0 puzzle controls; public artifact aggregate counts + raw result SHA only; no complete PGN/player data or modified Stockfish GPLv3 binary.

**No T2 source SEE actuator has been executed as of this precommit.**
