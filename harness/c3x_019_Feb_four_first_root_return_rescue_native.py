#!/usr/bin/env python3
"""Four adaptive February root-choice flips: restore one root child-return edge.

Native SF16 source patch executes between completed child search and root
candidate score update. All four cases and coordinates fixed before runs.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play, need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES, mask_filters
from c3x_019_February_semantic_root_prefix_audit import (
    first_semantic_divergence, candidate_identity, window_class
)

SOURCE_SHA = "2942b1933030227f36b669faff41f15ff234c27127dbf2403bf2e8e4f12ebdc8"
PRIOR_SHA = "2a67839faf37c19ac1749c9b88200546c04f33e2b397159435a4ab97434fee74"
ROOT_SHA = "6601dc3397ce939ce61a5bd85ec91190292e823a40230978569f5705e717d613"
FIXED = ((3,"STRICT",4,4,1,231,2,-190,-166,-1031,-967,"a1c1","e1e3"),
         (6,"STRICT",10,19,2,1291,1,94,114,103,114,"g2g4","e3d2"),
         (7,"BROAD",4,4,1,2917,3,-343,-334,-613,-642,"g8e7","e8f7"),
         (10,"STRICT",4,4,1,2910,2,103,123,-459,-892,"d8b8","b7a6"))

def config(item,mode="REPAIR",sham=False):
    gid,role,depth,root_call,trial,move,index,alpha,beta,fval,vval,fmove,vmove=item
    return {"depth":depth,"root_call":root_call,"trial":trial,
            "move":65535 if sham else move,"index":index,
            "alpha":alpha,"beta":beta,"expected":vval,
            "replacement":fval,"mode":mode}

def run(engine,world,clock,role,pair,mode,ret=None):
    options={"fen_clocks":clock}
    if ret is not None:
        options["root_return"]=ret
    target=None
    tt_mode="OBS"
    if mode!="F":
        tt_mode="V"
        target=pair["physical"]
        options["tt_reader_filters"]=mask_filters(RULES[role],pair,"FIRST")
    x=play(engine,world,"F",tt_mode,target,**options)
    y=play(engine,world,"F",tt_mode,target,**options)
    need(x==y,"COLD_REPEAT_"+mode)
    need(x["root_events"] and len(x["root_events"])<4096,
         "MISSING_OR_CENSORED_ROOT_TRACE_"+mode)
    return {"UCI":x["UCI"],
            "root_events":x["root_events"],
            "return_contacts":x["root_return_events"],
            "V_reader_block_calls":[a["root_call"] for a in x["blocks"]
                                    if a["kind"]=="reader_block"],
            "V_reader_block_events":[a for a in x["blocks"]
                                     if a["kind"]=="reader_block"],
            "p4_root_contact":x["root_contact"]}

def source_pair_assert(item,old):
    gid,role,depth,call,trial,move,index,alpha,beta,fval,vval,fmove,vmove=item
    need(old["game_id"]==gid and old["selector"]==role,
         "SOURCE_GAME_AND_ROLE_"+str(gid))
    f=old["arms"]["F"]["all_root_search_events"]
    v=old["arms"]["FIRST"]["all_root_search_events"]
    hit=first_semantic_divergence(f,v)
    need(hit is not None, "SOURCE_FIRST_DIVERGENCE_MISSING")
    _,o,t=hit
    expected={"depth":depth,"root_call":call,"trial":trial,
              "move":move,"index":index,"alpha":alpha,"beta":beta,
              "F_child":fval,"FIRST_child":vval}
    found={"depth":o["depth"],"root_call":o["root_call"],
           "trial":o["trial"],"move":o["move"],"index":o["index"],
           "alpha":o["alpha"],"beta":o["beta"],
           "F_child":o["child_return"],"FIRST_child":t["child_return"]}
    need(found==expected and candidate_identity(o)==candidate_identity(t),
         "ORIGINAL_FIRST_SEMANTIC_CANDIDATE_MISMATCH")
    return {"original":o,"first":t}

def outcome_summary(row):
    controls=row["arms"]
    o=controls["FIRST"]
    repair=controls["FIRST_REPAIR"]
    observed=controls["FIRST_OBS"]
    sham=controls["FIRST_SHAM"]
    required=row["source_candidate"]
    events=repair["return_contacts"]
    fired=(len(events)==1 and events[0]["kind"]=="repaired")
    local_changed=bool(fired and
          events[0]["child_before"]==required["first"]["child_return"] and
          events[0]["child_after"]==required["original"]["child_return"])
    expected_after=(required["original"]["after"])
    found=next((e for e in repair["root_events"]
        if e["kind"]=="candidate"
        and candidate_identity(e)==candidate_identity(required["first"])),None)
    local_after=found is not None and found["after"]==expected_after
    direct_broken=(row["game"]==6 and local_changed and local_after
           and window_class(events[0]["child_after"],94,114)=="inside_window")
    back_to_f=repair["UCI"]["bestmove"]==controls["F"]["UCI"]["bestmove"]
    return {"actual_return_site_fired":fired,
            "actual_before_after_values_equal_frozen":local_changed,
            "repaired_local_candidate_after_F":local_after,
            "original_F_candidate_after":expected_after,
            "repaired_candidate_event":found,
            "restored_original_F_bestmove":back_to_f,
            "F_bestmove":controls["F"]["UCI"]["bestmove"],
            "FIRST_bestmove":controls["FIRST"]["UCI"]["bestmove"],
            "REPAIR_bestmove":repair["UCI"]["bestmove"],
            "repaired_depth10_beta_crossing_removed":direct_broken if row["game"]==6 else None,
            "OBS_no_mutation":observed["UCI"]==o["UCI"] and len(observed["return_contacts"])==1 and observed["return_contacts"][0]["kind"]=="observed",
            "SHAM_no_contact":sham["UCI"]==o["UCI"] and not sham["return_contacts"]}

def main():
    p=argparse.ArgumentParser()
    for arg in ("source","prior","prior-root","engine","out"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    raw=[]
    for path,sha in ((a.source,SOURCE_SHA),(a.prior,PRIOR_SHA),(a.prior_root,ROOT_SHA)):
        data=Path(path).read_bytes()
        need(hashlib.sha256(data).hexdigest()==sha,"FROZEN_PRIOR_SOURCE_SHA_"+Path(path).name)
        raw.append(json.loads(data))
    games,prev,roots=raw
    need(len(games["selected"])==len(prev["cases"])==16
        and [q["game_id"] for q in roots["cases"]]==[3,6,7,10],
        "ALL_FIXED_SOURCE_DENOMINATORS")
    report={"schema":"c3x019-Feb-four-one-root-child-return-edge-restoration-v1",
            "study":"ADAPTIVE_AFTER_F19_5_FAIL",
            "preregistration":"c3x/ontology/c3x-019-P4-first-divergent-root-return-surgical-restoration-precommit.md",
            "sha256":{"source_feb16":SOURCE_SHA,"prospective_native":PRIOR_SHA,
                      "preintervention_root_trace":ROOT_SHA},
            "cases":[]}
    for item,old in zip(FIXED,roots["cases"]):
        gid,role,depth,call,trial,move,index,alpha,beta,fval,vval,fmove,vmove=item
        world,_=canonical_engine_world(games["selected"][gid-1])
        clock=game_clocks(games["selected"][gid-1])
        previous=prev["cases"][gid-1]
        selected=previous["selectors"][role]["selection"]
        source=source_pair_assert(item,old)
        need(previous["baseline"]["F"]["bestmove"]==fmove
             and previous["selectors"][role]["first"]["UCI"]["bestmove"]==vmove,
             "FROZEN_SOURCE_FIRST_OUTCOME_"+str(gid))
        row={"game":gid,"selector":role,"source_candidate":source,
             "frozen_source_event":config(item),
             "arms":{}}
        treatments=(("F","F",None),
                    ("FIRST","FIRST",None),
                    ("FIRST_OBS","FIRST",config(item,"OBS")),
                    ("FIRST_REPAIR","FIRST",config(item,"REPAIR")),
                    ("FIRST_SHAM","FIRST",config(item,"REPAIR",sham=True)))
        for label,mode,rettarget in treatments:
            arm=run(a.engine,world,clock,role,selected,mode,rettarget)
            if label=="F":
                need(arm["UCI"]==previous["baseline"]["F"],
                     "F_ORIGINAL_UCI_DRIFT_"+str(gid))
            if label in ("FIRST","FIRST_OBS","FIRST_SHAM"):
                need(arm["UCI"]==previous["selectors"][role]["first"]["UCI"],
                     "V_FIRST_ORIGINAL_UCI_DRIFT_"+str(gid))
            if label!="F":
                need(arm["V_reader_block_calls"]==
                     previous["selectors"][role]["first"]["source_actual_V_block_calls"],
                     "TT_FIRST_PHYSICAL_CONTACT_DRIFT_"+str(gid)+"_"+label)
            row["arms"][label]=arm
            print("C3X019_ONE_ROOT_RETURN",gid,label,
                  "return_contact",arm["return_contacts"],
                  "tt_V_blocks",arm["V_reader_block_calls"],
                  "bestmove",arm["UCI"]["bestmove"],flush=True)
        row["outcomes"]=outcome_summary(row)
        report["cases"].append(row)
    outcomes=[row["outcomes"] for row in report["cases"]]
    report["summary"]={
      "cases_fixed":4,
      "actual_repaired_site_contacts":sum(o["actual_return_site_fired"] for o in outcomes),
      "local_frozen_F_return_restored":sum(o["actual_before_after_values_equal_frozen"] for o in outcomes),
      "local_root_candidate_F_after_restored":sum(o["repaired_local_candidate_after_F"] for o in outcomes),
      "final_bestmove_original_F_restored":sum(o["restored_original_F_bestmove"] for o in outcomes),
      "per_case_root_bestmove":{str(row["game"]):{k:row["arms"][k]["UCI"]["bestmove"] for k in ("F","FIRST","FIRST_REPAIR")} for row in report["cases"]},
      "K1_EVENT_CONTACT":"PASS" if all(o["actual_return_site_fired"] for o in outcomes) else "FAIL",
      "K2_LOCAL_RETURN":"PASS" if all(o["actual_before_after_values_equal_frozen"] and o["repaired_local_candidate_after_F"] for o in outcomes) else "FAIL",
      "K3_BETA_GATE_TRANSPORT":"PASS" if outcomes[1]["repaired_depth10_beta_crossing_removed"] else "FAIL",
      "K4_FINAL_ROOT_RESCUE":"PASS" if any(o["restored_original_F_bestmove"] for o in outcomes) else "FAIL",
      "K5_SHAM_NONINTERFERENCE":"PASS" if all(o["OBS_no_mutation"] and o["SHAM_no_contact"] for o in outcomes) else "FAIL",
      "K6_SOURCE_COUNTERFACTUAL_IDENTITY":"PASS",
      "K7_FULL_DENOMINATOR":"PASS",
      "earlier_february_F19_5":"FAIL_RETAINED"}
    report["limits"]=[
      "Original child was searched and native TT state already updated before root repair; intervention does not roll back subtree",
      "Return-site source coordinates are part of fixed source semantic prefix, not universal chess node identities",
      "A final root rescue is synthetic sufficiency of one return-edge intervention and NOT unique TT mediation",
      "This is a post-outcome adaptive four-game case audit, not independent validation",
      "Any noncontact or negative K1-K4 results remain FAIL; no search for new targets in this cohort",
      "Prior January J2/J3/J4 and February F19.5 failures are not overwritten"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X019_FEB_ONE_SITE_ROOT_RETURN_NATIVE_VERDICT",
          json.dumps(report["summary"],sort_keys=True),flush=True)

if __name__=="__main__":
    main()
