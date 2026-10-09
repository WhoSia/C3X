# C3X 0.18 — Rule50 Counter, Fullmove Label, and Historical Repetition Discrimination

**Adaptive mechanistic follow-up.** The new independent sixteen-game history-vs-FEN native court #37983641417 has already shown that recorded FEN-only vs full-original-history root outputs can differ. This is not a preregistered discovery on new games; sample and contrasts are frozen before this finer dissection.

The same sixteen full original UCI move prefixes are replayed with a chess rules validator to compute the exact **halfmove clock H** and **fullmove number N** at each fixed position. Apply the same unmodified Stockfish 16 root-order source intervention and depth12 cold settings to four standalone input classes:

- `C00`: FEN original board + `0 1`, the earlier baseline
- `C10`: same board + `H 1`, halfmove only
- `C01`: same board + `0 N`, fullmove only
- `C11`: same board + `H N`, full six-field snapshot
- `HIST`: actual `position startpos moves <original exact prefix>`, from the already-sealed secondary court

For O and F, cold-repeat C10/C01/C11; C00/HIST are SHA-frozen existing data. For C11, cold-repeat no-contact Z and require exact O/Z six-field UCI equality. Keep all 16 cases; source SHA and prior native JSON SHA must match exactly.

Report separate categorical bestmove and entire UCI-core differences for each factor arm, plus whether C11 reconstructs HIST output. Where C11 differs from HIST, **history beyond the six FEN fields remains observationally relevant**; do not automatically label this as repetition without source-level evidence. If C11 equals HIST, the two clocks may be sufficient for these recorded outcomes, but the specific contribution of halfmove vs fullmove requires the C10 and C01 controls.

All events and results must be sha-hashed, failures retained and final conclusions scoped to frozen SF16 and source-only game state.
