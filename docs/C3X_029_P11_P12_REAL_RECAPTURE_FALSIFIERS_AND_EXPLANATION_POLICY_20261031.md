# C3X 0.29-P11/P12 — Explanatory Quantifiers and Real-Research Return Edge
2026-10-31. Scientific problem: can a short contrastive explanation reliably specify what a player should do against alternative opponent moves rather than merely rationalize a preferred root move?

## Inherited REAL negative data (not newly measured)
C3X 0.27 P3 original WSL-native-validated P2B supplied exactly 18 canonical legal root states from 72 arm copies/9 root pairs. Full-universal immediate recapture was FALSE in 18/18. Nonempty opponent-capture-only conditioned immediate recapture TRUE 15/18; 3 FALSE. Positive-rank comparison development cases42/43 both TRUE on both candidates and hence offer zero preference discrimination. Negative index99 had distinct statuses; cannot select 99 post outcome and call confirmatory. This explicitly disproves any claim that a capture-conditioned universal policy proves all-opponent-move robustness or generally ranks near-equal root moves. See docs/C3X_027_P3_NATIVE_BRANCH_LOGIC_CERTIFICATES_20261019.md and docs/C3X_027_P3_IMPLICATION_THEOREMS_ARCHIVE_REUSE_20261019.md.

## P11 falsifiable claim
Given a declared COMPLETE legal reply domain R and an independent collector's validated set of legal responses T(r), each stated property P_i determines allowable response subset A_i(r). The strong simultaneous explanation claim
FORALL r in R, EXISTS ONE t in intersection_i A_i(r)
holds iff each intersection is nonempty. Source-contract implementation tools/c3x_029_p11_finite_contingent_claim_checker.py returns one common witness per reply or the first explicit refuting reply, with abstentions for missing domain, unknown values and no properties. Counterexample P and Q individually true by DIFFERENT moves yet conjunction false is an implemented regression test; no original chess-engine run. Tool certifies relative to declared legality, not original legality itself. A candidate comparison needs a certificate for candidate A and a refuter for competing candidate B under the SAME semantic predicate and scope; otherwise ABSTAIN. A captured-only claim cannot be promoted to all-legal without collector coverage proof.

## P12 short explanation sufficiency
Given readable response feature z and legal/joint-valid action sets A(r), a single concrete action (or independently verified executable action schema) can be chosen based only on z iff each feature-cell intersection of A(r) is nonempty. tools/c3x_029_p12_feature_abstraction_refuter.py computes witness or a collision. Important subtle counterexample: three reply sets {a,b},{b,c},{a,c} have pairwise intersections but EMPTY three-way intersection. Therefore an explanation's insufficient feature partition is NOT always refutable with just two opponent replies. The code reports collision_pair=null and a three-reply cell count rather than inventing a false pairwise witness. This is a consequence of elementary set intersection, not C3X novel theorem; concrete chess source applicability awaits verified action-schema semantics. Paired independent legal responses after different opponent replies may require different legal UCI moves; raw UCI equality across different boards must not be assumed meaningful.

## Actual artifacts
tools/c3x_029_p11_finite_contingent_claim_checker.py
tools/test_c3x_029_p11_finite_contingent_claim_checker.py
tools/c3x_029_p12_feature_abstraction_refuter.py
tools/test_c3x_029_p12_feature_abstraction_refuter.py
.github/workflows/c3x-029-p9-public-receipt-regression.yml (read-only CI enhanced)
All changes committed in separate human-associated GitHub connector calls. CI execution itself is not independently verified in this turn.

## New experimental gate, not yet executed
1. Declare candidate pair and claim vocabulary independent of evaluation outcomes, with nonvacuous property and full history-aware legal domain. Freeze before chess outcomes are opened.
2. Construct R(s,a) via independent chess legality; ensure all moves and history included and record whether domain is all_legal or capture_only.
3. Check opponent replies and property P_i on source-verified states with common t. If a property is undecidable at given horizon, ABSTAIN, never coerce UNKNOWN to FALSE.
4. Compare two candidates under identical P, horizon, legal scope and coverage; only call it contrastive if one universal claim is proved and rival refuted by a legal counterexample. This DOES NOT prove why Stockfish selected A.
5. Evaluate on disjoint new games against scores/PV and generic concepts with coverage-matched risk; human comprehension separately.
6. Release no original private PGN/FEN/TT keys; preserve license bounds. No newer native results or human effects claimed.

## Verdict
PROVEN (finite mathematical): joint witness obligation; triple-intersection counterexample.
HISTORICAL NEGATIVE (real C3X): all-reply recapture 0/18 and nondiscriminative case42/43.
NEW IMPLEMENTATION: proof/refutation APIs + regression specifications.
UNTESTED: original P3 JSON input replay, new chess-native case, CI green, generalization, educational transfer.
