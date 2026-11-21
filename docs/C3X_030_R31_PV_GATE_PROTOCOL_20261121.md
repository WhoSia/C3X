# R31 — Follow-up on the PV fail-low heuristic

The first field cross found a direction-dependent effect. Under the ordinary
scout, making the PV consumer see depth 10 instead of 12 switched off
`likelyFailLow`, changed several move reductions and changed the final move
from g5 to Kg7. The immediate child return remained 1934. In the full-hint
mask world, the reciprocal swap enabled the heuristic and left every public
output and the immediate PV return unchanged. Neither swap recreated the
other scout world's PV return.

Before running the follow-up, prescribe one replacement of the Boolean
at the PV call while leaving its physical and effective TT tuple alone.
Use false after the ordinary scout and true after the masked scout.
Keep the two depth-cross arms and untreated controls in the same build.
For each direction require equality of the ordered late-move depth
records, local returned score, root updates and normalized public output
to say the Boolean switch reproduces that direction's depth effect.
Repeat from fresh processes. Log whether the scout directly took the
cut-node depth decrement without a TT move, regardless of later stores.
