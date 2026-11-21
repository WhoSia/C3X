"""C3X 0.31/P2-D1 postoutcome equal-depth physical native diagnostic.

Seven previously exposed P2 root flips and 13 fixed-depth cells. Explicitly
NOT independent prospective replication, same node budget or chess-strategy test.
"""
from __future__ import annotations
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_r33_gate_panel import trial
from c3x_030_r33_replay import PRETREATMENT

SAMPLE_SHA = "2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
SOURCE_SHA = "17915c7d9ae56dd950cd026d07a4917a414213415ea3b28af256b305eb8ad146"
TREAT_SHA = "69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f"
BINARY_SHA = "ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"
BASELINE_SHA = "78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb"
NET_SHA = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
FROZEN_CASES = {
    "P2-008-1": (13, 13),
    "P2-027-1": (11, 10),
    "P2-028-0": (16, 15),
    "P2-034-1": (12, 11),
    "P2-035-0": (12, 10),
    "P2-043-1": (11, 9),
    "P2-055-0": (17, 13),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok,why):
    if not ok:
        raise ValueError(why)


def last_nodes(uci):
    rows=[line.split() for line in uci if line.startswith("info depth ")]
    require(rows,"native depth trace absent")
    last=rows[-1]
    require("nodes" in last and "score" in last,"node/score omitted by source")
    return int(last[last.index("nodes")+1])


def real_target(events, frozen):
    matched=[row for row in events if row["open"]["event"]==frozen["event"]]
    if not matched:
        return None,"HOLD_TARGET_ABSENT"
    if len(matched)!=1:
        return None,"HOLD_DUPLICATE_TARGET_ORDINAL"
    row=matched[0]
    if not all(row["open"].get(k)==frozen[k] for k in PRETREATMENT):
        return row,"HOLD_PRECONTACT_TARGET_DRIFT"
    if row["close"]["stopped"]!="0":
        return row,"HOLD_INTERRUPTED_TARGET"
    return row,"SOURCE_TARGET_PHYSICALLY_MATCHED"


def basic(receipt):
    return {
        "best":receipt["proof"]["best"],
        "best_source":receipt["proof"]["best_source"],
        "uci":receipt["uci"],
        "stderr_sha256":receipt["trace"],
        "nodes":last_nodes(receipt["uci"]),
    }


def prepare(args):
    for p,expected in [
        (args.sample,SAMPLE_SHA),(args.source,SOURCE_SHA),
        (args.treated,TREAT_SHA),(args.old,BASELINE_SHA),
        (args.patch,BINARY_SHA),(args.net,NET_SHA)
    ]:
        require(digest(p.read_bytes())==expected,
                "original source pre-D1 identity changed: "+p.name)
    sample=json.loads(args.sample.read_text())
    pre=json.loads(args.source.read_text())
    treated=json.loads(args.treated.read_text())
    positions={r["id"]:r for r in sample["sample"]}
    prior={r["id"]:r for r in pre["source_events"]}
    old={r["id"]:r for r in treated["cases"]}
    require(len(positions)==len(prior)==len(old)==64,
            "historical 64-case denominator unexpectedly changed")
    require(len(FROZEN_CASES)==7 and
            sum(int(e["treatment_bestmove_changed"])
                for x in old.values() for e in x["targets"].values())==7,
            "incorrect postoutcome diagnostic selection")
    for key,(original_depth,treated_depth) in FROZEN_CASES.items():
        game,group=key.rsplit("-",1)
        require(group in ("0","1") and
                original_depth==int(prior[game]["untouched_public"][0])
                and treated_depth==int(old[game]["targets"][group]
                                      ["arms"]["both_off"]["final_completed_depth"])
                and old[game]["targets"][group]["treatment_bestmove_changed"] is True,
                "frozen selected source event or depth drift")
    require(sum(len(set(v)) for v in FROZEN_CASES.values())==13,
            "incorrect preregistered fixed-depth cell denominator")
    return positions,prior,old


