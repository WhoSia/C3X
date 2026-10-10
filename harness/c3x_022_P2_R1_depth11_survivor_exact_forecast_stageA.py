#!/usr/bin/env python3
"""P2-R1 StageA: exact per-game UCI move predictions on frozen TWIC1664.

NO native TT FIRST suppression. Models M0 unchanged, M1 historical restoration,
M2 precommitted depth11 survivor with lower source-blind six-recapture risk.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair
from c3x_022_P2_two_stage_exact_move_scout import (
    cold,native_world,source_depth_ladder,stockfish16_encoded_move)

SOURCE_SHA="3cc4c788eec55960921e653604b2fbb3113163862e2652271b939fb12fb9eeb3"
PRIMITIVE_SHA="321f3af0ea90625929d639142ec8f930eacee5a7c6e7d856235267bb7f908423"
ISSUE=1664
ROLES=("STRICT","BROAD")
WORLDS=("O","F")
SCHEMA="c3x022-P2-R1-TWIC1664-stageA-three-exact-UCI-model-forecasts-v1"

def frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,
         "P2_R1_FROZEN_NEW_SOURCE_OR_CHESS_SHA_CHANGED")
    return json.loads(raw)

def native_leader_uci(board,native_move):
    """Exact typed SF16 Move decoded by legal chess move-identity matching."""
    if native_move is None:return None
    legal={stockfish16_encoded_move(board,m):m.uci() for m in board.legal_moves}
    return legal.get(native_move)

def forecast_three(baseline,other,leader11,risk,eligible):
    """Entire decision rule registered before any StageB V intervention."""
    if not eligible:
        return {"status":"NO_TREATMENT","M0":None,"M1":None,"M2":None,
                "M2_depth11_legal_candidate":leader11}
    m0=baseline
    m1=other if baseline!=other else baseline
    m2=(leader11 if leader11 in risk and leader11!=baseline and
        risk[leader11]<risk[baseline] else baseline)
    return {"status":"FORECAST_REGISTERED_BEFORE_FIRST_TT_READER_BLOCK",
            "M0":m0,"M1":m1,"M2":m2,
            "M2_positive_prediction":m2!=baseline,
            "M1_positive_prediction":m1!=baseline,
            "M2_depth11_legal_candidate":leader11,
            "baseline_legal_recapture_exposure":risk[baseline],
            "depth11_legal_recapture_exposure":risk.get(leader11) if leader11 else None}

def study(source,primitives,engine):
    need(source["phase"]=="NEW_TWIC1664_SOURCE_ONLY_BEFORE_ANY_NEW_NATIVE_OUTCOME",
         "SOURCE_P2_R1_NOT_ENGINE_BLIND")
    need(primitives["phase"]=="PRE_NATIVE_ALL_ACTIONS_CHESS_AND_EXCHANGE_FROZEN",
         "LEGAL_EXCHANGE_NOT_PREENGINE")
    a=source["selected"];b=primitives["positions"]
    need(len(a)==len(b)==16,"EXACT16")
    out={"schema":SCHEMA,"source_sha256":SOURCE_SHA,
         "primitives_sha256":PRIMITIVE_SHA,
         "engine_stage":"NO_FIRST_TT_V_INTERVENTIONS",
         "models":"M0 nochange, M1 cross-order, M2 depth11 survivor lower recapture risk",
         "cases":[]}
    for raw,pre in zip(a,b):
        need(raw["id"]==pre["id"] and
             raw["source_game_sha256"]==pre["source_game_sha256"],
             "NEW_GAME_SOURCE_ID_NOT_ALIGNED")
        w,clock,_=native_world(raw)
        board=chess.Board(w["fen4"]+" "+str(clock[0])+" "+str(clock[1]))
        risk={x["UCI"]:x["responder_optimal_legal_exchange_gain"] for x in pre["legal_exchange_tree"]}
        need(len(risk)==raw["source_root_legal_count"],"LEGAL_SEE_CENSUS_DRIFT")
        baselines={};events={}
        for order in WORLDS:
            obs=cold(engine,w,clock,order)
            discovery=cold(engine,w,clock,order,discovery=True)
            need(obs["UCI"]==discovery["UCI"],"PASSIVE_DISCOVERY_CHANGED_BASELINE")
            baselines[order]=obs
            events[order]=[e for e in discovery["payload_witnesses"] if e["kind"]=="discovery"]
            need(len(events[order])<=2048,"DISCOVERY_OVER_LIMIT")
        moves={order:baselines[order]["UCI"]["bestmove"] for order in WORLDS}
        need(all(m in risk for m in moves.values()),"BASELINE_NOT_LEGAL_CHESS")
        row={"id":raw["id"],"game_sha256":raw["source_game_sha256"],
             "baseline_O_UCI":baselines["O"]["UCI"],
             "baseline_F_UCI":baselines["F"]["UCI"],
             "worlds":{}}
        for order in WORLDS:
            rawladder=source_depth_ladder(baselines[order]["root_events"])
            lead11=native_leader_uci(board,rawladder.get("11",{}).get("native_leader"))
            leader_trace_missing=(not rawladder or "11" not in rawladder)
            role_forecasts={}
            for role in ROLES:
                pair=first_pair(events[order],RULES[role])
                f=forecast_three(moves[order],moves["F" if order=="O" else "O"],
                                 lead11,risk,pair is not None)
                if pair is None and len(events[order])==2048:
                    f={"status":"HOLD_CENSORED_NO_FIRST_SOURCE_PAIR","M0":None,"M1":None,"M2":None,"M2_depth11_legal_candidate":lead11}
                if pair:
                    f.update({"physical":pair["physical"],"root_calls":pair["root_calls"],
                              "root_candidate_native":pair["root_candidate_native"],
                              "source_indices":pair["indices"]})
                role_forecasts[role]=f
            row["worlds"][order]={
                "baseline_UCI":baselines[order]["UCI"],
                "depthwise_baseline_leaders":rawladder,
                "depth11_UCI":lead11,
                "missing_depth11":leader_trace_missing,
                "role_forecasts":role_forecasts,
                "discovery_events":len(events[order])}
        out["cases"].append(row)
        print("C3X022_P2_R1_STAGE_A_FROZEN_FORECAST",raw["id"],
              {order:{"base":moves[order],"11":row["worlds"][order]["depth11_UCI"],
                      "M2":{k:rv["M2"] for k,rv in row["worlds"][order]["role_forecasts"].items()}}
               for order in WORLDS},flush=True)
    out["summary"]={"games":16,"role_order_cells":64,
       "eligible_first_TT_source_cells":sum(v["status"]=="FORECAST_REGISTERED_BEFORE_FIRST_TT_READER_BLOCK"
          for row in out["cases"] for w in row["worlds"].values()
          for v in w["role_forecasts"].values()),
       "O_F_baselines_disagree_games":sum(x["baseline_O_UCI"]["bestmove"]!=x["baseline_F_UCI"]["bestmove"]
                                           for x in out["cases"]),
       "M2_predicted_flip_cells":sum(v.get("M2_positive_prediction",False)
          for row in out["cases"] for w in row["worlds"].values()
          for v in w["role_forecasts"].values()),
       "FIRST_TT_interventions_performed":0}
    return out

def main():
    a=argparse.ArgumentParser()
    for k in ("source","primitives","engine","out"):a.add_argument("--"+k,required=True)
    q=a.parse_args()
    d=study(frozen(q.source,SOURCE_SHA),frozen(q.primitives,PRIMITIVE_SHA),q.engine)
    out=Path(q.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_R1_STAGEA_THREE_MODELS_BEFORE_TT_TREATMENT",d["summary"],
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
