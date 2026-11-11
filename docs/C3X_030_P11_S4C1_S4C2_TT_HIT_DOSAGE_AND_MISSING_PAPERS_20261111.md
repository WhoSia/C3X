# C3X 0.30/P11-S4C1–S4C2 — Single TT Hit Is Insufficient in Development; Same-Binary Source-Hit Dose and First Ancestor Context

**Research date:** 2026-11-11 KST. **Chat index:** C3X32. **Software version:** C3X 0.30 retained. **Decision provenance:** D1 native TT event causal attribution priority. This is an experiment, not a confirmed TT entry→ancestor→root strategy causal explanation.

## 1. Why S4C was necessary

[P11-S4B actual native mask success](C3X_030_P11_S4A_S4B_ORIGINAL_NATIVE_TT_SITE_MASK_AND_SHAM_20261111.md) physically masked **repeated hits** to one preselected depth-one chess position key; 3/6 two-run root decisions changed relative to a same-binary sham. Because a function-local counter exists separately for each `search<NodeType>` template instantiation, that prior patch did **not** isolate a *single* hit event. Different engine builds also cannot conclusively establish that an individual event or even exactly two hits were sufficient. This report isolates the **number of source-site hit-signal suppressions per engine process**, not individual TT cell contents or true causal mediation.

The **three previously seen development FENs** and exact target keys were frozen from original S4-A/S4-B SHA-locked JSON **before seeing any S4C outcomes**:
- Queen's Gambit ply4, target key `4160624996999542926`
- Sicilian Najdorf ply4, target key `288240010984383972`
- English ply4, target key `2688154765401883805`

All experiments pin **unmodified upstream Stockfish16 source** commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, with independently compiled modified variants; `Threads=1`, `Hash=16MiB`, `Skill Level20`, `UCI_LimitStrength=false`, `Use NNUE=false`, two consecutive search commands per experimental arm, each `go nodes 12000` requested. Actual nodes and depths differ after intervention and are not assumed exactly matched.

## 2. S4C1 — exactly one matching native TT-hit signal per process

[S4C1 source patch](../harness/c3x_030_p11s4c_single_hit_patch.py) defines **one namespace-scope `std::atomic<bool>` shared across all Root/PV/NonPV instantiations** and changes `ss->ttHit=true` to `false` only on the **first qualifying** `ply==1` and `posKey==preselected key` condition in a process. Logs that exact contact along with `(ss-1)->currentMove` raw parent stack identifier and search depth. **The parent stack identifier by itself is not a measured child→parent→root valuation chain.** Later matching hits have unchanged TT-hit signals. The same patched engine binary runs both irrelevant-key sham and target condition.

