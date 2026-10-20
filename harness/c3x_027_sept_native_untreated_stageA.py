#!/usr/bin/env python3
"""C3X 0.27 September16 untreated native Stockfish Stage A. NO TT/SEE intervention."""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import first_pair,RULES
SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
SCHEMA="c3x027-sept2026-untreated-native-first-TT-reader-source-v1"
def repeat(engine,world,clock,order,discovery):
 kw={"fen_clocks":clock,"allow_empty_lineage":True,"discovery":discovery}
 a=play(engine,world,order,"OBS",**kw)
 b=play(engine,world,order,"OBS",**kw)
 need(a==b,"UNSTABLE_FROZEN_BASELINE_OR_DISCOVERY")
 need(not a["blocks"],"UNTREATED_HAS_TT_ACTUATION_BLOCK")
 return a
def run(path,engine):
 raw=Path(path).read_bytes()
 need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"SEPT_SOURCE_FREEZE_SHA_DRIFT")
 source=json.loads(raw)
 need(source["phase"]=="SOURCE_ONLY_PRE_NATIVE_TREATMENT" and len(source["source_games"])==16,"SEPT_SOURCE_COUNT_DRIFT")
 rows=[]
 for row in source["source_games"]:
  b=chess.Board(row["fen4"]+" "+str(row["source_halfmove_clock"])+" "+str(row["source_fullmove_number"]))
  m=chess.Move.from_uci(row["played_legal_move_uci"])
  need(b.is_valid() and m in b.legal_moves,"INVALID_SOURCE_CHESS")
  original={**row,"native_move":m.from_square*64+m.to_square}
  world,clock,_=native_world(original)
  outcomes={}
  for order in ("O","F"):
   untreated=repeat(engine,world,clock,order,False)
   discovery=repeat(engine,world,clock,order,True)
   need(untreated["UCI"]==discovery["UCI"],"OBS_DISCOVERY_MUTATED_ROOT")
   events=[e for e in discovery["payload_witnesses"] if e["kind"]=="discovery"]
   need(len(events)<2048,"SOURCE_TRACE_CENSORED")
   pair=first_pair(events,RULES["STRICT"])
   outcomes[order]={"baseline_uci":untreated["UCI"],
       "source_contact_candidate":"FIRST_SOURCE_PAIR" if pair else "NO_ELIGIBLE_TT_FIRST_READER",
       "candidate":({"physical":pair["physical"],"root_calls":pair["root_calls"],
                     "root_candidate_native":pair["root_candidate_native"],
                     "source_indices":pair["indices"]} if pair else None),
       "discovery_event_count":len(events),
       "root_trace_count":len(untreated["root_events"])}
  rows.append({"id":row["id"],"source_game_sha256":row["source_game_sha256"],"source_fen4":row["fen4"],
        "source_halfmove_clock":row["source_halfmove_clock"],"source_fullmove_number":row["source_fullmove_number"],
        "played_legal_move_uci":row["played_legal_move_uci"],"source_root_legal_count":row["source_root_legal_count"],
        "worlds":outcomes})
  print("C3X027_SEPT_STAGEA",row["id"],[(k,v["baseline_uci"]["bestmove"],v["source_contact_candidate"]) for k,v in outcomes.items()],flush=True)
 return {"schema":SCHEMA,"status":"FROZEN_PRE_TT_SOURCE_STAGEA_NO_INTERVENTION",
         "source_sha256":SOURCE_SHA,"engine_revision":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
         "selected_order_policy":"O and F; first discovered source pair STRICT; no post-treatment choice",
         "source_games":rows,
         "summary":{"games":16,"worlds":32,"eligible_first_source_pairs":sum(v["candidate"] is not None for x in rows for v in x["worlds"].values()),"actual_TT_FIRST_blocks":0,"actual_SEE_bool_flips":0}}
if __name__=="__main__":
 a=argparse.ArgumentParser()
 for k in ("source","engine","out"):a.add_argument("--"+k,required=True)
 x=a.parse_args();result=run(x.source,x.engine);p=Path(x.out);p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print("C3X027_SEPT_STAGEA_PASS",result["summary"],hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
