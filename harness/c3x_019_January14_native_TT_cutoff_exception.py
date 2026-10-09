#!/usr/bin/env python3
"""Adaptive source case14: actual TT cutoff return vs eval assignment exception."""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SRC="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
PREV="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"
GAME=14
ROLE="STRICT"
KEY=9126712024987466350

def main():
 p=argparse.ArgumentParser()
 for name in ("source","prior","engine","out"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 rb=Path(a.source).read_bytes();pb=Path(a.prior).read_bytes()
 need(hashlib.sha256(rb).hexdigest()==SRC,"SOURCE_COHORT_SHA")
 need(hashlib.sha256(pb).hexdigest()==PREV,"JANUARY_ORIGINAL_COURT_SHA")
 orig=json.loads(rb)["selected"][GAME-1]
 frozen=json.loads(pb)["cases"][GAME-1]
 need(orig["id"]==frozen["id"]==GAME,"SOURCE_GAME14")
 role=frozen["selectors"][ROLE]
 pair=role["selected_passive_pair"]
 need(pair["root_calls"]==[7,8] and pair["physical"]==
      {"key64":KEY,"slot":0,"epoch":1},"SOURCE_PHYSICAL_NOT_FROZEN")
 world,_=canonical_engine_world(orig)
 clock=game_clocks(orig)
 kwargs={"fen_clocks":clock,
     "tt_reader_filters":mask_filters(RULES[ROLE],pair,"BOTH"),
     "native_use_watch":{"key64":KEY,"root_call":8},
     "probe_watch":{"key64":KEY,"root_call":8}}
 x=play(a.engine,world,"F","V",pair["physical"],**kwargs)
 y=play(a.engine,world,"F","V",pair["physical"],**kwargs)
 need(x==y,"TWO_COLD_NATIVE_ROOT_REPLAYS")
 need(x["UCI"]==role["arms"]["BOTH"]["UCI"],"PRIOR_ORIGINAL_CORE_CHANGED")
 blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
 need(len(blocks)==role["arms"]["BOTH"]["blocked"]==1
      and blocks[0]["root_call"]==7,"ORIGINAL_GATE_CONTACT_DRIFT")
 uses=[e for e in x["native_tt_value_uses"] if e["kind"]=="used"]
 cutoffs=[e for e in uses if e["site"] in ("main_cutoff","qsearch_cutoff")]
 evals=[e for e in uses if e["site"] in ("main","qsearch")]
 probes=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
 need(not any(e["kind"]=="censored" for e in x["native_tt_value_uses"]),
      "NATIVE_SOURCE_WATCH_CENSORED")
 need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
      "TT_PROBE_CENSORED")
 need(all(e["full64_match"]==1 and e["root_call"]==8
             and e["key64"]==KEY for e in uses),"ACTUAL_RETURN_NOT_SELECTED_PHYSICAL")
 need(all(e["site"] in ("main_cutoff","qsearch_cutoff","main","qsearch")
             for e in uses),"UNKNOWN_VALUE_USE_SITE")
 cutoff_gate=bool(cutoffs) and all(
       e["raw_bound"]==2 and e["raw_depth"]>=e["depth"] and
       e["effective_tt_value"]>=e["beta"]
       for e in cutoffs)
 result={"schema":"c3x019-Jan-case14-original-TT-value-as-early-cutoff-vs-eval-assignment-v1",
  "status":"ADAPTIVE_SOURCE_EXCEPTION_AFTER_ALL31_ASSIGNMENT_AUDIT",
  "source_sha256":SRC,"original_prior_sha256":PREV,
  "game_id":14,"source_selector":"STRICT",
  "original_root_calls":pair["root_calls"],
  "physical_target":pair["physical"],
  "UCI":x["UCI"],"original_first_source_V_block":blocks,
  "native_actual_eval_assignments":evals,
  "native_actual_TT_cutoff_returns":cutoffs,
  "all_native_TT_use_records":uses,
  "all_selected_second_root_TT_probes":probes,
  "summary":{
    "C14_1_MAIN_CUTOFF":"PASS" if any(e["site"]=="main_cutoff" for e in cutoffs) else "FAIL",
    "C14_2_EXPECTED_NO_EVAL_ASSIGNMENT":"PASS" if not evals else "FAIL",
    "C14_3_PRIOR_NATIVE_CORE_AND_GATE":"PASS",
    "C14_4_ACTUAL_CUTOFF_CONDITIONS":"PASS" if cutoff_gate else "FAIL",
    "C14_5_NO_GENERALIZATION":"PASS",
    "native_main_cutoff_return_count":sum(e["site"]=="main_cutoff" for e in cutoffs),
    "native_qsearch_cutoff_return_count":sum(e["site"]=="qsearch_cutoff" for e in cutoffs),
    "native_eval_assignment_count":len(evals),
    "selected_main_TT_probe_count":len(probes)},
  "limits":[
   "Native TT cutoff return is a distinct functional TT consumer from cached value-as-evaluation assignment",
   "Single selected January source diagnostic after inspecting 31-arm outcomes, not new independent holdout",
   "Earlier independent January J2 J3 J4 forecasts remain FAILED",
   "No source-level proof of unique root bestmove mediation"]}
 output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("C3X019_CASE14_ACTUAL_NATIVE_TT_CUTOFF_RESULT",
       json.dumps(result["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
