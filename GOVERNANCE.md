# C3X Repository Governance

## 1. Ambition Prior

Within scientifically admissible possibilities, C3X chooses the path with the greatest potential for:
- explanatory reach;
- black-box reduction;
- generalization;
- mechanism discovery;
- new systems and inventions.

Rigor, provenance, reproducibility, and world-contact controls are constraints on ambition, not the final objective.

## 2. One black-box problem, multiple scales

C3X may study search, evaluation, representation, memory, state abstraction, or world-model behavior at different levels. These are not independent prestige projects. Each branch must reduce uncertainty about the same long-run black-box problem.

## 3. GitHub is executable authority, not scientific sovereignty

A commit, tag, workflow PASS, benchmark PASS, binary, or release does **not** promote a scientific claim.

Scientific promotion requires the Research OS / Notion authority path.

## 4. Main branch rule

`main` is the canonical executable history.

Commits should be atomic enough that:
- the exact source state is recoverable;
- failed engineering transitions are legible;
- an RC can be tied to exact bytes.

Do not rewrite published RC history.

## 5. No hidden outcomes in Git history

Do not commit:
- sealed keys;
- private/unblinded outcome bundles;
- pre-authorization target results;
- API secrets;
- private provider credentials;
- large transient logs.

If an experiment needs such bytes, use Drive or transient Actions artifacts according to the scientific protocol.

## 6. No large-runtime dumping

Git is not the C3X data room.

Do not commit:
- engine binaries;
- NNUE networks;
- tablebases;
- large ZIP capsules;
- historical runtime packs;
- bulk PGN corpora.

Store manifests, hashes, source deltas, and small fixtures instead.

## 7. Patch-overlay first

Until C3X becomes a sustained independent engine fork, preserve Stockfish as an explicit upstream dependency:
- bind an exact upstream ref;
- verify pre-patch identity;
- apply a reviewable C3X delta;
- bind post-patch / binary identity.

Do not vendor a full Stockfish tree merely for convenience.

## 8. Commit != Court

Engineering facts belong in Git.
Scientific meaning belongs in the Research OS.

If a commit changes a scientific estimand, rival ecology, evidence class, or authority target, the corresponding Notion mainline must change too.

## 9. Failure is first-class

Do not "clean up" failed builds, invalid instruments, null probes, or superseded patches in a way that erases why they failed.

Preserve the minimal provenance needed to distinguish:
- scientific failure;
- instrument failure;
- runtime incompatibility;
- obsolete implementation.

## 10. Release-candidate rule

An executable C3X RC requires at minimum:
- exact upstream identity;
- exact C3X source / patch identity;
- deterministic build recipe;
- binary hash;
- regression receipt;
- UCI compatibility receipt;
- applicable corresponding-source / license compliance.

A release candidate certifies an instrument state, not a scientific mechanism claim.

## 11. Research OS runtime

Substantive scientific stages inherit:
- Explanandum Lock;
- adaptive Workshop-Method routing;
- RAVEL adversarial loop;
- authority separation;
- Return-to-Origin;
- permission to repair, shrink, kill, fork, or re-expand.

Private chain-of-thought is not stored. Persist only decision-relevant hypotheses, attacks, mutations, and verdicts.

## 12. Custody

See [docs/CUSTODY.md](docs/CUSTODY.md).
