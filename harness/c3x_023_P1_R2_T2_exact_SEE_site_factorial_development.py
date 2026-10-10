#!/usr/bin/env python3
"""C3X 0.23-P1-R2-T2 source-EXACT native SEE single Boolean perturbation.

MUST recompute earlier private T1 original+TT-FIRST six case JSON and require
same SHA before selecting targets. Deterministic preregistered rule: only first
two already T1-matched, earliest eligible quiet/qsearch pruning. A missing or
rejected target NEVER falls back to arbitrary root-descendant. Development only.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_023_P1_R2_T1_exact_state_six_native_development import (
    scan as stageT1,SCHEMA as T1_SCHEMA)
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
    SELECTED, SOURCE_SHA, STAGEA_SHA, frozen)

T1_SHA="1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb"
SEELIST=("quiet_prune","qsearch_prune","qsearch_futility")
FIELDS=("key64","parent_key64","path_exact","root_call","root_move",
        "move","site","threshold","source_ply","source_depth",
        "source_alpha","source_beta","source_pv","source_rule50",
        "source_occupancy64")
SCHEMA="c3x023-P1-R2-T2-exact-native-pruning-SEE-source-factorial-development-v1"

def select(case):
    """Only first-two original T1 matches (frozen before any T2 actuation).
    No target after T1 count >2, no cherry-picking by root move endpoints."""
    c=case["SEE_native_search_state_comparison"]
    if c["status"]!="POST_TT_COMPUTATIONAL_SEE_INPUT_WINDOW_MATCH":
        return {"status":c["status"],"target":None}
    records=c["first_two_full_computational_match_candidates"]
    need(len(records) in (1,2),"T2_T1_FIRST_TWO_SOURCE_CASE_INVALID")
    for r in records:
        if r["source_key"]["site"] not in SEELIST:continue
        source={**r["source_key"],**r["state"]}
        need(all(k in source for k in FIELDS),"T2_T1_SOURCE_KEY_AND_LIVE_STATE_INCOMPLETE")
        t={k:source[k] for k in FIELDS}
        need(t["source_alpha"]<t["source_beta"] and
             t["site"] in SEELIST and
             len(t["path_exact"].split(","))>=1,
             "T2_SOURCE_TARGET_INVALID_COMPUTATIONAL_INPUT")
        return {"status":"T1_FIRST_TWO_SOURCE_SEE_ELIGIBLE", "target":t,
                "original_native_SEE_boolean":r["SEE_original_boolean"]}
    return {"status":"NO_PRESEALED_FIRST_TWO_NONCAPTURE_SEE_SITE","target":None}

def cold(engine,world,clocks,order,target,role,tt,flip,scope):
    # TT FIRST only at original pinned physical writer-reader.
    kw={"fen_clocks":clocks,"allow_empty_lineage":True,
        "ordered_source_trace":True,
        "native_use_watch":{"key64":scope["key64"],"root_call":scope["root_call"]},
        "see_watch":{"key64":scope["key64"],"root_call":scope["root_call"],
                     "policy":"OBS","passive_ancestry":True}}
    mode="OBS";triple=None
    if tt:
        mode="V";triple=role["physical"]
        pair={"physical":role["physical"],"root_calls":role["root_calls"],
              "root_candidate_native":role["root_candidate_native"]}
        kw["tt_reader_filters"]=mask_filters(RULES[role["source_role"]],
                                               pair,"FIRST")
    if flip:kw["t2_target"]=target
    x=play(engine,world,order,mode,triple,**kw)
    y=play(engine,world,order,mode,triple,**kw)
    need(x==y,"T2_EXACT_NATIVE_ACTUATOR_COLD_REPRODUCIBILITY")
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    if not tt:
        need(not blocks,"T2_TT_ORIGINAL_UNEXPECTED_READER_SUPPRESSION")
    else:
        need(blocks and len(blocks)==x["lineage_summary"]["reader_block"] and
             all(e["key64"]==role["physical"]["key64"] and
                 e["slot"]==role["physical"]["slot"] and
                 e["epoch"]==role["physical"]["epoch"] and
                 e["root_call"]==role["root_calls"][0] and
                 e["root_move"]==role["root_candidate_native"] for e in blocks),
             "T2_WRONG_PHYSICAL_TT_FIRST_WRITER_READER")
        lineage=verified_reader_lineage(x)
        need(lineage["all_valid"] and lineage["count"]>=len(blocks),
             "T2_NATIVE_WRITER_TO_FIRST_READER_CERTIFICATE")
    forced=[e for e in x["native_see_events"] if e.get("altered")==1]
    need(not forced if not flip else len(forced)<=1,"T2_SINGULAR_SEE_FORCE_SOURCE_CONTACT")
    if forced:
        actual=forced[0]
        need(all(actual[k]==target[k] for k in FIELDS if k in actual) and
             actual["original"]!=actual["delivered"] and
             actual["site"]==target["site"] and
             actual["kind"] in ("witness","forced"),
             "T2_ACTUATED_WRONG_SEE_SOURCE_OR_BOOL")
    return {"bestmove":x["UCI"]["bestmove"],"UCI":x["UCI"],
            "real_TT_reader_blocks":len(blocks),
            "SEE_forced_actual_source_contacts":len(forced),
            "SEE_forced_source_event":forced,
            "native_SEE_log_is_censored":any(e["kind"]=="censored"
                                           for e in x["native_see_events"]),
            "root_depth_leaders":source_depth_ladder(x["root_events"]),
            "native_value_uses_at_selected_source":x["native_tt_value_uses"],
            "cold_reproduced":True}

def run(source,stageA,engine):
    # Exact T1 source measurement retaken with S=0 on a T2-aware executable.
    # Original source root JSON not distributed in T2 public aggregate.
    T1=stageT1(source,stageA,engine)
    raw=(json.dumps(T1,indent=2,sort_keys=True)+"\n").encode()
    actual_hash=hashlib.sha256(raw).hexdigest()
    need(T1["schema"]==T1_SCHEMA and actual_hash==T1_SHA,
         "T2_T1_READONLY_RAW_SHA_REPLAY_DRIFT_ABORT_BEFORE_ACTUATOR_"+actual_hash)
    output={"schema":SCHEMA,"phase":"AFTER_PREREG_T1_NATIVE_SOURCE_EXACT_SEE_POLICY",
            "T1_original_native_raw_verified_sha256":actual_hash,
            "new_chess_source_sha256":SOURCE_SHA,
            "frozen_stageA_sha256":STAGEA_SHA,"study":"POST_R1_OUTCOME_INFORMED_DEVELOPMENT_ONLY",
            "cases":[]}
    case_by_id={(c["game_id"],c["original_source_order"],c["source_TT_role"]):c
                for c in T1["cases"]}
    for gid,order,role in SELECTED:
        prev=case_by_id[(gid,order,role)]
        selected=select(prev)
        rec={"game_id":gid,"order":order,"role":role,
             "presealed_deterministic_target_status":selected["status"],
             "frozen_T1_pruning_operator_original_bool":
                 selected.get("original_native_SEE_boolean"),
             "actual_T2_source_exact_site_intervention_executed":False}
        target=selected["target"]
        if target is None:
            rec["status"]="HOLD_NO_UNIQUE_PRESEALED_PRUNING_EVENT"
            output["cases"].append(rec)
            print("C3X023_P1_R2_T2_NONCONTACT_TARGET_HOLD",gid,order,role,
                  selected["status"],flush=True)
            continue
        # Record full source identity in private experiment ONLY.
        rec["target"]=target
        original=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        earlier=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        role_entry={**earlier["worlds"][order]["roles"][role],"source_role":role}
        board,clocks,_=native_world(original)
        watch={"key64":role_entry["physical"]["key64"],
               "root_call":role_entry["root_calls"][0]}
        need(target["root_call"]==watch["root_call"],"T2_TARGET_NOT_ORIGINAL_ROOT_CALL")
        cells={}
        for tt in (False,True):
            for forced in (False,True):
                arm=f"T{int(tt)}_S{int(forced)}"
                cells[arm]=cold(engine,board,clocks,order,target,role_entry,
                                tt,forced,watch)
        need(cells["T0_S0"]["UCI"]==earlier["worlds"][order]["baseline_UCI"],
             "T2_ACTUATOR_OFF_BASELINE_UCI_NOT_FROZEN_STAGEA")
        need((cells["T1_S0"]["bestmove"]!=cells["T0_S0"]["bestmove"])==
             prev["bestmove_changed"],"T2_TT_ONLY_RESULT_DRIFT_FROM_T1")
        a=cells["T0_S1"];b=cells["T1_S1"]
        active=(a["SEE_forced_actual_source_contacts"]==1 and
                b["SEE_forced_actual_source_contacts"]==1)
        rec.update({"status":"EXACT_TWO_ARM_SOURCE_SITE_DOSE_VALID" if active
                    else "NO_CONTACT_T2_IDENTICAL_SITE_IN_ONE_OR_MORE_ARMS",
                    "actual_T2_source_exact_site_intervention_executed":
                       bool(a["SEE_forced_actual_source_contacts"] or
                            b["SEE_forced_actual_source_contacts"]),
                    "per_arm":cells,
                    "complete_source_identical_2x2":active,
                    "SEE_only_changes_final_move":
                      (cells["T0_S1"]["bestmove"]!=cells["T0_S0"]["bestmove"]
                       if active else None),
                    "joint_changes_TT_only_final_move":
                      (cells["T1_S1"]["bestmove"]!=cells["T1_S0"]["bestmove"]
                       if active else None),
                    "joint_is_novel_fourth_root_move":
                      (cells["T1_S1"]["bestmove"] not in
                       (cells["T0_S0"]["bestmove"],
                        cells["T1_S0"]["bestmove"],
                        cells["T0_S1"]["bestmove"]) if active else None)})
        output["cases"].append(rec)
        print("C3X023_P1_R2_T2_NATIVE_ONE_OPERATOR",gid,order,role,
              "site",target["site"],"contact_TT0",a["SEE_forced_actual_source_contacts"],
              "contact_TT1",b["SEE_forced_actual_source_contacts"],
              "valid_2x2",active,
              "SEE_only_choice_change",rec["SEE_only_changes_final_move"],
              "SEE_joint_choice_change",rec["joint_changes_TT_only_final_move"],
              flush=True)
    out=output["cases"]
    valid=[x for x in out if x.get("complete_source_identical_2x2")]
    selected=[x for x in out if x.get("target") is not None]
    output["summary"]={
      "source_T1_true_byte_for_byte_replay_verified":True,
      "original_precommitted_development_role_cells":len(SELECTED),
      "first_two_strict_matched_SEE_source_targets_eligible":len(selected),
      "predeclared_HOLD_no_target_count":len(SELECTED)-len(selected),
      "valid_two_SEE_dosed_2x2_games":len(valid),
      "native_SEE_true_Boolean_dose_arms":sum(
         c["SEE_forced_actual_source_contacts"]>0 for x in selected
         for key,c in x.get("per_arm",{}).items() if key.endswith("_S1")),
      "active_target_sites":dict(sorted({site:sum(
          x["target"]["site"]==site for x in selected)
          for site in SEELIST}.items())),
      "SEE_only_changes_final_move_on_valid_2x2_count":sum(
           x["SEE_only_changes_final_move"] for x in valid),
      "same_exact_SEE_node_joint_changes_TT_only_final_move_count":sum(
           x["joint_changes_TT_only_final_move"] for x in valid),
      "joint_novel_root_move_on_valid_2x2_count":sum(
           x["joint_is_novel_fourth_root_move"] for x in valid),
      "no_TWIC_PGN_original_redistribution":True,
      "population_claim":"NONE_DEVELOPMENT_CASES_POST_R1_ONLY",
      "natural_mediation_claimed":False}
    return output

def main():
    a=argparse.ArgumentParser()
    for k in ("source","stagea","engine","out"):a.add_argument("--"+k,required=True)
    x=a.parse_args()
    v=run(frozen(x.source,SOURCE_SHA),frozen(x.stagea,STAGEA_SHA),x.engine)
    p=Path(x.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print("C3X023_P1_R2_T2_FULL_SOURCE_EXACT_NATIVE_SEE_TT_FACTORIAL_VERDICT",
          v["summary"],hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
