# C3X 0.30 S4-L/R12 — Matched legal-reply forecasts

2026-11-17 KST. D1 asks whether adding explanations grounded in source computation helps predict the strategic difference between nearly tied moves. R12 defines and exercises the scoring boundary on R11 material.

## Comparison

Fix the complete game history, a pair of ordered candidate moves, and one legal opponent reply playable after either move. Freeze the questions and the ordinal predictions (first better, tie, second better or abstain) before running an independent judge. Compare three arms: PV, reply tree, and the same reply tree with attributable source events. The intended prospective runner must record equivalent search budgets, shared tree inputs for the tree and trace arms, when the forecast digest was sealed, and which source events support each prediction. This scorer reads caller-supplied prediction labels and checks file integrity and cohort joins. The producer and proof of chronology are separate.

For each question, judge the difference using the same forced reply under each candidate from the root player's perspective. Keep the actual outcome tied if its ordered values are equal. Withhold the target if either point is absent, only a search bound, or below the fixed judge depth, except enumerated terminal positions. Report available labels and individually correct signs for each arm. Use only questions with both judge points and all three forecasts to compute paired comparison counts.

## Historical smoke replay

The [R11 cohort and judge archive](https://drive.google.com/file/d/1BQPYBC6FVyF_wlj71UvJ6lJAFf4Wq5jd/view) contains eight near pairs. Seven had a reply shared by both 12k-discovery tree shortlists. Choose the lexicographically first intersection member per question. The PV baseline uses the free-response gap's sign. The tree uses the selected common reply's gap sign. Trace forecasts explicitly abstain. Depth 12 and depth 14 both produce PV 4/7, tree 3/7, trace coverage 0/7 and paired coverage 0/7. This is a retrospective scoring fixture on R11, including already available judge results. No new search, cohort, prospective trace label or effect estimate was produced.

The [R12 replay archive](https://drive.google.com/file/d/1-jrnCGsDAX4kBWj5p62uA7O-Gy79DPyb/view) contains requests, questions, forecasts, scored outputs and their SHA-256 manifest. The downloaded archive matched the upload byte-for-byte. Archive SHA-256: `d53130b0f2db24f9224a1401b092c31bbe9d4aeb25f7215958888cf1ae2d3132`.

```bash
python harness/c3x_030_s4l_r12_reply_questions.py r11-cohort.json r12-requests.json
python harness/c3x_030_s4l_r12_explanation_score.py \
  r11-cohort.json r12-questions.json r12-forecast.json r11-judge12.json \
  --forecast-sha256 36158406268d05898079fc6641fc91eea10bc8f06eaed9e0d3717551d5586387
```

Substitute `r11-judge14.json` for the depth sensitivity replay. In the next independent event, keep the tree fixed, bind source traces to exact candidate and reply histories, and seal all three forecasts against a separate deeper judge. This comparison targets predictive value of additional information about the actual search. Source intervention fidelity and human transfer each require their own outcomes.
