# C3X 0.21-P2-R1 — Natural-versus-Prioritized Root-Order TT Writer–Reader Remapping

**PRE-NATIVE-OUTCOME REGISTRATION, 2026-10-10 · C3X 0.21 ACTIVE · exploratory fixed March16**

## Why this experiment exists

C3X016-P4's `F` treatment rotates a *played-in-PGN root move* to first place; `O` leaves normal engine root order unchanged; `Z` is the no-contact control. Four of 16 frozen March positions have O↔F final bestmove differences; games4 and9 return to O's bestmove after `F+FIRST` exact physical TT reader suppression. P2 source exact first vs second physical reader factorial delivered (31/31 FIRST, 31/31 SECOND, 5/31 BOTH with both contacts). This supports **root-order conditioned search-state sensitivity**, and leaves open whether a similar native TT effect appears in natural O. Reusing F's full64 key, slot, epoch or root calls in O would be source-confounded.

## Protocol sealed before any O-TT counterfactual outcomes

**Universe:** exact 2026-March16 source SHA `d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee`, 16 positions, 32 STRUCTURAL STRICT/BROAD role cells. Historical fixed source `F`/V comparison SHA `5ee15c3ec48be0042a9bb0ae7566808737f56e7568c2b29d43f00ae64afcb259`. All chess decision primitives remain frozen.

**Engine:** unmodified Stockfish 16 revision `68e1e9b3811e16cad014b590d7443b9063b52` plus validated immutable C3X016–020 overlays, single-thread, 16MB hash, NNUE off, depth12, original source clocks. Same binary and source instrumentation as P2.

**Natural O independent discovery:**
1. Per position, run cold O-OBS and Z-OBS duplicates; O/Z six-field UCI equality, and O-OBS UCI exact match to SHA-frozen earlier P1 `O_UCI`.
2. O-OBS discovery cold duplicates, exact UCI equality with O reference; no payload censor and 2048-event source bound recorded (not faked into full coverage).
3. For each O world, use exact unchanged January frozen STRICT/BROAD `first_pair` selector on only O's own passive writer-reader event history. The eligible source pair carries its *own* `key64/slot/epoch/writer_serial/root_move/calls`. No result-based source retargeting.
4. O-ZERO: same actual O selected physical target, no blocked reader (strict sham); O-FIRST: suppress first selected O physical TT reader only, cold twice. A valid contact must match exact O source's full64, slot, epoch, root candidate and root call, with a genuine `reader_block` event; no contact = noncontact not success.
5. Outcomes: final categorical bestmove, complete UCI, nodes, PV, depthwise root leader, source-aligned first recorded child return change (only prior to recorded path divergence), writer–reader physical integrity. Fixed denominator of 32 roles including NO_ELIGIBLE. Full O vs F, O-FIRST vs O and F-FIRST vs F comparisons; never interpret F root source physical as O identity.

**Primary exploratory results:** total native O eligible, actual contact, O-FIRST bestmove flips/denominator, overlap of affected chess positions with F-FIRST, source lineage differences and reordering effects. The focal #4 and #9 subgroup was chosen based on *earlier* P1 F outcome and remains retrospective.

**Competing interpretations:** H_order: search order changes candidate history and hence which TT identities are visited; H_reuse: physical TT first-reader can change final choice even without played-first rotation; H_prefix: root order alone explains all observed end moves independent of physical TT effects. Compare observed O-world data without assuming any H is true.

**No code edits to Stockfish16 for this contrast; no root order forced in O.** Same frozen 635 legal move and 3-ply reply-affordance metrics only used to interpret which legal moves changed, not to train selectors. Fail closed for source mismatch/trace censor/duplicate cold anomalies; do not promote tech failure into scientific FAIL. Keep old PAG, `CPP_224`, F19.5, K4 failures recorded.

## Gate to 0.22

0.22 should follow a **new independent prediction capability** and paper-ready method, not merely an extra instrumentation artifact. This run establishes one missing causal reference frame: independent natural O TT source remapping. A disjoint new-month PGN source cohort and paper hypotheses are to be frozen separately, after examining this R1 experiment.
