#!/usr/bin/env python3
"""Adaptive physical TT case11 actual age90 reader vs earlier age18 collision.

Source SHA, old 96 treatment JSON SHA and physical target are frozen.
Force per-read event age and root-call filters; never retarget after outcome.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
 canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks

SOURCE_SHA="51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd"
PRIOR_SHA="93742e35c09f83a24aeea91f3632227165bb9208c606e3b81766e54d512a9883"
BASE={"C3X018_FILTER_MIN_WRITE_AGE":64}
EXACT={**BASE,"C3X018_FILTER_ROOT_CALL":9,
       "C3X018_FILTER_ROOT_MOVE":1431,
       "C3X018_FILTER_PLY":1,
       "C3X018_FILTER_RAW_BOUND":2}
WRONG={**EXACT,"C3X018_FILTER_ROOT_CALL":8}

def run_two(engine,w,clocks,mode,target,filters=None):
    kwargs={"fen_clocks":clocks}
    if filters is not None:kwargs["tt_reader_filters"]=filters
    x=play(engine,w,"F",mode,target,**kwargs)
    y=play(engine,w,"F",mode,target,**kwargs)
    need(x==y,"COLD_PHYSICAL_EVENT_FILTER_NONDETERMINISM")
    witness=verified_reader_lineage(x)
    need(witness["all_valid"] is not False,"SOURCE_LAST_WRITER_RAW_VALUE_MISMATCH")
    return {"UCI":x["UCI"],"source_reader_blocks":x["lineage_summary"]["reader_block"],
            "source_writer_value_witness":witness,
            "physical_reader_events":[e for e in x["payload_witnesses"] if e["kind"]=="reader"]}

def main():
 p=argparse.ArgumentParser()
 for k in ("source","prior","engine","out"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 source=Path(a.source).read_bytes()
 prior=Path(a.prior).read_bytes()
 need(hashlib.sha256(source).hexdigest()==SOURCE_SHA,"DECEMBER_SOURCE_DRIFT")
 need(hashlib.sha256(prior).hexdigest()==PRIOR_SHA,"FIRST_DECEMBER_NATIVE_RESULT_DRIFT")
 c=json.loads(source)["selected"][10]
 prev=json.loads(prior)["cases"][10]
 need(c["id"]==prev["id"]==11,"CASE11_ID")
 w,norm=canonical_engine_world(c)
 half,full=game_clocks(c);clocks=(half,full)
 old=prev["selectors"]["old"]
 other=prev["selectors"]["other_root"]
 need(old["bestmove_changed"] and other["bestmove_changed"],
      "PRIOR_CASE11_EFFECT_MISSING")
 need(old["selected_physical_target"]==other["selected_physical_target"],
      "NOT_SAME_PHYSICAL_TT_TARGET")
 sel=old["passive_source_feature"]
 other_ev=other["passive_source_feature"]
 need(sel["writer_age_writes"]==90 and
      sel["reader_root_call"]==9 and sel["reader_root_move"]==1431 and
      sel["ply"]==1 and sel["raw_bound"]==2 and
      other_ev["writer_age_writes"]==18 and other_ev["reader_root_call"]==5,
      "ORIGINAL_FIRST_LAST_READER_COLLISION_UNVERIFIED")
 t=old["selected_physical_target"]
 need(t=={"key64":16448589199907615799,"slot":0,"epoch":2},
      "SOURCE_PRESELECTED_PHYSICAL_TARGET_CHANGED")
 output={"schema":"c3x018-case11-age-conditioned-physical-TT-V-source-court-v1",
         "study_type":"ADAPTIVE_AFTER_DECEMBER_OUTPUT",
         "source_sha256":SOURCE_SHA,"prior_native_sha256":PRIOR_SHA,
         "previous_selected_reader":sel,"earlier_same_target_reader":other_ev,
         "frozen_target":t,"source_clock":clocks,"arms":{}}
 base=play(a.engine,w,"F","OBS",fen_clocks=clocks)
 base2=play(a.engine,w,"F","OBS",fen_clocks=clocks)
 need(base==base2,"ORIGINAL_BASE_NONDETERMINISTIC")
 need(base["UCI"]==prev["source_cores"]["F"],"ORIGINAL_F_CORE_DRIFT")
 output["arms"]["F"]={"UCI":base["UCI"],"source_reader_blocks":0}
 for label,filters in (("V_ALL",None),("V_AGE64",BASE),
                       ("V_EXACT_AGE90",EXACT),("V_WRONG_ROOT_CALL8",WRONG)):
    arm=run_two(a.engine,w,clocks,"V",t,filters)
    arm["bestmove_changed"]=arm["UCI"]["bestmove"]!=base["UCI"]["bestmove"]
    arm["full_UCI_changed"]=arm["UCI"]!=base["UCI"]
    output["arms"][label]=arm
    print("C3X018_CASE11_OLD_PHYSICAL_TARGET",label,
          "blocked",arm["source_reader_blocks"],
          "best",arm["UCI"]["bestmove"],
          "events",[(e.get("writer_age_writes"),e.get("reader_root_call"),
                     e.get("reader_root_move"),e.get("ply"),e.get("raw_bound"))
                    for e in arm["physical_reader_events"]],flush=True)
 need(output["arms"]["V_ALL"]["UCI"]==old["final_UCI"],
      "ORIGINAL_PHYSICAL_V_EFFECT_NOT_REPRODUCED")
 need(output["arms"]["V_ALL"]["source_reader_blocks"]>=1,
      "ORIGINAL_V_PHYSICAL_GATE_NO_CONTACT")
 wrong=output["arms"]["V_WRONG_ROOT_CALL8"]
 need(wrong["source_reader_blocks"]==0 and wrong["UCI"]==base["UCI"],
      "WRONG_ROOT_CALL_NEGATIVE_CONTROL_FIRED")
 exact=output["arms"]["V_EXACT_AGE90"]
 age=output["arms"]["V_AGE64"]
 def verdict(x):
    return "NOT_TESTED" if x["source_reader_blocks"]==0 else (
        "PASS" if not x["bestmove_changed"] else "FAIL")
 output["summary"]={
    "V_ALL_bestmove_changed":output["arms"]["V_ALL"]["bestmove_changed"],
    "V_AGE64_blocked":age["source_reader_blocks"],
    "V_AGE64_bestmove_changed":age["bestmove_changed"],
    "V_EXACT_AGE90_blocked":exact["source_reader_blocks"],
    "V_EXACT_AGE90_bestmove_changed":exact["bestmove_changed"],
    "A11_EARLIER_SCREEN":verdict(exact),
    "A11_EARLY_ONLY":verdict(age),
    "A11_SOURCE_CONTROL":"PASS",
    "A11_LOCAL_CONTACT":"PASS" if exact["source_reader_blocks"] and exact["source_writer_value_witness"]["all_valid"] else "NOT_TESTED"}
 output["limits"]=[
  "Case11 original old-category PASS was based on source target selection, not actual older reader engagement",
  "All source discovery and resulting outcome information was already observed; this is adaptive evidence only",
  "Age>=64 uses global successful TT writes since physical last writer, not wall clock",
  "C3X018 root_call matching is within-arm, physical key-slot-epoch guards prevent irrelevant node interventions",
  "All V physical selected writer/reader contacts may trigger multiple sites; root cause remains conditional on search path",
  "No natural unique TT mediation or portable chess concept relation proven"]
 dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print("C3X018_ADAPTIVE_CASE11_OLDER_ONLY_RESULT",
       json.dumps(output["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
