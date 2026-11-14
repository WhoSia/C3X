# C3X 0.30 S4-L/R4 — Crossed Search State and Categorical Interaction

2026-11-14 KST. Eight frozen development positions from four researcher-constructed game histories. All inputs from the development subset of the S4H2 protocol. Pinned S4-L archive SHA256 a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9. Stockfish 16 at 68e1e9b3811e16cad014b590d7443b9063b3eb52, R3 base, one thread, 16 MiB, classical evaluation, 12k requested nodes per go. Same-build re-run in fresh processes matches parsed outcomes and donor snapshot SHA256s. Each pass ran 192 searches, 2306483 reported nodes, 72 crossed second-go cells plus donor and recipient preparation. No holdout.

## Intervention and controls

Each donor executes go 1 under sham, first-two-hit mask, or second-eligible-hit-only mask. All cases had physical mask counts 0/2/1. Save TT clusters including generation, and counter-move, main, capture and continuation histories. Each recipient independently runs sham go 1, then loads TT and history from independently selected donor runs before go 2. Remaining state belongs to the sham recipient. File serialization is for same-build experimental snapshots. Diagonal sham-sham matches natural sham. All 24 diagonals reproduce the donor move, and 21 match the whole normalized UCI tuple. Three second-only diagonals preserve move but alter tuple, so these blocks do not reconstruct the complete search state.

## Cross-case results

| Case | Donor TT / history diversity | Move map | Nonzero rectangles out of 9 |
| --- | --- | --- | ---: |
| Italian ply10 | 3 / 3 | both | 4 |
| Italian ply8 | 3 / 3 | both | 6 |
| London ply8 | 3 / 3 | both | 4 |
| London ply10 | 1 / 1 | constant | 0 |
| Pirc ply8 | 1 / 1 | constant | 0 |
| Pirc ply10 | 1 / 1 | constant | 0 |
| Scandinavian ply8 | 1 / 1 | constant | 0 |
| Scandinavian ply10 | 1 / 1 | constant | 0 |

In Italian ply10 a two-hit TT combined with sham history transfers O-O. A second-only TT combined with sham history yields h3; with second-only history it yields O-O. In Italian ply8 all natural go-2 runs choose d4, while off-diagonal transplants yield d3 and O-O. In London ply8 the second-only combination yields Nd2; either component alone on sham yields Ne5. The five constant maps offer no TT/history donor variation at byte level despite physical masks. These are nonseparating treatments for these blocks, not evidence of robustness to different state.

## Mathematical structure

For fixed position, node budget and recipient residual state, write M(T,H) for the categorical move. Encode each move as its own basis vector e_m. A rectangle has contrast D=e_(M11)+e_(M22)-e_(M12)-e_(M21). D=0 precisely when the two diagonal multisets agree. If every rectangle vanishes and some row has distinct values a,b in columns i,j, every other row must have the same ordered pair in i,j, because e_a-e_b determines the ordered pair uniquely. Comparing each other column with an anchor now fixes every row to the original row. If no row varies, only TT can matter. Thus all rectangles vanish iff the map depends on at most one input on the tested grid. Exhaustively verified over 19683 ternary 3x3 maps (3 constant, 24 TT only, 24 history only, 19632 both). This theorem is for one-hot decisions. Additive latent scores followed by argmax can also produce a nonzero rectangle, so the test does not prove nonadditive internal scoring.

## Novelty and promotion

TT, history heuristics and interchange interventions are established. A candidate contribution is to link a source-local edit, the persistent state it creates, the counterfactual move map, and a prospective explanation of its strategic effect. Next separate state production from decision susceptibility. Freeze a donor-generation protocol on a new game-disjoint development set, include mismatched-donor examples that elicit a third candidate, predict complete move maps and compare against a root-margin plus independent-score model before claiming a distinct internal interaction. Then narrow the successful transplant to TT clusters and history cells, tracing their first consumers. Novelty relative to the literature, generalization, and learning effects remain unresolved.

[Patch](../harness/c3x_030_s4l_r4_patch.py) · [Experiment](../harness/c3x_030_s4l_r4_exchange.py) · [Analysis](../harness/c3x_030_s4l_r4_structure.py) · [Raw and replay summaries](https://drive.google.com/file/d/1qKfTySITKNBtAZRBrnfNGcoAtPIeU5xs/view). ZIP SHA256 e9a939db9670dc99a00e5ab7194709a3b43aa5157759cb08ad5051b7a7a12ecd. Build R3 first, apply the R4 patch to src, rebuild with ARCH=x86-64. State snapshots were hashed before deletion; raw search logs and replay summaries are archived. Binary SHA256 3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb.
