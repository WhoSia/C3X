#!/usr/bin/env python3
"""P2-R2-D2 development-only TT FIRST x first quiet/qsearch SEE Boolean under same rootcall.

All target cases already seen under R1 and D1; no heldout claims, no
outcomes and R1 actual recorded choice changes. NEVER a new heldout test.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_022_P2_R1_depth11_survivor_exact_forecast_stageA import SOURCE_SHA

STAGEA_SHA="a84a9a2b38bacedb140724c08fc5137b98c8f0077d4754bb5f399a3c30284c35"
# Cases selected from already known R1 outcome; DEVELOPMENT ONLY.
CASES=((2,"O","STRICT"),(3,"F","STRICT"),(6,"O","STRICT"),
       (12,"O","STRICT"),(13,"F","STRICT"),(14,"O","STRICT"))
SCHEMA="c3x022-P2-R2-D2-first-eligible-descendant-SEE-pruning-x-TT-2x2-development-v1"

def frozen(path,sha):
    b=Path(path).read_bytes()
    need(hashlib.sha256(b).hexdigest()==sha,"R2_SOURCE_OR_STAGE_A_DRIFT")
    return json.loads(b)

def trial(engine,world,clocks,order,target,pair,see_mode,tt_flag,source_role):
    filt=mask_filters(RULES[source_role],pair,"FIRST") if tt_flag else None
    args={"fen_clocks":clocks,"allow_empty_lineage":True,
          "native_use_watch":{"key64":target["key64"],"root_call":pair["root_calls"][0]},
          "see_watch":{"key64":target["key64"],"root_call":pair["root_calls"][0],
                       "policy":see_mode,"passive_ancestry":True,
                       **({"descendant_prune_flip":True} if see_mode=="FLIP" else {})}}
    if filt is not None:args["tt_reader_filters"]=filt
    mode="V" if tt_flag else "OBS"
    t=target if tt_flag else None
    x=play(engine,world,order,mode,t,**args)
    y=play(engine,world,order,mode,t,**args)
    need(x==y,"R2_TWICE_COLD_REPRODUCIBILITY")
    see=x["native_see_events"]
    truncated=any(z.get("kind")=="censored" for z in see)
    contact=sum(z.get("kind") in ("witness","forced") and z.get("altered")==1
                for z in see)
    need(contact <= 1,"R2_D2_NATIVE_SEE_FIRST_SINGLETON_DOSE")
    need(all(z.get("site") in ("quiet_prune","qsearch_prune")
             for z in see if z.get("altered")==1),
         "R2_D2_SEE_WRONG_PRUNING_SITE")
    if see_mode=="OBS":
        need(contact==0,"D2_PASSIVE_OBSERVATION_ALTERED_SEE_RETURN")
    if not tt_flag:
        need(x["lineage_summary"]["reader_block"]==0,"R2_NO_TT_ARM_ACTUALLY_BLOCKED")
    else:
        blocks=[z for z in x["blocks"] if z["kind"]=="reader_block"]
        need(blocks,"R2_EXPECTED_REAL_FIRST_READER_NONCONTACT")
        need(all(z["key64"]==target["key64"] and z["slot"]==target["slot"] and
                 z["epoch"]==target["epoch"] and z["root_call"]==pair["root_calls"][0]
                 for z in blocks),"R2_WRONG_PHYSICAL_TT_EVENT")
    return {
      "TT_FIRST_reader_suppressed":tt_flag,"native_SEE_policy":see_mode,
      "UCI":x["UCI"],"native_SEE_witness_events":see,
      "SEE_callsite_count":sum(z.get("kind")=="witness" for z in see),
      "SEE_witness_first32_truncated":truncated,
      "SEE_first_Boolean_intervention_count":contact,
      "native_value_uses":x["native_tt_value_uses"],
      "physical_reader_block":x["lineage_summary"]["reader_block"],
      "root_depth_ladder":source_depth_ladder(x["root_events"]),
      "cold_pair_equal":True}

def run(src,stageA,engine):
    assert len(src["selected"])==len(stageA["cases"])==16
    out={"schema":SCHEMA,"study":"POST_D1_DEVELOPMENT_DESCENDANT_PRUNE_NOT_HELDOUT",
         "source_sha256":SOURCE_SHA,"source_stageA_sha256":STAGEA_SHA,
         "cases":[]}
    for gid,order,role in CASES:
        row=src["selected"][gid-1];old=stageA["cases"][gid-1]
        need(row["id"]==old["id"]==gid and
             row["source_game_sha256"]==old["game_sha256"],"R2_SOURCE_ID")
        forecast=old["worlds"][order]["role_forecasts"][role]
        need(forecast["status"]=="FORECAST_REGISTERED_BEFORE_FIRST_TT_READER_BLOCK","R2_SELECTED_NOT_ELIGIBLE")
        world,clocks,_=native_world(row)
        pair={"physical":forecast["physical"],"root_calls":forecast["root_calls"],
              "root_candidate_native":forecast["root_candidate_native"]}
        cells={}
        # Logical 2x2 factorial, avoid confusing "TT read" and "SEE_BOOL".
        for tt_flag in (False,True):
            for see_mode in ("OBS","FLIP"):
                key=f"T{int(tt_flag)}_S{int(see_mode=='FLIP')}"
                cells[key]=trial(engine,world,clocks,order,forecast["physical"],
                                 pair,see_mode,tt_flag,role)
        need(cells["T0_S0"]["UCI"]==old["worlds"][order]["baseline_UCI"],
             "R2_D2_PASSIVE_SEE_WATCH_CHANGED_R1_FROZEN_BASELINE")
        r={"game_id":gid,"original_order":order,"original_source_role":role,
           "source_physical":forecast["physical"],
           "scoped_key64":str(forecast["physical"]["key64"]),
           "scoped_root_call":forecast["root_calls"][0],
           "source_game_sha256":row["source_game_sha256"],
           "factorial":cells}
        out["cases"].append(r)
        print("C3X022_P2_R2_D2_NATIVE_SEE_FACTORIAL_CASE",gid,order,role,
              {k:{"SEE_call":v["SEE_callsite_count"],
                  "SEE_modified":v["SEE_first_Boolean_intervention_count"],
                  "tt_reader_contact":v["physical_reader_block"]>0}
               for k,v in cells.items()},flush=True)
    out["summary"]={"development_cases":len(CASES),
     "complete_two_by_two_case_count":len(out["cases"]),
     "factorial_arms":len(CASES)*4,
     "TT_FIRST_arms_with_reader_contact":sum(
         v["physical_reader_block"]>0 for x in out["cases"]
         for v in x["factorial"].values() if v["TT_FIRST_reader_suppressed"]),
     "SEE_OBS_arms_with_exact_scoped_call":sum(
         v["SEE_callsite_count"]>0 for x in out["cases"]
         for v in x["factorial"].values() if v["native_SEE_policy"]=="OBS"),
     "SEE_FLIP_arms_with_actual_modified_Boolean":sum(
         v["SEE_first_Boolean_intervention_count"]==1 for x in out["cases"]
         for v in x["factorial"].values() if v["native_SEE_policy"]=="FLIP"),
     "source_rights":"TWIC original PGN ZIP excluded; derived chess case output requires 0.23 release review",
     "does_not_claim_heldout_prospective_model_improvement":True}
    return out

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    d=run(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("C3X022_P2_R2_D2_ACTUAL_QUIET_PRUNE_SEE_OPERATOR_CONTACT",
          d["summary"],hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