[S4C1 actual native GitHub CI #42975239331 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42975239331); 8 synthetic contract tests pass. **18 actual native searches, 216,249 actual nodes** (3 FEN ×3 arms ×2 searches). Each target was physically changed **exactly once per process**; each sham had zero physical changes. Unmodified baseline and same-binary sham selected identical moves, scores, depths, native nodes and PVs.

**Observed primary negative result: exactly one matching hit change caused `0/6` root bestmove changes** compared with sham, although raw source contact was verified. This is a narrow null outcome in previously seen positions, not proof of universal necessity of multiple hits. The byte-sealed source JSON SHA256 is `fdb582510d7b415fbf4b9a917c7abfacdddb220a1af79d52137b9c7ffd19a05a`; original Actions ZIP SHA256 `6b8e979da133019dec0fe7e3afd0ff8ed2ae3829037d725ffae9a699702c6d72`. [Original S4C1 evidence ZIP sealed in Drive](https://drive.google.com/file/d/1FS5Pgw4xirADsK6KYbYRvgya6ASuiS9X/view).

## 3. S4C2 — strict SAME-modified-binary dose experiment

To remove cross-compiled-binary differences, [S4C2 original source patch](../harness/c3x_030_p11s4c_dose_patch.py) uses a single **process-global `std::atomic<unsigned>`** hit count shared across all search templates. The original TT probe/store instructions are preserved, and the one modification is to set `ss->ttHit=false` for matching key/ply hits with ordinal strictly less than runtime-frozen `C3X_S4C2_LIMIT`. The selected key and full original source JSON SHA remain fixed in advance.

**Six arms per FEN**, each with two consecutive real native UCI searches:
1. **Upstream**: original untouched Stockfish16.
2. **Sham**: same patched engine with an irrelevant 64-bit key and a large suppression cap.
3. **Zero**: the same patched engine with the real target key but allowed suppressions 0.
4. **One**: the same patched engine with allowed suppressions 1.
5. **Two**: the same patched engine with allowed suppressions 2.
6. **Unbounded practical**: the same patched engine with allowed suppressions 10,000 per process (not proof all possible visits >10K); only first **8** physical suppression events are emitted to stderr, so 8 is an **observed lower bound** for this arm, not the total suppressed-event count.

[**S4C2 actual native CI #42975829335 SUCCESS**](https://github.com/WhoSia/C3X/actions/runs/42975829335) with 8 independent fail-closed tests, **36 real Stockfish16 searches, 432,459 actual nodes**. Original/sham/zero match exactly on selected root bestmove, measured nodes/depth/score/PV across all 6 separate trials; physical masked events are 0,0,0 and exactly one and exactly two as preregistered for the 1/2 arms.

| Target FEN | Original/sham/zero first→second root moves | 1-hit root changes vs sham | 2-hit root changes vs sham | 10K cap (8 logged) root moves | 10K cap root changes |
| --- | --- | ---: | ---: | --- | ---: |
| Queen's Gambit ply4 | `b1c3 → b1c3` | **0/2** | **0/2** | `e2e3 → b1c3` | **1/2** |
| Sicilian Najdorf ply4 | `c2c3 → f1c4` | **0/2** | **0/2** | `f1c4 → f1c4` | **1/2** |
| English ply4 | `g1f3 → e2e3` | **0/2** | **0/2** | `d2d4 → e2e3` | **1/2** |

**Observed across six paired decisions:** upstream/sham/zero/one/two all **0 root bestmove differences** relative to sham; large-cap repeated masking yields **3 root differences** (one in each developer FEN, all first search). This strengthens a **dose-dependent source-site intervention association**, but **does not locate the true minimal threshold**; 3–9999 masks were not tested and the number of TT hits after 8 is not logged. At one shared patch binary, the effect cannot be ascribed to the different C++ source of S4B vs S4C1.

**Evidence receipts:** Raw original S4C2 JSON SHA256 `522e1d9d466b3552056a163f8bc7cc7f607177106f52724d49b47540db7f6618`. Original Actions ZIP SHA256 `d68e9bfa7aca4684b18a48eeb4ff51d7cd6851216e090d1cdc00699d8a5fa805`. [Original 36-search S4C2 evidence sealed on Drive](https://drive.google.com/file/d/1r8zqrG69gDFrp4U7oP310zXMS5GLmIhb/view).

### Source identity and reproducibility

- [One-event intervention runner](../harness/c3x_030_p11s4c_once_native_court.py) with [single-event source-patch tests](../harness/test_c3x_030_p11s4c_single_hit_patch.py) and [native contract tests](../harness/test_c3x_030_p11s4c_once_native_court.py).
- [Dose runner](../harness/c3x_030_p11s4c_dose_court.py) with [source patch tests](../harness/test_c3x_030_p11s4c_dose_patch.py) and [native receipt tests](../harness/test_c3x_030_p11s4c_dose_court.py).
- CI workflows compile source pinned to Stockfish16 official commit, original source JSON `081ee839...` fetched and strictly SHA-verified before execution, no bot writes.
- S4C original upsteam source `search.cpp` SHA `21b79baa7ce9dabec5b3b9e3854bed9869a1935277247832e550cf395bccd644`. S4C1 patched source SHA `73776be539e0774f3695a2e5b3c104d78b5f06dc2f994fa1cd6ff84a6ea713d1`. The S4C2 original ZIP includes actual patch and binary SHAs; reconstruct from `S4C2_BINARY_AND_SOURCE_SHA256.txt`.
- **54 NEW actual native searches, 648,708 measured native nodes** in S4C1+S4C2. Do not add inherited S4B 18 searches as newly performed. Current S4C2 pilot is a development, not independent prospective confirmation.

## 4. Scientific interpretation and decision

**PASS** (limited): source-site one-hit gating works physically, controls are source-identical across experimental dosage groups, null root change from 1/2-hit gate is genuine, and large-cap targeted hit-signal removal changes final root move in the same three previously observed FENs. This is a **computational intervention effect** at a TT-hit usage site.

**HOLD**:
- A *single original specific TT entry* or individual event uniquely transmits through ancestors. In S4C2 the repeated masks target a **single position key**, not independently validated actual entry values, replacement status or write/read ancestry.
- Full causal child-state→parent-return-value→root-ranking explanation. `parent_move_raw` at source hit is just an observed stack value, **not** a tracked returned score or proof of a parent/ancestor causal mediator.
- A precise dose threshold (3? 4? 8?), effect per unique TT entry or all hit logs (8-event cap).
- Independent heldout game/FEN reproduction; all 3 FENs were known from P11/P11-S4 and selected for instrumentation, and are correlated with the source histories.
- Realized work equivalence, NNUE evaluation effects (`Use NNUE=false`), relative future-plan strategic robustness and human learning improvement.
- Historic C3X 0.29 prospective 7/8 cohort remains **HOLD** and cannot be fixed by redefining eligible games.

**Next D1 experiment decision:** S4/D — in the exact same original Stockfish source instrumentation, record selected hit→search node parent relation, return values, per-root candidate bestValue/rank at multiple safe logging points with logger noninterference tested before claim promotion; then preregister a **new unseen** independent set of chess histories and record all nulls. For a sharper threshold, use one-binary 3,4,8,16 hit caps only if those dose levels are frozen before outcome inspection; the current pilot must not be treated as a blinded confirmatory test.

## 5. Literature acquisition and source-custody update — 2026-11-11

**New source in Drive**: [Gadwal, Greer & McCalla (1993), *Tutoring Bishop-Pawn Endgames: An Experiment in Using Knowledge-Based Chess as a Domain for Intelligent Tutoring*](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view) is now a **36-page author-manuscript original text**, confirmed against author-line / ARIES Laboratory / expert-novice strategy graph / tutor model-tracing content and moved in place to `10_PAPERS`; it is **not verified as the final Springer typeset** `Applied Intelligence 3(3):207–224`, DOI `10.1007/BF00871938`. [ResearchGate author-placed text](https://www.researchgate.net/publication/2556833_Tutoring_Bishop-Pawn_Endgames_An_Experiment_in_Using_Knowledge-Based_Chess_as_a_Domain_for_Intelligent_Tutoring) visible with complete main text; ResearchGate page metadata sometimes says 1999 but original publisher DOI/volume confirms **1993**. The earlier owned 1991 Gadwal UMRAO is a different conference paper; both retain separate original Drive IDs. This source explicitly distinguishes expert and novice plans with advice-language strategy graphs and optional feedback—**do not conflate validated tutor architecture with chess-engine native search causality**.

**Only remaining exact-original acquisition issues**, with legal pathways checked; do NOT imply access restrictions are bypassed:
| Priority | Work / exact version | Present evidence and legal/free path | Status |
| --- | --- | --- | --- |
| 1 | Björnsson (2024) *Chess and explainable AI*, ICGA46(2):67–75, DOI `10.3233/ICG-240256` | [Official journal](https://journals.sagepub.com/doi/10.3233/ICG-240256), restricted. Reykjavik University corresponding author contact `yngvi@ru.is` publicly on publisher metadata; request accepted manuscript or institutional access. | **Final original full text not verified** |
| 2 | Bratko & Kopec (1982) *The Bratko-Kopec Experiment: A Comparison of Human and Computer Performance in Chess*, *Advances in Computer Chess* pp57–72 | [Original Elsevier chapter metadata](https://www.sciencedirect.com/science/article/abs/pii/B9780080268989500097), restricted; legal library/interlibrary loan. [Free *Computer Chess Digest* 1982/83 **updated experiment**](https://www.chesscomputeruk.com/Computer_Chess_Digest_1983_9Mb.pdf) is **held but NOT equivalent to original chapter**. | **Exact chapter still missing** |
| 3 | Herbeck & Barth (1996), *An Explanation Tool for Chess Endgames Based on Rules*, ICCA19(2):75–82 | [Publisher volume 19(2)](https://journals.sagepub.com/toc/icga/19/2) restricted; [Scribd publicly indexed text](https://www.scribd.com/document/712057415/icg-1996-19202) provides article text preview with page/figures but open PDF download and rights not verified, so not preserved as original. Ask author/library/permissions. [Chess Programming Wiki method summary](https://chessprogramming.org/Endspiel). | **Authorized original PDF unverified** |
| 4 | Demura & Kaneko (2024), *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA46(2):40–66 | [Official restricted journal](https://journals.sagepub.com/doi/10.3233/ICG-240255); [Tomoyuki Kaneko official publications](https://www.graco.c.u-tokyo.ac.jp/~kaneko/papers/index.html) verifies exact paper but supplies DOI only; publicly listed author contacts `demura@game.c.u-tokyo.ac.jp`, `kaneko@acm.org`; request accepted manuscript. 2023 Japanese shogi game workshop paper is **different work**, not same version. | **Exact final full text unverified** |
| 5 (version audit only) | Gadwal et al. (1993) exact **typeset journal** version | [Springer DOI](https://doi.org/10.1007/BF00871938) publisher comparison or institutional copy; **author manuscript contents already owned** [Drive](https://drive.google.com/file/d/1iRfADIUxHmiVD4vOEVsaTAZw2ivYtFcy/view). | **Text acquired; typeset version not compared** |

**Not a missing work anymore:** Gadwal et al. 1993 *research content*, Seidel1994, Guid2013, Silva2020/21, etc. Accessible original paper-count and categorical holdings must be separated from typeset-edition verification and author-manuscript custody.

All source documents are distinct from P11/S4 native engine evidence. Unrelated historical `00_INTAKE` duplicate/illegible and source-version HOLDs remain untouched.
