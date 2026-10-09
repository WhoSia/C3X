# C3X 0.15 — Causal Search-Window Provenance (CSWP), Theory v0.1

**Formal status: ORIGINAL PROPOSED THEORY, NOT AN ESTABLISHED DISCIPLINE.** Date: 2026-10-09. C3X 0.15 is research-OPEN; no theoretical definition should be substituted for source-native evidence. The four-game procedural P1 holdout stays sealed.

## Founding problem

A human strategic label such as pin can map to several distinct chess-engine operators: position legality, pinned attacker exclusion in static exchange evaluation (SEE), classical mobility/WeakQueen routing, search pruning, move ordering, TT bound reuse and PV competition. Their interactions can change the chosen root move. Chess law alone does not identify which event caused an observed preference.

C3X 0.14 proved limited software treatment sensitivity, not neural conceptual taxonomy. Its S28 same-law retrospective pattern transfer scored 6/32 versus 16/32 for the trivial no-change comparator. C3X 0.15 tests the harder question on fresh TWIC 1665 games, with labels and model presealed before the new intervention.

## Definition 1 — operational state

For a bounded, single-thread, fixed-build, deterministic native chess search, let

  E=(Sigma, ->, I, Y)

with state s=(P,H,R,Q,d,alpha,beta,T,O,V,K,theta).

- P: board and legal move relation.
- H: prior move history, repetition and rule-50 state.
- R: root candidates and current root/PV ordering.
- Q: search stack, history, LMR/reduction, killers and pending transitions.
- d, alpha, beta: active depth and window at a particular event, including caller frames.
- T: physical TT slots, exact full keys (sidecar), generations, replacement, stored bound/depth, writer and consumer.
- O: source-site operator eligibility and actual firing.
- V: classical/NNUE/PSQ route and evaluation state.
- K: callsite and search-episode provenance.
- theta: exact engine source SHA, binary/build settings, Hash, Threads, MultiPV, depth, etc.

An exact FEN by itself does not specify this operational state. Two searches of equal FEN can differ under different TT/history/evaluation context.

## Definition 2 — typed intervention

Let E[j] be the executable obtained by changing exactly one specified source operator while leaving the actual legal chess rules unchanged.

  I_j(w) = 1[bestmove(E[j],w) != bestmove(E[0],w)]

for frozen original-source world w. The operator treatment is **not** do(pin geometry changed). A root-object identity guard by square/color/piece/pinner/king is also not permanent piece identity through all game histories.

## Definition 3 — intervention evidence and provenance

An actual search event has a type in:
LAW, OP_ELIGIBLE, OP_FIRED, EVALUATOR_ROUTE, SEARCH_ENTER, WINDOW, TT_WRITE,
TT_READ, CUTOFF, REDUCTION, MOVE_ORDER, PV_UPDATE, ROOT_CHOICE.

An event identity must contain source SHA+site, original game-root ID, root move,
position full key, recursive frame or call ordinal, depth and window where relevant.
A TT writer->reader edge additionally requires physical slot, last exact full key,
writer generation/sequence and applicable bound/depth checks; low-16 key equality
alone never certifies provenance.

A time-unrolled graph Gamma contains typed possible-dependency edges:
search-parent, branch-local, window-parent-child, TT-write-read, history/LMR,
evaluation-route, root-competition. Membership in this graph is NOT by itself
counterfactual necessity. Event ancestry and actual difference-making are different.

## Definition 4 — the three firsts

F_site: first actually *effective source-code arm divergence*, witnessed by eligible
root-object SEE branch and exact native source guard. A counter in treated but not
OFF is not enough to establish a particular window change.

F_state: earliest correspondingly aligned *semantic transition* where the compared
runs move to different operational states. Raw event list indices need not align if
instrumentation inserts events: require a semantic common-prefix relation.

F_window: first correspondent search frame where (alpha,beta,depth,bound class)
or propagated cut/return permission differs. It can occur after F_site; it can be
absent even when the final bestmove differs.

F_TT and F_PV are separately typed first physical TT lineage and root/PV differences.
Do not identify F_site with F_window or F_TT without evidence.

## Proposition A — deterministic prefix locality (conditional)

Assume two fixed-environment deterministic operational runs have identical complete
initial states; the observer is semantically inert; and the transitions agree on all
source instructions not changed by the treatment. Prior to the first exercised
differing instruction, the runs have identical semantic states and enabled steps.

Proof: induction on the execution step, using transition determinism. This is a
standard operational-semantics consequence, not an invented fundamental theorem.
Its falsifier in practice is any observed pre-source-site search difference that
cannot be explained by incomplete state capture or nondeterministic execution.

## Proposition B — treatment inclusion does not imply outcome monotonicity

For nested treated source-site sets A subset B, neither
I_A(w) <= I_B(w) nor I_A(w) >= I_B(w) holds in general.

Counterexample: consider a deterministic two-branch root-score difference f(a,b)
with f(0,0)=-1, f(1,0)=+1, f(1,1)=-1; an intervention on a alone
changes the selected move, while the larger intervention on (a,b) does not.
This is possible even without TT or alpha-beta, so previous observed
global-versus-root SEE nonmonotonicity is NOT a proof of TT mediation.

## Proposition C — typed alpha-beta bounds have conditional truth licenses

