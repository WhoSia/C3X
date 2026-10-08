# C3X 0.13 P6-I — Intervention Identifiability, Feature Fibers and Causal Claim Court

State: mathematical post-measurement audit precommit. No unique chess-concept cause identified.

Define exact board feature vector F(s)=(center occupancy, center attack, pawn isolation, passed pawns, king shield, etc.) in ORIGINAL MOVER perspective. For a legal root a in s, F_a=F(s_after_a). A matched contrast between legal roots a and b is D_F=F_a-F_b. If target concept component D_C is nonzero but nuisance vector D_N is nonzero too, a ranking difference D_V=V(s,a)-V(s,b) alone CANNOT uniquely determine mediation through C.

Even under a linear surrogate D_V = beta_C D_C + beta_N^T D_N + epsilon, one observed scalar and multiple changing coordinates is underdetermined. Restricting to repeated engine restarts or multiple search depths on the SAME two root moves does not create independent chess-world interventions. A full-rank design matrix over concept + nuisance coordinates is a necessary algebraic condition to identify linear coefficients, but still not sufficient to establish chess causality without exclusion controls, intervention legitimacy and source/engine transport.

Exact witnessed confounds from P6 real Stockfish16:
- PASSED_BOUNDARY root d4d5 vs a4a5: own passed-pawn difference +1, BUT own center-control count -1 and opponent passed-pawn count +1. Score differences at completed depths [8,12,16] are [-345,-538,-595] cp (two exact independent restarts each). This is NOT a negative causal estimate of passed-pawn value. It says naive 'one more passed pawn always increases engine move preference' is violated on this legal synthetic root pair.
- ISOLATION_CAPTURE root c4b5 vs d4e5: own isolated-pawn count difference +2, BUT own center control -1, opponent center control +1, opponent center occupancy +1, own passed-pawn count -1. Completed depth [8,12,16] ranking [70,140,124] cp, two exact restarts each. Two root moves capture DIFFERENT enemy pawns, so material change parity alone does not match capture location or pawn-structure consequences.

Formal types:
  BOARD_FACT(FEN, square, color) != LEGAL_TRANSITION(FEN, UCI) != VALID_BUT_ARTIFICIAL_BOARD_EDIT(FEN,FEN')
  != ENGINE_CONTRAST(engine, budget, source, legal-root-pair) != CAUSAL_CONCEPT_CERTIFICATE.
Do not promote across type boundaries absent a declared intervention, support family, collateral audit, negative control and prospective independent verification.

P6 stop if the selected concept coordinate toggles but any monitored nuisance also toggles, unless there are matched negative controls and a separately registered identification argument capable of distinguishing them. Conversely no change in concept coordinate => SUPPORT_HOLD even if the engine score changes. Unknown or unmeasured chess features are never assumed constant.

A future 0.14 paradigm would require independent source worlds where an intervention-compatible *typed chess-concept reason* predicts and survives adversarial cross-engine and alternate-reply tests beyond P15/P16 local scope, not simply this formal vocabulary or two synthetic successful executions.