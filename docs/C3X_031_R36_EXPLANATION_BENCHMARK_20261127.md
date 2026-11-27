# R36-T01 — Explanation benchmark v0 (2026-11-27)
Status: public feature scan, not a hands-on quality comparison. No claims about comparative superiority.
## Direct sources
- DecodeChess https://decodechess.com/features/ and https://decodechess.com/faq/ — threats, plans, concepts, piece functions, alternative good moves. Primary structured explanation baseline.
- ExplainThatMove https://www.explainthatmove.com/ — explicitly compares two moves and explains why one is stronger. Closest direct contrastive baseline; inspect actual outputs before novelty claims.
- WhyThisMove https://whythismove.com/ — natural-language coach, ideas on board, game analysis, opening explanations.
- Nova Chess https://novachess.ai/ — vendor describes Stockfish analysis enriched by 40+ structural features; inspect faithfulness rather than assume implementation verified.
- Chessiverse https://chessiverse.com/faq — move review with candidate alternatives, evaluations, clickable moves, AI-written breakdown.
- Mated https://mated.gg/reviewer — turning-point explanations and review workflow.
- Chess.com https://support.chess.com/en/articles/8584089-how-does-game-review-work — mainstream review baseline.
- Chessigma https://www.chessigma.com/products/analysis — engine/review baseline, not evidence of contrastive explanation quality.
- chessfeed.ai https://chessfeed.ai/ — board-linked study, candidates, plans, comparisons.
## Freeze candidate experiment
Use 24 previously unseen lawful positions, 6 each tactical, quiet near-equal, prophylactic and endgame; separate 2 exposed development cases P2-028-0 and P2-056-1, not in holdout. Select using pinned engine before reading site outputs. Store full history where needed, FEN, pair of legal moves, score convention, engine version, threads, hash, nodes and uncertainty. For near-equal cases predeclare absolute score gap <= 20cp and repeat at multiple budgets; do not exclude unstable cases post hoc. Same position/pair/prompt where supported, log limitations and access failure. Compare default and standardized follow-up separately. No personal accounts or private PGN disclosure needed.
Prompt: Compare A and B, name the opponent's strongest practical reply to each, specify how a plan or threat changes, and identify uncertainty. Avoid inventing certainty or forced replies.
Separate scores in [0,1]: legality (hard gate), factual correctness, contrast specificity, strongest-reply coverage, continuation robustness, evidence traceability, calibration, pedagogical clarity, latency and usability. Record raw evidence, not an aggregate. Unknown = null. Two independent human or model raters where actually available; model rating is not learner-effect evidence. Blind labels/random order when feasible. Assess disagreement and cluster by game. Freeze criteria before actual outputs.
Track A: computational intervention and strategy evidence are distinct from fluent rationalization. Track B: actionable explanations with board-linked evidence. No claim that existing commercial methods lack causality based on feature pages.
## New prior-art lead
Explaining Chess and Go in Natural Language (arXiv:2610.23166, https://arxiv.org/abs/2610.23166) surfaced in search; exact bibliographic verification, Drive possession and source reading pending. Do not claim novelty before review. Canonical missing-literature ledger only, no parallel lists.
