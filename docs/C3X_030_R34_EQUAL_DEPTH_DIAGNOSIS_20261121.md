# C3X 0.30 R34 — Equal-depth controls for 11 R33 move changes

R33 observed 11 event-level final-move changes in nine fresh TWIC
1671 positions under `go nodes 32000`. This follow-up selected those
eleven outcomes after seeing R33 and is a mechanistic diagnostic.
Every target's event ordinal and pre-intervention source signature
was retained. Each case was searched from a fresh engine at the
originally completed depth and, when different, at the treated
completed depth as well. Both the no-intervention and paired
early-return intervention were repeated.

For 16 target/depth combinations, the exact target was reached with
the frozen signature and all 32 stderr replay pairs matched byte for
byte. At each of the 13 unique position/depth combinations, R31
and observation-disabled R33 had equal normalized UCI and native
root receipts. The observation-enabled fixed-depth control had the
same bestmove and public iteration sequence.

## Results

At the original completed depth, 8 of 11 target comparisons still
gave different final recommendations. Three comparisons became
identical. At the 16 total prespecified target/depth comparisons,
11 had a final difference.

| Case | Null-move stratum | 32k original → treated | Fixed depth | Original → treated at fixed depth |
| --- | --- | --- | ---: | --- |
| R33-002 | Eligible | Qb5 → Rae1 | 13 | Qb5 → Rae1 |
| R33-003 | Eligible | h3 → Bc7 | 11 | h3 → h3 |
| R33-007 | Eligible | h3 → Rdg1 | 10 | h3 → f3 |
| R33-009 | Eligible | Rxb3 → Rc8 | 13 | Rxb3 → Rc8 |
| R33-010 | Eligible | Nh2 → g3 | 13 | Nh2 → Nh2 |
| R33-021 | Ineligible | h6 → Nxe4 | 11 | h6 → h6 |
| R33-036 | Eligible | e4 → a4 | 11 | a4 → e4 |
| R33-036 | Ineligible | e4 → b4 | 11 | a4 → b4 |
| R33-040 | Ineligible | h3 → Nb3 | 12 | h3 → Qxc7 |
| R33-040 | Eligible | h3 → Qxc7 | 12 | h3 → Qxc7 |
| R33-042 | Ineligible | Bc4 → Bb3 | 10 | Bc4 → Bb3 |

Each SAN is recalculated from the exact PGN history at the sampled
board. Both arms in a row search to the same completed depth. The
table emphasizes that this does not always preserve the particular
alternative move seen under a node cap.

R33-003 changed to Bc7 under 32,000 nodes partly because the
intervention allowed a depth-12 completion, while the original run
ended at depth 11. At a fixed depth 11 both recommended h3. At a
fixed depth 12 the original chose Rea1 and the intervention Bc7.
The effect is conditional on reaching that later search depth.

R33-010 had the reverse sensitivity. At depth 12, Nh2 versus g3
differed. At depth 13 both selected Nh2. Thus the source intervention
created a transient preference difference that a deeper completed
search removed.

R33-021 changed h6 to Nxe4 under the node limit, although both
reported 11 completed depths. At exactly depth 11 both selected h6.
The completed-depth counter alone therefore does not identify the
relevant search horizon of an interrupted engine process.

R33-040 is the preferred next source-lineage diagnosis. Both of
its preselected early-return events can change the final recommendation
at a fixed depth of 12. The null-eligible arm reproduces the exact
h3 → Qxc7 pair from the node-limited test. The null-ineligible
arm instead gives Qxc7 at fixed depth, while its node-capped
treatment gave Nb3. Trace the actual 12th-depth root candidate
updates under a shared alpha before testing any proposed mediator.
A single route need not explain the two event strata.

## Limits and decision

These comparisons retain the same fixed source event, but they
are all drawn from the R33 flip subset. They cannot estimate the
prevalence of stable recommendation changes in a new population
of games. A completed depth also permits different amounts of
search work within that depth. Distinguish a deeper completed
iteration from a changed score or move order inside an iteration.

The evidence supports maintaining separate endpoints for
the exact early-return effect, its root-candidate descendants,
the completed-depth public report and the final recommendation.
For learner-facing Explainable Stockfish, a source event can
be shown as a computation fact only when its observed reach is
specified. In particular, a source intervention that changes
the final recommendation at one finite budget cannot be used
to assert that its move is strategically stronger over unseen
opponent replies.

The original human trial remains R31's four-arm comparison of
board reasoning, public PV history and native causal trace.
No participant outcomes were collected here.
