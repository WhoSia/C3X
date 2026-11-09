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


## 2026-11-09 — Actual pinned source-native R20 result SUCCESS, with source-support ontology correction

Real original Game14 [R20 run #42554911743](https://github.com/WhoSia/C3X/actions/runs/42554911743) **COMPLETED SUCCESS**: original source/test suite, source locked binary, StageA 16-case SHA, unchanged R18/R19 physical source event/cutoff, two original cold runs, all root leaders validated as **legal moves in the original chess position**. The original public artifact #13647425447 was independently downloaded: ZIP SHA256 `67435f72fc893f02fdd9bb8b97e29b7be8dd44a7df00624fdc9bc427f6478869`; JSON SHA256 `8d176b66f1fa92bda13c74cc62939fd9b114912c5d02e29091ec13ad4a820054`.

**Actual native root leaders (UCI, legal original source chess board):**

| Native depth | Original A | Original TT-FIRST B | Original guard C | Exact reversed C |
|---:|---|---|---|---|
| 9 | f3f4 | f3f4 | b3a4 | **f3f4** |
| 10 | b3a4 | e1e4 | b3a4 | **f3f4** |
| 11 | b3a4 | f3f4 | f3f4 | **b3a4** |
| 12 | b3a4 | f3f4 | b3a4 | b3a4 |

Depths 1–8 had no C-vs-reversed-C leader difference. All 12 depth leaders in each A/B/C/reversed-C world were validated against the actual legal chess state; this was not a retrospective assignment of an intended move name.

**Critical semantic correction to the original R20 native JSON:** its field `third_candidate_emergence_depths=[10,11]` used a narrow definition: reversed-C leader differs from *B and C at that same depth*. At depth 11 the reversed leader b3a4 is **the original A leader**, not a genuinely third globally unseen move. At depth 10 reversed f3f4 is outside the simultaneous A/B/C leader set (A=C=b3a4; B=e1e4) and so is a genuine **third simultaneous legal leader** relative to those controls. But f3f4 was **already a known root move at other depths**; no novel UCI move arises outside the global original A/B/C 12-depth universe. Conflating these three notions would make a misleading candidate-set novelty claim.

Created [SHA-locked deterministic source-public semantic court](../tools/c3x_029_p42_r20_reclassify_dynamic_root_support.py), [10 adversarial semantic tests](../tools/test_c3x_029_p42_r20_reclassify_dynamic_root_support.py), [independent reproducible read-only Actions](../.github/workflows/c3x-029-p42-r20-source-support-semantics.yml). Actual [#42555461192](https://github.com/WhoSia/C3X/actions/runs/42555461192) **SUCCESS**, consumed *exact* native original JSON SHA above, verified:
- depths outside contemporaneous B/C pair: **[10,11]**;
- depths outside contemporaneous **A/B/C** leaders: **[10] only**;
- depths with a genuinely unseen move across the whole original A/B/C all-depth support: **none**.

The semantic correction's original downloaded ZIP #13646609767 SHA256 `f12c396296e9752c97ca35b56d03fb22b19e331e08f76881c1a1a38ba67de605`, member JSON SHA256 `b4541eaa8d6779d737aaedc0d681984b7bec8031bb5a9a03d2caeb95b3f2009b`. Both native and semantic source artifacts have been downloaded, content inspected and checked independently; [human-authored dual receipt and exact source event scope](../evidence/C3X_029_P42_R20_ACTUAL_LEGAL_ROOT_SUPPORT_AND_SEMANTIC_RECEIPT_20261109.json).

**Scientific inference:** The R18 single original cycle-alpha return reversal temporarily shifts intermediate legal root preference through a nonlinear A/B/C candidate competition: at depth9 it matches original B; at depth10 it chooses a simultaneous alternative f3f4 not leading either original A/B/C; at depth11 it agrees with A rather than B/C; depth12 it recovers original C b3a4 although numeric search states remain different. This is **physical computational action-preference sensitivity**, not evidence the move's strategic chess value is increased by these draw-score artifacts. Source state, actual root candidate competition and chess-contingency meaning must be bridged, not conflated.

No native outcome was fabricated, source/privacy rights were checked and all historical failed runs / original R18/R19 root artifacts remain preserved. Original Game14 is postselected and NNUE OFF, and no prospective independent chess-strategy evaluation PASS exists.
