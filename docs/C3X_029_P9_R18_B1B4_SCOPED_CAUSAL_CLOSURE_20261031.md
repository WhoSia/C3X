# C3X 0.29-P9-R18 — Closed Answer: Joint-only b1b4 Is an Identified Controlled Selection Interaction, Not an Identified Root-Score Mechanism

Date 2026-10-31. SCIENTIFIC DECISION / archival native receipt adjudication. No fresh Stockfish execution; no new source-node causal chain invented.

## Exact question
Why did game2 O/STRICT depth12 select b1b4 only under TT FIRST+SEE-guard Boolean intervention? Distinguish (I) observed causal decision interaction from (II) full internal root candidate-score/search-state mechanism.

## Observed treatment contrasts: VALID 0.23-T3 2x2 within a post-outcome-selected development case
Fixed original Stockfish16 commit 68e1e9b3811e16cad014b590d7443b9063b52, Threads=1, Hash16MB, NNUE OFF, depth12, reproducible cold pairs.
(TT0,SEE_SHAM): e1g1, -8cp, 20062 nodes.
(TT1,SEE_SHAM): e1g1, -8cp, 41685 nodes.
(TT0,SEE_FLIP): e1g1, +1cp, 46783 nodes.
(TT1,SEE_FLIP): b1b4, -4cp, 47563 nodes.
Physical TT source writer-reader proof and source-exact SEE Boolean singleton actuation recorded. Treating the selected root as binary Z=1(bestmove=b1b4), observed controlled interaction Z11-Z10-Z01+Z00=1. Node count interaction 47563-41685-46783+20062=-20843. Cp output contrast -5cp has NO interpretation as b1b4-v-e1g1 margin or natural indirect effect. This is an observed *behavioral response under a controlled source intervention* and does not assert that b1b4 is objectively superior in chess.

## Critical branch-level reason identified (but no complete mechanistic mediation)
0.23-T4 actual native C++ branch witness: in game2 the targeted quiet_prune predicate original SEE Boolean=1; both SEE_SHAM arms PASS_GUARD; in both SEE_FLIP arms original predicate is toggled 1->0 and executes ACTUAL_CONTINUE. Thus this specific quiet-move child branch is SKIPPED in both SEEflip worlds. Meanwhile the final winner changes only in TT1+SEEflip. Crucially skipping *this branch* is not proof that b1b4 itself was never searched; the tracked branch is source-local and its candidate identity is not established as winning b1b4.
0.24-P2-R2 C3b: game2 sham arms FULL source ancestor-to-root; flipped arms actual CONTINUE. 0.24-P2-R3: both fully traced root candidates LOST final bestmove (not b1b4). Game11 original qsearch guard flipped to pass, source child ancestry remained partial in both flipped arms and terminal choices were unchanged by SEE within matching TT condition (negative control).
The displayed causal logic is therefore:
Physical TT change × source-specific quiet-prune change -> altered whole search computation -> final root UCI switches to b1b4.
Source-level branch direction and actual source delivery are witnessed; identity-preserving intervening candidate scores/aspiration operations are NOT witnessed.
Do not assert `TT->natural SEE->b1b4`; SEE Boolean intervention was *external*, not caused naturally by TT.

## Distinguish necessary/sufficient scope
Within this SINGLE fixed controlled four-arm table, both treatments are required for b1b4 relative to these four observed treatment combinations. Neither singleton produces b1b4 and the joint combination does. This is not a general necessity/sufficiency theorem over all engine configurations or all internal source events. It is not a global opening move law. Other depth, NNUE, hardware, TT history and thread conditions remain untested.

## Decisive scientific verdict and STOP rule
Question A 'Does the joint source intervention uniquely produce a new root choice in this observed case?' = CLOSED YES, original repeated native evidence.
Question B 'Does the candidate b1b4 gain a provable numerical advantage over e1g1 because of a particular alpha/beta, root order or aspiration gate?' = CLOSED AS NOT IDENTIFIED FROM THE AVAILABLE OBSERVATIONS; distinguish hypothesis from fact. Neither the -4cp terminal report nor C3b sham ancestor chain can supply a candidate margin. This is an identification limitation, not scientific defeat. NO further recursive archival docs should be created as though this were unanswered by an available receipt.
Question C 'Does this controlled interaction transport to different chess positions or deeper searches?' = UNTESTED; separate prospective study and robustness target, not a reason to hold open A.

Causal validity: original selected *after* source outcomes and only two distinct May chess games; no population interaction estimate. Game11 controls source specificity but cannot by itself demonstrate generality.

## Evidence in GitHub
- c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json
- c3x/receipts/c3x-023-P1-R2-T4-native-actual-prune-continue-branch-and-T3-observer-equivalence-20261011.json
- c3x/receipts/c3x-024-P2-R2-native-ancestor-root-full-and-partial-development-20261011.json
- c3x/receipts/c3x-024-P2-R3-source-root-candidate-reached-but-not-final-and-May11-partial-20261011.json
- c3x/receipts/c3x-015-P10-R2-first-root-candidate-child-return-vs-stored-score-48-native-20261009.json

No new engine run, per-candidate scored path or CI PASS claimed. Historical reproducibility is scope-limited to the original native cold duplicate and T4 repeat. For scientific allocation, CLOSE the chosen historical b1b4 case under this exact split verdict, and shift new science to rigorously budget-shifted multi-position chess-world explanations; reopen specific mechanistic subquestion only when actual private native source trace is obtained and instrumented.
