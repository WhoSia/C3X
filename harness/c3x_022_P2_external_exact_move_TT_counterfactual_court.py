#!/usr/bin/env python3
"""C3X022-P2 Stage B: execute previously literal-locked UCI forecasts, no refit.

Original TWIC and Lichess puzzle source positions, no original TWIC PGN
redistribution. Stage A selected O/F baselines and physical writer/reader
targets WITHOUT executing V. Stage B evaluates native FIRST only after Git
forecast SHA and all chess root affordances were independently sealed.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_021_P1_march_native_TT_atomic_bridge import (
    root_depth_ladder,first_semantic_source_split,move_micro_comparison)
from c3x_022_P2_two_stage_exact_move_scout import native_world,ECOLOGIES,WORLDS,ROLES,source_depth_ladder

SOURCE_SHA="ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"
PRIMITIVES_SHA="b3b4a29788c1f9dc2b4d491cd60d44ad8e6530d3d66be5d77039a6fd59cc958d"
SCHEMA="c3x022-P2-TWIC-puzzle-exact-move-counterfactual-stageB-v1"
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,
         "C3X022_P2_FROZEN_SOURCE_SHA_DRIFT_"+Path(path).name)
    return json.loads(raw)

def cold(engine,w,clock,order,mode,target=None,filters=None):
    kw={"fen_clocks":clock}
    if filters is not None:
        kw["tt_reader_filters"]=filters
    a=play(engine,w,order,mode,target,allow_empty_lineage=True,**kw)
    b=play(engine,w,order,mode,target,allow_empty_lineage=True,**kw)
    need(a==b,"P2_STAGE_B_TWO_COLD_NATIVE_RUNS_DIFFER")
    need(len(a["root_events"])<4096,"P2_STAGE_B_ROOT_TRACE_CENSORED")
    need(a["root_events"] or not a["payload_witnesses"],
         "P2_STAGE_B_TT_PAYLOAD_WITHOUT_ROOT_TRACE")
    return a

def actual_block(witness,pair):
    blocks=[x for x in witness["blocks"] if x["kind"]=="reader_block"]
    need(len(blocks)==witness["lineage_summary"]["reader_block"],
         "P2_STAGE_B_READER_COUNT_DRIFT")
    expected=pair["source_physical"]
    first_rootcall=pair["root_calls"][0]
    need(all(
         e["root_call"]==first_rootcall and
         e["root_move"]==pair["source_root_move_native"] and
         all(e[k]==expected[k] for k in ("key64","slot","epoch"))
         for e in blocks),"P2_STAGE_B_BAD_PHYSICAL_WRITER_READER_IDENTITY")
    p=verified_reader_lineage(witness)
    need(not blocks or (p["all_valid"] is True and p["count"]>=len(blocks)),
         "P2_STAGE_B_WRITER_READER_WITNESS_FAIL")
    return blocks,p

def try_role(engine,world,clock,order,role,forecast,baseline,baseline_ladder,atoms):
    if forecast["status"]=="NO_TREATMENT":
        need(forecast["predicted_UCI"] is None and
             forecast["predicted_flip"] is None,
             "P2_NONELIGIBLE_PRECOMMIT_FORGED")
        return {"status":"NO_SOURCE_ELIGIBLE_PAIR","source_contact":False}
    need(forecast["status"]=="PREDICTED_EXACT_UCI_BEFORE_TT_INTERVENTION",
         "P2_NOT_PREFORECASTED")
    need(forecast["predicted_UCI"] in {x["move"] for x in atoms["profile"]["moves"]},
         "P2_PREDICTED_MOVE_NOT_LEGAL")
    pair={"physical":forecast["source_physical"],
          "root_calls":forecast["root_calls"],
          "root_candidate_native":forecast["source_root_move_native"]}
    zero=cold(engine,world,clock,order,"V",pair["physical"],
              filters=mask_filters(RULES[role],pair,"ZERO"))
    need(zero["UCI"]==baseline and
         zero["lineage_summary"]["reader_block"]==0,
         "P2_UNMODIFIED_ZERO_NOT_SAME_AS_STAGE_A_BASELINE")
    first=cold(engine,world,clock,order,"V",pair["physical"],
               filters=mask_filters(RULES[role],pair,"FIRST"))
    blocks,proof=actual_block(first,forecast)
    changed=first["UCI"]["bestmove"]!=baseline["bestmove"]
    delivered=bool(blocks)
    exact=first["UCI"]["bestmove"]==forecast["predicted_UCI"] if delivered else None
    actual_move=first["UCI"]["bestmove"]
    target_ladder=source_depth_ladder(first["root_events"])
    shared_depths=[d for d in range(1,13)
                   if str(d) in baseline_ladder and str(d) in target_ladder]
    observed_changed_depths=[
        depth for depth in shared_depths
        if baseline_ladder[str(depth)]["native_leader"]!=target_ladder[str(depth)]["native_leader"]]
    return {
        "status":"REAL_NATIVE_READER_BLOCK_DELIVERED" if delivered else
                 "SELECTED_BUT_NONCONTACT",
        "source_contact":delivered,
        "source_reader_block_count":len(blocks),
        "verified_writer_reader":proof,
        "actual_blocks":blocks,
        "first_physical_target":forecast["source_physical"],
        "first_source_root_calls":forecast["root_calls"],
        "source_root_native":forecast["source_root_move_native"],
        "registered_exact_UCI_forecast":forecast["predicted_UCI"],
        "registered_binary_flip_forecast":forecast["predicted_flip"],
        "actual_post_intervention_UCI":first["UCI"],
        "actual_post_intervention_bestmove":actual_move,
        "exact_forecast_correct_if_contact":exact,
        "actual_final_move_flip_if_contact":changed if delivered else None,
        "binary_flip_forecast_correct_if_contact":
            forecast["predicted_flip"]==changed if delivered else None,
        "majority_no_flip_baseline_UCI":baseline["bestmove"],
        "majority_no_flip_correct_if_contact":not changed if delivered else None,
        "actual_chess_move_microcontrast":move_micro_comparison(
            baseline["bestmove"],actual_move,atoms),
        "depthwise_actual_root_leader":target_ladder,
        "depthwise_source_root_leader_before_TT":baseline_ladder,
        "changed_root_leader_depths":observed_changed_depths,
        "earliest_root_leader_depth_changed":observed_changed_depths[0] if observed_changed_depths else None,
        "shared_observable_root_depths":shared_depths,
        "missing_root_depths_due_to_source_stop_or_trace":
            [d for d in range(1,13) if d not in shared_depths],
        "source_event_alignment_limit":"Without a fully baseline-recorded candidate trace in stage A, root-call-specific child event causal attribution beyond the depth leader is not claimed.",
        "cold_repeated_exactly":True
    }

def evaluate(d,forecast,primitive,engine):
    need(forecast["schema"]=="c3x022-P2-cross-ecology-literal-specific-UCI-forecast-stageA-v1",
         "STAGE_A_SCHEMA_DRIFT")
    need(forecast["summary"]["any_TT_V_intervention_performed"] is False,
         "STAGE_A_LEAKS_V_TO_STAGE_B")
    need(primitive["phase"]=="ALL_LEGAL_BOARD_TRANSITIONS_FROZEN_BEFORE_NATIVE_O_F",
         "CHESS_PRIMITIVES_NOT_PREENGINE")
    result={"schema":SCHEMA,"pre_registered_rule":"CROSS_ORDER_RESTORATION_V1",
            "per_ecology":{},"source_sha256":SOURCE_SHA,
            "chess_primitives_sha256":PRIMITIVES_SHA}
    for eco in ECOLOGIES:
        src=d["ecologies"][eco]["selected"]
        pre=forecast["ecologies"][eco]["selected"]
        atoms=primitive["ecologies"][eco]["selected"]
        need(len(src)==len(pre)==len(atoms)==16,
             "P2_TWIC_PUZZLE_16_DENOMINATOR")
        cases=[]
        for orig,old,atom in zip(src,pre,atoms):
            gid=orig["id"]
            need(gid==old["id"]==atom["id"] and
                 orig["source_game_sha256"]==old["game_sha256"]==
                 atom["source_game_sha256"],
                 "P2_TWO_STAGE_CHESS_IDENTITY_MISMATCH")
            w,clock,ep=native_world(orig)
            row={"game":gid,"source_game_sha256":orig["source_game_sha256"],
                 "worlds":{}}
            for order in WORLDS:
                world_forecast=old["worlds"][order]
                base=world_forecast["baseline_UCI"]
                # Before any suppression, verify same-world impossible TT target
                # is a no-contact baseline. This is not a separate prediction.
                decoy=cold(engine,w,clock,order,"V",DECOY)
                need(decoy["UCI"]==base and
                     decoy["lineage_summary"]["reader_block"]==0,
                     "P2_DECOY_V_ALREADY_MOVES_CHESS_BESTMOVE")
                roles={}
                for role in ROLES:
                    roles[role]=try_role(engine,w,clock,order,role,
                                         world_forecast["roles"][role],
                                         base,world_forecast["root_depth_ladder"],atom)
                row["worlds"][order]={"baseline_UCI":base,
                                     "source_decoy_equal":True,
                                     "roles":roles}
            cases.append(row)
            print("C3X022_P2_STAGE_B_ACTUAL",eco,gid,
                  {order:{role:(r["status"],r.get("actual_post_intervention_bestmove"),
                                    r.get("exact_forecast_correct_if_contact"))
                          for role,r in row["worlds"][order]["roles"].items()}
                   for order in WORLDS},flush=True)
        contacts=[r for row in cases for world in row["worlds"].values()
                  for r in world["roles"].values() if r["source_contact"]]
        predicted_flip=sum(r["registered_binary_flip_forecast"] for r in contacts)
        flips=sum(r["actual_final_move_flip_if_contact"] for r in contacts)
        tp=sum(r["registered_binary_flip_forecast"] and r["actual_final_move_flip_if_contact"]
               for r in contacts)
        fp=sum(r["registered_binary_flip_forecast"] and not r["actual_final_move_flip_if_contact"]
               for r in contacts)
        fn=sum(not r["registered_binary_flip_forecast"] and r["actual_final_move_flip_if_contact"]
               for r in contacts)
        tn=sum(not r["registered_binary_flip_forecast"] and not r["actual_final_move_flip_if_contact"]
               for r in contacts)
        actual_flipped_games=sorted({row["game"] for row in cases
            for world in row["worlds"].values() for r in world["roles"].values()
            if r.get("actual_final_move_flip_if_contact")})
        summary={
            "game_denominator":16,"potential_order_role_cells":64,
            "selected_eligible_role_cells":sum(
                r["status"]!="NO_SOURCE_ELIGIBLE_PAIR" for row in cases
                for world in row["worlds"].values() for r in world["roles"].values()),
            "actual_reader_contact_role_cells":len(contacts),
            "actual_flip_cells":flips,"actual_flip_distinct_games":actual_flipped_games,
            "predicted_flip_cells":predicted_flip,
            "literal_exact_move_correct_contacts":sum(r["exact_forecast_correct_if_contact"] for r in contacts),
            "majority_no_change_correct_contacts":sum(r["majority_no_flip_correct_if_contact"] for r in contacts),
            "TP":tp,"FP":fp,"FN":fn,"TN":tn,
            "positive_flip_precision":tp/(tp+fp) if tp+fp else None,
            "positive_flip_recall":tp/(tp+fn) if tp+fn else None,
            "specific_move_accurate_when_actually_flipped":sum(
                r["exact_forecast_correct_if_contact"]
                for r in contacts if r["actual_final_move_flip_if_contact"]),
            "not_independent_role_cells":True,
            "science_verdict":"EXACT_MOVE_MODEL_FALSIFIED_IN_ANY_WRONG_CONTACT_CELL" if
               any(not r["exact_forecast_correct_if_contact"] for r in contacts)
               else "ALL_DELIVERED_EXACT_PREDICTIONS_MATCHED" if contacts
               else "NO_TREATMENT_DELIVERED",
        }
        result["per_ecology"][eco]={"summary":summary,"cases":cases}
    return result

def main():
    a=argparse.ArgumentParser()
    for field in ("source","stage-a","stage-a-sha","primitives","engine","out"):
        a.add_argument("--"+field,required=True)
    args=a.parse_args()
    report=evaluate(frozen(args.source,SOURCE_SHA),
                    frozen(args.stage_a,args.stage_a_sha),
                    frozen(args.primitives,PRIMITIVES_SHA),args.engine)
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    for eco,result in report["per_ecology"].items():
        print("C3X022_P2_STAGE_B_ECOLOGY_EXACT_UCI_VERDICT",
              eco,json.dumps(result["summary"],sort_keys=True),flush=True)
    print("C3X022_P2_STAGE_B_EVIDENCE_SHA",
          hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
