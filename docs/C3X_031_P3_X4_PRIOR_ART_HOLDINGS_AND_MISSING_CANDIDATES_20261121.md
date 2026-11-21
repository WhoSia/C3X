# C3X 0.31 — Literature Commons Availability Audit and Unowned New Research Leads (2026-11-21)

**Method**: Direct connected Google Drive PDF metadata/title searches, not just whether a work is *cited* in the C3X literature index; DOI/author/title/version normalization required. Confirmed one direct PDF is **not proof of scientific reading**; a negative exact-title Drive search is **not proof of universal absence** (untitled scans, PDFs in ZIP, aliases and inaccessible folders can remain). Cross-checked official publisher/proceedings public download links. C3X canonical policy: centralized `10_PAPERS` owns PDF bytes; lab `00_LITERATURE_INDEX` owns specific interpretation, citations and version; new unverified bytes to `00_INTAKE` before SHA/edition validation. Do not duplicate `10_PAPERS`.

## A. Directly confirmed PDF owned in Google Drive

| Priority | Title / edition | Exact Drive original PDF metadata | C3X research use |
| --- | --- | --- | --- |
| A | Russell & Wefald (1991), *Principles of Metareasoning* | [Google Drive](https://drive.google.com/file/d/1SAvlhQSvPEXTV4QxmsnrCZtzWk-x9ZWT/view) | Theory for choosing computations under bounded resources, **not C3X's novelty** |
| A | Geiger et al. (2025), *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* | [Canonical Google Drive](https://drive.google.com/file/d/1i_i_cFFv6vqYHaBOgKK9AbuprPtj8v91/view), [separate duplicate](https://drive.google.com/file/d/1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK/view) | Intervention validity vs observational fit; duplicate requires byte/edition check before cleanup |
| A | Kishimoto & Müller (2005), *A Solution to the GHI Problem for Depth-First Proof-Number Search* | [Google Drive](https://drive.google.com/file/d/1Q_T8JQT2Wa0aqWEJeLQAUq_c09fBSgOV/view) | Specific graph-history solution, **different work** from their AAAI 2004 paper |
| A | Breuker, Uiterwijk & van den Herik (1994), *Replacement Schemes for Transposition Tables* | [Google Drive](https://drive.google.com/file/d/18cL-ECAavR4ZDw3rfwB2VOR7_GQCFEUg/view) | TT age, replacement, memory restoration semantics |
| A | Hyatt & Cozzie (2005), *The Effect of Hash Signature Collisions in a Chess Program* | [Google Drive](https://drive.google.com/file/d/1ZqyIeTTKlZpSzIb6UEoEwEXgN7DjiS17/view) | TT partial-key collisions; full-key source attribution |
| B | Marsland (1986), *A Review of Game-Tree Pruning* | [Google Drive](https://drive.google.com/file/d/1c9-iqvrTW_6JZqHM6VUtSvCYRuM-E_fZ/view) | source gating historical prior art |
| B | Knuth & Moore (1975), *An Analysis of Alpha-Beta Pruning* | [Google Drive](https://drive.google.com/file/d/118TK7JM2aeQpgl5TsACOSjIoQkuo_YL5/view) | candidate ordering and resource consumption |
| B | Griffiths, Lieder & Goodman (2015), *Rational Use of Cognitive Resources* | [Google Drive](https://drive.google.com/file/d/1Oh9BTVK4mtY6uRhN2r2WqSDGn64IOM9g/view) | resource-rational models and limitations of human transfer |
| B | Callaway et al. (2022), *Rational Use of Cognitive Resources in Human Planning* | [Google Drive](https://drive.google.com/file/d/11lmR6cdEBj38-HL8jRh_WJMMkrsJfPr3/view) | human planning separate causal and behavioral authority |
| A | Zhang & Nanda (2024), *Towards Best Practices of Activation Patching in Language Models* | [Google Drive](https://drive.google.com/file/d/1k5Y-wOyHVK1vGQ6l58O1axhBoY4JBQoM/view) | sham/baseline/metric artifacts caution, not same program substrate |
| B | Pálsson & Björnsson (2023), *Unveiling Concepts Learned by a World-Class Chess-Playing Agent* | [Google Drive](https://drive.google.com/file/d/16yo6d9HdDeQb5PPZkB4wTbCNaZHD9AYO/view) | direct chess XAI prior-art collision |

## B. Candidate **not yet located as the exact PDF** in accessible Google Drive metadata searches

The status below is **`MISSING_CANDIDATE_VERIFY_ARCHIVE`**, not assertive `ABSENT_EVERYWHERE`. The central `10_PAPERS`, `00_INTAKE`, ZIP assets, untitled scans, and older e-print revisions need DOI/full-text fingerprint checks before a definitive disposition.

| Priority | Exact work | Official reliable downloadable source | Why it matters; distinct from held files |
| --- | --- | --- | --- |
| **P0** | Kishimoto & Müller (2004), *A General Solution to the Graph History Interaction Problem* (AAAI 2004) | [AAAI paper PDF](https://s.aaai.org/Papers/AAAI/2004/AAAI04-102.pdf), [AAAI metadata](https://mlanthology.org/aaai/2004/kishimoto2004aaai-general/) | **Different** paper from owned Kishimoto & Müller 2005 DfPn GHI; rule-history/graph-dependence and exact TT read-state pitfalls |
| **P0** | Russell & Wefald (1989), *On Optimal Game-Tree Search Using Rational Meta-Reasoning* (IJCAI) | [IJCAI PDF](https://www.ijcai.org/Proceedings/89-1/Papers/053.pdf), [IJCAI metadata](https://ijcai.org/proceedings/1989/53) | Direct game-tree computation allocation paper, **not equivalent** to owned 1991 `Principles of Metareasoning` |
| **P0** | Hay & Russell (2011), *Metareasoning for Monte Carlo Tree Search* (UC Berkeley EECS-2011-119) | [Berkeley official PDF](https://digicoll.lib.berkeley.edu/record/136151/files/EECS-2011-119.pdf), [record](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2011/EECS-2011-119.html) | Search computation selection and multiple root impacts; MCTS substrate differs from Stockfish alpha-beta |
| **P1** | Hay, Russell, Tolpin & Shimony (2012), *Selecting Computations: Theory and Applications* (UAI) | [PMLR official article/PDF](https://proceedings.mlr.press/r10/hay12a.html), [original PDF](https://raw.githubusercontent.com/mlresearch/r10/main/assets/hay12a/hay12a.pdf) | formal meta-level allocation; no direct TT causation identification |
| **P0** | Geiger, Wu, Potts, Icard & Goodman (2024), *Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations* (CLeaR) | [PMLR official paper/PDF](https://proceedings.mlr.press/v236/geiger24a.html), [official PDF](https://proceedings.mlr.press/v236/geiger24a/geiger24a.pdf) | distributed alignment / interchange causal abstraction, **distinct** from owned Geiger et al. JMLR 2025 |
| **P1** | Pîslar, Magliacane & Geiger (2025), *Combining Causal Models for More Accurate Abstractions of Neural Networks* (CLeaR) | [PMLR paper and official PDF](https://proceedings.mlr.press/v275/pislar25a.html), [original PDF](https://raw.githubusercontent.com/mlresearch/v275/main/assets/pislar25a/pislar25a.pdf) | mixtures/context-specific abstractions as rival; neural networks vs classical engine source must be clearly separated |

**No unvalidated claim** about an independent newly invented paper: these six are existing prior art. No PDF has been copied or reorganized by this audit itself. P3-X4 uses exactly one source game twice under different node caps; separate game histories are not implied.

## C. Prior-art synthesis and actual experiment allocation

- **Main P3-B development**: zero extra probes at TT gate; exact Stockfish16 partial-key/age/slot read/write identity; original P3-B pre-registration on P2-028 (historical family-exposed), true physical cold shams, reciprocal TT/history state restoration **only after proven causal writer-to-reader access**. Work agent assigned B exclusively owns experiment branch and source patch.
- **P3-X4 off-target third root**: `P2-056-1` source target `h5e2`, original `b8d8`, treated depth13 `f5h3` under two node caps; outcome has one game and one signed source event. Source-derived 128+12 court and 12 CI tests already in main. No new independent run in literature work.
- **Human/plan tracks**: defer any claim of better chess plan until independent legal opponent replies and separate human learner test; Russell/Hay computation selection theory is prior art, not a value-of-computation score already measured.

## D. Work parallel agents no-collision schedule

| Work session | Ownership | Deliverable | Explicit exclusion |
| --- | --- | --- | --- |
| A / Literature audit | `docs/...`, independent literature branch, intake verification | Full filename, DOI, actual PDF bytes, edition+SHA, 6-candidate MISSING table repaired | Do not touch P3-B source patch/experimental outcome |
| B / Source mediator | P3-B dedicated new branch and pinned engine source | B0 original source noninterference; writer→reader first-difference, before any TT/Heuristic family transplant | Do not merge P3-X4 / touch original P3-B pre-registration |
| C / Off-target and chess referee | Separate P3-X4 follow-up branch | Original `P2-056-1` root chronology; independently repeat root refutation and plan reply analysis | Do not claim TT causal mediator; no source mutation overlapping B |
| D / Skeptical integrator | Reviewer only | Audit original CI runs, collisions, sample-family independence, STRAT vs CAUSAL claim ledger | Do not merge other agents' PR until all independent evidence verified |

**Model recommendation:** ChatGPT **Work mode**, choose **GPT-6 High or Extra High reasoning effort only if a corresponding selector is offered inside the current interface**; otherwise use Work mode as available without assuming its underlying model is user-selectable. Prioritize four independent Work sessions and separate branches, avoid multiple writers on the same file and avoid bot commits. A human can reserve merge authority until independent CI evidence passes.
