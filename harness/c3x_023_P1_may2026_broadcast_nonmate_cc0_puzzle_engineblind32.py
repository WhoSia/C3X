#!/usr/bin/env python3
"""C3X023-P1 engine-free lawful-source 16 May2026 broadcast+16 disjoint CC0 puzzles.

May2026 Lichess broadcast CC BY-SA 4.0, Lichess puzzles CC0. No original
PGN, complete mainline, player metadata or puzzle GameUrl in public output.
Zero Stockfish use until frozen hashes and source provenance reviewed.
"""
import argparse,csv,hashlib,io,json
from pathlib import Path
import chess
import zstandard
from c3x_022_P2_external_TWIC_puzzle_engineblind_selector import prior_fens,HISTORY
from c3x_020_C_March2026_enginefree_blind16 import select_compressed_archive

BROADCAST_URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2026-05.pgn.zst"
PUZZLE_URL="https://database.lichess.org/lichess_db_puzzle.csv.zst"
PUZZLE_SNAPSHOT_SHA="76335bfa7d7c4a7f93c1366d81549e53951ebb79dd43d34904cab8f22d962f8d"
PRIOR32_SHA="ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"
PRIOR_TWIC1664_SHA="3cc4c788eec55960921e653604b2fbb3113163862e2652271b939fb12fb9eeb3"
REGISTRATION="c3x/ontology/c3x-023-P1-independent-licensed-chess-cohorts-and-source-key-aligned-SEE-TT-precommit.md"
FIRST_ELIGIBLE=512
PICK=16
MAX_SCAN_PUZZLE=40000

def digest(raw): return hashlib.sha256(raw).hexdigest()
def frozen(path, expected):
    raw=Path(path).read_bytes()
    if digest(raw)!=expected:raise ValueError("P1_HISTORIC_INPUT_SHA_CHANGED_"+str(path))
    return json.loads(raw)
def source_fens(prior,prior32,twic1664):
    fens,receipts=prior_fens(prior)
    old32=frozen(prior32,PRIOR32_SHA)
    t=frozen(twic1664,PRIOR_TWIC1664_SHA)
    old=old32["ecologies"]["twic"]["selected"]+old32["ecologies"]["lichess_puzzles"]["selected"]
    if len(old)!=32 or len(t["selected"])!=16:raise ValueError("P1_OLD_32_AND_16_COUNT_DRIFT")
    for row in old+t["selected"]:fens.add(row["fen4"])
    receipts["TWIC1656_plus_old_puzzles32"]={"sha256":PRIOR32_SHA,"source_records":32}
    receipts["TWIC1664_dev16"]={"sha256":PRIOR_TWIC1664_SHA,"source_records":16}
    return fens,receipts

def may_source(path,old_fens):
    selected,sha,scanned,rejected=select_compressed_archive(path,old_fens)
    if len(selected)!=PICK:raise ValueError("P1_MAY_SOURCE_COUNT")
    # External upstream selector has original full PGN mainline in memory.
    # Must explicitly DENYLIST raw score, people, headers and game URL.
    clean=[]
    for r in selected:
        moves=r["full_original_mainline_uci"]
        at=r["source_ply_before_original_move"]
        b=chess.Board()
        for u in moves[:at]:
            move=chess.Move.from_uci(u)
            if move not in b.legal_moves:raise ValueError("MAY_CHESS_LEGALITY_DRIFT")
            b.push(move)
        f=" ".join(b.fen(en_passant="fen").split()[:4])
        if f!=r["fen4"] or b.legal_moves.count()!=r["source_root_legal_count"]:
            raise ValueError("MAY_ENGINE_FREE_MOVE_CENSUS_DRIFT")
        clean.append({
           "id":r["id"],"fen4":r["fen4"],
           "source_game_sha256":r["source_game_sha256"],
           "source_ordinal":r["source_ordinal"],
           "source_ply_before_original_move":at,
           "played_legal_move_uci":r["played_legal_move_uci"],
           "native_move":r["native_move"],
           "source_root_legal_count":r["source_root_legal_count"],
           "source_halfmove_clock":b.halfmove_clock,
           "source_fullmove_number":b.fullmove_number,
           "CC_BY_SA_4_0_source":BROADCAST_URL
        })
    if len({x["fen4"] for x in clean})!=PICK or any(x["fen4"] in old_fens for x in clean):
        raise ValueError("MAY_HISTORY_OVERLAP")
    return clean,{"source_file_SHA256":sha,"scanned_games":scanned,
                   "eligible_before_hash_sort":FIRST_ELIGIBLE,
                   "exclusion_reasons":rejected,"license":"CC BY-SA 4.0",
                   "attribution":"Lichess broadcasts 2026-05",
                   "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
                   "attribution_original_source":BROADCAST_URL,
                   "changed":"Original broadcast PGN truncated to SHA-defined chess root only; player names, game headers and full score omitted"}

