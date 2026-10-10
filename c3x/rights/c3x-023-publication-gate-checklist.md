# C3X 0.23-P0 — Release-Evidence Boundaries and Research Reproduction Checklist

**Scope: all C3X 0.11–0.23 chess evidence pipelines; 2026-10-10. Not legal advice.**

For every prospective upload to GitHub, OSF, Zenodo or any public issue, check **the real bytes** not the filename. Obtain source-specific licence from the actual publisher, not a secondary dataset mirror. Preserve original archive SHA, original URL and collection date. Distinguish facts, selection rules and public domain chess geometry from publicly downloadable but restricted PGN *collections*.

## Primary verifiable sources

- TWIC official: https://theweekinchess.com/twic — archive explicitly states **free for personal use only; all rights reserved**, contact Mark Crowther for reuse. Before permission, **do not redistribute zipped TWIC collections, original full PGNs or reproducible full score lists**. Selected FEN/short UCI strings are a separate publication-review question; not automatically whitelisted.
- Lichess official: https://database.lichess.org/ — puzzle database CC0; chess broadcast PGNs specifically CC BY-SA 4.0. Keep licences separate. For BY-SA material preserve attribution, licence URI, changes and applicable ShareAlike conditions; third-party rights and privacy still require care.
- Stockfish official: https://stockfishchess.org/about/ — GPLv3. Any modified binary released must be matched to reconstructable **exact modified source** with license compliance. Distinguish patch-only source publication from binary distribution, inspect included neural nets if any, do not infer all harness files automatically inherit engine copyright.

## Machine gate

`tools/c3x_023_rights_preupload_gate.py` classifies selected file payloads by **content**:
- original PGN headers and multi-move sequences (particularly TWIC);
- ZIP nested PGN or embedded moves (read contents, fail closed when cannot inspect);
- unknown binary objects, full original data versus authored analytic summary;
- malformed or absent provenance per payload.

Explicitly request one of the audited categories: `P0_AUTHORED_CODE`, `P1_SOURCE_POINTER`, `P2_AGGREGATE_SUMMARY`, `P3_LICENSED_DATA`. **TWIC source full PGN/ZIP category is always HOLD until documented permission**. Ambiguous derivatives are `MANUAL_REVIEW`; a scan PASS does not constitute legal permission. *In GitHub Actions `if: always()` upload steps*, ensure that failure logs and manifests cannot include raw source material. Instrumentation stdout can leak FEN or move source; audit logs too.

## Previous history review

C3X-0.22 P2 historical artifact actions #38047000932 and #38050910527 selected TWIC FEN4 and source played UCI, not full PGNs; their selected derivatives have **REVIEW_PENDING** and should not be falsely described as rights-cleared. Raw TWIC ZIP never intentionally uploaded by those pipelines; historic action logs, zip members and Git commits still require retrospective byte-level review and potential retention cleanup if necessary.

## Legitimate replication under restricted-source access

Publish exact issuer/source URL, content SHA256, source selector code and binary/source patch manifests, deterministic seed, scientific aggregate endpoints, and *empty or synthetic fixtures*. Independent researchers can acquire the TWIC source in accordance with its terms or obtain separate permission and replay the same extraction. If access is blocked, be candid that the restricted-source replication may not be fully available to all, and prioritize Lichess CC0 and CC BY-SA compliant public alternatives for broad reproduction.

Human approval is required before claiming TWIC derivative release permission or before publishing full original chess source materials.
