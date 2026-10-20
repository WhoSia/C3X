#!/usr/bin/env python3
"""Untreated Stage A of presealed Sept16 TT→SEE source experiment.
Frozen STRICT/BROAD first writer–reader selection, no V/SEE mutation.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair
from c3x_022_P2_two_stage_exact_move_scout import native_world

SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
def load(path):
 raw=Path(path).read_bytes()
 need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"SEPT16_SOURCE_SHA_CHANGED")
 d=json.loads(raw)
 need(d["phase"]=="SOURCE_ONLY_PRE_NATIVE_TREATMENT" and len(d["source_games"])==16,
      "SEPT16_SOURCE_SCOPE_INVALID")
 return d
def cold(engine,world,clocks,order,discovery=False):
 args=dict(fen_clocks=clocks,discovery=discovery,allow_empty_lineage=True)
 a=play(engine,world,order,"OBS",**args)
 b=play(engine,world,order,"OBS",**args)
 need(a==b,"SEPT_COLD_BASELINE_NONDTERMINISTIC")
 need(a["lineage_summary"]["reader_block"]==0,"SEPT_BASELINE_NOT_UNTREATED")
 return a
def run(source,engine):
 cases=[]
 for row in source["source_games"]:
  w=dict(row)
  m=chess.Move.from_uci(row["played_legal_move_uci"])
  w["native_move"]=m.from_square*64+m.to_square
  world,clocks,_=native_world(w)
  worlds={}
  for order in ("O","F"):
   b=cold(engine,world,clocks,order,False)
   d=cold(engine,world,clocks,order,True)
   need(b["UCI"]==d["UCI"],"SEPT_DISCOVERY_CHANGED_BASELINE")
   events=[x for x in d["payload_witnesses"] if x["kind"]=="discovery"]
   roles={}
   for name in ("STRICT","BROAD"):
    pair=first_pair(events,RULES[name])
    roles[name]={"status":"ELIGIBLE_FROZEN_FIRST_PAIR" if pair else "NO_ELIGIBLE_SOURCE_PAIR",
                 "physical":pair["physical"] if pair else None,
                 "root_calls":pair["root_calls"] if pair else None,
                 "root_candidate_native":pair["root_candidate_native"] if pair else None,
                 "selected_indices":pair["indices"] if pair else None}
   worlds[order]={"baseline_UCI":b["UCI"],
     "seen_discovery_events":len(events),
     "SEE_baseline_first32_total":len(b["native_see_events"]),
     "SEE_discovery_first32_total":len(d["native_see_events"]),
     "root_trace_event_count":len(b["root_events"]),
     "roles":roles}
  cases.append({"id":row["id"],"source_game_sha256":row["source_game_sha256"],
                "worlds":worlds})
  print("C3X027_STAGEA",row["id"],"O",worlds["O"]["baseline_UCI"]["bestmove"],
    "F",worlds["F"]["baseline_UCI"]["bestmove"],
    "eligible",[(o,z) for o in ("O","F") for z in ("STRICT","BROAD")
                 if worlds[o]["roles"][z]["physical"] is not None],flush=True)
 out={"schema":"c3x027-sept16-native-untreated-stageA-before-TT-first-v1",
      "source_sha256":SOURCE_SHA,"original_stockfish_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "native_TT_interventions":0,"native_SEE_Boolean_interventions":0,
      "selection":"original 0.18 STRICT/BROAD first_pair from passive discovery; no selected postoutcome",
      "cases":cases,"summary":{"distinct_game_units":len(cases),
         "root_order_cells":len(cases)*2,
         "eligible_first_pair_cells":sum(bool(r["worlds"][o]["roles"][z]["physical"])
              for r in cases for o in ("O","F") for z in ("STRICT","BROAD")),
         "baseline_root_choice_O_F_disagree_games":sum(
            r["worlds"]["O"]["baseline_UCI"]["bestmove"]!=r["worlds"]["F"]["baseline_UCI"]["bestmove"]
            for r in cases)}}
 return out
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for field in ("source","engine","out"):p.add_argument("--"+field,required=True)
 a=p.parse_args()
 result=run(load(a.source),a.engine)
 dest=Path(a.out);dest.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print("C3X027_SEPT_NATIVE_STAGEA_PASS",result["summary"],hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
