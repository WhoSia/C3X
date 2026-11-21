"""P3-X2: do the exposed source bestmove flips survive fixed depth caps?

Three ORIGINAL P2 source cases were selected and disclosed in a GitHub
protocol BEFORE running this follow-up. An entire (D,D+1) ×
(32k,64k) × (sham twice, F-only once, both-off twice) native matrix is
executed without cherry-picked source retargeting (60 genuine searches).

A GO with both nodes and depth is capped by EITHER, not equal visited nodes.
The raw UCI and R23 source receipts are preserved even on missing contacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from c3x_030_r33_gate_panel import trial
from c3x_030_r33_replay import focus
from c3x_031_p2_1669_native_discovery import (
    SAMPLE_SHA, PATCHED_BINARY_SHA, NNUE_SHA, require, digest
)
from c3x_031_p2_1669_native_treatment import B1_SHA
from c3x_031_p3_x1_gate_factorial import B2_SHA

FROZEN_THREE = (
    ("P2-005-0", 12, "g8f8", "g7g6"),
    ("P2-052-1", 11, "a7c7", "e5d6"),
    ("P2-056-1", 13, "b8d8", "h5e2"),
)
NODES=(32000,64000)
DEPTH_OFFSETS=(0,1)
ARMS=(
    ("sham0",False,False),
    ("sham1",False,False),
    ("futility_only",True,False),
    ("both_off0",True,True),
    ("both_off1",True,True),
)
TOTAL_NEW_NATIVE_SEARCHES=len(FROZEN_THREE)*len(NODES)*len(DEPTH_OFFSETS)*len(ARMS)
UCI_DEPTH=re.compile(r"^info depth (\d+)\b")
UCI_NODES=re.compile(r"\bnodes (\d+)\b")


def verify_sources(args):
    for path,sha in ((args.sample,SAMPLE_SHA),(args.b1,B1_SHA),
                     (args.b2,B2_SHA),(args.patch,PATCHED_BINARY_SHA),
                     (args.net,NNUE_SHA)):
        require(digest(path)==sha,"P3-X2 originally frozen identity changed")
    original=json.loads(args.sample.read_text())
    b1=json.loads(args.b1.read_text())
    b2=json.loads(args.b2.read_text())
    cases={r["id"]:r for r in original["positions"]}
    observed={r["id"]:r for r in b1["native_source_records"]}
    outcomes={r["id"]:r for r in b2["source_event_results"]}
    require(len(cases)==64 and len(observed)==64 and len(outcomes)==128,
            "P3-X2 historical denominators changed")
    for case,D,old,new in FROZEN_THREE:
        require(case in outcomes and D in (11,12,13),"wrong originally selected follow-up case")
        r=outcomes[case]
        require(r["valid_primary"] and r["y"]==1
                and r["original_untreated_bestmove"]==old
                and r["arms"]["both_off0"]["bestmove"]==new
                and r["original_target"]==
                    observed[r["case_id"]]["targets"][r["group"]]["native_open_close"]["open"],
                "exposed original same-reported-completed-depth source case changed")
        require(len(cases[r["case_id"]]["moves"])==cases[r["case_id"]]["ply"],
                "original full game history missing")
    return cases,outcomes


def reported_uci(trace):
    depths, nodes=[],[]
    for line in trace:
        if not line.startswith("info depth "):
            continue
        matched=UCI_DEPTH.match(line)
        require(matched is not None,"public depth line malformed")
        depths.append(int(matched.group(1)))
        node=UCI_NODES.search(line)
        if node:
            nodes.append(int(node.group(1)))
    require(len(depths)>0 and len(nodes)>0 and
            len(depths)==len(nodes),"unclear UCI depth/node accounting")
    return {"last_reported_uci_depth":depths[-1],
            "max_reported_uci_depth":max(depths),
            "last_reported_uci_nodes":nodes[-1],
            "all_reported_depths":depths}


def extract_arm(row,receipt,cap,budget,skip_f,skip_n):
    target=focus(receipt["events"],row["original_target"])
    require(target["open"]==row["original_target"],
            "same source event not physically contacted under horizon")
    close=target["close"]
    require(close["stopped"]=="0" and
            close["skip_f"]==str(int(skip_f)) and
            close["skip_n"]==str(int(skip_n)),
            "source event flags interrupted or mismatched under depth cap")
    require(receipt["proof"]["best"]["move"]==receipt["uci"][-1].split()[1],
            "native root winner and public bestmove differ")
    depth=reported_uci(receipt["uci"])
    require(depth["max_reported_uci_depth"]<=cap,
            "actual engine exceeded requested depth cap")
    return {
        "source_treatment": {"futility_disabled":skip_f,"null_disabled":skip_n},
        "genuine_source_event":{"open":target["open"],"close":close},
        "native_root_best":receipt["proof"]["best"],
        "native_root_source":receipt["proof"]["best_source"],
        "native_proof":receipt["proof"],
        "native_stderr_sha256":receipt["trace"],
        "native_uci":receipt["uci"],
        "public_budget_cap_nodes":budget,
        "public_budget_cap_depth":cap,
        **depth,
    }


def execute(args):
    cases,outcomes=verify_sources(args)
    args.out.mkdir(parents=True,exist_ok=True)
    matrix=[]
    for case,D,baseline,new in FROZEN_THREE:
        old=outcomes[case]
        pos=cases[old["case_id"]]
        for budget in NODES:
            for offset in DEPTH_OFFSETS:
                cap=D+offset
                name=f"{case}/nodes{budget}/depth{cap}"
                record={
                    "original_target":case,
                    "game_id":old["case_id"],
                    "family":old["family"],
                    "prior_original_node_budget":32000,
                    "original_P2_sham_move":baseline,
                    "original_P2_both_off_move":new,
                    "previously_reported_completed_depth":D,
                    "horizon_node_cap":budget,
                    "horizon_depth_cap":cap,
                    "actual_source_searches":len(ARMS),
                    "arms":{},"valid":False,"error":None,
                    "same_depthcap_root_flip":None,
                    "incremental_null_flip_given_futility_off":None,
                }
                for arm,f,n in ARMS:
                    try:
                        receipt=trial(args,pos,name+"/"+arm,binary=args.patch,
                                      observer=True,
                                      target=int(old["original_target"]["event"]),
                                      skip_f=f,skip_n=n,nodes=budget,depth=cap)
                        record["arms"][arm]=extract_arm(old,receipt,cap,budget,f,n)
                    except (ValueError,KeyError,IndexError,AssertionError) as err:
                        reason=f"{type(err).__name__}: {err}"
                        record["arms"][arm]={"status":"PHYSICAL_INVALID","reason":reason}
                        if record["error"] is None:record["error"]=reason
                if record["error"] is None:
                    arms=record["arms"]
                    if arms["sham0"]!=arms["sham1"]:
                        record["error"]="SHAM_COLD_REPLAY_DIVERGENCE"
                    elif arms["both_off0"]!=arms["both_off1"]:
                        record["error"]="TREATMENT_COLD_REPLAY_DIVERGENCE"
                    else:
                        record["valid"]=True
                        record["same_depthcap_root_flip"]=int(
                            arms["sham0"]["native_root_best"]["move"]!=
                            arms["both_off0"]["native_root_best"]["move"])
                        record["incremental_null_flip_given_futility_off"]=int(
                            arms["futility_only"]["native_root_best"]["move"]!=
                            arms["both_off0"]["native_root_best"]["move"])
                matrix.append(record)
                print("P3_X2_NATIVE",case,"nodes",budget,"cap",cap,
                      "valid",record["valid"],"flip",
                      record["same_depthcap_root_flip"],"failure",record["error"],flush=True)
    require(len(matrix)==12 and sum(r["actual_source_searches"] for r in matrix)==
            TOTAL_NEW_NATIVE_SEARCHES,"P3-X2 60 original search denominator changed")
    valid=[r for r in matrix if r["valid"]]
    return {
        "schema":"C3X_031_P3_X2_DEPTH_CAPPED_HORIZON_TRANSPORT_V1",
        "study_class":"POST_OUTCOME_SELECTED_THREE_CASES_EXPLORATORY_NOT_UNSEEN",
        "source_sample_sha256":SAMPLE_SHA,
        "source_B1_signed_events_sha256":B1_SHA,
        "source_B2_original_effects_sha256":B2_SHA,
        "pinned_patched_stockfish_sha256":PATCHED_BINARY_SHA,
        "neural_network_sha256":NNUE_SHA,
        "three_fixed_exposed_original_P2_events":[r[0] for r in FROZEN_THREE],
        "fixed_12_horizon_cells":12,
        "actual_new_native_searches":TOTAL_NEW_NATIVE_SEARCHES,
        "physically_contacted_valid_cells":len(valid),
        "invalid_or_missed_original_event_cells":12-len(valid),
        "original_same_depth_cap_root_flip_cells":sum(r["same_depthcap_root_flip"]
                                                      for r in valid),
        "original_same_depth_cap_incremental_null_flip_cells":sum(
            r["incremental_null_flip_given_futility_off"] for r in valid),
        "horizon_cells":matrix,
        "limitations":[
            "This is a follow-up selected after P2 root flip outcomes were exposed.",
            "Both depth and node caps are imposed; visited nodes may differ.",
            "Missing predeclared target signatures are counted, not retrospectively retargeted.",
            "Same nominal depth cap is not a matched internal TT/history state.",
            "Any source root flip is not an independent chess plan superiority result.",
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("sample","b1","b2","patch","net","out","result"):
        ap.add_argument(k,type=Path)
    a=ap.parse_args()
    data=execute(a)
    a.result.parent.mkdir(parents=True,exist_ok=True)
    a.result.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("P3_X2_DEPTHCAP_VERDICT",data["physically_contacted_valid_cells"],
          "of 12, flips",data["original_same_depth_cap_root_flip_cells"],
          "of valid, new real searches",data["actual_new_native_searches"],
          "sha256",digest(a.result))


if __name__=="__main__":
    main()
