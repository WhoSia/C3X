# C3X 0.25-P14-P8 — History-Refined Search Abstractions, Actual TT Writer Provenance, and Two-Sided Explainable Warrant

**Formal:** History-Refined Search Abstractions & Certified TT Provenance: Contextual Hash Fibers, Repetition-Aware Quiescence Simulation, Source-Typed Value Bounds & Counterexample-Driven Engine Optimization.

**2026-10-12 verdict:** P14-P8 *actual original SF16 native history difference PASS*, *first-4 × 2 true original same-execution TT writer→qsearch return provenance PASS*, *bilateral possibility/necessity abstraction finite theorem court PASS*; **actual source-certified true chess-score bound HOLD, complete original K HOLD, safe novel search controller HOLD, Elo gain UNTESTED**. First [human WhoSia preregistration](https://github.com/WhoSia/C3X/commit/35fbabe96671d4bb6886b716e69bac2cda7d2567) preceded all P8 native results. Original Stockfish16 git: `68e1e9b3811e16cad014b590d7443b9063b3eb52`. Original SF16 GPLv3. No modified binary/PGN uploaded.

## 1. Real native same-FEN, same-key, same-rule50 history contrast

Original native [CI #38211358123 PASS](https://github.com/WhoSia/C3X/actions/runs/38211358123); original/observer combined [CI #38211438198 PASS](https://github.com/WhoSia/C3X/actions/runs/38211438198). Two development, synthetic but lawful UCI histories:
- `position fen 5k2/8/8/8/8/8/4Q3/4K3 w - - 24 55`;
- `position fen 5k2/8/8/8/8/8/4Q3/4K3 w - - 16 51 moves e2e3 f8g8 e3e2 g8f8 e2e3 f8g8 e3e2 g8f8`.

BOTH yield exactly the original complete FEN `5k2/8/8/8/8/8/4Q3/4K3 w - - 24 55`, full adjusted original Position::key `FA93A6DF698F1317`, rule50=24, and actual depth4 NNUE-off Threads1 Hash16MB `bestmove e1d2`, score `cp 3134`. But *actual original StateInfo* differs: direct position `repetition=0, is_draw(0)=0, has_repeated=0`; repeated path `repetition=-4, is_draw(0)=1, has_repeated=1`. Actual nodes **522 vs 448**. Each cold twice, observer parity with original on every position, full FEN/key/move/score/nodes.

**Mathematical source implication:** for this **two-source-state fiber**, action and displayed score are constant although draw legitimacy and node consumption are NOT constant. Hence key+FEN+rule50 is a sufficient abstraction to factor this PAIR's bestmove, but *insufficient to factor draw predicate or cost*; source execution traces are different even while final choice is stable. Do NOT claim a global key→move theorem, a score disagreement, a TT corruption, or a legal historical reconstructed PGN. The original P14-P7 94 vs 100 same-key different-bestmove remains an independently described prior developmental result, not new P8 validation.

## 2. Genuine original TTEntry::save -> qsearch early return same-run physical provenance

[Original C++ reversible observer](https://github.com/WhoSia/C3X/blob/main/tools/c3x_025_P14_P8_tt_writer_reader_observer.py) records last **ACTUAL overwrite** inside original `TTEntry::save` at each `TTEntry*` with full writer 64-bit key, raw stored value, writer bound/depth and serial; original `search.cpp` executes its unchanged qsearch numeric cutoff and emits the first FOUR events per run from that actual source return. [Independently implemented JS source court](https://github.com/WhoSia/C3X/blob/main/tools/c3x_025_P14_P8_original_source_provenance_court.mjs) retrieves native receipts rather than rerunning Stockfish; [CI #38211885999 PASS](https://github.com/WhoSia/C3X/actions/runs/38211885999). **All 8/8 OBSERVED events** had known last original source writer, same full writer/reader key, same underlying raw original TTEntry value, bound/depth agreement and permitted source-side return predicate. Source returns: **2 lower-side, 6 upper-side** across two histories. E.g., serial39 lower-side value -10145 / beta -10331; serial96 upper-side value 10145 / beta10332. These are source numeric TT values, NOT common true chess candidate utilities. Two cold repeats per case; baseline original/observer parity. The four-event cap is *censored*, not a proof of 100% full-horizon original read events. Independent court [#38211726092 PASS](https://github.com/WhoSia/C3X/actions/runs/38211726092) first established the 8 joins; combined theory court #38211885999 revalidated.

**Boundary:** proving a last physical writer and local reader were associated with the same full key/raw storage on executed runs does NOT establish that the writer's `BOUND_UPPER/LOWER` arose from a sound semantic alpha-beta bound, that its rule50/repetition assumptions remain admissible, that the source record is globally identical across hidden histories/TT generations, or that a natural TT→SEE→root mediator is uniquely identified. The distinction `SourceTTRecord` vs `VerifiedSemanticRange` survives. All undisplayed later events remain unknown.

## 3. Why justification is more than safe exclusion — bilateral possible-world approximation

For a fixed, carefully typed universe of admissible original worlds `K`, distinguish underapproximate actually reachable witnesses `K^-⊆K` from a proved sound overapproximation `K⊆K^+`. A query-specific explanation has two *directions of warrant*:

| Epistemic question | Sound logical test | Status in original Stockfish |
|---|---|---|
| Can candidate w **actually** be selected? | An explicitly source-reachable witness of w inside K^- | Yes, for particular actual observed runs/contexts; not every counterfactual policy |
| Is w **necessarily** selected? | Every world in K^+ selects w | Absent full source-sound overapproximation, ABSTAIN |
| Is candidate w **impossible**? | No world in K^+ selects w | Not certified by these trace records |
| Is the claimed necessary winner **falsified**? | Source-reachable rival action in K^- | Prior P14-P7 94/100 and P14-P6 real interventions refute suitably *specified* universality claims |
| Which further search is **worth doing**? | Additional admissibility and value-of-information / compute-cost model | Open; cannot infer Elo or speed from membership alone |
| Why did this actual execution choose w? | Verified source control/TT writer/reader and root sorting with accurate explanation scope | Bounded descriptive source explanations are feasible |

Source-grounded **existential witnesses** and **universal guarantees** have different proof obligations. In particular, a w in K^+ is NOT evidence that w can actually occur, and a w universally selected in K^- is NOT evidence of necessity. Retain explicit source policy, history, resource budget, tie rules and candidate set in the world type; actual original runs under distinct histories are not magically synchronized paired counterfactual worlds.

[Independent C++17 exact finite court](https://github.com/WhoSia/C3X/blob/main/tools/c3x_025_P14_P8_bilateral_possibility_necessity_court.cpp), [CI #38211885999 PASS](https://github.com/WhoSia/C3X/actions/runs/38211885999): 5 small abstract execution worlds, 992 valid `K^-⊆K⊆K^+` triplets, 2976 designated candidate queries; correct underapprox potential certificates 1152, upper impossibility 352, upper necessity 26, lower refuted necessity 1884. Deliberately wrong direction rules generated **576 spurious possibility** claims from K^+ and **868 spurious necessity** claims from K^- (total 1444 counterexamples). These elementary set-theoretic principles are not new general theorems, and no original Stockfish full K was enumerated. Their scientific value lies in architecting a faithful, non-binary Explainable Stockfish justification language.

## 4. Compositional search abstraction: current action is not the only target

A source abstraction `π:S→O` is **query-relative**. For actual deterministic action `A`, source draw predicate `D`, resource trace/cost `C` and next state transition `T`, there are DIFFERENT proof obligations `A=f_A∘π`, `D=f_D∘π`, `C=f_C∘π` and `π(T(s))=π(T(t))` for equal π states. Neither an observed action invariant nor valid local TT writer/reader equality implies the other contracts. Previous locally executed P14-P8 16-state standalone C++17 finite court (attached in the conversation) found 0 present-decision conflicts but 32 future-transition conflicts after refining two toy state bits; it was NOT original SF16 transition semantics. Present native pair is more direct: same source key/FEN/rule50, same root move, **different real draw judgment and nodes**. This is a source-grounded contrast requiring different query abstractions.

TT provenance may justify a literal physical account of *what was read from which writer*; it is not itself a justification of *why the score is correct* or *which search should be safely skipped*. An explanatory system can report an actual witness and a contrary possibility, not only suppress moves. Proof-carrying **search intervention rights** are strictly stronger than observationally faithful explanation rights.

## 5. C3X 0.26 milestone — not a version bump for artifact counts

0.26 is **not** justified solely by the P14-P8 native success. Three evidence gates:
1. **TCS THEORY:** source-defined domain and nontrivial **sound local-to-composed semantic contract**, e.g. original TT writer *eligibility* under rule50/repetition plus qsearch/alpha-beta bound transfer to a restricted root question, or a substantial source-proven inability result and sound stronger abstraction; negative controls challenge the assumptions.
2. **NATIVE IMPLEMENTATION:** unmodified or transparently reversible official Stockfish source produces independently verified witness/counterexample, observer-disabled parity and legal/history/mate regressions; first-four-event source join is a meaningful step but not full contract.
3. **INVENTION:** a source-reachable **usable typed certificate/explanation producer** or substantive verified conditional engine search controller, not an always-abstain harness. For research version 0.26 we should require benefit in explanation correctness or genuinely measured fixed-budget compute, without claiming engine playing strength.

Earliest plausible **P14-P9–P14-P10** if all three gates actually pass; no automatic stage/time promotion. For an advertised **0.26-Elo-stronger engine**, add independent preregistered clock-matched color-swapped paired matches, same NNUE/cores/hash, uncertainty/SPRT and genuine improvement. Current *actual game count 0; Elo UNTESTED*. Users' aim of stronger chess remains an independent engineering axis, not the definition of all mathematical progress.

Next suggested title: **`C3X 0.25-P14-P9 — Source-Eligible Value Bounds & Bilateral Explanatory Warrants: Repetition-Typed TT Contracts, Counterexample-Validated Score Semantics, Query-Specific Search Refinement & Native Decision Certificates`**. Priority: original source justification of writer-produced TT bound, alternative candidate/possibility witnesses, and a first non-vacuous typed native explanation product; then actual performance.

## 6. Provenance without file/CI fetish

[Actual native original+observer CI #38211438198](https://github.com/WhoSia/C3X/actions/runs/38211438198) [~1.7KB evidence ZIP](https://github.com/WhoSia/C3X/actions/runs/38211438198/artifacts/11728469512). [Independent native readback+finite bilateral court #38211885999](https://github.com/WhoSia/C3X/actions/runs/38211885999) [~1.1KB evidence ZIP](https://github.com/WhoSia/C3X/actions/runs/38211885999/artifacts/11730120463). Prior P14-P7 failure 0/100 source key hypothesis, fixed 94/100 and actual result retained. Prior M3v2/M4/M5 negatives and M6 selective qualification unchanged. Read-only GitHub Actions, human WhoSia author/committer only; original SF16 GPLv3, no modified SF16 binary or copyrighted full PGN. No ceremonial SHA ledgers, no extra engine recompilation for independent analysis.
