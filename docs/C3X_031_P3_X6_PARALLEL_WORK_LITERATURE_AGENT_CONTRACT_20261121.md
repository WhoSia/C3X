# C3X 0.31/P3-X6 — Parallel Work literature-agent handoff, source custody, and conflict boundary

**2026-11-21 · Operational protocol. Not a new native research result.** The pre-existing authoritative C3X 0.31/P3-X5 file [literature possession and unlocated 5](C3X_031_P3_X5_LITERATURE_POSSESSION_MISSING_AND_PARALLEL_WORK_20261121.md) is already merged in `main`. This P3-X6 is a **non-conflicting specialist Work handoff**; it does **not** reopen P2 predictive verdict, modify P3-B preregistration, or claim papers were downloaded.

## 1. Frozen research and task identities

- C3X GitHub repository: [WhoSia/C3X](https://github.com/WhoSia/C3X). Baseline when this handoff began: `3a1832e4df7e6b7cf31ca5378e594811d6d8dff2` (update with a fresh GitHub main read before any write).
- Central lab Notion [C3X active](https://app.notion.com/p/41fef561cf9281ae8a62d4c153f11c01); existing specific [P3-X5 literary audit](https://app.notion.com/p/41fef561cf9281de97e8f42d1610d5aa).
- Google Drive Research OS [00_INTAKE](https://drive.google.com/drive/folders/1MLtYh0pv8QUZDReYzRqjDrOjRkSJAD16), [10_PAPERS current shared literature collection](https://drive.google.com/drive/folders/1D2M4LHcejREhlyp6vTd71xxLLx-6ldUP).
- Original [P3-B exact native TT/history/budget mediator transplant preregistration](C3X_031_P3_B_STATE_FAMILY_TRANSPLANT_PREREG_20261121.md) **must not be retrospectively edited**.
- Pre-existing native findings [P3-A1 root-only state insufficiency](C3X_031_P3_A1_ROOT_ONLY_STATE_SUFFICIENCY_COUNTEREXAMPLE_20261121.md) and [P3-X4 off-target root/terminal reconvergence](C3X_031_P3_X4_TWO_HISTORIES_THIRD_WINNER_CAUSAL_SPILLOVER_20261121.md) are separate mechanism development cases, not newly validated generalization.
- Source engine code owner (this chat) alone may write Stockfish patches, CI native workflows, game treatment code, README science claims, `receipts/` original source results, or P3-B protocol.

## 2. Work literature-agent role split

This is **one specialist Work run**, logically organized into four analysis roles. The Work UI may not expose actual parallel model-agent spawning. Distinct roles are a reasoning/checking workflow; do not claim that physically independent agents were spawned without proof.

| Role | Responsibility | Artifact |
| --- | --- | --- |
| Acquisition/rights | Official publisher, author-accepted, institutional and conference open-access PDF identity; access and license assessment | Exact publisher URL, permitted retrieval state, ISBN/DOI, no shadow-library path |
| Bibliographic/byte forensic | Drive file ID, real PDF mime/byte SHA256, page range/title/author/year, exact and near duplicate classification, version provenance | Source manifest with status and evidence |
| Mechanism reading | Source-level argument, model assumptions, theorem/algorithm, how it supports or contradicts P3-B TT/history/value-of-computation hypotheses | Page-grounded summaries; no fabricated page citations |
| Adversarial auditor | Attempt to falsify each authorship/edition claim, distinguish game-rule path history from engine computational history, detect unearned novelty or false causal mediation | FAIL/HOLD/PASS decisions with reasons |

**Strongly recommended model for reasoning-heavy Work session:** choose **GPT-6, High**; use **Extra High** if available and the full audit + source cross-check fits the plan. High reasoning configuration belongs to the Work session/model selector only if the UI offers it; it is not a guarantee of four independently running model instances. For routine raw-file bookkeeping, Medium is sufficient but **not** a substitute for High review of ambiguous identity/causal arguments. Avoid `gpt-5.6-sol`, consistent with the established Research OS operational policy. Verify actual model capabilities in the user's UI rather than inventing model entitlements.

## 3. Exactly five open/unlocated distinct bibliographic items

| ID | Priority | Publication | Source |
| --- | --- | --- | --- |
| C3X-LIT-001 | P0 | Kishimoto and Müller (2004), *A General Solution to the Graph History Interaction Problem*, AAAI 2004, pp. 644–649 | https://s.aaai.org/Papers/AAAI/2004/AAAI04-102.pdf ; author copy https://webdocs.cs.ualberta.ca/~mmueller/ps/2004/aaai-ghi.pdf |
| C3X-LIT-002 | P0 | Schaeffer (1983), *The History Heuristic*, ICCA Journal | https://doi.org/10.3233/ICG-1983-6305 |
| C3X-LIT-003 | P1 | Russell and Wefald (1989), *On Optimal Game-Tree Search Using Rational Meta-Reasoning*, IJCAI 1989 pp. 334–340 | https://www.ijcai.org/Proceedings/89-1/Papers/053.pdf |
| C3X-LIT-004 | P1 | Hay, Russell, Tolpin and Shimony (2012), *Selecting Computations: Theory and Applications*, UAI 2012 pp. 344–353 | https://proceedings.mlr.press/r10/hay12a.html |
| C3X-LIT-005 | P2 | Warnock and Wendroff (1988), *Search Tables in Computer Chess*, ICCA Journal | https://doi.org/10.3233/ICG-1988-11103 |

**Do not conflate** the already present [Kishimoto & Müller 2005 DFPN paper](https://drive.google.com/file/d/1Q_T8JQT2Wa0aqWEJeLQAUq_c09fBSgOV/view) with the distinct missing 2004 AAAI GHI paper. Already present source PDFs include [Russell–Wefald 1991](https://drive.google.com/file/d/1SAvlhQSvPEXTV4QxmsnrCZtzWk-x9ZWT/view) and [Geiger et al. 2025](https://drive.google.com/file/d/1i_i_cFFv6vqYHaBOgKK9AbuprPtj8v91/view); a [second Geiger file](https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view) is NOT an exact byte duplicate until SHA confirms.

## 4. Mandatory acquisition and error semantics

1. Before downloading, query connected Drive by **exact and normalized full title**, author, DOI and target folder parents. Discover actual file IDs; avoid duplicate reimports. Different file name or scan means unknown until pages and original bytes checked.
2. For a confirmed legitimate public PDF, acquire original bytes using Work browser/available connected tools, stage into **00_INTAKE**, calculate SHA256 and inspect PDF first page, last page, page count and title. Move original ID or create a clearly named final file in **10_PAPERS** only after source/edition/dedup gates. Preserve the current organizational structure and original references. If a PDF is already correctly in 10_PAPERS, *do not re-download it*.
3. For paywalled original journal articles, search legal author/institution/preprint copies. If none, leave `NOT_LOCATED / LICENSED_ACCESS_REQUIRED`; save exact bibliographic/DOI info and legal request link, not a false "acquired" status. Never use access bypasses or sites distributing unauthorized copies.
4. Data row schema: `id, authors, year, exact_title, venue, DOI_or_canonical_id, publisher_url, candidate_open_pdf_url, drive_file_id, drive_path, mime_type, pages, version, sha256_bytes, existing_matching_sha, content_first_last_page_verified, status, relevance_P3_B, relevance_P3_X4, novelty_overlap, rights, notes, verified_at`.
5. Work should write **separate dated literature-only research records** in Research OS/Notion child page, not edit historical original P2/P3 results or P3-B source experiment. Do not create local sandbox archives as permanent result. Review and preserve exact evidence URLs and Drive file IDs.
6. Work may independently survey secondary citations and promising 2020–2026 work, but append them as *NEW CANDIDATES*, not silently inflate the existing five-open-item denominator. Cite prior work without granting it unquestionable authority; critique its assumptions and possible failure conditions.
7. Work MUST treat prior source claims about general graph history, TT replacements, and choosing computations as established possible antecedents, not C3X novelty. C3X's present specific observation is a source-verified **finite conditional third-root response**, not identified post-gate TT/history/budget mediation nor beneficial chess strategy.

## 5. Completion gate and this-chat handback

Work output: (A) linked final 5-row file state table with strict proof type, (B) verified bibliographic + source-page methodological notes, (C) actual Drive folder/file IDs and SHA records, (D) unresolved failures, (E) independent research-graph recommendations to P3-B and X4, (F) link to new dated Notion and Drive artifacts, (G) four short wrap-up lines: completed / next / blocked / user input.

**Conflict resolution:** This chat owns **C3X original engine/causal code and source interpretation**; Work owns **literature acquisition and bibliographic inventory only**. Any optional GitHub Work commits must go to `research/c3x-031-literature-work-20261121` (or date-labeled distinct branch), touching only `docs/literature/` or a dedicated handoff document, **never main, Stockfish source, research result receipt, README scientific verdict or P3-B prereg**. Human-author commits only; GitHub Actions must not author. Leave PR for review rather than automatic merge in a parallel session. Merge decisions require comparing current main, file paths and status to avoid cross-agent overwrites.
