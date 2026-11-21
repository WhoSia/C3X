# C3X 0.30 R31 — The TT record between the Kg7 scout and its PV re-search

Reproduce the R29-031 R30 reversal under Stockfish 16, original move history,
NNUE, unrestricted root, one thread, MultiPV 1, 16 MiB hash and 32,000 nodes.
Preserve the original hint intervention at scout probe 233. The later consumer
is the unexcluded PV call at ply 1 in attempt 14, root f6g7, candidate 236,
key 17109324142970305696, window [1706,1951] and input depth 12.
Require one physical consumer hit and identify the actual cluster and slot.
The probe sequence number may differ across arms.

## Writer followed by field intervention

1. In fresh sham, full hint-mask and restore runs, only observe. Trace writes
   and generation refreshes in the scout entry's cluster until PV consumption.
   For each write record full writer key, slot, site, incoming tuple and
   actual before/after tuple. Check writer continuity at the read. Preserve
   move-only writes and rejected payload replacements.
2. After inspecting the passive tuples, cross the two sender worlds with
   their own PV fields and with each differing value, depth or bound from
   the other world individually. Equal fields are checked as identity arms.
   Compare each swap against its own arm, including the physical rather than
   substituted tuple at consumer entry. Effective fields are confined to
   the one PV stack frame and the entry observed on arrival. Descendant probes
   and stores operate on the real TT. Repeat fresh runs. Treat any subsequent
   world divergence as a consequence of the intervention, within that frame's
   scope.
3. Record scout and PV child returns, Kg7's root update against its live
   alpha, and final recommendation. Check no-op observer and restore parity
   with the existing R30 binary. Count a forward depth cross plus reverse
   rescue as support at each endpoint where both occurred. A change in the
   PV return alone has a narrower interpretation than a root or final change.
   A one-way result is conditional on the sender world.

Value is the raw stored value before conversion by the consumer. Compare
bound direction with alpha and beta and keep TT depth distinct from the
depth argument to search. Raw internal scores in a window are not exact
centipawn gaps. Treat this exposed position as a diagnosis of an existing
case. The next independent sample begins after its selection rule is fixed.

## Learner comparison

Extend the existing R29 packet without changing its board explanation. The
native panel and a public-only iteration panel must carry the same amount of
material, identical formatting and the same questions. Keep the advice,
board facts and tested position constant. Both panels can describe one
search. Assign one lesson to each person and score threat and conditional
plan together on hidden replies, keeping same-game and new-game results
separate. Native-mechanism comprehension and confidence are secondary.
