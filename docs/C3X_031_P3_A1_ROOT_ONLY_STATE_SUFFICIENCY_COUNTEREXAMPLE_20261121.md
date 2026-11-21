# C3X 0.31/P3-A1 — A Finite Failure of Root-Candidate-Ledger-Only Markov Sufficiency

**Original native evidence:** P2-D1 physically contacted Stockfish16 source event, **one historically exposed development game**, 2 correlated depth stopping rules (15 and 16). **New engine searches: ZERO.** Derived original-byte [P3-A1 CI #44880727661](https://github.com/WhoSia/C3X/actions/runs/44880727661): all **11 actual-data and deliberate mutation tests passed**. Data custody: [checked Drive ZIP](https://drive.google.com/file/d/1zVvNz0W5Bdm9zqm5wQSuPt7bNi0zl7Ca/view), original ZIP SHA256 `5e0b5f8cb547ae163bc8bad670f4d79bc7ca70bdbaba1d4b9d19f7b09cd29d57`, inside source-derived JSON SHA256 `48aca69626fca7683ab5184244e437b1e795858d8f5d127db1553213aa3230ef`. Drive readback checksums and ZIP CRC agree.

## A precise candidate abstraction that this *one* original example rejects

Define a restricted **end-of-iteration root telemetry projection** `phi_R` that saves exactly:

1. The real root `C3X_R23_START` source record of **attempt 16, iteration 13**, prior to the physical early-return intervention: root candidate count, original completed iteration, adjusted depth and initial alpha/beta.
2. The **complete set of 45 original ordered `C3X_R23_CANDIDATE` lines** during that attempt, retaining global candidate IDs, root UCI move, source-native return score, incoming alpha/beta, search depth, search count and local `update` flag. No pairwise filtering or cherry-picking; equality means exact line equality.
3. The original `C3X_R23_END` move/value/stopped/producer record of attempt16 **without cumulative nodes**, plus the original publicly emitted **`info depth 13`** record retaining seldepth, multipv, cp score and its bound context, PV, hashfull and tbhits but **excluding node count, nps and time**.

This `phi_R` is a **carefully restricted, outcome-blind projection of the executed root telemetry**, not the entire Stockfish runtime state. It specifically excludes persistent TT table bytes, full-key writer history, search history/countermove/order and stack and the actual remaining calculation budget.

Let `s_0` be the source state reached after the ordinary futility early return and `s_1` the same-history state reached after the targeted physical skip-futility/null intervention at event19. The two source input histories and original pre-contact event signatures are the same. We can **directly check from authentic source bytes**:

```
phi_R(s_0) == phi_R(s_1)             # exact all 45 root candidate rows
Y_depth15(s_0) = d4e5 != f4e5 = Y_depth15(s_1)
Y_depth16(s_0) = d4e5 != f4e5 = Y_depth16(s_1)
```

Consequently, **there is no deterministic function `f(phi_R)` that predicts both actually observed later root selections on this recorded pair**, *under the defined common fixed-depth continuation protocol*. This is a **finite counterexample for this particular choice of root-only state projection**. It is not a theorem that every small representation is impossible or that TT/history specifically mediates the effect.

## Source-level certificate facts

The original physical target inside attempt16, depth13 was `C3X_R33_OPEN event=19`; original child return **−2429**, treated return **−2500** after two actual examined replies. The original complete **45** candidate records within the same attempt are **byte-identical** under the two executions, as is their precontact `START`. Their `END` move/value/producer all agree with `d4e5/2447/545`, **except** actual native node counts **7699 vs 7717**. Public depth13 reports the same finite `score cp 746` and same PV, with different nodes, nps/time.

The exact restricted `phi_R` SHA256 for both arms and both depth15/depth16 original native logs is **`1aba3cac8ee75cad17c5bd7601f148116cf0fc45c455aa0d63dec99dafcf3b4d`**. The public `info depth13` score/PV projection SHA256 is **`b2014465dbdfc060cafd2b7725a67eafa17dfb2189c2d232a9f6b4d89a19eb8c`**. These hashes are of the defined normalized text, not full binary original runtime snapshots.

The latent difference first becomes **externally visible in the next root iteration14**, where candidate `f4e5` changed from **2265→2280** with the same alpha2289 and no local leader update. In iteration15, its return **2238→2256** changed `update 0→1`, and the two final source choices at fixed depths15/16 differ. The initial root search window only diverges at iteration16. [P3-A0 full original source chronology](C3X_031_P3_A0_INTERITERATION_ROOT_TRANSPORT_RESULTS_20261121.md).

## What this falsifier *cannot* say

- **Not full-state equivalence:** `nodes=7699` versus `7717` is already sufficient to distinguish the two runtime states. A state abstraction retaining nodes need not identify them, and a TT/history-aware state may capture additional differences. The certificate tests **root-ledger-only sufficiency**, not any complete or universal Markov property.
- **Not a named causal mediator:** The observed intervention did change the original source search and later root choice, but the exact persistence of TT-value/depth/bound, history and search allocation to the next iteration is unobserved. No TT byte or history entry has been separately restored or transplanted.
- **Not proof of independent-game generalization:** P2-028 is a single post-selected source game with earlier R26 macro-event exposure. The depth15 and16 repetitions share the same original prefix and event, so they are correlated.
- **Not a chess-strength statement:** Neither `d4e5` nor `f4e5` is independently proven objectively better; the finite-window internal values cannot be equated to a chess advantage or a human learning gain.

## Why it matters to the 0.31 formal version question

The P1/P2 pre-event heuristic state predictor failed its held-out transport gate. P3-A0 then found the exact source event's **delayed** root contrast. P3-A1 refutes a stronger yet natural alternate rescue: **save everything the root search prints at the current completed iteration and assume it is sufficient for predicting its next move**. In one verified original program execution, that entire 45-candidate projection is identical while the future differs.

This narrows P3's search for a **nonvacuous, compact** state abstraction to information that persists between search iterations *and actually affects a downstream decision*. But the only scientifically acceptable next step is still [P3-B source checkpoint / TT-history-node intervention protocol](C3X_031_P3_B_STATE_FAMILY_TRANSPLANT_PREREG_20261121.md), with physically valid writer→reader links, read-only noninterference and reciprocal restore. Merely adding every hidden bit and fitting an unrestricted decoder would be an uninformative causal abstraction; the design must be constrained and falsifiable.

## Reproducibility

[Original-byte, full-candidate source checker](../harness/c3x_031_p3_a1_root_only_markov_falsifier.py) · [11 original-data and synthetic-tamper regression tests](../tests/test_c3x_031_p3_a1_root_only_markov_falsifier.py) · [CI source](../.github/workflows/c3x-031-p3-a1-root-only-falsifier.yml), which downloads exact 78-run P2-D1 raw artifact ZIPs, uses [A0 source proof](../harness/c3x_031_p3_a0_interiteration_root.py), hashes actual 45-candidate root projection and public depth13 projection, verifies two different later root choices and explicitly rejects inflated full-state/mediator claims. All original PGN/full raw logs remain in Drive rather than Git.
