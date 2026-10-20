#!/usr/bin/env python3
"""C3X027 fresh game-disjoint source TT-FIRST arm; exact StageA precommit reverified before any intervention."""
import argparse,hashlib,json
from collections import Counter
from c3x_023_P1_same_descendant_SEE_node_matcher import identity
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold,post_source_match

SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one_sided_after_physical_TT_block(untreated,treated,physical,root_call):
    """Chronology of treated-only native SEE events relative to actual TT reader block.
    Exact source identity is retained only in private, not exported."""
    observed=Counter(identity(e) for e in untreated["native_see_events"] if e.get("kind")=="witness")
    compared=Counter(identity(e) for e in treated["native_see_events"] if e.get("kind")=="witness")
    only=compared-observed
    blocks=[]
    for ev in treated["ordered_source_operator_trace"]:
        f=ev["fields"]
        if ev["source"]=="physical_TT" and f.get("kind")=="reader_block" and
           f.get("root_call")==root_call and
           all(f.get(k)==physical[k] for k in ("key64","slot","epoch")):
            blocks.append(ev["line_ordinal"])
    if not blocks:
        return {"status":"HOLD_NO_ORDERED_TT_READER","new_seen_after_TT":None}
    first=min(blocks)
    seen=[]
    for ev in treated["ordered_source_operator_trace"]:
        f=ev["fields"]
        if ev["source"]!="native_SEE" or f.get("kind")!="witness":continue
        key=identity(f)
        if only[key]<=0:continue
        only[key]-=1
        seen.append({"site":f["site"],"boolean":f["delivered"],
                     "decision":"CONTINUE_PRUNE" if f["delivered"]==0 else "SEE_GUARD_PASSED",
                     "after_TT_reader_block":ev["line_ordinal"]>first,
                     "ordinal_delta_from_TT_block":ev["line_ordinal"]-first})
    if any(only.values()):
        return {"status":"HOLD_EVENT_ORDINAL_MATCH_INCOMPLETE","new_seen_after_TT":None}
    return {"status":"BOUNDED_ONE_SIDED_SOURCE_CHRONOLOGY",
            "new_seen_after_TT":sum(z["after_TT_reader_block"] for z in seen),
            "new_seen_before_TT":sum(not z["after_TT_reader_block"] for z in seen),
            "one_sided_guard_events":seen,
            "root_value_mediation_certified":False}

