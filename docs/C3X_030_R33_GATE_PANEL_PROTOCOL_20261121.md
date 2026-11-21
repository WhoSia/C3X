# C3X 0.30 R33 — Early-return interventions on fresh games

Use TWIC 1671, with one position per game, a deterministic ply
checkpoint and round-robin event-family sampling. Cap the panel
at 64 before looking at the engine. Exclude known R26–R32 game
and board overlaps plus the sampled prior event families. Keep
the 32,000-node single-threaded R31 configuration and clear
search state between every run.

Observe direct non-PV search children of the same-position
singular-verification call. A target naturally reaches and takes
child futility, at input depth 1–5 and ply 2–5, under a cut node.
Keep both strata according to whether null move would be
eligible on falling through to the next check. In each position
take the smallest nonnegative futility-floor slack over beta in
each stratum, breaking ties by first invocation in the run.
Use only the untouched trace to choose. Seal its event identity,
root candidate and pre-intervention values before applying any
intervention. Treat positions without an eligible target as
coverage outcomes.

For each target, replay unchanged, suppress futility only, and
suppress both futility and null-move entry. Keep the search window,
TT and move history at entry fixed. An intervention touches exactly
one invocation in one process. In the null-ineligible stratum,
blocking null too is a negative control and should reproduce the
futility-only execution. Require observer-only agreement with the
R31 executable and repeat every selected arm. Measure actual
null/board work, immediate return, enclosing root-move probe
and candidate return, then the final move. Treat interruptions as
unobservable intermediate scores and report them. The coverage and
effect counts describe this selected panel, not human players or
the prevalence of the complete R32 causal chain.
