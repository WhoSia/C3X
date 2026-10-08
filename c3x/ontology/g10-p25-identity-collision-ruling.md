# C3X G10-P25 — Pre-Outcome Identity and Collision Audit Ruling

Status: FROZEN METHODOLOGICAL RULING; NO ENGINE OR FULL_CLASS OUTCOME OPENED.

## 1. Evidence question

The objects (a) board-state alias, (b) provenance trajectory identity, and (c) experimental intervention-world identity are different. P25 must measure their divergence while preserving prior P19–P24 freshness exclusions.

## 2. Frozen legacy exclusion

Reuse the exact P19 canonical FEN convention from `tools/g10_p19_source_census.py`:

`canonical_fen(board) = " ".join(board.fen(en_passant="fen").split()[:4]) + " 0 1"`

and SHA-256 over the resulting UTF-8 string. The existing `candidate_sha256` also means exactly this hash. Reusing a historical candidate canonical-FEN hash is an exclusion, regardless of alternative trajectory provenance. Do not modify this definition or silently substitute `board.fen()` with differing en-passant semantics.

The prior P19 acquisition bounds, `ply_lo=12`, `ply_hi=160`, the geometry grid and deterministic source ordering should be reused for any P25 comparison under the inherited acquisition protocol. Note that broad raw PGN collision counts for ply 0–11 can be reported descriptively, but they are not added to the frozen P19 candidate-exclusion rule.

## 3. Three collision tiers (all report separately)

**Tier F: canonical state reuse.** `F = sha256(canonical_fen(board))`. When the candidate F hash is found in historical hash universe or another candidate source, record and apply legacy exclusion. Report source counts and whether the overlap was historical or cross-cohort.

**Tier T: provenance/trajectory reuse.** Record game/ply/position lineage, including stable event/section identifiers and game headers when present. Hash a pre-outcome, canonical provenance tuple; do not treat an arbitrary source-specific identifier as proof of new underlying chess worlds. Tier T is a diagnostic tier, not a reason to re-admit Tier-F-excluded worlds.

**Tier W: prospective intervention-world identity.** Defined only after the frozen candidate move pair and router-derived TARGET/SUBSET/SHAM FENs are fixed. Record board state, ordered move pair, router grammar, intervention family, and relevant BASE protocol identity. W is never consulted to restore Tier-F-excluded worlds. W may be analyzed as a distinct conditional experimental object only inside the frozen supported population.

## 4. Anti-selection guarantee

No FULL_CLASS responses, post-intervention PVs, activation labels, Q0 outcomes, or predicted ACTIVE fractions enter any F/T/W collision rule, source selection, or quota stopping.

If Tier-F legacy exclusion leaves inadequate support, emit HOLD. Never relax source/world freshness because a more refined T/W representation would rescue sample size.

## 5. Charlotte eligibility

The Lichess event group `3hq9MXIq` and Round 9 child `UxSO2MGW` are not the GM-section parent tournament identifier. GM-section PGN bytes, section parent and raw-byte SHA remain unsealed. No inference of identity follows solely from round-name similarity.

## 6. Scientific novelty boundary

The central contribution is not a generic deduplication algorithm. The new testable claim is that provenance validity (source I), executable contrast support (R), and mediator-class response (A) are distinct measurable filters, and that the *selection geometry* induced by those filters changes the scientifically transportable target population. A distribution shift after conditioning on R does not itself establish a causal effect of that selection.

## 7. Development track

A source-audit compiler is complete only after its code actually lands in GitHub and a test run produces an inspectable artifact. Two earlier connector create_file calls were rejected; no audit implementation PASS may be inferred from those attempts.

## 8. Authority

P23 = CLOSED/FAIL. P24 = CLOSED/ADMINISTRATIVE HOLD with zero primary outcomes. P25 = OPEN/PRE-OUTCOME. Q0 = DENIED. Track B's calibration abstention remains binding. Chat Mode only, no GitHub Actions bot-authored history.
