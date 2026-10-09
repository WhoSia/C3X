#!/usr/bin/env python3
"""C3X 0.14 — physical TT slot last-writer lineage, 14 source game groups.

Uses exact legal history source frozen before chess engine outcomes and exact
previously authenticated 224-run first-TT-return parent, with new sidecar on
TTEntry::save. New patch must be observationally equivalent in all modes.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from c3x_014_single_TT_event_pathway_court import run,semantic

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PARENT_SHA="afd48ceb040668c53609d8d5bd78d7a9b781243044cd4187a87896929ef0dd6b"
BASE_MECHANISM=("picker_main_nodes","picker_main_ttmove","lmr_invoked","lmr_with_reduction",
     "history_quiet_update","history_continuation_update","main_evaluate_calls",
     "main_tt_eval_reads","main_alpha_beta_move_cutoffs","main_tt_save_terminal",
     "first_blocked_key","first_blocked_ply","first_blocked_depth","first_blocked_bound",
     "first_blocked_tt_value","first_blocked_beta")
SITES={1:"TABLEBASE",2:"STATIC_EVAL_SAVE",3:"PROBCUT",
       4:"MAIN_TERMINAL",5:"Q_STAND_PAT",6:"Q_TERMINAL"}

def load(path,expected):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=expected:
        raise RuntimeError("C3X014_PROVENANCE_SOURCE_SHA_MISMATCH")
    return json.loads(b)
def exact_old(a,b):
    if semantic(a)!=semantic(b):return False
    if a.get("native_tt")!=b.get("native_tt"):return False
    if a.get("native_completed")!=b.get("native_completed"):return False
    if "mechanism_path" in a and "mechanism_path" in b:
        if any(a["mechanism_path"][x]!=b["mechanism_path"][x] for x in BASE_MECHANISM):
            return False
    return True

def entry(t):
    if not t["first_blocked_ply"]>=0:return None
    return {name:t[name] for name in (
        "first_blocked_key","first_blocked_ply","first_blocked_depth",
        "first_blocked_bound","first_blocked_tt_value","first_blocked_beta",
        "first_writer_known","first_writer_key_match","first_writer_full_key",
        "first_writer_site","first_writer_sequence","first_writer_slot_replacements",
        "first_writer_slot_saves","first_writer_full_overwrite")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--legal-source",required=True)
    p.add_argument("--original-224-panel",required=True)
    p.add_argument("--clean",required=True)
    p.add_argument("--lineage-bin",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--smoke",action="store_true")
    a=p.parse_args()
    source=load(a.legal_source,SOURCE_SHA);parent=load(a.original_224_panel,PARENT_SHA)
    assert source["schema"]=="c3x-014-legal-black18-alternative-chess-pawn-feature-court-v1"
    assert parent["schema"]=="c3x-014-one-native-TT-return-vs-family-and-mechanism-rival-trace-v1"
    assert parent["source_worlds_sha256"]==SOURCE_SHA
    assert parent["source_game_groups"]==14 and parent["actual_engine_processes"]==224
    assert not parent["P1_sealed_four_games_opened"] and not source["P1_sealed_holdout_read"]
    games=[z for z in source["cases"] if z["concept_preserving_world"] is not None and z["concept_changing_world"] is not None]
    assert len(games)==14
    if a.smoke:games=games[:1]
    parent_map={(z["group"],z["world"],z["cold_repeat"]):z for z in parent["all_raw_native_run_cells"]}
    assert len(parent_map)==56
    cells=[]
    for idx,c in enumerate(games,1):
        for world,black,fen in [
            ("PLAYED_HISTORY",c["original_black18"],c["original_legal_history_root_fen"]),
            ("CONCEPT_SHAM_HISTORY",c["concept_preserving_world"]["black18_uci"],c["concept_preserving_world"]["root_full_FEN"])]:
            history=c["first_17_ply_path_uci"]+[black]
            for cold in (1,2):
                old=parent_map[c["source_group"],world,cold]
                arms={}
                for mode in ("CLEAN","OFF","ONE_MAIN","MAIN"):
                    old_data=old["arms"][mode]
                    data=run(a.clean if mode=="CLEAN" else a.lineage_bin,
                             fen,c["root_candidate_pair"],history,mode)
                    if not exact_old(data,old_data):
                        raise RuntimeError("LINEAGE_INSTRUMENT_CHANGES_FROZEN_SF16_NATIVE_BEHAVIOR "+
                                           str((c["official_original_game_headers"]["Round"],world,cold,mode)))
                    arms[mode]=data
                for mode in ("OFF","ONE_MAIN","MAIN"):
                    s=arms[mode].get("slot_writer_summary")
                    if s is None or s["saves"]<=0 or s["full_overwrites"]<=0 or s["mapped_slots"]<=0:
                        raise RuntimeError("TT_SOURCE_SLOT_SIDE_CAR_NOT_RUNNING")
                one=arms["ONE_MAIN"]["mechanism_path"];allmain=arms["MAIN"]["mechanism_path"]
                if arms["ONE_MAIN"]["native_tt"]["main_blocked"]!=1:
                    raise RuntimeError("SURGICAL_FIRST_ACTUAL_TT_EVENT_NOT_BLOCKED_ONCE")
                for d in (one,allmain):
                    if d["first_blocked_ply"]>=0:
                        if d["first_writer_known"] not in (0,1) or d["first_writer_key_match"] not in (0,1):
                            raise RuntimeError("BROKEN_PHYSICAL_SLOT_WRITER_CERT")
                        if d["first_writer_key_match"] and d["first_writer_full_key"]!=d["first_blocked_key"]:
                            raise RuntimeError("IMPOSSIBLE_FULL_KEY_MATCH")
                        if d["first_writer_site"] not in (0,1,2,3,4,5,6):
                            raise RuntimeError("UNKNOWN_WRITER_CLASS")
                result={
                    "source_group":c["source_group"],"source_round":c["official_original_game_headers"]["Round"],
                    "world":world,"cold_repeat":cold,
                    "original_black_move":black,"history_18_plies":history,
                    "full_root_fen":fen,"white_root_candidates":c["root_candidate_pair"],
                    "all_four_arms_original_224_run_behavior_identical":True,
                    "one_first_blocked_consumer_and_last_writer":entry(one),
                    "main_family_first_blocked_consumer_and_last_writer":entry(allmain),
                    "one_slot_summary":arms["ONE_MAIN"]["slot_writer_summary"],
                    "main_slot_summary":arms["MAIN"]["slot_writer_summary"],
                    "off_slot_summary":arms["OFF"]["slot_writer_summary"],
                    "white_cp_OFF_ONE_MAIN_MAIN":[arms[arm]["signed_white_cp_gap"] for arm in ("OFF","ONE_MAIN","MAIN")],
                    "bestmoves_OFF_ONE_MAIN_MAIN":[arms[arm]["bestmove"] for arm in ("OFF","ONE_MAIN","MAIN")],
                    "per_arm_mechanism_counter_payload":{arm:arms[arm]["mechanism_path"] for arm in ("OFF","ONE_MAIN","MAIN")}
                }
                cells.append(result)
                first=one
                print("C3X014_TT_PRODUCER_CONSUMER_REAL_EVENT",idx,result["source_round"],world,cold,
                      "site",first["first_writer_site"],
                      "known",first["first_writer_known"],
                      "fullkey",first["first_writer_key_match"],
                      "reuse",first["first_writer_slot_replacements"],
                      "writer_seq",first["first_writer_sequence"],
                      "slots",arms["ONE_MAIN"]["slot_writer_summary"]["mapped_slots"],
                      flush=True)
    count_expected=len(games)*2*2
    assert len(cells)==count_expected
    cold_equal=0
    for g in games:
        for w in ("PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"):
            a1,a2=[x for x in cells if x["source_group"]==g["source_group"] and x["world"]==w]
            pfields=["one_first_blocked_consumer_and_last_writer",
                  "main_family_first_blocked_consumer_and_last_writer",
                  "one_slot_summary","main_slot_summary","off_slot_summary",
                  "white_cp_OFF_ONE_MAIN_MAIN","bestmoves_OFF_ONE_MAIN_MAIN",
                  "per_arm_mechanism_counter_payload"]
            if all(a1[k]==a2[k] for k in pfields):cold_equal+=1
    if cold_equal!=len(games)*2:raise RuntimeError("TT_WRITER_LOG_NONDETERMINISTIC")
    first=[z for z in cells if z["cold_repeat"]==1]
    def counted(pred):return sum(bool(pred(z["one_first_blocked_consumer_and_last_writer"])) for z in first)
    known=counted(lambda e:e["first_writer_known"])
    match=counted(lambda e:e["first_writer_key_match"])
    reused=counted(lambda e:e["first_writer_slot_replacements"]>0)
    site_count={str(i)+"_"+label:counted(lambda e:e["first_writer_site"]==i) for i,label in SITES.items()}
    site_count["0_UNATTRIBUTED"]=counted(lambda e:e["first_writer_site"]==0)
    output={
       "schema":"c3x-014-source-native-TT-physical-slot-last-writer-and-single-consumer-v1",
       "formal_research_unit":"C3X 0.14","internal_checkpoint_only":True,
       "actual_source_only_sha256":SOURCE_SHA,
       "previous_exact_224_process_court_sha256":PARENT_SHA,
       "sf16_full_physically_observed_last_writer_sidecar_only":True,
       "trace_limit":"TTEntry::save last FULL data writer to physical 10-byte slot; no full recursive causal ancestry, but six search.cpp writer sites tagged",
       "source_game_groups":len(games),"legally_reached_worlds":len(games)*2,
       "actual_engine_processes":len(cells)*4,
       "complete_all_four_arms_parent_native_exact_equivalence":len(cells)*4,
       "technical_cold_repro_worlds":cold_equal,
       "all_ONE_MAIN_blocked_exactly_one_return":len(cells),
       "first_blocked_event_producer_known_worlds":known,
       "first_blocked_event_last_producer_full64key_match_worlds":match,
       "first_blocked_event_slot_reused_different_key_worlds":reused,
       "writer_site_counts":site_count,
       "actual_raw_world_runs":cells,
       "P1_four_sealed_holdout_groups_opened":False,
       "causal_chess_concept_mediation_certified":False,
       "causal_history_lmr_NNUE_alpha_beta_mediators_independently_identified":False,
       "scope_warnings":[
         "The full 64-bit key is tracked only by a passive sidecar after TTEntry::save; native SF16 TT itself retains only 16-bit key and cluster index.",
         "Writer counts identify the last full-record writer, not previous learning or search ancestry; move-only updates can alter the native entry move field separately.",
         "ONE_MAIN selects dynamically first actual would-return; key/slot is not a fixed intervention target across alternative black moves.",
         "No independent game source and no randomization: 14 development groups are the actual scientific units, cold repeats only technical.",
         "Observed physical slot last-writer and key match cannot by itself establish the causality of the eventual chess concept or NNUE/history/LMR mediation.",
         "Source lineage memory allocation may affect runtime but must not change deterministically searched move output or work in CLEAN versus OFF or versus prior native record."]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,indent=2)+"\n")
    print("C3X014_TT_PRODUCER_CONSUMER_VERDICT",json.dumps({
       "games":len(games),"worlds":len(first),"processes":len(cells)*4,
       "parent_equivalence":len(cells)*4,"cold":cold_equal,
       "first_last_writer_known":known,"first_fullkey_match":match,
       "reused_slot":reused,"site_classes":site_count}),flush=True)
if __name__=="__main__":main()
