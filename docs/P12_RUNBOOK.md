# G9.4-P12 executable runbook

## Scientific boundary

This runbook certifies the **instrument** only.

It does not authorize interpretation of MASKED outcomes as chess knowledge, representation, or cognitive mechanism.

## Targets

- frozen dev commit `5062aee519a1ba262d472d8ab139851ced56573e`
- Stockfish 19 commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`

## Modes

- `NATIVE`: unmodified TT-read semantics.
- `SHAM`: identical search semantics plus telemetry.
- `MASKED`: the three admitted search-mediation TT reads are converted to canonical miss packets; writers remain real.

The post-search ponder TT probe is intentionally not masked.

## Gate order

1. verify exact upstream commit/blob identities;
2. materialize patch;
3. build baseline;
4. build patched engine;
5. UCI smoke;
6. baseline = NATIVE semantic identity;
7. NATIVE = SHAM semantic identity;
8. SHAM telemetry nonzero;
9. generate exact diff + SHA manifests;
10. only after later exact-world tranche commitment may MASKED science open.

## First scientific runtime

- Threads=1
- Hash=64
- internal Syzygy disabled
- Clear Hash before each arm
- fixed-node budget

## Failure labels

- source mismatch → `UPSTREAM-IDENTITY-FAIL`
- compile failure → `PATCH-MATERIALIZATION-FAIL`
- default/NATIVE mismatch → `NATIVE-NONINTERFERENCE-FAIL`
- NATIVE/SHAM mismatch → `SHAM-NONINTERFERENCE-FAIL`
- zero SHAM TT engagement → `ENGAGEMENT-FAIL`

No such failure is a chess-mechanism result.
