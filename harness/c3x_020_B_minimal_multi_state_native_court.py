#!/usr/bin/env python3
"""C3X020-B: source-exact, fixed-four native root-choice sufficiency court.

Exploratory after 0.19 K4 FAIL. Primary endpoint is restoration of the original
F categorical bestmove; score/window equality is explicitly secondary.
Run only against Stockfish16 built from the 0.19 overlay PLUS C3X020 overlay.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play, need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES, mask_filters
from c3x_019_Feb_four_first_root_return_rescue_native import (
    FIXED, SOURCE_SHA, PRIOR_SHA, ROOT_SHA, config as first_config
)

OLD_NATIVE_SHA = "8639dc5d512ffb9a421164fe2631698af59e76b876aa43ac2aee99378045ab47"
# Earliest second *same candidate* child-return mismatch in F versus REPAIR,
# fixed using original 0.19 frozen artifact before any 0.20-B new outcome.
SECOND = {
    3: dict(depth=4, root_call=4, trial=1, move=222, index=5,
            alpha=-190, beta=-166, expected=-179, target=-206),
    6: dict(depth=10, root_call=19, trial=2, move=1307, index=2,
            alpha=103, beta=114, expected=96, target=89),
    10: dict(depth=4, root_call=5, trial=2, move=2910, index=2,
             alpha=91, beta=113, expected=-892, target=-459),
}
# Game7 first residual mismatch changes candidate identity: not an
# admissible single candidate-return replacement.
BOUNDARY_MOVE = {3: 1, 6: 1291, 7: 4020, 10: 2908}
ARMS = ("F_OBS", "FIRST", "A0", "A0_OBS", "A0_SHAM",
        "SECOND_ONLY", "A0_SECOND", "A0_AVERAGE",
        "A0_SCORE", "A0_BOTH", "A0_SECOND_BOTH")


def checked_json(path, expected):
    raw = Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected,
         "C3X020_B_FROZEN_SHA_" + Path(path).name)
    return json.loads(raw)


def boundary_config(depth, move, mode="O", expected=None, target=None):
    expected = expected or {"score": 0, "average": 0}
    target = target or {"score": 0, "average": 0}
    return {"depth": depth, "move": move, "mode": mode,
            "expect_score": expected["score"],
            "expect_average": expected["average"],
            "target_score": target["score"],
            "target_average": target["average"]}


def second_config(gid, mode="REPAIR", sham=False):
    return {**SECOND[gid], "mode": mode,
            "move": 65535 if sham else SECOND[gid]["move"]}


def snapshot(arm):
    events = arm["boundary_state_events"]
    need(len(events) == 1 and events[0]["kind"] == "observed",
         "C3X020_B_MISSING_NATIVE_BOUNDARY_SNAPSHOT")
    event = events[0]
    need(event["before_score"] == event["after_score"] and
         event["before_average"] == event["after_average"],
         "C3X020_B_OBSERVER_CHANGED_STATE")
    return {"score": event["before_score"], "average": event["before_average"]}


def actual_contacts(arm, want_return, want_second=None, want_boundary=None):
    first = arm["root_return_events"]
    second = arm["second_return_events"]
    boundary = arm["boundary_state_events"]
    if want_return is not None:
        need(len(first) == want_return, "FIRST_RETURN_CONTACT_DENOMINATOR")
        if want_return:
            need(first[0]["kind"] == "repaired", "FIRST_RETURN_NOT_REPAIRED")
    if want_second is not None:
        need(len(second) == want_second, "SECOND_RETURN_CONTACT_DENOMINATOR")
        if want_second:
            need(second[0]["kind"] == "repaired", "SECOND_RETURN_NOT_REPAIRED")
    if want_boundary is not None:
        need(len(boundary) == want_boundary, "BOUNDARY_CONTACT_DENOMINATOR")
        if want_boundary:
            need(boundary[0]["kind"] == "repaired", "BOUNDARY_SOURCE_MISMATCH")
    return True


def play_cold(engine, world, clocks, role, selected, source_mode,
              first=None, second=None, boundary=None):
    opts = {"fen_clocks": clocks}
    if first is not None:
        opts["root_return"] = first
    if second is not None or boundary is not None:
        opts["multi_state"] = {"second": second, "boundary": boundary}
    tt_mode = "OBS" if source_mode == "F" else "V"
    target = None if source_mode == "F" else selected["physical"]
    if source_mode != "F":
        opts["tt_reader_filters"] = mask_filters(RULES[role], selected, "FIRST")
    x = play(engine, world, "F", tt_mode, target, **opts)
    y = play(engine, world, "F", tt_mode, target, **opts)
    need(x == y, "C3X020_B_COLD_DUPLICATE_FAIL")
    need(len(x["root_events"]) > 0 and len(x["root_events"]) < 4096,
         "C3X020_B_TRACE_CENSORED")
    return {"UCI": x["UCI"],
            "root_return_events": x["root_return_events"],
            "second_return_events": x["second_return_events"],
            "boundary_state_events": x["boundary_state_events"],
            "source_reader_calls": [e["root_call"] for e in x["blocks"]
                                    if e["kind"] == "reader_block"],
            "terminal_depth_events": [e for e in x["root_events"]
                                       if e["kind"] == "after_sort"],
            "cold_identical": True}


def outcome(row, arm):
    return {"UCI": row["arms"][arm]["UCI"],
            "restores_F_bestmove":
                row["arms"][arm]["UCI"]["bestmove"] == row["arms"]["F_OBS"]["UCI"]["bestmove"],
            "actual_second": row["arms"][arm]["second_return_events"],
            "actual_boundary": row["arms"][arm]["boundary_state_events"]}


def main():
    p = argparse.ArgumentParser()
    for x in ("source", "prior", "prior-root", "frozen-019",
              "engine", "out"):
        p.add_argument("--" + x, required=True)
    args = p.parse_args()
    games = checked_json(args.source, SOURCE_SHA)
    previous = checked_json(args.prior, PRIOR_SHA)
    roots = checked_json(args.prior_root, ROOT_SHA)
    frozen = checked_json(args.frozen_019, OLD_NATIVE_SHA)
    need(len(games["selected"]) == len(previous["cases"]) == 16,
         "C3X020_B_FEB_SOURCE_DENOMINATOR")
    need([x["game_id"] for x in roots["cases"]] == [3, 6, 7, 10],
         "C3X020_B_ROOT_GENEALOGY")
    need([x["game"] for x in frozen["cases"]] == [3, 6, 7, 10],
         "C3X020_B_PREVIOUS_COURT_CASES")
    report = {"schema": "c3x020-B-minimal-native-multistate-root-choice-v1",
              "study": "ADAPTIVE_FROZEN_FEBRUARY_FOUR_NO_INDEPENDENT_TRANSPORT",
              "historical_K4": "FAIL_0_OF_4_RETAINED",
              "historical_F19_5": "FAIL_RETAINED",
              "source_sha256": {"source": SOURCE_SHA, "prior": PRIOR_SHA,
                                "roots": ROOT_SHA, "0.19": OLD_NATIVE_SHA},
              "cases": []}
    for item, old in zip(FIXED, frozen["cases"]):
        gid, role, depth, *_ = item
        need(old["game"] == gid and old["role"] == role,
             "C3X020_B_FROZEN_CASE_IDENTITY")
        world, _ = canonical_engine_world(games["selected"][gid-1])
        clocks = game_clocks(games["selected"][gid-1])
        selected = previous["cases"][gid-1]["selectors"][role]["selection"]
        first = first_config(item)
        passive = boundary_config(depth, BOUNDARY_MOVE[gid])
        row = {"game": gid, "role": role, "arms": {},
               "second_eligible": gid in SECOND, "excluded_reason": None}
        run = lambda source_mode, f=None, s=None, b=None: play_cold(
            args.engine, world, clocks, role, selected, source_mode, f, s, b)
        row["arms"]["F_OBS"] = run("F", b=passive)
        row["arms"]["FIRST"] = run("V")
        row["arms"]["A0"] = run("V", f=first)
        row["arms"]["A0_OBS"] = run("V", f=first, b=passive)
        row["arms"]["A0_SHAM"] = run(
            "V", f=first, s=second_config(gid, sham=True) if gid in SECOND else None,
            b=boundary_config(depth, 65535))
        need(row["arms"]["F_OBS"]["UCI"] == old["arms"]["F"]["UCI"],
             "F_OBSERVER_UCI_DRIFT")
        need(row["arms"]["FIRST"]["UCI"] == old["arms"]["FIRST"]["UCI"],
             "FIRST_SOURCE_DRIFT")
        for k in ("A0", "A0_OBS", "A0_SHAM"):
            need(row["arms"][k]["UCI"] == old["arms"]["FIRST_REPAIR"]["UCI"],
                 "0_19_REPAIR_CONTROL_DRIFT_" + k)
        actual_contacts(row["arms"]["A0"], 1, 0, 0)
        actual_contacts(row["arms"]["A0_SHAM"], 1, 0, 0)
        need(row["arms"]["F_OBS"]["boundary_state_events"][0]["kind"] == "observed",
             "F_OBS_MISSING")
        fstate = snapshot(row["arms"]["F_OBS"])
        rstate = snapshot(row["arms"]["A0_OBS"])
        row["boundary_snapshots"] = {"F": fstate, "A0": rstate}
        if gid in SECOND:
            row["arms"]["SECOND_ONLY"] = run("V", s=second_config(gid))
            # The second-alone treatment may or may not contact in a distinct
            # root history; noncontact is explicitly recorded, not discarded.
            row["arms"]["A0_SECOND"] = run("V", f=first, s=second_config(gid))
            actual_contacts(row["arms"]["A0_SECOND"], 1, 1, 0)
        else:
            row["excluded_reason"] = "POST_REPAIR_NEXT_EVENT_DIFFERENT_MOVE_NO_SAME_CANDIDATE"
        modified_fields = {field for field in ("score","average")
                           if fstate[field] != rstate[field]}
        row["boundary_nonzero_dose_fields"] = sorted(modified_fields)
        for name, mode, required in (("A0_AVERAGE", "A", {"average"}),
                                     ("A0_SCORE", "S", {"score"}),
                                     ("A0_BOTH", "B", {"score","average"})):
            if not modified_fields.intersection(required):
                row["arms"][name] = {"status": "ZERO_DOSE_PREDECLARED_SKIP"}
                continue
            treatment = boundary_config(depth, BOUNDARY_MOVE[gid],
                                        mode, rstate, fstate)
            row["arms"][name] = run("V", f=first, b=treatment)
            actual_contacts(row["arms"][name], 1, 0, 1)
            e = row["arms"][name]["boundary_state_events"][0]
            need((e["after_score"] != e["before_score"]) == (mode in ("S","B") and "score" in modified_fields),
                 "SCORE_DOSE_INCORRECT")
            need((e["after_average"] != e["before_average"]) == (mode in ("A","B") and "average" in modified_fields),
                 "AVERAGE_DOSE_INCORRECT")
        if gid in SECOND and modified_fields:
            b = boundary_config(depth, BOUNDARY_MOVE[gid], "B", rstate, fstate)
            # Interaction can change the boundary pre-state: do NOT adapt the
            # expected values after seeing the outcome.
            row["arms"]["A0_SECOND_BOTH"] = run("V", f=first,
                                               s=second_config(gid), b=b)
            actual_contacts(row["arms"]["A0_SECOND_BOTH"], 1, 1, 1)
        else:
            row["arms"]["A0_SECOND_BOTH"] = {
                "status": "NO_SECOND_CANDIDATE_OR_BOUNDARY_DOSE"}
        row["outcomes"] = {
            key: outcome(row,key) for key in ARMS
            if key in row["arms"] and "UCI" in row["arms"][key]}
        report["cases"].append(row)
        print("C3X020_B_CASE",gid,"F",row["arms"]["F_OBS"]["UCI"]["bestmove"],
              "A0",row["arms"]["A0"]["UCI"]["bestmove"],
              "actual_arms",len(row["outcomes"]),flush=True)
    report["summary"] = {
        "full_four_case_denominator": len(report["cases"]),
        "scientific_primary": "categorical_F_bestmove_restored",
        "F19_5": "FAIL_RETAINED",
        "historical_K4": "FAIL_RETAINED",
        "restorations_by_arm": {arm: sum(int(c["outcomes"][arm]["restores_F_bestmove"])
                   for c in report["cases"] if arm in c["outcomes"])
                   for arm in ARMS if arm not in ("F_OBS","FIRST")},
        "eligible_denominators_by_arm": {arm: sum(arm in c["outcomes"]
                   for c in report["cases"]) for arm in ARMS},
        "note": "Four post-outcome selected cases, not a prospective holdout."
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X020_B_NATIVE_COURT_COMPLETE",json.dumps(report["summary"],sort_keys=True))

if __name__ == "__main__":
    main()
