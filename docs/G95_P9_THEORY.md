# C3X 0.7.0-G9.5-P9 — Opening-to-Middlegame TT-Sensitivity Cartography

## 1. Return to direct chess-engine science

P8 solved an engineering problem and then stopped correctly: scale-normalized search neighborhoods became reusable, but ROOT_CHANGE support was too narrow across source regimes to validate analogue retrieval.

P9 does not build another representation. It asks a more direct chess question:

Where, during a fresh opening-to-middlegame trajectory, does suppressing an exact TT semantic-use event actually destabilize the engine's root move?

The unit of interest is now a chess-search world, not a learned state.

## 2. P8 is motivation, not evidence

The P8 source concentration may motivate looking at phase, but:

- no P8 target label may vote in P9;
- no P8 positive position is reused;
- no P8 prototype or descriptor enters the P9 estimand;
- no P9 world is selected because it resembles a P8 positive.

P9 must stand on fresh phase-matched PGN trajectories.

## 3. Longitudinal phase matching

Rather than comparing unrelated opening and middlegame position pools, P9 selects complete PGN lines that can supply all four prospectively defined windows:

1. EARLY_OPENING — plies 4–7
2. DEVELOPING_OPENING — plies 8–13
3. LATE_OPENING — plies 14–21
4. EARLY_MIDDLEGAME — plies 22–35

For each admitted line, one deterministic legal position is selected from every window.

Thus one trajectory contributes a four-position progression. Source/opening-family differences are partially controlled because phase contrasts occur within the same PGN line.

Three PGN sources contribute two trajectories each, for six trajectories and 24 fresh positions.

## 4. Complexity guard

P9 excludes pathological phase examples before engine execution:

- no terminal positions;
- not currently in check;
- legal move count 18–48;
- absolute material imbalance at most three pawns.

The corpus records legal moves, material imbalance, material phase units and castling rights for audit. These variables do not use engine outcomes.

## 5. Exact intervention

The existing outcome-blind P4 sampler selects up to 16 near-root TT semantic-use events per engine×position world.

Every selected event is replayed under the same exact event-address intervention used in the G9.4/G9.5 lineage.

Primary target:

ROOT_CHANGE = counterfactual bestmove differs from baseline bestmove.

P9 does not substitute evaluation deltas, explanation scores or learned risk models for this target.

## 6. Cartography, not winner selection

For each of the four phases P9 reports:

- sensitive-world fraction;
- event sensitivity rate;
- engine-specific sensitivity;
- source-specific sensitivity;
- TT semantic-class sensitivity;
- same-position cross-engine replication.

P9 does not choose the best or most causal phase.

A phase receives the operational label developer regression hotspot only if it independently clears the same fixed breadth rule:

- at least 4 ROOT_CHANGE events;
- at least 3 sensitive engine×position worlds;
- at least 2 sensitive positions;
- positives in at least 2 engines;
- positives in at least 2 PGN sources;
- at least 1 position where two engines independently show ROOT_CHANGE.

Every phase is evaluated under this exact rule, and non-hotspots remain in the atlas.

## 7. Why cross-engine replication matters

A single engine may expose an idiosyncratic search path. P9 therefore asks whether the same chess position/phase is sensitive in two or more independently implemented engines.

This does not prove implementation-independent causation. It creates a stronger regression witness: the instability is associated with the chess/search situation rather than one implementation alone.

## 8. Developer regression bank

For every operational hotspot, P9 compiles replayable positive cases:

- exact event address;
- engine binary identity;
- FEN identity;
- phase and trajectory;
- TT semantic class;
- baseline and counterfactual root move;
- baseline and counterfactual PV;
- first legal PV divergence.

Where possible, each positive is paired with a same-position/same-class negative exact-event control.

The intended use is practical: a search/TT patch can replay known sensitivity witnesses and detect whether the causal search path has moved, disappeared or changed character.

## 9. Relation to existing engine testing

Game-level regression frameworks test whether an engine patch improves play through many games. P9 targets a different scale: within-search causal regression witnesses for specific TT semantic uses and root decisions.

The two are complementary, not substitutes.

## 10. Harvest collaboration

P9 carries forward three P8 backflow lessons:

- cross-engine balance is not cross-world balance;
- an index or map must not outrun its causal ecology;
- stop at the earliest failed entitlement.

Harvest remains a design donor and memory surface. The P9 chess claims are earned only by fresh engine intervention.

## 11. Stop rule

P9 is deliberately finite.

- corpus failure → close;
- support failure → close;
- support pass → publish the full four-phase map and hotspot bank;
- no new representation family, no post-hoc phase boundary, no threshold relaxation.

P9 is done when the chess map is done.
