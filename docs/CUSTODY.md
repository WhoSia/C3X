# C3X Custody Constitution

## Canonical surfaces

### Research OS / Notion
Holds:
- current scientific state;
- formal stage names;
- Court decisions;
- theory / rival genealogy;
- authority boundaries;
- methodological doctrine.

### Google Drive — C3X data room
Holds:
- large or private byte artifacts;
- historical experiment capsules;
- source-accrual packages;
- blinded packages;
- sealed results;
- runtime bundles;
- literature index / research notes.

The Drive room is organized functionally:
`00_GOVERNANCE_INDEX`, `01_SOURCE_ACCRUAL_RAW`, `02_BLINDED_ANALYSIS_SAFE`, `03_PATCHES_RUNTIME`, `04_SEALED_RESULTS_COURTS`, `05_PAPERS_REFERENCES_NOTES`, `99_LEGACY_PROVENANCE_ARCHIVE`.

### GitHub
Holds:
- active code;
- patch deltas;
- upstream locks;
- schemas;
- small test fixtures;
- CI / regression workflows;
- RC manifests.

### GitHub Actions artifacts
Transient:
- compiled binaries;
- build bundles;
- noncanonical execution receipts.

### Local WSL/runtime
Working copy only.

## Capsule rule

Old experiment directories that bind scripts + blinded objects + keys + logs + manifests may be archived intact. Retroactively splitting such a capsule into functional folders can destroy provenance.

## Duplicate rule

Same filename and same byte count are not enough to delete an object. Duplicate candidates are quarantined until cryptographic identity is verified.

## Large-byte rule

If a byte object can be reconstructed from:
- exact upstream ref,
- exact patch,
- deterministic build recipe,

prefer storing those small authoritative objects in GitHub and the resulting binary as a transient artifact or Drive release byte.

## Public/private boundary

Never move a hidden scientific outcome into public Git history merely because the repository is convenient.
