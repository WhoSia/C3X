#!/usr/bin/env python3
"""C3X S4G native same-binary TT-dose + invocation value-flow pilot.

Six arms: original, sham, zero dose, one, two, many. Five latter SAME modified
binary; source TT key frozen by original S4B SHA. Audits probe/same invocation
normal return/root candidate negamax equality and physical mask ID contacts.
This is a development pilot, NOT proof of direct TT-cell-to-root mediation.
"""
import argparse,hashlib,json,os,re
from pathlib import Path
from c3x_030_p11s4e_invocation_court import search as native_search
from c3x_030_p11s4a_native_trace_court import compare_records

SOURCE_SHA="081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300"
SCHEMA="c3x030-s4g-same-binary-TT-dose-invocation-court-v1"
ARMS=("original","sham","zero","one","two","many")
SHAM_KEY="18446744073709551615"
CAPS={"sham":10000,"zero":0,"one":1,"two":2,"many":10000}
POSITIONS=("queens_gambit_ply4","sicilian_najdorf_ply4","english_ply4")

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run_source(binary,fen,trace_key,mask_key,mask_cap):
    old_key=os.environ.get("C3X_S4G_MASK_KEY")
    old_cap=os.environ.get("C3X_S4G_MASK_LIMIT")
    os.environ["C3X_S4G_MASK_KEY"]=str(mask_key)
    os.environ["C3X_S4G_MASK_LIMIT"]=str(mask_cap)
    try:return native_search(binary,fen,trace_key)
    finally:
        if old_key is None:os.environ.pop("C3X_S4G_MASK_KEY",None)
        else:os.environ["C3X_S4G_MASK_KEY"]=old_key
        if old_cap is None:os.environ.pop("C3X_S4G_MASK_LIMIT",None)
        else:os.environ["C3X_S4G_MASK_LIMIT"]=old_cap

def native_mask_receipts(r):
    out=[]
    for line in r["other_stderr"]:
        if not line.startswith("C3X_S4G_MASK"):continue
        pairs=dict(re.findall(r"([a-z_]+)=(-?\d+)",line))
        needed={"ordinal","key","ply","id","parent","hit_before","hit_after"}
        if not needed.issubset(pairs) or pairs["ply"]!="1" or pairs["hit_before"]!="1" or pairs["hit_after"]!="0":
            raise ValueError("S4G_HOLD_BAD_ACTUAL_MASK_SOURCE_LOG")
        out.append(dict(pairs,raw=line))
    return out

def inspect_edges(events):
    probes={};returns={};mask_links=[];negamax_links=[]
    for i,x in enumerate(events):
        if x["kind"]=="probe":probes[x["id"]]=(i,x)
        if x["kind"]=="normal_return":returns[x["id"]]=(i,x)
        if x["kind"]!="root_candidate":continue
        child=x.get("child_last")
        if child not in probes or child not in returns:continue
        a,p=probes[child];b,r=returns[child]
        if not(a<b<i) or p["parent"]!=x["id"] or r["parent"]!=x["id"]:
            raise ValueError("S4G_HOLD_INVOKE_PARENT_OR_ORDER")
        if int(x["value"])!=-int(r["value"]):
            raise ValueError("S4G_HOLD_NEGAMAX_VALUE_NOT_PRESERVED")
        negamax_links.append({"child_id":child,"parent_id":x["id"],
          "child_return":int(r["value"]),"root_score":int(x["value"]),
          "probe_hit_after_mask":p["hit"],
          "root_raw_move":x["root_move_raw"]})
    return {"observed_sign_correct_links":len(negamax_links),
            "observed_links_with_source_TT_hit":sum(z["probe_hit_after_mask"]=="1" for z in negamax_links),
            "observed_links_with_masked_TT_hit":sum(z["probe_hit_after_mask"]=="0" for z in negamax_links),
            "records":negamax_links,
            "not_complete_mediation":True}

