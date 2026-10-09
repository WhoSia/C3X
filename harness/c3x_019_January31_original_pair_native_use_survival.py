#!/usr/bin/env python3
"""All January 31 preselected TT source arms: genuine native value-use survival.

No writer intervention rescue, retargeting or new source case selection.
Every source-selected V-BOTH arm is replayed cold, with independent post-native
eval assignment watch on its prior selected second root call.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SOURCE_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
NATIVE_SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"

def main():
    ap=argparse.ArgumentParser()
    for n in ("source","prior","engine","out"):ap.add_argument("--"+n,required=True)
    a=ap.parse_args()
    raw=Path(a.source).read_bytes();native=Path(a.prior).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"FROZEN_SOURCE_SHA")
    need(hashlib.sha256(native).hexdigest()==NATIVE_SHA,"FROZEN_PRIOR_JANUARY_SHA")
    originals=json.loads(raw)["selected"]
    earlier=json.loads(native)["cases"]
    need(len(originals)==len(earlier)==16,"ALL_SIXTEEN_JANUARY")
    report={"schema":"c3x019-January2026-native-TT-score-evaluation-use-survival-31-original-pair-arm-v1",
        "study":"ADAPTIVE_AFTER_JANUARY_ORIGINAL_J2_J3_J4_FAIL_AND_FIRST_C3X019_CASE2",
        "source_sha256":SOURCE_SHA,"prior_January_native_sha256":NATIVE_SHA,
        "cases":[]}
    unique=set();records=[];failed=[];types=Counter()
    for item,prev in zip(originals,earlier):
        cid=item["id"]
        need(prev["id"]==cid,"GAME_ID_MISMATCH")
        world,_=canonical_engine_world(item)
        clock=game_clocks(item)
        case={"id":cid,"selectors":{},"status":"VALID"}
        for role in ("STRICT","BROAD"):
            pred=prev["selectors"][role]
            if pred["status"]=="NO_ELIGIBLE_PAIR":
                case["selectors"][role]={"status":"NO_ELIGIBLE_PAIR"}
                continue
            pair=pred["selected_passive_pair"]
            key=pair["physical"]["key64"]
            call=pair["root_calls"][1]
            unique.add((cid,key,pair["physical"]["slot"],pair["physical"]["epoch"],
                        *pair["root_calls"]))
            kw={"fen_clocks":clock,
                "tt_reader_filters":mask_filters(RULES[role],pair,"BOTH"),
                "native_use_watch":{"key64":key,"root_call":call},
                "probe_watch":{"key64":key,"root_call":call}}
            try:
                x=play(a.engine,world,"F","V",pair["physical"],**kw)
                y=play(a.engine,world,"F","V",pair["physical"],**kw)
                need(x==y,"COLD_REPLAY_"+str(cid)+"_"+role)
                need(x["UCI"]==pred["arms"]["BOTH"]["UCI"],
                     "NATIVE_UCI_DRIFT_"+str(cid)+"_"+role)
                blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
                need(len(blocks)==pred["arms"]["BOTH"]["blocked"],
                    "ACTUAL_SOURCE_GATE_COUNT_CHANGED_"+str(cid)+"_"+role)
                need([e["root_call"] for e in blocks]==
                     [e["root_call"] for e in pred["arms"]["BOTH"]["source_block_events"]],
                     "ACTUAL_BLOCK_CALLS_CHANGED_"+str(cid)+"_"+role)
                uses=[e for e in x["native_tt_value_uses"] if e["kind"]=="used"]
                need(not any(e["kind"]=="censored" for e in x["native_tt_value_uses"]),
                     "NATIVE_USE_WATCH_CENSORED")
                need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
                     "PROBE_WATCH_CENSORED")
                probes=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
                need(all(e["key64"]==key and e["root_call"]==call and
                         e["full64_match"]==1 and e["site"] in ("main","qsearch")
                         for e in uses),
                     "POST_ASSIGNMENT_SOURCE_MATCH")
                need(all(any(p["tt_hit"]==1 and
                             p["shadow_full64_match"]==1 and
                             p["tt_slot"]==pair["physical"]["slot"]
                             for p in probes) for _ in uses),
                     "USED_WITHOUT_PHYSICAL_PROBE")
                only_first=len(blocks)==1 and blocks[0]["root_call"]==pair["root_calls"][0]
                need(only_first or len(blocks)==2,"ORIGINAL_REALIZED_PAIR_ARITY")
                if only_first:types["target_old_epoch_lost"]+=1
                else:types["both_old_epoch_gates"]+=1
                if only_first and uses:types["genuine_native_second_assignment_survived"]+=1
                if only_first and not uses:types["no_native_second_assignment"]+=1
                row={"selector":role,"status":"VALID","physical_target":pair["physical"],
                     "prior_selected_source_calls":pair["root_calls"],
                     "original_old_epoch_second_gate_lost":only_first,
                     "source_block_calls":[e["root_call"] for e in blocks],
                     "native_second_actual_use_count":len(uses),
                     "native_second_actual_uses":uses,
                     "second_root_native_probes":probes,
                     "UCI":x["UCI"]}
                case["selectors"][role]=row
                records.append((cid,role,row))
                print("C3X019_NATIVE_SECOND_USE",cid,role,
                      "old_epoch_gate_lost",only_first,
                      "native_actual_uses",len(uses),
                      "shadow_epochs",sorted({p["shadow_epoch"] for p in probes}),
                      flush=True)
            except (RuntimeError,KeyError,ValueError) as e:
                case["status"]="HOLD_FAIL_CLOSED"
                case["selectors"][role]={"selector":role,"status":"HOLD_FAIL_CLOSED",
                    "failure":type(e).__name__+":"+str(e)[:300]}
                failed.append((cid,role,str(e)[:300]))
        report["cases"].append(case)
    need([r["id"] for r in report["cases"]]==list(range(1,17)),
         "FULL_SOURCE_DENOMINATOR")
    valid=len(records)
    missing=sum(c["status"]!="VALID" for c in report["cases"])
    survivors=types["genuine_native_second_assignment_survived"]
    denom=types["target_old_epoch_lost"]
    summary={"game_count":16,"role_arms_recorded":valid,"physically_unique_source_pair_targets":len(unique),
      "original_old_writer_epoch_gate_lost":denom,
      "original_both_reader_target_gates":types["both_old_epoch_gates"],
      "true_native_second_eval_assignments_survived":survivors,
      "no_native_second_assignment_after_epoch_change":types["no_native_second_assignment"],
      "technical_holds":failed,
      "A1_NATIVE_SURVIVAL_AT_LEAST20":("PASS" if survivors>=20 else "FAIL"),
      "A2_MATCHED_NATIVE_SCORE":("PASS" if not failed else "HOLD"),
      "A3_NATURAL_SOURCE_UNCHANGED":("PASS" if not failed else "HOLD"),
      "A4_DENOMINATOR":("PASS" if valid==31 and missing==0 else "HOLD"),
      "A5_DISTINCT_PAIR_COUNTS":("PASS" if len(unique)==25 and valid==31 else "FAIL")}
    if valid!=31 or missing:
        summary["A1_NATIVE_SURVIVAL_AT_LEAST20"]="HOLD_INCOMPLETE"
    report["summary"]=summary
    report["limits"]=[
      "Post-outcome diagnostic on original sixteen January sources, not an independent sample",
      "31 role arms include overlapping STRICT and BROAD physical targets; 25 distinct game-key-slot-epoch-call sets",
      "True use means native main/qsearch assignment actually executed, not proof of contribution to final categorical bestmove",
      "C3X018 writer epoch change is real; an epoch mismatch need not extinguish native cached evaluation use",
      "All source-first caps and preregistered January J2/J3/J4 negative forecasts remain historical FAIL"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X019_ALL_JAN_SOURCE_PAIR_TRUE_TT_CONSUMPTION_RESULT",
          json.dumps(summary,sort_keys=True),flush=True)
    if failed or valid!=31:raise RuntimeError("C3X019_FAIL_CLOSED_NATIVE31")
if __name__=="__main__":main()
