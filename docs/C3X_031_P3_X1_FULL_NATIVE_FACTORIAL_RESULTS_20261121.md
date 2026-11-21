# C3X 0.31/P3-X1 — Completed 128-Event Two-Gate Factorial with 256 New Native Stockfish16 Searches

**Source experiment status:** read-only [CI #44895972238](https://github.com/WhoSia/C3X/actions/runs/44895972238) **SUCCESS** (9 source-path negative unit regressions + genuine original Stockfish16 128×2 independent cold processes). **Scientific claim:** a **sequential causal gate interaction within finite engine search**, not a proven TT/history mediator or a source-state sufficiency proof. This is a follow-up on already-exposed P2 cases rather than new independent games.

### Actual full 2×2 physical source factorial

Each source row refers to one of **128 original pre-targeted engine events** across **64 full TWIC1669 games / 25 conservative tournament event series**. F=1 disables **only the targeted futility return**; N=1 disables **only the targeted following null gate**. No board or legal-move mutation and no global pruning disable. The three original cells were physically run and cold-repeated in 0.31/P2 B2. The formerly missing (F=0,N=1) arm has now been physically completed twice for **every original event**, totalling **256 new genuine Stockfish16 native searches**. All 128 event OPEN signatures, source child returned values, original root bestmoves and source-root producers exactly matched the original sham; no changed final recommendation in any of the 128 null-only arms.

| Targeted futility blocked F | Targeted null blocked N | Changed actual Stockfish final root bestmove vs original sham | Original physical source authority |
| --- | --- | ---: | --- |
| 0 | 0 | **0/128** | Original P2 B2 sham×2, exact original R33 physical receipt |
| 0 | 1 | **0/128** | **NEW P3-X1 256 searches**, 128/128 pass, both cold repeats source-parity matched |
| 1 | 0 | **8/128** | Original P2 B2 futility-only physical interventions, single process |
| 1 | 1 | **14/128** | Original P2 B2 futility+null physical interventions, cold repeats ×2 |

This is a **serial, conditional gate interaction**, not two additive independent benefits. With original futility intact, the search exits before the null-move test; every physical null-only target reported `futility=1, null_tried=0, null_cut=0, replies=0`, despite `skip_n=1` as an **assigned, not executed**, treatment flag. In contrast, with futility removed, **64** originally null-eligible events reached the null search; it was tried **64** times and led to **50** actual null cutoffs, with **14** null searches not cutting off. Blocking null on top of futility gave **six** additional *root bestmove* flips, all among the 50 originally observed null-cutoff cases. The other **44 cutoff cases** retained the final root choice.

The six signed physical source events with an incremental null effect, each of the same selected sample and different source context: `P2-013-1`, `P2-021-1`, `P2-041-1`, `P2-052-1`, `P2-056-1`, `P2-058-1`. The **eight** futility-only root flips are one null-eligible and seven null-ineligible source events. The group0 `null_eligible=0` original 64 cells had futility-only vs combined control same final bestmove/public UCI in **64/64**, and the additional physical N-only negative control verified the complete downstream behavior.

For a binary outcome Y(F,N)=1 if the final root move is different from its original reference, this finite sample has `sum Y(0,1)=0, sum Y(1,0)=8, sum Y(1,1)=14`; the sample-wise interaction `sum[Y(1,1)-Y(1,0)-Y(0,1)+Y(0,0)]=+6`. No claims about an average effect over the population of all engine events are warranted from the selected 128. Source events are non-independent within games and tournament series, and intermediate TT/history/search-budget state was not separately swapped or restored.

### Original source evidence / verification

- [P3-X1 original 256 new SF16 UCI + source stderr files](https://drive.google.com/file/d/1ShnKHUjk4E36vzokjxx3JLMuo9HCtMh2/view), **512 raw members**, ZIP SHA256 `ad25b507b17eb7dac2d2f98ea50a9307abe648b3b706941671ba5d211c55a3fb`.
- [P3-X1 exact original 128 target × 2 controls JSON + scope](https://drive.google.com/file/d/1acTfhvlX7vZ7FMSXVeDvSJam29I3TUlD/view), ZIP SHA256 `10985e24ad3bd016839f1e9af3e70973654e0f470141b049501b22f95b09f7ab`. Original JSON SHA256 `370aa71f16f2c577b3fc6234cad67805415c64936ded845200342ded221fb11f`.
- Original frozen pre-treatment event signatures from [P2-B1 Drive](https://drive.google.com/file/d/1oGnINF5rPtjjmaRZimlOodUnFEZpHkh-/view), JSON SHA256 `d364e6ca24599110fa19ac41e19164069a164c15aa396aac6b2833482e3818b1`. Original P2-B2 three earlier arms and true native source logs [here](https://drive.google.com/file/d/1wvWAb7CsZkpbjQTknM4Xfil8AmvC4E7B/view).
- Exact original source-bin SHA256 `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1` and NNUE SHA256 `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b` were verified before new P3 searches. All source events contacted; null-only assigned `skip_f=0 skip_n=1`, real computation ended in futility, no unintended actual null action.
- All files uploaded to private Drive, downloaded and compared to GitHub Actions artifact SHA256/ZIP CRC **PASS**. User GitHub author commits only; Actions read-only with no code writes.

### Scientific next question

The sequential early-return mechanism is now identified **at the software control-flow gate level**. The same source-level root effect can still propagate through child returns, transposition-table writes, history counters and changed iteration/node allocation; **none of those actual intermediate states have been independently fixed and restored**. The next intervention must distinguish their post-treatment values while holding all other reachable state fixed; a source-pruning gate toggle does not itself establish a minimal causal search-memory abstraction.
