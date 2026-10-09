# C3X 0.18 — Adaptive December Case11 Late TT Reader Call-by-Call Court

**ADAPTIVE after source group result; not independent prediction.** Source 12-game SHA `51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd`. The last exact age-target native court [#37988654788](https://github.com/WhoSia/C3X/actions/runs/37988654788) has raw JSON SHA `b035c8d184d4c3c474d8592793af442f00fb135276426db1e78d447999609952`. The original unfiltered physical triple `(16448589199907615799,0,2)` affects the bestmove `b2b3→c1f4` at a first reader with age18; an age>=64 grouped V suppresses five reader events and also flips the root, but an *exact* age90/root_call9/ply1/bound2 single suppression does not.

**Frozen adaptive follow-up, no new target selection:** retain exactly the same source game11, original six-field clock, same TT key/slot/epoch, depth12, threads1, Hash16, NNUE off. Native V branch is allowed only if global accepted-write age >=64 and current source-root-call equals each fixed number **9,10,11,12,13**, one caller at a time. Include impossible negative root_call8. Double independent cold process repeat per condition. Do not retry with another call if a condition does not fire. Record `reader_block` events, last physical writer payload, all matching passive TT reads, exact final UCI score/bound/nodes/PV.

**Risk tests:**
- `S1_SINGLE_LATE_EFFECT`: >=1 of those five isolated late root-call gates actually fires and changes final bestmove. Zero = FAIL (not replaced by other calls).
- `S2_SINGLES_COMPLETE`: all five original physical targets and their explicit root calls are tried and records retained; missing contact recorded NOT_FIRED.
- `S3_NO_CONTACT`: wrong root_call8 + accepted age>=64 does not fire and final six-field UCI identical to F. If fires: FAIL-CLOSED.
- `S4_SOURCE_WRITER`: all claimed physically gated readers have full64 and raw writer payload match.

**Causal boundary:** A group flip with no single flip is a source conditional multi-node phenomenon but not necessarily synergy because each standalone treatment changes downstream search trajectory and their collective interaction may depend on non-additive alpha-beta windows. A single effect would identify a sufficient source gate but not the only mediator. This experiment is explicitly after output inspection and may not rescue December preregistered D1.