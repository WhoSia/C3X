# C3X 0.27 — P2-C: Strict-Recapture Evidence Gate, Proof Minimization and Human Transfer Protocol

Date 2026-10-19. Official 0.27 title preserved.

## Observed evidence, not prediction
Native P2-B JSON was searched by exact title in connected Google Drive and in mounted conversation container files; no output was found. Existing P11 144-row JSONL and P2-A JSON are readable. Native `python-chess` is unavailable in assistant runtime. **P2-B native PASS/FAIL and all individual strict-recapture results remain UNOBSERVED.** No new numerical H* result.

Actual P2-A `C3X_027_P2A_REPORTED_REPLY_CAPTURE_RESULTS.json`, source SHA 071dee670b0c9f14f845e6a2080f91a0267f6abea6736b8059689e6f48f75487: position 2 shows mixed capture availability; positions 31,42,43,47,52,56,79,99 all 4 context rows have 'at least one generic capture' after both roots' two *reported* opponent replies. This does not prove strict recapture or all-legal-reply claim. Preserve this failed discriminator.

## Exact proof obligations for P2-B (two separate predicates)
q_target after legal opponent reply r: legal original-mover reply t captures the *specific just-moved opponent piece* on r.to_square, regardless of whether r was capture.
q_conditional only on r in {all legal opponent capturing replies}; empty conditioning set => EMPTY_CONDITION not certified PASS. Need piece identity, legal moves, relevant terminal states and source state/FEN. A promotion reply changes moved piece type and must not fail an inappropriate equality check. A castling reply moves two pieces and is excluded from single just-moved-piece simplification.

For U2(a) = forall admissible r exists legal t q:
- PASS: full exhaustive list of legal r, plus at least one legal t witness for every r, with exact board replay.
- FAIL: one legal r, plus exhaustive proof that no legal t on r-board satisfies q. If q means capture of just-moved piece on arrival square, legality of all candidate destination moves can be checked; keep board and declared semantics.
- UNKNOWN: timeout, absent source history, failed invariants, missing r, or any other gap. Do not infer U2 from top-two PV.
- EMPTY_CONDITION distinct from TRUE for q_conditional.
Minimal negative certificate: (source FEN, first root a, legal r, q definition, exhaustive legal t witness-of-absence). Minimality means deleting any *necessary proof component* invalidates the declared certificate. A short {a,r} pointer alone is not a standalone certificate. Minimal positive certificate needs at least one valid t for each legal r; delta compression of shared entries is allowed only with independently replayable decompression.

## Model example for human commentary (not position-specific observed finding)
Only after true contrast is certified, template: 'A는 [구체적인 상대 잡기 수]에 [합법적 재포획]이 가능하지만, B에서는 [특정 반례 수] 때문에 같은 대응이 불가능하다. 이 차이는 [명시한 수순 지평과 응수 범위] 안에서 확인된다. 상대가 [새 응수]를 두면 어떤 기물이 다시 잡힐까?' No case42/43 text can be filled with concrete move labels before legal P2-B native result. Also avoid saying 'therefore A is better' without independent value evidence. Template is a design artifact, not proven learner outcome.

## Prospective blinded human evaluation
Trial conditions on game-disjoint heldout examples: (1) no commentary + board, (2) Stockfish score+PV (budget matched), (3) generic model chess prose with the same displayed information, (4) certificate-grounded concise commentary. Hold chess position, candidate alternatives, reading time and problem difficulty fixed/randomized; randomly allocate across examples with counterbalancing and preregistration.
Primary metric: correct transfer to *unseen* counterfactual 'if opponent plays a different reply' problems. Secondary metrics: factual understanding, choosing between near-equal roots, overconfidence calibration and reading time, factual-error rate. Independent blind legal proof grader distinct from language quality ratings. Require both machine legality/certificate fidelity and transfer benefit before 'human-useful explanatory system' claim. No human participants, responses or learning gains have been measured.

## Runtime and custody
Revised tool `tools/C3X_027_P2B_STRICT_RECAPTURE_H2.py` at WhoSia/C3X commit 7340e329b86d93dd2e42e08e73ee3c7a19391fed; conditional output fields awaiting WSL. Do not require Stockfish engine, just existing WSL python-chess venv and P11 JSONL. User's WSL data not remotely accessible. Source code currently GitHub durable; Drive file custody for new scripts/results not yet verified. No bot contributors, no new branch, do not rename earlier versions. New test is pending, not retroactively PASS.
