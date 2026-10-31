# C3X 0.29-P9-R12/R13 — Numeric Interaction and Replay Metadata Admission

2026-10-31. Two executable source-level analysis units, independently committed and corrected. No new Stockfish binary run or full GitHub repository test execution.

## R12: factorial descriptive numeric contract
Tool tools/c3x_029_p9_r12_factorial_numeric_contrasts.py, tests tools/test_c3x_029_p9_r12_factorial_numeric_contrasts.py.
Original May game2 2x2 reported nodes = [20062,41685,46783,47563], so difference-in-differences 47563-41685-46783+20062 = -20843 nodes. Reported root cp [-8,-8,+1,-4] yields -5 arithmetic cp contrast; this is NOT b1b4-vs-e1g1 score margin or natural TT×SEE mediated effect. Categorical b1b4 indicator contrast is +1.
Game11 nodes [64424,68114,64426,68116], yielding zero 2x2 node contrast; cp [-95,-104,-95,-104] yields zero, and final-joint-choice indicator contrast zero. These differences are developmental, within one position each. Static arithmetic confirmed; unit-test scripts committed but not executed in remote repository.

## R13: replay metadata preflight
Tool tools/c3x_029_p9_r13_replay_metadata_gate.py, tests tools/test_c3x_029_p9_r13_replay_metadata_gate.py. Ensures frozen game2 source SHA, SF16 upstream SHA, threads1/hash16/NNUE false/depth12 O STRICT, separate TT0 sham vs TT1 reader block, and SEE original-site contact exactly once per arm while boolean mutation only occurs for SEE_FLIP. Requires >=2 declared cold processes/arm, declared binary and patch SHA shaped as 64 hex characters, complete per-arm evidence keys. A nonoriginal depth is CONFIGURATION_SHIFT, not failed original parity. Mismatched source hash or wrong arm set aborts.

**Code-review correction preserved:** original R13 draft mistakenly required a TT-reader contact in both untreated and treated arms. This was corrected in follow-up commits with strict TT0-vs-TT1 and SHAM-vs-FLIP checks. Another correction changed a brittle subset check to required-key containment and renamed the result METADATA_ELIGIBLE_NOT_VERIFIED_REPLAY, because merely declared binary/patch hashes are not byte-verified. Tests updated accordingly. Do not erase mistaken earlier commit from history; this is precisely why microcommits improve auditability.

## Research limitations
No synthetic metadata fixture proves actual native contact. The entire test suite has not been executed against a local repository checkout in this turn, and GitHub content was created via connector commits, not local filesystem sync. No private May PGN or raw key shared. To graduate from metadata eligibility to native pass, re-fetch original protected inputs, hash raw bytes, rebuild exact pinned source, replay cold arms with independently parsed logs, and compare UCI/nodes/cp/depth against archived receipt. Only then consider configuration shifts or root candidate bounds.

Source: c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json.
