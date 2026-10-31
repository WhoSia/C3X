# C3X 0.29-P9-R7 — Cross-Run Evidence-Joins Cannot Certify a Same-Run Causal Path

2026-10-31 | original historical GitHub receipt audit; no new Stockfish run, no raw private artifact replay.

## Core logical result: cross-run join impossibility
We inspected native receipts:
- 0.24-P2-R2: May broadcast two development games, depth12, factorial arms; 2 FULL source ancestor→root chains (game2 sham arms), 2 PARTIAL (game11 SEE flip), 4 actual CONTINUE; full source chain under sham is NOT the observed joint-only bestmove switch arm.
- 0.25-P11/P12: public Standard starting board, depth7, 24 source-native TT returns, 24 immediate parent frames, 24 SEE guard class events, 20 root updates; each class sampled under independent quota. Parent returned-score consumption not instrumented in P12.
- 0.25-P13-R4: public Standard starting board, depth7, 24 QSearch TT child-parent assignments and 18 q→bestValue public joins, but zero full same-run P11→P12→P13 public event joins. Main/LMR/PV sites censored.

The above do not form a single path by transitivity: P0 (0.24) and P1/P2 (0.25) concern DIFFERENT BOARDS, depths, builds, root calls and interventions. Even within 0.25, identical counts for disjoint class-quota samples are NOT event-identity joins. Therefore `full ancestor in experiment A` + `score consumed in experiment B` does not imply a full TT→SEE→root mediator in any one execution.

## A properly typed witness
Define a native event ID as tuple of source-game history / FEN6, exact engine and patch SHA, cold process & root-call, search iteration, aspiration attempt, ordered node-call identity and parent-call identity, candidate root UCI, event class and ordinal. An evidentiary join is valid only where the necessary tuple coordinates agree or there is an explicit native call-identity ancestor map. Parent consumption of a returned score must be directly witnessed with sign and bound; cannot be deduced from a source 'return ttValue' or an uninstrumented call-frame unwind. The final candidate update and bestmove must be sourced from the same process/attempt, with retry state documented.

When any mandatory coordinate differs across records, no same-execution identification is possible. When coordinates are hidden/censored, classification is UNKNOWN, not a proved absent path.

## Novelty and decision implications
This is an evidence typing and admission check, not a novel general theorem or experimentally established mediation mechanism. It prevents a false positive causal claim in an aggregation/reanalysis workflow. What remains scientifically useful: choose ONE original source experiment (the 0.23 joint-only b1b4 case if raw logs available), audit the existing cross-arm event coordinates and explicit root updates, and add ONLY missing per-candidate source records with cold noninterference controls. Negative case game11 retained.
Preserve all 0.22–0.25 prospective predictive negatives and TWIC source rights boundaries.

## Exact receipts
- c3x/receipts/c3x-024-P2-R2-native-ancestor-root-full-and-partial-development-20261011.json
- c3x/receipts/c3x-025-P11-P12-actual-TT-return-SEE-pruning-root-score-and-native-parent-frame-science-20261011.json
- c3x/receipts/c3x-025-P13-R4-native-original-full64-writer-q-parent-public-censor-20261012.json
- c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json

## Literature authority
Original Drive papers for background: Knuth & Moore (1975), Marsland (1986), Avin/Shpitser/Pearl (2005). No new bibliographic additions were needed for this source audit.
