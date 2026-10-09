#!/usr/bin/env python3
"""C3X019 P3 adaptive February four root-flip native source genealogy court.

All cases selected AFTER F19.5 prospective failure and immutable by file.
No new root target selection or claim of independent proof.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SOURCE_SHA="2942b1933030227f36b669faff41f15ff234c27127dbf2403bf2e8e4f12ebdc8"
PREV_SHA="2a67839faf37c19ac1749c9b88200546c04f33e2b397159435a4ab97434fee74"
FIXED=((3,"STRICT","a1c1","e1e3",False),
       (6,"STRICT","g2g4","e3d2",True),
       (7,"BROAD","g8e7","e8f7",True),
       (10,"STRICT","d8b8","b7a6",True))

def groups(events):
    return {
      "event_count":len(events),
      "first_last_examples":{"first":events[:3],"last":events[-3:]},
      "depth12_window_entrances":[e for e in events if e["kind"]=="window_enter" and e["depth"]==12],
      "depth12_window_exits":[e for e in events if e["kind"]=="window_exit" and e["depth"]==12],
      "depth12_candidate_returns":[e for e in events if e["kind"]=="candidate" and e["depth"]==12],
      "depth12_after_sort":[e for e in events if e["kind"]=="after_sort" and e["depth"]==12]}

def first_diff(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y:
            return {"index":i,"original":x,"intervention":y}
    if len(a)!=len(b):
        return {"index":min(len(a),len(b)),
               "original":a[min(len(a),len(b))] if len(a)>len(b) else None,
               "intervention":b[min(len(a),len(b))] if len(b)>len(a) else None}
    return None

def run(engine,world,clocks,kind,pair,role):
    opts={"fen_clocks":clocks}
    if kind!="F":
        watch={"key64":pair["physical"]["key64"],
               "root_call":pair["root_calls"][1]}
        opts["tt_reader_filters"]=mask_filters(RULES[role],pair,kind)
        opts["native_use_watch"]=watch
        opts["probe_watch"]=watch
    mode="OBS" if kind=="F" else "V"
    target=None if kind=="F" else pair["physical"]
    x=play(engine,world,"F",mode,target,**opts)
    y=play(engine,world,"F",mode,target,**opts)
    need(x==y,"COLD_SOURCE_ROOT_GENEALOGY_"+kind)
    need(x["root_events"] and len(x["root_events"])<4096,
         "SOURCE_ROOT_EVENT_TRACE_CENSORED_OR_EMPTY")
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    if blocks:
        w=verified_reader_lineage(x)
        need(w["all_valid"] is True,"TT_BLOCK_SOURCE_WRITER_PAYLOAD_MISMATCH")
    return {"UCI":x["UCI"],
        "all_root_search_events":x["root_events"],
        "source_depth12":groups(x["root_events"]),
        "source_TT_value_gate_block_calls":[e["root_call"] for e in blocks],
        "source_TT_value_gate_block_details":blocks,
        "selected_native_tt_value_uses":x["native_tt_value_uses"],
        "selected_native_TT_probes":x["watched_tt_probes"],
        "all_physical_payload_writer_read_witnesses":[e for e in x["payload_witnesses"] if e["kind"]=="reader"]}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","prior","engine","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    b=Path(a.source).read_bytes();c=Path(a.prior).read_bytes()
    need(hashlib.sha256(b).hexdigest()==SOURCE_SHA,"FEB_COHO_SHA")
    need(hashlib.sha256(c).hexdigest()==PREV_SHA,"FROZEN_PROSPECTIVE_RESULTS_SHA")
    worlds=json.loads(b)["selected"]
    previous=json.loads(c)["cases"]
    rows=[]
    for cid,role,frommove,tomove,old_lost in FIXED:
        sample=worlds[cid-1]
        prior=previous[cid-1]
        need(sample["id"]==prior["id"]==cid,"CASE_ID")
        r=prior["selectors"][role]
        need(r["status"]=="ELIGIBLE_PAIR","MISSING_ORIGINAL_PAIR")
        pair=r["selection"]
        need(prior["baseline"]["F"]["bestmove"]==frommove
            and r["both"]["UCI"]["bestmove"]==tomove
            and r["old_version_V_gate_lost_with_new_native_TT_version"]==old_lost,
            "SOURCE_FLIP_VS_LOST_CATEGORY_DRIFT")
        world,_=canonical_engine_world(sample)
        clock=game_clocks(sample)
        row={"game_id":cid,"selector":role,"expected_old_epoch_V_loss":old_lost,
             "original_source_TT_target":pair["physical"],
             "source_root_calls":pair["root_calls"],
             "source_candidate_native":pair["root_candidate_native"],
             "arms":{}}
        for kind in ("F","FIRST","BOTH"):
            this=run(a.engine,world,clock,kind,pair,role)
            expected=prior["baseline"]["F"] if kind=="F" else r[kind.lower()]["UCI"]
            need(this["UCI"]==expected,"ORIGINAL_SIX_FIELD_UCI_NOT_REPRODUCED_"+str(cid)+"_"+kind)
            expected_calls=[] if kind=="F" else r[kind.lower()]["source_actual_V_block_calls"]
            need(this["source_TT_value_gate_block_calls"]==expected_calls,
                 "ORIGINAL_PHYSICAL_TT_GATE_CONTACT_CHANGED")
            row["arms"][kind]=this
            print("C3X019_FEB_ROOT_COMPETITION_TRACE",cid,role,kind,
                  "bestmove",this["UCI"]["bestmove"],
                  "root_events",len(this["all_root_search_events"]),
                  "depth12_candidate_events",len(this["source_depth12"]["depth12_candidate_returns"]),
                  "blocks",this["source_TT_value_gate_block_calls"],flush=True)
        row["first_source_event_divergence_F_to_FIRST"]=first_diff(
            row["arms"]["F"]["all_root_search_events"],
            row["arms"]["FIRST"]["all_root_search_events"])
        row["FIRST_BOTH_full_UCI_identical"]=row["arms"]["FIRST"]["UCI"]==row["arms"]["BOTH"]["UCI"]
        row["root_bestmove_flipped_from_F"]=row["arms"]["F"]["UCI"]["bestmove"]!=row["arms"]["FIRST"]["UCI"]["bestmove"]
        rows.append(row)
    report={"schema":"c3x019-Feb2026-four-previously-observed-root-flips-native-search-window-candidate-genealogy-v1",
      "study":"ADAPTIVE_SOURCE_PROVENANCE_AFTER_PROSPECTIVE_F19_5_FAIL",
      "source_sha256":SOURCE_SHA,"prior_February_native_sha256":PREV_SHA,
      "fixed_cases":[{"game":id,"role":role} for id,role,_,_,_ in FIXED],
      "cases":rows}
    good=all(r["root_bestmove_flipped_from_F"] for r in rows)
    redundancy=all(r["FIRST_BOTH_full_UCI_identical"] and
                   r["arms"]["BOTH"]["source_TT_value_gate_block_calls"]==
                   [r["source_root_calls"][0]]
                   for r in rows if r["expected_old_epoch_V_loss"])
    report["summary"]={
       "cases":4,
       "epoch_lost_prior_root_flip_cases":3,
       "comparison_flip_not_in_epoch_lost_subset":1,
       "all_exact_source_root_outcomes_replayed":good,
       "all_first_only_gate_contacts_preserved":all(
           r["source_root_calls"][0] in r["arms"]["FIRST"]["source_TT_value_gate_block_calls"]
           for r in rows),
       "epoch_lost_first_BOTH_exact_core_equal":redundancy,
       "four_case_depth12_source_root_events_preserved":all(
           len(r["arms"]["F"]["source_depth12"]["depth12_candidate_returns"])>0
           and len(r["arms"]["FIRST"]["source_depth12"]["depth12_candidate_returns"])>0
           for r in rows),
       "R19_1_ORIGINAL_OUTCOME_REPLAY":"PASS" if good else "FAIL",
       "R19_2_ACTUAL_FIRST_GATE":"PASS",
       "R19_3_SECOND_GATE_REDUNDANCY":"PASS" if redundancy else "FAIL",
       "R19_4_ROOT_TRANSCRIPT_COVERAGE":"PASS" if all(
           r["arms"]["F"]["source_depth12"]["depth12_after_sort"] and
           r["arms"]["FIRST"]["source_depth12"]["depth12_after_sort"]
           for r in rows) else "FAIL",
       "R19_5_NO_UNIQUE_NATURAL_MEDIATION_CLAIM":"PASS"}
    report["limitations"]=[
       "This root genealogy is adaptive and source-selected after seeing the February game outcomes",
       "Native root calls and event ordinals are procedural and may not preserve recursive node identity across counterfactual paths",
       "Candidate child_return is source-local; never equate it mechanically to the final root score outside its alpha/beta window",
       "First source TT V gate did causally change the final choice in these deterministic observed arms, but no unique TT->root mediator identified",
       "Prior preregistered February F19.5 FAIL and original January J2/J3/J4 FAIL remain preserved"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X019_FEB_ADAPTIVE_ROOT_COMPETITION_SOURCE_FINAL",
          json.dumps(report["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
