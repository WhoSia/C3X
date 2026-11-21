# R31 — Scope the final-move effect to the search budget

The 32,000-node follow-up directly switched the fail-low heuristic. In
the ordinary world the changed later g5 candidate failed to lead,
although the earlier Kg7 return stayed equal. Test whether the
final-move finding persists at node limits 24,000, 48,000 and 64,000.
The node limit is changed identically for both treatments within a
budget. Use four arms, crossing the scout hint with forcing the
opposite of the natural PV fail-low Boolean inside each sender world.
Verify that the target calls, tuple and Kg7 return match their
32,000-node counterparts. Report a budget separately if the target
is not reached or does not complete. Record the original attempt 14
winner and nodes alongside the final producer and completed depth.
This is a sensitivity test on the exposed case.
