#!/usr/bin/env python3
"""C3X021 P2-R1: independent naturally ordered O full64 TT reader lineage.

Previously C3X16 'F' rotated source game's played move to the front. This court
NEVER imports its physical target into 'O'. Both STRICT and BROAD pairs are
selected from O's own source-only passive native discovery.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import (
    RULES,first_pair,mask_filters)
from c3x_021_P1_march_native_TT_atomic_bridge import (
    root_depth_ladder,first_semantic_source_split)

MARCH_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
F_P1_SHA="5ee15c3ec48be0042a9bb0ae7566808737f56e7568c2b29d43f00ae64afcb259"
ROLES=("STRICT","BROAD")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def read_sha(path,expected):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==expected,"BAD_FROZEN_SOURCE_SHA_"+Path(path).name)
    return json.loads(raw)

def cold(engine,world,clocks,world_order,mode,target=None,**extra):
    settings={"fen_clocks":clocks,**extra}
    a=play(engine,world,world_order,mode,target,**settings)
    b=play(engine,world,world_order,mode,target,**settings)
    need(a==b,"O_WORLD_COLD_REPRODUCIBILITY")
    need(a["root_events"] and len(a["root_events"])<4096,
         "O_WORLD_ROOT_EVENTS_MISSING_OR_CENSORED")
    need(not any(e.get("kind")=="trace_censored" for e in a["payload_witnesses"]),
         "O_WORLD_PASSIVE_SOURCE_CENSORED")
    return a

def judge(O,V,pair,role):
    physical=pair["physical"]
    call=pair["root_calls"][0]
    blocked=[e for e in V["blocks"] if e["kind"]=="reader_block"]
    need(len(blocked)==V["lineage_summary"]["reader_block"],
         "O_TT_BLOCK_CENSUS_DRIFT")
    need(all(
        e["root_call"]==call and
        e["root_move"]==pair["root_candidate_native"] and
        all(e[k]==physical[k] for k in ("key64","slot","epoch"))
        for e in blocked), "O_TT_WRONG_PHYSICAL_SOURCE")
    valid=verified_reader_lineage(V)
    need(not blocked or (valid["all_valid"] and valid["count"]>=len(blocked)),
         "O_TT_WRITER_READ_LINEAGE_NOT_VERIFIED")
    return {
        "status":"O_FIRST_SOURCE_DELIVERED" if blocked else "O_SOURCE_SELECTED_BUT_NOT_REACHED",
        "physical":physical,
        "source_root_calls":pair["root_calls"],
        "source_root_move_native":pair["root_candidate_native"],
        "native_reader_block_count":len(blocked),
        "native_contact":bool(blocked),
        "root_bestmove_changed":O["UCI"]["bestmove"]!=V["UCI"]["bestmove"],
        "delivered_final_choice_change":bool(blocked) and O["UCI"]["bestmove"]!=V["UCI"]["bestmove"],
        "full_UCI_changed":O["UCI"]!=V["UCI"],
        "V_UCI":V["UCI"],
        "O_vs_O_FIRST_root_ladder":{
            "O":root_depth_ladder(O["root_events"]),
            "O_FIRST":root_depth_ladder(V["root_events"])},
        "first_logged_semantic_split":first_semantic_source_split(O["root_events"],V["root_events"]),
        "native_block_events":blocked,
        "physical_writer_integrity":valid,
        "source":role,
        "cold_repeat_identical":True
    }

def court(march,frozen_F,engine):
    need(len(march["selected"])==len(frozen_F["cases"])==16,
         "O_FULL16_FROZEN_INPUT_COUNT")
    result={
        "schema":"c3x021-P2-R1-2026March16-naturalO-independent-physicalTT-first-consumer-v1",
        "protocol":"c3x/ontology/c3x-021-P2-R1-natural-O-root-order-independent-TT-lineage-precommit.md",
        "frozen_input_sha256":{"march":MARCH_SHA,"F_world_parent":F_P1_SHA},
        "semantics":"O is native initial root order, F rotates source played move to first",
        "target_source":"O world O-OBS discovery only, never F source selection",
        "strict_broad_rules":RULES,
        "games":[]}
    for src,parent in zip(march["selected"],frozen_F["cases"]):
        gid=src["id"]
        need(parent["id"]==gid and
             parent["source_sha"]==src["source_game_sha256"],
             "O_F_COHORT_IDENTITY")
        world,_=canonical_engine_world(src)
        clocks=game_clocks(src)
        O=cold(engine,world,clocks,"O","OBS")
        Z=cold(engine,world,clocks,"Z","OBS")
        need(O["UCI"]==Z["UCI"]==parent["controls"]["O_UCI"],
             "O_BASELINE_OR_SHAM_SIX_FIELD_DRIFT")
        discovery=cold(engine,world,clocks,"O","OBS",discovery=True)
        need(discovery["UCI"]==O["UCI"],
             "O_PASSIVE_DISCOVERY_INTERFERED")
        decoy=cold(engine,world,clocks,"O","V",DECOY)
        need(decoy["UCI"]==O["UCI"] and
             decoy["lineage_summary"]["reader_block"]==0,
             "O_NO_CONTACT_TT_DECOY_INTERFERED")
        # O source discovery is independent of historically F-selected physical triplet
        witness=[e for e in discovery["payload_witnesses"] if e["kind"]=="discovery"]
        need(len(witness)<=2048,"O_SOURCE_2048_CENSUS_CAP")
        row={
            "game":gid,"source_game_sha256":src["source_game_sha256"],
            "O_UCI":O["UCI"],"F_UCI":parent["controls"]["F"]["UCI"],
            "F_vs_O_bestmove_different":
                O["UCI"]["bestmove"]!=parent["controls"]["F"]["UCI"]["bestmove"],
            "F_role_previous_bestmove_flips":{
                role:parent["roles"][role].get("delivered_and_bestmove_changed",False)
                for role in ROLES},
            "O_original_root_ladder":root_depth_ladder(O["root_events"]),
            "O_passive_discovery_witnesses":len(witness),
            "O_source_reader_census_reached_limit":len(witness)>=2048,
            "O_root_order_sham":"PASS",
            "O_physical_source_decoy":"PASS",
            "roles":{}}
        for role in ROLES:
            pair=first_pair(witness,RULES[role])
            if pair is None:
                row["roles"][role]={"status":"O_NO_ELIGIBLE_SOURCE_PAIR",
                                    "native_contact":False,
                                    "delivered_final_choice_change":False}
                continue
            ZERO=cold(engine,world,clocks,"O","V",pair["physical"],
                tt_reader_filters=mask_filters(RULES[role],pair,"ZERO"))
            need(ZERO["UCI"]==O["UCI"] and
                 ZERO["lineage_summary"]["reader_block"]==0,
                 "O_PHYSICAL_ZERO_INTERFERED")
            V=cold(engine,world,clocks,"O","V",pair["physical"],
                tt_reader_filters=mask_filters(RULES[role],pair,"FIRST"))
            judge_result=judge(O,V,pair,role)
            judge_result["O_ZERO_full_UCI"]=ZERO["UCI"]
            old=parent["roles"][role]
            judge_result["F_source_status"]=old["status"]
            judge_result["F_source_physical"]=old.get("source_physical")
            judge_result["same_O_F_physical_triplet"]=(
                judge_result["physical"]==old.get("source_physical")
                if old.get("source_physical") else None)
            judge_result["same_board_O_vs_F_chess_move_changed"]=row["F_vs_O_bestmove_different"]
            row["roles"][role]=judge_result
        result["games"].append(row)
        print("C3X021_P2_R1_NATURAL_O",gid,
              "O",row["O_UCI"]["bestmove"],"F",row["F_UCI"]["bestmove"],
              {k:(v["status"],v.get("root_bestmove_changed",False))
               for k,v in row["roles"].items()},flush=True)
    roles=[g["roles"][r] for g in result["games"] for r in ROLES]
    eligible=[r for r in roles if r["status"]!="O_NO_ELIGIBLE_SOURCE_PAIR"]
    contact=[r for r in eligible if r["native_contact"]]
    result["summary"]={
        "fixed_games":16,"fixed_role_denominator":32,
        "O_source_eligible_roles":len(eligible),
        "O_first_reader_contact_roles":len(contact),
        "O_source_noncontact_roles":len(eligible)-len(contact),
        "O_first_reader_root_choice_flips":sum(r["delivered_final_choice_change"] for r in contact),
        "O_first_reader_full_UCI_changed":sum(r["full_UCI_changed"] for r in contact),
        "O_F_root_choice_different_games":sum(
            g["F_vs_O_bestmove_different"] for g in result["games"]),
        "O_F_same_physical_target_role_cells":sum(
            r["same_O_F_physical_triplet"] is True for r in eligible),
        "original_F_source_choice_flips":2,
        "focal":{
            str(gid)+"_"+role:{
                "O":result["games"][gid-1]["O_UCI"]["bestmove"],
                "F":result["games"][gid-1]["F_UCI"]["bestmove"],
                "O_source_status":result["games"][gid-1]["roles"][role]["status"],
                "O_first_reader_choice_flip":result["games"][gid-1]["roles"][role].get("delivered_final_choice_change",False),
                "O_FIRST":result["games"][gid-1]["roles"][role].get("V_UCI",{}).get("bestmove"),
                "O_vs_F_physical_same":result["games"][gid-1]["roles"][role].get("same_O_F_physical_triplet")
            } for gid,role in ((4,"BROAD"),(9,"STRICT"))},
        "historical_negative":"PAG / CPP224 / F19.5 / K4 failures retained",
        "status":"NEW_SOURCE_ROOT_ORDER_EXPLORATORY",
    }
    return result

def main():
    a=argparse.ArgumentParser()
    for k in ("march","f-parent","engine","out"):a.add_argument("--"+k,required=True)
    p=a.parse_args()
    report=court(read_sha(p.march,MARCH_SHA),read_sha(p.f_parent,F_P1_SHA),p.engine)
    path=Path(p.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("C3X021_P2_R1_NATURAL_O_TT_WRITER_READER_COURT",
          json.dumps(report["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
