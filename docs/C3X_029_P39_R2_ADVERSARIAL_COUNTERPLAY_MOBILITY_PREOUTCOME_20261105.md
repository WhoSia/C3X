# C3X 0.29-P39/R2 — Reply-Robust Counterplay Suppression: Exact Minimax Chess-Law Pilot

2026-11-05 KST. PRE-OUTCOME: committed before any R2 labels computed. Source is the **already exposed** P37 eight-event game cohort and two sealed SF16 candidates per game; R2 is a methodological diagnostic, NOT prospective source-disjoint validation or a new causal explanation.

## Why this exact objective, and its limitation

R1's decisive forced mate in two was 0/16 and did not discriminate general middlegame preference. We need a multi-response property that can vary without invoking deeper SF16 as ground truth or repeating the old 3-ply *material-recovery* heuristic.

For source state s and legal first mover candidate m, opponent r chooses from ALL legal responses after m. We then allow our mover reply u from ALL legal responses to s,m,r. Set C(s,m,r,u) = number of legal **opponent** replies after u (side to move is opponent), with C=0 for immediate checkmate and C=256 for terminal stalemate/draw (avoid rewarding draws as forced wins). If after r our side is already checkmated or the game ended as a draw, define the entire branch value 256. Then define B(s,m,r) = min_legal_own_u C(s,m,r,u), and W(s,m) = max_legal_opponent_r B(s,m,r). Lower W means our side has a legal response which can **restrict the opponent's immediate legal move options** even under its most option-preserving first response. Unlike a single PV, this Q sees the full legal adversarial reply universe. It is a narrow *forcing/counterplay option count proxy*, not positional advantage, winning probability or perfect-play minimax value.

Report all 16 W scores and original candidate contrast ΔW=W(first)-W(second) in P37 sealed candidate order, no hindsight reordering. Compute and store each opponent response's best constraining u, each exact reply count, a maximizing counterexample r, and a full independent verifier that replays the full legal universe and recomputes W. Root source history, original 8 game hashes, source/prediction JSON member hashes are identical to R1.

## Fail/stop

Predeclared max 250,000 leaf legal successor expansions per root; if reached: TECHNICAL_HOLD, never assign W. Do not drop/censor or replace worlds to obtain more pair separation. A terminal child draw and a terminal opponent reply each count as penalty256, with exact labels; no vacuous low mobility. If <2/8 candidate pairs have unequal W, NO-PROMOTION of this tactic/option proxy; even if ≥2 differ, NOT CLAIMED predictive or superior until a genuinely new independent source-cohort with frozen forecasts beats strong Stockfish+PV and equally budgeted foil JSON on a separately fixed chess-valued target. A selected W with low count may simply reflect giving checks, so compare it to rule-only simple immediate-check baseline and PV on a later pre-outcome test, not in this construction.

## Distinct from prior fatal issues

P27/P28 universal next-turn Nf3 legality is not value; this proxy measures exact opponent-option consequences but still cannot identify a *good* chess move. P36 showed near pair/budget instability, require 24/48/96k identity and gap transport for future near candidates. P37 PV beat old three-ply material move predictor; NO reuse of that model under the name 'C3X'. P38 Ethereal source trial stopped under actual node-count failure; do not revive. P39 R1 forced mate 0/16 remains adverse negative.

## Governance

All GitHub writes human WhoSia, Actions only read/compute/upload, no github-actions[bot] commits/push/ref changes. Notion scientific authority, Drive original artifacts and raw bytes. This registered protocol precedes the R2 CI and any R2 W calculation.