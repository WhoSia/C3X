#!/usr/bin/env python3
"""Adaptive full-31 January joint TT reader disappearance: true probe and epoch.

This never changes the PREVIOUS 16-game preregistered native outcomes.
Read-only TT probe/shadow writer witness, 31 role-arm denominator retained.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SOURCE_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
PRIOR_SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"

def categorise(probes,original,observed_blocks):
    if observed_blocks==2:return "DUAL_READER_ACTUAL_CONTACT"
    if observed_blocks!=1:return "OTHER_COMPLEX_MULTIPROBE"
    if not probes:return "NO_TT_KEY_PROBE"
    if not any(p["tt_hit"]==1 for p in probes):return "TT_KEY_PROBE_ONLY_MISS"
    hits=[p for p in probes if p["tt_hit"]==1]
    match=[p for p in hits if
            p["shadow_full64_match"]==1 and
            p["tt_slot"]==original["slot"] and
            p["shadow_writer_key64"]==original["key64"]]
    if not match:return "KEY16_HIT_WRONG_FULL64_SHADOW"
    if any(p["shadow_epoch"]==original["epoch"] for p in match):
        return "SAME_CARRIER_BUT_EVAL_CONSUMER_INELIGIBLE"
    if any(p["shadow_epoch"]!=original["epoch"] for p in match):
        return "SAME_KEY_DIFFERENT_PHYSICAL_EPOCH"
    return "OTHER_COMPLEX_MULTIPROBE"

def main():
    p=argparse.ArgumentParser()
    for k in ("source","prior","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    src=Path(a.source).read_bytes();old=Path(a.prior).read_bytes()
    need(hashlib.sha256(src).hexdigest()==SOURCE_SHA,"SOURCE_SHA")
    need(hashlib.sha256(old).hexdigest()==PRIOR_SHA,"JANUARY_PREREG_NATIVE_SHA")
    source=json.loads(src)["selected"]
    before=json.loads(old)["cases"]
    need(len(source)==len(before)==16,"FULL_16_SOURCE")
    report={"schema":"c3x018-Jan2026-31-source-pair-TT-shadow-writer-epoch-attrition-taxonomy-v1",
        "study":"POST_OUTCOME_16_SOURCE_ROLE_ARM_MECHANISM_DIAGNOSTIC",
        "source_sha256":SOURCE_SHA,"original_native_sha256":PRIOR_SHA,
        "original_independent_J2_J3_J4":"FAIL_RETAINED",
        "prespecified_role_selectors":["STRICT","BROAD"],
        "cases":[]}
    tally=Counter();valid=0
    for source_case,prior in zip(source,before):
        cid=source_case["id"]
        need(prior["id"]==cid,"CASE_ALIGNMENT")
        world,norm=canonical_engine_world(source_case)
        clocks=game_clocks(source_case)
        case={"id":cid,"status":"NOT_STARTED","selectors":{}}
        try:
            for role in ("STRICT","BROAD"):
                b=prior["selectors"][role]
                if b["status"]=="NO_ELIGIBLE_PAIR":
                    case["selectors"][role]={"status":"NO_ELIGIBLE_PAIR"}
                    continue
                pair=b["selected_passive_pair"]
                watch={"key64":pair["physical"]["key64"],
                       "root_call":pair["root_calls"][1]}
                arms={}
                for mode in ("BASE","BOTH"):
                    extra={"fen_clocks":clocks,"probe_watch":watch}
                    if mode=="BOTH":
                        extra["tt_reader_filters"]=mask_filters(RULES[role],pair,"BOTH")
                    target=None if mode=="BASE" else pair["physical"]
                    lineage="OBS" if mode=="BASE" else "V"
                    x=play(a.engine,world,"F",lineage,target,**extra)
                    y=play(a.engine,world,"F",lineage,target,**extra)
                    need(x==y,f"COLD_PROBE_{cid}_{role}_{mode}")
                    old_uci=(prior["controls"]["F"] if mode=="BASE"
                             else b["arms"]["BOTH"]["UCI"])
                    need(x["UCI"]==old_uci,
                         f"PROBE_WATCH_CHANGED_GAME_{cid}_{role}_{mode}")
                    probes=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
                    need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
                         "PROBE_CENSORED")
                    need(all(p["key64"]==watch["key64"] and
                             p["root_call"]==watch["root_call"] for p in probes),
                         "SOURCE_TT_PROBE_WATCH_UNEXPECTED_SITE")
                    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
                    expected=0 if mode=="BASE" else b["arms"]["BOTH"]["blocked"]
                    need(len(blocks)==expected,
                         "CHANGED_ORIGINAL_ACTUAL_READER_BLOCK_COUNT")
                    arms[mode]={"source_tt_probes":probes,"source_tt_probe_count":len(probes),
                        "source_tt_hit_count":sum(e["tt_hit"]==1 for e in probes),
                        "actual_value_reader_block_count":len(blocks),
                        "actual_value_reader_blocks":blocks,
                        "UCI":x["UCI"],
                        "root_call_window_entered":any(e["kind"]=="window_enter" and
                          e["root_call"]==watch["root_call"] for e in x["root_events"])}
                category=categorise(arms["BOTH"]["source_tt_probes"],
                                    pair["physical"],
                                    arms["BOTH"]["actual_value_reader_block_count"])
                tally[role+"_"+category]+=1
                valid+=1
                case["selectors"][role]={"status":"VALID","classification":category,
                    "original_selected_physical":pair["physical"],
                    "selected_root_call_pair":pair["root_calls"],
                    "original_selector_status":b["status"],
                    "arms":arms}
                print("C3X018_JAN_ALL_PAIR_PROBE_ATTRITION",cid,role,category,
                      "base",arms["BASE"]["source_tt_probe_count"],
                      "both",arms["BOTH"]["source_tt_probe_count"],flush=True)
            case["status"]="VALID"
        except (RuntimeError,ValueError,KeyError) as exc:
            case["status"]="HOLD_FAIL_CLOSED"
            case["failure"]=type(exc).__name__+":"+str(exc)[:280]
        report["cases"].append(case)
        print("C3X018_JAN_ATTRITION_SOURCE_CASE",cid,case["status"],flush=True)
    need([c["id"] for c in report["cases"]]==list(range(1,17)),
         "JANUARY_CASE_DENOMINATOR")
    held=sum(c["status"]!="VALID" for c in report["cases"])
    epoch_count=sum(v for k,v in tally.items() if k.endswith("SAME_KEY_DIFFERENT_PHYSICAL_EPOCH"))
    report["summary"]={"cases":16,"held":held,"role_arms_expected":31,"role_arms_valid":valid,
         "prior_single_block_source_arms":29,
         "prior_two_block_source_arms":2,
         "class_counts":dict(tally),
         "same_key_new_epoch_arms":epoch_count,
         "TAX1_EPOCH_CHURN_PREDOMINANCE":"PASS" if epoch_count>=15 else "FAIL",
         "TAX2_FULL_KEY_MATCH":"PASS" if all(
             p["shadow_full64_match"]==1
             for c in report["cases"] if c["status"]=="VALID"
             for r in c["selectors"].values() if r.get("status")=="VALID"
             for p in r["arms"]["BOTH"]["source_tt_probes"]
             if p["tt_hit"]==1 and p["tt_slot"]==r["original_selected_physical"]["slot"])
             else "FAIL",
         "TAX3_HISTORICAL_OUTCOME_NONINTERFERENCE":"PASS" if held==0 else "HOLD",
         "TAX4_DENOMINATOR":"PASS" if held==0 and valid==31 else "HOLD"}
    if held:
        for k in ("TAX1_EPOCH_CHURN_PREDOMINANCE","TAX2_FULL_KEY_MATCH"):
            report["summary"][k]="HOLD_INCOMPLETE_SAMPLE"
    report["limits"]=[
       "Adaptive selected 31 role arms (25 distinct source game-target-call pairs) after original January prospective FAIL",
       "Within-arm root_call handles may not denote path-invariant recursive nodes across arms",
       "A shadow epoch change is an accepted TT payload rewrite; it may preserve value/bound/eval while changing depth",
       "TT probe hit is a native key16 match but we also require independent full64 shadow writer match",
       "No source node-entry observer, so missing TT probe does not prove no search node was visited",
       "Any new hypothesis based on this taxonomy needs a separate blinded cohort"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X018_JAN_PHYSICAL_WRITER_EPOCH_ATTRITION_FINAL",
          json.dumps(report["summary"],sort_keys=True),flush=True)
    if held:raise RuntimeError("C3X018_JAN_FULL31_SOURCE_TAXONOMY_HOLD")
if __name__=="__main__":main()
