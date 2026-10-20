#!/usr/bin/env python3
"""Prospective September16 original native TT-FIRST physical source -> SEE frontier -> root.
Treat ALL 30 source-eligible O/F cells from SHA sealed untreated Stage A.
No SEE Boolean actuation; any unobserved source-event path is HOLD, not absence.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold,source_lines,post_source_match
from c3x_023_P1_R3_native_SEE_activation_frontier_chess_exchange_bridge import categorized
SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
STAGEA_SHA="444a03dc999a544d74587dba69b88b956c5ff827ed577363e54632b110dc6575"
def load(path,digest):
 b=Path(path).read_bytes()
 need(hashlib.sha256(b).hexdigest()==digest,"PRETREATMENT_SOURCE_STAGEA_SHA_DRIFT")
 return json.loads(b)
def check(engine,world,clock,initial,order):
 target=initial["candidate"]
 need(target is not None,"TARGET_REQUIRED")
 triple=target["physical"]
 role={"physical":triple,"root_calls":target["root_calls"],"root_candidate_native":target["root_candidate_native"]}
 watch={"key64":triple["key64"],"root_call":target["root_calls"][0]}
 obs=cold(engine,world,clock,order,"OBS",watch=watch)
 need(obs["UCI"]==initial["baseline_uci"],"PASSIVE_OBSERVER_CHANGED_NATIVE_ROOT")
 V=cold(engine,world,clock,order,"V",triple,
      filter=mask_filters(RULES["STRICT"],role,"FIRST"),watch=watch)
 blocks=[q for q in V["blocks"] if q.get("kind")=="reader_block"]
 chain=verified_reader_lineage(V)
 need(all(q["key64"]==triple["key64"] and
              q["slot"]==triple["slot"] and
              q["epoch"]==triple["epoch"] and
              q["root_call"]==watch["root_call"] for q in blocks),"WRONG_ORIGINAL_READER")
 observed_original_uses=sum(len(source_lines(obs,"TT_value_used",kind,role))
        for kind in ("used","main_cutoff","qsearch_cutoff"))
 observed_blocks=len(source_lines(V,"physical_TT","reader_block",role))
 physical_contact=bool(blocks) and observed_blocks>0 and chain["all_valid"]
 report={"status":"PHYSICAL_TT_CONTACT" if physical_contact else "HOLD_UNVERIFIED_NATIVE_TT_BLOCK",
         "source_physical_contact":physical_contact,
         "native_block_event_count":len(blocks),
         "source_chronological_block_count":observed_blocks,
         "source_original_TT_value_use_count":observed_original_uses,
         "physical_writer_reader_chain_all_valid":chain["all_valid"],
         "baseline_bestmove":obs["UCI"]["bestmove"],
         "treated_bestmove":V["UCI"]["bestmove"],
         "root_choice_changed":obs["UCI"]["bestmove"]!=V["UCI"]["bestmove"],
         "baseline_root_UCI":obs["UCI"],"treated_root_UCI":V["UCI"],
         "native_SEE_boolean_actuations":0,
         "SEE_caller_result_consumption":"NOT_OBSERVED_BY_PASSIVE_SEE_WITNESS_HOLD"}
 if observed_original_uses and observed_blocks and physical_contact:
  try:
   chronology=post_source_match(obs,V,role)
   baseline_uses=sum(len(source_lines(obs,"TT_value_used",kind,role))
        for kind in ("used","main_cutoff","qsearch_cutoff"))
   block_lines=source_lines(V,"physical_TT","reader_block",role)
   # Original 0.23 R3 categorization: FULL native state equality, not just chess FEN.
   original_lines=[]
   for k in ("used","main_cutoff","qsearch_cutoff"):
    original_lines.extend(source_lines(obs,"TT_value_used",k,role))
   first=min(x["line_ordinal"] for x in original_lines)
   second=min(x["line_ordinal"] for x in block_lines)
   frontier=categorized(obs,V,first,second)
   report["chronology"]=chronology
   report["source_SEE_frontier"]=frontier
   report["source_contract"]="PASSIVE_FROZEN_SOURCE_FRONTIER_NOT_NATURAL_MEDIATION"
  except (ValueError,KeyError,RuntimeError) as err:
   report["source_contract"]="HOLD_FRONTIER_MATCH_ERROR"
   report["frontier_error"]=str(err)[:250]
 else:
  report["source_contract"]="HOLD_TT_SOURCE_NOT_VERIFIED_FOR_SEE_FRONTIER"
 return report
def run(source,stagea,engine):
 need(len(source["source_games"])==len(stagea["source_games"])==16,"SOURCE_N_DENOM_DRIFT")
 out=[]
 for a,b in zip(source["source_games"],stagea["source_games"]):
  need(a["source_game_sha256"]==b["source_game_sha256"] and a["id"]==b["id"],
       "FROZEN_GAME_SOURCE_SELECTION_MISMATCH")
  board=chess.Board(a["fen4"]+" "+str(a["source_halfmove_clock"])+" "+str(a["source_fullmove_number"]))
  m=chess.Move.from_uci(a["played_legal_move_uci"])
  original={**a,"native_move":m.from_square*64+m.to_square}
  world,clock,_=native_world(original)
  for order in ("O","F"):
   initial=b["worlds"][order]
   entry={"game_id":a["id"],"source_game_sha256":a["source_game_sha256"],"order":order,
          "stageA_observed_source_prefix_censored":initial["source_prefix_censored"],
          "observed_pre_original_bestmove":initial["baseline_uci"]["bestmove"]}
   if initial["candidate"] is None:
    entry.update({"status":"HOLD_CENSORED_NO_FIRST_PAIR","source_physical_contact":False,"native_SEE_boolean_actuations":0})
   else:
    try:entry.update(check(engine,world,clock,initial,order))
    except (ValueError,KeyError,RuntimeError) as err:
     entry.update({"status":"HOLD_ACTUAL_SOURCE_VERIFICATION_FAILED","error":str(err)[:300],
                   "native_SEE_boolean_actuations":0})
   out.append(entry)
   print("C3X027_SEPT_TTSEE",a["id"],order,entry["status"],
       "choiceflip",entry.get("root_choice_changed"),"SEE",entry.get("source_SEE_frontier",{}).get("same_full_source_state_post_TT_both_arms_count"),flush=True)
 results={"schema":"c3x027-september16-native-physicalTT-first-see-frontier-root-v1",
          "source_SHA256":SOURCE_SHA,"untreated_StageA_SHA256":STAGEA_SHA,
          "study":"PROSPECTIVELY_FROZEN_FULL30_TREATMENT_CELLS",
          "intervention":"NATIVE_PHYSICAL_FIRST_READER_SUPPRESSION_ONLY__SEE_BOOLEAN_UNCHANGED",
          "cases":out,"summary":{
             "source_games":16,"all_O_F_cells":32,
             "preeligible_cells":sum(x["stageA_observed_source_prefix_censored"] and x["status"]!="HOLD_CENSORED_NO_FIRST_PAIR" for x in out),
             "actual_physical_contact_cells":sum(x.get("source_physical_contact",False) for x in out),
             "root_flip_cells":sum(x.get("root_choice_changed",False) for x in out),
             "noncontact_hold_cells":sum(x["status"]!="PHYSICAL_TT_CONTACT" for x in out),
             "positive_post_TT_common_SEE_cells":sum(x.get("source_SEE_frontier",{}).get("same_full_source_state_post_TT_both_arms_count",0)>0 for x in out),
             "one_sided_original_SEE_events_observed":sum(x.get("source_SEE_frontier",{}).get("original_only_post_TT_prefix_native_SEE_states",0) for x in out),
             "one_sided_treated_SEE_events_observed":sum(x.get("source_SEE_frontier",{}).get("TT_FIRST_only_post_TT_prefix_native_SEE_states",0) for x in out),
             "native_SEE_bool_actuations":0,
             "caller_pruning_branches_independently_traced":False,
             "causal_mediation_proven":False}}
 return results
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for z in ("source","stagea","engine","out"):p.add_argument("--"+z,required=True)
 a=p.parse_args()
 result=run(load(a.source,SOURCE_SHA),load(a.stagea,STAGEA_SHA),a.engine)
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print("C3X027_SEPT_NATIVE_TTSEE_ROOT_TRIAL_COMPLETE",result["summary"],hashlib.sha256(Path(a.out).read_bytes()).hexdigest(),flush=True)
