#!/usr/bin/env python3
"""Prospective Feb2026 native TT value use beyond analyst shadow writer epoch.

Original 16 source games frozen before engine analysis, same strict/broad
pair selectors as January. Actual native main/qsearch eval assignment OR real
TT cutoff return counted, not V reader_block or key16 probe alone.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair,mask_filters

SOURCE_SHA="2942b1933030227f36b669faff41f15ff234c27127dbf2403bf2e8e4f12ebdc8"
ARCHIVE_SHA="ea977569917718b33940ba5379db2adad77d58876c29084294d357f15fe6a31b"
ALLOW_USE=("main","qsearch","main_cutoff","qsearch_cutoff")
ROLES=("STRICT","BROAD")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def replay(engine,world,clock,mode,target=None,**extra):
    opts={"fen_clocks":clock,**extra}
    x=play(engine,world,"F" if mode=="V" else mode,mode if mode=="V" else "OBS",target,**opts)
    y=play(engine,world,"F" if mode=="V" else mode,mode if mode=="V" else "OBS",target,**opts)
    need(x==y,"COLD_ND_"+mode)
    return x

def arm(engine,world,clock,rule,pair,kind):
    physical=pair["physical"]
    watch={"key64":physical["key64"],"root_call":pair["root_calls"][1]}
    x=replay(engine,world,clock,"V",physical,
        tt_reader_filters=mask_filters(rule,pair,kind),
        probe_watch=watch,native_use_watch=watch)
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    valid_calls={pair["root_calls"][0]} if kind=="FIRST" else set(pair["root_calls"])
    need(all(e["root_call"] in valid_calls and
             all(e[k]==physical[k] for k in ("key64","slot","epoch"))
             for e in blocks),"V_ACTUAL_BLOCK_WRONG_ORIGINAL_TARGET")
    witness=[e for e in x["payload_witnesses"] if e["kind"]=="reader"]
    if blocks:
        verified=verified_reader_lineage(x)
        need(verified["all_valid"] is True and
             verified["count"]>=len(blocks),"ACTUAL_SOURCE_BLOCK_RAW_LAST_WRITER_INVALID")
    uses=[e for e in x["native_tt_value_uses"] if e["kind"]=="used"]
    need(not any(e["kind"]=="censored" for e in x["native_tt_value_uses"]),
         "NATIVE_ASSIGNMENT_OR_CUTOFF_CENSORED")
    need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
         "SOURCE_KEY_PROBE_CENSORED")
    need(all(e["site"] in ALLOW_USE and
             e["key64"]==watch["key64"] and
             e["root_call"]==watch["root_call"] and
             e["full64_match"]==1 for e in uses),
         "NATIVE_ACTUAL_USE_WITNESS_INVALID")
    probes=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
    need(all(e["key64"]==watch["key64"] and e["root_call"]==watch["root_call"]
             for e in probes),"NATIVE_PROBE_SOURCE_WRONG")
    live=[e for e in probes if e["tt_hit"]==1 and
            e["shadow_full64_match"]==1 and
            e["tt_slot"]==physical["slot"]]
    need(not uses or live,"ACTUAL_NATIVE_USE_WITHOUT_MATCHING_FULL64_TT_PROBE")
    return {"UCI":x["UCI"],
        "source_actual_V_block_calls":[e["root_call"] for e in blocks],
        "source_reader_block_count":len(blocks),
        "source_V_actual_block_events":blocks,
        "source_last_writer_raw_payload_witnesses":witness,
        "second_source_root_search_entered":any(e["kind"]=="window_enter" and
            e.get("root_call")==watch["root_call"] for e in x["root_events"]),
        "second_source_TT_probe":probes,
        "second_source_key_full64_matching_hits":live,
        "actual_native_value_uses":uses,
        "actual_native_eval_assignments":sum(e["site"] in ("main","qsearch") for e in uses),
        "actual_native_TT_cutoff_returns":sum(e["site"] in ("main_cutoff","qsearch_cutoff") for e in uses)}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","engine","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    b=Path(a.source).read_bytes()
    need(hashlib.sha256(b).hexdigest()==SOURCE_SHA,"NEW_FEB_SOURCE_SHA")
    cohort=json.loads(b)
    need(cohort["compressed_source_sha256"]==ARCHIVE_SHA,"FEB_ORIGINAL_PGN_ARCHIVE_SHA")
    need(len(cohort["selected"])==16,"FEB_SOURCE_16_COMPLETE")
    data={"schema":"c3x019-FEB2026-prospective-native-TT-consumer-survival-v1",
      "study_type":"BLIND_NEW_SOURCE_MONTH_PRECOMMITTED_BEFORE_OUTCOME",
      "source_sha256":SOURCE_SHA,"PGN_archive_sha256":ARCHIVE_SHA,
      "preregistration":"c3x/ontology/c3x-019-P2-february2026-blind16-native-TT-consumption-transport-preregistration.md",
      "roles":RULES,"cases":[]}
    held=[]
    for source in cohort["selected"]:
        cid=source["id"]
        world,norm=canonical_engine_world(source)
        clock=game_clocks(source)
        row={"id":cid,"source_game_sha256":source["source_game_sha256"],
             "source_clock":list(clock),"selectors":{},
             "status":"NOT_STARTED"}
        try:
            O=replay(a.engine,world,clock,"O")
            F=replay(a.engine,world,clock,"F")
            Z=replay(a.engine,world,clock,"Z")
            need(O["UCI"]==Z["UCI"],"NO_ROOT_TOUCH_SHAM_CHANGED")
            discovered=replay(a.engine,world,clock,"F",discovery=True)
            need(discovered["UCI"]==F["UCI"],"PASSIVE_SOURCE_MUTATED_UCI")
            decoy=replay(a.engine,world,clock,"V",DECOY)
            need(decoy["UCI"]==F["UCI"] and
                 decoy["lineage_summary"]["reader_block"]==0,
                 "IMPOSSIBLE_PHYSICAL_WRITER_KEY_CHANGED_UCI")
            events=[x for x in discovered["payload_witnesses"]
                      if x["kind"]=="discovery"]
            need(len(events)<=2048,"CENSUS_GT_CAP")
            row.update(status="VALID",
                baseline={"O":O["UCI"],"F":F["UCI"],"Z":Z["UCI"]},
                no_contact_sham_pass=True,
                passive_readers=events,
                passive_census_count=len(events),
                census_censored=len(events)==2048)
            for role in ROLES:
                pair=first_pair(events,RULES[role])
                if pair is None:
                    row["selectors"][role]={"status":"NO_ELIGIBLE_PAIR"}
                    continue
                a_first=arm(a.engine,world,clock,RULES[role],pair,"FIRST")
                a_both=arm(a.engine,world,clock,RULES[role],pair,"BOTH")
                original=pair["physical"]
                first=pair["root_calls"][0]
                second=pair["root_calls"][1]
                old_target_ineligible=(a_first["source_actual_V_block_calls"]==[first] and
                    a_both["source_actual_V_block_calls"]==[first] and
                    a_both["second_source_root_search_entered"] and
                    bool(a_both["second_source_key_full64_matching_hits"]) and
                    all(e["shadow_epoch"]!=original["epoch"]
                        for e in a_both["second_source_key_full64_matching_hits"]))
                native_uses=a_both["actual_native_value_uses"]
                output={"status":"ELIGIBLE_PAIR","selection":pair,
                    "first":a_first,"both":a_both,
                    "old_version_V_gate_lost_with_new_native_TT_version":old_target_ineligible,
                    "native_value_use_survived_after_old_gate_loss":bool(native_uses) if old_target_ineligible else None,
                    "native_cutoff_after_old_gate_loss":bool(a_both["actual_native_TT_cutoff_returns"]) if old_target_ineligible else None,
                    "categorical_bestmove_changed":a_both["UCI"]["bestmove"]!=F["UCI"]["bestmove"]}
                row["selectors"][role]=output
            row["status"]="VALID"
        except (RuntimeError,KeyError,ValueError) as exc:
            row["status"]="HOLD_FAIL_CLOSED"
            row["failure"]=type(exc).__name__+":"+str(exc)[:350]
            held.append((cid,row["failure"]))
        data["cases"].append(row)
        print("C3X019_FEB_NATIVE_SOURCE",cid,row["status"],
              {r:(q["status"],q.get("old_version_V_gate_lost_with_new_native_TT_version"),
                  q.get("native_value_use_survived_after_old_gate_loss")) for r,q in row["selectors"].items()},flush=True)
    need([c["id"] for c in data["cases"]]==list(range(1,17)),
         "SOURCE_GAME_DENOMINATOR")
    eligible=[(c,r,v) for c in data["cases"] if c["status"]=="VALID"
            for r,v in c["selectors"].items() if v["status"]=="ELIGIBLE_PAIR"]
    strict=sum(r=="STRICT" for _,r,v in eligible)
    lost=[(c,r,v) for c,r,v in eligible
          if v["old_version_V_gate_lost_with_new_native_TT_version"]]
    survivor=sum(v["native_value_use_survived_after_old_gate_loss"] for _,_,v in lost)
    cutoff=sum(v["native_cutoff_after_old_gate_loss"] for _,_,v in lost)
    flips=sum(v["categorical_bestmove_changed"] for _,_,v in lost)
    valid=len([c for c in data["cases"] if c["status"]=="VALID"])
    summary={"source_games":16,"valid_games":valid,"technical_holds":held,
      "strict_eligible_games":strict,"eligible_role_arms":len(eligible),
      "old_version_gate_lost_and_new_key_valid":len(lost),
      "native_value_use_survived_arms":survivor,
      "native_value_use_survival_rate":survivor/len(lost) if lost else None,
      "native_TT_cutoff_survived_arms":cutoff,
      "root_bestmove_change_in_lost_old_gate_arms":flips,
      "F19_1_ELIGIBLE_STRUCTURE":"PASS" if strict>=12 else "FAIL",
      "F19_2_OLD_TARGET_ATTRITION":"PASS" if len(lost)>=12 else "FAIL",
      "F19_3_NATIVE_VALUE_SURVIVAL":"PASS" if len(lost) and survivor/len(lost)>=.70 else "FAIL",
      "F19_4_DUAL_USE_TAXONOMY":"PASS" if cutoff>=1 else "FAIL",
      "F19_5_ROOT_CHOICE_NONTRANSPORT":"PASS" if flips<=2 else "FAIL",
      "F19_6_SOURCE_PROVENANCE":"PASS" if valid==16 and not held else "HOLD"}
    if held or valid!=16:
        for k in list(summary):
            if k.startswith("F19_"):summary[k]="HOLD_SOURCE_INCOMPLETE"
    data["summary"]=summary
    data["limitations"]=[
       "First 2048 passive V reader events are censored at that count; denominator has both eligible and no-pair cases",
       "Source Feb cohort is new month, but engine is same SF16 source and all game states are standalone FEN with authentic clocks; no original repetition history",
       "Native TT value used includes distinct source eval assignment and real early cutoff; effects on categorical root bestmove require separate proof",
       "STRICT and BROAD selectors can select the same physical game-key-slot-epoch-call pair; don't treat overlap as independent population",
       "Prediction F19.3 tests survival of native consumption, not sufficiency of writer version to cause final bestmove",
       "Old January J2 J3 J4 prospective failures remain failures even if new Feb predictions pass"]
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("C3X019_FEBRUARY_PRECOMMITTED_TT_NATIVE_USE_HOLDOUT_FINAL",
          json.dumps(summary,sort_keys=True),flush=True)
    if held:raise RuntimeError("FEB_C3X019_FULL_SOURCE_HOLD")
if __name__=="__main__":main()
