#!/usr/bin/env python3
"""C3X 0.14 TT physical-slot last-writer vs first blocked consumer.

224 true SF16 runs, 14 known source game groups/28 legal chess worlds,
CLEAN/OFF/ONE_MAIN/MAIN and two cold repeats. The source and earlier actual
engine panel were frozen before the present full-key lineage patch.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics
from pathlib import Path
from c3x_014_single_TT_event_pathway_court import run,semantic

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PRIOR_NATIVE_SHA="afd48ceb040668c53609d8d5bd78d7a9b781243044cd4187a87896929ef0dd6b"
ARMS=("CLEAN","OFF","ONE_MAIN","MAIN")
COUNTERS=("picker_main_nodes","picker_main_ttmove","lmr_invoked","lmr_with_reduction",
 "history_quiet_update","history_continuation_update","main_evaluate_calls",
 "main_tt_eval_reads","main_alpha_beta_move_cutoffs","main_tt_save_terminal")
TT_TYPES={1:"MAIN_TABLEBASE_WRITE",2:"MAIN_STATIC_EVALUATION",3:"MAIN_PROBCUT",
 4:"MAIN_TERMINAL",5:"QSEARCH_EARLY",6:"QSEARCH_TERMINAL"}
def filehash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check(ok,why):
    if not ok:raise RuntimeError(why)
def match_old(old,new,arm):
    check(semantic(old)==semantic(new),"SOURCE_FROZEN_UCI_SHAM_OR_INTERVENTION_OUTPUT_DIFFERS_"+arm)
    if arm!="CLEAN":
        for key in ("native_tt","native_completed"):
            check(old[key]==new[key],"PRIOR_NATIVE_COUNTER_DRIFT_"+key+"_"+arm)
        for key in COUNTERS:
            check(old["mechanism_path"][key]==new["mechanism_path"][key],
                  "PASSIVE_TT_PATCH_CHANGED_SEARCH_COUNTER_"+key+"_"+arm)
        for key in ("first_blocked_key","first_blocked_ply","first_blocked_depth",
                    "first_blocked_bound","first_blocked_tt_value","first_blocked_beta"):
            check(old["mechanism_path"][key]==new["mechanism_path"][key],
                  "FIRST_TT_EVENT_IDENTITY_CHANGED_"+key+"_"+arm)
def verify_lineage(arm,z):
    if arm=="CLEAN":
        check("slot_writer_summary" not in z,"ORIGINAL_WAS_PATCHED")
        return
    x=z.get("slot_writer_summary")
    check(x is not None,"SIDE_CAR_NOT_REPORTED")
    check(x["saves"]==x["full"]+x["move_only"],"TT_SAVE_DISPOSITION_CENSUS_INVALID")
    check(x["probes"]>=x["probe_hits"],"TT_PROBE_HITS_EXCEED_PROBES")
    check(x["saves"]>0 and x["full"]>0,"ZERO_TT_WRITES")
    check(x["recycled"]>=0,"BAD_SLOT_REPLACEMENT")
    m=z["mechanism_path"]
    if arm=="OFF":
        check(m["first_blocked_ply"]==-1 and m["producer_known"]==0,"OFF_MUST_NOT_HAVE_BLOCKED_SITE")
    else:
        check(m["first_blocked_ply"]>=0,"MISSING_ACTUAL_RETURN")
        check(m["producer_slot_offset"] in (0,1,2),"PHYSICAL_SLOT_OUTSIDE_CLUSTER")
        check(m["producer_known"] in (0,1),"PRODUCER_TRISTATE_INVALID")
        check(m["producer_full_key_matches"] in (0,1),"FULLKEY_TEST_INVALID")
        if m["producer_known"]:
            check(m["producer_class"] in TT_TYPES,"UNTAGGED_LAST_FULLFIELD_WRITER")
            check(m["producer_full_field_writes"]>0,"NO_SUCCESSFUL_NATIVE_SAVE")
            check(m["producer_write_sequence"]>0,"NO_NATIVE_SOURCE_WRITE_ORDINAL")
            check(m["producer_full_key_matches"]==
                  int(m["producer_full_key"]==m["first_blocked_key"]),
                  "FALSE_FULL_64_BIT_IDENTITY")
            check(m["producer_full_field_writes"]>=m["producer_slot_replacements"]+1,
                  "MORE_REPLACEMENTS_THAN_ACTUAL_FULL_WRITES")
            check(m["producer_write_sequence"]<=x["saves"],"PRODUCER_FROM_THE_FUTURE")
        else:
            check(m["producer_class"]==0 and m["producer_full_key_matches"]==0,
                  "INVENTED_MISSING_PRODUCER")

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source-worlds",required=True)
    a.add_argument("--prior-engine-panel",required=True)
    a.add_argument("--original-bin",required=True)
    a.add_argument("--lineage-bin",required=True)
    a.add_argument("--out",required=True)
    x=a.parse_args()
    check(filehash(x.source_worlds)==SOURCE_SHA,"FROZEN_CHESS_SOURCE_SHA")
    check(filehash(x.prior_engine_panel)==PRIOR_NATIVE_SHA,"HISTORICAL_NATIVE_SHA")
    source=json.loads(Path(x.source_worlds).read_bytes())
    prior=json.loads(Path(x.prior_engine_panel).read_bytes())
    check(source["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1","SOURCE_SCHEMA")
    check(prior["schema"]=="c3x-014-one-native-TT-return-vs-family-and-mechanism-rival-trace-v1","PRIOR_NATIVE_SCHEMA")
    check(prior["source_game_groups"]==14 and prior["actual_engine_processes"]==224,"PRIOR_N_224")
    check(not prior["P1_sealed_four_games_opened"] and not source["P1_sealed_holdout_read"],"P1_HOLDOUT_NOT_ALLOWED")
    src=[g for g in source["cases"] if g["concept_changing_world"] and g["concept_preserving_world"]]
    check(len(src)==14,"REUSED_SOURCE_GROUP_CENSUS")
    old={(c["group"],c["world"],c["cold_repeat"]):c for c in prior["all_raw_native_run_cells"]}
    check(len(old)==56,"PRIOR_SOURCE_GROUP_CELL_CENSUS")
    samples=[];replay_checks=0;clean_sham=0
    for gi,g in enumerate(src,1):
        for name,black,fen in (
            ("PLAYED_HISTORY",g["original_black18"],g["original_legal_history_root_fen"]),
            ("CONCEPT_SHAM_HISTORY",g["concept_preserving_world"]["black18_uci"],
             g["concept_preserving_world"]["root_full_FEN"])):
            full_history=g["first_17_ply_path_uci"]+[black]
            for cold in (1,2):
                prior_cell=old[(g["source_group"],name,cold)]
                outcomes={}
                for arm in ARMS:
                    path=x.original_bin if arm=="CLEAN" else x.lineage_bin
                    outcome=run(path,fen,g["root_candidate_pair"],full_history,arm)
                    match_old(prior_cell["arms"][arm],outcome,arm)
                    replay_checks+=1
                    verify_lineage(arm,outcome)
                    outcomes[arm]=outcome
                identical=semantic(outcomes["CLEAN"])==semantic(outcomes["OFF"])
                check(identical,"NEW_PASSIVE_LINEAGE_CLEAN_OFF_SHAM_FAILED")
                clean_sham+=1
                check(outcomes["ONE_MAIN"]["native_tt"]["main_blocked"]==1,
                      "ONE_MAIN_NOT_EXACTLY_ONE_BLOCKED_EVENT")
                check(outcomes["MAIN"]["native_tt"]["main_taken"]==0,"FAMILY_ARM_INCOMPLETE")
                ob=outcomes["ONE_MAIN"]["mechanism_path"]
                row={"source_game_id":g["source_game_id"],"source_group":g["source_group"],
                    "round":g["official_original_game_headers"]["Round"],
                    "world":name,"cold":cold,
                    "original_black18":black,"full_history":full_history,
                    "legal_white_pair":g["root_candidate_pair"],"fen":fen,
                    "original_sham_exact":identical,
                    "one_return_actual_site":{
                       k:v for k,v in ob.items() if k.startswith("first_blocked") or k.startswith("producer_")},
                    "one_return_producer_class_name":TT_TYPES.get(ob["producer_class"],"UNKNOWN"),
                    "one_return_causal_uci_choice_relabel":
                       outcomes["OFF"]["bestmove"]!=outcomes["ONE_MAIN"]["bestmove"],
                    "one_return_strict_cp_sign_inversion":(
                       outcomes["OFF"]["signed_white_cp_gap"] is not None
                       and outcomes["ONE_MAIN"]["signed_white_cp_gap"] is not None
                       and outcomes["OFF"]["signed_white_cp_gap"]*
                           outcomes["ONE_MAIN"]["signed_white_cp_gap"]<0),
                    "arms":outcomes}
                samples.append(row)
                print("C3X014_TT_PRODUCER_CONSUMER_REAL",gi,row["round"],name,cold,
                     "writer",ob["producer_class"],"full64",ob["producer_full_key_matches"],
                     "reuse",ob["producer_slot_replacements"],"writes",
                     ob["producer_full_field_writes"],"last_move_only",
                     ob["producer_last_move_only"],
                     "choice_relabel",row["one_return_causal_uci_choice_relabel"],flush=True)
    check(len(samples)==56 and replay_checks==224 and clean_sham==56,"INCOMPLETE_WORLD_REPLAY")
    repeated=0
    for g in src:
        for name in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"):
            pair=[s for s in samples if s["source_group"]==g["source_group"] and s["world"]==name]
            check(len(pair)==2,"COLD_DUPLICATE")
            if pair[0]["arms"]==pair[1]["arms"]:repeated+=1
    check(repeated==28,"SIDE_CAR_COLD_REPLAY_FAILURE")
    first=[r for r in samples if r["cold"]==1]
    known=[r for r in first if r["one_return_actual_site"]["producer_known"]]
    exact=[r for r in known if r["one_return_actual_site"]["producer_full_key_matches"]]
    wrong=[r for r in known if not r["one_return_actual_site"]["producer_full_key_matches"]]
    counts={k:sum(r["one_return_producer_class_name"]==k for r in first) for k in TT_TYPES.values()}
    recycled=sum(r["one_return_actual_site"]["producer_slot_replacements"]>0 for r in first)
    moveonly=sum(r["one_return_actual_site"]["producer_last_move_only"]>0 for r in first)
    changed=[r for r in first if r["one_return_causal_uci_choice_relabel"]]
    summary={"schema":"c3x-014-pinned-sf16-native-tt-physical-slot-last-writer-lineage-v1",
       "one_formal_research_unit":"C3X 0.14","P_checkpoints_only":True,
       "source_chess_world_sha256":SOURCE_SHA,"prior_engine_panel_sha256":PRIOR_NATIVE_SHA,
       "original_stockfish16_binary_sha256":filehash(x.original_bin),
       "sidecar_stockfish16_binary_sha256":filehash(x.lineage_bin),
       "source_game_groups":14,"legal_history_worlds":28,
       "cold_restarts":2,"native_engine_processes":224,
       "new_vs_prior_native_engine_arm_outputs_exact":replay_checks,
       "within_new_original_vs_OFF_sham":clean_sham,
       "cold_technical_reproducibility_worlds":repeated,
       "ONE_MAIN_exactly_one_blocked_per_run":56,
       "first_cold_producer_known_worlds":len(known),
       "first_cold_full_64_bit_writer_key_matches_consumed_key":len(exact),
       "first_cold_native_full_key_mismatch":len(wrong),
       "first_cold_slot_reuse_occurring_before_first_blocked_event":recycled,
       "first_cold_last_slot_touch_only_move_write":moveonly,
       "first_cold_last_fullfield_writer_classes":counts,
       "first_cold_ONE_MAIN_root_choice_relabels":len(changed),
       "root_choice_relabels_with_full64_matched_producer":
          sum(r["one_return_actual_site"]["producer_full_key_matches"]==1 for r in changed),
       "source_first_cold":first,
       "all_actual_224_native_engine_arms":samples,
       "P1_four_heldout_games_opened":False,
       "scientific_claim_limitations":[
           "Observed producer is last successful full-field save into same physical TT slot in THIS cold engine run, not provenance of all ancestors of cached value.",
           "TT actual hit logic compares 16-bit stored key inside a cluster indexed by high-width mul_hi64, not full 64 bits; sidecar match is independent diagnostic.",
           "The sidecar counts source-write classes and physical replacements but does not identify why the last writer computed its value.",
           "Observed writer↔consumer connection does not identify separate LMR/history/move ordering/NNUE/alpha-beta mediators.",
           "Original and concept-preserving last-black-move worlds are different boards and have different TT search keys; do not infer same exact source TT event transport.",
           "All 14 chess games are old known development samples; four P1 source holdout games remain unopened.",
           "Every TTEntry::save call in native SF16 search.cpp tagged; other writer classes must be separately audited before claiming complete global TT provenance.",
           "Cold technical repeats do not count as 56 independent games or confirm cross-engine transport."
       ]}
    out=Path(x.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_TT_PRODUCER_LINEAGE_VERDICT",json.dumps({
      "groups":14,"worlds":28,"runs":224,"prior_exact":replay_checks,"sham":clean_sham,
      "cold":repeated,"known":len(known),"full64":len(exact),"different64":len(wrong),
      "recycled":recycled,"moveonly":moveonly,"writers":counts,
      "ONE_MAIN_choice_relabels":len(changed)}),flush=True)
if __name__=="__main__":main()
