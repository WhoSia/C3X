#!/usr/bin/env python3
"""C3X 0.27 September Stage A: source SHA frozen; NO TT interventions; raw private baseline, PUBLIC summary."""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder,stockfish16_encoded_move

SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
def cold(engine,world,clock,order,discovery):
 kw={"fen_clocks":clock,"allow_empty_lineage":True,"discovery":discovery}
 a=play(engine,world,order,"OBS",**kw)
 b=play(engine,world,order,"OBS",**kw)
 need(a==b,"SEPT_STAGEA_COLD_SHAM_NONDETERMINISTIC")
 need(not a.get("lineage_summary",{}).get("reader_block"),"STAGEA_OBS_MUST_NOT_SUPPRESS_TT")
 return a
def main():
 q=argparse.ArgumentParser()
 for k in ("source","engine","out","public"):q.add_argument("--"+k,required=True)
 a=q.parse_args()
 raw=Path(a.source).read_bytes()
 need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"SOURCE_FROZEN_SHA_DRIFT")
 d=json.loads(raw)
 need(d["phase"]=="SOURCE_ONLY_PRE_NATIVE_TREATMENT" and d["native_stockfish_treatment_runs"]==0,"NOT_PRETREATMENT")
 rows=d["source_games"]
 need(len(rows)==16 and len({x["source_game_sha256"] for x in rows})==16,"COHORT_DRIFT")
 complete=[];public=[]
 for idx,r in enumerate(rows):
  b=chess.Board(r["fen4"]+" "+str(r["source_halfmove_clock"])+" "+str(r["source_fullmove_number"]))
  mv=chess.Move.from_uci(r["played_legal_move_uci"])
  need(b.is_valid() and mv in b.legal_moves,"BAD_SOURCE_CHESS_STATE")
  w=dict(r);w["native_move"]=mv.from_square*64+mv.to_square
  world,clocks,_=native_world(w)
  record={"id":r["id"],"source_game_sha256":r["source_game_sha256"],"worlds":{}}
  outcomes={}
  for order in ("O","F"):
   first=cold(a.engine,world,clocks,order,False)
   passive=cold(a.engine,world,clocks,order,True)
   need(first["UCI"]==passive["UCI"],"DISCOVERY_NOT_PASSIVE")
   events=[v for v in passive["payload_witnesses"] if v.get("kind")=="discovery"]
   need(len(events)<=2048,"STAGEA_DISCOVERY_CAP_REACHED")
   roles={}
   for role in ("STRICT","BROAD"):
    pair=first_pair(events,RULES[role])
    roles[role]=({"status":"FIRST_SOURCE_PAIR_PRE_TREATMENT","physical":pair["physical"],
                  "root_calls":pair["root_calls"],"root_candidate_native":pair["root_candidate_native"],
                  "source_indices":pair["indices"]} if pair else {"status":"NO_SOURCE_PAIR_HOLD"})
   record["worlds"][order]={"baseline_UCI":first["UCI"],"root_depth_ladder":source_depth_ladder(first["root_events"]),
                            "passive_see_first32":passive["native_see_events"],
                            "roles":roles,"discovery_count":len(events)}
   outcomes[order]=first["UCI"]["bestmove"]
  record["baseline_order_distinct"]=outcomes["O"]!=outcomes["F"]
  complete.append(record)
  public.append({"id":r["id"],"source_sha256":r["source_game_sha256"],
      "baseline_O_UCI":outcomes["O"],"baseline_F_UCI":outcomes["F"],
      "O_F_diverge":record["baseline_order_distinct"],
      "source_roles":{o:{role:{"eligible":record["worlds"][o]["roles"][role]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT",
      "M0_exact_UCI":outcomes[o] if record["worlds"][o]["roles"][role]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT" else None,
      "M1_exact_UCI":outcomes["F" if o=="O" else "O"] if record["worlds"][o]["roles"][role]["status"]=="FIRST_SOURCE_PAIR_PRE_TREATMENT" else None}
      for role in ("STRICT","BROAD")} for o in ("O","F")}})
  print("C3X027_SEPT_STAGEA_SOURCE",r["id"],"O",outcomes["O"],"F",outcomes["F"],
        "eligible",sum(x["eligible"] for o in public[-1]["source_roles"].values() for x in o.values()),flush=True)
 out={"schema":"c3x027-sept16-original-stockfish-pre-treatment-stageA-v1",
      "source_sha256":SOURCE_SHA,"native_TT_source_interventions":0,"SEE_bool_flips":0,
      "original_game_count":16,"cases":complete,
      "summary":{"distinct_root_games":sum(r["baseline_order_distinct"] for r in complete),
      "eligible_role_cells":sum(x["eligible"] for p in public for o in p["source_roles"].values() for x in o.values())}}
 p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
 pub={"schema":"c3x027-sept16-exact-root-and-TT-source-forecast-before-intervention",
      "status":"FROZEN_BEFORE_ANY_TT_SOURCE_INTERVENTION",
      "source_sha256":SOURCE_SHA,"private_stageA_SHA256":hashlib.sha256(p.read_bytes()).hexdigest(),
      "source_game_count":16,"source_only":True,"actual_TT_suppressions":0,"actual_SEE_flips":0,
      "cases":public,"summary":out["summary"],
      "no_original_PGN_player_data":True,"no_original_TT_key_raw":True}
 z=Path(a.public);z.parent.mkdir(parents=True,exist_ok=True);z.write_text(json.dumps(pub,sort_keys=True,indent=2)+"\n")
 print("C3X027_SEPT_STAGEA_PASS",out["summary"],"private_sha",pub["private_stageA_SHA256"],"public_sha",hashlib.sha256(z.read_bytes()).hexdigest())
if __name__=="__main__":main()
