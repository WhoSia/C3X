#!/usr/bin/env python3
"""C3X022 P2-R1: SHA-frozen 16 TWIC1664 native FIRST TT consumer tests.

M0/M1/M2 exact UCI forecasts from BEFORE TT treatment; source-aligned physical
key+slot+epoch and writer+reader; instrumented *actual* native TT value-use and
cutoff watchers separately from mere TT probe or physical block.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_021_P1_march_native_TT_atomic_bridge import first_semantic_source_split
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_022_P2_R1_depth11_survivor_exact_forecast_stageA import SOURCE_SHA,PRIMITIVE_SHA

ROLES=("STRICT","BROAD")
WORLDS=("O","F")
SCHEMA="c3x022-P2-R1-TWIC1664-native-TT-real-valueuse-cutoff-SEE-chess-survivor-v1"
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def source_file(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,"P2_R1_UNSEALED_SOURCE_OR_PREDICTION")
    return json.loads(raw)

def cold(engine,world,clock,order,mode,target=None,filters=None,watch=None):
    opts={"fen_clocks":clock,"allow_empty_lineage":True}
    if filters is not None:opts["tt_reader_filters"]=filters
    if watch is not None:opts["native_use_watch"]=watch
    x=play(engine,world,order,mode,target,**opts)
    y=play(engine,world,order,mode,target,**opts)
    need(x==y,"NEW_TWIC1664_COLD_REPRODUCIBILITY")
    need(len(x["root_events"])<4096,"NATIVE_ROOT_TRACE_CENSORED")
    return x

def exact_block(x,forecast):
    physical=forecast["physical"]
    calls=forecast["root_calls"]
    move=forecast["root_candidate_native"]
    blocked=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    need(len(blocked)==x["lineage_summary"]["reader_block"],
         "PHYSICAL_SOURCE_READER_BLOCK_COUNT_DRIFT")
    need(all(e["root_call"]==calls[0] and e["root_move"]==move and
             all(e[k]==physical[k] for k in ("key64","slot","epoch"))
             for e in blocked),"WRONG_TT_PHYSICAL_KEY_SLOT_EPOCH_ROOTCALL_MOVE")
    lineage=verified_reader_lineage(x)
    need(not blocked or (lineage["all_valid"] and lineage["count"]>=len(blocked)),
         "WRITER_TO_READERS_RAW_VALUE_PROOF_FAIL")
    return blocked,lineage

def scan(source,primitives,stageA,engine):
    need(stageA["schema"]=="c3x022-P2-R1-TWIC1664-stageA-three-exact-UCI-model-forecasts-v1",
         "STAGEA_NOT_SEALED_OR_WRONG_SCHEMA")
    need(stageA["summary"]["FIRST_TT_interventions_performed"]==0,
         "STAGE_A_INTERVENTION_LEAK")
    need(len(stageA["cases"])==len(source["selected"])==len(primitives["positions"])==16,
         "SIXTEEN_GAMES_PRESERVED")
    result={"schema":SCHEMA,"source_sha256":SOURCE_SHA,
            "chess_legal_exchange_sha256":PRIMITIVE_SHA,
            "stageA_exact_pred_sha256":None,"games":[]}
    for row,prev,chessfacts in zip(source["selected"],stageA["cases"],primitives["positions"]):
        need(row["id"]==prev["id"]==chessfacts["id"] and
             row["source_game_sha256"]==prev["game_sha256"]==chessfacts["source_game_sha256"],
             "SOURCE_TO_FORECAST_TO_LEGAL_CHESS_ID_MISMATCH")
        world,clock,_=native_world(row)
        legal_moves={m["UCI"]:m for m in chessfacts["legal_exchange_tree"]}
        case={"id":row["id"],"game_sha256":row["source_game_sha256"],"orders":{}}
        for order in WORLDS:
            prior=prev["worlds"][order]
            base=prior["baseline_UCI"]
            zero=cold(engine,world,clock,order,"V",DECOY)
            need(zero["UCI"]==base and
                 zero["lineage_summary"]["reader_block"]==0,
                 "PRECOMMITTED_STAGE_A_BASELINE_OR_DECOY_DRIFT")
            roles={}
            for role in ROLES:
                f=prior["role_forecasts"][role]
                if f["status"] in ("NO_TREATMENT","HOLD_CENSORED_NO_FIRST_SOURCE_PAIR"):
                    roles[role]={"status":"NO_ELIGIBLE_TT_PAIR" if f["status"]=="NO_TREATMENT" else "HOLD_CENSORED_DISCOVERY","contact":False}
                    continue
                triple=f["physical"]
                pair={"physical":triple,"root_calls":f["root_calls"],
                      "root_candidate_native":f["root_candidate_native"]}
                m0,m1,m2=f["M0"],f["M1"],f["M2"]
                need(all(x in legal_moves for x in (m0,m1,m2)),
                     "REGISTERED_EXACT_UCI_NOT_LEGAL")
                watched={"key64":triple["key64"],"root_call":f["root_calls"][0]}
                # Passive native watcher only; precommitted baseline must not change.
                baseline=cold(engine,world,clock,order,"OBS",watch=watched)
                need(baseline["UCI"]==base,"NATIVE_USE_WATCH_INTERFERES_WITH_BASELINE")
                phantom=cold(engine,world,clock,order,"V",triple,
                             filters=mask_filters(RULES[role],pair,"ZERO"),watch=watched)
                need(phantom["UCI"]==base and
                     phantom["lineage_summary"]["reader_block"]==0,
                     "ZERO_CONTACT_SHAM_CHANGED_UCI")
                treated=cold(engine,world,clock,order,"V",triple,
                             filters=mask_filters(RULES[role],pair,"FIRST"),watch=watched)
                blocks,proof=exact_block(treated,f)
                contact=bool(blocks)
                actual=treated["UCI"]["bestmove"]
                before=source_depth_ladder(baseline["root_events"])
                after=source_depth_ladder(treated["root_events"])
                shared=[d for d in range(1,13) if str(d) in before and str(d) in after]
                leader_diff=[d for d in shared if before[str(d)]["native_leader"]!=after[str(d)]["native_leader"]]
                split=first_semantic_source_split(baseline["root_events"],treated["root_events"])
                roles[role]={
                    "status":"SOURCE_PHYSICAL_FIRST_READER_DELIVERED" if contact else "NONCONTACT",
                    "contact":contact,
                    "physical":triple,"rootcalls":f["root_calls"],
                    "exact_reader_blocks":blocks,"native_writer_proof":proof,
                    "baseline_UCI":base,"treated_UCI":treated["UCI"],
                    "M0_exact_UCI":m0,"M1_exact_UCI":m1,"M2_exact_UCI":m2,
                    "prediction_exact_correct_if_contact":{key:(guess==actual if contact else None)
                          for key,guess in (("M0",m0),("M1",m1),("M2",m2))},
                    "predicted_flip_if_contact":{key:(guess!=base["bestmove"] if contact else None)
                          for key,guess in (("M0",m0),("M1",m1),("M2",m2))},
                    "actual_first_reader_flip":(actual!=base["bestmove"] if contact else None),
                    "actual_root_bestmove":actual,
                    "registered_depth11_survivor":f["M2_depth11_legal_candidate"],
                    "registered_baseline_exchange_risk":f.get("baseline_legal_recapture_exposure"),
                    "registered_depth11_exchange_risk":f.get("depth11_legal_recapture_exposure"),
                    "source_blind_actual_move_legal_recapture_risk":
                        legal_moves[actual]["responder_optimal_legal_exchange_gain"],
                    "source_blind_actual_move_first_recapture_count":
                        legal_moves[actual]["legal_first_destination_capture_count"],
                    "source_blind_actual_move_piece":legal_moves[actual]["mover_piece"],
                    "native_baseline_watch_value_events":baseline["native_tt_value_uses"],
                    "native_FIRST_watch_value_events":treated["native_tt_value_uses"],
                    "native_watch_kind_baseline":sorted({x.get("kind","") for x in baseline["native_tt_value_uses"]}),
                    "native_watch_kind_FIRST":sorted({x.get("kind","") for x in treated["native_tt_value_uses"]}),
                    "changed_root_leader_depths":leader_diff,
                    "earliest_root_leader_divergence":leader_diff[0] if leader_diff else None,
                    "shared_root_depths":shared,
                    "first_semantic_root_source_difference":split,
                    "cold_repeated_every_native_arm":True
                }
            case["orders"][order]={"roles":roles}
        result["games"].append(case)
        print("C3X022_P2_R1_NEW_NATIVE_CHOICE",row["id"],
              {order:{role:(r["status"],r.get("actual_root_bestmove"),
                              r.get("prediction_exact_correct_if_contact"))
                      for role,r in case["orders"][order]["roles"].items()}
               for order in WORLDS},flush=True)
    roles=[(g["id"],order,role,r) for g in result["games"]
           for order,v in g["orders"].items() for role,r in v["roles"].items()]
    eligible=[x for x in roles if x[3]["status"]!="NO_ELIGIBLE_TT_PAIR"]
    contacts=[x for x in eligible if x[3]["contact"]]
    flipped=[x for x in contacts if x[3]["actual_first_reader_flip"]]
    summary={"source_games":16,"role_order_cells":64,
             "eligible_source_cells":len(eligible),"actual_source_first_reader_contact_cells":len(contacts),
             "actual_flip_role_cells":len(flipped),
             "actual_flip_distinct_game_ids":sorted({x[0] for x in flipped}),
             "verified_native_watched_value_event_cells":
                 sum(bool(x[3]["native_baseline_watch_value_events"]) for x in contacts),
             "model_metrics":{}}
    for model in ("M0","M1","M2"):
        accuracy=sum(x[3]["prediction_exact_correct_if_contact"][model] for x in contacts)
        positive_correct=sum(x[3]["prediction_exact_correct_if_contact"][model] for x in flipped)
        tp=sum(x[3]["predicted_flip_if_contact"][model] and x[3]["actual_first_reader_flip"] for x in contacts)
        fp=sum(x[3]["predicted_flip_if_contact"][model] and not x[3]["actual_first_reader_flip"] for x in contacts)
        fn=sum(not x[3]["predicted_flip_if_contact"][model] and x[3]["actual_first_reader_flip"] for x in contacts)
        tn=sum(not x[3]["predicted_flip_if_contact"][model] and not x[3]["actual_first_reader_flip"] for x in contacts)
        summary["model_metrics"][model]={
            "exact_correct_contact_role_cells":accuracy,
            "positive_actual_flips_with_exact_UCI_correct":positive_correct,
            "TP":tp,"FP":fp,"FN":fn,"TN":tn,
            "positive_precision":tp/(tp+fp) if tp+fp else None,
            "positive_recall":tp/(tp+fn) if tp+fn else None}
    summary["M2_vs_M0_game_wins"]=sum(
        sum(g["orders"][o]["roles"][r].get("prediction_exact_correct_if_contact",{}).get("M2") is True
          for o in WORLDS for r in ROLES) >
        sum(g["orders"][o]["roles"][r].get("prediction_exact_correct_if_contact",{}).get("M0") is True
          for o in WORLDS for r in ROLES)
        for g in result["games"])
    summary["M2_vs_M0_game_losses"]=sum(
        sum(g["orders"][o]["roles"][r].get("prediction_exact_correct_if_contact",{}).get("M2") is True
          for o in WORLDS for r in ROLES) <
        sum(g["orders"][o]["roles"][r].get("prediction_exact_correct_if_contact",{}).get("M0") is True
          for o in WORLDS for r in ROLES)
        for g in result["games"])
    summary["M2_scientific_rule_verdict"]=(
        "PILOT_POSITIVE" if summary["M2_vs_M0_game_wins"]>summary["M2_vs_M0_game_losses"]
        and summary["model_metrics"]["M2"]["positive_actual_flips_with_exact_UCI_correct"]>0
        else "FAIL_NO_GAIN_OR_NO_CORRECT_POSITIVE")
    summary["role_cells_not_independent_games"]=True
    result["summary"]=summary
    return result

def main():
    a=argparse.ArgumentParser()
    for k in ("source","primitives","stagea","stagea-sha","engine","out"):a.add_argument("--"+k,required=True)
    q=a.parse_args()
    d=scan(source_file(q.source,SOURCE_SHA),source_file(q.primitives,PRIMITIVE_SHA),
           source_file(q.stagea,q.stagea_sha),q.engine)
    d["stageA_exact_pred_sha256"]=q.stagea_sha
    dest=Path(q.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_R1_NEW_TWIC1664_THREE_RIVAL_MODEL_SCIENTIFIC_VERDICT",d["summary"],
          hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
