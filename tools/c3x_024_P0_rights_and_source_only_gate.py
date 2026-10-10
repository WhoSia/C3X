#!/usr/bin/env python3
"""C3X 0.24 P0 rights-aware provenance and minimum research-source validator.

Validates locally derived Lichess broadcast positions; this is NOT a legal
opinion, blanket redistribution permission or an engine outcome certificate.
"""
import argparse,hashlib,json,re
from pathlib import Path
import chess

SCHEMA="c3x024-P0-blind-Aug2025-broadcast16-before-any-native-treatment-v1"
URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2025-08.pgn.zst"
ROW_KEYS={"id","source_game_sha256","source_ordinal",
          "source_ply_before_original_move","fen4","played_legal_move_uci",
          "native_move","root_legal_move_count","source_halfmove_clock",
          "source_fullmove_number","engine_outcomes_seen"}
DENY={"source_headers","White","Black","full_original_mainline_uci",
      "game_url","player_name","game_pgn","PGN","GameUrl",
      "Site","Event","source_player_name","TWIC_original_PGN","source_original_mainline_uci"}
HEX=re.compile(r"^[0-9a-f]{64}$")

def audit(d):
    fail=[]
    if d.get("schema")!=SCHEMA:fail.append("UNRECOGNISED_SOURCE_SCHEMA")
    if d.get("source_archive_url")!=URL:fail.append("WRONG_ORIGIN_URL")
    if d.get("license")!="CC BY-SA 4.0":fail.append("LICENCE_MISSING")
    if d.get("license_url")!="https://creativecommons.org/licenses/by-sa/4.0/":
        fail.append("LICENCE_URL_MISMATCH")
    if d.get("phase")!="SOURCE_ONLY_FROZEN_BEFORE_ENGINE_OR_INTERVENTION":
        fail.append("TREATMENT_OR_ENGINE_PHASE_LEAK")
    if d.get("source_only_no_stockfish_used") is not True or \
       d.get("TT_FIRST_interventions")!=0 or d.get("SEE_forced_interventions")!=0 or \
       d.get("treatment_outcomes_seen") is not False:
        fail.append("ENGINE_OR_TREATMENT_USED_BEFORE_FREEZE")
    if not HEX.fullmatch(d.get("original_compressed_source_sha256","")):
        fail.append("SOURCE_ARCHIVE_SHA_MISSING")
    history=d.get("historical_source_receipts")
    if not isinstance(history,dict) or len(history)<11 or any(
         not HEX.fullmatch(v.get("source_json_sha256","")) or v.get("fen4_count",0)<1
         for v in history.values()):
        fail.append("HISTORICAL_SOURCE_EVIDENCE_MISSING")
    if d.get("eligible_before_hash_sort")!=512 or d.get("source_fen_count")!=16 or \
       d.get("max_scan")!=20000 or not 512<=d.get("scanned_game_count",0)<=20000:
        fail.append("ENGINEBLIND_SELECTOR_SIZE_DRIFT")
    rows=d.get("selected")
    if not isinstance(rows,list) or len(rows)!=16:
        return sorted(set(fail+["NO_16_FROZEN_SOURCE_ROWS"]))
    seen_fens=set();seen_games=set();hashes=[]
    for index,r in enumerate(rows,1):
        if not isinstance(r,dict) or set(r)!=ROW_KEYS:
            fail.append("ROW_FIELDS_NOT_MINIMAL")
            continue
        if set(r)&DENY:fail.append("PERSONAL_OR_ORIGINAL_GAME_SOURCE_LEAK")
        s=r["source_game_sha256"]
        if not isinstance(s,str) or not HEX.fullmatch(s):
            fail.append("GAME_SHA_MALFORMED")
            continue
        hashes.append(s)
        fen=r["fen4"]
        if not isinstance(fen,str) or len(fen.split())!=4:
            fail.append("NOT_FEN4")
            continue
        try:
            board=chess.Board(fen+" 0 1")
            move=chess.Move.from_uci(r["played_legal_move_uci"])
            if (not board.is_valid() or move not in board.legal_moves or
                move.promotion or board.legal_moves.count()!=r["root_legal_move_count"] or
                r["native_move"]!=move.from_square*64+move.to_square or
                r["source_ply_before_original_move"]!=30+(int(s[:8],16)%15) or
                r["engine_outcomes_seen"] is not False or
                r["id"]!=index or r["source_halfmove_clock"]<0 or
                r["source_fullmove_number"]<1):
                fail.append("CHESS_LEGALITY_OR_DETERMINISTIC_PLY_DRIFT")
        except (ValueError,TypeError,chess.InvalidMoveError):
            fail.append("BAD_LEGAL_BOARD_OR_PLAYED_MOVE")
        if fen in seen_fens:fail.append("REPEATED_FEN")
        seen_fens.add(fen)
        if s in seen_games:fail.append("REPEATED_GAME")
        seen_games.add(s)
    if hashes!=sorted(hashes):fail.append("HASH_SORT_NOT_DETERMINISTIC")
    # Any originally structured prohibited keys in any nested field: fail-closed.
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in DENY:fail.append("RESTRICTED_OR_FULL_PGN_METADATA")
                walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(d)
    return sorted(set(fail))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--file",required=True)
    p.add_argument("--report",required=True)
    a=p.parse_args()
    f=Path(a.file)
    raw=f.read_bytes()
    if len(raw)>2_500_000:
        raise ValueError("SOURCE_AUDIT_OVERSIZED_DERIVATIVE")
    reasons=audit(json.loads(raw))
    report={"schema":"c3x024-P0-derived-source-licence-and-chess-law-content-scan-v1",
            "filename":f.name,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "status":"SCAN_FAIL" if reasons else "PASS_SOURCE_ONLY_CONTENT_NOT_LEGAL_CLEARANCE",
            "reasons":reasons,"origin":URL,
            "rights":"Lichess broadcast original CC BY-SA 4.0, attribution/alteration notice; no raw complete PGN or private TWIC email",
            "scientific_authority":"BEFORE_ENGINE_ONLY_NOT_PREDICTIVE_M3_TEST"}
    out=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X024_P0_RIGHTS_PROVENANCE_SOURCE_ONLY_GATE",report["status"],reasons,flush=True)
    if reasons:raise ValueError("C3X024_SOURCE_NOT_APPROVED_"+",".join(reasons))
if __name__=="__main__":main()
