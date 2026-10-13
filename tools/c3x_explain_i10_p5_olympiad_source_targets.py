"""C3X P5 PRE-ENGINE sealed source root intervention cohort, eight 2026 Olympiad games.

Only prior PGN chess legality/move facts are used for target selection. No
engine score, PV or even binary is present. Full historical startpos moves are
preserved for native UCI replay. UCI raw native encoding excludes castle/EP/
promotion and incompatible alternative histories.
"""
from __future__ import annotations
import argparse, hashlib, io, json
from pathlib import Path
import chess, chess.pgn

SOURCE_SHA="363c4fd6d1bd17ead0890a068c14838296c2393f6de8469633edc0e1bc126a07"
GAME_SHA=[
"1e762b0287736a854fd6","19abf1f7f89391235d1b","f05846eaf2d4b3908401",
"2c3d71d1707446e48ffb","a6f468519beb081daa66","a7ab515ec2727f70d9b9",
"80920bed08fbe6c3dfd9","f5e5cb9790c26c7d69b8"]

def native_uci(move:str)->int:
    if len(move)!=4 or any(move[i] not in "abcdefgh" for i in (0,2)) or any(move[i] not in "12345678" for i in (1,3)):
        raise ValueError("SOURCE_PATCH_TARGET_SPECIAL_UCI_NOT_ALLOWED")
    fr=(ord(move[0])-97)+8*(int(move[1])-1)
    to=(ord(move[2])-97)+8*(int(move[3])-1)
    return fr*64+to

def target(pgn:str,game_id:str)->dict:
    g=chess.pgn.read_game(io.StringIO(pgn))
    if g is None or g.errors:raise ValueError("INVALID_FROZEN_PGN")
    b=g.board()
    moves=list(g.mainline_moves())
    records=[]
    for ply,m in enumerate(moves,1):
        if not b.is_valid() or m not in b.legal_moves:raise ValueError("ILLEGAL_REPLAY")
        if 16<=ply<=min(45,len(moves)-1) and b.legal_moves.count()>=3 and not (
            b.is_castling(m) or b.is_en_passant(m) or m.promotion):
            score=(3 if b.gives_check(m) else 0)+(2 if b.is_capture(m) else 0)
            records.append({"ply":ply,"uci":m.uci(),"san":b.san(m),
                            "fen4":" ".join(b.fen().split()[:4]),
                            "full_fen":b.fen(),"native_move":native_uci(m.uci()),
                            "context_pre_moves":[z.uci() for z in moves[:ply-1]],
                            "history_move_count":ply-1,
                            "engine_blind_chess_salience":score,
                            "opponent_actual_next_uci":moves[ply].uci()})
        b.push(m)
    if not records:raise ValueError("NO_PREDECLARED_SOURCE_ELIGIBLE_PLY")
    row=sorted(records,key=lambda x:(-x["engine_blind_chess_salience"],x["ply"]))[0]
    row["game_id"]=game_id
    row["mode_preseal"]="ONE_PREOUTCOME_LEGAL_NORMAL_MOVE_PER_NEW_GAME"
    row["original_numerical_engine_result_exposed_preseal"]=False
    row["source_semantic_chess_concept_label"]=None
    return row

def make_manifest(folder:Path,original_pgn:Path)->dict:
    raw=original_pgn.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError("ORIGINAL_2026_BROADCAST_SHA_CHANGED")
    rows=[]
    for i,gid in enumerate(GAME_SHA):
        p=folder/("game-"+gid+".pgn")
        if not p.is_file():raise ValueError("EXPECTED_FROZEN_GAME_MISSING")
        row=target(p.read_text(encoding="utf-8"),gid)
        row["source_ordinal"]=i
        row["split"]="TRAIN" if i<4 else "EVAL"
        rows.append(row)
    if len({x["fen4"] for x in rows})!=8:raise ValueError("SOURCE_FEN_COLLISION")
    return {
      "schema":"c3x-i10-p5-new-Olympiad-eight-game-pre-engine-native-source-intervention-cohort-v1",
      "date":"2026-10-13",
      "source_round":"2026 FIDE Olympiad Open Matches 1-12 Round 1",
      "original_source_sha256":SOURCE_SHA,
      "source_license":"Lichess CC BY-SA 4.0 broadcast attribution",
      "selection":"HIGHEST_PLAYED_MOVE_PRIOR_CHESS_FACT_SALIENCE_TIE_EARLIEST_PLY_16_TO_45",
      "prior_two_development_games_excluded":True,
      "engine_search_not_yet_executed_at_preselection":True,
      "source_original_engine_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "intervention":"C3X016 P4 exact ROOT_MOVES first-cycle pre-root reorder O/F/Z, original legal set preserved",
      "negative_controls":["O patched vs unmodified original","Z targeted impossible sentinel no-contact","F true physical event contact and verified root reorder only"],
      "historic_full_UCI_startpos_moves_replayed":True,
      "training_groups":[x["game_id"] for x in rows[:4]],
      "evaluation_groups":[x["game_id"] for x in rows[4:]],
      "positions":rows,
      "forbidden_claims":["high_level_chess_semantic_causality","meaning_of_engine_source_cause_for_human","human_utility","true_best_move","elo_gain"]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",required=True)
    a.add_argument("--original-pgn",required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    x=make_manifest(Path(args.input),Path(args.original_pgn))
    Path(args.out).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
    print("C3X_P5_PREENGINE_EIGHT_FRESH_SOURCE_TARGETS",[(x["game_id"],x["ply"],x["played_san"] if "played_san" in x else x["san"]) for x in x["positions"]])

if __name__=="__main__":main()
