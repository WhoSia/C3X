# C3X 0.29-P42/R1 — Negative Theorems for Plan Regret as Chess Explanation
Date: 2026-11-05 KST. Source-first PI audit after rereading Chat Archive 20–29, P40/P41 docs, Cui/Ling/Ng, BinProp and Jenner originals. **SYNTHETIC MATHEMATICS ONLY; NO NEW CHESS/NATIVE/HUMAN RESULT.**

## 1. Fatal identification gap in the current P40 regret contract
For candidate move m, opponent reply r, permitted plan moves P(m,r), and independent value labels V_J, define:
- Q(m) = min_r max_{u in L(s,m,r)} V_J(s,m,r,u) (idealized finite three-ply root value).
- R_P(m) = max_r [max_{u in L(s,m,r)} V_J(s,m,r,u) - max_{u in P(s,m,r)} V_J(s,m,r,u)].

**Proposition A (value-shift nonidentifiability):** For any constants c_m, shifting *all* leaves under each candidate m by c_m leaves R_P(m) unchanged but shifts Q(m) by c_m. Proof: both inner maxima within each reply shift by c_m and their difference cancels, while min_r max_u shifts by c_m. Thus even exact R_P(m)=0 does NOT establish m is a good root move, let alone why Stockfish chose it.

Constructive finite-world refuter (source test): m=a has leaf values (40,10) under r1 and (50,20) under r2, with singleton best-action plan, hence Q(a)=40, R(a)=0. m=b shifts the values by -140, giving Q(b)=-100 and R(b)=0. All plans are selective, all replies covered. The root ordering is clear, regret cannot identify it.

**Proposition B (label leakage):** Choosing after receiving judge scores P(m,r)={argmax_u V_J(s,m,r,u)} yields regret 0 for every reply while being purely retrospective oracle construction. A digest of the plan and a string phase 'PRE_JUDGE' do not prove chronological separation; require independently timestamped, source-bound predictor artifact committed before labels exist.

**Proposition C (mechanism gap):** Even genuinely prospectively computed low-regret P does not establish NNUE/alpha-beta/TT mediation or natural unrestricted root choice cause. This remains a separate source-native intervention claim.

## 2. P41 structural preflight discovered weakness
Read `tools/c3x_029_p41_r3_independent_plan_court_preflight.py`. It checks each competitor's `native_nodes`, `legal_expansions`, and `cpu_ms` against shared *caps*, and equal `claim_slots`, but it does NOT require equal consumed resources or an explicit matched-budget normalization / cost-conditioned score comparison. It can structurally pass where a method actually uses much more compute than another. The preflight explicitly labels itself STRUCTURAL_PREFLIGHT_ONLY; do not promote its PASS to fair-competition certification.

Also `freeze["phase"] == "PRE_JUDGE"` and a self-consistent SHA are *assertions*, not a trusted chronology proof. External immutable timestamps, separation of prediction and reference labels, and judge-blind plan selection are missing from the structural contract.

## 3. New 3-gate scientific decomposition (no goal dilution)
**G1: Move-quality**: evaluate root candidate ordering or regret-to-best-root under an independent, budget/source audited J. Compare forced candidate after complete legal history; retain cp/mate/bounds and root POV; report uncertain ties as HOLD.
**G2: Plan-quality**: evaluate selectivity, coverage, one-sided counterexample regret, multi-reply value and prospective typed plan consistency. Require no reference-label leakage, avoid a singleton oracle per reply after seeing J.
**G3: Mechanism-fidelity**: source-native local features and upstream ancestor state perturbation cause an unrestricted root-action change with contact/sham/restore and negative controls. Neither G1 nor G2 implies G3.

A strong chess-explanation claim requires G1+G2 at independent event/game heldout, and requires G3 additionally if claiming that the explanation reflects the engine's actual causal decision mechanism.

## 4. Binding prior art and historical failures
- Cui, Ling & Ng 2026 original already includes sampled off-mainline chess responses, strong engine-backed branch JSON and downstream human/LLM evaluation; do not claim branch planning as new.
- Press & Golubev 2026 BinProp already uses engine-backed near-negative contrast and motif tests; don't claim contrastive legality as new.
- Jenner et al 2024 Leela causal future-move representations, and subsequent Sandmann v4 (Drive original not yet held/read), preempt generic learned lookahead claims.
- P37 weak C3X heuristic lost 1/6 versus actual-human PV 4/6; P39 mate-2 0/16; P40 24k root PV matched bounded 96k preference 5/5 identifiable cases. Retain negatives.
- P41 real independent J has not been admitted; P41 R2/R3 and R4 Actions were QUEUED in the original record; do not manufacture success.

## 5. Next experiment, stringent falsifier-first design
(1) Freeze one near-equal candidate pair based only on a game/event-disjoint source intake and pre-J 24k score uncertainty; avoid outcome-driven cherry picking.
(2) Freeze typed C3X plan and a Cui-style engine-backed k=3 branching JSON under the same *actual* cost accounting and output cardinality, before J labels.
(3) Certify J provenance and true native node consumption; check score POV/bounds, source history, network digest and independence. Ethereal P38 2–5-node shallow results remain invalid.
(4) Evaluate *both* root quality Q and conditional plan regret R. One robust counterexample falsifies all-response low-regret; missing refutation cannot certify it.
(5) Mechanism arm remains HOLD until source-executed NNUE feature→ancestor→root causal path is separately demonstrated.

## 6. Version/CI/evidence
Research unit **P42/R1**, not formal C3X 0.30 promotion. New source court `tools/c3x_029_p42_regret_nonidentification_court.py` and 5 negative/control tests `tools/test_c3x_029_p42_regret_nonidentification_court.py`. Source-only refuters; do not infer chess or causal effectiveness. **No native CI was run or marked PASS in this unit.** GitHub author/committer must be WhoSia, no github-actions[bot] commits. Notion meaning, Drive bytes, GitHub executable records; external archive mirroring is a separately verified step.
