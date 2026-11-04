# C3X 0.29-P31 — Five Original Monographs, Causal/Planning Authority, and a Legal Chess Rebuttal

Date 2026-11-04 (KST). Status: **primary-source selected-chapter close reading, five PDF custody updates, newly executed rule-law chess counterexample.** No new native Stockfish value runs, no source-independent game outcome and no proof of a novel causal mechanism.

## A. Library state and publication identity

Acquired five actual PDFs from Research OS `00_INTAKE — Literature Radar`, confirmed title/edition/author on their PDF pages rather than trusting initial filename, checked SHA-256 and page counts, and moved originals (preserving file IDs) to `11_BOOKS — Canonical Monographs`. Post-move metadata verified. Zero remaining missing in the **previous C3X four-item exact-title queue**. General Research OS 00_INTAKE still contains other paper, duplicate and unidentified HOLDs.

- Bratman (1987), *Intention, Plans, and Practical Reason* (Harvard University Press), Drive 1UbRXai7booxjmeLbUonZlV7jjDqBsVun, SHA256 55b2d2e549bef06517a44d32412fd7d93d12d02609ea3a303f3ef9dcc99a388f, 224 PDF pages.
- Lipton (2004), *Inference to the Best Explanation*, second ed. (Routledge), Drive 17pkgXiMnAw9TLEIaUqikEJB3AFM-i7NZ, SHA256 ac16e7a88e9f31cb3744045acf420a2823ddad407d948b2e476deabaa7b30d1f, 232 PDF pages. **Extractor returns corrupted font encodings; physical page 5 imprint confirms 2004 2nd edition, page 8-9 contents, page 10 preface visually inspected. Text-level exhaustive reading is therefore HOLD and no unsupported full-text claim can be made.**
- Halpern (2016), *Actual Causality* (MIT Press), Drive 1fbqvXOAZpYGKRJ_NAqBtCxBmqgnixU0r, SHA256 ffdde93613fdda52934e1922b332c8bacff49dea81de363a5a2afcf14c452214, 240 PDF pages.
- Pearl (2009), *Causality: Models, Reasoning, and Inference*, second ed. (Cambridge UP), Drive 186bJjGkA5vWjFMX9jOZiaNQRDZaHMDwt, SHA256 0c1e7bd1676260feb5ec909839b01f1ff16538febfe23755192e565895202e4c, 487 PDF pages.
- Sloman (2005), *Causal Models: How People Think about the World and Its Alternatives* (Oxford UP), Drive 1DwXMY6rvopsN4NKhBC63lamP495v860M, SHA256 2482418713b5ade77309a6421cb7b3bf30053d0693134c6f128ed94dda0a8f94, 218 PDF pages.

## B. Distinguish primary-source authors and our extrapolations

### B1 Bratman (1987): intention is not an arbitrary opportunity

**Source:** Preface and Introduction discuss future-directed intentions and partial plans as inputs to ongoing practical reasoning, constraints on reconsideration, and coordination across time. A merely possible path is not by itself evidence of an intention or a persistent policy. Relevant inspected physical pages: source PDF pp. 11–28 (introduction), 56 (conditional planning), 93 (historical rationality).
**Our C3X extension:** Avoid anthropomorphically calling a legal tactic "what Stockfish intended." Predeclare a *contingent policy mapping opponent replies to legal own moves*, and test whether its outcome/value is stable through further play. Stockfish internal causal attribution is separately identified with genuine search-source interventions.

### B2 Lipton (2004): fact, foil, bad contrasts and selection

**Source:** Actual visually inspected 2nd ed. contents: chapter 3 *The Causal Model* with "Fact and foil", "Failed reductions and false differences", "Causal triangulation"; chapter 5 *Contrastive Inference*; chapters 8–9 "Explanation as a guide to inference" and "Loveliness and truth". Preface visually confirms improvements to contrastive explanation and to the role of explanation in inference. **Do not claim line-by-line reading of the 232-page original: machine-extracted glyphs are corrupt.**
**Our C3X extension:** In source chess, merely giving contrasting board properties is not sufficient when the root preference is unstable, and explanatory “goodness” should not be confused with objective action value or human transfer.

### B3 Halpern (2016): actual cause is model- and situation-relative

**Source:** Chapter 2 §2.2 defines actual causality for causal setting (M,u), including AC1 actual occurrence, differentiated AC2 counterfactual clauses, and AC3 minimality. Chapter 4 §4.4 discusses how (non-)causality may change when models gain additional variables. Chapter 7 §7.1–7.2 addresses explanations relative to epistemic contexts and partial explanatory power. Inspect PDF around pages 34–38, 128–132, 198–206.
**Our C3X extension:** Do not equate source-observed plan availability, a conditional policy certificate, and actual engine choice causation. A reliable causal claim needs an explicit structural model over engine search events (e.g., root score window, TT writer/reader, move ordering), specified interventions and observed before/after outcomes. Adding mediator measurements can change the claim; hold claim authority to the verified causal graph.

### B4 Pearl (2009): action/intervention is not observation

**Source:** Second-edition contents chapters 3–4 distinguish causal effects, actions and policies; chapter 7 §7.1–7.2 grounds structural counterfactuals. Chapter 4 discusses *conditional actions and stochastic policies*. Selected text chapters/TOC read; no claim that the book licenses direct person-style explanations of a chess engine.
**Our C3X extension:** Chess root move do(a) (changing board state) and engine instrument do(root-order / TT) are **different interventions**. Neither can stand in for the other without an explicit cross-level causal bridge. Game-history-complete board state is needed for true state identity; standalone 4-field FEN is insufficient.

