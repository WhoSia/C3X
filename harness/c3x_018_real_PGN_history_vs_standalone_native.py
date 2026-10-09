#!/usr/bin/env python3
"""Secondary historical game-state challenge after independent TT V falsification.

Replays original complete UCI prefix instead of standalone FEN. No filtering
based on changes to root move; no source selection or engine re-tuning.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,FROZEN_SOURCE_SHA)

FROZEN_EXTERNAL_NATIVE_SHA="519796b24302736da13929076453cfc5278c2402a19c9903270057eee59832eb"

def main():
 p=argparse.ArgumentParser()
 for opt in ("cohort","standalone","engine","out"):p.add_argument("--"+opt,required=True)
 a=p.parse_args()
 source_bytes=Path(a.cohort).read_bytes()
 result_bytes=Path(a.standalone).read_bytes()
 need(hashlib.sha256(source_bytes).hexdigest()==FROZEN_SOURCE_SHA,"SOURCE_COHORT_DRIFT")
 need(hashlib.sha256(result_bytes).hexdigest()==FROZEN_EXTERNAL_NATIVE_SHA,
      "STANDALONE_NATIVE_RESULT_DRIFT")
 src=json.loads(source_bytes)
 previous=json.loads(result_bytes)
 need(len(src["selected"])==len(previous["cases"])==16,"DENOMINATOR")
 court={"schema":"c3x018-secondary-16-original-UCI-history-vs-standalone-FEN-root-court-v1",
        "source_sha256":FROZEN_SOURCE_SHA,
        "standalone_experiment_sha256":FROZEN_EXTERNAL_NATIVE_SHA,
        "status":"ADAPTIVE_SECONDARY_NOT_ORIGINAL_PREREGISTRATION",
        "cases":[]}
 for original,earlier in zip(src["selected"],previous["cases"]):
    cid=original["id"]
    need(cid==earlier["id"],"SOURCE_CASE_ORDER")
    w,norm=canonical_engine_world(original)
    row={"id":cid,"game_url":original["game_url"],
         "fen_before":norm["source_fen4"],
         "fen_native":norm["engine_fen4"],
         "original_history_length":original["source_ply_before_original_move"],
         "status":"NOT_RUN","arms":{}}
    try:
      for arm in ("O","F","Z"):
       history=play(a.engine,w,arm,"OBS",history=True)
       repeat=play(a.engine,w,arm,"OBS",history=True)
       need(history==repeat,"HISTORY_NOT_REPRODUCIBLE_"+str(cid)+"_"+arm)
       old=earlier["arms"][arm]
       row["arms"][arm]={
         "historical_UCI":history["UCI"],
         "standalone_UCI":old,
         "bestmove_different":history["UCI"]["bestmove"]!=old["bestmove"],
         "full_core_different":history["UCI"]!=old,
         "tt_early_cutoff_count_historical":history["lineage_summary"]["consumer_reached"],
         "root_contact":history["root_contact"]
       }
       expected_root_contact="0" if arm=="Z" else "1"
       need(history["root_contact"]["target_contact"]==expected_root_contact,
           "ROOT_CONTACT_NEGATIVE_CONTROL_MISMATCH_"+str(cid)+"_"+arm)
      need(row["arms"]["O"]["historical_UCI"]==row["arms"]["Z"]["historical_UCI"],
           "HISTORY_NO_CONTACT_SHAM_"+str(cid))
      row["status"]="EXPERIMENTED"
      print("C3X018_HISTORICAL_GAME_STATE",cid,
            [(arm,row["arms"][arm]["historical_UCI"]["bestmove"],
              row["arms"][arm]["bestmove_different"],
              row["arms"][arm]["full_core_different"])
             for arm in ("O","F","Z")],flush=True)
    except (RuntimeError,ValueError,KeyError) as exc:
      row["status"]="HOLD_FAIL_CLOSED"
      row["failure"]=type(exc).__name__+":"+str(exc)[:240]
      print("C3X018_HISTORY_HOLD",cid,row["failure"],flush=True)
    court["cases"].append(row)
 need([c["id"] for c in court["cases"]]==list(range(1,17)),"FULL_DENOMINATOR")
 done=[c for c in court["cases"] if c["status"]=="EXPERIMENTED"]
 court["summary"]={
  "total":16,"tested":len(done),
  "hold":16-len(done),
  "history_changes_F_bestmove":sum(c["arms"]["F"]["bestmove_different"] for c in done),
  "history_changes_F_full_UCI":sum(c["arms"]["F"]["full_core_different"] for c in done),
  "history_changes_O_bestmove":sum(c["arms"]["O"]["bestmove_different"] for c in done),
  "history_changes_O_full_UCI":sum(c["arms"]["O"]["full_core_different"] for c in done),
  "history_O_F_bestmove_different":sum(
     c["arms"]["O"]["historical_UCI"]["bestmove"]!=c["arms"]["F"]["historical_UCI"]["bestmove"]
      for c in done)
 }
 court["limits"]=[
  "Exploratory secondary after inspection of standalone results",
  "Identical pieces and side to move do not imply same full game history, rule50 and repetition position keys",
  "Original game move histories are authentic from frozen Lichess 2025-10 broadcast PGN; standalone FEN search resets clocks",
  "Source root action is same original played move, but move-order intervention can have different effects under history",
  "SF16 Threads1 Hash16 NNUE off depth12, no new engine/epoch reader targeting and no natural TT unique mediation proof"
 ]
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(court,indent=2,sort_keys=True)+"\n")
 print("C3X018_REAL_GAME_HISTORY_REPLAY_SOURCE_COURT",
       json.dumps(court["summary"],sort_keys=True),flush=True)
 if court["summary"]["hold"]:raise RuntimeError("C3X018_HISTORY_HOLD_FAIL_CLOSED")
if __name__=="__main__":main()
