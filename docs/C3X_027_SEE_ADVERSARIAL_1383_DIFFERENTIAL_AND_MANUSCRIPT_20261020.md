# C3X 0.27 — Adversarial Stockfish16 SEE Differential Boundary Audit
Date 2026-10-20. Manuscript-bound engineering evidence; causal mediation and formal source equivalence remain HOLD.

## Actual executed results
Main GitHub Actions success https://github.com/WhoSia/C3X/actions/runs/39344590480, frozen original SF16 revision 68e1e9b3811e16cad014b590d7443b9063b3eb52, original Position::see_ge unmodified, read-only UCI oracle patch. Fixed-seed random 960 comparisons reproduced with 0 Boolean discrepancies (444 nonzero native internal occupied outputs). Newly authored adversarial legal FEN fixture suite produced 423 comparison pairs with zero Boolean discrepancies (133 nonzero native occupied). Total 1383 executed differential comparisons, observed mismatches 0.

## Audited specific fixture coverage (numbers of threshold-move comparisons)
pinned_knight 9, pin_rook 45, xray_rooks 45, bishop_xray 45, king_retake 45, en_passant 45, promotion 72, castling-board OTHER ordinary moves 36, knight_exchange 36, rook_exchange 45. 10 board categories. Native oracle CASTLING MOVES were excluded 18 times (nine per kingside/queenside), because the stockfish native/Chess960 UCI encoding was not normalized; **do not claim castling move equivalence**. Artifact parser examined every recorded exclusion: all 18 are only CASTLE_UCI_ORACLE_ENCODING_UNSUPPORTED. Fixtures are intentionally hand-constructed and not scientifically independent game samples. 'Pinned' and 'xray' are fixture labels, not internal loop branches proved executed; nonzero occupied alone does not establish pin or x-ray branch coverage.

The source-owned audit artifact was downloaded and JSON fields manually inspected: artifact 12230985926, files C3X_027_SEE_DIFFERENTIAL.json, C3X_027_SEE_BOUNDARY_DIFFERENTIAL.json and original oracle manifest. Actual suite and workflow: tools/c3x_027_see_boundary_differential.py and .github/workflows/c3x-027-see-native-differential.yml. No native raw Stockfish binary delivered to user.

## What is not yet proved
- The port's piece attack logic and pin filtering are not formally equivalent to original Stockfish for every FEN and occupancy. 1383 PASS observations do not certify source equivalence.
- The oracle exercises external `see_ge(move, occupied_output, threshold)`, where the occupied input parameter is overwritten by original Stockfish on normal moves; externally preloaded occupancy is not a distinct start-state parameter in this source. This important semantics must be preserved.
- Castling direct special-move checks are missing, and special move policy `type_of(move)!=NORMAL => 0>=threshold` should get an exact oracle comparison after UCI encoding normalization.
- The engine causal study remains absent: exact TT reader→natural SEE event activation/consumer→root in prospectively disjoint games still not measured.

## Manuscript Results revision
A source-level differential oracle was built around the unchanged Stockfish16 static-exchange routine and compared with a separate Python implementation. The first fixed-seed run agreed on 960 input triples. We extended this with 10 hand-constructed types of board stressors, including pins, sliding-piece x-rays, king recaptures and promotion/en-passant configurations. Of 423 executable additional comparisons, none disagreed on the returned Boolean. Eighteen direct castling comparisons could not be interpreted by the UCI adapter and were excluded rather than counted as passes. A zero-disagreement tally is a useful engineering check but can conceal unactivated internal branches: a position designed to contain a pin is not proof that the pin-filtering condition was reached during that SEE call. Further work requires per-branch native instrumentation and reproducible event-specific counterexamples before claiming complete conformance or transfer to causal explanation.

## Next executable work
1. Correct the castling representation and compare source's special move threshold semantics, then explicitly tally native SEE interior branch coverage (pin rejection, king path, x-ray revelation).
2. Extend trial corpus with deliberately selected crossing gates and property-based differential counterexample reduction.
3. Reuse the frozen 0.23 native TT/SEE two-factor harness on a source-disjoint game cohort, first making literal test target registration and rights checks. No natural causal mediation claim before that execution.
