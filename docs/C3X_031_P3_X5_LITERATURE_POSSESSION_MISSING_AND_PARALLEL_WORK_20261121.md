# C3X 0.31/P3-X5 — Literature possession audit and missing originals (2026-11-21)

**Scope and honesty:** Actual connected Google Drive file metadata, exact-title/name searches across accessible files, and first-page extracted text from three readable PDFs. This does not prove every inaccessible or differently named file is absent. No new paper has yet been downloaded, moved, or refiled. Book and repository source are not automatically journal papers.

## A. Verified or identified source possession

| Work | Research OS status | Source and use |
| --- | --- | --- |
| Russell & Wefald (1991), Principles of Metareasoning | **PDF present, first page and real text verified** | [Drive](https://drive.google.com/file/d/1SAvlhQSvPEXTV4QxmsnrCZtzWk-x9ZWT/view); theoretical metareasoning, existing prior art |
| Geiger et al. (2025), Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability | **PDF present, first page and real text verified** | [Drive canonical](https://drive.google.com/file/d/1i_i_cFFv6vqYHaBOgKK9AbuprPtj8v91/view), [second file labeled Duplicate](https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view). Do not assume byte-identical without SHA check |
| Kishimoto & Müller (2005), A Solution to the GHI Problem for Depth-First Proof-Number Search | **PDF present, first page and real text verified** | [Drive](https://drive.google.com/file/d/1Q_T8JQT2Wa0aqWEJeLQAUq_c09fBSgOV/view). This is the df-pn paper, NOT the distinct 2004 AAAI general GHI paper |
| Breuker, Uiterwijk & van den Herik (1994), Replacement Schemes for Transposition Tables | **PDF present, IMAGE SCAN, visually unverified** | [Drive](https://drive.google.com/file/d/18cL-ECAavR4ZDw3rfwB2VOR7_GQCFEUg/view); TT replacement and generation hypotheses |
| Schaeffer & Plaat (1996), New Advances in Alpha-Beta Searching | **PDF present by exact filename; full body unchecked** | [Drive](https://drive.google.com/file/d/1hOKgvI6s3ZlWApX8zamOoJEABXJuslun/view) |
| Griffiths, Lieder & Goodman (2015), Rational Use of Cognitive Resources | **PDF present by exact filename; body unchecked** | [Drive](https://drive.google.com/file/d/1Oh9BTVK4mtY6uRhN2r2WqSDGn64IOM9g/view) |
| Callaway et al. (2022), Rational Use of Cognitive Resources in Human Planning | **PDF present by exact filename; body unchecked** | [Drive](https://drive.google.com/file/d/11lmR6cdEBj38-HL8jRh_WJMMkrsJfPr3/view) |
| Schölkopf et al. (2021), Towards Causal Representation Learning | **PDF present by exact filename; body unchecked** | [Drive](https://drive.google.com/file/d/1G1yX6eKweXOxXmWszP4k6XkN4qccG0eE/view) |
| Sutter et al. (2025), The Non-Linear Representation Dilemma | **PDF present by exact filename; body unchecked** | [Drive](https://drive.google.com/file/d/1e4SKpJ4yaYETPCadT-NxOwAat-XuF-Yw/view) |

**Original Stockfish16 sf_16 at commit 68e1e9b3811e16cad014b590d7443b9063b3eb52 is SOURCE CODE, not a research paper:** [search.cpp](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/search.cpp), [tt.cpp](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/tt.cpp). The second TT.probe call is not observationally passive because original probe refreshes genBound8.

## B. Current missing or unlocated PDF acquisition table

| Missing key | Priority | Exact reference and why | Provider-authoritative source | Inventory finding |
| --- | --- | --- | --- | --- |
| C3X-LIT-001 | **P0** | **Kishimoto & Müller (2004), A General Solution to the Graph History Interaction Problem, AAAI, pp. 644–649.** Full history/repetition and graph-search re-use foundations | [AAAI official PDF](https://cdn.aaai.org/AAAI/2004/AAAI04-102.pdf), [canonical metadata](https://mlanthology.org/aaai/2004/kishimoto2004aaai-general/) | **Not located**: no matching exact-title PDF; DIFFERENT 2005 df-pn GHI article is present |
| C3X-LIT-002 | **P0** | **Schaeffer (1983), The History Heuristic.** Direct historical source for dynamically reordered tree search | [publisher DOI](https://doi.org/10.3233/ICG-1983-6305) | **Not located**: exact-title file missing; official journal copy may be access-restricted |
| C3X-LIT-003 | **P1** | **Russell & Wefald (1989), On Optimal Game-Tree Search Using Rational Meta-Reasoning.** Actual game-tree computation choice and objective | [IJCAI original PDF](https://www.ijcai.org/Proceedings/89-1/Papers/053.pdf), [metadata](https://ijcai.org/proceedings/1989/53) | **Not located**: 1991 journal article present but distinct |
| C3X-LIT-004 | **P1** | **Hay, Russell, Tolpin & Shimony (2012), Selecting Computations: Theory and Applications.** Bayesian metalevel search and value-of-computation analysis | [PMLR canonical paper/PDF](https://proceedings.mlr.press/r10/hay12a.html) | **Not located**: exact-title PDF search empty |
| C3X-LIT-005 | **P2** | **Warnock & Wendroff (1988), Search Tables in Computer Chess.** Source-grounded TT encoding/consistency and collision issues | [publisher DOI](https://doi.org/10.3233/ICG-1988-11103) | **Not located**: exact-title file search empty; journal full PDF access may be restricted |

**Terminology:** NOT LOCATED = current connected Drive title and folder search failed. It is not conclusive proof of user-wide absence. Status accepted only after exact authors/year/title, source PDF actual pages/text, original bytes and SHA-256. Mark restricted full text honestly rather than copying unlicensed material. Existing scan may be image-only; verify visually rather than claim it contains searchable text. An original publisher URL is not a Drive possession record.

## C. C3X research graph / preexisting theory boundaries

- Russell & Wefald 1989/1991 and Hay et al. 2012: bounded metareasoning already formalizes choosing computations; a changed source root bestmove does not establish a beneficial computation without independent chess utility and cost.
- Kishimoto & Müller 2004/2005: graph history interaction concerns path-dependent game rule/solution semantics and TT reuse. Distinguish full chess-rule history from the hidden computational search history.
- Schaeffer 1983, Breuker et al. 1994 and the exact original Stockfish16 code: move ordering and TT replacement/age are established mechanisms, but which post-R33 source TT/history/budget field physically mediates a P3 root flip remains unknown.
- Geiger et al. 2025: intervention-preserving causal abstractions preexist C3X. P3-A1 temporal root-ledger insufficiency and P3-X4 third-root score-only counterexample are finite source-level falsifiers for TWO LIMITED abstractions, not a proof of universal minimal state.

## D. Work vs this-chat parallel ownership

**Work literature lane:** verify all five missing originals and existing duplicate/scan; use browser and connected Drive; acquire legal full source PDFs into Research OS 00_INTAKE first, verify original bytes, promote into 10_PAPERS only after bibliographic/duplication/quality gates. Maintain status with Drive file IDs, canonical title/year/DOI, URLs, byte SHA256 and explicit file state. Save a date-stamped Google Drive inventory/Notion child page. Avoid source code, README, native CI workflows, TT experimental patches, or historical existing research receipts.

**This chat's C3X development lane:** keep original [P3-B state-family transplant preregistration](C3X_031_P3_B_STATE_FAMILY_TRANSPLANT_PREREG_20261121.md) frozen; develop physical original Stockfish16 TT writer-reader and reverse restoration; use the [P3-X4 third-winner off-target](C3X_031_P3_X4_TWO_HISTORIES_THIRD_WINNER_CAUSAL_SPILLOVER_20261121.md) as independently labelled exploratory mechanism case. Do not silently alter research claims based on literature acquisitions. Use GitHub author commits only; Github Actions bot must not create commits. Synchronize by Notion links and Drive file IDs rather than concurrent edits.

**Verdict:** At least 9 relevant paper PDFs with varying verification confidence were located; **5 distinct relevant classics remain unlocated**. This audit itself introduced no new native Stockfish searches and did not retrieve any new paper originals.
