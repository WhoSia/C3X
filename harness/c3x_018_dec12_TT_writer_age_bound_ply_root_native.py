#!/usr/bin/env python3
"""December 2025 prespecified TT source role eight-selector intervention court.

The original game source is SHA frozen before any engine results. Observer
matches TT full64 writer key, 3-entry physical slot, epoch and raw payload.
Writer age is number of accepted global in-process saves since that writer.
Selectors overlap; no artificial statistical independence asserted.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world, verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks

SOURCE_SHA="51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd"
ARCHIVE_SHA="fadbe80ee65e9f8499578e934d7600ece69d09b1cf8abc75fdd3bd840f61e63f"
SELECTORS=("young","old","lower","upper","shallow","deep","original_root","other_root")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def audit_reader(e):
    need(e["known"]==1 and e["matched"]==1,"UNMATCHED_LAST_PHYSICAL_WRITER")
    need(e["writer_serial"]>0,"MISSING_LAST_WRITER_SERIAL")
    need(e["key64"]==e["writer_key64"],"MISMATCHED_WRITER_FULL64")
    need(e["epoch"]>0 and 0<=e["slot"]<3,"BAD_PHYSICAL_SLOT")
    need(e["current_write_serial"]>=e["writer_serial"],"NONMONOTONE_WRITER_COUNT")
    need(e["writer_age_writes"]==e["current_write_serial"]-e["writer_serial"],
         "WRITER_AGE_ARITHMETIC")
    need(e["ply"]>=0,"NEGATIVE_SEARCH_PLY")
    need(e["raw_bound"] in (1,2,3),"UNRECOGNIZED_STOCKFISH_BOUND")
    return True

def belongs(e,category,original_move):
    if category=="young":return 0<=e["writer_age_writes"]<=8
    if category=="old":return e["writer_age_writes"]>=64
    if category=="lower":return e["raw_bound"]==2
    if category=="upper":return e["raw_bound"]==1
    if category=="shallow":return e["ply"]<=2
    if category=="deep":return e["ply"]>=4
    if category=="original_root":
        return e["reader_root_call"]>0 and e["reader_root_move"]==original_move
    if category=="other_root":
        return e["reader_root_call"]>0 and e["reader_root_move"]!=0 and e["reader_root_move"]!=original_move
    raise RuntimeError("UNKNOWN_PREREGISTERED_CATEGORY")

def main():
    p=argparse.ArgumentParser()
    for key in ("source","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    source_raw=Path(a.source).read_bytes()
    need(hashlib.sha256(source_raw).hexdigest()==SOURCE_SHA,"DECEMBER_SEALED_COHORT_SHA")
    cohort=json.loads(source_raw)
    need(cohort["compressed_source_sha256"]==ARCHIVE_SHA,"DECEMBER_ORIGINAL_ARCHIVE_SHA")
    need(len(cohort["selected"])==12,"TWELVE_FROZEN_GAMES")
    result={"schema":"c3x018-december-independent12-TT-role-factor-eight-selector-native-v1",
       "source_sha256":SOURCE_SHA,"archive_sha256":ARCHIVE_SHA,
       "preregistration":"c3x/ontology/c3x-018-dec2025-blind12-TT-writer-age-bound-ply-root-preregistration.md",
       "search_depth":12,"selector_order":list(SELECTORS),"cases":[]}
    for original in cohort["selected"]:
        world,normalize=canonical_engine_world(original)
        half,full=game_clocks(original)
        case={"id":original["id"],"original_game_sha256":original["source_game_sha256"],
             "fen4":world["fen4"],"clock":[half,full],"normalization":normalize,
             "root_played_move_native":world["native_move"],"status":"NOT_RUN",
             "selectors":{cat:{"status":"NOT_RUN"} for cat in SELECTORS}}
        try:
            controls={}
            for mode in ("O","F","Z"):
                x=play(a.engine,world,mode,"OBS",fen_clocks=(half,full))
                y=play(a.engine,world,mode,"OBS",fen_clocks=(half,full))
                need(x==y,f"COLD_CONTROL_{mode}")
                need(x["root_contact"]["target_contact"]==("0" if mode=="Z" else "1"),
                     "ROOT_NO_CONTACT_NEGATIVE_CONTROL_"+mode)
                controls[mode]=x["UCI"]
            need(controls["O"]==controls["Z"],"NEGATIVE_ROOT_SHAM_DRIFT")
            d1=play(a.engine,world,"F","OBS",discovery=True,fen_clocks=(half,full))
            d2=play(a.engine,world,"F","OBS",discovery=True,fen_clocks=(half,full))
            need(d1==d2,"PASSIVE_FEATURE_DISCOVERY_NONDETERMINISTIC")
            need(d1["UCI"]==controls["F"],"SOURCE_FEATURE_OBSERVER_CHANGED_ENGINE")
            candidates=[e for e in d1["payload_witnesses"] if e["kind"]=="discovery"]
            for e in candidates:audit_reader(e)
            case["source_cores"]=controls
            case["passive_discovery_count"]=len(candidates)
            case["passive_census_cap"]=256
            case["passive_censored_if_at_cap"]=len(candidates)>=256
            case["passive_source_candidates"]=candidates  # preserve entire source ordering to audit selection
            decoy=play(a.engine,world,"F","V",DECOY,fen_clocks=(half,full))
            need(decoy["UCI"]==controls["F"] and decoy["lineage_summary"]["reader_block"]==0,
                 "IMPOSSIBLE_FULL64_DECOY_FAIL")
            case["decoy_no_contact_exact"]=True
            for cat in SELECTORS:
                chosen=next(((i,e) for i,e in enumerate(candidates)
                            if belongs(e,cat,world["native_move"])),None)
                record={"category":cat,"status":"NOT_ELIGIBLE"}
                if chosen is not None:
                    ordinal,event=chosen
                    target={k:event[k] for k in ("key64","slot","epoch")}
                    x=play(a.engine,world,"F","V",target,fen_clocks=(half,full))
                    y=play(a.engine,world,"F","V",target,fen_clocks=(half,full))
                    need(x==y,f"COLD_V_{cat}")
                    verified=verified_reader_lineage(x)
                    reached=x["lineage_summary"]["reader_block"]
                    need(reached==0 or (
                       verified["count"]>=reached and verified["all_valid"] is True),
                       "PHYSICAL_WRITER_PAYLOAD_FAIL_"+cat)
                    reader_witness=[e for e in x["payload_witnesses"] if e["kind"]=="reader"]
                    for r in reader_witness:audit_reader(r)
                    record={"category":cat,
                       "status":"FIRED" if reached>0 else "NOT_FIRED",
                       "selected_passive_ordinal":ordinal,
                       "selected_physical_target":target,
                       "passive_source_feature":event,
                       "reader_hits":reached,
                       "physical_writer_value_witnesses":reader_witness,
                       "writer_provenance_valid":verified["all_valid"],
                       "final_UCI":x["UCI"],
                       "bestmove_changed":x["UCI"]["bestmove"]!=controls["F"]["bestmove"],
                       "full_core_changed":x["UCI"]!=controls["F"],
                       "selected_role_is_observer_label_not_cross_arm_unique_event":True}
                case["selectors"][cat]=record
            case["status"]="VALID"
        except (RuntimeError,KeyError,ValueError) as err:
            case["status"]="HOLD_FAIL_CLOSED"
            case["failure"]=type(err).__name__+":"+str(err)[:320]
        result["cases"].append(case)
        print("C3X018_DECEMBER_TT_FACTOR",case["id"],case["status"],
              {k:(v["status"],v.get("bestmove_changed")) for k,v in case["selectors"].items()},
              flush=True)
    need([x["id"] for x in result["cases"]]==list(range(1,13)),"DENOMINATOR_IDS")
    valid=[x for x in result["cases"] if x["status"]=="VALID"]
    def flips(cat):
        return sum(x["selectors"][cat]["status"]=="FIRED" and
                   x["selectors"][cat]["bestmove_changed"] for x in valid)
    def realized(cat):
        return sum(x["selectors"][cat]["status"]=="FIRED" for x in valid)
    owner_contrast=[x["id"] for x in valid if all(x["selectors"][k]["status"]=="FIRED"
              for k in ("original_root","other_root")) and
              x["selectors"]["original_root"]["bestmove_changed"] !=
              x["selectors"]["other_root"]["bestmove_changed"]]
    all_arms=[x["selectors"][k] for x in valid for k in SELECTORS]
    eligible=[x for x in all_arms if x["status"]!="NOT_ELIGIBLE"]
    invalid=[x for x in eligible if x.get("status")=="FIRED" and
            x["writer_provenance_valid"] is not True]
    summary={
       "full_denominator":12,"valid_source_games":len(valid),
       "held_source_games":12-len(valid),"planned_selectors":96,
       "observed_selectors":sum(len(x["selectors"]) for x in result["cases"]),
       "eligible_selectors":len(eligible),
       "actual_fired_selectors":sum(x["status"]=="FIRED" for x in eligible),
       "source_contact_by_selector":{cat:realized(cat) for cat in SELECTORS},
       "bestmove_changes_by_selector":{cat:flips(cat) for cat in SELECTORS},
       "owner_contrast_source_game_ids":owner_contrast,
       "unverified_writer_payloads":len(invalid),
       "D1_OLD_ROOT":"PASS" if flips("old")>0 else "FAIL",
       "D2_DEEP_ROOT":"PASS" if flips("deep")>0 else "FAIL",
       "D3_BOUND_ROOT":"PASS" if flips("lower")+flips("upper")>0 else "FAIL",
       "D4_OWNER_CONTRAST":"PASS" if owner_contrast else "FAIL",
       "D5_SOURCE_INTEGRITY":("FAIL" if invalid else "PASS" if any(x["status"]=="FIRED" for x in eligible) else "NOT_TESTED"),
       "D6_NO_CONTACT":"PASS" if len(valid)==12 else "HOLD",
       "D7_COMPLETE_DENOMINATOR":"PASS" if len(result["cases"])==12 and all(len(x["selectors"])==8 for x in result["cases"]) else "FAIL"
    }
    if len(valid)!=12:
       for k in ("D1_OLD_ROOT","D2_DEEP_ROOT","D3_BOUND_ROOT","D4_OWNER_CONTRAST","D5_SOURCE_INTEGRITY"):
           summary[k]="HOLD_INCOMPLETE_NATIVE_SAMPLE"
    result["summary"]=summary
    result["limits"]=[
      "Each selector chooses first qualifying passive source event BEFORE any V output; eight overlapping marginal selectors",
      "Multiple V reader events may have identical physical source target; a target can affect more than the nominated reader",
      "Age is global accepted TT save count after last physical writer, not elapsed seconds nor slot replacement count",
      "Root attribution is the last native root candidate for current cold root search call, not proof of natural TT ownership",
      "Source reader discovery capped at 256 records; cap hit means a censored later-search census",
      "Position uses original authentic rule50/fullmove in standalone legal-EP FEN, not original repetition move stack",
      "Successful V effect is selective perturbation response, not sole natural causal mediation",
      "Failing prospective predictions not reclassified through same-source retargeting"]
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_DECEMBER_TT_WRITER_AGE_BOUND_PLY_ROOT_NATIVE",
          json.dumps(summary,sort_keys=True),flush=True)
    if len(valid)!=12:raise RuntimeError("DECEMBER_NATIVE_COURT_HOLD_FAIL_CLOSED")
if __name__=="__main__":main()
