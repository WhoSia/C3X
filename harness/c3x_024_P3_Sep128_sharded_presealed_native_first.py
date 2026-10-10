#!/usr/bin/env python3
"""C3X 0.24 P3 128-game prospective TT FIRST only AFTER full literal human Git seal.
Shard by predeclared contiguous source-game positions, never by model predictions.
No SEE Boolean intervention. Every contacted role includes two cold SHAM and two treated runs.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,verify_selected_blocks
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_024_P1_newAug2025_TT_FIRST_vs_four_presealed_literal_models import cold
from c3x_024_P3_preFIRST_literal_512role_integrity_gate import read,locked,SRC_SHA,STAGE_SHA,FORECAST_SHA,MODELS,ORDERS,ROLES
SCHEMA="c3x024-P3-128game-human-Git-presealed-five-model-physical-TT-FIRST-shard-v1"
def run(source,stage,forecast,seal,engine,shard):
    pre=locked(source,stage,forecast,seal)
    need(0<=shard<4,"P3_SHARD_RANGE")
    start=shard*32;stop=start+32
    cases=[]
    for s,old,pred in zip(source["selected"][start:stop],
                          stage["ecologies"]["sep2025_broadcast"]["cases"][start:stop],
                          forecast["cases"][start:stop]):
        world,clock,_=native_world({**s,"source_root_legal_count":s["root_legal_move_count"]})
        parts=[]
        for order in ORDERS:
            reference=old["worlds"][order]
            for role in ROLES:
                scope=reference["roles"][role]
                fc=pred["root_orders"][order][role]
                literals={m:fc[m] for m in MODELS}
                if fc["status"]!="FROZEN_SOURCE_ELIGIBLE":
                    need(scope["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME","P3_NONELIGIBLE_BAD_PRELABEL")
                    parts.append({"root_order":order,"role":role,
                        "status":"PRESEALED_INELIGIBLE_NO_FIRST_READER",
                        "predicted":literals,"sham_bestmove":reference["baseline_UCI"]["bestmove"],
                        "treated_bestmove":None,"correct":{m:None for m in MODELS},
                        "source_TT_first_contact":False,"actual_root_flip":None,"cold_pairs_checked":0})
                    continue
                need(scope["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME","P3_MISSING_NATIVE_PAIR")
                control=cold(engine,world,clock,order,scope,role,False)
                need(control["UCI"]==reference["baseline_UCI"],
                     "P3_SHAM_NOT_EXACT_ORIGINAL_PRECOMMITTED_STAGE_A")
                if role=="STRICT":
                    need(control["native_see_events"]==reference["passive_first32_SEE_events"],
                         "P3_STRICT_PASSIVE_SOURCE_SEE_PATH_CHANGED")
                dose=cold(engine,world,clock,order,scope,role,True)
                target={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
                proof=verify_selected_blocks(dose,target,RULES[role],"FIRST")
                contact=proof["blocked"]>0
                best=dose["UCI"]["bestmove"]
                scores={m:(best==lit if contact and lit is not None else None)
                        for m,lit in literals.items()}
                parts.append({"root_order":order,"role":role,
                    "status":"REAL_NATIVE_PHYSICAL_TT_FIRST" if contact else "NO_CONTACT_HOLD",
                    "predicted":literals,"sham_bestmove":control["UCI"]["bestmove"],
                    "treated_bestmove":best,"correct":scores,
                    "source_TT_first_contact":contact,
                    "selected_native_reader_blocks":proof["blocked"],
                    "source_physical_writer_integrity":proof["writer_integrity"],
                    "actual_root_flip":best!=control["UCI"]["bestmove"] if contact else None,
                    "source_SEE_Boolean_flips":0,
                    "cold_pairs_checked":2,
                    "source_preFIRST_SEE_prefix_censored":reference["passive_SEE_witness_censored"]})
        need(len(parts)==4,"P3_NOT_FOUR_ROLES_PER_GAME")
        cases.append({"game_id":s["id"],"roles":parts})
        print("C3X024_P3_NATIVE_FIRST_SEALED_GAME",s["id"],
              {x["root_order"]+"/"+x["role"]:x["status"] for x in parts},flush=True)
    need(len(cases)==32 and cases[0]["game_id"]==start+1
         and cases[-1]["game_id"]==stop,"P3_SHARD_SEQUENCE_WRONG")
    entries=[x for case in cases for x in case["roles"]]
    contact=sum(x["status"]=="REAL_NATIVE_PHYSICAL_TT_FIRST" for x in entries)
    held=sum(x["status"]=="PRESEALED_INELIGIBLE_NO_FIRST_READER" for x in entries)
    no_contact=sum(x["status"]=="NO_CONTACT_HOLD" for x in entries)
    eligible=contact+no_contact
    return {"schema":SCHEMA,"shard":shard,"case_range":[start+1,stop],
      "model_forecast_source_SHA256":FORECAST_SHA,
      "human_Git_seal":"c3x/forecasts/c3x-024-P3-Sep2025-128game-512role-five-model-literal-UCI-before-FIRST-human-Git-seal-20261011.json",
      "original_source_JSON_SHA256":SRC_SHA,"untreated_stageA_SHA256":STAGE_SHA,
      "source_games":32,"potential_roles":128,
      "presealed_eligible_roles":eligible,"presealed_HOLD_roles":held,
      "source_real_TT_FIRST_contact_roles":contact,"source_NO_CONTACT_HOLD":no_contact,
      "model_names":list(MODELS),"treated_SEE_Boolean_flips":0,
      "source_chess_license":"Lichess 2025-09 broadcast CC BY-SA 4.0",
      "source_original_PGN_FEN_player_names_excluded":True,
      "not_a_natural_TT_SEE_mediation_estimate":True,
      "all_cells":cases}
def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","forecast","seal","engine","out"):p.add_argument("--"+k,required=True)
    p.add_argument("--shard",type=int,required=True)
    a=p.parse_args()
    src=read(a.source,SRC_SHA)
    stage=read(a.stagea,STAGE_SHA)
    fore=read(a.forecast,FORECAST_SHA)
    seal=json.loads(Path(a.seal).read_text())
    payload=run(src,stage,fore,seal,a.engine,a.shard)
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("C3X024_P3_PRESEALED_NATIVE_TT_FIRST_SHARD_COMPLETE",
          {"shard":a.shard,"games":32,"eligible":payload["presealed_eligible_roles"],
           "contact":payload["source_real_TT_FIRST_contact_roles"],
           "hold":payload["presealed_HOLD_roles"],"no_contact":payload["source_NO_CONTACT_HOLD"]},
          hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
