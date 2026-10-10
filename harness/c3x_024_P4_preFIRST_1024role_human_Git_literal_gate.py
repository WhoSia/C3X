#!/usr/bin/env python3
"""July256 all 1,024 exact-UCI six-model rows, human Git pre-FIRST barrier.
Receipt original source and StageA SHA; treated data forbidden.
"""
import argparse,hashlib,json
from pathlib import Path
SOURCE_SHA="d2c50a1293e68c3feb8571d1ee1be6ba1a7ee539a12dd1a98378adfa9b54fb58"
PRENATIVE_REGISTRY="c3x/forecasts/c3x-024-P4-July2025-256-source-game-SHA-human-Git-seal-before-native-20261011.json"
MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2","M4_survivor")
ORDERS=("O","F")
ROLES=("STRICT","BROAD")
SEAL="c3x/forecasts/c3x-024-P4-July2025-256game-1024role-six-model-literal-UCI-before-FIRST-human-Git-seal-20261011.json"
def read(path,expected=None):
    raw=Path(path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if expected is not None and digest!=expected:
        raise ValueError("P4_ORIGINAL_SHA_MISMATCH_"+str(path))
    return json.loads(raw),digest
def locked(source,stage,forecast,seal):
    if source["schema"]!="c3x024-P4-blind-July2025-broadcast256-before-any-native-treatment-v1" or source["source_fen_count"]!=256 or source["TT_FIRST_interventions"]!=0 or source["SEE_forced_interventions"]!=0:
        raise ValueError("P4_SOURCE_FROZEN_ENGINEBLIND_UNTRUSTED")
    if stage["source_sha256"]!=SOURCE_SHA or stage["summary"]["actual_TT_FIRST_interventions"]!=0 or stage["summary"]["actual_SEE_Boolean_interventions"]!=0 or stage["summary"]["treatment_outcomes_seen"]:
        raise ValueError("P4_STAGEA_MUST_BE_UNTREATED")
    if stage["summary"]["distinct_source_boards"]!=256 or stage["summary"]["potential_role_cells"]!=1024:
        raise ValueError("P4_STAGEA_DENOMINATOR_WRONG")
    if forecast["schema"]!="c3x024-P4-July2025-256-source-only-untreated-six-model-exact-UCI-FORECAST-NO-TREATMENT-v1" or forecast["TT_FIRST_interventions_seen"]!=0 or forecast["SEE_boolean_interventions_seen"]!=0:
        raise ValueError("P4_TREATMENT_SEEN_BEFORE_FORECAST")
    if seal["schema"]!="c3x024-P4-July2025-256games-1024role-six-model-HUMAN_GIT_literal-before-FIRST-v1" or seal["phase"]!="BEFORE_ANY_JULY_NATIVE_TT_FIRST_TREATED_OUTCOME":
        raise ValueError("P4_FULL_HUMAN_GIT_EXACT_UCI_LITERAL_SEAL_MISSING")
    if seal["source_JSON_SHA256"]!=SOURCE_SHA:
        raise ValueError("P4_PRECOMMIT_SOURCE_JSON_SHA_WRONG")
    reg=json.loads(Path(PRENATIVE_REGISTRY).read_text())
    cases=seal["ordered_games_literal_rows"]
    originals=source["selected"]
    base=stage["ecologies"]["july2025_broadcast"]["cases"]
    fore=forecast["cases"]
    if not len(cases)==len(originals)==len(base)==len(fore)==256:
        raise ValueError("P4_256_GAME_SOURCES_NOT_COMPLETE")
    eligible=flips=0; statuses={}
    for i,(lit,orig,stagegame,fc) in enumerate(zip(cases,originals,base,fore),1):
        gid,sha,rows=lit
        if gid!=i or gid!=orig["id"] or gid!=stagegame["id"] or gid!=fc["game_id"] or sha!=orig["source_game_sha256"] or sha!=stagegame["source_sha256"] or sha!=fc["source_game_sha256"] or sha!=reg["ordered_selected_source_game_sha256"][i-1]:
            raise ValueError("P4_SOURCE_GAME_SHA_NOT_SEALED")
        if len(rows)!=4:raise ValueError("P4_EXPECTED_4_ORDER_ROLE_PER_GAME")
        for row,(o,r) in zip(rows,((o,r) for o in ORDERS for r in ROLES)):
            c=fc["root_orders"][o][r]
            expect=[o,r,c["status"],*(c[m] for m in MODELS),int(c["M3_v1_trigger"]),int(c["M3_v2_trigger"]),int(c["M4_trigger"]),c["M4_reason"]]
            if row!=expect:raise ValueError("P4_SEALED_UCI_PRETREATMENT_ROLE_DRIFT")
            st=stagegame["worlds"][o]["roles"][r]["status"]
            statuses[c["status"]]=statuses.get(c["status"],0)+1
            if c["status"]=="FROZEN_SOURCE_ELIGIBLE":
                if st!="FIRST_SOURCE_PAIR_PRE_OUTCOME" or c["M0"] is None or c["M4_survivor"] is None:
                    raise ValueError("P4_M4_ELIGIBLE_SOURCE_LEGAL_MOVE_MISSING")
                eligible+=1;flips+=int(c["M4_survivor"]!=c["M0"])
            else:
                if st=="FIRST_SOURCE_PAIR_PRE_OUTCOME" or any(c[m] is not None for m in MODELS):
                    raise ValueError("P4_PRE_HOLD_MUST_NOT_HAVE_PREDICTION")
    if sum(statuses.values())!=1024 or eligible!=seal["eligible_first_reader_role_cells"] or flips!=seal["M4_predicted_changes"]:
        raise ValueError("P4_ALL_1024_PRE_FIRST_DENOMINATOR_CHANGED")
    return {"source_game_rows":256,"all_role_rows":1024,
        "pre_first_eligible":eligible,"prior_HOLD":1024-eligible,
        "M4_predicted_changes":flips,"treatment_outcomes_seen":False,
        "original_forecast_JSON_SHA256":seal["forecast_raw_SHA256"]}
def main():
    p=argparse.ArgumentParser()
    for n in ("source","stagea","forecast","seal"):p.add_argument("--"+n,required=True)
    a=p.parse_args()
    seal,sha=read(a.seal)
    src,_=read(a.source,SOURCE_SHA)
    stage,_=read(a.stagea,seal["stageA_untreated_raw_SHA256"])
    fore,_=read(a.forecast,seal["forecast_raw_SHA256"])
    result=locked(src,stage,fore,seal)
    print("C3X024_P4_JULY256_ALL_1024ROLE_HUMAN_GIT_PRE_FIRST_EXACT_UCI_GATE_PASS",result,flush=True)
if __name__=="__main__":main()
