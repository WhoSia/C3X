#!/usr/bin/env python3
"""Actual SF16 first TT-returnable-event matching across OFF, ONE_MAIN, MAIN.

The same frozen 14 games/28 legal source worlds. 168 native C++ processes;
no new independent game samples; exact comparison to preceding 224-run file.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics
from pathlib import Path
from c3x_014_single_TT_event_pathway_court import run,semantic

WORLD_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PRIOR_SHA="577a19d6fda01350605fa92da2cf33265fd62b356958043e8ac4b853dc1ff5ae"
ARMS=("OFF","ONE_MAIN","MAIN")
TT_LABELS={1:"MAIN_TABLEBASE",2:"MAIN_STATIC_EVAL",3:"MAIN_PROBCUT",
 4:"MAIN_TERMINAL",5:"QSEARCH_EARLY",6:"QSEARCH_TERMINAL"}
EVENT_FIELDS=("first_eligible_key","first_eligible_ply","first_eligible_depth",
  "first_eligible_bound","first_eligible_tt_value","first_eligible_beta",
  "first_eligible_writer_tag","first_eligible_saved_fullkey",
  "first_eligible_fullkey_match","first_eligible_writer_ply")
ORIGINAL_PATH_FIELDS=("picker_main_nodes","picker_main_ttmove","lmr_invoked",
 "lmr_with_reduction","history_quiet_update","history_continuation_update",
 "main_evaluate_calls","main_tt_eval_reads","main_alpha_beta_move_cutoffs",
 "main_tt_save_terminal","first_blocked_key","first_blocked_ply","first_blocked_depth",
 "first_blocked_bound","first_blocked_tt_value","first_blocked_beta",
 "producer_cluster","producer_slot_offset","producer_full_key",
 "producer_write_sequence","producer_class","producer_last_touch_class",
 "producer_full_key_matches","producer_known","producer_slot_replacements",
 "producer_full_field_writes","producer_last_move_only","producer_previous_full_key")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def demand(x,m):
    if not x:raise RuntimeError(m)
def norm(x):
    r=semantic(x);r["ranks"]={str(k):v for k,v in r["ranks"].items()}
    return r
def equal_to_prior(o,n,arm):
    demand(norm(o)==norm(n),"LAST_WRITER_CONTEXT_LOGGER_UCI_DRIFT_"+arm)
    demand(o["native_tt"]==n["native_tt"],"NATIVE_EP9_TRACE_DRIFT_"+arm)
    demand(o["native_completed"]==n["native_completed"],"NATIVE_COMPLETION_DRIFT_"+arm)
    for k in ORIGINAL_PATH_FIELDS:
        demand(o["mechanism_path"][k]==n["mechanism_path"][k],
               "ORIGINAL_PATH_OR_TT_CONSUMER_CHANGED_"+k+"_"+arm)
    x=o["slot_writer_summary"];y=n["slot_writer_summary"]
    for k in ("saves","full","recycled","first_key_match","first_unknown",
              "first_key_mismatch","probes","probe_hits"):
        demand(x[k]==y[k],"SOURCE_TT_WRITE_CENSUS_DRIFT_"+k+"_"+arm)
    demand(x["move_only"]==y["move_only"]+y["no_op"],"OLD_NOFULL_WRITES_DID_NOT_PARTITION")

def test_triads(arms):
    triads=[arms[arm]["mechanism_path"] for arm in ARMS]
    ref={k:triads[0][k] for k in EVENT_FIELDS}
    for arm,trace in zip(ARMS[1:],triads[1:]):
        demand({k:trace[k] for k in EVENT_FIELDS}==ref,
               "PRETREATMENT_FIRST_TT_EVENT_NOT_MATCHED_ACROSS_OFF_ONE_MAIN_"+arm)
    demand(ref["first_eligible_ply"]>=0,"NO_ACTUALLY_RETURNABLE_FIRST_EVENT")
    demand(ref["first_eligible_writer_tag"] in TT_LABELS,"ELIGIBLE_SOURCE_WRITER_UNTAGGED")
    demand(ref["first_eligible_fullkey_match"]==1,"FIRST_ELIGIBLE_WRONG_FULL64KEY")
    demand(ref["first_eligible_saved_fullkey"]==ref["first_eligible_key"],
           "PRETREATMENT_TT_FULL_KEY_ERROR")
    for mode in ("ONE_MAIN","MAIN"):
        t=arms[mode]["mechanism_path"]
        for a,b in (("first_blocked_key","first_eligible_key"),
                    ("first_blocked_ply","first_eligible_ply"),
                    ("first_blocked_depth","first_eligible_depth"),
                    ("first_blocked_bound","first_eligible_bound"),
                    ("first_blocked_tt_value","first_eligible_tt_value"),
                    ("first_blocked_beta","first_eligible_beta")):
            demand(t[a]==t[b],"FIRST_BLOCKED_IS_NOT_FIRST_ELIGIBLE_"+mode+"_"+a)
        demand(t["producer_writer_saved_bound"]==t["first_blocked_bound"],
               "WRITER_SAVE_BOUND_CHANGED_BEFORE_CONSUMPTION_"+mode)
        demand(t["producer_writer_ply"]>=0,"MISSING_NATIVE_WRITER_PLY")
        demand(t["producer_writer_saved_depth"]>=0,"MISSING_SAVED_POSITIVE_DEPTH")
        demand(t["producer_writer_saved_tt_value"]!=32767,"NONSENSICAL_TT_VALUE")
        demand(t["producer_class"]==ref["first_eligible_writer_tag"],
               "FIRST_ELIGIBLE_WRITER_CLASS_CHANGED")
    return ref

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--previous",required=True)
    ap.add_argument("--patched-bin",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    demand(sha(a.source)==WORLD_SHA and sha(a.previous)==PRIOR_SHA,"FROZEN_SOURCE_ARTIFACT_SHA")
    src=json.loads(Path(a.source).read_bytes())
    prior=json.loads(Path(a.previous).read_bytes())
    demand(prior["schema"]=="c3x-014-pinned-sf16-native-tt-physical-slot-last-writer-lineage-v1","PARENT_SCHEMA")
    demand(prior["new_vs_prior_native_engine_arm_outputs_exact"]==224,"NOT_A_VERIFIED_PARENT")
    groups=[x for x in src["cases"] if x["concept_changing_world"] and x["concept_preserving_world"]]
    demand(len(groups)==14,"SOURCE_14")
    baseline={(r["source_group"],r["world"],r["cold"]):r for r in prior["all_actual_224_native_engine_arms"]}
    demand(len(baseline)==56,"PARENT_56")
    cells=[]
    for gi,g in enumerate(groups,1):
        for world,black,fen in (
            ("PLAYED_HISTORY",g["original_black18"],g["original_legal_history_root_fen"]),
            ("CONCEPT_SHAM_HISTORY",g["concept_preserving_world"]["black18_uci"],g["concept_preserving_world"]["root_full_FEN"])):
            hist=g["first_17_ply_path_uci"]+[black]
            for cold in (1,2):
                parent=baseline[(g["source_group"],world,cold)]
                arms={}
                for mode in ARMS:
                    cur=run(a.patched_bin,fen,g["root_candidate_pair"],hist,mode)
                    equal_to_prior(parent["arms"][mode],cur,mode)
                    arms[mode]=cur
                matched=test_triads(arms)
                clean_against_prior=norm(arms["OFF"])==norm(parent["arms"]["CLEAN"])
                demand(clean_against_prior,"PASSIVE_PATCH_BREAKS_PREVIOUS_TRUE_CLEAN")
                row={"game_id":g["source_game_id"],"group":g["source_group"],
                    "round":g["official_original_game_headers"]["Round"],
                    "world":world,"cold":cold,"fen":fen,
                    "full_legal_history":hist,"legal_white_pair":g["root_candidate_pair"],
                    "exact_pretreatment_first_event":matched,"three_way_first_eligible_identical":True,
                    "first_TT_blocked_matches_that_eligible_event":True,
                    "writer_ply_from_ONE_MAIN":arms["ONE_MAIN"]["mechanism_path"]["producer_writer_ply"],
                    "writer_saved_depth":arms["ONE_MAIN"]["mechanism_path"]["producer_writer_saved_depth"],
                    "writer_saved_bound":arms["ONE_MAIN"]["mechanism_path"]["producer_writer_saved_bound"],
                    "writer_saved_tt_value":arms["ONE_MAIN"]["mechanism_path"]["producer_writer_saved_tt_value"],
                    "consumer_ply":matched["first_eligible_ply"],
                    "consumer_depth":matched["first_eligible_depth"],
                    "writer_consumer_ply_delta":matched["first_eligible_ply"]-arms["ONE_MAIN"]["mechanism_path"]["producer_writer_ply"],
                    "no_full_field_save_calls_by_mode":{m:arms[m]["slot_writer_summary"]["no_op"] for m in ARMS},
                    "actual_move_field_only_save_calls_by_mode":{m:arms[m]["slot_writer_summary"]["move_only"] for m in ARMS},
                    "arms":arms}
                cells.append(row)
                print("C3X014_FIRST_ELIGIBLE_WRITER_CONSUMER_REAL",gi,row["round"],world,cold,
                      "first_key",matched["first_eligible_key"],
                      "writer_ply",row["writer_ply_from_ONE_MAIN"],
                      "consumer_ply",row["consumer_ply"],
                      "writer_depth",row["writer_saved_depth"],
                      "consumer_depth",row["consumer_depth"],flush=True)
    demand(len(cells)==56,"TOTAL_ARM_CELL_MISSING")
    tech=0
    for g in groups:
        for world in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"):
            pair=[c for c in cells if c["group"]==g["source_group"] and c["world"]==world]
            demand(len(pair)==2,"DUPLICATE_COLD")
            if pair[0]["arms"]==pair[1]["arms"]:tech+=1
    demand(tech==28,"COLD_CONTEXT_NOT_STABLE")
    observed=[r for r in cells if r["cold"]==1]
    result={"schema":"c3x-014-sf16-exact-first-returnable-event-and-writer-ply-depth-context-v1",
        "research_unit":"C3X 0.14","inside_same_formal_stage":True,
        "prior_source_world_sha256":WORLD_SHA,"prior_last_writer_native_panel_sha256":PRIOR_SHA,
        "source_groups":14,"source_worlds":28,"technical_restarts":2,
        "new_native_engine_processes":168,
        "prior_native_UCI_and_original_path_replayed_exact_arm_count":168,
        "cold_pair_replay_all_arm_values_out_of28":tech,
        "OFF_ONE_MAIN_MAIN_first_eligible_full_event_identical_in_all_28_worlds":
            sum(r["three_way_first_eligible_identical"] for r in observed),
        "ONE_MAIN_FIRST_BLOCKED_matches_OFF_FIRST_TAKEN_pretreatment_site":
            sum(r["first_TT_blocked_matches_that_eligible_event"] for r in observed),
        "first_return_source_writer_classes":{
          TT_LABELS[k]:sum(r["exact_pretreatment_first_event"]["first_eligible_writer_tag"]==k for r in observed)
          for k in TT_LABELS},
        "true_saved_writer_ply_equals_first_consumer_ply":
          sum(r["writer_ply_from_ONE_MAIN"]==r["consumer_ply"] for r in observed),
        "writer_ply_less_than_consumer_ply":
          sum(r["writer_ply_from_ONE_MAIN"]<r["consumer_ply"] for r in observed),
        "writer_ply_greater_than_consumer_ply":
          sum(r["writer_ply_from_ONE_MAIN"]>r["consumer_ply"] for r in observed),
        "saved_tt_depth_equal_first_consumer_requested_depth":
          sum(r["writer_saved_depth"]==r["consumer_depth"] for r in observed),
        "writer_to_consumer_ply_delta_values":[r["writer_consumer_ply_delta"] for r in observed],
        "per_world_first_cold":observed,"all_cold_native_arm_outcomes":cells,
        "P1_four_game_holdout_opened":False,
        "chess_concept_causal_mediation_identified":False,
        "no_individual_competing_search_path_causality_identified":True,
        "science_limitations":[
         "This is the SAME previously exposed fourteen TCEC development source groups and not a fresh independent blind trial.",
         "The same first TT event is explicitly compared before choosing OFF taken or ONE_MAIN/MAIN blocked action; the parent writer sidecar was previously validated.",
         "Last saved writer ply, bound and depth are last fullfield save contexts, not the full search proof subtree that produced score.",
         "TT save method calls may produce no native field mutation (no_op). Move-only and full writes are distinguished but the recorder is not an event-level log of NNUE or alpha-beta computation.",
         "No intervening condition on posttreatment node counts is used to identify an unmeasured direct mediator.",
         "Chess legal concept change is not an isolated mediator and no human understanding claim is authorized."
        ]}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_MATCHED_ELIGIBLE_TT_EVENT_WRITER_CONTEXT_VERDICT",json.dumps({
      "worlds":28,"runs":168,"cold":tech,
      "matched_predecision":result["OFF_ONE_MAIN_MAIN_first_eligible_full_event_identical_in_all_28_worlds"],
      "classes":result["first_return_source_writer_classes"],
      "same_ply":result["true_saved_writer_ply_equals_first_consumer_ply"],
      "earlier_writer_ply":result["writer_ply_less_than_consumer_ply"],
      "later_writer_ply":result["writer_ply_greater_than_consumer_ply"],
      "same_saved_depth":result["saved_tt_depth_equal_first_consumer_requested_depth"]}),flush=True)
if __name__=="__main__":main()
