# C3X 0.14 — Operational Fibers of Chess Pin Concepts (Provisional Theory, Evidence-Gated)

**Same single formal research unit, C3X 0.14, OPEN.** This is an ontology/method section, not a separate P stage, Notion child, or established Stockfish learned-concept taxonomy. Canonical evidence: [bounded TT and pin receipt](../receipts/c3x-014-native-first64-TT-returns-and-pin-weakqueen-operational-ontology-20261009.json) and [prospective precommit](c3x-014-bounded-TT-return-census-and-pin-subtypes-precommit.md).

## Three distinct objects

1. **Human category** (H(P)): an educational/everyday concept such as absolute pin, relative pin, discovered attack. A human category is not source-native architecture evidence.
2. **Chess-law feature** (G(P,s)): the legally verified royal pin ray, pinned/pinner piece classes, ray direction, pinned-piece actual legal/pseudolegal move constraints and pinner-capture options at position (P), piece square (s), and actual side to move. Source-only original official PGN enumeration establishes 702 witnesses and 31 composite law-type labels in the studied 100 TCEC games, with no evaluator involvement.
3. **Native computational response** (Phi(P,s,e)): a *typed partial vector* of engine operations under pinned source and controlled execution mode (e). All unset components must be `NOT_MEASURED`, **not zero or inferred**:

[
Phi = (L_{\mathrm{legal}}, S_{\mathrm{SEE}}, E_{\mathrm{mobility}}, W_{\mathrm{WeakQueen}},
          V_{\mathrm{eval}}, R_{\mathrm{root}}, T_{\mathrm{TT}}, D_{\mathrm{LMR/history}}).
]

- `L_legal`: actual native Position::legal pin-alignment decisions **NOT yet runtime traced**, though G's legal move counts are independently certified.
- `S_SEE`: count/roles of actual pinned exchange attackers removed in Position::see_ge **NOT yet runtime traced**. Source shows the operation exists.
- `E_mobility`: source-classical evaluation mobility-area exclusion of king blockers **NOT yet runtime traced per pin witness**. Source shows the branch.
- `W_WeakQueen`: source-level relative queen ray one-blocker geometry: 557 own-side / 730 attacker-side blocker witnesses among actual TCEC games, but **NO native per-case branch-event log** yet. This term applies to both human relative-pin-like and discovery-like situations.
- `V_eval`: evaluator identity (SF16 NNUE or classical) and genuine UCI score; actually measured at 40 original pin positions, two cold repeats and 160 original engine runs.
- `R_root`: native root bestmove under two evaluator modes; measured difference 14/40 fixed source worlds. This is a **whole evaluator implementation** intervention, not pin causation.
- `T_TT`: actual native first-64 naturally taken TT return writer/alpha-beta bound event signatures; measured in **other known 28-source-world engine cohort**, not yet joined to the 40 pin test worlds.
- `D_LMR/history`: native search path counters; measured in **other 28-world engine cohort**, not yet instrumented against these same 40 pin source worlds.

**No false joins:** the 28-world TT group and 40-world pin source set are different observational populations. Do not fabricate (Phi) columns by copying cohort aggregate TT data into a particular pin position.

## Provisional operative equivalence, with partial evidence

For positions (P,Q), human concept equivalence (H(P)=H(Q)=mathrm{pin}) does **not** entail law geometry (G(P)=G(Q)), and law-equivalent positions need not have the same native search signature. Define **conditional operative subtype candidate** under a fixed engine build/option/search budget only if (G(P)=G(Q)) but native (Phi(P)
ePhi(Q)) on actually measured like-for-like channels, with trial fidelity and independent source-game/engine transport subsequently tested.

The reverse mapping is also non-injective: the *same* classical WeakQueen source operator can receive human-described relative pin or potential discovered-attack line geometry. Therefore human terms ↔ native functions form a **many-to-many relation**, not a natural one-label-per-hidden-unit mapping.

## Falsification and admission to a new formal stage

The next C3X 0.14 experiment shall add strictly passive native call-site counters for `Position::legal`, `Position::see_ge`, classical `mobilityArea` and `WeakQueen` to the 40 previously source-frozen legal histories. Separate SEE-pin exclusion and queen-line trigger frequencies by actual operating position; verify UCI clean/sham outputs unchanged; record all zero counters and unsuccessful hypothesis cases.

**Do not infer** a Stockfish-learned latent concept merely from a nonzero (Phi) difference, UCI output change, or source branch. A **0.15 computational chess concept-fiber discovery** stage is admissible only if a new independent outcome-blind source cohort, actual source-native per-position signatures, specified positive/negative/sham controls, and coherent cross-source validation plan are frozen. `0.16` only upon a later separate faithful explanation/human outcome or cross-engine transfer problem. Neither future version is OPEN here.
