#!/usr/bin/env python3
"""P3 exact source/untreated/forecast and human-Git 512-role pre-FIRST lock.
Read only. No native chess search; no treated outcome.
"""
import argparse,hashlib,json
from pathlib import Path
SRC_SHA="ee8265f96b055645428f2fa87b36647e1931c86c848db5725a8b0ec63596dacb"
STAGE_SHA="1c9f265b507712069442956c3ecf0dcdcb7e9abbeaaff4b683ba9beb263d3b09"
FORECAST_SHA="c402a6808bcaa2d73ec58632f87aa4ba7e8be0577b051b85e0a5610750eb1887"
SEAL_PATH="c3x/forecasts/c3x-024-P3-Sep2025-128game-512role-five-model-literal-UCI-before-FIRST-human-Git-seal-20261011.json"
MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2")
ROLES=("STRICT","BROAD")
ORDERS=("O","F")
def read(path,expected):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=expected:
        raise ValueError("P3_PRE_FIRST_SOURCE_UNTREATED_FORECAST_SHA_DRIFT_"+str(path))
    return json.loads(b)
def locked(src,stage,forecast,seal):
    if src["schema"]!="c3x024-P3-blind-Sep2025-broadcast128-before-any-native-treatment-v1" or not src["source_only_no_stockfish_used"] or src["treatment_outcomes_seen"]:
        raise ValueError("P3_SOURCE_ENGINE_BLIND_FORBIDDEN")
    if stage["source_sha256"]!=SRC_SHA or stage["summary"]["actual_TT_FIRST_interventions"]!=0 or stage["summary"]["actual_SEE_Boolean_interventions"]!=0 or stage["summary"]["treatment_outcomes_seen"]:
        raise ValueError("P3_STAGE_A_NOT_UNTREATED")
    if stage["summary"]["eligible_source_first_reader_role_cells"]!=501:
        raise ValueError("P3_EXPECTED_PRE_FIRST_ELIGIBLE_501")
    if forecast["schema"]!="c3x024-P3-September2025-128-source-only-untreated-five-model-exact-UCI-FORECAST-NO-TREATMENT-v1" or forecast["TT_FIRST_interventions_seen"] or forecast["SEE_boolean_interventions_seen"]:
        raise ValueError("P3_FORECAST_SEEN_TREATMENT")
    if seal["schema"]!="c3x024-P3-Sept2025-128game-512role-five-model-exact-UCI-HUMAN-GIT-PRE-FIRST-SEAL-v1" or seal["sealed_phase"]!="BEFORE_FIRST_TT_INTERVENTION_ZERO_TREATED_OUTCOMES":
        raise ValueError("P3_HUMAN_GIT_FULL_LITERAL_PRESEAL_MISSING")
    for k,e in (("original_source_JSON_SHA256",SRC_SHA),("stageA_untreated_full_JSON_SHA256",STAGE_SHA),("forecast_untreated_full_JSON_SHA256",FORECAST_SHA)):
        if seal[k]!=e:raise ValueError("P3_SEALED_RAW_SHA_WRONG_"+k)
    cases=seal["ordered_games_literal_rows"]
    natives=stage["ecologies"]["sep2025_broadcast"]["cases"]
    if len(cases)!=len(src["selected"]) or len(cases)!=len(forecast["cases"]) or len(cases)!=len(natives) or len(cases)!=128:
        raise ValueError("P3_128_GAMES_NOT_ALL_REGISTERED")
    eligible=flips_v1=flips_v2=0
    for idx,(locked_row,source_row,native_row,fc) in enumerate(zip(cases,src["selected"],natives,forecast["cases"]),1):
        gid,sh,rows=locked_row
        if gid!=idx or gid!=source_row["id"] or gid!=native_row["id"] or gid!=fc["game_id"] or sh!=source_row["source_game_sha256"] or sh!=native_row["source_sha256"] or sh!=fc["source_game_sha256"]:
            raise ValueError("P3_SEALED_SOURCE_GAME_ID_OR_HASH_DRIFT")
        if len(rows)!=4:raise ValueError("P3_ROLE_DENOMINATOR")
        for row,(order,role) in zip(rows,((o,r) for o in ORDERS for r in ROLES)):
            target=fc["root_orders"][order][role]
            source_scope=native_row["worlds"][order]["roles"][role]
            required=[order,role,target["status"],*(target[m] for m in MODELS),int(target["M3_v1_trigger"]),int(target["M3_v2_trigger"])]
            if row!=required:raise ValueError("P3_EXACT_LITERAL_DIFFERENCE_FROM_HUMAN_GIT_SEAL")
            if target["status"]=="FROZEN_SOURCE_ELIGIBLE":
                if source_scope["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":raise ValueError("P3_PHYSICAL_SCOPE_MISSING")
                eligible+=1
                flips_v1+=int(target["M3_v1"]!=target["M0"])
                flips_v2+=int(target["M3_v2"]!=target["M0"])
            else:
                if source_scope["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME" or any(target[m] is not None for m in MODELS):
                    raise ValueError("P3_HOLD_MISLABELED_ELIGIBLE")
    if (eligible,flips_v1,flips_v2)!=(501,0,1) or (seal["eligible_first_reader_role_cells"],seal["M3_v1_predicted_flips"],seal["M3_v2_predicted_flips"])!=(501,0,1):
        raise ValueError("P3_M3V2_PRETREATMENT_ONE_FLIP_DRIFT")
    return {"source_games":128,"all_role_rows":512,"eligible":eligible,"role_HOLD":11,"M3_v1_predicted_flips":0,"M3_v2_predicted_flips":1,"forecast_SHA256":FORECAST_SHA,"first_treatment_executed":False}
def main():
    p=argparse.ArgumentParser()
    for s in ("source","stagea","forecast","seal"):p.add_argument("--"+s,required=True)
    a=p.parse_args()
    result=locked(read(a.source,SRC_SHA),read(a.stagea,STAGE_SHA),read(a.forecast,FORECAST_SHA),json.loads(Path(a.seal).read_text()))
    print("C3X024_P3_HUMAN_GIT_512ROLE_PRE_FIRST_LITERAL_GATE_PASS",result,flush=True)
if __name__=="__main__":main()
