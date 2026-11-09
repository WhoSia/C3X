# C3X 0.29-P42/R24 — Actual Response-Conditioned Source Plans and Independent Legal Chess Adjudication

2026-11-09 KST. This is the **B-axis DFS** in a PI-controlled BFS/DFS portfolio, NOT an isolated "better regret metric" paper. It retains original A (Game14 physical search cause), C (new source transport), D (NNUE source mechanics), and E (strong published comparison), and requires them to converge on the **same heldout chess position and future** before a flagship causal-strategic claim.

## 1. Reconstructed experimental chronology and true bytes

### B1 PRE-REFERENCE SOURCE PLAN (actual native success)

The [read-only B1 native run #42565383643](https://github.com/WhoSia/C3X/actions/runs/42565383643) rebuilt **unmodified pinned official Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`**, Threads=1, Hash=16MB, `Use NNUE=false`, fixed depth12. It reopened the original 2026 October P37 source and original pre-judge P37 predictions with strict SHA+all legal game moves, selected exactly the **two R22-adaptively exposed Sahel/Cerrado cases**, four frozen root candidate moves, and enumerated their **40+40+32+35=147 complete legal first opponent replies**. For EVERY source `s,m,r`, it searched the source engine independently and FROZE its next own action `u_S(s,m,r)`, actual depth and nodes. **No Berserk reference calls occur in this B1 program.**

Successful raw B1 action vector `C3X042_R24_B_PREJUDGE_147_REPLY_CONDITIONED_OWN_CHOICES.json` independently downloaded and SHA-256 checked: ZIP artifact #13650858868 `808f1375ed03f843a6f5f6804c3364b1eb561600b7dbed40d08faec68b0d5100`; JSON member `3c8f2a57cefe19fcb7a00925f4434f5008195bce5adeba1e67dc84f18f084f34`. Source search nodes across 147 plans **8,563,329**. No claimed special cost-matching to independent referee or Cui/BinProp.

### B2 SOURCE-BLIND INDEPENDENT REFEREE (actual native success)

The separate [read-only B2 native run #42565712361](https://github.com/WhoSia/C3X/actions/runs/42565712361) downloaded the **already SHA-frozen B1 artifact**, verified exact B1 JSON digest BEFORE any analysis, downloaded the immutable P37 source/prediction artifacts again, rebuilt a different chess-engine family **Berserk14 commit `8ae895a6151695be4a50d4fb65b0c131659c513a`** with NNUE network SHA `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`, Threads1, Hash16MB.

For **each of 147** legal opponent replies at depth **12 and 16**, independently compared:
- `J_d(s,m,r)`: Berserk unrestricted search after that reply (Berserk chooses own next response);
- `J_d(s,m,r | root_moves=[u_S(s,m,r)])`: same Berserk source/nominal depth but forced to the PRE-JUDGE source next own action.

Total = **147×2 depths×2 searches = 588 independent referee analyses**, all 4 root candidates had full legal reply coverage and admitted finite values at both depths. Actual nodes: unrestricted d12 **5,577,343**, forced d12 **3,823,359**, unrestricted d16 **36,609,590**, forced d16 **30,740,424**: judge total **76,750,716**. Actual node budgets **were not equal** between free/forced, and depth matching is not score/cost calibration.

The B2 original JSON `C3X042_R24_B_JUDGED_REPLY_CONDITIONED_OWN_PLAN.json` was independently downloaded, ZIP artifact #13651426096 SHA `bcd78e80c0d5544ebe4ee1821e708ccb6e582bfc800a7c9617b050ab93484df5`, JSON SHA `2fd30e135a1d4f4575b71cd263f01fdd363659fe3f05b6cafc653dc98646e365`.

## 2. Concrete actual source-policy × independent adversarial consequence

Scores in centipawns from the **original root mover's** point of view, after *worst of every legal first opponent reply*, at Berserk depth16. They are finite-depth search estimates, not objective game-theoretic truth:

| Exposed historical game | Pre-frozen candidate | All legal first replies | Worst unrestricted Berserk-own next move | Worst forced pre-frozen SF16-own next move |
|---|---|---:|---:|---:|
| Sahel | e5f4 | 40 | +73 | **+64** |
| Sahel | e5c3 | 40 | +71 | **+62** |
| Cerrado | e5f6 | 32 | **−19** | **−65** |
| Cerrado | d1c2 | 35 | −36 | −36 |

This is the pivotal **candidate-choice/policy-dependent counterexample**: in Cerrado the apparent two-root ordering under independent unrestricted own continuation is `e5f6 > d1c2` by +17cp, whereas judging the actual PRE-FROZEN source policy gives `e5f6 < d1c2` by −29cp. A root-action preference and the realizable continuation policy are **not interchangeable**, even when both values come from the *same* independent chess referee with full first-opponent-reply coverage. This is a mechanistic strategic motivation, not a proof source NNUE/TT causes a choice.

More falsification:
- Sahel source plan d12 worst values e5f4 **+62** vs e5c3 **+68** (prefer e5c3), but d16 **+64** vs **+62** (prefer e5f4). Thus root ordering of the frozen *same plan* is unstable with reference depth.
- Cerrado source plan d12 e5f6 **−80** vs d1c2 **−40**, d16 **−65** vs **−36**.
- At depth16, source selected a different immediate next move from Berserk's unrestricted PV for **46 of 147** response conditions. At depth12 the count was 50/147. These describe *search policy disagreement*, not correctness labels.
- Crucial calibration limit: depth16 signed `J_unrestricted − J_forced` was **negative in 55/147** conditions (depth12 **50/147**). Nominal depth-limited unrestricted and forced-root searches visit different trees/consume different nodes and do NOT satisfy a mathematical oracle max inequality in finite search. Never call the signed gaps exact nonnegative regret or claim a formal oracle upper bound. The empirical scores are a **source-policy stress test under an imperfect independent judge**.
- Frozen source plan costs and judged depth/score/cost are logged in immutable aggregate source artifacts; no tuned response selection after reference outcomes, but the two event choices themselves were **selected after R22 reference scores**.

## 3. What this result proves and what it does NOT

**Real supported result:** One can make a source engine commit to a complete policy `r→u_S(s,m,r)` for EVERY legally possible first adversarial reply BEFORE independent continuation judging. On two deliberately selected historical near-tie pairs, a different-family finite-depth judge then finds materially different worst-opponent-reply scores and at least one root candidate-order reversal when evaluating the *frozen own plan* rather than the judge's freer own continuation. This is a real first experimental bridge from search plan selection to strategic consequence under perturbation.

**Not proved:** equivalence between engine values and objective minimax; all-root-support closure; full own-move opponent strategy horizon; cost-matched comparisons; Cui k3 partial-tree, BinProp contrast or Queen explain+play baselines; uniquely source-mediated root action; strong prospective heldout transport. Original shallow C3X three-ply heuristic lost to PV in P37 (1/6 versus 4/6). New B1 is **plain SF16 classical depth12**, NOT the causal C3X explainer or human strategy, and B2 case selection is endogenous to earlier R22 reference values. Do not write a paper claiming superiority.

The correct comparison is **not** whether `min_r J(s,m,r,u_S)` is a substitute for the final chess reason; it is a necessary causal/strategic consistency check. The flagship still asks whether the actual source-computation that chooses root move (m) represents, transmits and acts on the same future-contingent property measured independently on **the same frozen chess case**.

## 4. Next DFS requiring harder novelty and BFS transport

- First, capture **same-position source-native search state** for these B2 cases and test a predeclared intervention targeting the *specific response-conditioned continuation property* vs PV/k3/contrast; Game14 source causal results cannot simply be glued onto unrelated Sahel/Cerrado value scores.
- Upgrade a real **Cui-style k=3 partial response tree** with exact native compute accounting and a **BinProp typed foil/concept** as serious mandatory rivals. Queen (Bhaskar et al., `arXiv:2610.03695`) combines a chess expert encoder and LM with iterative move-explanation consolidation; SARFA (Puri et al. 2019, `arXiv:1912.12191`) addresses action-relative attribution. Existing work constrains the novelty of simply explaining plans, using foil concepts or showing action-sensitive features.
- Freeze a new November source event **before game/engine outcomes**, preserve original raw PGN SHA and full prior exposure checks; historical September/October sources are already exposed. Separate static NNUE difference from mechanistic feature→ancestor→root intervention.
- Publish null/negative outcomes and strong bounded caveats. No model can certify future robust semantic truth from this preliminary forced-root finite-depth experiment alone.
