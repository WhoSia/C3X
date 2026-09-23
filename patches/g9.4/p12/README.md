# G9.4-P12 byte-exact patch packet

The canonical P12 implementation is generated deterministically by `tools/materialize_p12.py` against exact upstream identities in `upstream/stockfish-lock.json`.

Final certified implementation commit:
`7236d6576857404d29f6c0b410c3dbec63f49f15`

Final Actions run:
`35907950858` — dual-target SUCCESS.

## Frozen 2026-08-10 target

- upstream: `5062aee519a1ba262d472d8ab139851ced56573e`
- self-contained unified patch SHA-256:
  `df7c72ccf86eb77c838297429b41107854fca96e29cebe355dbeb3f446ad9fe7`
- patched binary SHA-256:
  `84f52946eaea3b86770be5ca45ebe42729c945a76533bd295418310e3b2fd099`
- patch packet round-trip: PASS
- NATIVE/SHAM identity: PASS

## Stockfish 19 target

- upstream: `edb0d9db6731067ec50ce619ff372b463bc4dd5d`
- self-contained unified patch SHA-256:
  `d66a220c2d50b3de8ad215ff7e4752e396de69d3143f1dd4a00e17a7d3e79bb9`
- patched binary SHA-256:
  `6e74024b9e730ffcc8b86caa066ebf8ebae7bc2218bcf9356879116458a76e9d`
- patch packet round-trip: PASS
- NATIVE/SHAM identity: PASS

The full patch bytes + binary + manifests are kept in the canonical Drive RC1 packets, not Git history.

Scientific interpretation of MASKED outcomes remains unauthorized at P12.
