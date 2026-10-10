#!/usr/bin/env python3
"""P4 July256 1024-role M4 exact UCI forecasts: untouched source/StageA ONLY.
No engine or treatment is run here. Must Git-literal-seal output before FIRST.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_022_P2_two_stage_exact_move_scout import stockfish16_encoded_move
from c3x_024_P4_M4_preFIRST_survivor_corroboration_rule import m4_survivor_corroboration

SOURCE_SHA="d2c50a1293e68c3feb8571d1ee1be6ba1a7ee539a12dd1a98378adfa9b54fb58"
SOURCE_IDS="c3x/forecasts/c3x-024-P4-July2025-256-source-game-SHA-human-Git-seal-before-native-20261011.json"
POLICY="c3x/ontology/c3x-024-P4-M4-survivor-corroborated-preFIRST-exact-UCI-hypothesis-and-July256-prospective-lock-20261011.md"
SOURCE_SCHEMA="c3x024-P4-blind-July2025-broadcast256-before-any-native-treatment-v1"
STAGE_SCHEMA="c3x024-P4-July2025-256game-preFIRST-untreated-source-genealogy-v1"
SCHEMA="c3x024-P4-July2025-256-source-only-untreated-six-model-exact-UCI-FORECAST-NO-TREATMENT-v1"
def read(path,sha):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=sha:raise ValueError("P3_SHA_GATE_FAIL_"+str(path))
    return json.loads(data)
def native_lookup(row):
    b=chess.Board(row["fen4"]+" "+str(row["source_halfmove_clock"])+" "+str(row["source_fullmove_number"]))
    if not b.is_valid() or b.legal_moves.count()!=row["root_legal_move_count"]:
        raise ValueError("P3_ILLEGAL_PRESEALED_SOURCE_BOARD")
    source_to_uci={}
    uci_to_native={}
    for move in b.legal_moves:
        native=stockfish16_encoded_move(b,move)
        if native in source_to_uci and source_to_uci[native]!=move.uci():
            raise ValueError("P3_NONINJECTIVE_NATIVE_MOVE")
        source_to_uci[native]=move.uci()
        uci_to_native[move.uci()]=native
    return source_to_uci,uci_to_native
def exact_m3v2(role,target_native,base_native,base,opposite,depth11):
    """Immutable pre-FIRST TT-exposed root-order/depth instability rule."""
    if role!="STRICT" or target_native!=base_native:
        return base,False
    if base!=opposite:
        return opposite,True
    if depth11 is not None and depth11!=base:
        return depth11,True
    return base,False

def predict(source,stage,reg):
    if source["schema"]!=SOURCE_SCHEMA or stage["schema"]!=STAGE_SCHEMA:
        raise ValueError("P3_SOURCE_OR_STAGE_A_SCHEMA_WRONG")
    if reg["source_only_derived_JSON_SHA256"]!=SOURCE_SHA or reg["source_game_count"]!=256:
        raise ValueError("P3_SOURCE_GIT_ID_LOCK_WRONG")
    if [x["source_game_sha256"] for x in source["selected"]]!=reg["ordered_selected_source_game_sha256"]:
        raise ValueError("P3_128_SOURCE_IDENTITIES_DRIFT")
    if stage["source_sha256"]!=SOURCE_SHA or stage["literal_preNative_git_seal"]!=SOURCE_IDS:
        raise ValueError("P3_UNTREATED_STAGA_WRONG_SOURCE")
    sm=stage["summary"]
    if sm["actual_TT_FIRST_interventions"] or sm["actual_SEE_Boolean_interventions"] or sm["treatment_outcomes_seen"]:
        raise ValueError("P3_TREATED_DATA_UNALLOWED")
    if sm["distinct_source_boards"]!=256 or sm["potential_role_cells"]!=1024:
        raise ValueError("P3_128_512_STAGE_DENOMINATOR_MISMATCH")
    cases=stage["ecologies"]["july2025_broadcast"]["cases"]
    if len(cases)!=256:raise ValueError("P3_MISSING_UNTREATED_GAMES")
    report={"schema":SCHEMA,"stage":"EXACT_FIVE_MODEL_LITERAL_PRE_FIRST_NO_TREATED_OUTCOMES",
      "source_only_JSON_SHA256":SOURCE_SHA,"model_policy_git":POLICY,
      "source_literal_ids_git":SOURCE_IDS,"source_games":256,
      "role_cell_denominator":1024,"TT_FIRST_interventions_seen":0,
      "SEE_boolean_interventions_seen":0,
      "models":["M0","M1","M2_depth11","M3_v1","M3_v2","M4_survivor"],"cases":[]}
    triggers_v1=triggers_v2=triggers_m4=eligible=m2covered=0
    for row,case in zip(source["selected"],cases):
        if row["id"]!=case["id"] or row["source_game_sha256"]!=case["source_sha256"]:
            raise ValueError("P3_GAME_AND_STAGE_CASE_MISMATCH")
        native,UCI=native_lookup(row)
        bases={order:case["worlds"][order]["baseline_UCI"]["bestmove"] for order in ("O","F")}
        if not all(m in UCI for m in bases.values()):raise ValueError("P3_BASELINE_MOVE_ILLEGAL")
        result={"game_id":row["id"],"source_game_sha256":row["source_game_sha256"],"root_orders":{}}
        for order in ("O","F"):
            opposite="F" if order=="O" else "O"
            world=case["worlds"][order]
            depth=world["depth_leaders"].get("11",{}).get("native_leader")
            depth11=native.get(depth)
            noncensored=not world["passive_SEE_witness_censored"]
            events=world["passive_first32_SEE_events"]
            for role in ("STRICT","BROAD"):
                item=world["roles"][role]
                if item["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":
                    cell={"status":"HOLD_NO_PHYSICAL_FIRST_READER","M0":None,"M1":None,
                          "M2_depth11":None,"M3_v1":None,"M3_v2":None,
                          "M3_v1_trigger":False,"M3_v2_trigger":False,"M4_survivor":None,"M4_trigger":False,"M4_reason":"PRE_FIRST_INELIGIBLE_HOLD",
                          "reason":"NO_PRE_TREATMENT_FIRST_READER_ELIGIBILITY"}
                else:
                    eligible+=1
                    root_call=item["root_calls"][0]
                    target=item["root_candidate_native"]
                    base=bases[order]
                    opp=bases[opposite]
                    witness=noncensored and any(e["kind"]=="witness" and
                            e.get("root_call")==root_call and
                            e.get("original")==e.get("delivered") and
                            e.get("altered")==0 for e in events)
                    linked=(role=="STRICT" and target==UCI[base])
                    v1=linked and base!=opp and witness
                    pred_v2,v2=exact_m3v2(role,target,UCI[base],base,opp,depth11)
                    depth_by_native={d:native.get(world["depth_leaders"].get(str(d),{}).get("native_leader"))
                                     for d in (8,9,10,11)}
                    m4=m4_survivor_corroboration(role=role,eligible=True,
                        source_reader_native=target,baseline_native=UCI[base],
                        baseline_UCI=base,opposite_UCI=opp,
                        depth8to11=depth_by_native,legal_uci=set(UCI))
                    cell={"status":"FROZEN_SOURCE_ELIGIBLE",
                      "root_candidate_native":target,
                      "root_source_call":root_call,
                      "untreated_O_F_disagree":bases["O"]!=bases["F"],
                      "untreated_depth11_to12_disagree":bool(depth11 and depth11!=base),
                      "passive_SEE_prefix_censored":not noncensored,
                      "original_same_root_SEE_contact":witness,
                      "M0":base,"M1":opp,"M2_depth11":depth11,
                      "M3_v1":opp if v1 else base,
                      "M3_v2":pred_v2,"M3_v1_trigger":v1,"M3_v2_trigger":v2,
                      "M4_survivor":m4["M4"],"M4_trigger":m4["predict_flip"],
                      "M4_reason":m4["reason"],
                      "depth8to11_original_same_order_UCI":{str(d):depth_by_native[d] for d in (8,9,10,11)}}
                    for model in ("M0","M1","M3_v1","M3_v2","M4_survivor"):
                        if cell[model] not in UCI:raise ValueError("P3_ILLEGAL_"+model)
                    triggers_v1+=int(v1);triggers_v2+=int(v2);triggers_m4+=int(m4["predict_flip"])
                    m2covered+=int(depth11 is not None)
                result["root_orders"].setdefault(order,{})[role]=cell
        report["cases"].append(result)
    report["summary"]={"eligible_pre_FirST_physical_role_cells":eligible,
      "M3_v1_predicted_changes":triggers_v1,"M3_v2_predicted_changes":triggers_v2,"M4_predicted_changes":triggers_m4,
      "M2_depth11_covered":m2covered,"independent_games":256,
      "positive_v2_is_not_proven_accuracy":True,
      "M0_vs_M3v2_not_yet_scored":True,"NO_ORIGINAL_TREATED_NATIVE_OUTCOMES":True}
    return report
def main():
    p=argparse.ArgumentParser()
    for f in ("source","stagea","stagea-sha","out"):p.add_argument("--"+f,required=True)
    args=p.parse_args()
    source=read(args.source,SOURCE_SHA)
    stage=read(args.stagea,args.stagea_sha)
    reg=json.loads(Path(SOURCE_IDS).read_text())
    d=predict(source,stage,reg)
    f=Path(args.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X024_P4_PRETREATMENT_256_SIX_MODEL_FORECAST",d["summary"],
          hashlib.sha256(f.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
