#!/usr/bin/env python3
"""C3X 0.24 P1 prospective first-TT-reader outcome against Git-literal M0-M3.

First native TT-FIRST on Aug2025 frozen games is forbidden until:
source SHA, no-treatment StageA SHA, pre-treatment forecast raw SHA, and
Git-sealed exact four-model literal UCI per game/order/role ALL agree.
No SEE Boolean is ever altered in this P1 experiment.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters,verify_selected_blocks
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder

SOURCE_SHA="76391058cae1fad8d23e3ae8556e48b63a0d991a051c59fef2df15e11c73f529"
STAGE_A_SHA="116b3c0f63be3074236982c76abd059b1dca3bb1f019cc3c10f9b03a5ac1855e"
ORIGINAL_FORECAST_SHA="8fd04b842fb9731b45b79a6dccc0526b3a21cce52f22fde0b0d00094789da4ea"
SEAL="c3x/forecasts/c3x-024-P0-Aug2025-64role-4model-literal-UCI-Git-seal-before-FIRST-20261011.json"
MODELS=("M0","M1","M2_depth11","M3")
ROLES=("STRICT","BROAD")
ORDERS=("O","F")
SCHEMA="c3x024-P1-Aug2025-prospective-real-native-first-TT-vs-Git-sealed-four-model-exact-UCI-v1"

def frozen(path,expected):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==expected,"P1_FROZEN_PRETREATMENT_INPUT_SHA_DRIFT")
    return json.loads(raw)

def gate(source,stage,forecast,seal):
    need(source["schema"]=="c3x024-P0-blind-Aug2025-broadcast16-before-any-native-treatment-v1"
         and source["treatment_outcomes_seen"] is False
         and source["source_only_no_stockfish_used"] is True,
         "C3X024_P1_NOT_ORIGINAL_ENGINEBLIND_SOURCE")
    need(stage["summary"]["distinct_source_boards"]==16
         and stage["summary"]["actual_TT_FIRST_interventions"]==0
         and stage["summary"]["actual_SEE_Boolean_interventions"]==0
         and stage["summary"]["treatment_outcomes_seen"] is False,
         "C3X024_P1_STAGEA_HAS_TREATMENT")
    need(forecast["schema"]=="c3x024-P0-Aug2025-literal-four-model-no-treatment-predictions-v1"
         and forecast["new_2025_Aug_first_reader_treatments_seen"]==0
         and forecast["new_2025_Aug_SEE_treatments_seen"]==0,
         "C3X024_P1_FORECAST_EXPOSED_TO_OUTCOMES")
    need(seal["full_forecast_original_JSON_SHA256"]==ORIGINAL_FORECAST_SHA
         and seal["source_pretreatment_JSON_SHA256"]==SOURCE_SHA
         and seal["stageA_untreated_JSON_SHA256"]==STAGE_A_SHA
         and seal["M3_positive_flips_predicted"]==0,
         "C3X024_P1_GIT_SEAL_PROVENANCE_MISMATCH")
    need(len(source["selected"])==len(stage["ecologies"]["aug2025_broadcast"]["cases"])
         ==len(forecast["cases"])==len(seal["cases"])==16,"C3X024_P1_GAME_DENOMINATOR_DRIFT")
    checked=0
    for orig,old,pred,locked in zip(source["selected"],
                                   stage["ecologies"]["aug2025_broadcast"]["cases"],
                                   forecast["cases"],seal["cases"]):
        need(orig["id"]==old["id"]==pred["game_id"]==locked["game_id"]
             and orig["source_game_sha256"]==old["source_sha256"]
             ==pred["source_game_sha256"]==locked["source_game_sha256"],
             "C3X024_P1_GAME_IDENTITY_UNSEALED")
        for order in ORDERS:
            for role in ROLES:
                observed=pred["cases"] if False else pred["root_orders"][order][role]
                lockedrole=locked["root_orders"][order]["literal_by_role"][role]
                historic=old["worlds"][order]["roles"][role]
                need(historic["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME"
                     and observed["scope"]=="SOURCE_ELIGIBLE_FROZEN"
                     and lockedrole=={m:observed[m] for m in MODELS},
                     "C3X024_P1_LITERALS_NOT_EXACTLY_PRESEALED")
                need(lockedrole["M3"]==lockedrole["M0"],
                     "C3X024_P1_ZERO_M3_POSITIVES_FROZEN_CHANGED")
                checked+=1
    need(checked==64,"C3X024_P1_EXPECTED_64_LITERAL_ROLE_CELLS")
    return checked

def cold(engine,world,clock,order,scope,role,treated):
    key=scope["physical"]["key64"];call=scope["root_calls"][0]
    kw={"fen_clocks":clock,"allow_empty_lineage":True,
        "native_use_watch":{"key64":key,"root_call":call},
        "see_watch":{"key64":key,"root_call":call,
                     "policy":"OBS","passive_ancestry":True}}
    if treated:
        pair={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
        kw["tt_reader_filters"]=mask_filters(RULES[role],pair,"FIRST")
        kwargs=(engine,world,order,"V",scope["physical"])
    else:
        kwargs=(engine,world,order,"OBS",None)
    first=play(*kwargs,**kw);second=play(*kwargs,**kw)
    need(first==second,"C3X024_P1_NATIVE_COLD_DUPLICATE_MISMATCH")
    need(not any(e.get("altered") or e.get("original")!=e.get("delivered")
                 for e in first["native_see_events"] if e["kind"]=="witness"),
         "C3X024_P1_SEE_INTERVENTION_FORBIDDEN")
    if not treated:
        need(first["lineage_summary"]["reader_block"]==0,
             "C3X024_P1_SHAM_INTERVENED")
    return first

def experiment(src,stage,forecast,locked,engine):
    gate(src,stage,forecast,locked)
    results=[]
    for s,old,pred in zip(src["selected"],stage["ecologies"]["aug2025_broadcast"]["cases"],forecast["cases"]):
        world,clock,_=native_world({**s,"source_root_legal_count":s["root_legal_move_count"]})
        case={"game_id":s["id"],"source_game_sha256":s["source_game_sha256"],
              "root_orders":{}}
        for order in ORDERS:
            reference=old["worlds"][order]
            options={}
            for role in ROLES:
                source_scope=reference["roles"][role]
                literals={m:pred["root_orders"][order][role][m] for m in MODELS}
                sham=cold(engine,world,clock,order,source_scope,role,False)
                need(sham["UCI"]==reference["baseline_UCI"],"C3X024_P1_SHAM_CHANGED_STAGEA_BASELINE")
                if role=="STRICT":
                    need(sham["native_see_events"]==reference["passive_first32_SEE_events"],
                         "C3X024_P1_STRICT_SHAM_SEE_PATH_CHANGED")
                dose=cold(engine,world,clock,order,source_scope,role,True)
                pair={k:source_scope[k] for k in ("physical","root_calls","root_candidate_native")}
                proof=verify_selected_blocks(dose,pair,RULES[role],"FIRST")
                contact=proof["blocked"]>0
                need(all(e["kind"]!="reader_block" for e in sham["blocks"]), "C3X024_SHAM_BLOCK")
                if not contact:
                    status="NO_PHYSICAL_FIRST_READER_CONTACT_HOLD"
                else:status="PHYSICAL_FIRST_READER_SOURCE_VERIFIED"
                actual=dose["UCI"]["bestmove"]
                deltas={m:None if not contact or u is None else actual==u
                        for m,u in literals.items()}
                options[role]={"status":status,"real_physical_TT_FIRST":contact,
                   "TT_reader_block_count":proof["blocked"],
                   "written_reader_integrity":proof["writer_integrity"],
                   "original_UCI":reference["baseline_UCI"],
                   "treated_UCI":dose["UCI"],
                   "exact_literal_models_precommitted":literals,
                   "literal_exact_accuracy_when_contacted":deltas,
                   "actual_bestmove_flip":actual!=reference["baseline_UCI"]["bestmove"] if contact else None,
                   "SEE_Boolean_interventions":0,
                   "original_SEE_observer_censored":reference["passive_SEE_witness_censored"],
                   "native_treated_SEE_observer_censored":any(
                     e["kind"]=="censored" for e in dose["native_see_events"]),
                   "actual_source_TT_first_and_SEE_current_node_mediation_not_proved":True,
                   "cold_exact":True}
            case["root_orders"][order]=options
        results.append(case)
        brief={f"{o}/{r}":case["root_orders"][o][r]["treated_UCI"]["bestmove"]
              for o in ORDERS for r in ROLES}
        print("C3X024_P1_NATIVE_TT_FIRST_GAME",s["id"],brief,flush=True)
    rows=[(c["game_id"],o,r,c["root_orders"][o][r])
          for c in results for o in ORDERS for r in ROLES]
    contacted=[q for q in rows if q[3]["real_physical_TT_FIRST"]]
    role_correct={m:sum(bool(q[3]["literal_exact_accuracy_when_contacted"][m])
                       for q in contacted) for m in MODELS}
    contacted_games={q[0] for q in contacted}
    game_aggregate={}
    for m in MODELS:
        vals={}
        for g in contacted_games:
            cells=[q[3] for q in contacted if q[0]==g]
            vals[str(g)]=int(any(c["literal_exact_accuracy_when_contacted"][m] for c in cells))
        game_aggregate[m]=vals
    wins=sum(game_aggregate["M3"][str(g)]>game_aggregate["M0"][str(g)]
             for g in contacted_games)
    losses=sum(game_aggregate["M3"][str(g)]<game_aggregate["M0"][str(g)]
               for g in contacted_games)
    # Precommitted M3 == M0 all predictions, so ANY such wins/losses impossible.
    need(wins==losses==0 and role_correct["M3"]==role_correct["M0"],
         "C3X024_M3_PRESEALED_NULL_IDENTITY_BROKEN")
    summary={"source_games":16,"potential_roles":64,
       "actual_physical_TT_FIRST_contact_roles":len(contacted),
       "roles_no_contact":64-len(contacted),
       "distinct_contacted_games":len(contacted_games),
       "actual_root_bestmove_flip_roles":sum(x[3]["actual_bestmove_flip"] is True for x in contacted),
       "actual_root_bestmove_flip_distinct_games":len(
           {g for g,o,r,x in contacted if x["actual_bestmove_flip"]}),
       "exact_UCI_accuracy_roles":role_correct,
       "source_game_any_correct_by_model":{m:sum(v.values()) for m,v in game_aggregate.items()},
       "game_level_M3_vs_M0_wins":wins,"game_level_M3_vs_M0_losses":losses,
       "M3_did_NOT_beat_M0":True,
       "natural_TT_SEE_mediation_proven":False,
       "M3_cannot_beat_null_due_zero_positive_predictions":True,
       "role_cells_not_independent_games":True}
    return {"schema":SCHEMA,"research":"C3X 0.24 P1","phase":"TREATED_FIRST_AFTER_ALL_GIT_LITERAL_FORECASTS",
            "frozen_source_sha256":SOURCE_SHA,"stageA_sha256":STAGE_A_SHA,
            "preintervention_forecast_sha256":ORIGINAL_FORECAST_SHA,
            "Git_literal_registry":SEAL,"source_license":"Lichess Aug2025 broadcast CC BY-SA 4.0",
            "summary":summary,"cases":results}

def main():
    a=argparse.ArgumentParser()
    for n in ("source","stagea","forecast","seal","engine","out"):
        a.add_argument("--"+n,required=True)
    opts=a.parse_args()
    content=experiment(frozen(opts.source,SOURCE_SHA),
           frozen(opts.stagea,STAGE_A_SHA),
           frozen(opts.forecast,ORIGINAL_FORECAST_SHA),
           json.loads(Path(opts.seal).read_text()),opts.engine)
    dest=Path(opts.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(content,sort_keys=True,indent=2)+"\n")
    print("C3X024_P1_PRESEALED_NATIVE_FIRST_EXACT_UCI_VERDICT",
          content["summary"],hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
