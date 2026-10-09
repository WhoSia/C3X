# C3X 0.15 — CSWP v0.6: Incomparable Search-Observation Quotients
## Actual P9 source-native tests of return value, root score, search cost and categorical choice

**Date:** 2026-10-09. **Status:** Original research measurement framework and witnessed case-specific propositions, not a historically unprecedented mathematics theorem or universally established chess theory. C3X 0.15 remains OPEN, 0.16 NOT OPEN.

### 1. Four distinct observable maps on deterministic original engine runs

Fix an original legal game history, an SF16 source build/compile configuration, a full-cold UCI protocol, and an exact preselected source TT writer/reader target. A run r produces a tuple:
- \(L(r)\): numerically delivered result of that selected source-local TT/qsearch return, with the exact source event and exposure certificate.
- \(S(r)\): final completed-depth UCI root-side score, using score-type and lower/upper bound flags, NOT an oracle chess value.
- \(N(r)\): actual total native search node count.
- \(Y(r)\): final categorical UCI root bestmove.

Each observable induces an equivalence relation \(r\sim_L r'\iff L(r)=L(r')\), and analogously \(\sim_S,\sim_N,\sim_Y\). These are *measurement partitions*, not declarations of natural causal paths, human semantic understanding or universal chess theory.

The common mistake is to act as though a single scalar evaluation and the final bestmove determine every relevant engine mechanism. They do not.

### 2. Empirical nonimplications witnessed by frozen TWIC R2 worlds

**Proposition 0.15-P9.1 — Local return equivalence does NOT determine root choice.**
In original source world #29, SEE OFF, exact original selected TT immediate return I delivers 29 and produces root bestmove d1e2; treatment B blocks that one TT return and runs qsearch, which recomputes/delivers 29 but produces root bestmove f3e5. Thus \(I\sim_L B\) but \(I\not\sim_Y B\).

**Proposition 0.15-P9.2 — Same root choice does NOT determine local return.**
In original source world #2, SEE ON, exact B qsearch computes/returns 173 with bestmove d1d2; L executes the same target qsearch body but returns the previously stored TT value 14 at the exact local caller return gate, also with bestmove d1d2. Thus \(B\sim_Y L\) but \(B\not\sim_L L\). Important: root final score and total nodes actually change (B 54 cp, 65,172 nodes; L 63 cp, 60,927 nodes), proving final categorical invariance does not imply search-state equality.

**Proposition 0.15-P9.3 — Same root choice does NOT determine final root-side numerical score.**
In original #29, targeted first qsearch child score -59 is artificially replaced at one exactly matched source event with 130 or 131 (reader window alpha130, beta131). Both OFF conditions choose root move f3e5, but final recorded scores are respectively 4cp and 22cp (nodes 50,516 vs 77,115). Thus \(D130\sim_Y D131\) but \(D130\not\sim_S D131\), with the hard caveat that neither 130 nor 131 represents a credible real chess evaluation.

**Proposition 0.15-P9.4 — Same root move AND final score can conceal different search work.**
In #29 SEE OFF, B gives f3e5, final score4cp, nodes75,284. D129 gives f3e5, score4cp, nodes50,516; hence \(\sim_Y\cap\sim_S\) does not imply \(\sim_N\). The source-gated first child score substitution was actually delivered exactly once.

All four are simple logical facts about actual observed source-native run tuples under controlled interventions, NOT claims of an original mathematical discovery. The scientific contribution sought is rigorous **instrumented source-grounded examples**, reusable falsifiers, and systematic transport tests beyond these two outcome-disclosed chess games.

### 3. What P9 disproved, and what it did NOT identify

The A1 gate treatments targeted three different source instructions with at-most-one exposure: G ignored the actual world#2 check-evasion beta fail-high break after child173, W omitted one exact target qsearch terminal TT SAVE, and L changed only the target caller-visible return value after computing the full qsearch body. All source conditions fired where expected; the G world29 sham correctly had zero source contacts. Across both observed game worlds/SEE arms, NONE of G/W/L changed the categorical bestmove relative to B. Both G and W preserved final score/nodes; L in world2 SEE ON changed final score/nodes despite bestmove equality.