### B5 Sloman (2005): invariance alone is not cause

**Source:** Chapter 3 explicitly contains the section "Not All Invariance Is Causal" (PDF p.39). Chapter 5 distinguishes observing from acting, and chapter 7 covers "Deciding by Causal Explanation" (PDF p.94). In discussing decisions, Sloman emphasizes that choosing an action changes which causal consequences arise and cautions against relying on correlations without causal structure.
**Our C3X extension:** A plan that persists under many legal replies may be robust, but not automatically the engine's cause for preferring a move. Robustness is a potentially desirable feature of a strategy, not a verified mediator for move choice.

### Collision in research meaning

The five works jointly push us to distinguish:
(1) legal possibility, (2) conditional policy/future plan, (3) plan value under adversarial best response, (4) search-process actual cause, (5) useful fact/foil communication.
All are established philosophical/technical topics. A C3X scholarly contribution, if it exists, must be *demonstrated in real chess* through better verifiable policy consequences and independently tested explanation performance than matched baselines. We should not present this synthesis itself as a field-first theorem.

## C. New executable real-chess negative control (P31)

Historical Lichess standalone FEN, 0.16 P4 case 8, **source-outcome-exposed development** (not a new heldout):
`2k2r2/pp1rp2p/1bp1b1p1/4p1Pn/4P2P/1PP2P1B/P1K5/R1B2N1R b - -`

Source 0.17 historical native Stockfish root-order receipt reports bestmove `e6h3` in original order vs `h5g7` under reordered condition. This is **archival source** from `c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json`, not a new SF run.

Executed original P22 authenticated C3X Go chess legal law, using Board.Legal/Board.Do, newly enumerating reply fans for each distinct candidate (commands `GO111MODULE=off go test -count=1 -v *.go` in local directory with Go source unpacked):
- World A: `...Be6xh3` captures the white bishop, leaving black bishop on h3. White has exactly **20** legal responses. Only legal reply `Rh1xh3` (UCI `h1h3`) removes that black bishop immediately; it remains on h3 in **19/20** branches.
- World B: `...Nh5g7` leaves the white bishop on h3. White has exactly **24** legal replies. Following **20/24** replies, black still has legal `...Be6xh3` to capture that original white bishop on its next move. Exactly four white bishop relocations eliminate that *same particular* future capture: `h3g4`, `h3f5`, `h3e6`, `h3g2`.
- Full fresh locally re-extracted historical Go package with this test **7/7 PASS** (six original Go tests plus the new probe). GitHub `tools/p31_archived_case8_conditional_bishop_plan_test.go` separately records a replayable test requiring that archived Go source; it is not self-contained in public GitHub.
- The 19/20 and 20/24 frequencies are counts of legal reply choices, **NOT probabilities**, independence samples, or values. All-response universal survival is false in both candidates: the single `Rxh3` reply defeats A's bishop-survival plan, four relocations defeat B's delayed exact-capture plan. The plan predicates are intentionally different, so their fractions must NOT be compared as if measuring identical payoff or Q.
- Not a claim that one root is better, that the rook recapture is optimal, or that root-order sensitivity identifies plan causation. Actual utility, quiescence threats, exchange value and conditional plan robustness at greater horizons remain OPEN.

**Scientific finding:** A true tactical effect ("capture bishop now") may conceal immediate recapture, while a deferred objective can remain legally possible but fail under specific opponent counters. Descriptive presence, future reachability, universally guaranteed objective and net minimax utility are separate. This is a real-rule chess rebuttal to unqualified P29/P30 narration, not new engine-value confirmation.

## D. Prioritized next research, beyond gate accumulation

1. **Actual engine evaluation** on this exposed development case, candidate-restricted fixed/search-depth time windows, repeated root order and *complete history if accessible*, with exact controls for terminal state and PV. This can check robustness but cannot be scored as independent heldout.
2. **A single strong strategic Q:** e.g., verified net material after forced one- and two-reply tactical lines **plus board-utility effect**, not just capturing or preserving a bishop in isolation. Compare candidate A/B on their independent reply universes and same utility model. Note the risk of SEE and pin/check adjudication.
3. Run a **simple foil-aware plan JSON baseline** and engine+PV versus full C3X proof-carrying account; if these perform comparably on prospective independent games, reject extra C3X complexity.
4. Preserve paper-ready negative instances: robust board fact with no stable source preference, feasible plan with adverse opponent reply, and explanatory statement that does not distinguish actual foil.
5. Do not claim scientific novelty, real-game performance, AC2 actual-cause status or exhaustive book reading without the respective empirical and source checks.

## E. Current operational verification and stop rules

All 5 PDFs are under `11_BOOKS`, exact file IDs persisted, metadata readback successful. Miller 2019 remains in `10_PAPERS` from P30. Prior C3X missing exact-title list is now zero; non-C3X intake HOLDs unchanged. Experimental legal outcomes P31 newly run, native engine experiment NOT newly run, GitHub Actions for P31 Go test NOT run because original archived Go source is intentionally nonpublic. The future 0.29 research process should now emphasize native chess evidence rather than incrementally adding only metadata gates.
