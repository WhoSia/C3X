# C3X 0.30 R29 — Test the same selection rules on new games

The development case established two independently reproducible operations:
withholding a TT move hint at one read, and replacing one number in an
actual ply-one cutoff. Freeze the following external-case rules before
running any engine on the cohort.

- Use the original publisher's TWIC issue 1663 game ZIP (SHA-256
  `36ac4a1324a21674649f7b5eb12e0ef21167b18288917cce6aba3d8120669dd9`).
  Use R28's deterministic position sampler and exclude its admitted events
  in addition to the R26 and R27 events. Keep all 32 admitted games.
- Use the full unrestricted Stockfish 16 top choice at 32,000 requested
  nodes. The named alternative is the 8,000-node top choice if it differs,
  or the highest-ranked distinct move from the separate d12 MultiPV 3 run.
- Use fresh Berserk d13/d15 point scores for each root move from the root
  player's perspective. With margins recommendation minus alternative,
  assign reversal first when one margin is at least +15cp and the other
  is at most −15cp. Classify large stable when both are at least +100cp
  or both are at most −100cp, and close when both are within ±30cp.
  Preserve all intermediate and point-unavailable rows. These are
  reference-engine strata, and the cohort is a deterministic pilot.
- Use the first legal reply in Berserk's direct d15 PV for the alternative.
  Match its UCI move to the first non-excluded, ply-one TT move hit under
  that alternative in the actual Stockfish producing attempt. If absent,
  use the first match in the latest earlier eligible attempt. If none
  exists or the independent reply is unavailable, record abstention.
- Also target the first non-excluded genuine TT cutoff under the
  alternative in the producing attempt if it exists. This tests the
  native bound without requiring the stored move to coincide with the
  independent reply. Each case and channel receives its own clean mask.
- Verify the trace build against the original output. Require exactly
  one changed read, matched probe fields, and restored normalized output
  plus raw trace. Record first searched reply, returned child value,
  leader replacement for the named alternative in the target attempt,
  public output change and final recommendation change separately.
  Keep negative cases and partial results. Fixed depth thresholds are
  experimental strata, not estimates of objective advantage.
