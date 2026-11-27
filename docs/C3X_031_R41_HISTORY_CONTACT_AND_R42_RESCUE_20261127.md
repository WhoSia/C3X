# C3X 0.31 R41 — native scalar history contact; R42 sparse rescue design

R41 PASSIVE CONTACT VERIFIED; R42 conditional reciprocal sparse H7 rescue PASS; general mediator sufficiency HOLD. Original P3-B preregistration unchanged. One exposed P2-028 source game; depth15/16 share the same prefix.

## Observed native results
R41 exact R33 stack rebuilt, scalar StatsEntry read/write observer, full four-array checkpoint snapshot, physical source event19, normalized UCI/root trace/node parity across baseline, off, on0 and on1. 16 fresh native searches; run [46020749192](https://github.com/WhoSia/C3X/actions/runs/46020749192). At attempt17 (root14/completed13), nine scalar cells differ: main2, continuation6, countermove1, capture0. Seven different cells actually undergo a conversion read before first write and before frozen Y1; both arms have same seven. First such contact serial291 (main index6556, 6626 vs6235), then continuation index1743516 serial293. Complete source-ledger replay passed, no unclassified scalar address escapes. Per arm 141982/141441 accesses in attempt17; Y1 serial139630/139089, 2265/2280. These are contact witnesses, not individual causal effects.

| family | index | sham | both | before-Y1 contact |
|---|---:|---:|---:|---|
| main |6556|6626|6235|yes|
| main |7738|-4914|-4742|yes|
| cont |1427100|-71|-282|no|
| cont |1427258|11252|11384|yes|
| cont |1741468|-71|-282|no|
| cont |1741626|-196|15|yes|
| cont |1743516|-2039|-2236|yes|
| cont |1743674|881|1086|yes|
| counter |369|3642|2460|yes|

Node-dependent draw alternative: original SF16 value_draw returns VALUE_DRAW-1+Value(nodes&2). Nodes at checkpoint 7699 vs7717; actual before-Y1 draw calls 12 vs17, first two at serial7644/7834, (7906,+1)/(7908,-1) vs (7924,-1)/(7926,+1). First differing scalar read precedes first recorded draw call, but this alone cannot identify which path causes Y1. A different draw-return sequence can be effect or mediator. Stack/root/pawn/material state not fully mapped. Do not claim H sufficient yet.

## R42 frozen conditional experiment
H7 seven observed contact cells; P2 two noncontact cells. Both receiving natural arms, depths15/16, self-copy/H7 reciprocal/P2 reciprocal, two cold repeats (24 planned). Before ANY change compare entire native receiving four-array byte image against SHA-pinned R41 natural receiver; after change require entire native image equals independently constructed expected donor-cell splice. Only these scalar bytes modified; no node reset, no TT/stack/root or draw rule change. Source contact gate retained, same depth, self full root trace parity, cold exact repeats. Y1 same attempt/iteration/move/common alpha; Y2 same iteration and original window; report misalignment separately rather than interpreting an unmatched candidate as rescue. P2 is a negative-control candidate on natural pre-Y1 trajectory, not a priori proof of no effect on Y2 or on a new path. No broad H-family sufficiency, no independent tournament replication. [R42 run 46021292891](https://github.com/WhoSia/C3X/actions/runs/46021292891).

## Product and literature
Browser now accepts optional standard-start UCI history matching FEN, transmits it to analysis, displays repetition claim scope, disables unsupported strategy/mirror history endpoints, rejects stale asynchronous results after input revision and invalid history, clears history on reset. Real Chromium + Stockfish [run 46020775700](https://github.com/WhoSia/C3X/actions/runs/46020775700) PASS including 7-ply repetition case and invalid input. Not full PGN import or learner-efficacy evidence.
Drive search confirms already-owned Press & Golubev (2026), *Explaining Chess and Go in Natural Language* [PDF](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view) and Parfenova (2026) [PDF](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view). No new missing PDF entry. New public benchmark lead [GMBench](https://github.com/chessifyme/gmbench), expert-answer-key explanation evaluation; [Hindsight methodology](https://hindsightchess.com/methodology/) explicitly retains history for analysis. Feature/methodology leads only, no actual competitor evaluation. Do not claim history retention or contrastive explanation as novel.

## Raw custody
[Native R41 ZIP](https://drive.google.com/file/d/1TSryjwrW1gmlY5AR-OUyxMjBnb0UksiG/view), 40550810 bytes, SHA256 dc42f92f1a32d2f6a1fc82ffda5a8c72e03a650225bb6af8005ae1044a6b534f; downloaded CI artifact and remote Drive readback agree, ZIP CRC verified. 60 members. Aggregate receipt e4c634c3269e8ba9d801314a82ffe092c517595d8271f4b1052d619ee85b6928. Observer SHA256 2901ec40567a8f83c7fcb25a9ce5e587064c28bc35d08e2c7a345a8aa60537fb. R42 source frozen prior to outcomes; no outcome claim until actual logs. No legacy code deletion in this iteration.

## R42 execution audit
First run 46021292891 successfully built R42 but stopped before any native search because the workflow passed an extra baseline positional argument. Corrected only the invocation in 1da30218d7bd16c0a4959a209cdc3aa70b7f786b. [Corrected run 46021455971](https://github.com/WhoSia/C3X/actions/runs/46021455971) was observed to pass the source build and enter native execution; final results pending at this checkpoint. Preserve the failed run; do not include it in a native search denominator.

## R42 completed — reciprocal conditional H7 rescue
Corrected run 46021455971 PASS, 24 actual native searches (12 cells x two cold repeats), all full receiver-image and post-restore byte-image checks, original event19, completed depth, aligned Y1/Y2, self-copy root trace and cold repeat gates passed. No search in first CLI-failed run counted. At depth15 and16:
| receiving arm | intervention | Y1 | Y2/update | bestmove |
|---|---|---:|---|---|
| sham | self or P2 |2265|2238/0|d4e5|
| sham | H7 from both |2280|2256/1|f4e5|
| both | self or P2 |2280|2256/1|f4e5|
| both | H7 from sham |2265|2238/0|d4e5|

Native cumulative nodes depth15 self sham/both 18263/20963; H7 sham/both 20945/18281. Depth16 self 35662/36217; H7 36199/35680. Node counters were not altered; post-checkpoint work matches opposite natural arm's count in each H7 direction with original +/-18 node offset preserved. Both directions reproduce exact endpoints, not merely a movement toward them. P2 placebo preserves own endpoints and node counts; this does not prove the two cells are irrelevant everywhere.

Raw trace independent readback: first two draw calls on sham/H7 retain sham (7906,+1),(7908,-1); on both/H7 retain both (7924,-1),(7926,+1). Draw call totals before Y1 switch 12->17 and 17->12 respectively. Hence changing the first two draw return signs to the donor's is not necessary for this reciprocal rescue; cannot exclude subsequent draw effects, interactions or pre-checkpoint mechanisms. No unique mediator, no claim of universally minimal H7, no independent cohort. Strong bounded causal witness: conditional H7 state interchange transfers the specified Y1/Y2/choice in both observed receiving worlds at two dependent depth settings. Next: leave-one-out / family ablation with held-fixed controls, rival draw policy intervention, independent new-family prospective validation. Broad P3-B/HOLD on sufficiency beyond this source persists.

[Native CI](https://github.com/WhoSia/C3X/actions/runs/46021455971); [Drive original ZIP](https://drive.google.com/file/d/1ButYogns-IdZNL9PxWL863AwbqUPb85s/view) 52914075 bytes, SHA256 0090d3c0007275410e6a2b8f8e8168b07aff0d10680f590cdb43dafdc0f66f04, CRC all 124 members PASS, re-downloaded matching hash. Aggregate fd88d6312bc5866251b3f470597f37c0eaaabc677765bc9fffe037147725d02d, observer c65014a43fd7261ce65eeac10bb496bc307dbfc08349a4417b306a71c67f29c9.
