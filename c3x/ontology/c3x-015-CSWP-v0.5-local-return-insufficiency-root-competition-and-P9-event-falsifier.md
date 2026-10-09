# C3X 0.15 — CSWP v0.5: Local-Return Insufficiency and Root-Competition Provenance

**Scientific status 2026-10-09:** proposed source-specific operational distinction, based on actual C3X 0.15 P7/P8 original Stockfish16 trials. NOT an established general chess theory or new abstract mathematics. C3X 0.15 remains OPEN. C3X 0.16 NOT OPEN.

## 1. Exposed source location does not uniquely explain final root choice

Let a frozen world be the complete original TWIC game root, original SF16 source/build and search policy. Two factors:
- source SEE arm S in {OFF, ROOT_OBJECT_SEE_UNMASK};
- a distinct exact physical TT-return intervention R in {IDENTITY, RETURN_ALPHA, BLOCK_ONCE}, with P6S0-preselected full64 key, writer sequence, stored bound/depth, reader alpha/beta and physical slot.

Record not only the final categorical move Y(S,R), but also the **local qsearch target witness** L(S,R): (position full key, ply, alpha/beta, TT value, stand-pat/inCheck status, considered move, child return, beta/alpha response, target qsearch return). An aligned L is an observation of a source **event**, not the complete engine state.

### Proposition 0.15-P8.1 — isolated local return is not a sufficient function of final root move

For TWIC R2 world #2 under the exact BLOCK_ONCE TT treatment, both SEE OFF and SEE ON run the same recorded target-key qsearch:
- full-key 0x3dd7beae5d6596d5; ply4; alpha130/beta131; original TT return14;
- checked-node qsearch legal move native encoding391; recursive return173; beta-fail-high; matched qsearch returns173.
Yet Y(OFF,BLOCK)=d1e2 and Y(ON,BLOCK)=d1d2.

Hence NO function g solely of the scalar local target qsearch result (173) can map BOTH of these particular trials to final root moves. Proof by contradiction: g(173) would have to be two different moves. This is elementary mathematical reasoning applied to actual native source traces; **not** a claim that the qsearch return is causally irrelevant, nor that adding the full preceding state cannot restore sufficiency.

A similarly important separate example is #29: exact target qsearch original TT value29, alpha130/beta131, stand-pat29 and first inspected child return -59, three considered candidates and terminal qsearch return29, in both SEE arms under BLOCK. Here both root choices were f3e5. Same categorical root output does not prove identical upstream search histories or a common natural mediator.

### Proposition 0.15-P8.2 — iterative-root switch timing is a distinct evidence dimension

Define the FIRST observed PV-first-move divergence at completed UCI reported iterative depth d as D(S,R) = min{d in 1..12: PV_first(S,R,d) != PV_first(S,IDENTITY,d)} where D=null denotes none observed. (PV events may be associated with aspiration re-search; the last emitted information line per depth is used.)

Actual P8:
- #2 OFF RETURN_ALPHA: depth6; ON BLOCK_ONCE: depth12;
- #29 OFF RETURN_ALPHA: depth4; OFF BLOCK_ONCE: depth12.
- #29 ON RETURN_ALPHA can have an intermediate depth4 PV switch yet retains f3e5 at final depth12.

The delay between a targeted local intervention exposure and final root choice divergence may be horizon- or path-dependent. However D as defined is a **report-based observable**, not a precise causal time-of-first-internal-root-competitor update. Deterministic exact-depth final UCI repeatability and source-observer noninterference are required.

## 2. Explainable state must include root competition, not just a tactic label

A candidate causal concept fiber requires (i) chess legal geometry G; (ii) actual source SEE branch contact O; (iii) full physical TT writer/reader event E; (iv) target-local qsearch event sequence L; (v) root context (prior iterative PV, aspiration windows, TT history, move order, competing root candidates) C; (vi) categorical response matrix Y. The tuple (G,O,E,L,C,Y) is a research *measurement contract*, not evidence of a separate learned chess concept or neural representation.

The source data prove that L-target returned value alone is NOT an adequate state summary. It does NOT yet identify which element of C differed first nor prove a unique causal chain from qsearch to the root. State divergence events **outside the target qsearch** must be traced, compared and intervened upon.

## 3. Proposed next P9 event-specific falsifier

For #2, at the presealed exact TT bypass, intercept ONLY the recorded source qsearch beta-fail-high **break** (value173, beta131, native legal move encoded391, full key0x3dd7beae5d6596d5, ply4) and suppress the break at most once while leaving original move generation, SEE, TT save and evaluation unchanged. Compare against no-op exact-source sham for BOTH SEE arms. In world #29, where the target stand-pat route does not execute this break, the same code must be observationally null; preserve it as a negative control. All native return scores, node counts, PV changes, exposure and absence conditions must be recorded; P8 baseline UCI must be exact. An outcome change establishes a **bounded effect of disabling that one break**, not its necessity in a universal or fully natural-mediation sense. If no root change, the beta cutoff is not but-for necessary for final bestmove under that intervention, though it may affect work/cost.

Without this experiment, do not assert that the observed beta cutoff is the unique local cause of the final root selection.

## 4. Evidence and strict ceilings

- Original P8 native 24 process source instrumented experiment: https://github.com/WhoSia/C3X/actions/runs/37920098035
- P8 GitHub receipt: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P8-native-qsearch-event-and-first-root-PV-depth-24-process-20261009.json
- P8 Drive private ZIP: https://drive.google.com/file/d/15eWG9daEYoa8SY6WaooodR_7H6eBq8X3/view ; original zip SHA256 1f9689868918d80d1eee6966154cf8ce69bc25637c3e602e3f35679ad989d232.
- All P8 native conditions logged 1024 event rows and had extensive omitted tail; complete-suffix absence claims are disallowed. First 100 after-target events and aligned target-key microevents retained in canonical compact JSON, plus truncation counts.
- Original context prediction C1 overall-accuracy 42/64 vs trivial B0 53/64 FAIL is preserved.
- No NNUE learned latent, generalizable chess strategy, complete natural TT mediation, or publisher-source raw archival is implied.

**Court:** CSWP_V0.5_PROPOSED / P8_ISOLATED_LOCAL_RETURN_SUFFICIENCY_FALSIFIED_IN_CASE2 / QSEARCH_MICROPATHS_SOURCE_OBSERVED / FIRST_ROOT_PV_DEPTH_RECORDED / MISSING_FULL_ROOT_CAUSAL_ANCESTRY_HOLD / P9_NOT_EXECUTED / 0.15_OPEN_NO_0.16.
