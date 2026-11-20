# R33 — Replay and reporting locked after the 64-position discovery

The untouched panel has 64 positions. Each has an eligible target in
each of the two frozen null-eligibility strata, hence 128 targets.
All 64 old-build and observer-off runs agreed with the observer-on
public UCI and source root receipts. The target is the minimum-slack
one by stratum and first encounter, as fixed before outcome trials.

Replay each target under futility-off and futility-plus-null-off.
Each arm starts a fresh engine, and is repeated in another process.
Require event-entrance identity with the discovery signature.
The event's direct return, null attempt, child move count and native
attempt/producer should be reported separately. If a root probe was
interrupted, leave its score unobserved. Final changes require exact
bestmove discrepancy. Treat all 128 as selected events, clustered by
64 positions. The null-ineligible stratum supplies a control for the
extra null flag.

A resulting final recommendation change is a prospective engine
effect in this selected event cohort. It is not a claim that all
Stockfish recommendations are produced by this route. Compare the
event's root attempt and final source and distinguish score changes
inside a root attempt from changes at the public UCI endpoint.
