#!/usr/bin/env python3
"""July256 six-model pre-FIRST exact UCI human Git literal log exporter.
Prints NO FEN, PGN, player names, original move lists, engine TT/SEE outcome.
All 1024 roles must be emitted, including source HOLD rows, before any FIRST.
"""
import argparse,hashlib,json
from pathlib import Path

MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2","M4_survivor")
def record(d):
    if d["schema"]!="c3x024-P4-July2025-256-source-only-untreated-six-model-exact-UCI-FORECAST-NO-TREATMENT-v1":
        raise ValueError("P4_GIT_LITERAL_ONLY_UNTREATED_SCHEMA_REQUIRED")
    if d["source_games"]!=256 or d["role_cell_denominator"]!=1024 or d["TT_FIRST_interventions_seen"]!=0 or d["SEE_boolean_interventions_seen"]!=0:
        raise ValueError("P4_GIT_LITERAL_ONLY_1024_NO_FIRST_REQUIRED")
    if len(d["cases"])!=256 or any(g["game_id"]!=i for i,g in enumerate(d["cases"],1)):
        raise ValueError("P4_GIT_LITERAL_SOURCE_ORDER_INVALID")
    output=[];eligible=positives=0
    for g in d["cases"]:
        sh=g["source_game_sha256"]
        if len(sh)!=64 or not all(z in "0123456789abcdef" for z in sh):
            raise ValueError("P4_SHA_GAME_ID_INVALID")
        roles=[]
        for order in ("O","F"):
            for role in ("STRICT","BROAD"):
                x=g["root_orders"][order][role]
                row=[order,role,x["status"],*(x[k] for k in MODELS),
                     int(x["M3_v1_trigger"]),int(x["M3_v2_trigger"]),int(x["M4_trigger"]),x["M4_reason"]]
                if x["status"]=="FROZEN_SOURCE_ELIGIBLE":
                    if any(row[j] is None for j in range(3,9)):
                        raise ValueError("P4_SIX_MODEL_REQUIRED_EXACT_UCI_MISSING")
                    eligible+=1;positives+=int(x["M4_survivor"]!=x["M0"])
                else:
                    if any(row[j] is not None for j in range(3,9)) or x["M4_trigger"]:
                        raise ValueError("P4_HOLD_MUST_NOT_EXPOSE_TREATED_PREDICTION")
                roles.append(row)
        if len(roles)!=4:raise ValueError("P4_MISSING_O_F_STRICT_BROAD_ROWS")
        output.append([g["game_id"],sh,roles])
    if eligible!=d["summary"]["eligible_pre_FirST_physical_role_cells"] or positives!=d["summary"]["M4_predicted_changes"]:
        raise ValueError("P4_ORIGINAL_FORECAST_MODEL_POSITIVE_COUNT_DRIFT")
    return output,eligible,positives
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--file",required=True)
    a=p.parse_args()
    f=Path(a.file);raw=f.read_bytes();d=json.loads(raw)
    rows,eligible,pos=record(d)
    digest=hashlib.sha256(raw).hexdigest()
    print("C3X024_P4_PRE_FIRST_1024ROLE_SIX_MODEL_FULL_SHA256="+digest,flush=True)
    for i in range(0,256,16):
        print("C3X024_P4_HUMAN_GIT_LITERAL_BATCH_"+str(i//16)+"="+json.dumps(rows[i:i+16],separators=(",",":"),ensure_ascii=False),flush=True)
    print("C3X024_P4_ALL_1024_LITERAL_ROWS_PRINTED_FOR_HUMAN_GIT_SEAL",
          {"source_games":256,"role_cells":1024,"eligible":eligible,
           "prior_HOLD":1024-eligible,"M4_positive_changes":pos,
           "forecast_source_full_SHA256":digest,"TT_FIRST_treatments_seen":0},flush=True)
if __name__=="__main__":main()