def main():
 p=argparse.ArgumentParser()
 for k in ("source","stagea","forecast","engine","out","public"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 need(digest(a.source)==SOURCE_SHA,"SOURCE_REPLACED")
 cohort=json.loads(Path(a.source).read_text())
 stage=json.loads(Path(a.stagea).read_text())
 forecast=json.loads(Path(a.forecast).read_text())
 need(forecast["status"]=="FROZEN_BEFORE_ANY_TT_SOURCE_INTERVENTION" and
      forecast["source_sha256"]==SOURCE_SHA and
      forecast["private_stageA_SHA256"]==digest(a.stagea),"STAGEA_NOT_GIT_PRESEALED")
 need(cohort["native_stockfish_treatment_runs"]==0 and len(cohort["source_games"])==16,"SOURCE_NOT_PRETREATMENT")
 cases=[];summary=[]
 for r,old,f in zip(cohort["source_games"],stage["cases"],forecast["cases"]):
  need(r["id"]==old["id"]==f["id"] and r["source_game_sha256"]==old["source_game_sha256"]==f["source_sha256"],"GAME_ID_DRIFT")
  b=chess.Board(r["fen4"]+" "+str(r["source_halfmove_clock"])+" "+str(r["source_fullmove_number"]))
  m=chess.Move.from_uci(r["played_legal_move_uci"])
  need(b.is_valid() and m in b.legal_moves,"ILLEGAL_SOURCE")
  world=dict(r);world["native_move"]=m.from_square*64+m.to_square
  world,clock,_=native_world(world)
  order="O" # fixed before treatment; one independent world per source game.
  roles=old["worlds"][order]["roles"]
  # Frozen target selector: STRICT first, else BROAD; no source pair = HOLD.
  role=next((z for z in ("STRICT","BROAD") if roles[z]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT"),None)
  if role is None:
   summary.append({"id":r["id"],"source_game_sha256":r["source_game_sha256"],"status":"HOLD_NO_FROZEN_SOURCE_PAIR",
      "original_bestmove":f["baseline_O_UCI"],"TT_block":False,"SEE_changed":"NOT_TESTED","root_changed":"NOT_TESTED"})
   continue
  target=roles[role]
  need(f["source_roles"]["O"][role]["eligible"] is True and
       f["source_roles"]["O"][role]["M0_exact_UCI"]==old["worlds"]["O"]["baseline_UCI"]["bestmove"],"TT_FIRST_TARGET_NOT_PRESEALED")
  watch={"key64":target["physical"]["key64"],"root_call":target["root_calls"][0]}
  natural=cold(a.engine,world,clock,"O","OBS",watch=watch)
  need(natural["UCI"]==old["worlds"]["O"]["baseline_UCI"],"REPLAY_BASELINE_DRIFT")
  pair={"physical":target["physical"],"root_calls":target["root_calls"],
        "root_candidate_native":target["root_candidate_native"]}
  treated=cold(a.engine,world,clock,"O","V",target["physical"],
               filter=mask_filters(RULES[role],pair,"FIRST"),watch=watch)
  blocks=[z for z in treated["blocks"] if z.get("kind")=="reader_block"]
  confirmed=bool(blocks) and all(z["root_call"]==target["root_calls"][0] and
            all(z[k]==target["physical"][k] for k in ("key64","slot","epoch")) and
            z["root_move"]==target["root_candidate_native"] for z in blocks)
  if confirmed:
   lineage=verified_reader_lineage(treated)
   need(lineage["all_valid"] and lineage["count"]>=len(blocks),"PHYSICAL_SOURCE_WRITER_LINEAGE_BAD")
   analysis=post_source_match(natural,treated,target)
  else:analysis={"status":"HOLD_NO_SOURCE_CONTACT","strict_post_source_matches":0,"source_prefix_censored":True}
  asym=one_sided_after_physical_TT_block(natural,treated,target["physical"],target["root_calls"][0]) if confirmed else {"status":"HOLD_NO_CONTACT","new_seen_after_TT":None}
  original_move=natural["UCI"]["bestmove"];treated_move=treated["UCI"]["bestmove"]
  v={"id":r["id"],"source_game_sha256":r["source_game_sha256"],
     "role":role,"TT_FIRST_contact":confirmed,"TT_reader_blocks":len(blocks),
     "baseline_UCI":natural["UCI"],"treated_UCI":treated["UCI"],
     "root_changed":treated_move!=original_move if confirmed else None,
     "expected_M0":f["source_roles"]["O"][role]["M0_exact_UCI"],
     "expected_M1":f["source_roles"]["O"][role]["M1_exact_UCI"],
     "native_SEE_original":natural["native_see_events"],"native_SEE_treated":treated["native_see_events"],
     "source_chronology":analysis,"source_asymmetric_event_chronology":asym,"SEE_bool_interventions":0,
     "root_before":source_depth_ladder(natural["root_events"]),
     "root_after":source_depth_ladder(treated["root_events"])}
  cases.append(v)
  summary.append({"id":r["id"],"source_game_sha256":r["source_game_sha256"],
      "status":analysis["status"] if confirmed else "HOLD_NO_SOURCE_CONTACT",
      "role":role,"TT_block":confirmed,
      "root_changed":v["root_changed"],
      "original_bestmove":original_move,"treated_bestmove":treated_move,
      "strict_post_TT_common_source_SEE":analysis["strict_post_source_matches"],
      "treated_only_SEE_after_TT_block":asym.get("new_seen_after_TT"),
      "treated_only_SEE_before_TT_block":asym.get("new_seen_before_TT"),
      "treated_only_SEE_guard_sites":[z["site"] for z in asym.get("one_sided_guard_events",[]) if z["after_TT_reader_block"]],
      "first32_SEE_original":len(natural["native_see_events"]),
      "first32_SEE_treated":len(treated["native_see_events"]),
      "SEE_prefix_censored":analysis.get("source_prefix_censored",False)})
  print("C3X027_SEPT_TT_SEE",r["id"],role,"contact",confirmed,"SEE_common_post",analysis["strict_post_source_matches"],
        "root",original_move,treated_move,"status",analysis["status"],flush=True)
 private={"schema":"C3X027_SEPT16_NEW_GAME_TT_FIRST_SOURCE_SEE_ROOT_NATIVE-v1","source_sha256":SOURCE_SHA,
          "stageA_sha256":digest(a.stagea),"treatment_type":"TT_FIRST_SOURCE_REAL_PHYSICAL","SEE_boolean_interventions":0,"cases":cases}
 dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(private,indent=2,sort_keys=True)+"\n")
 pub={"schema":"C3X027_SEPT16_NEW_GAME_TT_FIRST_PUBLIC_AGGREGATE-v1",
      "source_sha256":SOURCE_SHA,"private_sha256":digest(dest),"prior_forecast_sha256":digest(a.forecast),
      "new_source_games":16,"no_physical_TT_keys_or_original_full_PGN_published":True,
      "SEE_boolean_interventions":0,"results":summary,
      "summary":{"source_games":16,"eligible":len(cases),
       "contact_confirmed":sum(x["TT_block"] for x in summary),
       "root_flips":sum(x["root_changed"] is True for x in summary),
       "after_native_TT_common_SEE_positive":sum(x.get("strict_post_TT_common_source_SEE",0)>0 for x in summary),
       "censored":sum(x.get("SEE_prefix_censored") is True for x in summary),
       "full_natural_TT_SEE_root_mediation_certificates":0},
      "boundaries":["Source-contact + post-source common SEE does not prove natural mediation",
      "Observed SEE prefix limited by native watch and may be censored",
      "A root flip may arise through TT pathways without a SEE mediator",
      "No new behavioral learner study or strategic correctness trial"]}
 o=Path(a.public);o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(pub,indent=2,sort_keys=True)+"\n")
 print("C3X027_SEPT_TT_SOURCE_EXPERIMENT_PASS",pub["summary"],"public_sha",digest(o))
if __name__=="__main__":main()
