"""Explicit single-played-move source-native ECL interpretation of an authorized PGN.

This is a scoped, runnable research CLI; the strong rival is frozen by an original
engine scout BEFORE root-restricted two-choice search. NOT a strong-engine oracle,
calibrated neural decision, causal certificate or human-learning measurement.
"""
from __future__ import annotations
import argparse, io, json
from pathlib import Path
import chess
import chess.pgn
import chess.engine
from .core import move_facts, heuristic_atoms, firewall, score_cp
from .graph import attach_graphs
from .renderer import attach_render_packets
from .realization import attach_realizations
from .verification import attach_verification
from .evidence_compiler import compile_evidence

def position_before_ply(pgn_text:str, ply:int):
    game=chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None or game.errors:
        raise ValueError("INVALID_OR_UNREPLAYABLE_PGN")
    moves=list(game.mainline_moves())
    if not isinstance(ply,int) or not (1 <= ply <= len(moves)):
        raise ValueError("PLY_NOT_IN_PGN")
    board=game.board()
    for m in moves[:ply-1]:
        if m not in board.legal_moves:raise ValueError("ILLEGAL_GAME_HISTORY")
        board.push(m)
    played=moves[ply-1]
    if not board.is_valid() or played not in board.legal_moves:
        raise ValueError("PLAYED_MOVE_ILLEGAL_OR_ORIGINAL_BOARD_INVALID")
    return board, played

def _native_candidate(info,board,rank:int)->dict:
    pv=info.get("pv") or []
    if not pv or pv[0] not in board.legal_moves:raise ValueError("BAD_NATIVE_ENGINE_PV")
    score=info.get("score")
    if score is None:raise ValueError("NATIVE_ENGINE_SCORE_MISSING")
    return {
        "rank":rank,"uci":pv[0].uci(),"san":board.san(pv[0]),
        "depth":info.get("depth"),"nodes":info.get("nodes"),"time":info.get("time"),
        "score_cp":score_cp(score,board.turn),
        "score_bound":bool(info.get("lowerbound") or info.get("upperbound")),
        "score_mate":score.pov(board.turn).mate(),
        "pv_uci":[m.uci() for m in pv[:10]]
    }

def _engine_rows(engine,board,depth:int,multipv:int,root_moves=None):
    r=engine.analyse(board,chess.engine.Limit(depth=depth),
                     multipv=multipv,root_moves=root_moves,
                     info=chess.engine.INFO_ALL)
    if isinstance(r,dict):r=[r]
    return [_native_candidate(row,board,k) for k,row in enumerate(r,1)]

def _focussed_i9_verified_moment(board,played,pair,ply:int):
    facts=move_facts(board,played)
    atoms=heuristic_atoms(board,played,pair,facts)
    for i,a in enumerate(atoms):a["atom_id"]=f"p{ply}:focus:a{i}"
    errors=firewall(board,atoms)
    moment={
        "ply":ply,"fen":board.fen(),"played_uci":played.uci(),
        "played_san":board.san(played),"atoms":atoms,"candidates":pair,
        "selection_reasons":["EXPLICIT_USER_PGN_PLY_FOCUS"],
        "commentary_plan":{"categories":[],"atom_ids":[a["atom_id"] for a in atoms]},
        "firewall":{"pass":not errors,"errors":errors}
    }
    attach_graphs([moment]);attach_render_packets([moment])
    attach_realizations([moment],"advanced");attach_verification([moment])
    return moment

def run_focussed_pgn(pgn_text:str, engine_path:str, ply:int,
                     *, scout_depth:int=9, pair_depth:int=12,
                     disable_nnue:bool=False)->dict:
    if not 1 <= scout_depth <= 30 or not 1 <= pair_depth <= 30:
        raise ValueError("UNSAFE_OR_INVALID_DEPTH_SETTING")
    board,played=position_before_ply(pgn_text,ply)
    if board.is_game_over(claim_draw=False):
        raise ValueError("TERMINAL_ORIGINAL_POSITION")
    opts={"Threads":1,"Hash":16}
    if disable_nnue:opts["Use NNUE"]=False
    with chess.engine.SimpleEngine.popen_uci(engine_path) as eng:
        eng.configure(opts)
        scout=_engine_rows(eng,board,scout_depth,3)
    rival=next((r for r in scout if r["uci"]!=played.uci()),None)
    if rival is None:
        raise ValueError("NO_SECOND_LEGAL_SOURCE_SCOUT_CANDIDATE")
    rival_move=chess.Move.from_uci(rival["uci"])
    if rival_move not in board.legal_moves:raise ValueError("SOURCE_SCOUT_RIVAL_NOT_LEGAL")
    with chess.engine.SimpleEngine.popen_uci(engine_path) as eng:
        eng.configure(opts)
        pair=_engine_rows(eng,board,pair_depth,2,root_moves=[played,rival_move])
    if len(pair)!=2 or {c["uci"] for c in pair}!={played.uci(),rival["uci"]}:
        raise ValueError("NATIVE_PAIR_NOT_COMPLETE")
    moment=_focussed_i9_verified_moment(board,played,pair,ply)
    compiled=compile_evidence(moment)
    return {
        "schema":"c3x-ecl-focus-original-source-two-rival-v1",
        "source":"LOCAL_USER_SUPPLIED_PGN",
        "source_executable_path":engine_path,
        "source_revision":"EXTERNAL_INVOKING_USER_MUST_VERIFY",
        "focused_ply":ply,"fen":board.fen(),
        "played_uci":played.uci(),"played_san":board.san(played),
        "source_scout_depth":scout_depth,"original_source_scout":scout,
        "source_selected_distinct_rival":rival["uci"],
        "restricted_pair_depth":pair_depth,"restricted_two_rival_source":pair,
        "legacy_I9_firewall_pass":moment["firewall"]["pass"],
        "legacy_I7_realization_pass":moment["realization_verification"]["pass"],
        "ecl":compiled,
        "new_causal_claim_authorized":False,
        "improvement_against_large_LM":None,
        "human_effect":None,
        "chess_truth_claim":None
    }

def main():
    ap=argparse.ArgumentParser(description="C3X ECL: explain one played PGN move against original engine-chosen rival")
    ap.add_argument("--pgn",required=True)
    ap.add_argument("--ply",type=int,required=True)
    ap.add_argument("--engine",required=True)
    ap.add_argument("--scout-depth",type=int,default=9)
    ap.add_argument("--pair-depth",type=int,default=12)
    ap.add_argument("--disable-nnue",action="store_true")
    ap.add_argument("--out-json",required=True)
    ap.add_argument("--out-markdown")
    a=ap.parse_args()
    result=run_focussed_pgn(Path(a.pgn).read_text(encoding="utf-8"),
        a.engine,a.ply,scout_depth=a.scout_depth,pair_depth=a.pair_depth,
        disable_nnue=a.disable_nnue)
    Path(a.out_json).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.out_markdown:
        text=result["ecl"].get("text_ko") or "판단 보류: "+result["ecl"]["reason"]
        Path(a.out_markdown).write_text(
            "# C3X ECL — 실제 대국의 지정된 수\n\n"
            +f"- Ply: {a.ply}; played: {result['played_san']}; rival: {result['source_selected_distinct_rival']}\n"
            +"- 권위: 제한된 원본 엔진 후보 비교만. 인과 증명서 및 객관적 최선수 증명 아님.\n\n"+text+"\n",
            encoding="utf-8")
    print("C3X_ECL_FOCUS",result["played_san"],result["source_selected_distinct_rival"],result["ecl"]["verdict"])

if __name__=="__main__":main()
