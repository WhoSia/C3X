#!/usr/bin/env python3
"""Post-exposure source forensic: exact event sequence of Sept game14 added SEE."""
import argparse,hashlib,json,os
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_023_P1_same_descendant_SEE_node_matcher import identity
SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
STAGEA_SHA="677e670b8bab6c48e194054b86d09d115f304c15c2804e1952fbe222284502cf"
def load(path,sha):
 b=Path(path).read_bytes();need(hashlib.sha256(b).hexdigest()==sha,"SOURCE_FROZEN_SHA_FAIL")
 return json.loads(b)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for f in ("source","stagea","engine","out"):p.add_argument("--"+f,required=True)
 a=p.parse_args()
 d=load(a.source,SOURCE_SHA);sa=load(a.stagea,STAGEA_SHA)
 row=d["source_games"][13];pre=sa["cases"][13]
 need(row["id"]==pre["id"]==14,"NOT_PRESELECTED_GAME14")
 scope=pre["worlds"]["O"]["roles"]["STRICT"]
 need(scope["status"]=="ELIGIBLE_FROZEN_FIRST_PAIR","NO_SOURCE")
 w=dict(row);move=chess.Move.from_uci(row["played_legal_move_uci"])
 w["native_move"]=move.from_square*64+move.to_square
 world,clocks,_=native_world(w)
 watch={"key64":scope["physical"]["key64"],"root_call":scope["root_calls"][0]}
 os.environ['C3X027_GAME14_CAPTURE_AUDIT']='1'
 os.environ['C3X027_GAME14_ARM']='OBS'
 obs=cold(a.engine,world,clocks,"O","OBS",watch=watch)
 pair={"physical":scope["physical"],"root_calls":scope["root_calls"],"root_candidate_native":scope["root_candidate_native"]}
 os.environ['C3X027_GAME14_ARM']='V'
 v=cold(a.engine,world,clocks,"O","V",scope["physical"],
   filter=mask_filters(RULES["STRICT"],pair,"FIRST"),watch=watch)
 need(obs["UCI"]==pre["worlds"]["O"]["baseline_UCI"],"BASELINE_CHANGED")
 need(obs["UCI"]["bestmove"]=="b3a4" and v["UCI"]["bestmove"]=="f3f4",
      "UNEXPECTED_ROOT_CONTRAST")
 oids={identity(e) for e in obs["native_see_events"] if e.get("kind")=="witness"}
 active=[e for e in v["native_see_events"] if e.get("kind")=="witness" and identity(e) not in oids]
 blocks=[e for e in v["ordered_source_operator_trace"]
  if e["source"]=="physical_TT" and e["fields"].get("kind")=="reader_block"
  and e["fields"].get("key64")==scope["physical"]["key64"]
  and e["fields"].get("root_call")==scope["root_calls"][0]]
 need(len(blocks)==1,"NOT_EXACT_SINGLE_FIRST_BLOCK")
 start=blocks[0]["line_ordinal"]
 entries=[]
 for event in active:
  key=identity(event)
  seq=[line for line in v["ordered_source_operator_trace"]
    if line["source"]=="native_SEE" and line["fields"].get("kind")=="witness"
    and identity(line["fields"])==key]
  entries.append({"event":event,"source_line_ordinals":[x["line_ordinal"] for x in seq],
    "after_actual_TT_first_block":len(seq)==1 and seq[0]["line_ordinal"]>start,
    "unique_ordered_source_occurrence":len(seq)==1,
    "actual_pruning_guard_branch_observed":False})
 raw=Path('private/C3X027_GAME14_CAPTURE_GUARD_ACTUAL.txt').read_text().splitlines()
 actual=[dict(item.split('=',1) for item in line.split()) for line in raw]
 obs_branch=[v for v in actual if v['arm']=='OBS']
 treated_branch=[v for v in actual if v['arm']=='V']
 need(not obs_branch and len(treated_branch)==2,'SOURCE_ACTUAL_GUARD_NOT_UNIQUE_IN_COLD_PAIR')
 need(treated_branch[0]['decision']==treated_branch[1]['decision'],'SOURCE_BRANCH_COLD_NONDETERMINISTIC')
 report={"schema":"c3x027-sept-game14-postexposure-actual-capture-guard-branch-v1",
  "source_sha256":SOURCE_SHA,"stageA_sha256":STAGEA_SHA,
  "source_game_sha256":row["source_game_sha256"],
  "tt_first_block_line_ordinal":start,"observed_V_only_SEE_count":len(entries),
  "actual_capture_prune_branch_observation":actual,
  "actual_native_guard_decision":treated_branch[0]["decision"],
  "actual_branch_source_replay_cold_duplicate":True,
  "entries":entries,"baseline_move":"b3a4","TT_first_move":"f3f4",
  "source_causality":"TT_FIRST causes root change, no SEE mediation proved",
  "postoutcome_selected_not_prospective":True}
 Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("C3X027_G14_ACTUAL_GUARD_BRANCH",treated_branch[0]["decision"],len(treated_branch),flush=True)
 print("C3X027_SEPT_GAME14_SEE_CHRONOLOGY",len(entries),
       [(e["event"]["site"],e["after_actual_TT_first_block"],
          e["event"]["original"],e["source_line_ordinals"]) for e in entries],flush=True)
