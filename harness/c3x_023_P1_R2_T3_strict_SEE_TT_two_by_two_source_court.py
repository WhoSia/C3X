#!/usr/bin/env python3
"""T3 actual pinned-sourced SEE Boolean SHAM/FLIP x physical TT FIRST 2x2.

All five gates before first mutation: Lichess S0 frozen, StageA SHA frozen,
T1 state identity SHA, T2 single-event site manifest Git-sealed, and genuine
SHAM contact under both unchanged TT and TT FIRST (cold twice). Only May #11
and no-flip control #2 eligible. #1/#12 HOLD, #8/#3 censored. DEVELOPMENT.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import (
 SOURCE_SHA,STAGEA_SHA,frozen)

T2_JSON_SHA="830536f445330b739a7a3b7e88ce4227e9ab9db43cf277f08a01ed5f9dc0ef69"
T2_GIT="c3x/forecasts/c3x-023-P1-R2-T2-exact-native-SEE-targets-before-first-actuator-20261011.json"
ELIGIBLE=((11,"F","STRICT"),(2,"O","STRICT"))
T3_FIELDS=("key64","parent_key64","t1_path","root_call","root_move",
           "move","site","threshold","t1_ply","t1_depth","t1_alpha",
           "t1_beta","t1_pv","t1_qsearch","t1_rule50",
           "t1_occupied_present","t1_occupied_out","original_SEE_Boolean")
SCHEMA="c3x023-P1-R2-T3-exact-native-SEE-two-cases-physical-TT-crossed-development-v1"

def prereg(source,stageA,preselected,artifact):
    need(source["schema"]=="c3x023-P1-licensed-independent-May-broadcast-and-disjoint-CC0-nonmate-puzzles-v1",
         "T3_SOURCE_PROVENANCE_WRONG")
    need(stageA["summary"]["actual_TT_FIRST_interventions"]==0,
         "T3_STAGE_A_ALREADY_TREATED")
    need(preselected["freeze_status"]==
         "GIT_LITERALS_COMMITTED_BEFORE_ANY_NEW_EXACT_SEE_OPERATOR_FLIP",
         "T3_SOURCE_LITERAL_UNSEALED")
    need(artifact["schema"]=="c3x023-P1-R2-T2-preactuation-four-May-source-exact-native-SEE-targets-v1" and
         artifact["original_T1_raw_full_SHA256"]==
         "6c0440693c83ba0cd219d396b7d1cb2cdd14e3324f0c0f77485edf1df288c0a8",
         "T3_TARGET_NOT_PROVEN_SOURCE_ONLY")
    original={(z["game_id"],z["root_order"],z["source_role"]):z
              for z in artifact["cases"]}
    sealed={(z["game_id"],z["root_order"],z["role"]):z
            for z in preselected["development_cases"]}
    need(set(original)==set(sealed) and len(sealed)==4,
         "T3_SOURCE_TARGETS_HAVE_BEEN_CHANGED")
    out=[]
    for key in original:
        x=original[key];y=sealed[key]
        z=x["source_exact_pruning_SEE_target"]
        t=y["selected_source_SEE"]
        need(bool(z)==bool(t),"T3_MANUALLY_SEALED_SITE_ELIGIBILITY_CHANGED")
        if z:
            need({f:(str(z[f]) if f in ("key64","parent_key64") else z[f])
                    for f in T3_FIELDS}
                 =={f:t[f] for f in T3_FIELDS},"T3_TARGET_SOURCE_LITERAL_MISMATCH")
    need(set(ELIGIBLE)=={k for k,v in sealed.items() if v["selected_source_SEE"]},
         "T3_UNPRESPECIFIED_NEW_DEVELOPMENT_CASE")
    for key in ELIGIBLE:
        t=sealed[key]["selected_source_SEE"]
        need(set(T3_FIELDS).issubset(t),"T3_FULL_NATIVE_SOURCE_SITE_FIELDS_MISSING")
        out.append((key,{f:t[f] for f in T3_FIELDS}))
    return out

def cold(engine,world,clock,order,policy,preregistered,scope,use_first,role):
    kwargs={"fen_clocks":clock,"allow_empty_lineage":True,
            "t3_target":preregistered,"t3_policy":policy,
            "see_watch":{"key64":scope["physical"]["key64"],
                         "root_call":scope["root_calls"][0],
                         "policy":"OBS","passive_ancestry":True},
            "native_use_watch":{"key64":scope["physical"]["key64"],
                                "root_call":scope["root_calls"][0]}}
    mode="V" if use_first else "OBS"
    tt_target=scope["physical"] if use_first else None
    if use_first:
        pair={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
        kwargs["tt_reader_filters"]=mask_filters(RULES[role],pair,"FIRST")
    a=play(engine,world,order,mode,tt_target,**kwargs)
    b=play(engine,world,order,mode,tt_target,**kwargs)
    need(a==b,"T3_EXACT_NATIVE_COLD_PAIR_UNSTABLE")
    hits=a["native_T3_exact_source_contact_events"]
    need(len(hits)<=2 and len([x for x in hits if x["kind"]=="contact"])<=2,
         "T3_MULTIPLE_OR_CENSORED_NATIVE_SAME_NODE_OCCURRENCES")
    need(all(x["key64"]==int(preregistered["key64"]) and
             x["root_call"]==preregistered["root_call"] and
             x["site"]==preregistered["site"] and
             x["original"]==preregistered["original_SEE_Boolean"]
             for x in hits),"T3_UNPRECOMMITTED_NATIVE_SOURCE_SCOPE_INTERFERED")
    blocks=[x for x in a["blocks"] if x["kind"]=="reader_block"]
    if use_first:
        need(blocks and all(x["key64"]==scope["physical"]["key64"] and
               x["slot"]==scope["physical"]["slot"] and
               x["epoch"]==scope["physical"]["epoch"] and
               x["root_call"]==scope["root_calls"][0] and
               x["root_move"]==scope["root_candidate_native"] for x in blocks),
             "T3_EXPECTED_ORIGINAL_PHYSICAL_TT_READER_MISSING")
        lin=verified_reader_lineage(a)
        need(lin["all_valid"] and lin["count"]>=len(blocks),
             "T3_PHYSICAL_SOURCE_WRITER_TO_READER_PROOF_BROKEN")
    else:
        need(not blocks,"T3_ORIGINAL_TT_SHAM_BLOCKED_READER")
    altered=sum(x["altered"]==1 for x in hits)
    need(altered==(1 if policy=="FLIP" and len(hits)==1 else 0),
         "T3_SOURCE_FIRST_SINGLETON_ACTUATOR_DOSE_WRONG")
    if len(hits)!=1:
        # A unique source identity is required even if source rootcall exists.
        return {"status":"HOLD_NO_UNIQUE_EXACT_NATIVE_SEE_SOURCE_CONTACT",
                "real_native_TT_FIRST":bool(blocks),
                "SEE_site_exact_hits":len(hits),
                "SEE_actuator_delivered":altered}
    return {"status":"VALID_SOURCE_SINGLETON",
            "real_native_TT_FIRST":bool(blocks),
            "SEE_site_exact_hits":len(hits),
            "SEE_actuator_delivered":altered,
            "source_native_SEE_original_Boolean":hits[0]["original"],
            "source_native_SEE_delivered_Boolean":hits[0]["delivered"],
            "terminal_UCI":a["UCI"],
            "root_depth_history":source_depth_ladder(a["root_events"]),
            "cold_reproducible":True}

def scan(source,stageA,presealed,source_target_manifest,engine):
    target_roles=prereg(source,stageA,presealed,source_target_manifest)
    cases=[]
    for (gid,order,role),t in target_roles:
        src=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        old=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(src["id"]==old["id"]==gid,"T3_SOURCE_GAME_ID")
        target=old["worlds"][order]["roles"][role]
        need(target["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME",
             "T3_TT_FIRST_SOURCE_NOT_ELIGIBLE")
        world,clock,_=native_world(src)
        # First validate both sham cells before ANY active SEE source mutation.
        base=cold(engine,world,clock,order,"SHAM",t,target,False,role)
        first=cold(engine,world,clock,order,"SHAM",t,target,True,role)
        need(base["status"]=="VALID_SOURCE_SINGLETON"
             and first["status"]=="VALID_SOURCE_SINGLETON",
             "T3_PREREGISTERED_SOURCE_SITE_NOT_PRESENT_UNIQUELY_IN_BOTH_SHAMS")
        need(base["terminal_UCI"]==old["worlds"][order]["baseline_UCI"],
             "T3_SHAM_EXACT_SOURCE_OBSERVER_CHANGED_ORIGINAL_UCI")
        # Only after source, rootcall, path, SEE Boolean and TT reader verified:
        see=cold(engine,world,clock,order,"FLIP",t,target,False,role)
        joint=cold(engine,world,clock,order,"FLIP",t,target,True,role)
        need(see["status"]=="VALID_SOURCE_SINGLETON"
             and joint["status"]=="VALID_SOURCE_SINGLETON"
             and see["SEE_actuator_delivered"]==joint["SEE_actuator_delivered"]==1,
             "T3_EXACT_TARGET_BECAME_INELIGIBLE_UNDER_SEE_OR_TT_PATH")
        A=base["terminal_UCI"]["bestmove"];B=first["terminal_UCI"]["bestmove"]
        C=see["terminal_UCI"]["bestmove"];D=joint["terminal_UCI"]["bestmove"]
        diff={"TT_ONLY_changes_baseline":B!=A,
              "SEE_ONLY_changes_baseline":C!=A,
              "JOINT_changes_baseline":D!=A,
              "JOINT_differs_from_TT_ONLY":D!=B,
              "JOINT_differs_from_SEE_ONLY":D!=C,
              "JOINT_new_move_not_in_other_three":D not in (A,B,C)}
        cases.append({"game_id":gid,"source_role":role,"root_order":order,
             "exact_source_preregistered_pruning_site":t["site"],
             "physical_TT_FIRST_source":target["physical"],
             "native_sham_baseline":base,"native_TT_FIRST_only":first,
             "native_SEE_once_only":see,"native_joint_once":joint,
             "categorical_terminal_move_differences":diff,
             "cause_kind":"EXACT_SOURCE_OPERATOR_BOOLEAN_FLIP_DEVELOPMENT_ONLY",
             "natural_TT_SEE_mediation_proved":False})
        print("C3X023_T3_NATIVE_EXACT_SEE_OPERATOR_FACTORIAL",gid,order,role,
              {"physical_TT_FIRST":True,
               "SEE_original_flip":see["SEE_actuator_delivered"],
               "SEE_joint_flip":joint["SEE_actuator_delivered"],
               **diff},flush=True)
    out={"schema":SCHEMA,"status":"VALIDATED_TWO_ACTUAL_PRECOMMITTED_SOURCE_SPECIFIC_FACTORIALS",
         "study":"POST_R1_DEVELOPMENT_NOT_NEW_HELDOUT",
         "source_root_SHA256":SOURCE_SHA,"stageA_sha256":STAGEA_SHA,
         "preactuator_site_selection_artifact_SHA256":T2_JSON_SHA,
         "git_presealed_site_literals":T2_GIT,"cases":cases}
    out["summary"]={"source_chess_cases":len(cases),
       "actual_physical_TT_FIRST_source_sham_and_joint_arms":2*len(cases),
       "exact_presealed_native_SEE_singleton_flips":2*len(cases),
       "exact_node_contact_sham_arms":2*len(cases),
       "cases_joint_differs_TT_only":sum(x["categorical_terminal_move_differences"][
          "JOINT_differs_from_TT_ONLY"] for x in cases),
       "cases_SEE_only_changes_baseline":sum(x["categorical_terminal_move_differences"][
          "SEE_ONLY_changes_baseline"] for x in cases),
       "prior_research_holds_not_reassigned":[1,12,8,3],
       "source_operator_controlled_interaction_not_natural_mediation":True}
    return out

def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","presealed","source-targets","engine","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    manifest=frozen(a.source_targets,T2_JSON_SHA)
    out=scan(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),
             json.loads(Path(a.presealed).read_bytes()),manifest,a.engine)
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X023_T3_EXACT_NATIVE_BOOL_INTERVENTION_TWO_CASE_VERDICT",
          out["summary"],hashlib.sha256(dst.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
