# C3X 0.7.0-G9.5-P13 — Root-Candidate Competition and Preference Boundaries

## 1. Return to the founding chess question
P13 does not refine the P12 cutoff taxonomy. It returns to the original C3X problem: why does an engine prefer one near-equal legal move over another under a controlled search regime?

The terminal objects are legal root moves, not telemetry labels. Search events matter only insofar as an exact intervention changes which candidate survives as the root choice, redirects the choice to a third candidate, or measurably reorganizes the candidate competition without crossing the root boundary.

## 2. Fresh world
P13 uses only completed July and August 2026 Lichess broadcast dumps. It scans the first 1,536 games per source and deterministically selects eight late-opening positions per month after excluding every recoverable P1-P12 candidate hash. Position selection is outcome-blind.

## 3. Candidate qualification before intervention
Every legal root move is evaluated once in a cold, root-restricted 12k-node probe. The six highest moves form the shortlist. Each shortlisted move is then re-evaluated twice, cold and root-restricted, at 30k nodes.

A move is stable only when both confirmatory searches return the same non-mate cp score. The contextual winner W is the 80k-node shared-search bestmove under the inherited prime/decoy history protocol. W must itself be a stable shortlisted move.

The rival R is the other stable shortlisted move whose confirmatory cp score lies closest to W. Ties prefer the higher score and then lexical UCI. The pair is admitted only when |score(W)-score(R)| <= 50 cp. This threshold is frozen before intervention outcomes.

This deliberately restores early C3X practice: a shared bestmove or MultiPV ordering does not by itself constitute a marginal preference object.

## 4. Two prospective seals
P13 has two nonintervention seals. The design precommit freezes sources, positions, binaries, budgets, qualification rules, target rules, support gates and replication criteria before any engine outcome. Qualification then produces only baseline and isolated-candidate evidence. A pair-freeze seals W/R identities and marginality evidence before any exact-event intervention is run.

No T_ONLY outcome can affect pair membership or target-selection rules.

## 5. Root-child attribution without public TT keys
P13 privately fingerprints each shortlisted legal move by a cold searchmoves trace. A unique ply-1 internal position key is mapped back to that legal UCI move. The map is used only inside the workflow to attribute shared-search ply-1 semantic events to root children.

Public artifacts contain only candidate identity and derived exposure summaries. Raw TT keys are never emitted.

This is deliberately called root-child search exposure, not candidate-specific node allocation. P13 does not have authority to claim a per-candidate node budget from semantic-event counts.

## 6. Candidate competition graph
For each shortlisted move P13 can report:
- legal UCI/SAN identity;
- root-child semantic-event exposure count and class composition;
- null-window exposure;
- maximum observed ply-1 search depth;
- first and last trace ordinals;
- whether the move ever became the depth-indexed PV incumbent;
- whether it finished as winner, was later displaced, was searched without becoming incumbent, or had no mapped root-child exposure.

The depth-indexed incumbent sequence supplies the PV branch-replacement path.

## 7. Exact event target
P13 inherits the already-earned P12 upstream skeleton only: MAIN MOVE_ORDER_SEED at ply 1, depth 5-8, repeated full key, same most-recent TT move, LOWER or UPPER bound.

A target is P13-eligible only when its private ply-1 key maps to W or R. Up to eight targets per world are chosen by exact address-id order from the baseline trace. Selection never consults the counterfactual root move.

The only primary intervention is T_ONLY: remove that exact semantic use during measurement search while leaving TT storage, replacement, indexing and age untouched.

## 8. Primary effects
DIRECT_PAIR_FLIP means W becomes the frozen rival R. This is the strongest P13 witness: an exact search event crossed a preference boundary between two independently qualified near-equal legal moves.

THIRD_MOVE_REDIRECT means the intervention selects a legal move other than W or R. It is causal search sensitivity but not pairwise boundary identification.

ROOT_UNCHANGED means W remains the bestmove. Exposure, candidate-fate and internal PV changes remain secondary diagnostics and cannot be relabeled as a pairwise causal flip.

## 9. Replication
The frozen signature is target side (winner/rival) + target bound + isolated-score gap band + effect category. A DIRECT_PAIR_FLIP signature is replicated only with at least three witnesses spanning at least two engines, two positions and both monthly sources.

Local exact causality and transportable law remain separate claims.

## 10. Authority ceiling
P13 can identify an engine preference boundary under the frozen search regime. It cannot establish objective chess truth, human strategic intent, or an engine cognitive reason. Root-child event exposure is not node accounting. A failure to replicate is a positive transport ceiling, not permission to invent a narrower post-hoc target class.

## 11. Stop rule
The 48-world campaign is adjudicated once. No near-equal threshold, effect category, target skeleton, or replication signature may be repaired after intervention outcomes. If transport fails, the mainline returns to the chess question at the next scale rather than reopening cutoff taxonomy.
