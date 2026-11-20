# R30 — Targeted follow-up on the previously exposed R29-031 reversal

The observed-reply arm nominated probe 233 in attempt 14, under
Kg7, matching the originally searched Bxc6 move. Withholding the
whole local move hint left the scout return at 1947 but changed
the next PV return from 1934 to 1952. The native trace shows a
singular verification search at the probed position only in
the untreated route. This is a post-observation mechanism test.

Compare untouched, full local hint mask, withholding the TT argument
at only the main move picker, and skipping only the admitted singular
verification branch while leaving the TT move and value intact.
Use fresh executions and the same 32,000-node limit. Gate both
refined interventions by the identical probe ordinal and verify
their pre-treatment signature. Record actual entry into each gate,
frozen scout and PV return paths, candidate-leader update and final
move. Trace-enabled sham and restore must match the R29 build.
Use this case to investigate mechanism only, with no claim that any
isolated route generalizes to other positions.
