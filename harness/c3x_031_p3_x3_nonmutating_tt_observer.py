"""P3-X3: source-first TT entry snapshot from ORIGINAL Stockfish16 lookup.

Read the tte/ttMove/ttValue fields already obtained in original search
at the exact source R33 futility event; do NOT add an age-refreshing TT.probe.

Seven P2-exposed original events are fixed before R39 experiment.
Each of three original R33 arms runs observational R39 off once and
R39 on twice: 7*3*3=63 genuine new Stockfish16 searches. The source
original root/proof/UCI must be unchanged from P2, and snapshot must
be byte-identical across repeated cold processes and all three arms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_r23_native_replay import run
from c3x_030_r33_gate_panel import events
from c3x_030_r33_replay import focus
from c3x_031_p2_1669_native_discovery import (
    SAMPLE_SHA, NNUE_SHA, PATCHED_BINARY_SHA, require, digest
)
from c3x_031_p3_x1_gate_factorial import B1_SHA, B2_SHA

FROZEN_CASES=(
    "P2-005-0",              # primary F-only, source zero-null comparison
    "P2-013-1",
    "P2-021-1",
    "P2-041-1",
    "P2-052-1",
    "P2-056-1",
    "P2-058-1",
)
ARMS=(
    ("sham",False,False,"sham0"),
    ("futility_only",True,False,"futility_only"),
    ("both_off",True,True,"both_off0"),
)
MODES=("observer_off","observer_on0","observer_on1")
NEW_SOURCE_SEARCHES=len(FROZEN_CASES)*len(ARMS)*len(MODES)
STATE_KEYS=(
    "event","key","tt_hit","tt_move","tt_depth","tt_bound","tt_raw_value",
    "tt_value","tt_eval","tt_pv","parent_stat","rule50","source_nodes"
)


def parse_state(lines):
    found=[]
    for line in lines:
        if line.startswith("C3X_R39_PRE "):
            data={}
            for token in line.split()[1:]:
                require("=" in token,"R39 source field lacking key=value")
                key,val=token.split("=",1)
                require(key not in data, "duplicate R39 source field "+key)
                data[key]=val
            require(set(data)==set(STATE_KEYS),"R39 source TT pre-event schema drift")
            for k in STATE_KEYS:
                if k!="tt_move":
                    int(data[k])    # permits negative mate/internal VALUE_NONE
            require(int(data["tt_hit"]) in (0,1) and
                    int(data["tt_pv"]) in (0,1) and
                    int(data["rule50"])>=0 and
                    int(data["source_nodes"])>=0,
                    "invalid raw TT pre-event state value")
            found.append(data)
    return found


def trial_r39(args,case,name,event_id,skip_f,skip_n,observe):
    env={
        "C3X_R33_OBSERVE":"1",
        "C3X_R33_TARGET":str(event_id),
        "C3X_R33_SKIP_FUTILITY":str(int(skip_f)),
        "C3X_R33_SKIP_NULL":str(int(skip_n)),
        "C3X_R39_TT_SNAPSHOT":str(int(observe)),
        "C3X_R29_PROBES":"0",
        "C3X_R31_OBSERVE":"0",
        "C3X_NO_TT_PICKER":"0",
        "C3X_NO_TT_VALUE":"0",
        "C3X_R29_MASK_MOVE":"0",
        "C3X_R29_MASK_VALUE":"0",
    }
    folder=args.out/name
    uci,proof=run(args.patch,{"history":case["moves"]},args.net,folder,
                  logging=True,paired=False,nnue=True,nodes=32000,
                  environment=env)
    lines=(folder/"stderr.txt").read_text().splitlines()
    return {"uci":uci,"proof":proof,
            "source_events":events(lines),
            "R39":parse_state(lines),
            "stderr_sha256":digest(folder/"stderr.txt")}


def original_signatures(args):
    for name,expected in (("sample",SAMPLE_SHA),("b1",B1_SHA),
                          ("b2",B2_SHA),("net",NNUE_SHA),
                          ("p2_reference",PATCHED_BINARY_SHA)):
        require(digest(getattr(args,name))==expected,
                "P3-X3 historical original physical source SHA changed: "+name)
    sample=json.loads(args.sample.read_text())
    b1=json.loads(args.b1.read_text())
    b2=json.loads(args.b2.read_text())
    cases={r["id"]:r for r in sample["positions"]}
    originals={r["id"]:r for r in b1["native_source_records"]}
    outcomes={r["id"]:r for r in b2["source_event_results"]}
    require(len(cases)==64 and len(originals)==64 and len(outcomes)==128,
            "original source census changed")
    for id in FROZEN_CASES:
        old=outcomes[id]
        require(old["valid_primary"] and old["y"]==1,
                "original root flip eligibility changed")
        before=originals[old["case_id"]]["targets"][old["group"]]
        require(old["original_target"]==before["native_open_close"]["open"],
                "P3-X3 source event reselected")
    return cases,outcomes


def verified_source_arm(original,trial,prior_arm,observe):
    source=focus(trial["source_events"],original["original_target"])
    require(source["open"]==original["original_target"],
            "R39 did not contact exact original native R33 source event")
    require(source["close"]==prior_arm["target_event"]["close"],
            "R39 source final child return/flags differ from original R33")
    require(trial["uci"]==prior_arm["source_uci"] and
            trial["proof"]["best"]==prior_arm["proof"] and
            trial["proof"]["best_source"]==prior_arm["root_producer"],
            "R39 observer/overlay changed original native search or root proof")
    require(len(trial["R39"])==(1 if observe else 0),
            "R39 snapshot count incorrect or observer-off leaked")
    if not observe:
        return None
    state=trial["R39"][0]
    require(state["event"]==original["original_target"]["event"]
            and state["key"]==original["original_target"]["key"]
            and state["source_nodes"]==original["original_target"]["nodes"],
            "R39 pre-gate TT state not aligned with original event")
    require(state["tt_hit"]=="1" or
            (state["tt_depth"]=="-99" and state["tt_bound"]=="0"),
            "TT miss was incorrectly logged as a valid original entry")
    return state


def execute(args):
    cases,outcomes=original_signatures(args)
    args.out.mkdir(parents=True,exist_ok=True)
    results=[]
    for id in FROZEN_CASES:
        original=outcomes[id]
        position=cases[original["case_id"]]
        site={"id":id,"family":original["family"],"source_event":original["original_target"],
              "arms":{},"site_valid":False,"pre_source_tt_snapshot":None}
        for label,off_f,off_n,prior_name in ARMS:
            prior=original["arms"][prior_name]
            row={"old_reference_arm":prior_name,"source_variants":{},
                 "tt_snapshots":[],"valid":False,"failure":None}
            for mode in MODES:
                name=f"{id}/{label}/{mode}"
                observing=mode.startswith("observer_on")
                try:
                    observed=trial_r39(args,position,name,
                                       int(original["original_target"]["event"]),
                                       off_f,off_n,observing)
                    snapshot=verified_source_arm(original,observed,prior,observing)
                    row["source_variants"][mode]={
                        "observed":observing,
                        "native_bestmove":observed["proof"]["best"]["move"],
                        "original_uci_sha256":hashlib.sha256(
                            ("\n".join(observed["uci"])+"\n").encode()).hexdigest(),
                        "stderr_sha256":observed["stderr_sha256"],
                        "target_source_event":focus(
                            observed["source_events"],original["original_target"]),
                        "R39_source_snapshot":snapshot,
                        "original_R23_best_producer":observed["proof"]["best_source"],
                    }
                    if snapshot is not None:
                        row["tt_snapshots"].append(snapshot)
                except (ValueError,KeyError,IndexError,AssertionError) as err:
                    row["failure"]=f"{type(err).__name__}: {err}"
                    row["source_variants"][mode]={"status":"INVALID_PHYSICAL_OBSERVER",
                                                  "reason":row["failure"]}
            if row["failure"] is None:
                a=row["source_variants"]
                if (len(row["tt_snapshots"])!=2 or
                    row["tt_snapshots"][0]!=row["tt_snapshots"][1] or
                    a["observer_on0"]["stderr_sha256"]!=a["observer_on1"]["stderr_sha256"]):
                    row["failure"]="R39_SNAPSHOT_OR_SOURCE_COLD_REPEAT_DIVERGED"
                else:
                    row["valid"]=True
            site["arms"][label]=row
            print("P3_X3_TT_SOURCE",id,label,
                  "valid",row["valid"],"error",row["failure"],flush=True)
        if all(arm["valid"] for arm in site["arms"].values()):
            s=[site["arms"][arm]["tt_snapshots"][0] for arm,_,_,_ in ARMS]
            if s[0]==s[1]==s[2]:
                site["site_valid"]=True
                site["pre_source_tt_snapshot"]=s[0]
            else:
                site["same_event_TT_snapshot_failure"]="SOURCE_PRE_EVENT_TT_DIFFERS_BETWEEN_ARMS"
        results.append(site)
    require(len(results)==7 and sum(
        len(r["arms"][x]["source_variants"]) for r in results for x,_,_,_ in ARMS
        )==NEW_SOURCE_SEARCHES,"P3-X3 63 real-search denominator changed")
    complete=sum(row["site_valid"] for row in results)
    hits=sum(row["pre_source_tt_snapshot"]["tt_hit"]=="1" for row in results
             if row["site_valid"])
    return {
        "schema":"C3X_031_P3_X3_NONMUTATING_PRE_GATE_TT_SOURCE_NATIVE_V1",
        "study_class":"PRE_GATE_OBSERVER_ON_P2_EXPOSED_SEVEN_CASES_NOT_INDEPENDENT",
        "origin_original_stockfish_p2_binary_sha256":PATCHED_BINARY_SHA,
        "new_r39_binary_sha256":digest(args.patch),
        "original_nnue_sha256":NNUE_SHA,
        "original_source_sample_sha256":SAMPLE_SHA,
        "original_B1_event_preoutcome_sha256":B1_SHA,
        "original_B2_causal_outcome_sha256":B2_SHA,
        "original_fixed_exposed_source_events":list(FROZEN_CASES),
        "new_native_stockfish_source_searches":NEW_SOURCE_SEARCHES,
        "original_source_case_count":7,
        "original_source_arm_count":len(FROZEN_CASES)*len(ARMS),
        "fully_passive_ttsnapshot_sites":complete,
        "failed_sites":7-complete,
        "actual_pre_gate_TT_hits_on_verified_sites":hits,
        "TT_snapshots_are_pre_event_not_postcausal_mediator":True,
        "no_extra_age_refreshing_TT_probe":True,
        "source_site_results":results,
        "scientific_claims":[
            "Original R39 pre-event TT fields directly read from existing Stockfish16 probe.",
            "No new TT.probe performed. R39 original root UCI/producer parity verified or marked HOLD.",
            "All seven cases were postoutcome selected from P2; no blind state classifier estimate.",
            "Pre-gate TT observation cannot identify mediator post-source causal sufficiency.",
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ("sample","b1","b2","p2_reference","patch","net","out","result"):
        ap.add_argument(name,type=Path)
    a=ap.parse_args()
    d=execute(a)
    a.result.parent.mkdir(parents=True,exist_ok=True)
    a.result.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("P3_X3_SAFE_TT_SNAPSHOT",d["fully_passive_ttsnapshot_sites"],
          "of 7, hits",d["actual_pre_gate_TT_hits_on_verified_sites"],
          "searches",d["new_native_stockfish_source_searches"],
          "sha",digest(a.result))


if __name__=="__main__":
    main()
