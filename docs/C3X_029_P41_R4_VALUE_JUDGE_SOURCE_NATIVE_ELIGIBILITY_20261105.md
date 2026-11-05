# C3X 0.29-P41/R4 — Independent Value-Judge Source Native Acceptance (Fail Closed)

2026-11-05 KST. Before invoking any external chess-value engine, require the original source/compilation/binary identity, legal-history context, consumed node count, usable score constraints and scientific family independence. **This is a quality gate only; it does not produce original chess-values.**

Historical negative: P38 Ethereal12.75 source experiment asked 96000/192000 nodes but actually returned 2–5 nodes at depth1. Those outputs CANNOT be judged independent high-quality values despite CI checkout/build success. Node and depth limits below are necessary minimums, not a guarantee of reference accuracy.

Receipt fields for each evaluated terminal candidate: engine_family, verified_source_commit, binary_sha256, source_audit_verified flag, original_chess_history_uci, intended_board_fen, candidate_root_uci, opponent_reply_uci, own_continuation_uci, requested_nodes, actual_nodes, depth, reported_root_mover_cp lower/upper and raw UCI score flags, legal PV. Outcome source identity and network SHA, if neural, pinned independently. Opponent-board FEN must be reconstructed by replaying all three moves after the original move history. The original mover is the reference value viewpoint; opponent-to-move scores must be sign flipped and proven.

Hard reject: missing SHA or manifest, family unverified or same family as source Stockfish16, source history/FEN mismatch, illegal candidate/opponent/own continuation, terminal unmodeled case, actual_nodes under 0.9 requested, depth <3, score mate coerced to cp, inconsistent bounds, PV illegal. If source family is declared different but external source-level code provenance was not read/verified, classify TECHNICAL_ELIGIBLE_ONLY not independent proven chess truth. Any bounded engine output remains finite-search estimate.

Design uses an independent full-history chess.Board replay in P41/R4 acceptance tests. No notebook-generated pseudo ChessBoard from an invalid FEN is admissible. The original C3X P38 STOP is not rescinded by this protocol.

Only if actual source-native separate engine search receipts pass can the P40 plan-regret interval scorer accept value labels. The rigorous workload audit P41/R3 projects ~2.39 billion requested nodes to cover the full eight-game P39 tree at 96k nodes per own continuation. Therefore favor preregistered falsification-by-one-bad-reply first, never claim universal low regret from a sample.

Primary paper baseline: Cui et al (2026), originally held in Drive 19zqCJXM631qasR9uIyg4GuBZxIBO7czw, already tests worst sampled response and downstream chess-playing utility. No novelty of adversarial branches alone.

All authored source files by WhoSia, no bot commits; Notion semantics, Drive bytes, GitHub code and CI.