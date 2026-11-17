# R26 — Equal-depth comparison and named-candidate replay

The 8k/32k panel is the discovery pass. Its 120k last-frame reference
left 46 of 88 margins unavailable. The fixed-depth follow-up preserves
all 88 histories and repeats upstream, passive, picker-only, value-only,
and joint masks to requested depth 13. Report recommendations, exact
passive matches and nodes by arm. Depth here controls the requested
iterative-deepening stop, while node costs and selective reach can vary.
Afterwards use a separate upstream depth-13 MultiPV=3 run on every case
to obtain an exact same-depth reference and retain unavailable cases.

Named candidates are chosen by the previous panel, so this is illustrative.
Use the three unique positions with a changed top recommendation in the
large 120k-reference band. At 500,000 requested nodes launch a fresh
unrestricted upstream search, then a fresh search per candidate that
appeared as upstream or perturbed recommendations at 8k/32k or among the
120k reference top three. Record the exact candidate-specific score and
reply with white/black POV kept relative to the original mover. A forced
root gives extra budget to that candidate and does not reconstruct the
default rank or score. Separately use the sole exact-score, same-winner
8k/32k default-search reply fork. Fix its root and each of its two
observed opponent replies on legal histories and search each child with
500,000 requested nodes. These are within-engine follow-ups, with no
independent-engine, causal mediation or human-study claim.

## Separate engine and board evidence

Freeze the named contrast from the 500k replays: 32k normal `...Nd7` and
32k joint mask `...a4` at TWIC case 08, ply 61. Using pinned Berserk 14 and
its own NNUE, enumerate every legal White reply to each root. Use one
fresh UCI game per leaf and fixed depths 13 and 15. Rank the two Black
roots by the minimum Black-POV leaf score, and compare shared legal
replies only on a separate diagnostic list. Root-specific minima can
use distinct legal replies. Exact report here means point form at the
requested depth, with inherent finite search approximation.

At TWIC case 13, ply 96, independently replay the four fixed prefixes
`h5 ...f4`, `h5 ...Nf6` and each with `h6` appended. Compare the free
White continuation after each reply and the White-POV reading after
committing to `h6`. Record the first White move and the evidence for a
shared legal resource across two branches. These selected cases have
already been exposed in the Stockfish work. Do not use them for
population inference or claim that the board resource mediated a TT read.
