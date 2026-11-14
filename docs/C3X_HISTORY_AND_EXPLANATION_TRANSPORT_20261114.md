# C3X historical synthesis — from near ties to explanation transport

2026-11-14 KST. Review of the origin, C3X 27/28/29/32 chat archives, D1, and R4–R6 artifacts. This is a focused retrospective on the project spine.

| Stage | Research question and carried evidence |
| --- | --- |
| [Origin / 0.2](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view) | Explain why two viable moves differ and what to do when an opponent deviates. Separate a small strategic advantage from finite search noise. |
| [0.27 / September](https://drive.google.com/file/d/1F1OUWuB7TYczA5HTmkkUq3F7W_lwS9UO/view) | Freeze source-derived inputs, perturb TT-FIRST, then intervene at the identified capture-pruning guard in game 14. Original b3a4, perturbation f3f4, guard release b3a4. One tested mechanism witness. |
| [0.28 / transport](https://drive.google.com/file/d/12Kwk4GFH7IUJviEOt-zjoswdYIBEEE0b/view) | Trace how effects reach parents and the root, test cohort transport. Retain the 64-position confirmation HOLD. |
| [0.29 / plan value](https://drive.google.com/file/d/13A7_J4V1PXSaCKPEZdKiYykM1QPmn2XN/view) | Plan existence alone has weak discrimination. Conditional trees can lose to a PV. Test added value, reply robustness and game-level transfer. Keep original 7/8 prospective gate separate. |
| [0.30 / D1](C3X_030_DECISION_D1_NATIVE_CAUSALITY_FIRST_20261111.md) | Source-local intervention and real choice transmission first. Attach independent reply analysis to the same contrast. |
| [R4](C3X_030_S4L_R4_CROSSED_SEARCH_STATE_20261114.md), [R5](C3X_030_S4L_R5_ADDITIVE_CHOICE_AND_REFERENCE_AUDIT_20261114.md), R6 | State exchange reveals hidden choice sensitivity. Additive latent scores fit the observed choice labels. Measuring fixed-depth forced-candidate gaps supplies a sharper falsifier. |

Borrow the established parts: Stockfish, Berserk, recursive reply-tree selection, SARFA and BinProp comparators, and interchange intervention. [Pinned index](C3X_030_PRIOR_ART_IMPLEMENTATION_INDEX_20261114.md). The C3X claim to test is whether a source-grounded contrast can predict a consequential outcome under a newly chosen opponent reply and can improve on a PV or concept baseline on that same task. Source faithfulness, robust chess value and learning are three independently measured outcomes.

Practical design: select full game histories before outcome, stratify small and larger score gaps and finite-search reversals, freeze a specific rival move and goal, publish predictions for unexplored replies, and keep a game-disjoint confirmation split. A defensible null is a correct source explanation with no added strategic or learner value. Existing sealed cohorts retain their original scope.
