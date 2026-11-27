# R36 repository hygiene and retirement audit — 2026-11-27

Baseline main d7dcba4cf8ee7725b9af68007b5bddcfcf226208, full recursive tree not truncated: 3,372 entries, 3,301 blobs, 2,012 code/config files (extension filter), 602 workflow files. Zero byte-identical SHA groups within the filtered code/config inventory. Count does not prove active use. README reduced 367,102 to 5,552 text characters, original exact blob e538b9868a5b57000f1226cb2151f3fc5d28d27c preserved at the pinned historical commit and read back. All 15 principal internal links in new README checked against tree.

## Retirement gate
For every candidate: known original blob / exact bytes, actual incoming imports, script and workflow call paths (including dynamic path cases and old reproducibility runners), document/receipt links, verified raw Drive custody SHA-256 and restored Git blob SHA, checkout/restore test, explicit replacement or archival replay command. Distinguish ACTIVE, DONOR, REPLAY_ONLY, RETIRE_READY, RETIRED. A zero search hit alone is insufficient. Do not sever existing executable workflow dependencies. A historical commit remains immutable; do not rewrite history.

## Concrete results
- 0.14 TT lineage patch is explicitly required by the active P3-B prereg and legacy workflow: DONOR, preserve.
- 0.25/P8 native TT field overlay: active reuse candidate and two old workflows: DONOR, preserve.
- scripts/p22_verify_seal.js: referenced in p22-design and p22-design-r-repair workflows: REPLAY_ONLY candidate; no deletion.
- c3x_g10 package: search found numerous callers and tests, result capped at 25. REPLAY_ONLY candidate group; cannot delete package in isolation.
- Legacy archive folder: https://drive.google.com/drive/folders/1kmsG0DcGLV2qnQLEtVsKqzEcue-q3L1T.
- Downloaded LEGACY_C3X_0.4.0_G6_E1_SOURCE_ACCRUAL_R1.zip, SHA256 2c4f4f91fe1bbb61436b07a25393c746ea381a0a5c21b4acf3d83d8d750df339; source corpus/ledger only, not a code backup.
- Downloaded [SUPERSEDED_P10_R1_PROVENANCE_CLASSIFIER_20261009.zip](https://drive.google.com/file/d/1YIjC0FMUm0ByKz5JAYSelCyKGKTZqjEx/view), SHA256 1e7f23896456a51aab4f50a05557cca28ae1d8dd071f6e5ace22584630db20e4; ZIP CRC all members passed. Member P10_ROOT_CANDIDATE_SOURCE_PATCHER.py, SHA256 2dc36c87af3639e0ffd12498795aee577a5bc432cc33d976fcd781fa92bf2760, Git blob f0ea3d3ac55c11be43ef0e2b30c1e89160ccdbf3 EXACTLY matches current tools/c3x_015_P10_SF16_root_candidate_aspiration_passive_patch.py. However current workflows c3x-015-p10-root-candidate-aspiration-provenance.yml, c3x-015-p11-exact-root-child-return-consumer.yml and c3x-016-p3-exact-TT-writer-reader-2x2.yml reference it. HOLD_DEPENDENCY, not safe removal. Other two archive code members did not match current tree blobs.
- GitHub raw text reads work; local git clone failed DNS. Drive upload accepts a connector-backed file reference; no verified route for arbitrary local newly generated ZIP into Drive was found in this cycle. No new raw-code archive or deletion claimed.

Next: group workflows and source closure by version, isolate obsolete entrypoints, use a source snapshot and exact archive upload/readback, then remove only fully validated groups. Prefer keeping donor and frozen replay layers separate from active entrypoints. This audit is not a complete dependency graph.

Decision: README navigation reorganization COMPLETE; code retirement 0 files deleted, 1 current code file byte-certified already in Drive, but retained due dependencies. Never inflate retirement counts.
