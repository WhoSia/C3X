# Executable Lineage Rules

C3X executable history is tracked as a relation:

```
scientific stage
↕
upstream identity
+ C3X delta identity
+ build environment
+ runtime constitution
+ output / receipt identity
```

No layer substitutes for another.

## Required distinctions

- upstream commit/tag != built binary;
- patch SHA != semantic equivalence;
- successful compile != valid instrument;
- valid instrument != scientific result;
- scientific result != cognitive/mechanism identity beyond its licensed scope.

## Historical continuity

C3X previously recovered an exact historical Stockfish runtime from an exact-commit GitHub Actions artifact and verified byte identity against a frozen binary SHA. Future RCs should make that recoverability deliberate rather than accidental.

## Current transition

The repository bootstrap precedes G9.4-P12.
P12 will be the first stage allowed to materialize the new byte-exact TT-read patch lineage here.
