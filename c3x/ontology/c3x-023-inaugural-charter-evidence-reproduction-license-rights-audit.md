# C3X 0.23 — Rights-Aware Chess Evidence & Reproducible Search Causality: Source-License Provenance, Native-Operator Mediation, Releasable Minimal Witnesses & Independent Move-Choice Transfer

**C3X 0.23 ACTIVE • authorized user activation 2026-10-10 • first source+methods charter**

## Why a new generation?

C3X0.22 demonstrates native Stockfish16 source-exact TT first-reader suppression, specific evaluations consumed, failures of simplistic *move-specific* models and different outputs in tournament games vs forceful puzzles. A scientifically stronger 0.23 must jointly solve TWO non-substitutable problems:
1. Correctly isolate the native *operator chain* TT score assignment vs cutoff, SEE threshold and actual king-safe recaptures → iterative candidate survival → final bestmove, including negative controls and out-of-ecology falsification.
2. Release reproducible evidence **without claiming permission to distribute a source just because it is publicly downloadable**. A rights-aware proof/replication packet has source-specific eligibility, licence, original URL, byte SHA, transformation lineage, verbatim content footprint, player privacy, sharing scope and explicit holds.

### First-party sources inspected (2026-10-10)

1. **TWIC The Week in Chess** official archive https://theweekinchess.com/twic explicitly says: "free for personal use only. All rights are reserved." Contact Mark Crowther (official archive lists email `mdcrowth@btinternet.com`). No general public re-use grant for its bundled PGN/ZIP has been verified. **RAW_REDISRIBUTION_HOLD**: do not distribute TWIC #1656/#1664 ZIP or entire PGN/collection, substantial replicated score lists, or public derivatives that might reconstruct its compiled database without explicit permission or a documented expert-reviewed exception. Small selected FEN/uci fragments require separate case-by-case assessment, not automatic public licence.
2. **Lichess puzzle database**, https://database.lichess.org/ — database page explicitly says general open exports under **CC0**. Individual puzzle source is an open research/release alternative, with original-source ID, dump dated SHA and appropriate attribution for scientific traceability. Verify other rights (individual player identifiers, linked GameUrl) before distributing personally identifying content.
3. **Lichess broadcast PGNs**, same official database page says **CC BY-SA 4.0** for the broadcast games *in particular* (not CC0, despite top-level open data banner). Preserve credit, licence link, ShareAlike obligations for adapted contents and indicate changes; independent code/data licences can remain separate if not a derivative of the broadcast collection. Document potential event/third-party rights and licence applicability before mass redistributing.
4. **Stockfish**, official https://stockfishchess.org/about/ and https://github.com/official-stockfish/Stockfish (GPL v3): a modified C++ *binary* may be redistributed only in accordance with GPLv3, supplying appropriate notices/licence and corresponding buildable source or compliant offer/pointer. The repository has Python analysis harnesses and original source **patches**, distinct from a complete derived Stockfish distribution; document obligations and exact source overlay chain and commit before releasing a compiled binary. Do not assert the entire C3X repository is automatically GPL-licensed or automatically unlicensed without provenance.
5. **FEN/chess move facts**: factual nature may limit copyright in isolated moves, but **collection rights, substantial extraction, contracts and country-specific database rights vary**. Treat any release of reconstructed TWIC chess positions/full move lists as needing distinct counsel/permission audit; do not equate 'fact' with blanket publication approval.

This is a workflow legal-risk audit, **not a legal opinion or final legal clearance**.

### Standardized release gate

For every file/entity, store:
`origin_url`, `original_file_sha256`, `original_access_date`, `asserted_owner`, `licence_text_url`, `licence_evidence`, `retained_licence`, `contains_TWIC_original_or_substantial_record`, `contains_personally_identifying_player_data`, `transformation_recipe_sha`, `literal_source_text_fraction`, `redistribution_authority`, `permission_document_ID`, `release_decision`, `machine_verifier`, `peer_review_required`, `rerun_instructions`. For uncertain fields default `HOLD`, no optimistic PUBLIC.

**Release tiers**
- `P0_PROCEDURE_PUBLIC`: authored algorithms, selectors, instrumentation code, scripts, deterministic pseudocode and test fixtures, without bundled restricted source.
- `P1_SOURCE_POINTER_PUBLIC`: original URL/issue/date + independently verifiable SHA of unavailable source, explanation of how a licensed investigator can fetch under source terms; no raw content.
- `P2_RESULT_MINIMAL_REVIEW`: aggregated metadata, per-game IDs/nonreconstructive summaries, synthetic examples and targeted native log fragments after rights/privacy audit. Do not automatically include TWIC FEN or move strings.
- `P3_ORIGINAL_SOURCE_PUBLIC`: only when appropriate permission/licence and downstream restrictions are documented; TWIC is **HOLD** pending permission.

**Absolute workflow gate**: no automation uploads raw TWIC PGN or full mainline into GitHub artifact; hash and rights-manifest checks must run *before* `upload-artifact`, including failure paths and logs. For files already shared, audit historic public commits and artifacts, retention/exposure and scope; do not falsely claim historic artefacts were legally cleared.

### Scientific P0–P4

P0 **Provenance/rights matrix and threat audit**: source inventory, terms verification, rights classifications including uncertain selected derivative FEN/labels, source/license citations and patch-chain source.
P1 **Native operator witness audit**: TT-used/cutoff and see_ge true site traces, sham/forced-site contact, exact C++ source correspondence.
P2 **Minimal publishable causal witness**: reconstruct native engine without shipping TWIC; independently verify code/experiment SHA and separate source authorization.
P3 **Independent multi-ecology falsification**: risk-stratified CC0 puzzle vs BY-SA broadcast vs permission-cleared TWIC, prespecify effect/hypothesis and exact UCI outcomes.
P4 **Paper-ready reproducibility package**: verifiable negative claims, actual independent audit, licence file and notices, publication method and preprint safeguards, reviewer checklist.

### Candidate manuscript

**Source-Exact Search Interventions with Rights-Aware Evidence: Reproducible Causal Explanations of Chess Engine Decisions** — possible methods/data governance paper. Another chess decision mechanism paper is still conditional on strong prospective success. Do not claim novelty, external peer review or accepted publication without a full literature audit.

### Historical commitment

0.22-P2 TWIC #1656 exact choice M1 scientific FAIL; 0.22-P2-R1 TWIC1664 M2 54/64 vs M0 54/64 and 0/10 actual switches predicted: FAIL. April 3/3 existence forecasts are weaker distinct claims. F19.5, K4 0/4, January J2/J3/J4, CPP224/PAG prior negatives remain. These historical failures are NOT re-opened or rewritten by 0.23 activation.
