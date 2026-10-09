#!/usr/bin/env python3
"""Exhaustive 2^5 fixed source TT reader root-call coalition court, case11.

Each mask changes only the set of root-call guards 9..13. Original source,
physical TT key/slot/epoch and accepted-write-age>=64 are fixed. This is
adaptively generated after all five singleton and full-coalition results.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world,verified_reader_lineage
from c3x_018_chess_clock_factorial_original_history_native import game_clocks

SOURCE_SHA="51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd"
PRIOR_SINGLETON_SHA="8e1ac0f02e63a9db93564181a7dd86162a552a5cb73493d5053e41573c4cf615"
PHYSICAL={"key64":16448589199907615799,"slot":0,"epoch":2}
CALLS=tuple(range(9,14))

def allowed(mask):return [9+i for i in range(5) if mask & (1<<i)]
def proper_subset(a,b):return a!=b and (a&b)==a

def main():
 p=argparse.ArgumentParser()
 for k in ("source","prior-singletons","engine","out"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 raw=Path(a.source).read_bytes();old=Path(a.prior_singletons).read_bytes()
 need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"BLIND_DECEMBER_SOURCE_HASH")
 need(hashlib.sha256(old).hexdigest()==PRIOR_SINGLETON_SHA,"PREVIOUS_SINGLETON_PROVENANCE")
 prior=json.loads(old)
 need(prior["physical_target"]==PHYSICAL and prior["planned_calls"]==list(CALLS),
      "PREVIOUS_FIXED_FIVE_TARGETS")
 original=json.loads(raw)["selected"][10]
 need(original["id"]==11,"DECEMBER_CASE11_GAME_ID")
 w,norm=canonical_engine_world(original)
 clock=game_clocks(original)
 result={"schema":"c3x018-case11-full-32-subset-TT-evaluation-reader-coalitions-v1",
  "source_sha256":SOURCE_SHA,"prior_singletons_sha256":PRIOR_SINGLETON_SHA,
  "source_precommit":"c3x/ontology/c3x-018-adaptive-case11-exhaustive-five-TT-reader-coalition-precommit.md",
  "source_physical_target":PHYSICAL,
  "original_clock":list(clock),"source_game_id":11,
  "status":"ADAPTIVE_FIXED_SOURCE_COALITION_SEARCH",
  "root_call_universe":list(CALLS),"masks":[]}
 # Cold F baseline under EXACT SAME overlay, env sanitization mandatory.
 f=play(a.engine,w,"F","OBS",fen_clocks=clock)
 repeat=play(a.engine,w,"F","OBS",fen_clocks=clock)
 need(f==repeat and f["UCI"]==prior["F_UCI"],"SOURCE_F_BASELINE_NONIDENTICAL")
 result["F_UCI"]=f["UCI"]
 for mask in range(32):
    filters={"C3X018_FILTER_MIN_WRITE_AGE":64,
             "C3X018_FILTER_CALL_MASK_9_13":mask}
    x=play(a.engine,w,"F","V",PHYSICAL,fen_clocks=clock,tt_reader_filters=filters)
    y=play(a.engine,w,"F","V",PHYSICAL,fen_clocks=clock,tt_reader_filters=filters)
    need(x==y,"COLD_REPEAT_MASK_"+str(mask))
    blocks=[evt for evt in x["blocks"] if evt["kind"]=="reader_block"]
    need(len(blocks)==x["lineage_summary"]["reader_block"],
         "SOURCE_EVENT_COUNT_MASK_"+str(mask))
    need(all(int(evt["root_call"]) in allowed(mask) for evt in blocks),
         "ROOT_CALL_NOT_ALLOWED_BY_MASK_"+str(mask))
    if blocks:
        proof=verified_reader_lineage(x)
        need(proof["count"]>=len(blocks) and proof["all_valid"] is True,
             "PHYSICAL_SOURCE_VALUE_WITNESS_"+str(mask))
    row={"mask":mask,"source_root_calls":allowed(mask),
       "cardinality":mask.bit_count(),
       "UCI":x["UCI"],"actual_blocked_readers":len(blocks),
       "source_reader_blocks":blocks,
       "bestmove_changed":x["UCI"]["bestmove"]!=f["UCI"]["bestmove"],
       "full_core_changed":x["UCI"]!=f["UCI"]}
    result["masks"].append(row)
    print("C3X018_CASE11_5_BIT_COALITION",mask,
          row["source_root_calls"],"blocks",len(blocks),
          "bestmove",x["UCI"]["bestmove"],
          "changed",row["bestmove_changed"],flush=True)
 need([r["mask"] for r in result["masks"]]==list(range(32)),"FULL_POWERSET_MISSING")
 by={r["mask"]:r for r in result["masks"]}
 need(by[0]["actual_blocked_readers"]==0 and by[0]["UCI"]==f["UCI"],
      "MASK0_NOT_EXACT_NO_CONTACT")
 need(by[31]["UCI"]==prior["arms"]["V_AGE64"]["UCI"] and
      by[31]["actual_blocked_readers"]==prior["arms"]["V_AGE64"]["source_reader_blocks"]==5,
      "FULL_GROUP_AGE64_REPLAY_CHANGED")
 for i in range(5):
    r=by[1<<i]
    source=prior["arms"][str(9+i)]
    need(r["UCI"]==source["UCI"] and
         r["actual_blocked_readers"]==source["reader_blocks"]==1,
         "SINGLETON_PREVIOUS_NATIVE_DRIFT_"+str(i))
 successful=[r["mask"] for r in result["masks"] if r["bestmove_changed"]]
 minimum=[m for m in successful if not any(proper_subset(k,m) for k in successful)]
 violations=[{"subset":a,"superset":b}
        for a in successful for b in range(32)
        if proper_subset(a,b) and b not in successful]
 pairs=[x for x in successful if x.bit_count()==2]
 proper=[x for x in successful if x!=31]
 summary={"masks_total":32,"full_group_changed_bestmove":by[31]["bestmove_changed"],
 "singletons_with_bestmove_flip":[x for x in successful if x.bit_count()==1],
 "pair_subsets_with_bestmove_flip":pairs,
 "successful_masks":successful,
 "minimal_sufficient_masks":minimum,
 "minimum_sufficient_cardinality":min((m.bit_count() for m in successful),default=None),
 "monotonicity_violations":violations,
 "C1_PAIR_SUFFICIENCY":"PASS" if pairs else "FAIL",
 "C2_LOWER_THAN_FIVE":"PASS" if proper else "FAIL",
 "C3_FULL_GROUP_REPLAY":"PASS",
 "C4_SINGLETON_NONFLIP":"PASS",
 "C5_FULL_COURT":"PASS",
 "C6_INCLUSION_MONOTONICITY":"PASS" if not violations else "FAIL"}
 result["summary"]=summary
 result["limits"]=[
   "This exhausts root call masks on one source game, but root calls are procedural IDs and changing prior nodes can change subsequent histories",
   "A minimal successful intervention coalition in the binary root outcome does NOT identify independent simultaneous causal mediators in an invariant DAG",
   "Source all five singleton interventions and full group were known before coalition hypotheses; exploratory only",
   "Bigger masked sets can change which TT readers become eligible or writer ages; actual blocked events are preserved per arm",
   "No unique natural physical TT writer-to-root mediation or external cohort generalization"]
 dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("C3X018_FIVE_READER_POWERSET_MINIMALITY_NATIVE_RESULT",
       json.dumps(summary,sort_keys=True),flush=True)
if __name__=="__main__":main()
