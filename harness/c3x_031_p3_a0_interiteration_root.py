"""C3X 0.31/P3-A0: root-iteration chronology from original P2-D1 native logs.

Retrospective one-game mechanism development, NOT new native search,
a TT/history mediator intervention, independent family transport or chess merit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

LOG_SHA = "e45dca037f748a06e5043194de397ca26659af726c174a9505f097a5566202bc"
RESULT_ZIP_SHA = "c9a060afea6d0fc93cd20f08eb12699fe4aca2763eb0e78d536e43bff19840c5"
RESULT_JSON_SHA = "e2a56d69342fbe60a522f62b69ca01c08446008c482a571b8dc0a47e5ba95f90"
RESULT_MEMBER = "C3X_031_P2_D1_ALL_NATIVE_EQUAL_DEPTH_EVENTS.json"
EVENT, TARGET = "P2-028-0", "19"
TAGS = ("C3X_R23_START", "C3X_R23_CANDIDATE", "C3X_R23_END",
        "C3X_R33_OPEN", "C3X_R33_CLOSE")


def check(condition, why):
    if not condition:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(raw):
    output = {tag: [] for tag in TAGS}
    for line in raw.decode().splitlines():
        if not line.strip():
            continue
        tag, *parts = line.split()
        if tag not in output:
            continue
        check(all("=" in item for item in parts), "malformed source tag " + tag)
        pairs = [item.split("=", 1) for item in parts]
        check(len(set(k for k, _ in pairs)) == len(pairs), "duplicate native key")
        output[tag].append(dict(pairs))
    check(all(output.values()), "missing source-native tags")
    return output


def root_attempt(rows, ordinal):
    str_ord = str(ordinal)
    start = [r for r in rows["C3X_R23_START"] if r["attempt"] == str_ord]
    end = [r for r in rows["C3X_R23_END"] if r["attempt"] == str_ord]
    moves = [r for r in rows["C3X_R23_CANDIDATE"] if r["attempt"] == str_ord]
    check(len(start) == len(end) == 1 and moves, "incomplete source root attempt")
    return start[0], end[0], moves


def trace(control, treated, target, depth, original):
    for side in (control, treated):
        starts = [int(x["attempt"]) for x in side["C3X_R23_START"]]
        check(starts == list(range(1, depth + 4)), "source attempt count/order changed")
        check([int(x["attempt"]) for x in side["C3X_R23_END"]] == starts,
              "source END attempt order drift")
        ids = [int(x["id"]) for x in side["C3X_R23_CANDIDATE"]]
        check(ids == list(range(1, len(ids) + 1)), "native candidate IDs changed")
        begin = [x for x in side["C3X_R33_OPEN"] if x["event"] == TARGET]
        close = [x for x in side["C3X_R33_CLOSE"] if x["event"] == TARGET]
        check(len(begin) == len(close) == 1 and begin[0] == target,
              "original R33 physical contact identity changed")
        check(close[0]["stopped"] == "0", "source target interrupted")
    a_return = next(x for x in control["C3X_R33_CLOSE"] if x["event"] == TARGET)
    b_return = next(x for x in treated["C3X_R33_CLOSE"] if x["event"] == TARGET)
    check(a_return["futility"] == "1"
          and a_return["skip_f"] == a_return["skip_n"] == "0"
          and a_return["value"] == "-2429", "original physical futility return drift")
    check(b_return["futility"] == "0"
          and b_return["skip_f"] == b_return["skip_n"] == "1"
          and b_return["value"] == "-2500"
          and b_return["replies"] == "2", "treated physical return did not execute")
    out, first_value, first_leader, first_order, first_window = [], None, None, None, None
    for ordinal in range(1, depth + 4):
        h, e, candidates = root_attempt(control, ordinal)
        ht, et, treated_candidates = root_attempt(treated, ordinal)
        check(len(candidates) == len(treated_candidates), "root candidate denominator drift")
        score_differences, update_differences, ordering_differences = [], [], []
        for index, (x, y) in enumerate(zip(candidates, treated_candidates)):
            if x["move"] != y["move"]:
                ordering_differences.append({"index": index,
                    "control_move": x["move"], "treated_move": y["move"]})
            if x["move"] == y["move"] and x["value"] != y["value"]:
                score_differences.append({"index": index, "move": x["move"],
                    "control": int(x["value"]), "treated": int(y["value"]),
                    "alpha_control": int(x["alpha"]), "alpha_treated": int(y["alpha"]),
                    "update_control": int(x["update"]), "update_treated": int(y["update"])})
            if x["move"] == y["move"] and x["update"] != y["update"]:
                update_differences.append({"index": index, "move": x["move"],
                    "control_update": int(x["update"]), "treated_update": int(y["update"]),
                    "control_value": int(x["value"]), "treated_value": int(y["value"])})
        prefix = {"attempt": ordinal, "iteration": int(h["iteration"])}
        if first_value is None and score_differences:
            first_value = {**prefix, **score_differences[0]}
        if first_leader is None and update_differences:
            first_leader = {**prefix, **update_differences[0]}
        if first_order is None and ordering_differences:
            first_order = {**prefix, **ordering_differences[0]}
        if first_window is None and (h["alpha"], h["beta"]) != (ht["alpha"], ht["beta"]):
            first_window = {**prefix,
                "control_alpha_beta": [int(h["alpha"]), int(h["beta"])],
                "treated_alpha_beta": [int(ht["alpha"]), int(ht["beta"])]}
        out.append({**prefix, "candidate_count": len(candidates),
            "same_start_alpha_beta": h["alpha"] == ht["alpha"] and h["beta"] == ht["beta"],
            "control_start_alpha_beta": [int(h["alpha"]), int(h["beta"])],
            "treated_start_alpha_beta": [int(ht["alpha"]), int(ht["beta"])],
            "control_start_nodes": int(h["nodes"]), "treated_start_nodes": int(ht["nodes"]),
            "control_end": {"move": e["move"], "value": int(e["value"]), "nodes": int(e["nodes"])},
            "treated_end": {"move": et["move"], "value": int(et["value"]), "nodes": int(et["nodes"])},
            "same_move_value_changes": len(score_differences),
            "same_move_update_changes": len(update_differences),
            "different_candidate_at_same_index": len(ordering_differences),
            "first_score_change": score_differences[0] if score_differences else None,
            "first_update_change": update_differences[0] if update_differences else None,
            "first_order_change": ordering_differences[0] if ordering_differences else None})
    check(out[-1]["control_end"]["move"] == original["control"]["best"]["move"]
          and out[-1]["treated_end"]["move"] == original["treatment"]["best"]["move"],
          "native root ledger not identical to sealed D1 decision")
    check(first_value is not None and first_value["attempt"] == 17
          and first_value["move"] == "f4e5"
          and (first_value["control"], first_value["treated"]) == (2265, 2280)
          and first_leader is not None and first_leader["attempt"] == 18
          and first_leader["move"] == "f4e5"
          and (first_leader["control_update"], first_leader["treated_update"]) == (0, 1)
          and (first_leader["control_value"], first_leader["treated_value"]) == (2238, 2256),
          "first observed downstream root value/leader transition changed")
    check(first_order is not None and first_order["attempt"] == 17,
          "first subsequent source candidate order divergence changed")
    if depth == 16:
        check(first_window is not None and first_window["attempt"] == 19
              and first_window["control_alpha_beta"] == [1932, 2602]
              and first_window["treated_alpha_beta"] == [1911, 2563],
              "iteration16 initial alpha-beta difference drift")
    else:
        check(first_window is None, "pre-depth16 root window already changed")
    same_iteration = out[15]
    check(same_iteration["attempt"] == 16
          and same_iteration["same_move_value_changes"] == 0
          and same_iteration["same_move_update_changes"] == 0
          and same_iteration["different_candidate_at_same_index"] == 0
          and same_iteration["control_end"]["move"] ==
              same_iteration["treated_end"]["move"] == "d4e5"
          and (same_iteration["control_end"]["nodes"],
               same_iteration["treated_end"]["nodes"]) == (7699, 7717),
          "intervention had a visible enclosing root result in attempt 16")
    check(out[16]["control_end"]["move"] == out[16]["treated_end"]["move"] == "d4e5"
          and out[17]["control_end"]["move"] == "d4e5"
          and out[17]["treated_end"]["move"] == "f4e5",
          "later iteration root recommendation transition changed")
    return {"depth": depth, "root_attempts": out,
            "physical_child_return": [int(a_return["value"]), int(b_return["value"])],
            "actual_treated_child_replies": int(b_return["replies"]),
            "first_root_same_move_value_change": first_value,
            "first_root_leader_update_change": first_leader,
            "first_root_order_index_change": first_order,
            "first_root_start_window_change": first_window,
            "final_fixed_depth_root_choice":
                [original["control"]["best"]["move"], original["treatment"]["best"]["move"]]}


def audit(log_zip, original_science_zip):
    log_bytes = Path(log_zip).read_bytes()
    results_bytes = Path(original_science_zip).read_bytes()
    check(sha(log_bytes) == LOG_SHA, "full original logs ZIP SHA changed")
    check(sha(results_bytes) == RESULT_ZIP_SHA, "full original science ZIP SHA changed")
    with zipfile.ZipFile(log_zip) as logs, zipfile.ZipFile(original_science_zip) as science:
        check(logs.testzip() is None and science.testzip() is None, "source ZIP CRC failed")
        names = logs.namelist()
        check(len(names) == len(set(names)) == 156, "not all 156 original stdout/stderr logs")
        check(science.namelist() == [RESULT_MEMBER], "science ZIP structure changed")
        source_bytes = science.read(RESULT_MEMBER)
        check(sha(source_bytes) == RESULT_JSON_SHA, "original source science JSON SHA changed")
        source = json.loads(source_bytes)
        check(source["actual_new_source_native_searches"] == 78
              and source["classification"] ==
                  "POST_OUTCOME_SELECTED_EXPLORATORY_NATIVE_DEPTH_RESEARCH",
              "wrong historical D1 native experiment")
        case = [c for c in source["results"] if c["source_event_id"] == EVENT]
        check(len(case) == 1, "P2-028 exact source case missing")
        case = case[0]
        target = case["target"]
        check(target["event"] == TARGET and target["attempt"] == "16"
              and target["root"] == "d4e5" and target["tested"] == "g7b7"
              and case["family"] == "fide world open u20 blitz"
              and case["original_32k_bestmove"] == "d4e5"
              and case["treated_32k_bestmove"] == "f4e5",
              "original source event/decision identities changed")
        output = {}
        for depth in (15, 16):
            cells = [c for c in case["fixed_depth_cells"] if c["depth"] == depth]
            check(len(cells) == 1, "source fixed-depth cell missing")
            cell = cells[0]
            check(cell["matched_physical_target"] is True
                  and cell["completed_both_target_depth"] is True
                  and cell["status"] == "VALID_EQUAL_DEPTH_FINAL_CHOICE_CHANGED",
                  "fixed-depth original world did not physically contact target")
            branches = {}
            for kind, arm in (("control", "untouched"), ("treated", "both_off")):
                repeats = []
                for rep in (0, 1):
                    base = f"{EVENT}/depth-{depth}/{arm}-{rep}/"
                    check(base+"stderr.txt" in names and base+"stdout.txt" in names,
                          "original native stdout/stderr member missing")
                    text = logs.read(base+"stderr.txt")
                    stdout = logs.read(base+"stdout.txt").decode().splitlines()
                    frozen = cell["all_repeats"][arm][rep]
                    check(sha(text) == frozen["stderr_sha256"], "original stderr SHA mismatch")
                    check(stdout[-1].split()[1] == frozen["best"]["move"]
                          and stdout[-1].split()[0] == "bestmove",
                          "raw stdout original bestmove mismatched")
                    repeats.append(text)
                check(repeats[0] == repeats[1], "cold original raw native replays differ")
                branches[kind] = parse(repeats[0])
            output[str(depth)] = trace(branches["control"], branches["treated"],
                                       target, depth, cell)
        return {
            "id": "C3X_031_P3_A0_P2_028_INTERITERATION_ROOT_CHRONOLOGY",
            "classification": "RETROSPECTIVE_REAL_NATIVE_LOG_DEVELOPMENT",
            "original_156_log_zip_sha256": LOG_SHA,
            "original_78_native_science_zip_sha256": RESULT_ZIP_SHA,
            "original_science_json_sha256": RESULT_JSON_SHA,
            "original_physical_target": target,
            "source_full_game_sha256": case["game_sha256"],
            "R26_prior_exposed_macro_family": True,
            "new_native_searches": 0,
            "original_D1_native_searches": 78,
            "one_original_development_game": True,
            "same_completed_depth_not_equal_budget": True,
            "TT_history_or_budget_causal_mediator_identified": False,
            "strategic_chess_superiority_demonstrated": False,
            "human_learning_tested": False,
            "source_total_effect_root_transport_observed": True,
            "root_trajectories": output
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_logs_zip", type=Path)
    parser.add_argument("original_D1_science_zip", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()
    result = audit(args.native_logs_zip, args.original_D1_science_zip)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("P3_A0_REAL_ROOT", result["root_trajectories"]["16"]
          ["first_root_leader_update_change"], "new_native_searches", 0,
          "sha", sha(args.output_json.read_bytes()))


if __name__ == "__main__":
    main()
