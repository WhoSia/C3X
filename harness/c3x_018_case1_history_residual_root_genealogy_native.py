#!/usr/bin/env python3
"""C3X018 case1 native recursive-root transcript: 6-field FEN vs exact PGN history.

History-only residual (#1) selected based on prior 16-world analysis: explicitly
ADAPTIVE. Lock both source and prior outputs, compare root-events and TT cutoff
ancestry but do not claim same individual recursive event across two arms.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_independent16_TT_value_transport_native import FROZEN_SOURCE_SHA,canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import HIST_BASELINE_SHA,game_clocks
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_root_call_TT_genealogy_native import summarize

def divergence(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    return {"common_prefix":n,"left_count":len(a),"right_count":len(b),
      "identical":a==b,
      "first_fen":a[n] if n<len(a) else None,
      "first_history":b[n] if n<len(b) else None}

def main():
    p=argparse.ArgumentParser()
    for k in ("source","prior-history","engine","out"):p.add_argument("--"+k,required=True)
    args=p.parse_args()
    source=Path(args.source).read_bytes()
    hist=Path(args.prior_history).read_bytes()
    need(hashlib.sha256(source).hexdigest()==FROZEN_SOURCE_SHA,"FROZEN_SOURCE_SHA")
    need(hashlib.sha256(hist).hexdigest()==HIST_BASELINE_SHA,"FROZEN_HISTORY_SHA")
    original=json.loads(source)["selected"][0]
    need(original["id"]==1,"TARGET_CASE1")
    world,normal=canonical_engine_world(original)
    half,full=game_clocks(original)
    past=json.loads(hist)["cases"][0]
    output={"schema":"c3x018-case1-full-fen-vs-history-root-aspiration-TT-cutoff-genealogy-v1",
        "study_status":"ADAPTIVE_SECONDARY_AFTER_RESIDUAL_DISCOVERY",
        "case_id":1,"source_sha256":FROZEN_SOURCE_SHA,
        "prior_history_sha256":HIST_BASELINE_SHA,
        "halfmove":half,"fullmove":full,"arms":{},"contrasts":{}}
    for mode in ("O","F","Z"):
        record={}
        for form in ("FEN6","ORIGINAL_PGN"):
            x=play(args.engine,world,mode,"OBS",
                   fen_clocks=(half,full) if form=="FEN6" else None,
                   history=form=="ORIGINAL_PGN")
            y=play(args.engine,world,mode,"OBS",
                   fen_clocks=(half,full) if form=="FEN6" else None,
                   history=form=="ORIGINAL_PGN")
            need(x==y,"COLD_REPEAT_"+mode+"_"+form)
            need(x["root_events"] and len(x["root_events"])<4096,
                 "ROOT_TRACE_CENSORED_"+mode+"_"+form)
            if form=="ORIGINAL_PGN":
                need(x["UCI"]==past["arms"][mode]["historical_UCI"],
                    "HISTORICAL_PRIOR_CORE_DRIFT")
            need(x["root_contact"]["target_contact"]==
                 ("0" if mode=="Z" else "1"),
                 "ROOT_OPERATOR_CONTACT_SHAM_"+mode)
            record[form]={"UCI":x["UCI"],
              "root_events":x["root_events"],
              "root_structure":summarize(x),
              "tt_event_summary":x["lineage_summary"]}
            print("C3X018_CASE1_HISTORY_MICRO",mode,form,
                  x["UCI"]["bestmove"],x["UCI"]["nodes"],
                  len(x["root_events"]),x["lineage_summary"]["consumer_reached"],flush=True)
        output["arms"][mode]=record
        rootfen=record["FEN6"]["root_events"]
        rootpg=record["ORIGINAL_PGN"]["root_events"]
        output["contrasts"][mode]={
          "root_event_stream":divergence(rootfen,rootpg),
          "bestmove_identical":
              record["FEN6"]["UCI"]["bestmove"]==record["ORIGINAL_PGN"]["UCI"]["bestmove"],
          "full_core_identical":record["FEN6"]["UCI"]==record["ORIGINAL_PGN"]["UCI"],
          "tt_cutoff_count_difference":
              record["ORIGINAL_PGN"]["tt_event_summary"]["consumer_reached"]-
              record["FEN6"]["tt_event_summary"]["consumer_reached"]}
    for form in ("FEN6","ORIGINAL_PGN"):
        need(output["arms"]["O"][form]["UCI"]==output["arms"]["Z"][form]["UCI"],
             "NEGATIVE_ROOT_SHAM_"+form)
    need(not output["contrasts"]["O"]["full_core_identical"] and
         not output["contrasts"]["F"]["full_core_identical"],
         "ORIGINAL_CASE1_RESIDUAL_NOT_PRESENT")
    output["limitations"]=[
        "Case1 was selected after observing residual history differences, not preregistered independent sample",
        "First mismatching root event is an observation of arithmetic search divergence, not a proven cause",
        "History vs FEN6 may differ because of internal repetition, rule50 accumulator, move stack, or other position history",
        "Full64 TT key per writer and selected main/qsearch early TT cutoff ancestry only; no exhaustive event-level search DAG",
        "Treat numeric root_call indexes after divergence as nonidentical across arms",
        "No unique natural TT mediation or cross-engine finding"]
    dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_CASE1_NATIVE_HISTORICAL_GENEALOGY_COURT_PASS",flush=True)
if __name__=="__main__":main()
