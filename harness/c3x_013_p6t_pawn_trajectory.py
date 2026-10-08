#!/usr/bin/env python3
"""P6-T: frozen source full-game pawn-status trajectory, no engine/causal labels."""
import argparse,hashlib,io,json
from pathlib import Path
import chess,chess.pgn
from c3x_explain.concepts import snapshot
from harness.c3x_013_p5_source_partition import extract

PLY=[16,32,48,64,80,100]
def status(board):
    w=snapshot(board,chess.WHITE)
    b=snapshot(board,chess.BLACK)
    return {"white_passed":w["own_passed_pawn_count"],"black_passed":b["own_passed_pawn_count"],
            "white_isolated":w["own_isolated_pawn_count"],"black_isolated":b["own_isolated_pawn_count"]}

def one_game(row):
    game=chess.pgn.read_game(io.StringIO(row["raw"].decode("utf8","replace")))
    rec={"broadcast":row["broadcast"],"game_url":row["game_url"],
         "source_sha256":row["sha"]}
    if not game or game.errors:
        rec.update({"status":"HOLD_PGN_OR_VARIANT","error_type":[type(e).__name__ for e in
                    (game.errors if game else [])[:3]]});return rec
    board=game.board()
    snapshots={}
    n=0;quiet=0;coactivation=0;own_activation=0;opp_activation=0
    violations=[]
    for move in game.mainline_moves():
        n+=1
        if move not in board.legal_moves:
            rec.update({"status":"HOLD_ILLEGAL_MOVE","at_ply":n});return rec
        moving=board.piece_at(move.from_square)
        is_quiet_pawn=bool(moving and moving.piece_type==chess.PAWN and
                           not board.is_capture(move) and not move.promotion)
        before=status(board) if is_quiet_pawn else None
        mover=moving.color if moving else None
        board.push(move)
        if not board.is_valid():
            rec.update({"status":"HOLD_INVALID_BOARD","at_ply":n});return rec
        if is_quiet_pawn:
            quiet+=1
            after=status(board)
            oc="white" if mover else "black"
            ec="black" if mover else "white"
            di=after[oc+"_isolated"]-before[oc+"_isolated"]
            dp=after[oc+"_passed"]-before[oc+"_passed"]
            dq=after[ec+"_passed"]-before[ec+"_passed"]
            if di!=0 or dp not in (0,1) or dq<0:
                violations.append({"ply":n,"uci":move.uci(),"isolated_delta":di,
                                   "own_passed_delta":dp,"opp_passed_delta":dq})
            own_activation+=int(dp>0)
            opp_activation+=int(dq>0)
            coactivation+=int(dp>0 and dq>0)
        if n in PLY:snapshots[str(n)]=status(board)
    rec.update({"status":"LEGAL_FULL_GAME","ply_count":n,"snapshots":snapshots,
                "quiet_nonpromoting_noncapture_pawn_pushes":quiet,
                "own_passed_activation_pushes":own_activation,
                "opponent_passed_activation_pushes":opp_activation,
                "simultaneous_two_color_activation_pushes":coactivation,
                "invariant_violations":violations})
    return rec

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True);a.add_argument("--output",required=True)
    v=a.parse_args()
    chosen=extract(v.source)
    docs=[one_game(x) for x in chosen]
    valid=[x for x in docs if x["status"]=="LEGAL_FULL_GAME"]
    aggregates={}
    for ply in PLY:
        snap=[x["snapshots"][str(ply)] for x in valid if str(ply) in x["snapshots"]]
        aggregates[str(ply)]={"observed_games":len(snap),
             "any_side_passed":sum(z["white_passed"]>0 or z["black_passed"]>0 for z in snap),
             "both_sides_passed":sum(z["white_passed"]>0 and z["black_passed"]>0 for z in snap),
             "white_passed":sum(z["white_passed"]>0 for z in snap),
             "black_passed":sum(z["black_passed"]>0 for z in snap)}
    out={"schema":"c3x-013-p6t-natural-pawn-trajectory-v1",
         "status":"EXPLORATORY_POST_P5_SAMPLING_AUDIT",
         "frozen_p5_source_sha256":hashlib.sha256(Path(v.source).read_bytes()).hexdigest(),
         "denominator_original_groups":16,"valid_full_game_count":len(valid),
         "source_holds":[{"broadcast":x["broadcast"],"status":x["status"]} for x in docs
                         if x["status"]!="LEGAL_FULL_GAME"],
         "landmarks":aggregates,
         "eligible_quiet_pawn_pushes":sum(x["quiet_nonpromoting_noncapture_pawn_pushes"] for x in valid),
         "own_activation_pushes":sum(x["own_passed_activation_pushes"] for x in valid),
         "opponent_activation_pushes":sum(x["opponent_passed_activation_pushes"] for x in valid),
         "coactivation_pushes":sum(x["simultaneous_two_color_activation_pushes"] for x in valid),
         "invariance_violations":[{"broadcast":x["broadcast"],"errors":x["invariant_violations"]}
                                  for x in valid if x["invariant_violations"]],
         "games":docs,"causal_explanation_authority":False,"human_outcome":None}
    Path(v.output).parent.mkdir(parents=True,exist_ok=True)
    Path(v.output).write_text(json.dumps(out,indent=2)+"\n")
    print("P6_T_NATURAL_GAME_DENOMINATORS",len(valid),aggregates)
    print("P6_T_QUIET_PAWN_ACTIVATIONS",out["eligible_quiet_pawn_pushes"],
          out["own_activation_pushes"],out["opponent_activation_pushes"],out["coactivation_pushes"])
    assert len(chosen)==16 and not out["invariance_violations"]
    if not valid:raise SystemExit("NO_VALID_P6_TRAJECTORY_GAMES")
if __name__=="__main__":main()