def run(args):
    positions,prior,original=prepare(args)
    results=[]
    counter=Counter()
    for event_id,(original_depth,treated_depth) in FROZEN_CASES.items():
        game,group=event_id.rsplit("-",1)
        game_row=positions[game]
        source=prior[game]
        orig=original[game]
        original_target=source["targets"][group]["target"]
        item={"source_event_id":event_id,
              "game_sha256":game_row["game_sha256"],
              "family":game_row["family"],"stratum":group,
              "original_32k_depth":original_depth,
              "treatment_32k_depth":treated_depth,
              "original_32k_bestmove":source["baseline_bestmove"],
              "treated_32k_bestmove":
                  orig["targets"][group]["arms"]["both_off"]["final_move"],
              "target":original_target,
              "fixed_depth_cells":[]}
        for depth in sorted({original_depth,treated_depth}):
            label=f"{event_id}/depth-{depth}"
            reference=trial(args,game_row,label+"/R31-reference",
                            binary=args.old,observer=False,nodes=None,depth=depth)
            counter["native_searches"]+=1
            unobserved=trial(args,game_row,label+"/R33-off",
                             binary=args.patch,observer=False,nodes=None,depth=depth)
            counter["native_searches"]+=1
            require(reference["uci"]==unobserved["uci"] and
                    reference["proof"]==unobserved["proof"],
                    "observer-disabled native parity failed at "+label)
            arms={}
            for treatment in ("untouched","both_off"):
                replays=[]
                for rep in (0,1):
                    is_treatment=treatment=="both_off"
                    trace=trial(args,game_row,label+f"/{treatment}-{rep}",
                                binary=args.patch,observer=True,
                                target=int(original_target["event"]),
                                skip_f=is_treatment,skip_n=is_treatment,
                                nodes=None,depth=depth)
                    counter["native_searches"]+=1
                    matched,status=real_target(trace["events"],original_target)
                    if matched is not None and status=="SOURCE_TARGET_PHYSICALLY_MATCHED":
                        close=matched["close"]
                        if close["skip_f"]!=str(int(is_treatment)) or close["skip_n"]!=str(int(is_treatment)):
                            status="HOLD_INSTRUMENT_GATE_FLAG_MISMATCH"
                    replays.append({**basic(trace),
                                    "contact_status":status,
                                    "target_event":matched,
                                    "actual_completed_depth":int(trace["proof"]["best"]["completed"])})
                # Cold source replays must be deterministic independently of contact.
                for key in ("uci","best","best_source","contact_status","target_event","nodes"):
                    require(replays[0][key]==replays[1][key],
                            "nonreproducible fixed-depth source repeated run "+label+"/"+treatment+"/"+key)
                if not is_treatment:
                    require(reference["uci"]==replays[0]["uci"] and
                            reference["proof"]["best"]==replays[0]["best"] and
                            reference["proof"]["best_source"]==replays[0]["best_source"],
                            "observer-only fixed-depth changed root "+label)
                arms[treatment]=replays
            a,b=arms["untouched"][0],arms["both_off"][0]
            complete=(a["actual_completed_depth"]==depth and
                      b["actual_completed_depth"]==depth)
            contact=(a["contact_status"]==b["contact_status"]==
                     "SOURCE_TARGET_PHYSICALLY_MATCHED")
            if not complete:
                status="HOLD_COMPLETED_DEPTH"
            elif not contact:
                status="HOLD_SOURCE_CONTACT_OR_IDENTITY"
            elif a["best"]["move"]==b["best"]["move"]:
                status="VALID_EQUAL_DEPTH_NO_FINAL_CHOICE_CHANGE"
            else:
                status="VALID_EQUAL_DEPTH_FINAL_CHOICE_CHANGED"
            cell={
                "depth":depth,
                "is_original_completed_depth":depth==original_depth,
                "status":status,
                "matched_physical_target":contact,
                "completed_both_target_depth":complete,
                "root_choice_changed":a["best"]["move"]!=b["best"]["move"],
                "reference_native":basic(reference),
                "observer_disabled_native":basic(unobserved),
                "control":a,
                "treatment":b,
                "all_repeats":arms
            }
            item["fixed_depth_cells"].append(cell)
            counter["depth_cells"]+=1
            counter["contact_verified"]+=int(contact)
            counter[status]+=1
            print("P2_D1_CASE",event_id,"depth",depth,
                  "contact",contact,"status",status,
                  "old",a["best"]["move"],"new",b["best"]["move"],
                  "nodes",a["nodes"],b["nodes"],flush=True)
        results.append(item)
    require(len(results)==7 and counter["depth_cells"]==13
            and counter["native_searches"]==78,
            "full frozen D1 requested search count truncated")
    summary=Counter()
    for row in results:
        original_cell=next(cell for cell in row["fixed_depth_cells"]
                           if cell["is_original_completed_depth"])
        summary[original_cell["status"]]+=1
    return {
        "id":"C3X_031_P2_D1_EQUAL_DEPTH_DIAGNOSIS",
        "classification":"POST_OUTCOME_SELECTED_EXPLORATORY_NATIVE_DEPTH_RESEARCH",
        "first_p2_source_original_sha256":SOURCE_SHA,
        "first_p2_treated_original_sha256":TREAT_SHA,
        "frozen_seven_source_events":list(FROZEN_CASES),
        "seven_postselected_cases":len(results),
        "frozen_depth_cells":13,
        "actual_new_source_native_searches":counter["native_searches"],
        "run_counts":dict(counter),
        "original_completed_depth_verdict":dict(summary),
        "same_depth_not_same_node_budget":True,
        "full_history_original_game_used":True,
        "intermediate_TT_history_mediator_proved":False,
        "independent_chess_move_superiority_proved":False,
        "human_learning_measured":False,
        "results":results,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("sample","source","treated","old","patch","net","out","private","public"):
        p.add_argument(key,type=Path)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    results=run(args)
    args.private.parent.mkdir(parents=True,exist_ok=True)
    args.private.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    pub={k:v for k,v in results.items() if k!="results"}
    pub["per_event"]=[
        {"id":r["source_event_id"],
         "original_completed_depth":r["original_32k_depth"],
         "cells":[{"depth":c["depth"],"status":c["status"],
                   "control_move":c["control"]["best"]["move"],
                   "treated_move":c["treatment"]["best"]["move"],
                   "control_nodes":c["control"]["nodes"],
                   "treated_nodes":c["treatment"]["nodes"]}
                  for c in r["fixed_depth_cells"]]}
        for r in results["results"]]
    args.public.parent.mkdir(parents=True,exist_ok=True)
    args.public.write_text(json.dumps(pub,indent=2,sort_keys=True)+"\n")
    print("P2_D1_FINAL",results["original_completed_depth_verdict"],
          "actual_native_searches",results["actual_new_source_native_searches"],
          "sha",digest(args.private.read_bytes()))


if __name__=="__main__":
    main()
