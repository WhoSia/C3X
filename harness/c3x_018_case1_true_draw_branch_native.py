#!/usr/bin/env python3
"""C3X018 case1 true draw/game-cycle source predicate court.

Compare same board and exact source halfmove/fullmove C11 FEN to true PGN
history at first divergent root candidate. Fixed case1 after prior residual
discovery; descriptive not an independent preregistered causal result.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world,FROZEN_SOURCE_SHA
from c3x_018_chess_clock_factorial_original_history_native import game_clocks,HIST_BASELINE_SHA

def first_diff(a,b):
 n=0
 for x,y in zip(a,b):
  if x!=y:break
  n+=1
 return {"common_prefix":n,"first_fen":a[n] if n<len(a) else None,
         "first_game":b[n] if n<len(b) else None}

def main():
 p=argparse.ArgumentParser()
 for name in ("cohort","prior-history","engine","out"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 raw=Path(a.cohort).read_bytes();h=Path(a.prior_history).read_bytes()
 need(hashlib.sha256(raw).hexdigest()==FROZEN_SOURCE_SHA,"SOURCE_COHORT_SHA")
 need(hashlib.sha256(h).hexdigest()==HIST_BASELINE_SHA,"HISTORICAL_NATIVE_SHA")
 orig=json.loads(raw)["selected"][0]
 world,norm=canonical_engine_world(orig)
 half,full=game_clocks(orig)
 old=json.loads(h)["cases"][0]
 result={"schema":"c3x018-case1-verified-draw-branch-initial-root-divergence-v1",
   "status":"ADAPTIVE_SOURCE_MICRO_MECHANISM",
   "case":1,"frozen_original_game_sha256":orig["source_game_sha256"],
   "rule50":half,"fullmove":full,"arms":{},"contrasts":{}}
 for arm in ("O","F","Z"):
  pairs={}
  for name,history in (("FEN6",False),("ORIGINAL_HISTORY",True)):
   pkw={"history":history} if history else {"fen_clocks":(half,full)}
   x=play(a.engine,world,arm,"OBS",**pkw)
   y=play(a.engine,world,arm,"OBS",**pkw)
   need(x==y,"DRAW_LOG_NONDETERMINISTIC")
   if history:
    need(x["UCI"]==old["arms"][arm]["historical_UCI"],"ORIGINAL_HISTORY_NATIVE_DRIFT")
   need(x["root_events"] and len(x["root_events"])<4096,"ROOT_TRACE_CENSORED")
   need(x["root_contact"]["target_contact"]==("0" if arm=="Z" else "1"),
        "ROOT_CONTACT_CONTRACT")
   pairs[name]={"UCI":x["UCI"],"root_events":x["root_events"],
                "positive_draw_predicates":x["draw_probes"],
                "draw_log_count":len(x["draw_probes"]),
                "tt_cutoffs":x["lineage_summary"]["consumer_reached"]}
   print("C3X018_DRAW_BRANCH_CASE1",arm,name,
         x["UCI"]["bestmove"],len(x["draw_probes"]),
         x["lineage_summary"]["consumer_reached"],flush=True)
  result["arms"][arm]=pairs
  result["contrasts"][arm]={
    "root_first":first_diff(pairs["FEN6"]["root_events"],pairs["ORIGINAL_HISTORY"]["root_events"]),
    "draw_first":first_diff(pairs["FEN6"]["positive_draw_predicates"],
                            pairs["ORIGINAL_HISTORY"]["positive_draw_predicates"]),
    "draw_events_FEN6":pairs["FEN6"]["draw_log_count"],
    "draw_events_history":pairs["ORIGINAL_HISTORY"]["draw_log_count"]}
 for form in ("FEN6","ORIGINAL_HISTORY"):
  need(result["arms"]["O"][form]["UCI"]==result["arms"]["Z"][form]["UCI"],
       "O_Z_NEGATIVE_CONTROL")
 result["limitations"]=[
  "Observer logs only first 240 positive immediate draw/game-cycle predicates per cold search; censored beyond cap",
  "A draw predicate in the same root call does not automatically parent the specific divergent child return",
  "Source position hash and within-arm root IDs cannot pair counterfactual recursive calls after divergence",
  "Root case selected from observed residual, not newly sampled independent sample",
  "No unique natural TT writer-reader or human chess motif mediation proven"]
 dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("C3X018_CASE1_SOURCE_DRAW_BRANCH_WITNESS_NATIVE_PASS",flush=True)
if __name__=="__main__":main()
