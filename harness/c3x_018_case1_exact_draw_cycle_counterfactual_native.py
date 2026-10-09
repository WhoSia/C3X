#!/usr/bin/env python3
"""Case1 native source-specific cycle/draw counterfactual G D GD.

Source key, root call and child are fixed from the earlier observation. Never
select another key or root visit after looking at this experiment's output.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import FROZEN_SOURCE_SHA,canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks,HIST_BASELINE_SHA

PIN_FIRST={"key64":1393645049232160636,"root_call":1,"root_move":2313,"ply":1}

def first_child_event(x):
    e=x["root_events"]
    need(len(e)>22 and e[22]["seq"]==23 and e[22]["kind"]=="candidate",
         "FIRST_DIVERGENCE_SOURCE_LOCATION_DRIFT")
    need(e[22]["root_call"]==1 and e[22]["move"]==2313,
         "FIRST_DIVERGENT_CANDIDATE_CHANGED")
    return e[22]

def main():
 p=argparse.ArgumentParser()
 for k in ("cohort","prior-history","engine","out"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 src=Path(a.cohort).read_bytes();prior=Path(a.prior_history).read_bytes()
 need(hashlib.sha256(src).hexdigest()==FROZEN_SOURCE_SHA,"PRIOR_SOURCE_SHA")
 need(hashlib.sha256(prior).hexdigest()==HIST_BASELINE_SHA,"PRIOR_HISTORY_SHA")
 w,norm=canonical_engine_world(json.loads(src)["selected"][0])
 half,full=game_clocks(json.loads(src)["selected"][0])
 original=json.loads(prior)["cases"][0]
 output={"schema":"c3x018-case1-exact-root-call-key-draw-cycle-native-intervention-v1",
  "status":"ADAPTIVE_DIAGNOSTIC_SOURCE_COUNTERFACTUAL",
  "source_target":PIN_FIRST,
  "source_sample_sha256":FROZEN_SOURCE_SHA,
  "case_id":1,"arms":{},"limits":[]}
 for mode in ("O","F"):
    row={}
    for form,hist in (("FEN6",False),("HISTORY",True)):
        for gate in ("BASE","G","D","GD"):
            kwargs={"history":True} if hist else {"fen_clocks":(half,full)}
            if gate!="BASE":kwargs["draw_mode"]=gate
            x=play(a.engine,w,mode,"OBS",**kwargs)
            y=play(a.engine,w,mode,"OBS",**kwargs)
            need(x==y,f"COLD_REPLAY_{mode}_{form}_{gate}")
            need(x["root_events"] and len(x["root_events"])<4096,
                 "ROOT_TRACE_CENSORED")
            root=first_child_event(x)
            contacts=x["draw_gate_contacts"]
            if gate=="BASE":need(not contacts,"BASE_OPERATOR_FIRED")
            if not hist:need(not contacts,"FEN6_NEGATIVE_GATE_CONTACT")
            need(all(e["key64"]==PIN_FIRST["key64"] and
                         e["root_call"]==1 and e["root_move"]==2313 and e["ply"]==1
                         for e in contacts),"UNEXPECTED_INTERVENTION_SITE")
            row[form+"_"+gate]={
                "UCI":x["UCI"],
                "first_root_candidate_return":root["child_return"],
                "first_root_event":root,
                "root_event_count":len(x["root_events"]),
                "gate_contact_count":len(contacts),
                "gate_contact_sites":[e["site"] for e in contacts],
                "TT_cutoffs":x["lineage_summary"]["consumer_reached"]
            }
            print("C3X018_CASE1_EXACT_DRAW_GATE",mode,form,gate,
                  "contact",len(contacts),"child",root["child_return"],
                  "nodes",x["UCI"]["nodes"],flush=True)
        # No invariance constraint: every gate result is a possible falsifier.
    need(row["HISTORY_BASE"]["UCI"]==original["arms"][mode]["historical_UCI"],
         "HISTORICAL_SOURCE_OUTPUT_DRIFT")
    need(row["FEN6_BASE"]["first_root_candidate_return"]==68,
         "HISTORICAL_FEN_FIRST_CHILD_68_NOT_REPRODUCED")
    need(row["HISTORY_BASE"]["first_root_candidate_return"] in (-1,1),
         "HISTORICAL_PGN_FIRST_CHILD_DRAW_NOT_REPRODUCED")
    output["arms"][mode]=row
 output["limits"]=[
  "Preselected #1 based on prior measured source history residual and observed positive game cycle; no independent claim",
  "Original history C++ cycle/draw suppression is artificial and applied only at one exact search-call/key/ply location",
  "Same candidate child return after source gate would indicate local sufficiency, not uniqueness of all history pathways",
  "Draw predicate can affect root alpha/beta in several ways; restoration of final full UCI core is not guaranteed",
  "A missing D gate contact means the immediate-draw branch was never eligible at the selected node",
  "Original untouched Stockfish16 depth12 root order and no-contact controls only"]
 dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print("C3X018_CASE1_EXACT_GAME_CYCLE_SOURCE_GATE_COMPLETED",flush=True)
if __name__=="__main__":main()
