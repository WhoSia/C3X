#!/usr/bin/env python3
"""C3X 0.20-C precommitted alpha-boundary ladder on fixed February game #3.

Research endpoint: final categorical chess bestmove; native branch gate is
instrumented as the intervention reaches the original Stockfish16 root source.
No novel sample selection or outcome-driven threshold search occurs here.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play, need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES, mask_filters
from c3x_019_Feb_four_first_root_return_rescue_native import SOURCE_SHA, PRIOR_SHA
from c3x_020_B_minimal_multi_state_native_court import OLD_NATIVE_SHA

PRECOMMIT = "c3x/ontology/c3x-020-C-alpha-gate-root-choice-transmission-and-prospective-forecast-precommit.md"
B_NATIVE_SHA = "0d9d4c3a1fce8b7ae048df4341075a4bc985fdabbab3cd40f664ad7ad7e66bb6"
GAME = 3
ROLE = "STRICT"
ALPHA, BETA = -190, -166
F_MOVE, V_MOVE = "a1c1", "e1e3"
ORIGINAL_VALUE = -179
TARGETS = (("L0", -206, "a1c1"),
           ("L1", -191, "a1c1"),
           ("L2", -190, "a1c1"),
           ("L3", -189, "e1e3"),
           ("L4", -180, "e1e3"),
           ("L5", -179, "e1e3"))

def verify_data(path, sha):
    data = Path(path).read_bytes()
    need(hashlib.sha256(data).hexdigest() == sha,
         "C3X020C_INPUT_SHA_" + Path(path).name)
    return json.loads(data)

def treatment(value, mode="REPAIR", sham=False):
    need(type(value) is int and -32000 < value < 32000, "C_TARGET_INTEGER")
    need(mode in ("OBS", "REPAIR"), "C_MODE")
    return {
        "depth": 4, "root_call": 4, "trial": 1,
        "move": 65535 if sham else 222,
        "index": 5, "alpha": ALPHA, "beta": BETA,
        "expected": ORIGINAL_VALUE, "target": value, "mode": mode
    }

def terminal_by_depth(events):
    result = {}
    for event in events:
        if event["kind"] == "after_sort":
            d = event["depth"]
            need(1 <= d <= 12, "INVALID_AFTER_SORT_DEPTH")
            result[d] = event
    need(set(result) == set(range(1,13)), "MISSING_ROOT_TRIAL_DEPTH")
    return {str(d): {
        "leader_native": event["first_move"],
        "score": event["first_score"],
        "window_value": event["value"],
        "trial": event["trial"],
        "window_alpha": event["alpha"],
        "window_beta": event["beta"],
    } for d,event in result.items()}

def cold(engine, world, clocks, physical, mode="FIRST", config=None):
    options = {"fen_clocks": clocks}
    if config is not None:
        options["multi_state"] = {"second": config, "boundary": None}
    source = "OBS" if mode == "F" else "V"
    target = None if mode == "F" else physical["physical"]
    if mode != "F":
        options["tt_reader_filters"] = mask_filters(RULES[ROLE], physical, "FIRST")
    a = play(engine, world, "F", source, target, **options)
    b = play(engine, world, "F", source, target, **options)
    need(a == b, "COLD_REPEAT_MISMATCH")
    need(a["root_events"] and len(a["root_events"]) < 4096,
         "CENSORED_OR_MISSING_ROOT_EVENTS")
    return {
        "UCI": a["UCI"],
        "second_return_events": a["second_return_events"],
        "terminal_depth": terminal_by_depth(a["root_events"]),
        "native_V_reader_calls": [e["root_call"] for e in a["blocks"]
                                  if e["kind"] == "reader_block"],
        "cold_twice": True
    }

def observed_gate(value, contact):
    """Exact branch requirements; keep root source and expected outcome separate."""
    need(len(contact) == 1 and contact[0]["kind"] == "repaired",
         "MISSING_ACTUAL_NATIVE_CONTACT")
    event = contact[0]
    need(event["depth"] == 4 and event["root_call"] == 4
         and event["trial"] == 1 and event["move"] == 222
         and event["index"] == 5 and event["alpha"] == ALPHA
         and event["beta"] == BETA and event["before"] == ORIGINAL_VALUE
         and event["after"] == value and event["target"] == value,
         "CONTACT_COORDINATE_OR_DOSE_DRIFT")
    expected_gate = int(value > ALPHA)
    need(event["candidate_update_gate"] == expected_gate
         and event["alpha_improvement_gate"] == expected_gate
         and event["beta_boundary_gate"] == int(value >= BETA),
         "SOURCE_GATE_LOG_DISAGREES_WITH_STOCKFISH")
    return {"candidate_update": expected_gate,
            "alpha_improvement": expected_gate,
            "beta_boundary": int(value >= BETA),
            "native_value_changed": value != ORIGINAL_VALUE}

def classify_ladder(results):
    need([r["label"] for r in results] == [r[0] for r in TARGETS],
         "FROZEN_LADDER_ORDER")
    tested = len(results)
    correct = sum(bool(r["predict_bestmove_correct"]) for r in results)
    up = {r["label"]:r for r in results}
    sharp_gate = all(r["predict_bestmove_correct"] for r in results)
    one_unit_cross = (up["L2"]["bestmove"] == F_MOVE
                      and up["L3"]["bestmove"] == V_MOVE
                      and up["L2"]["actual_gate"]["candidate_update"] == 0
                      and up["L3"]["actual_gate"]["candidate_update"] == 1)
    return {
        "denominator": tested,
        "sharp_gate_H_G": "PASS" if sharp_gate else "FAIL",
        "one_unit_discontinuity_H_C": "PASS" if one_unit_cross else "FAIL",
        "correct_predictions": correct,
        "alpha": ALPHA,
        "no_selection_retargeting": True,
        "historical_F19_5": "FAIL_RETAINED",
        "historical_K4": "FAIL_0_OF_4_RETAINED",
        "exploratory_current_game": True
    }

def main():
    ap=argparse.ArgumentParser()
    for x in ("source","prior","frozen-B","engine","out"):
        ap.add_argument("--"+x,required=True)
    args=ap.parse_args()
    games=verify_data(args.source,SOURCE_SHA)
    old=verify_data(args.prior,PRIOR_SHA)
    b=verify_data(args.frozen_B,B_NATIVE_SHA)
    need(len(games["selected"])==len(old["cases"])==16, "SOURCE_GAME_DENOMINATOR")
    need([c["game"] for c in b["cases"]]==[3,6,7,10],
         "PREVIOUS_COURT_FOUR_DENOMINATOR")
    prior=b["cases"][0]
    need(prior["role"]==ROLE and prior["game"]==GAME,"GAME_ROLE_DRIFT")
    world,_=canonical_engine_world(games["selected"][GAME-1])
    clocks=game_clocks(games["selected"][GAME-1])
    selected=old["cases"][GAME-1]["selectors"][ROLE]["selection"]
    f=cold(args.engine,world,clocks,selected,"F")
    v=cold(args.engine,world,clocks,selected,"FIRST")
    need(f["UCI"]==prior["arms"]["F_OBS"]["UCI"] and
         v["UCI"]==prior["arms"]["FIRST"]["UCI"],
         "FROZEN_F_OR_FIRST_UCI_DRIFT")
    obs=cold(args.engine,world,clocks,selected,config=treatment(ORIGINAL_VALUE,mode="OBS"))
    sham=cold(args.engine,world,clocks,selected,config=treatment(ORIGINAL_VALUE,sham=True))
    need(obs["UCI"]==v["UCI"] and sham["UCI"]==v["UCI"],
         "OBS_SHAM_INTERFERED_WITH_NATIVE_CHESS")
    need(len(obs["second_return_events"])==1
         and obs["second_return_events"][0]["kind"]=="observed"
         and obs["second_return_events"][0]["before"]==ORIGINAL_VALUE
         and obs["second_return_events"][0]["after"]==ORIGINAL_VALUE
         and not sham["second_return_events"],
         "OBS_SHAM_UNEXPECTED_CONTACT")
    need(f["UCI"]["bestmove"]==F_MOVE and v["UCI"]["bestmove"]==V_MOVE,
         "HISTORICAL_CATEGORICAL_DRIFT")

    report={"schema":"c3x020-C-native-alpha-threshold-ladder-v1",
            "study":"PRECOMMITTED_MECHANISTIC_THRESHOLD_SWEEP_ON_KNOWN_ADAPTIVE_GAME3",
            "source_selection":"UNCHANGED_FEBRUARY_GAME3_STRICT",
            "native_pinned_stockfish":"68e1e9b3811e16cad014b590d7443b9063b52",
            "precommit":PRECOMMIT,
            "input_sha256":{"original_february":SOURCE_SHA,"prior_native":PRIOR_SHA,"B_native":B_NATIVE_SHA},
            "controls":{"F":f,"FIRST":v,"OBS":obs,"SHAM":sham},
            "ladder":[]}
    for label,value,pred in TARGETS:
        row=cold(args.engine,world,clocks,selected,config=treatment(value))
        gate=observed_gate(value,row["second_return_events"])
        result={"label":label,"target":value,"bestmove":row["UCI"]["bestmove"],
                "expected_bestmove":pred,
                "predict_bestmove_correct":row["UCI"]["bestmove"]==pred,
                "restored_F_bestmove":row["UCI"]["bestmove"]==F_MOVE,
                "actual_gate":gate,"UCI":row["UCI"],
                "terminal_depth":row["terminal_depth"],
                "cold_twice":row["cold_twice"]}
        if label=="L0":
            need(row["UCI"]==prior["arms"]["SECOND_ONLY"]["UCI"],
                 "HISTORICAL_SECOND_ONLY_UCI_DRIFT")
        if label=="L5":
            need(row["UCI"]==v["UCI"], "ZERO_DOSE_CONTROL_DRIFT")
        report["ladder"].append(result)
        print("C3X020C_LADDER",label,"target",value,"alpha_gate",
              gate["candidate_update"],"final_bestmove",
              result["bestmove"],"H_G_correct",int(result["predict_bestmove_correct"]),flush=True)
    report["summary"]=classify_ladder(report["ladder"])
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("C3X020C_RISKY_THRESHOLD_PREDICTION_VERDICT",
          json.dumps(report["summary"],sort_keys=True),flush=True)

if __name__=="__main__":
    main()
