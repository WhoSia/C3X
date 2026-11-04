# C3X 0.29-P35/R4 — Original P34 Three-Artifact Audit, Two Static Reversals, and Read-Only Cold Replay

Date: 2026-11-04 KST. **One real local archival reanalysis PASS; new native CI cold replay registered, execution outcome NOT yet verified.** Do not mislabel historical traces as a newly generated Stockfish search.

## Narrow question and stop rule

Before spending time on new NNUE semantic probes, can we establish the *authenticity and exact comparison lineage* of the existing 12 full direct traces? Then can we independently cold-repeat those legal boards without altering source or outputs? **No new concepts or wider claims until these gates pass.**

## What was actually read and checked (unpacked original full binary artifacts)

Original files were newly fetched as original bytes from:
- [Original source PGN artifact run 37981820261](https://github.com/WhoSia/C3X/actions/runs/37981820261): 16 source cases, canonical original JSON SHA256 `6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c`.
- [P34 source-executed equal-budget search artifact run 41778389205](https://github.com/WhoSia/C3X/actions/runs/41778389205): four selected roots from two exposed games; core result JSON SHA256 `c80704f2f81c4920597fbf6b559ef38dbae60f35458c7a2f665f1cf57d2563dc`.
- [P34 full direct NNUE::trace run 41778762120](https://github.com/WhoSia/C3X/actions/runs/41778762120) and [Drive raw archive](https://drive.google.com/file/d/1l6RVNZ79XyB_VORm79q-AUIQEwMtqa0_/view): outer ZIP SHA256 `2b426b81c97d1483581e398c7a300b221a39ebe6d9e5e0194bec4d3f2885547e`, raw JSON SHA256 `07d78a9261dd87d12b900bc3cec715d4d28aa739212ef3c81507b918a6ba14f9`.

**New local archival verification result:**
- Original 16 source cases, 4 unique candidate roots, **12/12 full-history board descriptions and numerical evaluations match** the original P34 compact archive fields, ignoring only the raw trace field absent in compact receipts.
- **12/12 individual raw NNUE::trace output SHA256** agrees with each original record; 12/12 contain the original classical, NNUE and final eval summaries, NNUE derived piece-value diagnostics and network contributions.
- Source ply lengths agree with each recorded root/reply history length. Each response identity matches its own original mode-specific worst-reply reference table (all 4 roots, 8 reference outcomes).
- P34 search-stage and direct-trace-stage stored executables share the same recorded binary digest `6458324545ef0f43b5a74de75c980e08413251247bba500d9befac113a43f325`. This shows original archived binary receipt parity; **not** an independent 2026-11-04 cold run.
- Local fail-closed archive verification tests **5/5 PASS**, including deliberate source and ZIP tampering rejection. Repository reusable [audit program](../tools/c3x_029_p35_r4_archival_lineage_gate.py) and [archive-backed tests](../tools/test_c3x_029_p35_r4_archival_lineage_gate.py); the standalone local code/test implementation was actually run, whereas new repository workflow completion has not been checked.

## Important refined result — 2 of 4 source-exposed roots have direct STATIC ranking reversal

For each candidate root, compare the **two already selected P34 evaluator-ref worst White/Black reply boards**, a = classical-ref worst and b = NNUE-ref worst. The scores below are *white-perspective direct static evaluation in pawns*, never the root-player perspective of search returns. Define `C = Eval_classical(a)-Eval_classical(b)`, `N = Eval_NNUE(a)-Eval_NNUE(b)`, `D=N-C`:

| Source game | Root | a vs b UCI | C | N | D | True static rank reversal? |
|---|---|---|---:|---:|---:|---|
| 10 | `e5f4` | `e3f4` vs `f3f4` | +0.09 | +0.10 | +0.01 | NO |
| 10 | `e8f7` | `f1e1` vs `e3e4` | +0.09 | -0.12 | -0.21 | **YES** |
| 14 | `c2c3` | `e7h4` vs `d8d7` | +0.30 | +0.07 | -0.23 | NO |
| 14 | `d5d3` | `c8e6` vs `b5b4` | -0.24 | +0.08 | +0.32 | **YES** |

This is an **archival reanalysis** newly tabulating four contrasts, NOT 4 novel independent games or a heldout causal discovery. We had previously highlighted the case10 `...Kf7` example. Case14 `d5d3` supplies a *second concrete example* of direct static ranking reversal in the same original selected developmental cohort. The `...Bxf4` pair remains the negative control: no static rank reversal despite differing referee search results.

## Identifiability boundary — do not spend time on speculative neuron semantics yet

`Eval::trace` prints both models and a final score on a board, regardless of which evaluator a search subtree actually took. In pinned SF16, `evaluate()` can choose HCE if `!useNNUE || abs(psq)>2048`. **Therefore these 12 static records are insufficient to assert NNUE was on the actual causally relevant path to a root decision.** No parent/root ancestry, dispatch counts, path-specific intervention, new holdout generalization or human usefulness claim.

## Real next native execution

A new [read-only SF16 12-board two-cold-replay workflow](https://github.com/WhoSia/C3X/blob/main/.github/workflows/c3x-029-p35-r4-cold-replay.yml) was committed [0e6a9c5](https://github.com/WhoSia/C3X/commit/0e6a9c5c2cbe904b30aea506826d6013d0887523). It: recovers immutable original GitHub artifacts; validates SHA; clones exact official `sf_16` commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; compiles; invokes original source-direct `eval` harness twice (one new subprocess per board per repeat); compares all 12 raw traces bit-for-bit across both cold runs and the archived original; emits artifact hashes and a verdict. GitHub Actions permissions are **contents: read** and artifact-only. **The run has not been confirmed succeeded in this turn**; if run fails, report that failure and do not claim P35 cold parity.

## PI decision

Proceed ONLY to evaluation routing (dispatch HCE/NNUE on actual engine search node) if the cold repeat really passes. Defer new latent-feature models and broad competing-paper surveys. Prefer an NNUE mediation falsifier under controlled source-native instrumentation, with matching search budget and genuine source-to-parent/root ancestry. Existing cases are exposed development only.

**Governance:** GitHub authenticated user `WhoSia` must author/commit; GitHub Actions must never push/commit/merge/tag or move refs; **`github-actions[bot]` contributor forbidden**. Drive original bytes preserved, Notion scientific current verdict.
