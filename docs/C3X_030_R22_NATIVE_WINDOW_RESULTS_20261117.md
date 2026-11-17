# R22 — A root window bounds its own attempt

[Protocol](C3X_030_R22_NATIVE_WINDOW_PROTOCOL_20261117.md). The replay used 28 complete archived Stockfish leaf traces across 14 R21 questions. It reconstructed native move identities, including encodings for castling, promotion and en passant. A full constant-window fail-low produced an upper threshold only when every legal root move was recorded. A beta cutoff supplied a lower threshold from that call's window.

Of 611 recorded root attempts, 335 did not retain the full effective depth, 28 lacked an ordinary window, and four provided no threshold. The remaining 244 contained 67 lower thresholds and 177 upper thresholds. Relative to the last public report at the same nominal depth, 14 repeated a threshold, 205 were weaker, and 25 were incompatible. These comparisons span separate native attempts, where aspiration state and TT state can change. The mismatch is evidence against pooling them as simultaneous bounds on one fixed score.

There was no newly justified strict rank across 162 paired question-depth entries, of which the public output already strictly ordered 142. This is a separate empirical negative from R21's zero usable point refinements. The next native comparison should join a bound to the exact public-producing attempt or run an intervention that fixes the rival state before testing transfer.