def puzzles_nonmate(path, history):
    data=Path(path)
    actual_sha=digest(data.read_bytes())
    if actual_sha!=PUZZLE_SNAPSHOT_SHA:
        raise ValueError("PUZZLE_SNAPSHOT_CHANGED_BEFORE_NATIVE__DO_NOT_RELABEL_BLIND")
    candidates=[];seen_id=set();seen_fen=set();scanned=0;reject={}
    def bad(reason):reject[reason]=reject.get(reason,0)+1
    with data.open("rb") as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with io.TextIOWrapper(stream,encoding="utf-8",errors="strict",newline="") as fp:
                r=csv.DictReader(fp)
                require={"PuzzleId","FEN","Moves","Themes","Rating"}
                if not require.issubset(r.fieldnames or []):raise ValueError("PUZZLE_CSV_SCHEMA")
                while scanned<MAX_SCAN_PUZZLE and len(candidates)<FIRST_ELIGIBLE:
                    try:row=next(r)
                    except StopIteration:break
                    scanned+=1
                    if row["PuzzleId"] in seen_id:
                        bad("DUPLICATE_PUZZLE_ID");continue
                    seen_id.add(row["PuzzleId"])
                    themes=set(row["Themes"].split())
                    if any("mate" in x.lower() for x in themes):
                        bad("MATE_THEME_EXCLUDED");continue
                    move_uci=row["Moves"].split()
                    if len(move_uci)<2:
                        bad("SHORT_PUZZLE");continue
                    try:
                        board=chess.Board(row["FEN"])
                        if not board.is_valid():raise ValueError("INVALID_BOARD")
                        script=[chess.Move.from_uci(m) for m in move_uci]
                        if script[0] not in board.legal_moves:
                            raise ValueError("ILLEGAL_OPPONENT_MOVE")
                        board.push(script[0])
                        if script[1] not in board.legal_moves or script[1].promotion:
                            raise ValueError("ILLEGAL_SOLVER_MOVE")
                        if board.legal_moves.count()<3:
                            raise ValueError("TOO_FEW_LEGAL")
                        fen4=" ".join(board.fen(en_passant="fen").split()[:4])
                        if fen4 in history or fen4 in seen_fen:
                            raise ValueError("HISTORICAL_FEN")
                        for m in script[1:]:
                            if m not in board.legal_moves:raise ValueError("ILLEGAL_SCRIPT")
                            board.push(m)
                        root=chess.Board(row["FEN"])
                        root.push(script[0])
                        # Classify no immediate available checkmate-in-one as source-only.
                        for m in root.legal_moves:
                            root.push(m)
                            ismate=root.is_checkmate()
                            root.pop()
                            if ismate:raise ValueError("MATE_IN_ONE_EXCLUDED")
                        seen_fen.add(fen4)
                        fingerprint=digest((row["PuzzleId"]+"|"+fen4).encode())
                        candidates.append({"id":None,"fen4":fen4,
                          "source_game_sha256":fingerprint,
                          "source_puzzle_id":row["PuzzleId"],
                          "source_ordinal":scanned,
                          "played_legal_move_uci":script[1].uci(),
                          "native_move":script[1].from_square*64+script[1].to_square,
                          "source_root_legal_count":root.legal_moves.count(),
                          "source_halfmove_clock":root.halfmove_clock,
                          "source_fullmove_number":root.fullmove_number,
                          "source_ply_before_original_move":1,
                          "puzzle_themes":sorted(themes),
                          "puzzle_rating":row["Rating"],
                          "original_solver_solution_used_to_define_F_order":True,
                          "source_moves_sha256":digest(row["Moves"].encode()),
                          "CC0_source":PUZZLE_URL})
                    except (ValueError,chess.InvalidMoveError):
                        bad("BROKEN_OR_OVERLAPPING_OR_MATE_PUZZLE");continue
    if len(candidates)!=FIRST_ELIGIBLE:
        raise ValueError("P1_PUZZLE_NONMATE_ELIGIBLE_512_NOT_FOUND_"+str(len(candidates)))
    selected=sorted(candidates,key=lambda x:x["source_game_sha256"])[:PICK]
    for idx,row in enumerate(selected,1):row["id"]=idx
    if len({x["fen4"] for x in selected})!=PICK:raise ValueError("P1_PUZZLE_DUPLICATE")
    return selected,{"source_file_SHA256":actual_sha,"scanned_puzzles":scanned,
      "eligible_before_hash_sort":FIRST_ELIGIBLE,
      "reject_counts":reject,"license":"CC0",
      "license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
      "original_source":PUZZLE_URL,
      "no_gameURL_or_players_redistributed":True}

