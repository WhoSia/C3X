# C3X 0.29-P36/R2 — Source-Integrity Failed July and Preregistered March Fallback

Date: 2026-11-05 KST. This fallback is sealed **before seeing any March chess games, move selections, engine scores, or explanation outcomes**. The July attempt did not pass the prior source-integration gate and may not count as a successful cohort.

## July original-source integrity verdict

GitHub Actions [41956963985](https://github.com/WhoSia/C3X/actions/runs/41956963985): all 5 legal-history fixture tests PASS, original official July file retrieved from `database.lichess.org`, then downloaded bytes FAILED published checksum verification. Official listing [sha256sums.txt](https://database.lichess.org/broadcast/sha256sums.txt) lists July 2026 SHA256 `e93b3ded55d463ff6839c06b42b740dc1d725145f7f4da460172a3cf84041a8b`; actual returned original ZIP member `lichess_db_broadcast_2026-07.pgn.zst` size 24,535,400 bytes SHA256 **`714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c`**. Original payload decompresses successfully into 171,942,676 bytes of plausible 2026-07 Lichess broadcast PGN. Root cause (stale checksum vs content substitution / archive revision) is unresolved. It remains `QUARANTINED_SOURCE_DIGEST_CONFLICT`; do not silently rewrite expected checksum or admit it as primary independent science.

The only downloaded July file was used to investigate format/bytes; **no July game selection or Stockfish model scores were produced**. The failed CI artifact itself is preserved [here](https://github.com/WhoSia/C3X/actions/runs/41956963985/artifacts/13383686969), including the contested source bytes for audit.

## Controlled fallback selected before game content

Use official **Lichess broadcast March 2026**, fixed URL `https://database.lichess.org/broadcast/lichess_db_broadcast_2026-03.pgn.zst`; official checksum `1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc` from the same [checksum listing](https://database.lichess.org/broadcast/sha256sums.txt). This choice is based on original availability, past Drive filename absence and expected smaller file, not engine results. March is an earlier month than the July candidate and must not be called temporally prospective; this is **pre-outcome, source-separated exploratory intake** only.

Apply **exactly the identical frozen rules** as P36/R1: eligible first 1000 complete standard games, min 60 full-game UCI plies, valid metadata, fixed root after ply30, deterministic eight minimal SHA256 identities (fixed tag+full move history), no reranking after outcomes and no engine calls during source freeze. Do not use the quarantined July content to tune filter/threshold or event selection.

Check overlap with original C3X 0.18 sixteen games, subsequently 0.28 64 cohort and independent event families. DO NOT claim independent heldout until all lineage gates pass. Preserve full original March corpus raw bytes and manifest to Drive on actual source verification PASS. If March SHA mismatch too, STOP new-source selection and investigate archive/checksum discrepancy, rather than trying multiple months looking for a favorable sample.

Purpose: the first durable game-independent test of **legal reply-conditioned chess consequence predictions versus Stockfish score/PV and simple plan JSON**, not more network instrumentation or posthoc cherry picking.
