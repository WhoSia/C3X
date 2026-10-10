#!/usr/bin/env python3
"""C3X023 conservative real-byte pre-upload gate, not a legal opinion.

Never authorize TWIC raw ZIP/PGN and full mainline. Restrictive rights alone
cannot be replaced by a public download URL. Scan zip members in memory and
all candidate logs; refuse unsupported compressed/binary payloads by default.
"""
import argparse
import hashlib
import json
import re
import zipfile
from io import BytesIO
from pathlib import Path

TEXT_SUFFIXES={".json",".md",".txt",".py",".yml",".yaml",".patch",".diff",".csv",".tsv"}
SOURCE_TEXT_SUFFIXES={".pgn",".cbv",".cbh",".cbf",".cbg",".cbp"}
BINARY_SUFFIXES={".zst",".gz",".7z",".rar",".bin",".exe",".so",".dylib",".o"}
PGN_HEADER=re.compile(rb"(?m)^\[(Event|Site|Date|Round|White|Black|Result)\s+\x22[^\r\n]+\x22\]")
TWIC_INDICATOR=re.compile(rb"(?i)(twic1(?:656|664)|theweekinchess|mark crowther)")
MULTI_SCORE=re.compile(rb"(?m)(?:^|\s)1\.\s*(?:[a-zNBRQKO0][a-z0-9+#x=?!-]*)\s+.{20,}",re.IGNORECASE)
TWIC_DERIVED_KEYS=(b'"fen4"',b'"played_legal_move_uci"',b'"source_game_url"',b'"native_move"')

def licensed_lichess_cohort_audit(raw):
    """Provenance-specific review of approved external Lichess extracts only.
    A scan cannot verify upstream licence grants beyond recorded authority."""
    try:
        d=json.loads(raw)
        if d["schema"]!="c3x023-P1-licensed-independent-May-broadcast-and-disjoint-CC0-nonmate-puzzles-v1":
            return ["UNRECOGNISED_LICHESS_LICENSED_EXTRACT"]
        if d.get("phase")!="SOURCE_ONLY__NO_ENGINE_OR_NATIVE_RESULT_YET":
            return ["NONBLIND_LICHESS_EXTRACT"]
        if d.get("source_only_no_stockfish_used") is not True:
            return ["UNVERIFIED_SOURCE_ONLY"]
        ec=d["per_ecology"];broadcast=ec["may2026_broadcast"]
        puzzle=ec["lichess_CC0_nonmate_puzzles"]
        if broadcast["source"].get("license")!="CC BY-SA 4.0" or puzzle["source"].get("license")!="CC0":
            return ["LICENCE_DISAGREEMENT"]
        if broadcast["source"].get("attribution_original_source")!="https://database.lichess.org/broadcast/lichess_db_broadcast_2026-05.pgn.zst":
            return ["OFFICIAL_BROADCAST_PROVENANCE_CHANGED"]
        if puzzle["source"].get("original_source")!="https://database.lichess.org/lichess_db_puzzle.csv.zst":
            return ["OFFICIAL_CC0_PUZZLE_PROVENANCE_CHANGED"]
        if len(broadcast["selected"])!=16 or len(puzzle["selected"])!=16:
            return ["LICENCE_COHORT_DENOMINATOR_DRIFT"]
        rows=broadcast["selected"]+puzzle["selected"]
        if len({x["fen4"] for x in rows})!=32:return ["LICENSED_COHORT_FEN_OVERLAP"]
        blocked=("source_headers","full_original_mainline_uci","source_game_url",
                 "game_url","source_event","source_game_date","White","Black",
                 "GameUrl","source_original_mainline_uci")
        if any(any(x in row for x in blocked) for row in rows):
            return ["PERSONAL_OR_COMPLETE_GAME_DATA_LEAK"]
        if any(len(x["fen4"].split())!=4 or x["source_root_legal_count"]<3 for x in rows):
            return ["MALFORMED_SOURCE_CHESS_POSITION"]
        if len(broadcast["source"].get("source_file_SHA256",""))!=64 or len(puzzle["source"].get("source_file_SHA256",""))!=64:
            return ["UNSEALED_ORIGINAL_SOURCE_BYTES"]
        return []
    except (KeyError,TypeError,ValueError,AttributeError):
        return ["INVALID_LICENSED_SOURCE_JSON"]

