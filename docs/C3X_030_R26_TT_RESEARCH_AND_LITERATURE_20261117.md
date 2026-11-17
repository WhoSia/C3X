# C3X R26 — Research direction and source inventory

[C3X 1.md](https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view)
opens with players wanting to learn from Stockfish and asking both why a
move is good and why it can be slightly better. The later 0.2.3 note narrows
comparison to near-equal, non-tactical positions because Poupart had
already used contrastive sparse autoencoders on paired chess trajectories.
It also requires testing the reason under multiple strong replies and across
populations. The 0.2.4.2 notes sharpen that requirement to independent games,
semantic blindness and prospective validation. Near ties remain an
informative stress test for explanations throughout the range of margins.

[Poupart's paper](https://drive.google.com/file/d/1jX9SqJCjdOSqmQ0f0r41L8YXJQCL567Q/view)
uses contrastive trajectory representations to probe planning concepts.
[Cui, Ling and Ng](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view)
already motivate strategy beyond the visible principal variation. The
research target for C3X is a *named move contrast* in a real search, with
a manipulable computational witness, legal alternative lines, and a test
of whether the chess explanation survives plausible replies. A feature
mask or a competing PV by itself only identifies part of that target.

## Next experiments by decision value

| Axis | Comparison | What it could establish |
| --- | --- | --- |
| Search consumers | Independently mask TT cutoff, static-eval substitution, singular extension, and the cached raw static eval. Cross the highest-yield gate with MovePicker. | Whether a specific reader or interaction drives the global value-mask phenotype. |
| Memory and history | Compare cold against parent-warmed and unrelated-warmed entries under identical legal history and node limits. Hold engine history constant while selectively retaining TT data. Then test generation and replacement with equal capacity. | Whether effect travels with an entry inherited from an ancestor or derives from what the target search itself writes. |
| Decision transmission | Replay the same selected key, matching depth/flag and writer, under targeted mask, irrelevant-key sham, and restoration, keeping the remaining game fixed. Trace parent return, root alpha/rank and played bestmove. | The local causal role of a TT entry in a specified recommendation. A failed local replay narrows the global phenotype. |
| Chess comparison | For some contrasts compare root A and B against all legal replies at the first layer. Report different minimizers, same legal replies and the moves that realize one verified plan in both. Include alternatives a human could choose and clear tactical losers. | A usable explanation of the candidate difference and its scope across opponent responses. |
| External confirmation | Freeze one fresh TWIC issue and one source outside TCEC, hold out whole events, then repeat at multiple equal depths and node levels. Score discovery and confirmation separately. | Reproducibility beyond the current exploratory cross-source panel. |

Test switching, restored default, invariant recommendation with differing
reply, and a divergent plan under an identical reply as distinct outcomes.
Use only the first two actions to drive case selection for native tracing.
Where the computational and chess evidence disagree, show both results.

## Recovered journal PDF

Kishimoto & Müller (2005), *A solution to the GHI problem for depth-first
proof-number search*, Information Sciences 175(4), 296–314,
[DOI 10.1016/j.ins.2004.04.012](https://doi.org/10.1016/j.ins.2004.04.012).
The former Alberta host redirects to a 404. The [Wayback PDF](https://web.archive.org/web/20250828223058id_/http://webdocs.cs.ualberta.ca/~mmueller/ps/kishimoto-mueller-infsci-ghi.pdf) returns
the 19-page journal article. The [Drive intake copy](https://drive.google.com/file/d/1Q_T8JQT2Wa0aqWEJeLQAUq_c09fBSgOV/view) was downloaded
back and byte-compared. SHA-256
`fff0001fc71f36bb462412b859064f06c10e8004c41869bec3e179b542cf27aa`.

The paper's path-dependent reuse problem motivates preserving full PGN history
for Stockfish replays. The tested algorithm is df-pn under Go's situational
superko.

## 2026-11-17 verified Drive intake

Three user-supplied PDFs were opened from `00_INTAKE`. Two are image scans,
verified by OCR and journal pagination. File names below are the observed
intake names.

| Publication | Verified copy | Scope relevant to C3X |
| --- | --- | --- |
| Breuker, Uiterwijk & van den Herik (1994), *Replacement Schemes for Transposition Tables*, 17(4), 183–193 | [REPLACEM.pdf](https://drive.google.com/file/d/18cL-ECAavR4ZDw3rfwB2VOR7_GQCFEUg/view), 11 pages, SHA-256 `4a0195d37664210cdef47cb16b9dea7e780f920ab2f136d7ef4f1c4b18242d19` | Seven chess middlegame replacement schemes. The two-level scheme using subtree node count is a precedent for varying retention policy at fixed capacity. |
| Schaeffer & Plaat (1996), *New Advances in Alpha-Beta Searching*, ACM CSC, 124–130 | [acm-final.pdf](https://drive.google.com/file/d/1hOKgvI6s3ZlWApX8zamOoJEABXJuslun/view), 7 pages, author-hosted layout, [DOI](https://doi.org/10.1145/228329.228344), SHA-256 `7d278288d67831e9258e015d7a30bfa4324e7a67637673646333c796d9ea2dfe` | Describes cached score cutoffs, stored-first-move ordering, and reusing the search table to find an alternative after excluding a move. Direct prior art for the proposed comparison. |
| Hyatt & Cozzie (2005), *The Effect of Hash Signature Collisions in a Chess Program*, 28(3), 131–139 | [hyatt2005.pdf](https://drive.google.com/file/d/1ZqyIeTTKlZpSzIb6UEoEwEXgN7DjiS17/view), 9 pages, SHA-256 `dad07ebb122741f8b0ab088a444bf7b1092b3dc196e1975c737185fb1fdc8378` | Injected false signature matches in Crafty and Zappa. Provides a precedent for a collision-specific arm, while the R26 1 MiB arm changes capacity and replacement pressure. |

## Missing-original literature census

Title, author, DOI and known filename variants were searched in connected
Drive, including a numbered-intake check. “Drive unconfirmed” records the
limits of search indexing, even when an external full text is available.

| Work | Drive status | Acquisition and immediate use |
| --- | --- | --- |
| Björnsson (2024), *Chess and explainable AI* | Unconfirmed, carried forward | [Journal record](https://doi.org/10.3233/ICG-240256). Obtain the journal article for its wider framing of explanatory systems. |
| Demura & Kaneko (2024), *Initial state diversification for efficient AlphaZero-style training* | Unconfirmed, carried forward | [Journal record](https://doi.org/10.3233/ICG-240255). [IPSJ precursor, Shogi816K (2023)](https://ipsj.ixsq.nii.ac.jp/records/229354) is separately identified and has its own full-text listing. Relevant to diversity design after the TT-specific works. |
