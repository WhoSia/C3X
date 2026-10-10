#!/usr/bin/env python3
"""C3X022-P1 April16 prospective root-order x TT source-physical first-reader court.

Every outcome comes AFTER official-SHA April source and all 486 legal root
action primitives were already sealed. No reuse of March physical TT identity,
no cross-order transfer of a source key, and no outcome-based position filter.
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
    root_depth_ladder,first_semantic_source_split,move_micro_comparison)

SOURCE_SHA="0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93"
ATOMIC_SHA="95b3d8857bad9147d5d655dcbe5d0e31300c57833bd6d04a8a905f278ac67986"
ROLES=("STRICT","BROAD")
WORLDS=("O","F")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def read_frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,
         "APRIL_PRENATIVE_SHA_DRIFT_"+Path(path).name)
    return json.loads(raw)

def cold(engine,world,clock,order,mode,target=None,**kw):
    extras={"fen_clocks":clock,**kw}
    a=play(engine,world,order,mode,target,**extras)
    b=play(engine,world,order,mode,target,**extras)
    need(a==b,"C3X022_COLD_REPEAT_MISMATCH")
    need(a["root_events"] and len(a["root_events"])<4096,
         "APRIL_ROOT_TRACE_MISSING_OR_CENSORED")
    need(not any(e.get("kind") in ("censored","trace_censored")
                 for e in a["payload_witnesses"]),
         "APRIL_PHYSICAL_TT_SOURCE_CENSORED")
    return a

def physical_contact(data,pair):
    blocks=[e for e in data["blocks"] if e["kind"]=="reader_block"]
    need(len(blocks)==data["lineage_summary"]["reader_block"],
         "APRIL_READER_BLOCK_COUNT_DRIFT")
    triple=pair["physical"];call=pair["root_calls"][0]
    need(all(
        e["root_call"]==call
        and e["root_move"]==pair["root_candidate_native"]
        and all(e[k]==triple[k] for k in ("key64","slot","epoch"))
        for e in blocks),"APRIL_NATIVE_SOURCE_PHYSICAL_CONTACT_MISMATCH")
    check=verified_reader_lineage(data)
    need(not blocks or (check["all_valid"] is True and
                        check["count"]>=len(blocks)),
         "APRIL_FIRST_TT_WRITER_READER_PROOF_FAIL")
    return blocks,check

def study(april,atom,engine):
    need(april["phase"]=="SOURCE_ONLY_BEFORE_APRIL_NATIVE_OUTCOMES" and
         atom["phase"]=="SOURCE_ONLY_COMPLETE_BEFORE_NATIVE_EXAMINATION" and
         len(april["selected"])==len(atom["positions"])==16,
         "APRIL16_ENGINE_BLIND_BEFORE_NATIVE_FAIL")
    report={
        "schema":"c3x022-P1-prospective-april16-OxF-rootorder-full64-firstTT-court-v1",
        "forecast_precommit":"c3x/ontology/c3x-022-P0-april2026-independent-ecology-source-and-prospective-forecast-precommit.md",
        "source_sha256":SOURCE_SHA,"all_legal_486_move_primitives_sha256":ATOMIC_SHA,
        "design":"RISKY_APRIL16_PROSPECTIVE_NATIVE_ROOT_CHOICE",
        "pinned_engine":"Stockfish16 68e1e9b3811e16cad014b590d7443b9063b52 Threads1 Hash16 NNUEoff depth12",
        "roles":ROLES,"order_worlds":WORLDS,
        "historical_negatives":["0.19 F19.5 FAIL","0.19 K4 0/4 FAIL",
                                "January J2/J3/J4 FAIL","PAG CPP_224 transfer FAIL"],
        "games":[]}
    for original,primitives in zip(april["selected"],atom["positions"]):
        gid=original["id"]
        need(gid==primitives["id"] and
             original["source_game_sha256"]==primitives["game_sha256"] and
             original["fen4"]==primitives["profile"]["fen4"],
             "APRIL16_BOARD_AND_CHESS_PRIMITIVES_JOIN_DRIFT")
        world,_=canonical_engine_world(original)
        clocks=game_clocks(original)
        record={"game":gid,"source_game_sha256":original["source_game_sha256"],
                "fen4":original["fen4"],"legal_root_moves":primitives["profile"]["legal_root_move_count"],
                "worlds":{}}
        baselines={}
        for order in WORLDS:
            baseline=cold(engine,world,clocks,order,"OBS")
            baselines[order]=baseline
            if order=="O":
                sham=cold(engine,world,clocks,"Z","OBS")
                need(sham["UCI"]==baseline["UCI"],"APRIL_OZ_SHAM_CHANGED_UCI")
            passive=cold(engine,world,clocks,order,"OBS",discovery=True)
            need(passive["UCI"]==baseline["UCI"],"APRIL_PASSIVE_DISCOVERY_CHANGED_NATIVE_UCI")
            decoy=cold(engine,world,clocks,order,"V",DECOY)
            need(decoy["UCI"]==baseline["UCI"] and
                 decoy["lineage_summary"]["reader_block"]==0,
                 "APRIL_TT_DECOY_CONTACT_OR_UCI_CHANGE")
            events=[e for e in passive["payload_witnesses"] if e["kind"]=="discovery"]
            need(len(events)<=2048,"APRIL_TT_DISCOVERY_LIMIT")
            order_row={
                "baseline_UCI":baseline["UCI"],
                "baseline_root_depth_leaders":root_depth_ladder(baseline["root_events"]),
                "source_writer_reader_discovery_events":len(events),
                "discovery_census_at_limit":len(events)>=2048,
                "OZ_or_source_decoy_pass":True,
                "roles":{}}
            for role in ROLES:
                pair=first_pair(events,RULES[role])
                if not pair:
                    order_row["roles"][role]={"status":"NO_SOURCE_ELIGIBLE_PAIR",
                                              "contact":False,
                                              "final_bestmove_changed":False}
                    continue
                zero=cold(engine,world,clocks,order,"V",pair["physical"],
                          tt_reader_filters=mask_filters(RULES[role],pair,"ZERO"))
                need(zero["UCI"]==baseline["UCI"] and
                     zero["lineage_summary"]["reader_block"]==0,
                     "APRIL_SELECTED_PAIR_ZERO_NOT_SHAM")
                first=cold(engine,world,clocks,order,"V",pair["physical"],
                           tt_reader_filters=mask_filters(RULES[role],pair,"FIRST"))
                blocks,proof=physical_contact(first,pair)
                changed=first["UCI"]["bestmove"]!=baseline["UCI"]["bestmove"]
                move_relation=move_micro_comparison(
                    baseline["UCI"]["bestmove"],first["UCI"]["bestmove"],primitives)
                order_row["roles"][role]={
                    "status":"DELIVERED_NATIVE_FIRST_READER" if blocks else "SELECTED_BUT_NONCONTACT",
                    "contact":bool(blocks),
                    "reader_block_events":blocks,
                    "source_native_root_move":pair["root_candidate_native"],
                    "source_root_calls":pair["root_calls"],
                    "source_physical":pair["physical"],
                    "source_writer_verified":proof,
                    "V_UCI":first["UCI"],
                    "final_bestmove_changed":changed,
                    "delivered_final_bestmove_changed":bool(blocks) and changed,
                    "changed_any_UCI_field":first["UCI"]!=baseline["UCI"],
                    "root_depth_leaders":root_depth_ladder(first["root_events"]),
                    "first_source_aligned_return_difference":first_semantic_source_split(
                        baseline["root_events"],first["root_events"]),
                    "frozen_chess_move_primitives_contrast":move_relation,
                    "cold_twice":True
                }
            record["worlds"][order]=order_row
        record["O_vs_F_bestmove_changed"]=(
            baselines["O"]["UCI"]["bestmove"]!=baselines["F"]["UCI"]["bestmove"])
        report["games"].append(record)
        print("C3X022_APRIL_NATIVE",gid,
              {o:{"bestmove":record["worlds"][o]["baseline_UCI"]["bestmove"],
                   "role_first_flip":{
                        r:record["worlds"][o]["roles"][r]["delivered_final_bestmove_changed"]
                        for r in ROLES}} for o in WORLDS},flush=True)
    def flipped(order):
        return sorted(row["game"] for row in report["games"]
                      if any(row["worlds"][order]["roles"][role].get(
                          "delivered_final_bestmove_changed",False) for role in ROLES))
    affected_o,affected_f=flipped("O"),flipped("F")
    source_contacts=sum(1 for row in report["games"] for order in WORLDS
                        for role in ROLES if row["worlds"][order]["roles"][role]["contact"])
    eligible=sum(1 for row in report["games"] for order in WORLDS
                 for role in ROLES if row["worlds"][order]["roles"][role]["status"]!="NO_SOURCE_ELIGIBLE_PAIR")
    order_disagreement=sum(row["O_vs_F_bestmove_changed"] for row in report["games"])
    summary={
        "source_games":16,"native_order_baselines":32,
        "role_cell_denominator":64,
        "eligible_source_role_cells":eligible,
        "real_first_reader_contact_cells":source_contacts,
        "O_vs_F_distinct_games_with_final_bestmove_difference":order_disagreement,
        "O_first_reader_affected_game_ids":affected_o,
        "F_first_reader_affected_game_ids":affected_f,
        "native_first_reader_affected_distinct_games":
            sorted(set(affected_o)|set(affected_f)),
        "H22_ORDER":"PASS" if order_disagreement>=1 else "FAIL",
        "H22_NATIVE":"PASS" if (affected_o or affected_f) else
                     "FAIL" if source_contacts else "INCONCLUSIVE_NO_NATIVE_CONTACT",
        "H22_CONTEXT":"PASS" if affected_o!=affected_f else "FAIL",
        "historical_March_same_sample_focal_selection":"NOT_USED",
        "all_games_in_denominator":True,
        "correlated_roles_not_independent_games":True
    }
    report["summary"]=summary
    return report

def main():
    p=argparse.ArgumentParser()
    for k in ("april","primitives","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    result=study(read_frozen(a.april,SOURCE_SHA),
                 read_frozen(a.primitives,ATOMIC_SHA),a.engine)
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_APRIL_PROSPECTIVE_FINAL_CHOICE_FORECAST_VERDICTS",
          json.dumps(result["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
