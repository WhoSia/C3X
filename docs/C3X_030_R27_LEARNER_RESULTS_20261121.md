# C3X R27 — Native move producers and a learner-feedback development kit

2026-11-21 KST. [Protocol](C3X_030_R27_LEARNER_PROTOCOL_20261121.md) ·
[Prior work and design decisions](C3X_030_R27_LEARNER_LITERATURE_20261121.md).

## Native provenance for the two candidates

On exposed R26 case TWIC 08, ply 61, reproduce the full 34-move legal
search at 32,000 requested nodes. Thirteen searches, 416,198 total last
reported nodes. Each arm reproduced its normalized UCI output with tracing
off, tracing on, and tracing on again. Untouched Stockfish16 matched the
instrumented baseline. The trace-on logs repeated byte for byte.

| Arm | Final recommendation | Producing attempt and internal iteration | Last UCI score (Black) |
| --- | --- | --- | --- |
| Default | …Nd7 | #37, iteration 14 | −257 cp |
| Withhold TT move from non-root picker | …Nd7 | #30, iteration 14 | lower bound −243 cp |
| Withhold TT search value | …Nd7 | #30, iteration 15 | −256 cp |
| Withhold both | …a4 | #38, iteration 13, effective root depth 12 | −250 cp |

In default attempt 37, …Nd7 supplied native value −845 within its window.
The later …a4 call returned −885 with alpha at −845, so the later call did
not move the leader. The return is below the window, not an exact
candidate score. On the joint-mask run, …a4 returned −820 within its window
and …Nd7 later returned −821 with alpha at −820. The output carrying the
default winner was emitted during attempt #38 at reported depth 15;
in the joint run it was emitted during attempt #39 at reported depth 14.
The separate recommendations and windows should not be subtracted as
matched chess-value estimates.

The earlier independent Berserk comparison found the defensive resource
32.b4 after …a4. The root-producer trace locates where the alternatives
were compared and what value was retained. It does not identify whether
that calculation backed up through 32.b4 or a particular TT entry.
The resulting C lesson explicitly describes provenance and the scope of the
global intervention.

## Try the development kit

Unzip the [byte-verified Drive archive](https://drive.google.com/file/d/1Zg8hUd_SU_QcsrKXXIpfA6_cjlEVjMol/view).
Choose one `participant/lesson-A.html`, `lesson-B.html`, or
`lesson-C.html`. Before opening the explanation, propose a move. Close
the lesson, then open `participant/assessment.html`. The boards include
coordinates and highlighted squares. Answer fields are scratch space;
there is no submission or storage. Keep `organizer/` separate when
testing the display without advance knowledge of the key.

The test contains two alternative same-game lines and four TWIC 1671
positions from different games, balanced by side to move and by whether
there is a witness. Selection excluded the R26 event strings and 12-ply
prefixes. Three of the four events are divisions of the same tournament
series, so this does not demonstrate event-family transport. TWIC fixture
generation repeated byte for byte. The scorer accepts a positive answer
only with an eligible legal pawn advance. Wrong, abstained, and missing
items remain in their denominators and the latter two have distinct
labels. The automatic key solved 2/2 near and 4/4 new-game tasks on a
synthetic response used only for testing the scorer. Five R27 tests and
four reused R23 tests passed. The HTML content and answer isolation were
checked programmatically; the restricted host could not start Chromium
for visual verification. The two support texts have 28 and 33
whitespace-delimited units. Recheck readability and use separately held-out
items before randomized human evaluation.

The first screen is source-grounded, but A–B still adds several pieces of
information. Treat it as an intervention on a reply-plus-board explanation
package. The tighter B–C comparison swaps the small support panel.
Keep the board claims identical and ask whether the source panel improves
decisions on new positions, only helps predict the engine, or also changes
acceptance of demonstrably weaker recommendations.

## Reproduction and custody

Run the new harnesses from this branch with python-chess 1.11.2, the pinned
R26 Stockfish build lineage (Stockfish 16, upstream
`68e1e9b3811e16cad014b590d7443b9063b3eb52`), and the R27 combined patch.
The archive has the full UCI logs, source archives, practice keys, and
participant HTML. SHA-256
`f967ed17f2415c2192cbd038c79ae821dbb48327c7b4e98edc257f6907623d75`.
There are no human participants or performance estimates in this round.
