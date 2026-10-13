"""C3X I10-P5 independently new 2026-09 Olympiad PGN byte/legality preseal.

NO chess engine is loaded. Original Lichess round is a public attributed,
finished 2026 Olympiad round and not present in prior project archive.
Original raw PGN and game identities are preserved only in CI artefact.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import urllib.request
from pathlib import Path
import chess
import chess.pgn

SOURCE="https://lichess.org/api/broadcast/round/DfnuMSan.pgn"
ATTRIBUTION="Lichess 2026 September 46th FIDE Chess Olympiad Samarkand Open Matches 1-12 Round 1; CC BY-SA 4.0 broadcast data"

def freeze(source:bytes,*,count:int=8,expected_sha256:str|None=None)->tuple[dict,list[str]]:
    sha=hashlib.sha256(source).hexdigest()
    if expected_sha256 is not None and sha!=expected_sha256:
        raise ValueError("ORIGINAL_BROADCAST_BYTES_CHANGED_OR_WRONG_ENDPOINT")
    if len(source)<1500 or len(source)>3_000_000:
        raise ValueError("SOURCE_LENGTH_OR_SIZE_UNEXPECTED")
    txt=source.decode("utf-8-sig")
    stream=io.StringIO(txt)
    all_games=[]
    while True:
        game=chess.pgn.read_game(stream)
        if game is None:break
        if game.errors:raise ValueError("ORIGINAL_PGN_PARSE_ERRORS")
        moves=list(game.mainline_moves())
        if len(moves)<35:continue
        # Preoutcome game-selection rule: ordinal first-eligible only, no engine,
        # annotation, score, player ranking, chess result or game-ending analysis.
        board=game.board()
        for m in moves:
            if m not in board.legal_moves:
                raise ValueError("INCONSISTENT_REPLAY")
            board.push(m)
        all_games.append(game)
    if len(all_games)<count:
        raise ValueError("ORIGINAL_SOURCE_INSUFFICIENT_ELIGIBLE_GAMES")
    selected=all_games[:count]
    serialized=[]
    games=[]
    for i,g in enumerate(selected):
        stream=io.StringIO()
        exp=chess.pgn.StringExporter(headers=True,variations=False,comments=False,columns=80)
        pgn=g.accept(exp)+"\n"
        serialized.append(pgn)
        moves=list(g.mainline_moves())
        # Use all moves UCI in exact order; game hash is computed on these
        # identity-bearing root moves with full initial FEN.
        game_hash=hashlib.sha256((g.board().fen()+" "+" ".join(m.uci() for m in moves)).encode()).hexdigest()
        games.append({
            "source_ordinal":i,
            "source_event":g.headers.get("Event"),
            "source_round":g.headers.get("Round"),
            "source_white":g.headers.get("White"),
            "source_black":g.headers.get("Black"),
            "game_id":game_hash[:20],
            "game_ucl_sha256":game_hash,
            "actual_plies":len(moves),
            "pgn_reexport_sha256":hashlib.sha256(pgn.encode()).hexdigest(),
            "game_label_seen_by_learner":False,
            "subject_to_future_engine_selection":False,
        })
    result={
        "schema":"c3x-i10-p5-2026-olympiad-untouched-source-freeze-v1",
        "source_url":SOURCE,
        "source_attribution_and_license":ATTRIBUTION,
        "raw_original_pgn_sha256":sha,
        "raw_original_bytes":len(source),
        "selection":"FIRST_EIGHT_CHESS_LEGAL_GAMES_AT_LEAST_35_PLIES_AS_BROADCAST_LISTED_BEFORE_ENGINE",
        "chosen_count":len(games),
        "selected_game_groups":games,
        "train_test_game_split":"FIRST_4_TRAIN_LAST_4_TEST_PREDECLARED_UNCHANGED",
        "outcome_selection_used":False,
        "engine_scoring_used":False,
        "prior_C3X_development_Kasparov_Morphy_overlap":False,
        "external_new_tournament_ECOLOGY_not_HUMAN_heldout":True,
        "data_rights":"CC BY-SA 4.0; attribute Lichess broadcast",
        "future_science":"Independent from historical P4 two-game development ONLY; prospective preseal before native source operation."
    }
    return result,serialized

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--source-file",help="offline replay existing exact source PGN bytes")
    p.add_argument("--expected-sha256")
    a=p.parse_args()
    if a.source_file:
        raw=Path(a.source_file).read_bytes()
    else:
        req=urllib.request.Request(SOURCE,headers={
             "User-Agent":"C3XResearch/0.26 chess academic reproducibility (read-only)",
             "Accept":"application/x-chess-pgn,text/plain"})
        with urllib.request.urlopen(req,timeout=35) as response:
            if response.status!=200:raise ValueError("LICHESS_SOURCE_HTTP_STATUS")
            raw=response.read(3_000_001)
    result,games=freeze(raw,expected_sha256=a.expected_sha256)
    root=Path(a.out);root.mkdir(parents=True,exist_ok=True)
    (root/"source-2026-olympiad-r1-original.pgn").write_bytes(raw)
    (root/"source-2026-olympiad-preseal.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    for info,pgn in zip(result["selected_game_groups"],games):
        (root/("game-"+info["game_id"]+".pgn")).write_text(pgn,encoding="utf-8")
    print("C3X_P5_NEW_OLYMPIAD_SOURCE_PRESEAL",result["raw_original_pgn_sha256"],
          len(result["selected_game_groups"]),[(x["game_id"],x["actual_plies"]) for x in result["selected_game_groups"]])

if __name__=="__main__":main()
