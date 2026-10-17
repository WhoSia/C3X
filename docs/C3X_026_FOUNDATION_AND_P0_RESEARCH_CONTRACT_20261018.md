# C3X 0.26 — Causal Foundations of Strategic Choice: Counterfactual Affordance Geometry, Minimal Distinguishing Reasons, Search–Strategy Disentanglement & Verifiable Human Understanding

Status: OPEN / THEORY AND IMPLEMENTATION DEVELOPMENT. No claim of causal or human-validation success.
Date: 2026-10-18. Canonical predecessor: C3X 0.25 (historical name unchanged).

## Central problem
For a position s and meaningful legal rivals a,b, determine which evidence-supported properties of their possible continuations distinguish them; separately identify whether those properties actually explain a specific search algorithm's choice, whether they support chess-relative merits, and whether an explanation transfers to human decisions.

## Four separately testable layers
1. Search mechanism: interventions on candidate root sets, search order, TT and budgets. Endpoint = protocol-conditional rankings; no inference of objective optimality.
2. Counterfactual strategic affordance: game-legal futures, threat/opportunity and constraint predicates, opponent-policy assumptions and horizon dependence. Define features and transformation invariances before observation.
3. Minimal distinguishing reasons: candidate reason R must discriminate a,b, be testable under legal targeted perturbations, and be checked against rival reasons and negative controls. Minimality is assessed against declared reason vocabulary, not prose length.
4. Human understanding: blinded test of ability to predict a rival's salient reply or evaluate unseen analogues, against score-only, PV-only and unguided baselines. Distinguish comprehension from move quality.

## Formal starting point (hypotheses, not established laws)
Let G(s,a;H,P) represent legally attainable continuation states to horizon H under declared policy/response family P. Let Phi map such states to prespecified strategic predicates, optionally distributions. Compare Phi(G(s,a;H,P)) and Phi(G(s,b;H,P)) with a declared, symmetry-aware contrast functional. Never infer preference merely from positive distance.
Separate hypotheses:
H_search: rank inversion is driven predominantly by protocol-specific allocation/path dependence.
H_strategy: reproducible constraints/opportunities discriminate legal continuations independent of the tested search protocol.
H_mixed: both contribute, with identifiable interactions.
H_null: proposed strategic factors do not outperform legal-PV / score baselines on untouched positions.

## Inheritance, no retroactive renaming
Preserve C3X 0.1–0.25 historical names and all negative findings; 0.25 P10 (53 strict within-arm cp margin sign reversals) and P11 (144 native calls, 72 identical cold-repeat pairs) remain valid diagnostic source evidence, not independent held-out proof or training labels for validation. P11 source SHA256: 18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2. User WSL original-history replay reported PASS 9 and root branches 18. Independent complete game-state/PV legality, move-clock/repetition rights and cross-branch convergence are NOT YET certified.

## P0 scientific gates
P0-A: original JSONL custody and strict unique-arm/repeat identity audit.
P0-B: complete legal board replay with castling, en-passant, halfmove/fullmove clock; compare piece-placement+turn / FEN4 / FEN6 / repetition-relevant history separately. Repeated transpositions must be reported with exact time/node/ply coordinates and compared at matched horizons.
P0-C: derive predicted differentiating chess factors from P11 development cases (e.g. 42,43), explicitly include P10 negative controls (47,99), test opponent reply alternatives and PV transpositions.
P0-D: preregister search-mechanism-versus-strategic explanations and counterfactual legal manipulations before obtaining further outcomes; use untouched event-separated heldouts. Historical source overlap/identity unresolved.
P0-E: pilot blinded explanation transfer against score-only and PV-only baselines; no claim of learning benefit without data.

## Data/statistics boundaries
144 Stockfish calls = 72 repeated arm conditions, not 144 independent positions. Development set comprises nine P10-outcome-selected positions, not independent population validation. No arbitrary feature-distance claim is a causal mechanism. Full search vs locked search may alter allocations; ranking reversal is not objective chess superiority.

## GitHub and Research OS governance
BOT_CONTRIBUTION_ZERO: no github-actions[bot] authored/committed history; no workflow pushes or tags. Actions read-only contents: read. Human WhoSia commits only; verify author and committer after writes. GitHub README succinct research entrypoint; Notion detailed canonical argument; Drive source/raw data custody with hash/readback. Never delete failures; no new branch for this launch.

## Success vs failure
An OPEN 0.26 denotes change in the central question, not proof that strategic geometry, search–strategy links or improved human understanding are achieved. If P0 finds only search implementation artifacts, record the null and continue rather than retrofitting the claims.


## P0-A/B execution receipt — 2026-10-18 (native user WSL and uploaded independent JSON)
The user ran `C3X_026_P0_P11_FULL_STATE_AUDIT.py` under Python chess 1.11.2, script SHA256 `cfc746bc080f700e820fd8438cd0a2473efa23dfa6e18a8fd3d34afd25674d88`. Terminal reported `P0_PASS 144 rows / 72 cold-repeat pairs / complete python-chess PV legality`. Uploaded independent audit JSON SHA256 `bf73bd29c1e3aca7631d5c66b605c6409d46cad306f3aee433eb3e4e9777aa09` (7,365 bytes); source P11 SHA256 `18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2`.

Unique arms 72; repeated pairs 72/72. Within first-root two reply-line comparison: board placement+turn 13/72, FEN4 13/72, **FEN6 8/72**. Across first roots: placement+turn 4/36, FEN4 4/36, **FEN6 4/36**. Thus five *comparison arms* with placement+turn/FEN4 recurrence are NOT full FEN6 matches; the remaining eight FEN6 matches are not repetition-history equivalence certificates.
Index 42 Classical Bf8 (d6f8): depth17 within-root board/FEN4 has four matching checkpoints but FEN6 zero; depth19 four board/FEN4, two FEN6 checkpoints. This distinction invalidates unqualified use of the P12 preliminary 13/72 as full-state transposition. Case 42 and 43 sampled between-root comparisons have no match in reported examples; global between-root 4/36 must not be misattributed to these cases.

**Authority boundaries**: exact report validates recorded trajectories only, not full policy reachable state equivalence; FEN6 does not encode prior repetition sequence, and move-number/clock dependencies may separate nominally matching board states. No objective move superiority, causal strategic factor, human learning gain or independently held-out generalization follows. Next: inspect all 5 FEN4-only discrepancies; factor repeated-transposition time/ply opportunities; separate repetition-relevant history; preregister mechanism vs strategic contrasts. Preserve 0.25 lineage and P10/P11 negative controls.
