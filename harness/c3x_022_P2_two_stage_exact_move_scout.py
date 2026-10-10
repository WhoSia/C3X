#!/usr/bin/env python3
"""C3X022-P2 stage A: literal UCI outcome predictions, zero TT interventions.

Novel ecologies TWIC1656 and puzzle solver root positions, with source-only
full clock history, frozen January STRICT/BROAD source selectors and game IDs.
No V intervention in stage A. All predictions precede separate stage B.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair,mask_filters
from c3x_021_P1_march_native_TT_atomic_bridge import root_depth_ladder

ROLES=("STRICT","BROAD")
WORLDS=("O","F")
ECOLOGIES=("twic","lichess_puzzles")
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}
SCHEMA="c3x022-P2-cross-ecology-literal-specific-UCI-forecast-stageA-v1"

def source(path,expected_sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==expected_sha,"P2_SOURCE_SNAPSHOT_SHA_DRIFT")
    d=json.loads(raw)
    need(d["phase"]=="ENGINE_BLIND_SOURCE_FREEZE_NO_TT_FORECAST_OUTCOME"
         and d["selected_count"]==32,"P2_SOURCE_NOT_32_PRENATIVE")
    return d

def stockfish16_encoded_move(board,move):
    """Exact pinned SF16 Move bits: NORMAL, EP 2<<14, CASTLING 3<<14.
    SF16 castling to-square stores the ROOK origin, not king arrival.
    """
    base=move.from_square*64+move.to_square
    if board.is_castling(move):
        rook_file=7 if board.is_kingside_castling(move) else 0
        rook_square=chess.square(rook_file,chess.square_rank(move.from_square))
        return (3<<14)+(move.from_square*64)+rook_square
    if board.is_en_passant(move):
        return (2<<14)+base
    return base

def native_world(row):
    need("source_halfmove_clock" in row and "source_fullmove_number" in row,
         "SOURCE_ORIGINAL_CHESS_CLOCK_NOT_FROZEN")
    half,full=row["source_halfmove_clock"],row["source_fullmove_number"]
    b=chess.Board(row["fen4"]+" "+str(half)+" "+str(full))
    need(b.is_valid(),"SOURCE_BAD_CHESS_BOARD")
    move=chess.Move.from_uci(row["played_legal_move_uci"])
    need(move in b.legal_moves and b.legal_moves.count()==row["source_root_legal_count"],
         "SOURCE_PLAYED_ROOT_NOT_LEGAL")
    valid=" ".join(b.fen(en_passant="legal").split()[:4])
    need(valid.split()[:3]==row["fen4"].split()[:3],
         "SOURCE_NON_EP_BOARD_NORMALIZED")
    w=dict(row);w["fen4"]=valid
    # Frozen source records legal chess UCI coordinates; C3X016-P4 reads
    # raw internal SF16 Move integers. Do not alter selected source positions.
    source_normal=row["native_move"]
    need(source_normal==move.from_square*64+move.to_square,
         "SOURCE_CHESS_COORDINATE_ENCODING_DRIFT")
    w["native_move"]=stockfish16_encoded_move(b,move)
    w["source_chess_coordinate_move"]=source_normal
    return w,(half,full),valid!=row["fen4"]

def cold(engine,w,clock,order,discovery=False):
    x=play(engine,w,order,"OBS",fen_clocks=clock,discovery=discovery)
    y=play(engine,w,order,"OBS",fen_clocks=clock,discovery=discovery)
    need(x==y,"P2_STAGE_A_COLD_DUPLICATE_MISMATCH")
    need(x["root_events"] and len(x["root_events"])<4096,
         "P2_STAGE_A_ROOT_TRACE_CENSORED")
    need(not any(e.get("kind") in ("censored","trace_censored")
                 for e in x["payload_witnesses"]),"P2_STAGE_A_TT_SOURCE_CENSORED")
    return x

def exact_forecast(O_move,F_move,order,eligible):
    if not eligible:
        return {"status":"NO_TREATMENT","predicted_UCI":None,"predicted_flip":None}
    predicted=(F_move if order=="O" else O_move) if O_move!=F_move else O_move
    actual_baseline=O_move if order=="O" else F_move
    return {"status":"PREDICTED_EXACT_UCI_BEFORE_TT_INTERVENTION",
            "predicted_UCI":predicted,
            "predicted_flip":predicted!=actual_baseline,
            "predictor":"CROSS_ORDER_RESTORATION_V1"}

def stage_a(d,engine):
    r={"schema":SCHEMA,"study":"TWO_STAGE_UNSEEN_TWIC_AND_PUZZLES_BEFORE_ANY_V",
       "source_digest_set_at_cli":True,
       "ecologies":{}}
    for eco in ECOLOGIES:
        part=d["ecologies"][eco]
        rows=part["selected"]
        need(len(rows)==16 and [v["id"] for v in rows]==list(range(1,17)),
             "EXACT16_PER_EXTERNAL_ECOLOGY")
        out=[]
        for row in rows:
            w,clock,ep=native_world(row)
            baselines={}
            discoveries={}
            for order in WORLDS:
                base=cold(engine,w,clock,order)
                passive=cold(engine,w,clock,order,discovery=True)
                need(base["UCI"]==passive["UCI"],
                     "PASSIVE_SOURCE_CHANGED_BASELINE_BESTMOVE")
                events=[e for e in passive["payload_witnesses"]
                        if e["kind"]=="discovery"]
                need(len(events)<=2048,"P2_SOURCE_DISCOVERY_CAP")
                baselines[order]=base
                discoveries[order]=events
            O=baselines["O"]["UCI"]["bestmove"]
            F=baselines["F"]["UCI"]["bestmove"]
            record={"id":row["id"],"game_sha256":row["source_game_sha256"],
                    "source_position_fen4":row["fen4"],
                    "source_clock":clock,
                    "source_legal_root_count":row["source_root_legal_count"],
                    "O_baseline_exact_UCI":baselines["O"]["UCI"],
                    "F_baseline_exact_UCI":baselines["F"]["UCI"],
                    "O_F_disagree":O!=F,
                    "worlds":{}}
            for order in WORLDS:
                role_data={}
                for role in ROLES:
                    pair=first_pair(discoveries[order],RULES[role])
                    forecast=exact_forecast(O,F,order,pair is not None)
                    if pair is not None:
                        forecast["source_physical"]=pair["physical"]
                        forecast["root_calls"]=pair["root_calls"]
                        forecast["source_root_move_native"]=pair["root_candidate_native"]
                        forecast["source_selected_indices"]=pair["indices"]
                    role_data[role]=forecast
                record["worlds"][order]={
                    "baseline_UCI":baselines[order]["UCI"],
                    "root_depth_ladder":root_depth_ladder(baselines[order]["root_events"]),
                    "number_discovery_events":len(discoveries[order]),
                    "source_C3X018_HARD_CAP_REACHED":len(discoveries[order])==2048,
                    "roles":role_data}
            out.append(record)
            print("C3X022_P2_STAGE_A_FORECAST",eco,row["id"],"O",O,"F",F,
                  {z:{k:(x["status"],x["predicted_UCI"]) for k,x in record["worlds"][z]["roles"].items()}
                   for z in WORLDS},flush=True)
        r["ecologies"][eco]={"source_archive_sha256":part["archive"].get("zip_sha256",part["archive"].get("compressed_file_sha256")),
                              "selected":out}
    r["summary"]={
        "ecologies":2,"games_per_ecology":16,"total_game_units":32,
        "role_order_cells":32*2*2,
        "eligible_source_cells":sum(
            o["roles"][role]["status"]!="NO_TREATMENT"
            for part in r["ecologies"].values() for row in part["selected"]
            for o in row["worlds"].values() for role in ROLES),
        "O_F_differ_games_by_ecology":{
            eco:sum(x["O_F_disagree"] for x in r["ecologies"][eco]["selected"])
            for eco in ECOLOGIES},
        "forecast_rule":"CROSS_ORDER_RESTORATION_V1_FIXED_BEFORE_NEW_CORPUS",
        "any_TT_V_intervention_performed":False
    }
    return r

def main():
    a=argparse.ArgumentParser()
    for name in ("source","source-sha","engine","out"):a.add_argument("--"+name,required=True)
    p=a.parse_args()
    result=stage_a(source(p.source,p.source_sha),p.engine)
    out=Path(p.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_ALL128_PRE_TREATMENT_EXACT_UCI_FORECASTS",
          result["summary"],hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