def scan_payload(name,raw,kind,depth=0):
    reasons=[]
    ext=Path(name).suffix.lower()
    if depth>4:return ["NESTED_ARCHIVE_DEPTH_LIMIT"]
    if kind=="P4_LICHESS_LICENSED_SOURCE_ONLY":
        return licensed_lichess_cohort_audit(raw) if ext==".json" else ["P4_NON_JSON_SOURCE_NOT_CLEARED"]
    if ext in SOURCE_TEXT_SUFFIXES:return ["RESTRICTED_OR_UNREVIEWED_CHESS_GAME_SOURCE"]
    if ext in BINARY_SUFFIXES:return ["NONTRANSPARENT_BINARY_OR_COMPRESSED_SOURCE"]
    if raw.startswith(b"PK\x03\x04") or ext==".zip":
        try:
            with zipfile.ZipFile(BytesIO(raw)) as z:
                for info in z.infolist():
                    if info.is_dir():continue
                    if info.file_size>12_000_000:
                        reasons.append("UNREVIEWED_LARGE_NESTED_ARCHIVE")
                        continue
                    reasons.extend("ARCHIVE/"+x for x in scan_payload(info.filename,z.read(info),
                                                                          kind,depth+1))
        except (ValueError,zipfile.BadZipFile,RuntimeError):
            reasons.append("MALFORMED_ARCHIVE_UNINSPECTABLE")
        return sorted(set(reasons))
    if raw[:4] == b"\x28\xb5\x2f\xfd":return ["ZSTD_SOURCE_OR_BINARY_NOT_LICENSE_CHECKED"]
    if ext not in TEXT_SUFFIXES:return ["UNREVIEWED_FILE_TYPE"]
    if b"\x00" in raw[:4096]:return ["BINARY_CONTENT_DISGUISED_AS_TEXT"]
    if PGN_HEADER.search(raw):reasons.append("PGN_RECORD_HEADERS_NOT_CLEAR_TO_RELEASE")
    if TWIC_INDICATOR.search(raw) and MULTI_SCORE.search(raw):
        reasons.append("TWIC_RECONSTRUCTABLE_GAME_SEQUENCE")
    if ext==".json" and b"TWIC" in raw.upper() and any(k in raw for k in TWIC_DERIVED_KEYS):
        reasons.append("TWIC_DERIVED_FEN_MOVE_REQUIRES_HUMAN_REVIEW")
    if kind=="P2_AGGREGATE_SUMMARY" and ext in (".py",".patch"):
        reasons.append("WRONG_KIND_FOR_SUMMARY")
    if kind=="P1_SOURCE_POINTER" and ext in (".csv",".tsv"):
        reasons.append("POINTER_TIER_CANNOT_INCLUDE_DATA_ROWS")
    if kind=="P3_LICENSED_DATA":
        reasons.append("P3_REQUIRES_INDIVIDUAL_LICENSE_AND_PERMISSION_REVIEW")
    return sorted(set(reasons))

def audit(paths,kind):
    if kind not in ("P0_AUTHORED_CODE","P1_SOURCE_POINTER",
                    "P2_AGGREGATE_SUMMARY","P3_LICENSED_DATA",
                    "P4_LICHESS_LICENSED_SOURCE_ONLY"):
        raise ValueError("INVALID_RELEASE_TIER")
    result={"schema":"c3x023-public-upload-real-bytes-guard-v1",
            "tier":kind,"status":"HOLD","files":[]}
    for path in paths:
        p=Path(path)
        if not p.is_file():raise ValueError("NOT_A_FILE_"+str(p))
        raw=p.read_bytes()
        flags=scan_payload(p.name,raw,kind)
        result["files"].append({"name":p.name,"sha256":hashlib.sha256(raw).hexdigest(),
                                "bytes":len(raw),"classification":"HOLD" if flags else "SCAN_PASS",
                                "issues":flags})
    result["status"]="SCAN_PASS_NOT_A_LEGAL_LICENSE" if result["files"] and all(
        x["classification"]=="SCAN_PASS" for x in result["files"]) else "HOLD"
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tier",required=True)
    ap.add_argument("--file",action="append",required=True)
    ap.add_argument("--report",required=True)
    a=ap.parse_args()
    result=audit(a.file,a.tier)
    out=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X023_PUBLICATION_RIGHTS_CONTENT_GATE",result["status"],
          [(x["name"],x["issues"]) for x in result["files"]],flush=True)
    if result["status"]!="SCAN_PASS_NOT_A_LEGAL_LICENSE":raise SystemExit(2)
if __name__=="__main__":main()
