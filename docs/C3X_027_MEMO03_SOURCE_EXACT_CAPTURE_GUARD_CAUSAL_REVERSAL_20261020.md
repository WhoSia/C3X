# C3X 0.27 — One Guarded Chess-Search Branch Reverses an Actual TT-Induced Root Decision

**Research Memo 03 · 20 October 2026 · Results and identifiability audit · WRITING 3.0**

## Abstract
A change in chess engine search configuration can create a new tactical test, but observing that test does not establish that it mattered to the final move choice. We studied a prospective, engine-blind cohort of 16 previously unused September 2026 Lichess broadcast games. Suppressing the first source-matched transposition-table reader changed the final Stockfish16 move in exactly one game. The treated execution of that game contained a new, source-identified static-exchange-evaluation (SEE) capture-pruning event. Subsequent inspection of the original C++ revealed an overlooked qualification: failure of this SEE test is not itself sufficient to prune a move, because the engine can preserve a candidate when a subsequent discovered attack warrants searching it. We added passive instrumentation to distinguish the three actual downstream outcomes. In the exposed game, the new SEE test took the no-discovered-attack `continue` branch. Keeping the original TT-reader intervention fixed while re-enabling only this single, source-exact guarded candidate restored the untreated root move in two duplicate cold executions. The result demonstrates a locally reversible, C++-identified decision pathway under a single-event counterfactual intervention. It does not establish that the SEE Boolean itself naturally changed under identical inputs, that the guarded event is the only TT-mediated pathway, or that the effect generalizes to unseen games.

## 1. Why the original reading was insufficient
The September16 primary study was frozen before native intervention: a legal, engine-independent source-only cohort, a byte-verified original Stage A, and a fixed first eligible TT reader policy. Sixteen of sixteen source-matched TT-FIRST suppressions physically contacted the intended reader. Only game 14 changed its final root: the original selected `b3a4`, and TT-FIRST suppression selected `f3f4`. No original source SEE Boolean was flipped. Earlier finite source-prefix checks found one `capture_prune` SEE event in game14's treated run but not its uncensored original trace, after the physical TT reader suppression.

Initially it appeared sufficient to translate `SEE FALSE` into `candidate pruned`. Original Stockfish16 `search.cpp` disproves that simplification. After `!see_ge(move, occupied, -205*depth)`, the engine first tests a depth/capture condition, then checks whether the post-exchange occupancy leaves a newly discovered attack on an enemy king, queen or rook. A candidate may survive despite SEE FALSE. This distinction was obscured when the old R3 ledger inferred pruning from the SEE Boolean and when the earlier T4 observer covered quiet/qsearch pruning but not capture pruning. We corrected the source-level obligation rather than presuming that the event caused the root flip.

