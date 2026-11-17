# C3X 0.30 R26 — TT Component Panel

Question: for the same legal game history, which TT read consumer changes the
recommended move or the continuation under fixed requested computation?
Advance the source-causality and board-comparison arms in parallel.

## Freeze before engine outcomes

Use November TWIC 1670 human tournament games and TCEC S29 League 2 engine
games, whose event has appeared in earlier C3X work. Sample 16 games per source
by SHA-256 of seed, source and UCI history, with distinct 12-ply prefixes across
sources and at most four games per TWIC event. Take plies 30, 61 and 96, when
present and nonterminal, using a minimum 64-ply game. The cohort is exploratory.
No outcome, eval, or margin participates in inclusion. These are chronological
bands and do not identify tactical, strategic or endgame regimes.

## Interventions

Use SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52, shipped NNUE, one thread,
skill 20, no tablebases, fresh processes, full legal menu. At requested 8,000
and 32,000 nodes, cross TT-MovePicker input on/off against TT searched-value
on/off with 16 MiB Hash. Compare passive patched binary to unpatched SF16 in
every cell. Add default-consumer 1 MiB as a capacity comparison. Keep main
root MovePicker priority from the root list, since it is sourced from the prior
root iteration. Keep cached static evaluation, TT depth and bounds metadata,
probe/refresh, store and replacement rules, and non-picker ttMove uses. Masking
searched values also affects their use in pruning and singular search. Feature
labels describe interventions at read consumers. The search may subsequently
change what it stores, reaches and compares.

Collect native bestmove, displayed score and bound, depth, observed nodes and
legal full PV. Compare exact score only when the head matches bestmove and no
bound is published. Record reply changes conditional on unchanged winner, and
on equal exact score as a nested outcome. Tabulate all four arms over each
paired cell, all source/ply denominators, and game counts for any root change.
Report the number of alternative roots among four arms. Mark any score absence
or unsuitable mate/cp comparison explicitly.

A separate upstream 120,000 requested-node MultiPV=3 search provides a common
margin reference. Use < 15, 15–49, and ≥ 50 cp for same-depth, unbounded cp
rows, keeping all other cases as unavailable. This margin can concern a
different winner from the factorial baseline. Stratification is descriptive.

## Scope of a finding

Exact passive match on untimed UCI fields licenses paired channel comparisons
at these stops. It gives no assurance about Elo or instrumented wall time.
An observed switch licenses a claim about the tested read consumer(s) at this
stop. Root recommendations can change because the intervention changes the
depth reached and the subtrees searched, so a switch alone does not identify
an individual TT entry or its causal transmission. Shared reply, shared score
and shared root each have their own denominators. An explanation of why one
move beats another on the board still needs explicit verified continuations
and an independently calibrated opponent-response evaluation.
