# C3X 0.30/R36 — Receipt-Level Claim Court & Negative-Knowledge Extraction

**Date:** 2026-11-21. **Authority:** derived-receipt consistency, not a new native chess experiment, original ZIP download, blind science pass, or human study.

## What was actually executed

The R36 parser reads the previously published [R33 cross-cohort derived receipt](../receipts/C3X_030_R33_cross_cohort_summary_20261121.json) and [R35 source-to-root derived receipt](../receipts/C3X_030_R35_root_lineage_20261121.json). It explicitly requires both frozen source-ZIP hash identities, the R33 intervention denominators, R35's two source events, the identical alpha-beta window and *negative* causal-authority constraints. It refuses altered intervention counts, missing or incorrectly judged third candidates, false shared search-window comparisons and claims that the intermediate state mediation has been discovered.

**Implementation:** [fail-closed checker](../harness/c3x_030_r36_claim_gate.py) · [13 verification tests](../tests/test_c3x_030_r36_claim_gate.py) · [read-only workflow](../.github/workflows/c3x-030-r36-claim-gate.yml). The workflow uses *zero* external writes or GitHub bot-authored commits. Its PASS applies to the actual checked derived JSON and mutated negative fixtures; it does not rehash the original Drive ZIPs this turn.

## Three findings with different evidence units

| Scientific proposition | Evidence from real upstream work | R36 verdict |
| --- | --- | --- |
| An unchanged public depth/score/bound/PV trajectory and final move imply the same internal computation | 15 / 28 observed direct child-return changes in the *selected* R29/R30 events were invisible in those public fields | Finite counterexample; not a general rate |
| A local root leader-update change in a fixed window necessarily changes the final recommendation | R29-018 and R30-028 each changed the local leader flag while final move was unchanged | Finite counterexample |
| Distinct search-event interventions can converge to the same later root decision | R35 R33-040 event 32 at attempt 20 and event 102 at attempt 24 each removed h3's local leader update in attempt 24 [367,407], then caused retry 25 to end at Qxc7 | One development **game**, two correlated intervention arms; no identified TT/history mediator |

The first changed same-window root candidate value in R35 was **Nb3**, not h3. The local h3 leader-update loss is the first consequential leader-update witness, not an assertion that every earlier return was identical.

The value 367 at the lower edge of window [367,407] is not interchangeable with a calibrated point estimate of chess advantage. In R33, two direct-child comparisons are unobserved, not negative. Event-level counts cannot be presented as independent game prevalence.

## Five necessary explanation distinctions

1. **Public output** — engine bestmove, completed depth, score *with its bound*, PV, exact engine conditions.
2. **Native observed computation** — a physically contacted source event, target identity, signed direct return and which fields were observable.
3. **Intervention total effect** — sham/mask/restoration with a valid same-prefix source event and observed downstream difference.
4. **Specified mediator** — a tested TT/state/history/budget transition channel shown sufficient or necessary for the defined endpoint, rather than merely intervening upstream and observing a later root move.
5. **Human-readable chess value** — independent legal reply evidence and actual learner comprehension transfer; neither follows from item 4.

R35 currently reaches a **matched-window competition witness and final-choice total-effect** for one development game. It does **not** reach identified mediation (level 4) or externally supported strategic/human meaning (level 5). R33-017's newly selected Qd3 was outside its prior independent referee pair and needs an additional referee evaluation.

## Why this is a theory-changing negative result

An engine's public explanation channel is a many-to-one projection of finite-budget search executions. R33 supplies physical same-public-output / changed-native-return witnesses. Therefore an inverse mapping from those public fields to a *unique* search history cannot hold over the recorded execution class. This conclusion is limited to the observed projection and pairwise interventions; it does not prove that *all* user-visible GUI metadata is equal, that no useful search mechanism can be identified, or that a particular hidden state was the causal mediator.

Equally, R35 demonstrates that distinct manipulated upstream branches may yield a common terminal decision without a known shared intermediate state. An explanation theorem that substitutes the output PV or the final candidate's local call for the search's complete decision history is already inadequate for these bounded cases.

The next research object should be an **intervention-stable, context-scoped decision-state abstraction**, not simply a longer event catalogue. See the 0.31 proposed constitution and the 0.30 version-close court.

## Reproduce

```sh
PYTHONPATH=harness python -m unittest -v tests.test_c3x_030_r36_claim_gate
python harness/c3x_030_r36_claim_gate.py \
  receipts/C3X_030_R33_cross_cohort_summary_20261121.json \
  receipts/C3X_030_R35_root_lineage_20261121.json \
  /tmp/c3x-r36-derived-court.json
```

**Boundary:** The 0.30 version may be closed as a coherent research phase with unresolved obligations transferred. This audit is not proof that C3X has solved the original near-equal chess strategy, NNUE representation or learner-effect explanandum.
