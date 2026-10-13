# C3X Explain I10-P1 — Two Real-Chess Rival Explanations: Source-Native Outcomes, Replayed Alternatives & Fair Comparator Boundaries

**2026-10-13 verified development CLOSE, not Track-A graduation.** [Prospective two-game preseal](EXPLANATION_I10_P1_CHESS_CASE_WORLD_CONTACT_PRESEAL.md), commit `d2fd9903` before new native runs. [Official pinned source native Actions #38332952446](https://github.com/WhoSia/C3X/actions/runs/38332952446) **SUCCESS**, 40/40 test PASS, original SF16 (SHA `68e1e9b3811e16cad014b590d7443b9063b3eb52`), cold depth-9 unrestricted MultiPV3 scout followed by depth-12 restricted two-move MultiPV2; 2/2 source-original chess positions legally reconstructed; old I9 commentary executed independently on the same source revision. [Development ZIP artifact #11783900801](https://github.com/WhoSia/C3X/actions/runs/38332952446/artifacts/11783900801) SHA256 `91449ec1e1227cb6be1ca2b051ee136c26aea1ede591efe88834e472a343e57d`, internal JSON SHA256 `1afc6f852593be512b1538569b245a17d7945e3850e5296a7382a8221659346f`. [Canonical run receipt](../c3x/receipts/c3x-explain-i10-p1-native-two-real-chess-rival-development-20261013.json).

## Case A: Kasparov vs Topalov 1999 — actual White 24.Rxd4, challenger 24.Nc6+

- Source game: [historical SAN and game score](https://www.chess.com/blog/Eshwar360/the-best-chess-game-of-all-time-garry-kasparov-vs-veselin-topalov-1999), independent [PGN transcription](https://github.com/kerry-huang-nyu/chessRobot/blob/main/kasparov_topalov_1999.pgn). Recorded real 24...cxd4 response checked legal. Pre-move exact FEN `b2r3r/k4p1p/p2q1np1/NppP4/3p1Q2/P4PPB/1PP4P/1K1RR3 w - - 1 24`.
- Unrestricted original scout **depth 9**, ranking: `Nc6+ -4 cp`, `Qxd6 -63 cp`, `Rxd4 -65 cp`; the historical move is **third** in that scout. Pick highest *other* candidate `Nc6+` prospectively, without knowing depth-12 outcome.
- Two-candidate original-depth-12 search, NNUE OFF: `Nc6+ −17cp` versus `Rxd4 −54cp`; gap `37cp`, opponent reply PV `Nc6+ Rxc6 Qxd6 Rxd6 dxc6` versus `Rxd4 cxd4 Qxd4+ Qb6 Re7+` in the original engine's distinct branch analyses (the longer PV is retained in the artifact). **Actual winner in this restricted search is not what Kasparov played**.
- Chess-native checked contrasts: `Nc6+` gives check and is a verified fork/attack on king + black rook d8. `Rxd4` is a capture, and the real game continued `...cxd4`; none of these facts prove the Rxd4 sacrifice was sound or explain Kasparov's cognitive process.
- **Actual preexisting I9 output** from original 4,000-node/ply independent baseline described `Rxd4` as its engine's first candidate and replayed `Rxd4 cxd4 Nc6+ Kb6 Qxd4+ Qc5`. Therefore the P1 depth-12 line **changes the apparent preference**. Budget and restricted candidate set differ—this is *NOT an identified benefit of C3X semantic innovation*.
- The verified I10 output explicitly reports `Nc6+` as preferred on the bounded root pair, surfaces `Rxd4` as the actually played **challenger**, and declines to infer an objective chess proof. C3X source-causal certificate links = **0**.

## Case B: Morphy Opera Game 1858 — actual White 12.O-O-O, challenger 12.Bxf6

- [Public historic record](https://rookhabit.com/en/games/morphy-opera-1858). Recorded real 12...Rd8 checked legal. Pre-move exact FEN `r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R w KQkq - 1 12`.
- Unrestricted original depth-9 scout: `Bxf6 +113cp`, `O-O +81cp`, `O-O-O +68cp`, so the played castle was **third** at first. Challenger was source-scored `Bxf6`.
- Two-candidate original depth-12 search: `O-O-O +249cp` versus `Bxf6 +99cp`; gap `150cp`. Its actual native line after `O-O-O` was `O-O-O Rd8 Rxd7 Rxd7 Rd1`. In the `Bxf6` branch it showed `Bxf6 gxf6 O-O-O Rd8 Kb1 a6`. Source-pinned, both legally replayed, neither declared forced in all possible opponent worlds.
- The actual chess concept behind the first continuation is **rook coordination on the d-file**: castling moves the rook a1→d1 and the displayed PV follows with a capture on d7 and recapture followed by another rook's `Rd1`. This is **human chess interpretation tied to verified moves**, NOT independent causal identification of why Stockfish internally evaluated O-O-O highly. Alternative `Bxf6` instead exchanges a bishop for the black knight and black g-pawn recaptures.
- **Actual old I9 output** from original 4,000-node/ply preferred `Bxf6` by about `6cp` and described `Bxf6 gxf6 O-O-O Rd8 Kb1 a6`; here the depth-12 restricted pair flips ordering. Again: **different depths and root constraints**, so not proof C3X yields better chess decisions.
- I10 returns `ENGINE_SNAPSHOT_PREFERENCE_ONLY` with source atom IDs and Korean readout, all bounded. C3X source-causal certificate links = **0**.

## Fair, rival-grounded comparator table

| Arm | Actually executed? | What it can support | What remains prohibited |
|---|---|---|---|
| Original **I9** (`c3x_explain`) | YES, on both actual historic prefixes with the pinned original engine | Verified SAN/PV/board facts, bounded prose, provenance | Its shallow best root is not chess truth or necessarily the best under deeper search |
| **ENGINE_SCORE_ONLY** source | YES, original SF16 native restricted pair | Rank, cp margin at *depth12*, source PV, lawful candidate set | Human strategy, causal value theorem, matched budget against the independent I9 root |
| **CONCEPT_AND_PV_DONOR_PROXY** | YES, deterministic existing board/tactical concept analyzers, source PV | Verified castling/check/capture, material/proxy count change, plausible chess-language bridge | Not the actual trained **Kim et al. CCC**, not an independently executed LLM |
| **C3X I10 typed judgment** | YES, evidence-bound old I9 atoms rebuilt for fixed pair, original engine and source legality | Play-preserving pair comparator, evidence IDs, uncertainty/authority abstention, human-legible bounded explanation | NO new source-local C3X causal certificate in these cases; NO demonstrated chess strength or pedagogical advantage |
| **Independent CCC / chess LLM + human benchmark** | **NOT RUN** | Strong test of whether warrant-aware explanation really helps | No accuracy, comprehensibility, preference, confidence or superiority estimate presently available |

No paired budget-matched original I9 vs I10 **quality difference** can be estimated from these two different search configs. It would be invalid to score the better deep engine judgment as a gain from C3X evidence semantics. We have confirmed *working* two-rival product contact, legible opposed examples, and a new empirical evaluation target, not a positive semantic-effect estimate.

### Crucial negative that stays

[I10-P0 actual native CI #38331884555](https://github.com/WhoSia/C3X/actions/runs/38331884555): 37 tests PASS, genuine original SF16 build, **0/4 real root decisions, 4/4 abstentions** in original tiny PGN. Its limited selection policy can fail to bring even usable pair rows into the judgment layer. I10-P1 deliberately chooses two public nonterminal historic moments and restricts original-root comparison to the actually played move versus the source-selected challenger. The resulting 2/2 decisions **are NOT representative general coverage**.

## Academic source custody updated

Three papers supplied by user were actually fetched and read in Drive, with metadata-only rename and relocation from `00_INTAKE` to `10_PAPERS — Canonical Literature Commons`, **same Google Drive IDs and byte sizes**:
- Tang & Zheng 2026, `2609.32160v1`, [Drive](https://drive.google.com/file/d/13cg7JKtrPH0K3j6QgTuIaA3d2Zitz5WV/view).
- Deußer, Sparrenberg & Sifa 2026, `2609.37647v1`, [Drive](https://drive.google.com/file/d/1nyhsNdWIb2IBp8aX1jSUZzWpHWgCtoCK/view).
- Gao & Wang 2026, `2609.38850v1`, [Drive](https://drive.google.com/file/d/1FIO-xUrgBYbcgy9FbPalf14zsGKz6Y-P/view).
Theory transfer: typed decision interface *is not* novel causal semantics (Tang & Zheng); empirical calibration/selective risk must be measured separately (Deußer et al.); per-rationale Brier optimization does not directly certify truthful/faithful chess explanations (Gao & Wang). The right future learning target is separate **candidate-pair preference**, **counterfactual certificate admissibility**, **human explanation understanding**, each with independent ground-truth labels and distinct uncertainty calibration. **Do not optimize one as a proxy and relabel as the others.**

## Next genuinely decisive experiment

Compare (a) original I9/stockfish commentary, (b) **actual runnable** Kim-style CCC/LLM at the *same original source packet*, (c) I10 evidence-bound commentary without authenticated C3X certificate, and (d) I10 with an **exactly applicable authenticated C3X source counterfactual certificate**. Use new source-disjoint nonterminal game positions and randomized blinded human understanding after move-name masking with alternative-reply probes and held-out objective reply correctness. Freeze source and prompt/model/retrieval versions. Evaluate claim correctness, coverage/abstention, decision quality, perceived usefulness and after-commentary *new* decision performance separately, not one composite number. Without certificate-bearing examples, the unique advantage over the concept baseline has not yet been exercised, so no 0.26 promotion.

**Final I10-P1 status:** `NATIVE_DEVELOPMENT_PASS / 2_OF_2_ACTUAL_DECISIONS / 0_CAUSAL_CERTIFICATES / 0_HUMAN_RATERS / ACTUAL_CCC_NOT_RUN / I8_HUMAN_HOLD / 0_26_HOLD`.