def create(may,puzzle,prior,prior32,twic1664):
    old,history=source_fens(prior,prior32,twic1664)
    broadcast,meta_b=may_source(may,old)
    puzzle_rows,meta_p=puzzles_nonmate(puzzle,old|{r["fen4"] for r in broadcast})
    if len({r["fen4"] for r in broadcast+puzzle_rows})!=32:raise ValueError("P1_SOURCE_DISJOINTNESS")
    result={"schema":"c3x023-P1-licensed-independent-May-broadcast-and-disjoint-CC0-nonmate-puzzles-v1",
      "phase":"SOURCE_ONLY__NO_ENGINE_OR_NATIVE_RESULT_YET",
      "precommit":REGISTRATION,"historical_source_provenance":history,
      "old_unique_position_count":len(old),
      "count":32,"per_ecology": {
       "may2026_broadcast":{"selected":broadcast,"source":meta_b},
       "lichess_CC0_nonmate_puzzles":{"selected":puzzle_rows,"source":meta_p}},
      "root_F_source":"broadcast actual played legal UCI; puzzle prepublished solver solution UCI (not an independent prediction)",
      "licenses_explicitly_distinct":["CC BY-SA 4.0","CC0"],
      "source_only_no_stockfish_used":True,
      "public_release_policy":"BY-SA credit/source/license and change notice for broadcast; CC0 puzzle; no raw original PGN or original full mainlines; no third-party player names"}
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--may",required=True);a.add_argument("--puzzles",required=True)
    a.add_argument("--old32",required=True);a.add_argument("--oldtwic1664",required=True)
    for name in HISTORY:a.add_argument("--"+name,required=True)
    a.add_argument("--out",required=True)
    q=a.parse_args()
    out=create(q.may,q.puzzles,{n:getattr(q,n) for n in HISTORY},
               q.old32,q.oldtwic1664)
    p=Path(q.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X023_P1_BEFORE_NATIVE_CC_BY_SA_MAY_CC0_NONMATE_NEW32",
          out["count"],len(out["per_ecology"]["may2026_broadcast"]["selected"]),
          len(out["per_ecology"]["lichess_CC0_nonmate_puzzles"]["selected"]),
          out["per_ecology"]["may2026_broadcast"]["source"]["source_file_SHA256"],
          out["per_ecology"]["lichess_CC0_nonmate_puzzles"]["source"]["source_file_SHA256"],
          hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