In a sound finite, exact minimax tree, a LOWER(v) record certifies V>=v, an
UPPER(v) record V<=v, and an EXACT(v) record V=v, subject to correct history,
depth and window applicability. In a selective practical engine, e.g. SF16
with LMR, pruning, fail-soft approximations and hash replacement, a recorded
LOWER/UPPER/EXACT is an *algorithmic bound tag*, not unconditional proof about
the perfect chess minimax value. Correctness claims must be relativized to the
actual implemented finite search procedure and its assumptions.

## Proposition D — evidence ancestry is weaker than but-for cause

An event can be naturally executed and appear in a provenance ancestry while
removing it leaves root bestmove unchanged: later overwrites, redundant bounds,
competing candidate paths and cancellation are counterexamples. To say that
a particular TT read causally mediated a root change requires an additional
writer/reader-preserving intervention and matched replay, not a single correlation.

## Chess-concept fiber, without neural ontology inflation

Define the candidate fiber of legal pinned object (P,s) under environment e as

  F(P,s;e)=[G,A,N,I,M,T]

G=law and geometry, A=explicitly scheduled root operator opportunity,
N=naturally executed source-site events (root-key versus descendants distinguished),
I=frozen code-intervention responses, M=post-treatment mediator/counterfactual
provenance, T=external transportability under recorded source/game/engine conditions.

The same-law fiber F_g={w : G(w)=g} may contain multiple operational responses.
This does NOT imply an encoded 'pin sub-neuron' or an invariant engine concept.
Conceptual naming requires within-law repetition, negative/positive source
interventions, event-graph explanation, and out-of-source predictive stability.

## Causal explanation certificates and claim tiers

A certificate has fields (source, treatment, provenance, bounds, rivals, negatives,
uncertainty, authority). Tier 0 certifies legal original chess source.
Tier 1 certifies actual source-site code intervention and output difference.
Tier 2 certifies aligned search-event, TT/write-read and alpha-beta mediation.
Tier 3 requires cross-source mechanism prediction and verified tactical abstraction.
Tier 4 requires independently identified NNUE learned features. If data only justify
Tier 1, higher tiers MUST ABSTAIN rather than extrapolate.

## Empirical court — prior and fresh

0.14 earlier TT: 28/28 first blocked-return writer matches main terminal, while
the first 1792 naturally taken returns include MainTerminal 1725 and ProbCut 67.
Their lower/exact/upper counts 1580/76/136 show search-bound reuse is not simply
an exact position-value cache. This antecedent did NOT identify first window
divergence after the original-root SEE treatment.

0.15 P0 R2: 64 pinned+64 nonpin original games in TWIC 1665; 39 chess-law types;
R2 source manifest exact SHA 1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534.

0.15 P1: B0/B1/C1 binary predictions sealed before new response, with exact
full prediction SHA a4ebc45f8ab844e502aa507c64eb78f72371952c0512df676e4b33b0ccc4d172.

0.15 P2: REAL Stockfish16 source-native 512 process court run 37906181077,
64 pin worlds and 64 nonpin shams. Target source code fired in 51/64 pin worlds,
15598 first-cold events, and changed 11/64 bestmoves. Frozen classifiers:
B0 accuracy 53/64, B1 53/64, C1 42/64; C1 detected 10/11 positives with 21 false positives.
C1 improves *screening sensitivity/balanced accuracy*, but FAILS the trivial
B0 on primary overall accuracy. Reclassifying this as universal predictor
superiority would violate precommit governance. TT/window source mediation
is still UNTESTED in the P2 result.

The next targeted court must align the first eligible SEE site to the active
search frame, record frame entry/current alpha/beta, source/root/TT identity and
the first post-exposure search-window divergence. Require cold repeat and
exact unchanged OFF output before licensing any explanatory mediator claim.

## Prior-art collision ledger — open novelty question

- Knuth & Moore (1975), An Analysis of Alpha-Beta Pruning,
  DOI 10.1016/0004-3702(75)90019-3, already develops alpha-beta foundations.
- Stockman (1979), A minimax algorithm better than alpha-beta?,
  DOI 10.1016/0004-3702(79)90016-X; and Berliner (1979),
  The B* tree search algorithm, DOI 10.1016/0004-3702(79)90003-1,
  develop proof/search and bound reasoning.
- Björnsson (2024), Chess and Explainable AI, DOI 10.3233/ICG-240256.
- Hammersborg & Strümke (2024), Information based explanation methods for
  deep learning agents, DOI 10.1038/s41598-024-70701-2.
- Silva (2011), Survey of algorithmic debugging strategies,
  DOI 10.1016/j.advengsoft.2011.05.024.
- C3X's prior source-native provenance P32, first-TT and 0.14 receipts.

Claimed contribution is the experimentally testable combination of
window-sensitive *executable interventional* ancestry and typed chess-fiber
explanation authorization; no assertion that no one previously attempted
any adjacent part. Full original novelty screening is still required.

**CURRENT COURT:** CSWP_THEORY_V0.1_PROPOSED / PREFIX_LOCALITY_PROPOSITION_CONDITIONAL /
NONMONOTONIC_COUNTEREXAMPLE_VALID / BOUND_TAG_LICENSE_SCOPED /
P2_NATIVE_SOURCE_EFFECT_PASS / C1_PRIMARY_ACCURACY_VS_B0_FAIL /
FIRST_SOURCE_TO_TT_WINDOW_CAUSAL_CHAIN_HOLD / NNUE_LATENT_HOLD.
