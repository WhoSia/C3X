# C3X 0.30 R30 — R29 abstention mechanisms and source-observed hint coverage

**Scope:** Retrospective rule audit of the *already exposed* TWIC 1663 R29 cohort; no new Stockfish masks, no randomized interventions, no learner outcomes. Complements rather than replaces the [independent TWIC 1664 R30 experiment](https://github.com/WhoSia/C3X/blob/research/c3x-r30-observed-reply/docs/C3X_030_R30_OBSERVED_REPLY_RESULTS_20261121.md).

## Deterministic source rule

In each of the ten R29 positions that failed the original selector, take the original *unmodified* Stockfish trace from the named alternative's ply-one subtree. Keep reads with `hit=1`, `excluded=0`, a real non-null stored move hint and `attempt <= original producer attempt`. Prefer a producing-attempt read; otherwise the latest earlier attempt. Break same-attempt ties by the *smallest physical sequence number*, not by Berserk's reply or by seeing intervention effects. Do **not** use an externally judged move to select the hint. This rule is for candidate eligibility only; its causal predictive power has to be tested separately.

Replay with:

```sh
PYTHONPATH=harness python harness/c3x_030_r30_reply_coverage.py \
    unseen-logs/result.json abstentions.json unseen-logs r30-coverage.json
```

## Observed eligibility, not an intervention effect

The archived R29 logs have **10** previously unselected positions. The alternative rule finds a genuinely recorded, nonempty TT move hint in **5/10**:

| Case | R29 reference stratum | Source-stored hint | Independent Berserk reply | Producer attempt |
| --- | --- | --- | --- | ---: |
| R29-007 | intermediate | `f6e4` | `d8d7` | 25 |
| R29-009 | close | `e8e5` | `e8a4` | 29 |
| R29-012 | intermediate | `d5e7` | `b8c7` | 46 |
| R29-020 | depth reversal | `g4g3` | `g4f3` | 30 |
| R29-031 | depth reversal | `b5c6` | `h4h5` | 14 |

All five selected hints were present in the original **producing attempt**; R29-031 had two same-attempt eligible physical reads and the rule chooses the earlier `seq=233`. The other five cases — R29-003, 013, 014, 016, 027 — had **no nonempty eligible hint** under the given gate, and remain unselected; some had TT reads carrying values but no useful stored move. A broader selection rule that forces these to be eligible would introduce an additional treatment family.

The two depth reversals in R29 therefore have **observed internal move candidates**, although neither matches Berserk's chosen reply. Under the original rule, event *coverage* was zero for both. This is a specific selection-bias diagnostic, not evidence that those TT hints change recommendations.

A separate already-completed [R30 native intervention campaign](https://github.com/WhoSia/C3X/blob/research/c3x-r30-observed-reply/docs/C3X_030_R30_REVERSAL_MECHANISM_RESULTS_20261121.md) subsequently studied these two R29 reversals: R29-020 had no child-return change under the nominated hint, while R29-031 displayed a source-hint total effect plus nontrivial scout/re-search behavior. That result and its raw logs belong to the separate R30 experimental branch. **Do not count the five candidates above as five additional interventions**, or reuse them as independent prospective tests.

## Research decision

The original selector used an independently evaluated reply to nominate a Stockfish TT hint. This makes the sample interpretable for a specified reply, but it drops cases where Stockfish's internal hint points to a different legal response. Expand *coverage* and *effect* denominators separately: all frozen positions; positions with legal eligible reads; actual nominated interventions; verified direct-return change; verified local candidate update; final move change; fully signed producer ancestry. Never promote a change in a bound-limited candidate `update` flag to an exact root-ranking estimate. For a new cohort, preregister the source-observed fallback before looking at outcomes and keep different engine issues separated.

[Original R29 ZIP](https://drive.google.com/file/d/11KYIlnfneW4Dg8YxKLYgs1LUbafnibO2/view) · [R30 causal-scope audit](C3X_030_R30_CAUSAL_TRANSPORT_AUDIT_20261121.md) · [Source-rule script](../harness/c3x_030_r30_reply_coverage.py).