def run(previous,baseline,modified):
    if sha(previous)!=SOURCE_SHA:raise ValueError("S4G_HOLD_SHA_FROZEN_SOURCE")
    d=json.loads(Path(previous).read_bytes())
    if d.get("status")!="PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS":
        raise ValueError("S4G_HOLD_PRIOR_SOURCE_RESULT")
    if d["unmodified_original_binary_sha256"]!=sha(baseline) or sha(baseline)==sha(modified):
        raise ValueError("S4G_HOLD_WRONG_ORIGINAL_ENGINE")
    out={"schema":SCHEMA,"source_frozen_S4B_json_sha":SOURCE_SHA,
         "baseline_binary_sha":sha(baseline),"one_modified_binary_sha":sha(modified),
         "developer_sample_not_unseen_games":True,"causal_mediation_proven":False,
         "same_patched_binary_for_all_five_controls_and_treatments":True,
         "native_original_source_modified":True,"arms":list(ARMS),"positions":{}}
    for id in POSITIONS:
        data=d["positions"][id];key=data["target_original_TT_key"]
        records={"original":run_source(baseline,data["fen"],key,SHAM_KEY,0)}
        for arm in ARMS[1:]:
            k=SHAM_KEY if arm=="sham" else key
            records[arm]=run_source(modified,data["fen"],key,k,CAPS[arm])
        sham=records["sham"]
        cmp={arm:compare_records({"trials":sham["trials"]},
                 {"trials":records[arm]["trials"],"events":[]}) for arm in ARMS}
        source_masks={arm:native_mask_receipts(records[arm]) for arm in ARMS}
        for name in ("original","sham","zero"):
            if source_masks[name]:raise ValueError("S4G_HOLD_NEGATIVE_KEY_CONTACT")
        if len(source_masks["one"])!=1 or len(source_masks["two"])!=2 or len(source_masks["many"])<2:
            raise ValueError("S4G_HOLD_WRONG_NATIVE_MASK_DOSE")
        edges={arm:inspect_edges(records[arm]["events"]) for arm in ARMS}
        out["positions"][id]={
            "fen":data["fen"],"source_move_history":data["history_uci"],
            "frozen_physical_TT_key":key,
            "source_mask_receipts":source_masks,
            "native_trials":{arm:records[arm]["trials"] for arm in ARMS},
            "same_invocation_arithmetic_edges":edges,
            "sham_equal_unmodified":cmp["original"]["noninterference_pass"],
            "zero_equal_sham":cmp["zero"]["noninterference_pass"],
            "root_move_changes_vs_sham":{arm:sum(a["bestmove"]!=b["bestmove"]
                for a,b in zip(sham["trials"],records[arm]["trials"])) for arm in ARMS}}
        print("S4G_REAL_NATIVE",id,
              "root",out["positions"][id]["root_move_changes_vs_sham"],
              "edge_counts",{k:v["observed_sign_correct_links"] for k,v in edges.items()},
              "contact_counts",{k:len(v) for k,v in source_masks.items()},
              flush=True)
    out["native_searches"]=len(POSITIONS)*len(ARMS)*2
    out["native_actual_nodes"]=sum(t["nodes"] for x in out["positions"].values()
        for rows in x["native_trials"].values() for t in rows)
    out["negative_controls_equal"]=all(x["sham_equal_unmodified"] and x["zero_equal_sham"]
                                       for x in out["positions"].values())
    out["root_changes_by_arm"]={a:sum(x["root_move_changes_vs_sham"][a]
        for x in out["positions"].values()) for a in ARMS}
    out["matched_masked_source_return_root_edges_by_arm"]={a:sum(
        x["same_invocation_arithmetic_edges"][a]["observed_links_with_masked_TT_hit"]
        for x in out["positions"].values()) for a in ARMS}
    out["status"]="PASS_SOURCE_MASK_AND_VALUE_EDGE_OBSERVATION" if out["negative_controls_equal"] else "HOLD_SOURCE_LOGGER_DRIFT"
    return out

def main():
    ap=argparse.ArgumentParser()
    for key in ("prior-original","baseline","modified","out"):ap.add_argument("--"+key,required=True)
    x=vars(ap.parse_args());r=run(x["prior_original"],x["baseline"],x["modified"])
    p=Path(x["out"]);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("S4G_REAL_SAME_BIN",r["status"],"SEARCHES",r["native_searches"],
          "NODES",r["native_actual_nodes"],"ROOT_CHANGES",r["root_changes_by_arm"],
          "MASKED_ARITHMETIC_LINKS",r["matched_masked_source_return_root_edges_by_arm"],
          "SHA",sha(p),flush=True)
    if not r["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":main()
