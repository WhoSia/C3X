#!/usr/bin/env python3
"""Development-only read-only first32 native SEE calls under exact root-call ancestry.

This does not rescue strict SEE×TT 2x2 noncontact. No SEE interventions, no
TT interventions. Exports an aggregate only; raw TWIC bestmoves/keys private.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_022_P2_R2_TWIC1664_native_SEE_operator_factorial import CASES,STAGEA_SHA
from c3x_022_P2_R1_depth11_survivor_exact_forecast_stageA import SOURCE_SHA

def frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,"D1_SOURCE_SHA_DRIFT")
    return json.loads(raw)

def sample(source,stageA,engine):
    counts=Counter();matched=0;with_events=0;censored=0
    case_summary=[]
    for gid,order,role in CASES:
        raw=source["selected"][gid-1];prev=stageA["cases"][gid-1]
        need(raw["id"]==prev["id"]==gid,"D1_SOURCE_CASE_ID")
        info=prev["worlds"][order]["role_forecasts"][role]
        need(info["status"]=="FORECAST_REGISTERED_BEFORE_FIRST_TT_READER_BLOCK","D1_PAIR_NOT_FROZEN")
        w,clocks,_=native_world(raw)
        watch={"key64":info["physical"]["key64"],"root_call":info["root_calls"][0],
               "policy":"OBS","passive_ancestry":True}
        kwargs={"fen_clocks":clocks,"allow_empty_lineage":True,
                "see_watch":watch,
                "native_use_watch":{"key64":info["physical"]["key64"],"root_call":info["root_calls"][0]}}
        a=play(engine,w,order,"OBS",**kwargs)
        b=play(engine,w,order,"OBS",**kwargs)
        need(a==b,"D1_COLD_UNSTABLE")
        need(a["UCI"]==prev["worlds"][order]["baseline_UCI"],"D1_OBSERVER_CHANGED_BESTMOVE")
        need(a["lineage_summary"]["reader_block"]==0,"D1_PASSIVE_WATCH_BLOCKED_TT")
        events=a["native_see_events"]
        witness=[x for x in events if x["kind"]=="witness"]
        stops=[x for x in events if x["kind"]=="censored"]
        need(not stops or len(stops)==1,"D1_UNCONTROLLED_CENSORED_LOG")
        need(not any(x["altered"]!=0 or x["original"]!=x["delivered"]
                     for x in witness),"D1_READ_ONLY_SEE_OPERATOR_MUTATED")
        need(len(witness)<=32,"D1_LOG_CAP")
        matched+=len(witness)
        with_events+=bool(witness)
        censored+=bool(stops)
        counts.update(x["site"] for x in witness)
        case_summary.append({"game_id":gid,
                             "passive_SEE_witness_count":len(witness),
                             "truncated_first32":bool(stops),
                             "distinct_witnessed_position_keys":len({x["key64"] for x in witness}),
                             "native_watched_TT_value_use_count":len(a["native_tt_value_uses"]),
                             "source_original_baseline_stable":True})
        print("C3X022_R2_D1_PASSIVE_SEE_ANCESTRY",gid,
              "observed_SEE_calls",len(witness),"censored",bool(stops),flush=True)
    return {"schema":"c3x022-R2-D1-passive-root-descendant-native-SEE-sites-v1",
            "study":"DEVELOPMENT_ONLY_POST_STRICT_NONCONTACT_DIAGNOSTIC",
            "source_sha256":SOURCE_SHA,"stageA_sha256":STAGEA_SHA,
            "case_counts":case_summary,
            "summary":{"development_case_count":len(CASES),
                       "cases_with_any_root_descendant_SEE_witness":with_events,
                       "observed_native_SEE_events_prefix":matched,
                       "censored_first32_case_count":censored,
                       "observed_first32_native_see_sites":dict(sorted(counts.items())),
                       "SEE_return_value_interventions":0,
                       "TT_interventions":0,
                       "cannot_claim_strict_same_key_2x2_mediation":True},
            "original_chess_source_PGN":"NOT_DISTRIBUTED"}

def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    x=sample(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print("C3X022_R2_D1_OBSERVED_NATIVE_SEE_ANCESTRY_SUMMARY",
          x["summary"],hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
