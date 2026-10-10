#!/usr/bin/env python3
"""C3X021-P1 source-frozen 16-game Stockfish16 TT × atomic chess action court.

No outcome-driven sampling, no refitting selectors, no post-hoc chess motifs.
This program first sees March native depth12 output AFTER atomic transitions
for all 635 legal root moves were already computed and independently frozen.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair,mask_filters

SOURCE_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
ATOMIC_SHA="c14711c0e31bde26c2c7fc6e77f1f2fdf0ac70180a517b91f71845f1fd78ed3f"
ROLES=("STRICT","BROAD")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,"FROZEN_INPUT_SHA_"+Path(path).name)
    return json.loads(raw)

def cold(engine,world,clock,p4,mode,target=None,**extras):
    opts={"fen_clocks":clock,**extras}
    a=play(engine,world,p4,mode,target,**opts)
    b=play(engine,world,p4,mode,target,**opts)
    need(a==b,"COLD_REPEAT_"+p4+"_"+mode)
    need(a["root_events"] and len(a["root_events"])<4096,
         "SOURCE_ROOT_TRACE_MISSING_OR_CENSORED")
    need(not any(e["kind"]=="trace_censored" for e in a["payload_witnesses"]),
         "SOURCE_TT_TRACE_CENSORED")
    return a

def root_depth_ladder(events):
    buckets={}
    for evt in events:
        if evt["kind"]=="after_sort":
            buckets.setdefault(evt["depth"],[]).append(evt)
    need(all(d in buckets for d in range(1,13)),
         "NATIVE_MISSING_DEPTH_ROOT_LADDER")
    return {str(d):{"native_leader":buckets[d][-1]["first_move"],
                    "score":buckets[d][-1]["value"],
                    "retry_count":len(buckets[d]),
                    "last_trial":buckets[d][-1]["trial"]}
            for d in range(1,13)}

def first_semantic_source_split(fevents,vevents):
    """Stop alignment at first nontrivial observed difference.
    This is not a guarantee of identical hidden TT/search state.
    """
    exclude={"root_nodes","seq"}
    for i in range(min(len(fevents),len(vevents))):
        f,v=fevents[i],vevents[i]
        if f["kind"]!=v["kind"]:
            return {"index":i,"kind":"PATH_DIVERGED_EVENT_KIND",
                    "F_event_kind":f["kind"],"V_event_kind":v["kind"]}
        if f["kind"]=="candidate":
            keys=("depth","root_call","trial","move","index","alpha","beta")
            if any(f.get(k)!=v.get(k) for k in keys):
                return {"index":i,"kind":"PATH_DIVERGED_CANDIDATE_IDENTITY"}
            if f.get("child_return")!=v.get("child_return"):
                if f["index"]>1:
                    fg=int(f["child_return"]>f["alpha"])
                    vg=int(v["child_return"]>v["alpha"])
                    label=("GATE_UP" if fg==0 and vg==1
                           else "GATE_DOWN" if fg==1 and vg==0
                           else "SAME_GATE")
                else:
                    fg=vg=None
                    label="FIRST_CANDIDATE_EXCLUDED"
                return {
                    "index":i,"kind":"ALIGNED_CHILD_RETURN_DIFFERENCE",
                    "depth":f["depth"],"root_call":f["root_call"],
                    "trial":f["trial"],"move":f["move"],
                    "candidate_index":f["index"],
                    "alpha":f["alpha"],"beta":f["beta"],
                    "F_child_return":f["child_return"],
                    "V_child_return":v["child_return"],
                    "F_alpha_gate":fg,"V_alpha_gate":vg,
                    "gate_class":label,
                }
        if {k:v for k,v in f.items() if k not in exclude} != {
            k:v for k,v in vevents[i].items() if k not in exclude
        }:
            return {"index":i,"kind":"PATH_DIVERGED_OTHER_RECORDED_STATE",
                    "event_kind":f["kind"]}
    return {"index":min(len(fevents),len(vevents)),
            "kind":"TRACE_EQUAL" if len(fevents)==len(vevents)
                    else "TRACE_LENGTH_MISMATCH"}

def move_micro_comparison(fmove,vmove,atom):
    moves={m["move"]:m for m in atom["profile"]["moves"]}
    need(len(moves)==atom["profile"]["legal_root_move_count"],
         "ATOMIC_LEGAL_MOVE_DENOMINATOR")
    need(fmove in moves and vmove in moves,"BESTMOVE_NOT_SOURCE_LEGAL")
    a,b=moves[fmove],moves[vmove]
    result={"F_move":fmove,"V_move":vmove,
            "F_native":a["native_move"],"V_native":b["native_move"],
            "F_micro":{k:a[k] for k in (
                "reply_legal_move_count","reply_capture_count","reply_check_count",
                "after_root_opponent_in_check","reply_captures_destination")},
            "V_micro":{k:b[k] for k in (
                "reply_legal_move_count","reply_capture_count","reply_check_count",
                "after_root_opponent_in_check","reply_captures_destination")},
            "different_legal_reply_counts":
                a["reply_legal_move_count"] != b["reply_legal_move_count"],
            "different_attacked_edge_gains":
                a["attack_edge_added"] != b["attack_edge_added"],
            "different_attacked_edge_losses":
                a["attack_edge_removed"] != b["attack_edge_removed"],
            "different_pin_constraints":
                (a["pin_added"],a["pin_removed"])!=(b["pin_added"],b["pin_removed"]),
            "different_occupied_target_attack_balance":
                a["occupied_target_attack_balance_delta"] != b["occupied_target_attack_balance_delta"],
            "same_board_different_root_move":fmove!=vmove,
            "limit":"Board transition contrast is not proof of Stockfish use of a chess property."}
    return result

def short_arm(a):
    return {"UCI":a["UCI"],
            "root_ladder":root_depth_ladder(a["root_events"]),
            "real_reader_block_events":[e for e in a["blocks"] if e["kind"]=="reader_block"],
            "tt_actual_native_use_events":a["native_tt_value_uses"],
            "native_watched_probes":a["watched_tt_probes"],
            "TT_lineage_summary":a["lineage_summary"],
            "root_event_count":len(a["root_events"])}

def court(march,atom,engine):
    need(len(march["selected"])==len(atom["positions"])==16,
         "FULL_MARCH_16_CASES")
    result={"schema":"c3x021-P1-march16-native-TT-and-atomic-root-choice-bridge-v1",
            "scientific_design":"FROZEN_BLIND_MARCH16_EXPLORATORY_NATIVE_ROOT_DECISION",
            "frozen_source_sha256":SOURCE_SHA,"frozen_atomic_sha256":ATOMIC_SHA,
            "historical_F19_5":"FAIL_RETAINED","historical_K4":"FAIL_RETAINED",
            "roles":ROLES,"cases":[]}
    for original,atoms in zip(march["selected"],atom["positions"]):
        gid=original["id"]
        need(gid==atoms["id"] and original["source_game_sha256"]==atoms["game_sha256"],
             "CHESS_SOURCE_JOIN_IDENTITY")
        world,norm=canonical_engine_world(original)
        clock=game_clocks(original)
        row={"id":gid,"source_sha":original["source_game_sha256"],
             "clock":list(clock),"native_fen_normalization":norm,
             "source_legal_moves":atoms["profile"]["legal_root_move_count"],
             "roles":{}}
        controls={}
        for p4 in ("O","F","Z"):
            controls[p4]=cold(engine,world,clock,p4,"OBS")
        need(controls["O"]["UCI"]==controls["Z"]["UCI"],
             "COLD_SHAM_ROOT_ORDER_INTERFERENCE")
        discovery=cold(engine,world,clock,"F","OBS",discovery=True)
        need(discovery["UCI"]==controls["F"]["UCI"],
             "PASSIVE_TT_SOURCE_CHANGED_UCI")
        # Exact physical target impossible: real decoder must be a no-op.
        decoy=cold(engine,world,clock,"F","V",DECOY)
        need(decoy["UCI"]==controls["F"]["UCI"] and
             decoy["lineage_summary"]["reader_block"]==0,
             "DECOY_TT_READER_CHANGED_NATIVE_CHESS")
        row["controls"]={
            "O_UCI":controls["O"]["UCI"],
            "F":short_arm(controls["F"]),
            "Z_UCI":controls["Z"]["UCI"],
            "discovery_UCI":discovery["UCI"],
            "decoy_UCI":decoy["UCI"],
            "discovered_payload_count":len(discovery["payload_witnesses"])}
        if (len(discovery["payload_witnesses"]) >= 2048
            or any(e.get("kind")=="censored" for e in discovery["payload_witnesses"])):
            row["source_censor"]="DISCOVERY_LIMIT_OR_CENSORED"
        else:
            row["source_censor"]=None
        for role in ROLES:
            source=first_pair(discovery["payload_witnesses"],RULES[role])
            if not source:
                row["roles"][role]={"status":"NO_ELIGIBLE_PHYSICAL_PAIR"}
                continue
            physical=source["physical"]
            x=cold(engine,world,clock,"F","V",physical,
                   tt_reader_filters=mask_filters(RULES[role],source,"FIRST"))
            allowed=source["root_calls"][0]
            block=[e for e in x["blocks"] if e["kind"]=="reader_block"]
            need(all(e["root_call"]==allowed and
                     all(e[key]==physical[key] for key in ("key64","slot","epoch"))
                     for e in block),"TT_BLOCK_WRONG_SOURCE_PHYSICAL_IDENTITY")
            need(len(block)==x["lineage_summary"]["reader_block"],
                 "INCOMPLETE_TT_READER_BLOCK_LINEAGE")
            if block:
                witness=verified_reader_lineage(x)
                need(witness["all_valid"] is True
                     and witness["count"]>=len(block),"TT_WRITER_READER_RAW_STATE_INVALID")
            diff=x["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"]
            delivered=len(block)>0
            row["roles"][role]={
                "status":"ACTUAL_SOURCE_CONTACT" if delivered else "SELECTED_BUT_NONCONTACT",
                "source_physical":physical,"source_root_calls":source["root_calls"],
                "source_root_move_native":source["root_candidate_native"],
                "F_vs_V":move_micro_comparison(controls["F"]["UCI"]["bestmove"],
                                               x["UCI"]["bestmove"],atoms),
                "V":short_arm(x),"actual_reader_block_count":len(block),
                "synthetic_reader_block_delivered":delivered,
                "categorical_F_V_bestmove_changed":diff,
                "delivered_and_bestmove_changed":delivered and diff,
                "first_semantic_source_split":first_semantic_source_split(
                    controls["F"]["root_events"],x["root_events"])}
        result["cases"].append(row)
        print("C3X021_P1_MARCH_NATIVE",gid,"F",controls["F"]["UCI"]["bestmove"],
              "roles",{k:(v["status"],v.get("categorical_F_V_bestmove_changed"))
                       for k,v in row["roles"].items()},flush=True)
    result["summary"]={
        "game_denominator":len(result["cases"]),
        "role_denominator":16*len(ROLES),
        "eligible_role_arms":sum(c["roles"][role]["status"]!="NO_ELIGIBLE_PHYSICAL_PAIR"
                                 for c in result["cases"] for role in ROLES),
        "actual_treatment_role_arms":sum(
            c["roles"][role].get("synthetic_reader_block_delivered",False)
            for c in result["cases"] for role in ROLES),
        "delivered_final_root_flips":sum(
            c["roles"][role].get("delivered_and_bestmove_changed",False)
            for c in result["cases"] for role in ROLES),
        "same_board_distinct_chess_action_comparisons":sum(
            c["roles"][role].get("delivered_and_bestmove_changed",False)
            for c in result["cases"] for role in ROLES),
        "known_historical_K4":"FAIL_0_OF_4_RETAINED",
        "known_F19_5":"FAIL_RETAINED",
        "status":"NEW_MONTH_EXPLORATORY_MECHANISTIC_ASSOCIATION_NOT_A_NAMED_TACTIC_LAW"}
    return result

def main():
    p=argparse.ArgumentParser()
    for key in ("march","atomic","engine","out"):p.add_argument("--"+key,required=True)
    args=p.parse_args()
    report=court(frozen(args.march,SOURCE_SHA),frozen(args.atomic,ATOMIC_SHA),args.engine)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("C3X021_P1_NATIVE_TT_ATOMIC_DECISION_COURT",
          json.dumps(report["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
