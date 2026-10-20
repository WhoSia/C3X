#!/usr/bin/env python3
"""Presealed Sept16 O/STRICT original native TT-FIRST V; passive SEE and chronology.
No SEE Boolean flip. Fail closed to HOLD on source mismatch or censored evidence.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold,post_source_match
from c3x_023_P1_R2_T1_exact_computational_SEE_comparator import temporal_common
from c3x_023_P1_same_descendant_SEE_node_matcher import candidates
SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
STAGEA_SHA="677e670b8bab6c48e194054b86d09d115f304c15c2804e1952fbe222284502cf"
def frozen(p,expected):
 raw=Path(p).read_bytes();need(hashlib.sha256(raw).hexdigest()==expected,"C3X027_PRE_V_FROZEN_SHA_DRIFT")
 return json.loads(raw)
def run(source,stage,engine):
 need(source["phase"]=="SOURCE_ONLY_PRE_NATIVE_TREATMENT" and
      stage["native_TT_interventions"]==0 and stage["native_SEE_Boolean_interventions"]==0,
      "C3X027_STAGEA_ALREADY_TREATED")
 results=[]
 for row,pre in zip(source["source_games"],stage["cases"]):
  need(row["id"]==pre["id"] and row["source_game_sha256"]==pre["source_game_sha256"],"GAME_SHA_STAGEA_MISMATCH")
  role=pre["worlds"]["O"]["roles"]["STRICT"]
  x={"id":row["id"],"source_game_sha256":row["source_game_sha256"],
     "baseline_bestmove":pre["worlds"]["O"]["baseline_UCI"]["bestmove"],
     "selection":"O_STRICT_ALL_GAMES_FIXED"}
  if role["status"]=="NO_ELIGIBLE_SOURCE_PAIR":
   x.update(status="NO_ELIGIBLE_SOURCE_PAIR_HOLD",physical_TT_contact=False,
            root_choice_changed=None,SEE_Boolean_interventions=0)
   results.append(x);print("C3X027_TT_SEE_TREATMENT",row["id"],x["status"],flush=True);continue
  need(role["status"]=="ELIGIBLE_FROZEN_FIRST_PAIR","ILLEGAL_TARGET_STATUS")
  w=dict(row);m=chess.Move.from_uci(row["played_legal_move_uci"])
  w["native_move"]=m.from_square*64+m.to_square
  world,clock,_=native_world(w)
  watch={"key64":role["physical"]["key64"],"root_call":role["root_calls"][0]}
  obs=cold(engine,world,clock,"O","OBS",watch=watch)
  need(obs["UCI"]==pre["worlds"]["O"]["baseline_UCI"],"OBS_CHANGE_FROM_FROZEN_BASELINE")
  pair={"physical":role["physical"],"root_calls":role["root_calls"],
        "root_candidate_native":role["root_candidate_native"]}
  v=cold(engine,world,clock,"O","V",role["physical"],
         filter=mask_filters(RULES["STRICT"],pair,"FIRST"),watch=watch)
  blocks=[e for e in v["blocks"] if e["kind"]=="reader_block"]
  correct=bool(blocks) and all(
     all(e[k]==role["physical"][k] for k in ("key64","slot","epoch"))
     and e["root_call"]==role["root_calls"][0]
     and e["root_move"]==role["root_candidate_native"]
     for e in blocks)
  proof=verified_reader_lineage(v)
  line_ok=bool(proof["all_valid"]) and proof["count"]>=len(blocks)
  need(correct and line_ok,"ACTUAL_PHYSICAL_TT_FIRST_CONTACT_SOURCE_CONSTRAINT_FAIL")
  match=candidates(obs["native_see_events"],v["native_see_events"],True)
  try:
   chronology=post_source_match(obs,v,role)
   temporal=temporal_common(obs,v,role)
   exact=len(temporal.get("exact_state_events",[]))
   exact_error=None
  except (ValueError,RuntimeError) as e:
   chronology={"status":"HOLD_MATCHING_COMPUTATION_ERROR"}
   temporal={"reason_census":{}}
   exact=0;exact_error=str(e)[:200]
  last_obs=obs["UCI"]["bestmove"];last_v=v["UCI"]["bestmove"]
  x.update(status="PHYSICAL_TT_FIRST_CONTACT_PASS",
     physical_TT_contact=True,TT_reader_block_count=len(blocks),
     native_writer_reader_lineage_valid=True,
     original_TT_used_event_count=len(obs["native_tt_value_uses"]),
     root_choice_changed=last_obs!=last_v,
     treated_bestmove=last_v,
     SEE_baseline_first32=len(obs["native_see_events"]),
     SEE_treated_first32=len(v["native_see_events"]),
     SEE_shared_matched=len(match["matched"]),
     SEE_original_only=len(match["untreated_only"]),
     SEE_treated_only=len(match["treated_only"]),
     SEE_observed_prefix_censored=bool(match["observed_prefix_censored"]),
     SEE_post_TT_chronological_status=chronology["status"],
     SEE_post_TT_common_count=chronology.get("strict_post_source_matches",0),
     SEE_full_state_exact_after_TT_count=exact,
     SEE_full_state_reason_counts=temporal.get("reason_census",{}),
     source_chronology_error_hold=exact_error,
     SEE_Boolean_interventions=0,
     source_SEE_guard_value_consumption="UNMEASURED_NEW_GAME_EXACT_SITE")
  results.append(x)
  print("C3X027_TT_SEE_TREATMENT",row["id"],"contact",len(blocks),
     "root_flip",x["root_choice_changed"],"see_shared",x["SEE_shared_matched"],
     "obsOnly",x["SEE_original_only"],"vOnly",x["SEE_treated_only"],
     "postTT",x["SEE_post_TT_common_count"],"stateExact",exact,flush=True)
 out={"schema":"c3x027-sept16-TT-FIRST-SEE-root-natural-activation-v1",
      "source_sha256":SOURCE_SHA,"stageA_sha256":STAGEA_SHA,
      "treatment_scope":"16 game distinct, all O STRICT, never outcome-select; no SEE mutation",
      "status":"OBSERVED_SOURCE_TT_EFFECT_NOT_NATURAL_SEE_MEDIATION_PROOF",
      "cases":results,
      "summary":{"source_distinct_games":len(results),
         "presealed_no_eligible":sum(r["status"]=="NO_ELIGIBLE_SOURCE_PAIR_HOLD" for r in results),
         "actual_physical_TT_contacts":sum(bool(r["physical_TT_contact"]) for r in results),
         "actual_root_flips":sum(r["root_choice_changed"] is True for r in results),
         "SEE_post_TT_common_matched_events":sum(r.get("SEE_post_TT_common_count",0) for r in results),
         "SEE_full_state_exact_after_TT":sum(r.get("SEE_full_state_exact_after_TT_count",0) for r in results),
         "SEE_censored_games":sum(r.get("SEE_observed_prefix_censored",False) for r in results),
         "SEE_Boolean_interventions":0,
         "natural_TT_SEE_root_mediation_proven":False,
         "source_call_consumption_at_exact_SEE_guard":"NOT_YET_TESTED"}}
 return out
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for field in ("source","stagea","engine","out"):p.add_argument("--"+field,required=True)
 a=p.parse_args()
 d=run(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
 dst=Path(a.out);dst.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
 print("C3X027_SEPT_TT_SEE_NATIVE_V_PASS",d["summary"],
        hashlib.sha256(dst.read_bytes()).hexdigest(),flush=True)
