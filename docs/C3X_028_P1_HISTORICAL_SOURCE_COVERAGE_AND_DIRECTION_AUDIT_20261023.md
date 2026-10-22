# C3X 0.28-P1 — Historical Source Coverage Matrix and Prospective Intake Gate

**2026-10-23 | DESIGN ARTIFACT ONLY | EMPIRICAL HOLD**

## Scientific objective and stop rule
Test *prospective causal transport* of physical TT-FIRST source suppression and a predeclared single real capture-prune bypass across **64 independently chosen chess games**, including null, ineligible, path-divergent and censored cases. Existing post-outcome Game14 evidence is not a population effect or natural mediation proof.

Stop historical bookkeeping once candidate disjointness can be supported against a documented exclusion universe; do **not** let unbounded identity work displace source-exact A/B/C interventions and E1/E2 ancestor-chain evidence. Conversely, no assertion of complete 0.18–0.27 disjointness from a subset of manifests.

## Actual WSL results reported by operator (not rerun by GitHub)
| Source tier | Evidence | Verified scope | What it does NOT establish |
|---|---|---|---|
| Local inventory | `C3X_028_HISTORICAL_SOURCE_INVENTORY.json`, SHA256 `708955b54fed3265acef546c279b1472020000ed4fcd88a737ad13f309275cfd` | Two searched WSL roots, 427 PGNs, 1266 JSON, 14 JSONL | Universal 0.18–0.27 coverage, archives outside roots, compressed PGN completeness |
| Replayed historical PGNs | `C3X_028_HISTORICAL_GAME_FINGERPRINT_AUDIT.json`, SHA256 `d6056c0b0ebaf39ee522234d0e88c551d17030602d06e97a4e56e1b95f788b72` | 12,013 parsed legal game occurrences; 11,224 distinct SHA256(initial FEN + "|" + complete legal UCI history) identifiers; 581 repeated IDs; 789 extra occurrences | Independently complete past-source register or verified rights |
| Derived JSON field inventory | `C3X_028_DERIVED_SOURCE_FIELD_AUDIT.json`, SHA256 `998a6e2cb60527109ad14a93a865c8d4012fb68b1b13e0974cefd917fa7cf729` | 1170 JSONs with source-related fields, zero read/hash errors | Identity equivalence just from matching field names |
| SHA crosswalk | `C3X_028_SOURCE_SHA_CROSSWALK.json`, SHA256 `de75efd4a218c9857532e536fbf88fbcdfa4185dbdf1fa51c4518d81e694678d` | 2303 SHA-field occurrences match 425 distinct archived PGN-byte hashes | 2303 distinct files/games; game-ID equivalence across legacy schemes |
| G9.2 selected 160 | `C3X_028_G92_CANONICAL_GAME_CROSSWALK.json`, SHA256 `f919347d95ea6e991b6c59f4afaeb9e6c0b8ef62736fdffec11502c0a64dfc42` | 160/160 legal UCI-history fingerprints found among 11,224; 0 within-cohort duplicates | Unstated initial FEN independently proved; all other G9.2 or 0.18–0.27 material |
| TWIC1660 selected 160 | `C3X_028_TWIC1660_CANONICAL_CROSSWALK.json`, SHA256 `368bfd616232a6aa7887ba91ca59a9c799c4cf6d80c32091994b4a95d4c465b0` | 160/160 matches within 11,224, 160/160 standard starts, **zero actual canonical game overlap with G9.2 160**, zero reported errors | Exact rehash of legacy `moves_sha256` producer; entire historical source universe |
| Earlier C3X cohort families, 0.18–0.27 | README and earlier source precommits give **some** named TWIC, Lichess broadcast, puzzle and legacy source categories | Historical references and rights cautions exist | Complete per-version source holdings, canonical ID manifest, or nonreuse attestation |

**Summary:** 320 distinct, specifically identified past selected games are linked to the 11,224-ID scanned inventory, not 11,224 independently verified studies. The historical exclusion universe is useful but **incomplete-by-proof**. `game_identity_sha256` from the TWIC manifest hashes metadata + a move digest, and cannot be compared directly to full-history canonical IDs. Do not reinterpret 0 matches between unlike SHA schemes as distinct games.

## Rights and sources
Earlier `c3x/ontology/c3x-023-P1-independent-licensed-chess-cohorts-and-source-key-aligned-SEE-TT-precommit.md` records a Lichess broadcast CC BY-SA 4.0 strategy, separate CC0 puzzle controls, and **restricted TWIC personal-use originals**. Source licences must be checked for the *specific* new acquisition; a repository's historical licence assertion is not current verification. A puzzle-position source is not automatically a full independent game. Keep private raw PGN, full player headers, FEN and modified GPL engine binaries out of public GitHub artifacts.

## Minimal prospective intake acceptance gates
1. Create a concise 0.18–0.27 **source-family coverage register**: observed roots, historical references/URLs, archived original SHA, existence, parsing, canonical ID coverage, rights, gaps. Distinguish VERIFIED / PARTIAL / UNKNOWN rather than self-attest universal completeness.
2. Resolve or conservatively exclude possible overlaps with *unaccounted* historical game families. If this cannot be established, label the pilot `DISJOINTNESS_UNVERIFIED`; **do not** describe it as the preregistered confirmatory 64.
3. Independently document new rights-cleared PGN originals, byte hashes, acquisition date/source and sampling frame; screen **entire game histories** against known historical canonical IDs and source-family provenance; also consider position-level exposure where relevant.
4. Freeze one legal position per distinct game, deterministic seed and exact source code/versions; preserve full denominators, invalid/excluded/ambiguous candidates, complete initial position and selected move history privately. No engine reads until immutable private cohort SHA and public privacy-safe summary are written.
5. **Existing intake code requires repair before production**: CLI `ALL_018_THROUGH_027_CHECKED` is a user string, not independently verified provenance; `errors="replace"` may mask PGN decoding defects; public/private output currently overwrite without refusal; ensure both outputs can be sealed atomically and checked; insist on source rights evidence rather than arbitrary prose. Changes should be bounded, tested and committed when they unblock legitimate preseal, not as speculative infrastructure.
6. A=OBS, B=physical TT-FIRST source-reader suppression, C=B+at most one actually executed capture-prune guard bypass chosen under fixed all-game source-event priority **without using bestmove outcome**. E1 child entry/return/parent-consumption, E2 ancestor/root propagation. Native actual instrumentation, bounded censor receipts and negative controls are empirical prerequisites.

## Direction/promotion audit
- **Already earned:** reproducible *source-custody and selected-cohort identity mapping* for G9.2/TWIC1660; a limited methodological improvement, not C3X 0.28 empirical elevation.
- **No empirical promotion:** no new independently frozen rights-cleared 64, no verified native A/B/C, no E1/E2 source-to-root transport, no effect denominator or uncertainty interval.
- **Next high-value action:** close identifiable source-family gaps minimally, select new independent data before engine exposure; then switch effort decisively to actual causal tracing. Revisit direction after every significant experimental result, not every additional hash.
- **Stop rule for engineering:** a code commit needs to either close a concrete preregistration risk, prevent invalid data release, implement needed native measurements, or repair a verified failure. Otherwise research and analysis come first.

References: [0.28 official charter](../docs/C3X_028_PROSPECTIVE_SOURCE_GUARD_TRANSMISSION_CHARTER_20261021.md); [existing intake](../tools/c3x_028_wsl_engine_blind_pgn_intake.py); [earlier rights and source design](../c3x/ontology/c3x-023-P1-independent-licensed-chess-cohorts-and-source-key-aligned-SEE-TT-precommit.md).