This falsifies strong and simplistic claims that **that isolated beta break**, **that single terminal TT write**, or **that one propagated score** is independently indispensable for the final categorical root change under the tested environment. It does NOT prove the entire search history or TT graph is causally unnecessary, and it does NOT identify unique natural mediation. State after a local source event includes other TT reads/writes, move ordering, iterative aspiration windows, root candidate competition, and accrued search history.

P9 A2 crossed the artificial first-child value across the single-element null-window boundary. At 129 and 130 the final world29 OFF score was 4cp (50,516 nodes); at 131 it became 22cp (77,115 nodes). All selected root move f3e5. World2 was no-contact sham in all six test arms. This is an observed source-program boundary response, not a mathematical proof of monotone search behavior or correct chess evaluation.

### 4. Multi-motif ontology rather than PIN monoculture

The scientific object is a typed interaction between source-law facts, candidate move-sequence tactics (skewer, pin, fork, interference, decoy, clearance, deflection, defender removal, intermezzo, mating net), persistent positional strategies (pawn structure, king activity, outposts, simplification, open files, center control, prophylaxis), original executed source operators (SEE, qsearch, TT writer/reader, alpha/beta, evaluator and root competition), and observable outcome projections \((L,S,N,Y)\).

One board can exhibit several candidate motifs simultaneously. Geometry-only pin or skewer contact is not the same as tactical necessity; a one-run TT return is not evidence of human-intended strategy. Each explanatory claim is labeled LEGAL_CERTIFIED, SOURCE_OBSERVED, INTERVENTION_IDENTIFIED, TRANSPORT_CONFIRMED, or ABSTAIN, with independent proof obligations for promotion.

For future source-independent strategy contact, the recovered STS1–15 EPD holds 1,500 rows but only **1,497 unique 4-field FEN classes** due to 3 exact duplicates crossing labeled strategy sections. Split by FEN equivalence class before learning. Do not use the EPD bestmove/c0 annotations as an exact chess oracle or causal truth.

### 5. Evidence, limits and future falsifier

- P9 A1 native SF16 48-process SUCCESS: https://github.com/WhoSia/C3X/actions/runs/37926784308
- P9 A2 native SF16 24-process SUCCESS: https://github.com/WhoSia/C3X/actions/runs/37927609148
- P9 actual A1 receipt: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P9-A1-CEFH-RISR-48-native-single-beta-TTsave-clamp-factorial-20261009.json
- P9 actual A2 receipt: https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P9-A2-RISR-first-child-alpha-beta-boundary-24-native-and-72-total-20261009.json
- Prior source-frozen P1 C1 context prediction FAILED overall-accuracy B0: 42/64 versus B0 53/64. Keep this as the primary prospective negative result.
- Total P9 original chess-game worlds n=2 selected after P6 outcomes; **72 native processes are technical repeats/arms, not 72 independent sample positions**.
- Stockfish16 uses Use NNUE=false in these trials. No actual NNUE feature was manipulated.
- Observed source and root-score dissociations require an expanded root-competition event ledger and new genuinely disjoint chess games / engine source families, with frozen predictive baselines, before any transferable tactical/strategic concept claim.

**Verdict:** CSWP_V0.6_FOUR_MEASUREMENT_QUOTIENT_NONIMPLICATIONS_ACTUALLY_WITNESSED / P9_72_NATIVE_SCOPED_PASS / CROSS_SOURCE_STRATEGIC_TRANSPORT_NOT_TESTED / NATURAL_TT_FULL_MEDIATION_HOLD / P1_C1_PRIMARY_ACCURACY_FAIL / C3X_0.15_OPEN_NO_0.16.
