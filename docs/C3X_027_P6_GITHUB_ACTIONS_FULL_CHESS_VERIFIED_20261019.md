# C3X 0.27 P6 — GitHub Actions Full-Chess Revalidation

Date 2026-10-19. Official C3X version unchanged.

## Independently executed CI receipt
GitHub Actions run https://github.com/WhoSia/C3X/actions/runs/39207862972
Commit 79fbda3d5ea6dce9ed8043a049fb684d06eafb01, branch main, trigger push, job verify SUCCESS. Installed python-chess==1.999 package exposing chess library version 1.11.2. Log exactly P6_FULL_RULES_PASS 20. Artifact c3x-027-p6-chess-certificates (id 12165834677) downloaded, ZIP inspected, JSON fully parsed. Raw JSON 128680 bytes, SHA256 f6ffb9cca1fff67ef75600965c8d8612897c9e782cc91507eb18d4a85abd61a4.

## Domain and classification
Twenty fixed root cases: two constructed white-K+rook-versus-black-K tactical roots and eighteen roots belonging to nine previously selected P11 game positions. These nine are NOT a new, game-disjoint independent cohort. Full orthodox legal move generation is from python-chess, with FEN as input; original full game move history and draw-by-repetition are unavailable, so this does NOT verify history-dependent terminal judgments. No Stockfish nor user WSL required.

Root-fixed claim: the root mover can force opponent checkmate within total horizon H plies (counting the first root). Fully evaluated H=1,2,3 for 20 roots = 60 bounded decisions, UNKNOWN_BUDGET=0. In constructed case WK c1 WR b3 BK a1, root b3a3 mate within H1 (TRUE all H). Constructed WK b1 WR c4 BK a3, root b1c2: H1 FALSE (visited edges 1, proof bytes 22), H2 FALSE (2,48), H3 TRUE (13,67). Hence Hstar=3 for fixed root and fixed forced-mate-within-H under frozen FEN semantics, matching but independently replaying restricted P5 rule outcome. The earlier self-implemented KRK scanner counted 19 visited nodes for H3, compared with CI 13; implementation-dependent search cost, not a lower bound.

P11 case42 black roots d6c5 and d6f8: mate-within-1/2/3 FALSE/FALSE/FALSE, H3 visited 5/4, proof 140/108 bytes, conditional recapture TRUE/TRUE. Case43 roots a8e8 and d5f5: H3 FALSE for both, visited 50/44, proof bytes 1580/1388, conditional recapture TRUE/TRUE. Case99 roots d2c2 and h2g2: H3 FALSE/FALSE, visited 47/39, bytes 1484/1228, conditional recapture FALSE/TRUE. Across 18 roots conditional recapture TRUE15 FALSE3, exactly matching earlier WSL P2-B counts. None are source-causal Stockfish preference explanations.

## Architecture decision and open scientific gates
Move chess execution from manual WSL to GitHub Actions (write-only evidence script, pinned python-chess, public main branch push-trigger plus workflow_dispatch, read-only permissions, upload artifact). Bot may run CI but must not commit to source; source author and committer WhoSia. C3X 0.9+ historic FAIL/HOLD remains unaltered.
P6 is a full-rule *rerun on preselected data*, not a new heldout game-generalization test. Pending: securely source disjoint new tactical game positions (avoid post-selection), include source_game_sha256 and actual game histories, compare genuinely interesting goal predicates to subtle decision roots, measure nontrivial proof cost and learner understanding. Hstar is per goal, not a universal explanatory horizon.
