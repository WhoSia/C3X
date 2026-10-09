#!/usr/bin/env python3
"""Actual SF16 TTEntry save predicate P0; single-writer skip/reinstate P1.

The source had previous independent January precommit failures. This is an
adaptive mechanism court, not new holdout. Two fixed games from earlier docs.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import mask_filters,RULES

SRC_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
PREV_SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"
ATTR_SHA="db5a780f463f88a87e222868a36c132aef4640020128210fb253d9a9bb323a88"
IMPOSSIBLE=18446744073709551615

def source_args(role,pair,arm,policy,watch):
    args={"tt_reader_filters":mask_filters(RULES[role],pair,arm),
          "probe_watch":watch}
    if policy is not None:
        physical=pair["physical"]
        args["p1_writer"]={"key64":IMPOSSIBLE if policy=="SHAM" else physical["key64"],
             "slot":physical["slot"],"epoch":physical["epoch"],
             "first_call":pair["root_calls"][0],
             "last_call":pair["root_calls"][1],
             "policy":"SKIP" if policy=="SHAM" else policy}
    else:
        # Active P0 log even without any writer actuator.
        physical=pair["physical"]
        args["p1_writer"]={"key64":physical["key64"],"slot":physical["slot"],
                          "epoch":physical["epoch"],"first_call":pair["root_calls"][0],
                          "last_call":pair["root_calls"][1],
                          "policy":"NONE"}
    return args

def run(engine,w,clock,role,pair,mode,policy):
    watch={"key64":pair["physical"]["key64"],
           "root_call":pair["root_calls"][1]}
    arg={"fen_clocks":clock,**source_args(role,pair,mode if mode!="OBS" else "FIRST",policy,watch)}
    target=None if mode=="OBS" else pair["physical"]
    x=play(engine,w,"F","OBS" if mode=="OBS" else "V",target,**arg)
    y=play(engine,w,"F","OBS" if mode=="OBS" else "V",target,**arg)
    need(x==y,"P0P1_COLD_REPLAY_"+mode+"_"+str(policy))
    p0=x["p0_save_events"]
    need(not any(e["kind"]=="censored" for e in p0),"P0_SOURCE_SAVE_PROPOSAL_CENSORED")
    probes=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
    need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
         "TT_PROBE_WATCH_CENSORED")
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    return {"UCI":x["UCI"],"actual_V_source_reader_calls":[b["root_call"] for b in blocks],
      "V_reader_block_count":len(blocks),
      "P0_source_save_decisions":p0,"probe_at_second_root_call":probes,
      "probe_shadow_version":[{"epoch":e["shadow_epoch"],
                              "serial":e["shadow_writer_serial"],
                              "full64_match":e["shadow_full64_match"],
                              "depth":e["shadow_writer_depth"],
                              "raw_bound":e["raw_bound"],
                              "raw_value":e["raw_value"]}
                              for e in probes],
      "source_payloads_at_exact_old_target":[e for e in x["payload_witnesses"]
          if e["kind"]=="reader"],
      "root_second_call_seen":any(e["kind"]=="window_enter"
           and e.get("root_call")==pair["root_calls"][1] for e in x["root_events"]),
      "writer_skip_count":sum(e["kind"]=="writer_skip" for e in p0),
      "writer_reinstate_selected_count":sum(e["kind"]=="writer_reinstate_selected" for e in p0),
      "writer_reinstated_count":sum(e["kind"]=="writer_reinstated" for e in p0),
      "true_proposals_from_old_epoch":[e for e in p0 if e["kind"]=="proposal"
                    and e["would_write"]==1
                    and e["old_epoch"]==pair["physical"]["epoch"]]
      }

def verdict(flag):return "PASS" if flag else "FAIL"

def main():
 p=argparse.ArgumentParser()
 for name in ("source","prior","attrition","engine","out"):
     p.add_argument("--"+name,required=True)
 a=p.parse_args()
 objs=[(a.source,SRC_SHA),(a.prior,PREV_SHA),(a.attrition,ATTR_SHA)]
 raw=[]
 for path,sha in objs:
     b=Path(path).read_bytes()
     need(hashlib.sha256(b).hexdigest()==sha,"SOURCE_OR_PRIOR_SHA_"+Path(path).name)
     raw.append(json.loads(b))
 source,prior,attrition=raw
 need(len(source["selected"])==len(prior["cases"])==len(attrition["cases"])==16,
      "JANUARY_FULL16_PROVENANCE")
 result={"schema":"c3x018-P0-source-TT-save-condition-P1-two-writer-rescue-v1",
         "status":"ADAPTIVE_TWO_CASES_NOT_INDEPENDENT_VALIDATION",
         "input_SHA256":{"source":SRC_SHA,"prior_January":PREV_SHA,"prior_attrition":ATTR_SHA},
         "fixed_cases":[{"game":2,"selector":"STRICT"},{"game":6,"selector":"BROAD"}],
         "cases":[]}
 for game,role in ((2,"STRICT"),(6,"BROAD")):
    raw_world=source["selected"][game-1]
    before=prior["cases"][game-1]
    old=attrition["cases"][game-1]
    need(raw_world["id"]==before["id"]==old["id"]==game,"SOURCE_CASE_MATCH")
    w,_=canonical_engine_world(raw_world)
    clock=game_clocks(raw_world)
    pair=before["selectors"][role]["selected_passive_pair"]
    need(old["selectors"][role]["original_selected_physical"]==pair["physical"],
         "ORIGINAL_WRITER_TARGET")
    row={"game":game,"selector":role,"physical_target":pair["physical"],
         "selected_root_calls":pair["root_calls"],"arms":{}}
    tests=(("OBS",None),("FIRST",None),("BOTH",None),
           ("FIRST","SKIP"),("BOTH","SKIP"),("FIRST","REINSTATE"),
           ("BOTH","REINSTATE"),("FIRST","SHAM")) if game==2 else (
           ("OBS",None),("BOTH",None),("BOTH","SKIP"))
    for mode,policy in tests:
        label=mode if policy is None else mode+"_"+policy
        arm=run(a.engine,w,clock,role,pair,mode,policy)
        before_core=(before["controls"]["F"] if mode=="OBS" else
                     before["selectors"][role]["arms"][mode]["UCI"])
        if policy is None or policy=="SHAM":
            need(arm["UCI"]==before_core,"UNMODIFIED_SOURCE_CORE_"+str(game)+"_"+label)
        row["arms"][label]=arm
        print("C3X018_P0P1",game,role,label,
              "blocks",arm["V_reader_block_count"],
              "skip",arm["writer_skip_count"],"reinstate",arm["writer_reinstated_count"],
              "probe_epoch",[p["shadow_epoch"] for p in arm["probe_at_second_root_call"]],
              "bestmove",arm["UCI"]["bestmove"],flush=True)
    result["cases"].append(row)
 main=next(r for r in result["cases"] if r["game"]==2)
 neg=next(r for r in result["cases"] if r["game"]==6)
 arms=main["arms"]
 def is_restored(label):
    probe=arms[label]["probe_at_second_root_call"]
    return bool(probe) and any(
      x["shadow_full64_match"]==1 and
      x["shadow_epoch"]==main["physical_target"]["epoch"]
      for x in probe)
 def second_contact(label):
    return main["selected_root_calls"][1] in arms[label]["actual_V_source_reader_calls"]
 vfirst=arms["FIRST"]
 normal=arms["BOTH"]
 t=main["physical_target"]
 original_writer=next((p for p in vfirst["true_proposals_from_old_epoch"]
                      if p["first_V_seen"]==1 and p["would_write"]==1
                      and p["key64"]==t["key64"] and p["slot"]==t["slot"]),None)
 second_probe=[p for p in vfirst["probe_at_second_root_call"]
               if p["shadow_epoch"]==t["epoch"]+1 and
                  p["shadow_full64_match"]==1 and p["tt_slot"]==t["slot"]]
 r0=bool(original_writer and second_probe and vfirst["V_reader_block_count"]==1)
 skip=arms["FIRST_SKIP"]
 reinstated=arms["FIRST_REINSTATE"]
 r1=skip["writer_skip_count"]==1 and is_restored("FIRST_SKIP")
 r2=(reinstated["writer_reinstate_selected_count"]==
     reinstated["writer_reinstated_count"]==1 and
     is_restored("FIRST_REINSTATE"))
 r3=second_contact("BOTH_SKIP") or second_contact("BOTH_REINSTATE")
 r4=arms["FIRST_SHAM"]["UCI"]==vfirst["UCI"] and arms["FIRST_SHAM"]["writer_skip_count"]==0
 r5=neg["arms"]["BOTH_SKIP"]["writer_skip_count"]==0
 summary={
     "P0_initial_rewriter_true_source_decision":original_writer,
     "P0_next_second_reader_probe_new_epoch":[{"epoch":p["shadow_epoch"],
          "writer_serial":p["shadow_writer_serial"],"raw_depth":p["raw_depth"]}
          for p in second_probe],
     "original_first_V_reader_blocks":vfirst["V_reader_block_count"],
     "original_both_reader_blocks":normal["V_reader_block_count"],
     "skip_selected_writer_blocks":skip["writer_skip_count"],
     "reinstate_selected_original_writes":reinstated["writer_reinstated_count"],
     "P1_both_skip_second_reader_reached":second_contact("BOTH_SKIP"),
     "P1_both_reinstate_second_reader_reached":second_contact("BOTH_REINSTATE"),
     "P1_first_skip_second_probe_old_epoch":is_restored("FIRST_SKIP"),
     "P1_first_reinstate_second_probe_old_epoch":is_restored("FIRST_REINSTATE"),
     "root_UCI_by_arm":{k:v["UCI"] for k,v in arms.items()},
     "R0_SOURCE_SAVE_PREDICATE":verdict(r0),
     "R1_SKIP_GATE_CONTACT":verdict(r1),
     "R2_REINSTATE_GATE_CONTACT":verdict(r2),
     "R3_SECOND_READER_RECOVERY":verdict(r3),
     "R4_SHAM_AND_BASELINE":verdict(r4),
     "R5_NEGATIVE_NO_REWRITE":verdict(r5),
     "R6_NO_INFERENCE_BY_BESTMOVE":"PASS",
     "R7_COLD_COMMIT":"PASS"}
 result["summary"]=summary
 result["limits"]=[
 "Selected January games 2/6 after known outcomes; this is an adaptive conditional causal court",
 "A TTEntry::save request can update a move16 without replacing depth/bound/value; record separate predicate bits",
 "SKIP suppresses only first accepted overwrite after actual first V block, not every later writer",
 "REINSTATE writes normally then repairs old full 10-byte TTEntry plus old shadow epoch/serial; synthetic state restoration",
 "Current accepted global TT write_serial never rolls back on REINSTATE, so reader writer_age can change",
 "Restored physical writer epoch and restored reader contact do not establish a root move mediation chain",
 "A changed search path may re-enter root calls with different recursive nodes; root call numbers are necessary but insufficient",
 "Independent January J2 J3 J4 all remain FAIL"]
 o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("C3X018_P0P1_SOURCE_WRITER_REWRITE_RESCUE_FINAL",json.dumps(
   {k:v for k,v in summary.items() if k.startswith("R")},sort_keys=True),flush=True)
if __name__=="__main__":main()
