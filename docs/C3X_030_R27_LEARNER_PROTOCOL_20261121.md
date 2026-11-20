# C3X R27 — What can a player reuse after reading a Stockfish explanation?

Development protocol, 2026-11-21 KST. Main outcome: after a worked example
disappears, choose a legal continuation that realizes a stated chess objective
after a different opponent reply or on a game-disjoint board. The game-disjoint
task is the primary endpoint of a future human comparison. Same-board reply
items measure near transfer. Confidence and reading time are separate.
Predicting which move Stockfish will emit tests engine simulatability. It
does not stand in for chess transfer.

## Compared presentations

| Condition | Participant sees |
| --- | --- |
| A | Board, two named candidates, original Stockfish recommendation and displayed score, one legal PV per candidate with each line's source |
| B | A plus a legal reply contrast, the board reason, its scope, and neutral search setup information |
| C | The same board text as B, paired with an observed trace or intervention record for that recommendation |

Give every participant the same immediate first-attempt prompt before the
worked example. Hold time budget, board display, notation, both candidates,
and test items fixed. Match B and C support-panel text length and layout,
and show provenance in both. The A–B contrast estimates the added
reply-and-concept package. The B–C contrast estimates replacing neutral
metadata with native evidence under this presentation. No rating of a
preferred explanation substitutes for actual follow-up choices. Test later,
as a separate treatment, whether starting with a withheld hint helps.

Use different full games for tutorial and game-disjoint test. Preserve item
versions and independent answer labels before randomization in the future
study. Randomize by participant within skill strata. With one arm per player,
the same examples and tasks can appear in each arm without crossover
carryover. Counterbalance test order separately. Use objective, reproducible
move predicates plus game-disjoint transfer and report geometry accuracy,
engine-prediction accuracy, abstention, response time, and confidence
separately. A factual label must survive exact legal replay. A supported
alternative in an evaluative task needs an explicit judge, depth and reserve
for disagreement; allow multiple correct moves and never use rank 1 alone
when the question asks for a board condition. Analyze participants as
independent assignments and account for repeated item and game-family
measurements. Recruit or collect data only in a separately arranged
evaluation. No human performance estimate is produced in this round.

## Development fixture and native replay

Use the exposed R26 TWIC 08 ply 61 (the ...Nd7/...a4 contrast) for the
lesson only. At 32k requested nodes, complete legal menu, 1 thread, 16 MiB
Hash, default NNUE, compose the R23 root producer with the R26 flags.
Compare fresh stockfish upstream and four R26 mask arms, each with trace
disabled, enabled, and an enabled repeat. Match normalized UCI reports
within arm and compare native trace repeats. Retain the actual final root
producer, available candidate returns in its attempt, and score bounds.
These identify a root computation and a global TT intervention. They do not
identify a local TT entry or authorize attributing the engine choice to b4.
Use only the observed root facts in C; never fill an unknown with a stronger
statement. The participant packet is a development example. Its rule-based
practice positions and answer keys can be openly inspected and are excluded
from any later blinded human trial.

## How outcomes redirect work

| Observed comparison in a future human trial | Next decision |
| --- | --- |
| B improves unassisted transfer over A; C adds little transfer | Prioritize reply selection and compact board reasoning; offer native trace on demand for substantiation. |
| C improves chess transfer over B at similar effort | Find which source facts people reuse and design targeted Stockfish traces around those facts. |
| C only improves prediction/audit of the engine | Expose an audit view and state the benefit in that task's terms. |
| C raises trust, while people accept unsupported recommendations more often | Reduce authoritative language, show explicit scope and test the revision on discordant cases. |
| B and C fail on a new FEN | Check item ambiguity, failed motif transport and absence of a useful rule before expanding trace depth. |
| Only same-board performance improves | Keep an in-position assistance claim and test more distant transfer separately. |

Before interpreting small effects, inspect confidence intervals, heterogeneous
effects by skill, time burden, and items where both independent judgments
agree against the source. A point estimate near zero in an underpowered
pilot does not settle the question.
