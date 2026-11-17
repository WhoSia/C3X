"""R25: evidence-conservative explanation of a Stockfish PV fork.

Only the observed root, score, PV and independent judgments are certified.
Different PVs alone cannot certify a strategic-plan change or an NNUE cause.
Pure Python, usable by the existing chess-aware renderer after legality checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EVIDENCE_CLASSES = (
    "NATIVE_SEARCH_OBSERVATION",
    "LEGAL_VARIATION_OBSERVATION",
    "INDEPENDENT_JUDGE_COMPARISON",
    "CAUSAL_CONTRAST_UNPROVEN",
    "PLAN_TRANSPORT_UNPROVEN",
    "HUMAN_LEARNING_UNTESTED",
)


@dataclass(frozen=True)
class ForkAudit:
    case_id: str
    recommendation: str
    displayed_cp: int
    native_values: tuple[int, int]
    first_divergence_ply: int
    chooser: str
    first_moves: tuple[str, str]
    shared_prefix: tuple[str, ...]
    report_depths: tuple[int, int]
    provenance: tuple[str, ...]
    verdict: str
    judge_order: tuple[tuple[int, str | None, int | None], ...]
    both_continuations_replayed: bool
    evidence_limit: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "recommendation": self.recommendation,
            "displayed_cp": self.displayed_cp,
            "native_values": list(self.native_values),
            "first_divergence_ply": self.first_divergence_ply,
            "chooser": self.chooser,
            "first_moves": list(self.first_moves),
            "shared_prefix": list(self.shared_prefix),
            "report_depths": list(self.report_depths),
            "provenance": list(self.provenance),
            "verdict": self.verdict,
            "judge_order": [{"depth": depth, "preferred": preferred, "margin_cp": margin}
                            for depth, preferred, margin in self.judge_order],
            "both_continuations_replayed": self.both_continuations_replayed,
            "evidence_limit": self.evidence_limit,
        }


def _validated_report(row: dict[str, Any]) -> None:
    if not row.get("eligible"):
        raise ValueError("Report lacks completed, in-window native proof")
    if row.get("bound") != "none":
        raise ValueError("Do not compare an alpha-beta bound as an exact score")
    if type(row.get("cp")) is not int or type(row.get("native")) is not int:
        raise ValueError("Both displayed and native scores must be integers")
    pv = row.get("pv")
    if not isinstance(pv, list) or not pv or not all(isinstance(x, str) and x for x in pv):
        raise ValueError("Missing or malformed principal variation")
    if pv[0] != row.get("move"):
        raise ValueError("Root move differs from PV")
    if type(row.get("depth")) is not int or row["depth"] < 1:
        raise ValueError("Invalid producer report depth")


def audit(case_id: str, reports: list[dict[str, Any]],
          *, judge: dict[str, Any] | None = None,
          replay_verified: bool = False) -> ForkAudit:
    """Audit two *already chess-legality-validated* source reports.

    judge maps the two UCI moves to {depth: int cp} from the perspective
    of the player at the divergence. These are not causal valuations or
    a universal claim over all opponent replies.
    """
    if len(reports) != 2:
        raise ValueError("Exactly two complete source reports required")
    first, second = reports
    _validated_report(first)
    _validated_report(second)
    if first["move"] != second["move"] or first["cp"] != second["cp"]:
        raise ValueError("This contract concerns the same root and displayed cp")
    a, b = first["pv"], second["pv"]
    common = 0
    while common < min(len(a), len(b)) and a[common] == b[common]:
        common += 1
    if common == min(len(a), len(b)):
        raise ValueError("Strict prefix or equal PV is not a continuation fork")
    if common < 1:
        raise ValueError("Root recommendation cannot diverge")
    chooser = first.get("fork_chooser")
    if chooser not in ("white", "black") or chooser != second.get("fork_chooser"):
        raise ValueError("A verified side-to-move tag is required")
    diverged = (a[common], b[common])

    orders: list[tuple[int, str | None, int | None]] = []
    if judge is not None:
        if set(judge) != set(diverged):
            raise ValueError("Judge evidence must cover exactly both first fork moves")
        depths = set(judge[diverged[0]]) | set(judge[diverged[1]])
        for depth in sorted(depths, key=int):
            v0, v1 = (judge[uci].get(depth) for uci in diverged)
            if not all(type(v) is int for v in (v0, v1)):
                orders.append((int(depth), None, None))
                continue
            margin = abs(v0 - v1)
            preferred = diverged[0] if v0 > v1 else diverged[1] if v1 > v0 else "tie"
            orders.append((int(depth), preferred, margin))
    preferred = {p for _, p, _ in orders if p not in (None, "tie")}
    if not judge or not orders:
        verdict = "NO_INDEPENDENT_JUDGEMENT"
    elif len(preferred) >= 2:
        verdict = "DEPTH_SENSITIVE_FORK_PREFERENCE"
    elif len(preferred) == 1 and all(p is not None for _, p, _ in orders):
        verdict = "JUDGE_ORDER_STABLE_AT_TESTED_DEPTHS"
    else:
        verdict = "INCONCLUSIVE_JUDGEMENT"
    provenance = ["NATIVE_SEARCH_OBSERVATION", "LEGAL_VARIATION_OBSERVATION",
                  "CAUSAL_CONTRAST_UNPROVEN", "PLAN_TRANSPORT_UNPROVEN",
                  "HUMAN_LEARNING_UNTESTED"]
    if judge:
        provenance.insert(2, "INDEPENDENT_JUDGE_COMPARISON")
    return ForkAudit(
        case_id=case_id, recommendation=first["move"], displayed_cp=first["cp"],
        native_values=(first["native"], second["native"]),
        first_divergence_ply=common + 1, chooser=chooser,
        first_moves=diverged, shared_prefix=tuple(a[:common]),
        report_depths=(first["depth"], second["depth"]),
        provenance=tuple(provenance), verdict=verdict,
        judge_order=tuple(orders), both_continuations_replayed=replay_verified,
        evidence_limit="Observed PV fork, not proof of a different strategic plan,"
                       " its causal neural feature, or superiority against all defenses."
    )


def required_plan_trial(audit_result: ForkAudit) -> dict[str, Any]:
    """Return a prospective question, not a post-hoc invented plan claim."""
    return {
        "case_id": audit_result.case_id,
        "start_after_shared_uci": list(audit_result.shared_prefix),
        "fork_moves": list(audit_result.first_moves),
        "question": "Which explicit board-level objective survives both lines and unseen defenses?",
        "before_judge": [
            "Freeze objective predicate, owner and maximum continuation length",
            "Freeze opponent reply family independently of the observed PV",
            "Define legal witness and counterexample for every defended line",
            "Pre-register independent judge, budget and abstention criteria",
        ],
        "result": "NOT_TESTED",
        "claim_authority": "PLAN_TRANSPORT_UNPROVEN",
    }
