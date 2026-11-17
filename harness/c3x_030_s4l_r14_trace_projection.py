"""Project comparable forecasts from public reports and a complete S4-L root trace."""

from c3x_030_s4l_r12_explanation_score import sign


ARMS = ("public_tree", "public_last", "trace")
ROOT = "C3X_S4L_ROOT_SCORE"
BEGIN = "C3X_S4K_GO_BEGIN"
END = "C3X_S4K_GO_END"
ORDINARY_LIMIT = 32000 - 2 * 246


def fields(line):
    return {key: int(value) for key, value in
            (token.split("=", 1) for token in line.split()[1:])}


def ordinary_cp(value):
    magnitude = abs(value) * 100 // 328
    return sign(value) * magnitude


def trace_candidate(lines, public_depth):
    starts = [fields(line) for line in lines if line.startswith(BEGIN + " ")]
    stops = [fields(line) for line in lines if line.startswith(END + " ")]
    root = [fields(line) for line in lines if line.startswith(ROOT + " ")]
    if len(starts) != 1 or len(stops) != 1:
        return None, "missing_unique_go_boundary"
    epoch = starts[0]["epoch"]
    if (stops[0]["epoch"] != epoch or stops[0]["root_score_total"] != len(root)
            or any(event["epoch"] != epoch or event["ordinal"] != index
                   for index, event in enumerate(root))):
        return None, "incomplete_go_trace"
    candidates = [
        event for event in root
        if event["iteration"] > public_depth and abs(event["value"]) < ORDINARY_LIMIT
        and event["alpha"] < event["value"] < event["beta"]
        and event["will_update_root_pv"] == 1
    ]
    if not candidates:
        return None, "no_deeper_strict_root_update"
    return max(candidates, key=lambda event: (event["iteration"], event["ordinal"])), "added"


def projections(reports, lines, mover_is_leaf_turn):
    score_depth = max((report["depth"] for report in reports), default=0)
    ordinary = [report for report in reports if report["cp"] is not None]
    exact = [report for report in ordinary if not report["bound"]]
    base = exact[-1]["cp"] if exact else None
    last = ordinary[-1] if ordinary else None
    event, status = trace_candidate(lines, score_depth)
    if base is None:
        event, status = None, "missing_public_tree_point"
    trace = base
    if event is not None:
        leaf_score = ordinary_cp(event["value"])
        trace = leaf_score if mover_is_leaf_turn else -leaf_score
    return {
        "values": {"public_tree": base, "public_last": last["cp"] if last else None,
                   "trace": trace},
        "trace_status": status,
        "trace_event": event,
        "public_score_depth": score_depth,
        "last_is_bound": last["bound"] if last else None,
    }


def pair_signs(points):
    first, second = (point["values"] for point in points)
    return {arm: sign(first[arm] - second[arm])
            if first[arm] is not None and second[arm] is not None else None
            for arm in ARMS}
