# C3X P40 R2 — Historical Baseline Audit

Date: 2026-11-05. This is a retrospective methodological check on previously analyzed chess data, NOT a prospective experiment.

Sources: original P39 R2 rule-based mobility archive JSON SHA256 84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf; P37 R2 Stockfish16 96k candidate evaluation archive JSON SHA256 d92c33d05fa506b1a84c222b57729f76a53a95970dd61ba38f67ea1ce3f700fa.

Match exact original game case ID and both legal candidate UCI moves. Compare lower mobility-score choice against higher 96k Stockfish root-perspective score, counting ties as abstention. Keep all eight cases. Compare with the simpler 24k top candidate as baseline. The 96k evaluations are separate constrained searches, not independent chess truth or a cross-engine referee. Costs differ substantially. No statistical generalization or C3X model superiority is implied.

Proceed only to independent future chess consequence tests with frozen predictions, full provenance and strong baselines. Original 8 cases were already exposed.