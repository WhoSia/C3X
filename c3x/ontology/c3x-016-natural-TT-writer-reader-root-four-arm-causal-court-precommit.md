# C3X 0.16 — Natural TT Writer–Reader–Root Causal Identification Court
## Mechanism-Warranted Case Splitting, Four-Arm Source Intervention and Path-Specific Counterexamples (PRE-OUTCOME)

**Status:** DESIGN FROZEN ONLY. No new C3X 0.16 native Stockfish searches are claimed here. C3X 0.15 formally CLOSED, prior P11/P10/P9 empirical traces used as inherited *development* evidence. 2026-10-09 KST.

### 1. What is the smallest defensible unit of one TT case?

A case is not a human tactical motif or simply one FEN. A **natural TT-use opportunity** is an authentic source history plus a frozen target event:
[
E=(P,H,	heta,mathrm{key64},mathrm{physicalSlot},mathrm{writerTag/Seq},mathrm{writerBound/Depth},mathrm{readerWindow},mathrm{readerPly},mathrm{readerReturnGuard}).
]
The proposed physical lineage `writer → consumer` must be demonstrated by an original source trace that uniquely distinguishes the selected TT generation from same-key later writers, slot replacement and hash collision. A match only on key or move is insufficient.

If a case must be split, give a **minimum differentiating witness** before trial:
- The source context changes whether the TT reader's bound qualifies for a cutoff, whether a qsearch continuation must run, whether its stand-pat is legal (in-check), and whether the subsequent root candidate is exposed.
- Merely changing the observed bestmove, score or node count after intervention is **not** an admissible new case discriminator.
- A source site matching but a branch not taken, an entry overwritten before the reader, and a no-contact site are **distinct null/contact conditions** and should not be dropped as failures.
- Do not multiply all combinations of motifs, bounds, depths, evaluator flags and engine families into empty nominal subclasses. A split must predict a new testable intervention contrast or a falsifying exception.

### 2. The motivating two-world contrast (development only)

**World #2 / CEFH**: selected exact TT shortcut value14, one bypass permits qsearch check evasion and β-cutoff with return173; P11 restoration of the exact earlier V-arm root child relay 130→14 changes the finished root output in SEE OFF and also restores SEE-ON score/work, while the analogous clamp on B is event-fired but does not alter its final root output. This is an **operator regime interaction**, not a claim that a pin concept lives inside TT.

**World #29 / RISR**: exact TT early return29 vs recomputed qsearch return29 (after legal continuation). The root may be affected by changing the presence/history of a TT read despite an identical returned scalar. The P11 root relay from #2 is NO-CONTACT here, yet world29 is a rich TT-computation case. The relevant null is **site relative**, not a worthless negative position. Both worlds were selected post-P6 outcome disclosure; keep these tests DEVELOPMENT.

### 3. Exact four-arm writer/reader factorial (new experiment)

From an independent source trace before reading any *new* downstream results, preselect one physical saved TT generation and its immediate consumer (key64, slot, writer seq/tag, bound, depth, reader alpha/beta, thread1). Create C++ patched SF16 `sf_16` at fixed commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, and a strictly identical sham build.

At a predeclared, exact writer event, apply `W=1` (original save) or `W=0` (suppress only that one save), preserving the rest of source execution. At a **separately frozen, physically identified** exact consumer, apply `R=1` (original eligible TT use) or `R=0` (suppress only that one early return and continue original source). Four source regimes:
- `W1-R1` original path (exact sham and no-op controls);
- `W0-R1` one source write suppressed, reader policy intact;
- `W1-R0` writer intact, one source reader shortcut blocked;
- `W0-R0` both specific events suppressed.

**Important competing paths:** after W0, the original selected read may never be reached or may read a different TT generation. **Do not dynamically reselect a new reader or a new physical event just because the treatment changed the search path.** Record intended assignment, actual writer/reader exposure, slot alias and hash replacement separately. No-contact remains in denominator. Factorial interactions in root outputs do not, on their own, prove natural indirect effects.

### 4. Hypotheses and required source observations

Run original/SF16-off/sham and each 2×2 arm at least two independent cold one-thread searches, with fixed depth, hash, NNUE policy, root history and compilation profile. Log for every arm:
- source writer: location, full key, slot, writer seq, generation, bound/depth, value, move;
- first physically linked reader, reader node type/ply, alpha/beta, TT return eligibility and actual taken-return guard;
- first downstream qsearch entry/stand-pat/legal replies/candidate child returns, chronological event and truncation;
- first aligned **root candidate visited**, **child value changed**, **stored candidate score mutated**, **aspiration-window/TT bound changed**, **PV reported** — distinct labels;
- final `(bestmove, score_kind/cp/mate/bound, nodes, PV)` and whether exact key/slot writer–reader provenance held;
- fail-closed original binary and root legality regressions; per-case body/history/FEN groups, cold reproducibility, strict outcome-blind cohort protocol.

Define directional contrasts using **categorical unequal/equal root moves**; do not subtract UCI codes. Value and cost contrasts are separate. Physical writer-to-reader causal claim is supported only when matched intervention and observed source event contact identify a *controlled* source path effect; stronger claims of **natural indirect effect** require additional identification assumptions (no unmeasured mediator-outcome confounding, no treatment-induced confounders, cross-world counterfactual assumptions) that TT-heavy search typically violates. The safer claim is **source-edge-specific controlled effect with an explicit limitation**.

### 5. Counterexample and control matrix

Challenge the most flattering explanation:
1. **Same key, different writer sequence**: if return changes without reading the selected writer, the alleged mediator is refuted.
2. **Writer suppressed but equal score later reconstructed**: even if final root equals original, record different visited candidates/TT slots. Identical output is not computational identity.
3. **Reader matched, return guard not taken**: site contact ≠ treatment exposure.
4. **No TT read, later root move changed**: path through source-local TT return cannot be the necessary mediator.
5. **Matched TT read and source value change, same root**: local effect may alter score/nodes without changing bestmove.
6. **Aspiration re-search overwrites an early candidate score**: first visible PV, child return and true decisive root mutation can be distinct.
7. **Same chess motif, different source operators**, or **different motif labels, same TT path**: do not automatically split/join solely by human labels.

### 6. Scientific stopping gates

- `FAIL_SOURCE_CUSTODY`, `FAIL_ROOT_LEGALITY`, `FAIL_SHAM_REGRESSION`, `FAIL_TT_SLOT_SOURCE_ALIGNMENT`, `FAIL_COLD_REPRODUCTION` lead to no scientific PASS.
- `NO_CONTACT`, `OVERWRITTEN_GENERATION`, `NEVER_RETURN_TAKEN`, `TRACE_CENSORED`, `ALIGNMENT_AMBIGUOUS` remain reported and counted, not silently excluded.
- **No outcome-dependent case split**. A source-path candidate discovered using historical world2/world29 needs a separate source-disjoint genuine PGN/FEN-group heldout, with nonpin/motif-negative controls and legal move/history checking; the existing P1 C1 accuracy FAIL 42/64 versus no-change 53/64 is immutable.
- No TT-to-root unique mediator, NNUE latent concept, or independent motif/evaluator/engine transport claim is allowed from the inherited two cases alone.

**Next-governing court:** `C3X016_NATURAL_TT_WRITER_READER_ROOT_FACTORIZATION_PRECOMMIT / NEW_NATIVE_COURT_NOT_EXECUTED / C3X015_CLOSED_EVIDENCE_P11_INHERITED / CASE_SPLIT_PREOUTCOME_ONLY / SCIENTIFIC_NATURAL_MEDIATION_HOLD`.
