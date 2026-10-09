# C3X 0.18 — Case11 Five-Reader Exhaustive Coalition Court

**ADAPTIVE / fixed-source**, filed after (a) December twelve role native outcome and (b) grouped-only age64 TT root flip and (c) all five singleton source root calls 9–13 (each fully realized without flipping root). This is *not* a new independent population, cannot retroactively rescue original December D1/D2 or establish unique natural TT mediation.

Pinned chess source `51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd`, previous singleton native JSON SHA `8e1ac0f02e63a9db93564181a7dd86162a552a5cb73493d5053e41573c4cf615`. Same December source #11, same original full six-field legal FEN, Stockfish16 original source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, depth12, Threads1, Hash16, NNUE off, root F, physical TT target `(key64=16448589199907615799,slot=0,epoch=2)`.

**Frozen exhaustive intervention:** Each of all **32** subsets `S ⊆ {9,10,11,12,13}` is encoded as a five-bit mask `0..31` (`bit i` means root call `9+i` is eligible). Source V suppresses a TT bound-conditioned *value-as-eval consumer* exactly when the unchanged physical triple matches, the global accepted-write age since the last writer is **>=64**, and the native current root-call ID is included in S. Any other reader must remain unchanged. A mask=0 must have zero contacts and identical six-field UCI to original source F. Mask=31 must reproduce the previously frozen age64-all native result, including its final UCI and source gate contact count. Each subset is executed **two cold native processes**. Retain every subset, contact sites (and root-call IDs), status, bestmove, full six-field UCI, writer raw payload witnesses and source hashes.

**Set-function object:** `Y(S)=1` iff the categorical bestmove after intervention in S differs from source F, under fixed run conditions. The operator is not a simultaneous independent swap of five fixed events: intervening earlier can change the search trajectory and later events may or may not be encountered. Exclude any claim that numeric root calls across arms are always equivalent.

**Risk gates written before these combinatorial outcomes:**
- `C1_PAIR_SUFFICIENCY`: at least one 2-element subset flips root bestmove (otherwise FAIL).
- `C2_LOWER_THAN_FIVE`: at least one proper subset flips root bestmove (otherwise FAIL).
- `C3_FULL_GROUP_REPLAY`: mask31 reproduces previously frozen 5-contact group result exactly, and mask0 matches untouched F with no contact.
- `C4_SINGLETON_NONFLIP`: all five mask 1,2,4,8,16 subsets physically fire but do not change bestmove, matching frozen previous singleton output.
- `C5_FULL_COURT`: all 32 masks present, each two cold identical, and every emitted reader_block has root_call in selected mask plus last writer full64/raw payload equality. Any missing or nondeterministic => HOLD FAIL-CLOSED.
- `C6_INCLUSION_MONOTONICITY`: If any inclusion pair `A ⊂ B` has `Y(A)=1` but `Y(B)=0`, this monotonicity prediction FAILS. It is not assumed true by theorem.

Compute all inclusion-minimal successful sets, their sizes and distinguish **singleton sufficiency (none)** vs **group sufficiency** vs **inclusion minimality**. Even a pair success is a *finite source-conditional causal interaction of interventions*, not a proof of natural modular additivity or unique physical TT root mediator.