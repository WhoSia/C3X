# C3X 0.30 R34 — Same completed depth after prospective gate interventions

This is a follow-up to the frozen R33 result, which had 11
target-level changes in nine sampled positions. The selection is
outcome-dependent and only a diagnosis of those cases. For each
changed target, run the original gate and the corresponding R33
treatment under `go depth N`, where N is the original completed
depth, then at the higher of the original and treated completed
depths if different. The R33 move order and original target
ordinal remain fixed from the node-limited discovery.

Require the original target read signature to match before each
intervention. A depth limit that finishes before the target read is
reported as out of reach. Treat different actual positions, attempt
or window as an identity failure. Clear the engine between arms,
repeat each arm once, and retain the exact stdout and stderr.
The comparison at an equal depth is then the engine's completed
iteration outcome. Node counts can differ because the intervention
changes search work. Record final move, score/bound and PV at the
prespecified depth. Test the extra depth separately rather than
inferring what the 32,000-node limit caused.

The result may show that a 32,000-node final flip vanishes when
both arms finish the same depth. Keep those cases as meaningful
negative tests. This follow-up does not generalize to untouched
new positions and does not judge chess move quality.
