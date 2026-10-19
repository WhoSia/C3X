# C3X 0.27 — Memo 02: A Real Root-Choice Intervention Without a Discriminating Immediate-Tactics Claim

*Working manuscript section, 2026-10-19; grounded in P14-P3 source and independent full-chess CI.*

The decisive experiment in the present evidence is not a synthetic variation: Stockfish 16 changed its selected root move in one game after a real qsearch bounded-score intervention. Game 28 of a presealed July 2026 cohort changed from Rf1-d1 to Ra1-a5. The source archive independently recorded a score-intervention contact, an altered root contender vector and a final root-choice flip. Removing the TT move hint alone did not reproduce the flip. These measurements identify a causal effect of this specific physical intervention on the engine's chosen move. They do not identify the full computational path through every parent assignment, nor an engine-recognized chess concept.

We now subjected both selected moves to a second execution environment using a standard legal chess implementation. From the same FEN, both legal roots leave Black 25 legal responses. In neither resulting position does Black have an immediate capture or checking move. The opponent-capture-conditioned recapture predicate consequently has an empty conditioning set in both arms; interpreting its Boolean false representation as a substantive failure to recapture would be erroneous. None of the inspected immediate-tactics features distinguish the two root choices. The Github Actions run completed successfully on 19 October 2026 (run 39219743776).

This negative result changes the explanatory question. The existence of a real root-choice effect does not license us to choose any post hoc property that differs between the two resulting boards and declare that property the cause. Indeed, if arbitrary predicates are allowed, the trivial predicate 'the rook occupies a5' separates the moves by construction. Such a distinction is exact and wholly uninformative about why Stockfish selected the move, what strategic outcomes remain possible, or how a human should decide.

The missing object is not another tally of legal moves. It is an *independently justified relevance relation* between a property of future chess consequences and the engine computation whose intervention changed the decision. This relation must survive an experiment that froze candidate properties and negative controls before inspecting the changed choices. For the exposed 28th game, further analyses can generate hypotheses but cannot become prospective confirmation. A next independent source cohort is needed to test whether such relevance is predictive.

### Scientific boundary
The game-28 source intervention result was real, but its expanded five-arm follow-up is post-outcome selected. The 25/25 and zero captures/checks measurements are independently rule-checked but limited to immediate replies. These findings do not establish strategic equivalence or absence of longer-term tactics. No causal chess-concept mediation, human learning benefit, or publishable novelty has yet been demonstrated.

### Verified source
- Original M6 sealed judgment c3x/receipts/c3x-025-P14-P3-M6-July64-human-Git-presealed-native-source-independent-verdict-20261012.json.
- Exposed root-28 source trace c3x/receipts/c3x-025-P14-P3-R3-exposed-Jul2026-original-root28-native-causal-slice-20261012.json.
- Full chess replay script tools/c3x_027_m6_root28_chess_replay.py and GitHub Actions run https://github.com/WhoSia/C3X/actions/runs/39219743776.

## Stronger theory question: relevance beyond logical discrimination

Let I alter an original engine computation, A(I) denote its root choice, and Q(h,a) a predefined chess property. The relation Q(h,A(0)) != Q(h,A(1)) is necessary for a nonzero effect on the selected property Y(I)=Q(h,A(I)), but it is not evidence that Q caused the changed choice. If Q is chosen after A(0),A(1) are known, selecting an identity predicate makes discrimination trivially possible. Thus a scientific explanation requires independent property-selection authority (e.g., an engine computation trace specifically tied to a chess state feature, with targeted interventions) and heldout prediction or transport tests. No causal mediation theorem is claimed here.

## Reader-facing implication
Chess explanations should resist two temptations: to present an attractive legal line as an adversarial guarantee, and to present a distinguishing board feature as the model's reason. Our data support caution about these confusions. The uncompleted research is to develop a test that certifies when a particular mechanism-connected consequence does more than describe a changed action.
