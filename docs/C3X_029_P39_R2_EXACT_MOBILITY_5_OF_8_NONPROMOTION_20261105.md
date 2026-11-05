# C3X 0.29-P39/R2 — Exact Reply-Robust Counterplay Option Count: 5/8 Variation, No Value Promotion

**2026-11-05 KST. Actual full-history 16-world chess-law computation and a separate replay-based verifier PASS; science status DEVELOPMENT ONLY, NOT chess-value prediction.**

## Prior results respected

P39/R1 exact forced mate-by-second-turn: 0/16 TRUE, all 16 FALSE. P37 24k PV dominated the old shallow material heuristic both versus same-engine 96k labels (11/15 vs 4/15) and human reply behavior (4/6 vs 1/6). P38 independent Ethereal method technically invalid at native node gating, STOP. No silent new source or retuning.

## Precommitted R2 target

Original protocol committed in `docs/C3X_029_P39_R2_ADVERSARIAL_COUNTERPLAY_MOBILITY_PREOUTCOME_20261105.md` at `0acf6810eaca593bbc851c321d0a8452b98949f4` BEFORE computing the new R2 W labels. Source already exposed: original P37 eight separate events and two previously frozen 24k SF16 candidates per case, same original source SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361` and prediction member SHA `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`. This is not a newly blinded holdout.

Define W(s,m)=max over ALL legal opponent first replies r of min over ALL legal own followups u of the number of legal opponent moves after s,m,r,u. Lower is better *only with respect to constraining immediate opponent mobility*. Immediate checkmate is 0, terminal draw/stalemate 256. Never call W win probability, perfect-play move value, future strategic plan worth or human teaching efficacy. The tactical option proxy may reward forcing checks without positional compensation.

## Actual two-run native chess-law evidence

First [actual CI 41992848026](https://github.com/WhoSia/C3X/actions/runs/41992848026) SUCCESS with six synthetic tests and all 16 original-world branch audits. We identified a weakness: its purported verifier re-called the same production calculation. Replaced it with a genuinely separate push/pop complete legal-universe replay implementation, retaining identical input and output requirements. Second [actual independent-verifier CI 41993256831](https://github.com/WhoSia/C3X/actions/runs/41993256831) SUCCESS, all synthetic tests, 16 original worlds and full independent replay. The two output JSON documents are **byte-identical**, original JSON SHA256 `84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf`.

Actual source-executed legal expansion count **25,554** across all 16 worlds, including **644 legal opponent first replies** total. Zero technical HOLD. There are **5/8 candidate pairs with unequal W, 3/8 exact ties**. On the 5 unequal pairs, *lower W preferred the SF16 first-ranked 24k candidate in 2/5 and the second candidate in 3/5*. This is a descriptive post-label agreement tally, not a preregistered hypothesis test, and search rank at 24k is not chess truth.

## Exact original case ledger

| Original event | SF16 candidate 1 W | SF16 candidate 2 W | Δ first-second | Interpretation against SF16 ranking |

|---|---:|---:|---:|---|

| Sahel | 36 | 34 | +2 | contrary |

| KazChess Masters | 54 | 44 | +10 | contrary |

| Chinese League | 45 | 52 | -7 | agrees |

| Clutch Chess | 33 | 33 | 0 | tie |

| Freiburger | 39 | 39 | 0 | tie |

| Magdeburg | 28 | 29 | -1 | agrees |

| Cerrado | 34 | 32 | +2 | contrary |

| Greg Hjorth | 51 | 51 | 0 | tie |

## Methodological counterargument and PI stop decision

Exact all-reply minimax and legal proof do not guarantee a strategically useful explanation. The W score may be low because a sacrificial check momentarily reduces response options, even when that move is chess-wise worse. Thus R2 crosses a **discriminability feasibility gate** (≥2 distinct candidate pairs), but fails to justify **value validity, root-choice causation, near-tie stability or explanatory superiority**. Do not optimize W thresholds or postselect events for sign alignment. Retain as a negative/control proxy with full original denominator.

Next scientific path: define an opponent-conditioned **value-bearing plan invariant** with independent reference and explicit losses, not purely legal feasibility or mobility. Two separate requirements: (A) plan quality versus strong PV+simple foil-aware rivals, with identical chess-law expansions/native nodes and abstentions, and (B) natural source-root choice mechanism only where NNUE route-to-decision has intervention evidence. A new event/game-disjoint prospective cohort with frozen candidate identities and multi-budget stability remains mandatory before promotional claims. Do NOT repeat source-only measurement under multiple arbitrary metric names.

## Bytes and audit trails

[New independent verifier GitHub source](https://github.com/WhoSia/C3X/blob/main/tools/c3x_029_p39_r2_adversarial_mobility.py); [unit tests](https://github.com/WhoSia/C3X/blob/main/tools/test_c3x_029_p39_r2_adversarial_mobility.py); [read-only workflow](https://github.com/WhoSia/C3X/blob/main/.github/workflows/c3x-029-p39-r2-adversarial-mobility.yml). Original second-run CI ZIP SHA256 `8f8b062f845de24643698a1bf71a142ede310b7d9bb1bda22a9f15dd341577ea` was [uploaded to Drive](https://drive.google.com/file/d/1qmjDqZAY882WyDzFmuarEEA7TTfgPhdj/view) and re-downloaded with exactly the same SHA256. GitHub user-authored commits only, github-actions[bot] never author/committer/push/merge/tag/ref changes.