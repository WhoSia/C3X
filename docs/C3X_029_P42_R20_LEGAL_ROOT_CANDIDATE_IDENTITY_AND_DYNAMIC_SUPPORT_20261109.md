# C3X 0.29-P42/R20 — Are the Interim Root Leaders the Original TT-First Move or Third Chess Moves?

Date 2026-11-09 KST. **Preregistered before first R20 native outcome.** This is a single difficult source/strategy bridge step, NOT a paper on legality, UCI encodings or progress-count metrics.

## Evidence requiring this research unit

Game14 is a postselected 2026 September Stockfish16 program with NNUE OFF. Authentic R18 [#42552769246](https://github.com/WhoSia/C3X/actions/runs/42552769246) forced one exact board+window-matched C cycle-alpha source return +1→−1: immediate cutoff TRUE→FALSE, root b3a4 unchanged in 2 cold. Authentic R19 [#42554337265](https://github.com/WhoSia/C3X/actions/runs/42554337265) found the *same* physical source intervention **changed root leaders at depths 9, 10, 11**, and changed score/average through depth12 even though original/reversed C final selected b3a4. Independent ZIP+JSON SHA256 were checked and [sealed](../evidence/C3X_029_P42_R19_ACTUAL_INTERIM_ROOT_LEADER_RECEIPT_20261109.json).

At this point neither the source-native native numeric move code nor score deltas explain WHICH legal root candidate gained an interim lead. Do not say source reversal selected original B=f3f4 until verified. A third candidate could emerge in an alpha-beta dynamic candidate set; past C3X 0.22 P8 root-support discoveries make this a real alternative, not rhetorical detail.

## Preregistered real original-source R20 experiment

The new [R20 executable](../harness/c3x_029_p42_r20_source_native_legal_root_candidate_transport.py) *reruns*, without editing, the original R18 physical source event proof through the R19 12-depth root court on the same pinned Stockfish16 SHA/StageA/native TT reader. It then:
1. independently reconstructs the actual Game14 `chess.Board` from the source's full FEN clock (no starting-position guess);
2. decodes the original Stockfish ordinary Move source integer `(from<<6)|to` conservatively; special-move flags, 0, unrecognized values are **HOLD**, not silently treated as normal;
3. checks **each** root leader at every depth in original A/B/C and source-reversed C is an actual legal candidate at the original same source board;
4. cross-checks the precise depths where original C and reverse C leader identity differs against the already independently admitted actual R19 native result;
5. reports per-depth legal UCI A/B/C/C_reverse leaders, whether reverse equals original B, and whether a **third legal candidate** appears; publishes only aggregate choices and no private board/FEN/PGN, source hash, TT trace or engine binary.

The permitted hypotheses:
- **Interim B-choice recovery:** reversing C's one original source event transiently restores the original B `f3f4` leader at some depth, yet C final move b3a4 persists. This is a source-interventional intermediate **root candidate** effect but does not identify the complete causal route.
- **Third-legal-candidate emergence:** source reversal selects a different legal root move, not the original B or C at some depths. This rules out a misleading two-move causal narrative and expands dynamic support.
- **Some depths return to C:** leader converges although score/average differences persist. Does not mean internal state or value equivalence.
- **Unrecognized move encoding, nonlegal root move, source/StageA/TT/cold drift:** HOLD; no invented strategic content.

[Ten adversarial synthetic tests](../harness/test_c3x_029_p42_r20_source_native_legal_root_candidate_transport.py), [read-only original R20 native workflow](../.github/workflows/c3x-029-p42-r20-native-legal-root-candidate.yml), first triggered [#42554911743](https://github.com/WhoSia/C3X/actions/runs/42554911743). Do not proclaim PASS without native logs, verified ZIP/member SHA and original rights gate.

**Novelty ceiling:** Matching an intermediate UCI chess move to source computation is still not the final central scientific problem. Need actual source-level multiple-path/ancestor cause *plus* independent, predeclared genuinely useful adversarial future-chess rationale with held-out transport. This experiment only prevents false candidate-support inference in that more difficult causal/semantic link. Original source and failed historical CI remain immutable; GitHub human WhoSia, Actions read-only, Notion semantic truth, Drive raw-byte custody unverified.
