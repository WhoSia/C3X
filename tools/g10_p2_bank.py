from __future__ import annotations
import argparse,json
from pathlib import Path
import chess,chess.pgn
from c3x_g10.question_identity import P2_POLICY,board_key,phase_from_board,stable_hash

def gid(g):
    h=g.headers
    return "|".join(str(h.get(k,"?")) for k in ("Event","Site","Date","Round","White","Black"))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pgn",required=True);ap.add_argument("--out",required=True);ap.add_argument("--game-cap",type=int,default=240);a=ap.parse_args()
    seen=set();cand=[];games=0
    with open(a.pgn,encoding="utf-8",errors="replace") as f:
        while games<a.game_cap:
            g=chess.pgn.read_game(f)
            if g is None:break
            if g.headers.get("Variant","Standard") not in ("Standard","From Position"):continue
            moves=list(g.mainline_moves())
            if len(moves)<20:continue
            games+=1;board=g.board();before=[];game=gid(g)
            for ply,m in enumerate(moves,1):
                if ply>=4 and not board.is_game_over():
                    key=board_key(board.fen())
                    if key not in seen:
                        seen.add(key)
                        cand.append({"case_id":stable_hash({"gid":game,"ply":ply,"key":key})[:24],"game_id":game,"event":g.headers.get("Event"),"site":g.headers.get("Site"),"date":g.headers.get("Date"),"round":g.headers.get("Round"),"white":g.headers.get("White"),"black":g.headers.get("Black"),"initial_fen":g.headers.get("FEN") or chess.STARTING_FEN,"moves_before_uci":list(before),"ply":ply,"position_fen":board.fen(),"position_key":key,"played_uci":m.uci(),"played_san":board.san(m),"phase":phase_from_board(board),"source_month":"2026-09","source_id":"P2_LICHESS_BROADCAST_2026_09","engine_outcomes_opened":False,"maia_outcomes_opened":False,"certificate_outcomes_opened":False})
                before.append(m.uci());board.push(m)
    selected=[];per_game={}
    for phase,target in P2_POLICY["phase_quota"].items():
        pool=sorted((x for x in cand if x["phase"]==phase),key=lambda x:stable_hash(x["case_id"]))
        count=0
        for x in pool:
            if per_game.get(x["game_id"],0)>=P2_POLICY["max_positions_per_game"]:continue
            selected.append(x);per_game[x["game_id"]]=per_game.get(x["game_id"],0)+1;count+=1
            if count>=target:break
        if count<target:raise SystemExit(f"INSUFFICIENT_PHASE_SUPPORT {phase} {count}<{target}")
    selected=sorted(selected,key=lambda x:x["case_id"])
    p={"schema":"c3x-g10-p2-position-bank-v1","source_month":"2026-09","fresh_disjoint":True,"p1_case_ids_used":[],"selection_inputs":["PGN identity","phase","stable hash"],"engine_outcomes_opened":False,"maia_outcomes_opened":False,"certificate_outcomes_opened":False,"games_scanned":games,"candidate_position_n":len(cand),"cases":selected}
    p["bank_sha256"]=stable_hash(selected)
    Path(a.out).write_text(json.dumps(p,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("G10_P2_BANK_FREEZE_PASS",len(selected),p["bank_sha256"],{ph:sum(x["phase"]==ph for x in selected) for ph in P2_POLICY["phase_quota"]})
if __name__=="__main__":main()
