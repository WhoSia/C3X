#!/usr/bin/env python3
"""C3X 0.24 literal forecasts generated ONLY from frozen source + untreated StageA.

Models defined in Git before reading any new Aug2025 physical FIRST/SEE results.
This run SHALL NOT call Stockfish and SHALL NOT inspect intervention outcomes.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_022_P2_two_stage_exact_move_scout import stockfish16_encoded_move

SOURCE_SHA="76391058cae1fad8d23e3ae8556e48b63a0d991a051c59fef2df15e11c73f529"
STAGE_A_SHA="116b3c0f63be3074236982c76abd059b1dca3bb1f019cc3c10f9b03a5ac1855e"
REGISTRY="c3x/forecasts/c3x-024-P0-Aug2025-16game-literal-source-Git-seal-before-native-20261011.json"
M3_CHARER="c3x/ontology/c3x-024-P0-to-P1-preintervention-M0-M1-M2-M3-forecast-rule-freeze-20261011.md"
SCHEMA="c3x024-P0-Aug2025-literal-four-model-no-treatment-predictions-v1"

def frozen(path,expected):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("C3X024_PRETREATMENT_FROZEN_SHA_DRIFT")
    return json.loads(raw)

def legal_native_map(source_row):
    board=chess.Board(source_row["fen4"]+" "+str(source_row["source_halfmove_clock"])+
                      " "+str(source_row["source_fullmove_number"]))
    if not board.is_valid() or board.legal_moves.count()!=source_row["root_legal_move_count"]:
        raise ValueError("LEGALITY_OR_BOARD_CHANGED")
    lookup={}
    for m in board.legal_moves:
        code=stockfish16_encoded_move(board,m)
        if code in lookup and lookup[code]!=m.uci():
            raise ValueError("NONINJECTIVE_ENGINE_MOVE_MAPPING")
        lookup[code]=m.uci()
    if source_row["played_legal_move_uci"] not in lookup.values():
        raise ValueError("PLAYED_SOURCE_NOT_LEGAL")
    return lookup,{uci:native for native,uci in lookup.items()}

def make(src,stage,source_registry):
    if src["schema"]!="c3x024-P0-blind-Aug2025-broadcast16-before-any-native-treatment-v1" or \
       src["treatment_outcomes_seen"] is not False:
        raise ValueError("NONFROZEN_SOURCE_NOT_ADMISSIBLE")
    if stage["schema"]!="c3x024-P0-Aug2025-16game-pre-V-untreated-native-original-source-genealogy-v1" or \
       stage["summary"]["actual_TT_FIRST_interventions"]!=0 or \
       stage["summary"]["actual_SEE_Boolean_interventions"]!=0 or \
       stage["summary"]["treatment_outcomes_seen"] is not False:
        raise ValueError("STAGEA_NOT_UNTREATED")
    selected=src["selected"]
    if len(selected)!=16 or [x["source_game_sha256"] for x in selected]!=\
       source_registry["literal_ordered_selected_source_game_sha256"]:
        raise ValueError("SOURCE_PRENATIVE_LITERAL_GIT_SEAL_MISMATCH")
    if stage["source_sha256"]!=SOURCE_SHA or stage["literal_preNative_git_seal"]!=REGISTRY:
        raise ValueError("STAGEA_WRONG_SOURCE")
    cases=stage["ecologies"]["aug2025_broadcast"]["cases"]
    if len(cases)!=16:raise ValueError("STAGEA_NOT_16_GAMES")
    report={"schema":SCHEMA,
       "status":"FULL_LITERAL_PRE_TT_FIRST_FORECAST_PENDING_GIT_COMMIT_NOT_YET_TREATMENT",
       "frozen_source_JSON_SHA256":SOURCE_SHA,
       "frozen_untreated_StageA_JSON_SHA256":STAGE_A_SHA,
       "source_literals_git":REGISTRY,
       "model_policy_Git_preintervention":M3_CHARER,
       "models":{
         "M0":"same-order no-treatment baseline exact UCI",
         "M1":"opposite-order no-treatment baseline exact UCI (historically poor)",
         "M2_depth11":"original depth11 native leader legal UCI; unavailable yields NO_PREDICTION",
         "M3":"opposite-order exact UCI only for strict first TT reader targeting baseline winner with noncensored same-source original SEE witness; otherwise M0"},
       "source_game_count":16,"role_cell_denominator":64,
       "new_2025_Aug_first_reader_treatments_seen":0,
       "new_2025_Aug_SEE_treatments_seen":0,
       "derived_research_no_original_game_PGN_or_player_headers":True,
       "cases":[]}
    predicted_m3=0; roles=0;m2_covered=0
    for source,case in zip(selected,cases):
        if source["id"]!=case["id"] or case["source_sha256"]!=source["source_game_sha256"]:
            raise ValueError("SOURCE_STAGEA_CASE_ALIGNMENT_DRIFT")
        lookup,reverse=legal_native_map(source)
        base={o:case["worlds"][o]["baseline_UCI"]["bestmove"] for o in ("O","F")}
        if any(v not in reverse for v in base.values()):
            raise ValueError("BASELINE_UCI_NOT_LEGAL_CHESS_ROOT")
        output={"game_id":source["id"],"source_game_sha256":source["source_game_sha256"],
                "root_orders":{}}
        for order in ("O","F"):
            world=case["worlds"][order]
            opposite="F" if order=="O" else "O"
            native_d11=world["depth_leaders"].get("11",{}).get("native_leader")
            depth11=lookup.get(native_d11)
            native_base=reverse[base[order]]
            source_events=world["passive_first32_SEE_events"]
            noncensored=not world["passive_SEE_witness_censored"]
            for role in ("STRICT","BROAD"):
                item=world["roles"][role]
                if item["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":
                    entry={"scope":"HOLD_NO_PHYSICAL_FIRST_READER","M0":None,"M1":None,
                           "M2_depth11":None,"M3":None,"reason":"NO_TREATMENT"}
                else:
                    source_call=item["root_calls"][0]
                    matching_SEE=(role=="STRICT" and noncensored and any(
                        e["kind"]=="witness" and e.get("root_call")==source_call and
                        e.get("original")==e.get("delivered") and
                        e.get("altered")==0 for e in source_events))
                    trigger=(role=="STRICT" and base[order]!=base[opposite] and
                             item["root_candidate_native"]==native_base and matching_SEE)
                    m3=base[opposite] if trigger else base[order]
                    entry={"scope":"SOURCE_ELIGIBLE_FROZEN",
                           "physical_FIRST_native_root_candidate":item["root_candidate_native"],
                           "source_root_call":source_call,
                           "SEE_same_first_STRICT_source_non_censored":matching_SEE,
                           "M3_rule_trigger":trigger,
                           "M0":base[order],"M1":base[opposite],
                           "M2_depth11":depth11,
                           "M2_status":"PREDICTION" if depth11 else "NO_PREDICTION",
                           "M3":m3}
                    for key in ("M0","M1","M3"):
                        if entry[key] not in reverse:
                            raise ValueError("ILLEGAL_LITERAL_PREDICTION_"+key)
                    if item["exact_UCI"]["M0"]!=entry["M0"] or \
                       item["exact_UCI"]["M1"]!=entry["M1"]:
                        raise ValueError("HISTORICAL_M0_M1_STAGEA_MISMATCH")
                    roles+=1;m2_covered+=int(depth11 is not None)
                    predicted_m3+=int(trigger)
                output["root_orders"].setdefault(order,{})[role]=entry
        report["cases"].append(output)
    report["summary"]={"new_unique_source_games":len(report["cases"]),
       "physically_eligible_role_cells":roles,
       "M2_depth11_literal_coverage":m2_covered,
       "M3_positive_prediction_cells":predicted_m3,
       "original_M0_M1_prior_history":"0.23 117/124 vs 111/124 (M1 FAIL); no retroactive refit",
       "source_games_are_cluster_unit":True,
       "pre_native_treatment_status":"FORECAST_GENERATION_ONLY_NO_FIRST_SEE_TREATMENT"}
    return report

def main():
    p=argparse.ArgumentParser()
    for name in ("source","stagea","registry","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    registry=json.loads(Path(a.registry).read_text())
    out=make(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGE_A_SHA),registry)
    file=Path(a.out);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("C3X024_P0_M0_M1_M2_M3_ALL_LITERAL_PRETREATMENT",
          out["summary"],hashlib.sha256(file.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