## 2. Exact original C++ branch measurement
Using the pinned Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` and existing C3X 0.23 TT/SEE native overlays, we inserted a passive outcome logger at the original capture SEE guard. The logger distinguishes `DEPTH_CONTINUE`, `NO_DISCOVERED_ATTACK_CONTINUE`, and `DISCOVERED_ATTACK_RETAIN` without changing any return value or continuation.

For September game 14 (source-game SHA256 `0822ec4ddab0339d51a65f3a9d077a1245b2402b111e78a3aa90d2a4d9a83652`), the sole treated-only bounded SEE capture witness matched a direct C++ guard action by key64, root call, encoded move, and threshold. Both independent cold observations followed `NO_DISCOVERED_ATTACK_CONTINUE`. The original untreated and TT-FIRST final moves remained `b3a4` and `f3f4`. Crucially, this established the actual skip, not merely the value of SEE.

GitHub Actions direct observation run [39355044167](https://github.com/WhoSia/C3X/actions/runs/39355044167) completed successfully after the two original pre-treatment Stage A public/private SHA values were reproduced exactly. This is a source-exact observation but not yet a counterfactual claim of root mediation.

## 3. Single guarded candidate re-enabling experiment
Before revealing the third-arm outcome, we committed an explicitly *postselection-exposed* contract: `c3x/forecasts/C3X_027_SEPT_GAME14_SINGLE_GUARD_COUNTERFACTUAL_PRESEAL_20261020.md`, commit `ce3a9487d56db649ae0fce8ff27ae059aab2e7fa`. This froze the original game, physical TT target, and a surgical manipulation. The original `see_ge` computation and Boolean are left intact. The physical TT-FIRST source-reader suppression is also left intact. Only the first `capture_prune` no-discovered-attack continuation whose key64, root call, move, and SEE threshold equal the already observed source event is replaced with a one-time fallthrough. Other capture guards and engine source decision logic are unmodified.

The three measurements were:

| Trial | Physical TT reader | Exact target guard | Final root UCI |
|---|---|---|---|
| A | untreated | natural source behavior | `b3a4` |
| B | FIRST suppressed | natural source behavior, actual skip | `f3f4` |
| C | FIRST suppressed | exactly one matched skip re-enabled | **`b3a4`** |

Under trial C the source logger recorded `EXACT_ONE_EVENT_REENABLED` exactly twice, corresponding to one intervention in each of two cold replay processes. Writer–reader physical TT lineage checks remained valid. Every arm produced reproducible identical UCI. Original Stage A input SHA gates passed at execution. The only changed behavior introduced by the third arm was the explicit source-local override after the SEE FALSE and discovered-attack check.

The third-arm result was executed by [GitHub Actions run 39355504956](https://github.com/WhoSia/C3X/actions/runs/39355504956), success, with public result artifact ID **12234853168** (`C3X027_SEPT_GAME14_DIRECT_CAPTURE_GUARD.json`). The public record contains no raw physical TT key, player name, PGN mainline, or modified GPL binary. The result's explicit scientific flags are `ORIGINAL_ROOT_RESTORED`, `actual_branch_proof=true`, `native_guard_one_event_contact=true`, `natural_full_mediation_certified=false`.

## 4. What the reversal identifies—and what it cannot
Let T denote the physical TT-FIRST reader treatment; let G denote the continuation at this one matched capture-pruning guard; and let A denote the engine's categorical root choice. The three measured potential outcomes are:

\[
A(T=0,G=G_0)=\mathtt{b3a4},\quad
A(T=1,G=G_1)=\mathtt{f3f4},\quad
A(T=1,G=\mathrm{force\ pass\ once})=\mathtt{b3a4}.
\]

This establishes **single-site reversibility in the treated search world**. It supports an interventional contribution by the observed guard to the treated root choice; the root restored even though the upstream TT intervention remained active. That is stronger evidence than temporal co-occurrence or a shared SEE Boolean.

It does **not** establish that this guard is the unique mediator of the natural TT effect. Re-enabling a pruned node alters downstream search, TT writes, move ordering, windows, and later decisions; such induced changes may cancel other TT-dependent effects. Neither all TT-root causal paths nor their exact descendants have been enumerated. Nor does it show that TT changed `see_ge`'s truth value for identical full arguments: the new source event was activated under a different search world. A result from one post-outcome-selected game cannot supply a generalizable success rate.

A direct confirmation requires an independently selected game cohort, frozen *before* inspecting root flips, with a predeclared event-matching rule and third-arm intervention. Negative examples where a newly activated, genuinely skipped candidate does not alter the root must be retained. For a human-centered chess explanation, one must additionally show what chess property the re-enabled candidate represents and whether a reader benefits; these are not established here.

## 5. Research OS writing-loop judgment
The paper-worthy question is no longer 'does a principal variation imply all responses?' nor 'can SEE be reproduced independently?' It is whether a *source-identifiable pruning event* can be causally connected to a change in search's final decision, with each inferential bridge independently tested. The present result supplies one concrete, falsifiable witness of local reversibility. It merits a substantial experimental Results section but **not** a general Stockfish mediation theorem or a novelty promotion without prior-art collision and prospective replication.

**Judgments:** SOURCE_ACTUAL_CAPTURE_GUARD_PASS; TT_FIRST_PHYSICAL_CONTACT_PASS; ONE_EVENT_INTERVENTIONAL_ROOT_RESTORATION_PASS; NATURAL_FULL_MEDIATION_HOLD; INDEPENDENT_REPLICATION_HOLD; HUMAN_TRANSFER_HOLD; PAPER_NOVELTY_HOLD.

## Source custody
- Pre-existing source-only September cohort and Stage A: runs 39348434657 and 39351313113.
- First source-matched TT intervention across all 16 new games: run 39351803989.
- Source chronology and initial bounded guard inference: runs 39353345692 and 39352824504.
- New direct guard observation: run 39355044167.
- New one-event counterfactual with exact source keys and SHA-rechecked Stage A: run 39355504956.
- Original game14 direct-branch observer: `tools/c3x_027_sept_capture_prune_exact_outcome_patch.py`.
- Surgical counterfactual source patch: `tools/c3x_027_sept_capture_counterfactual_patch.py`.
- Three-arm exact target, cold duplicates and conservative outcomes: `harness/c3x_027_sept_game14_direct_capture_guard.py`.
