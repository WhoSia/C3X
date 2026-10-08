#!/usr/bin/env python3
"""P5 source-locked chess board facts; zero causal or human outcome authority."""
import argparse,hashlib,io,json,re,subprocess
from pathlib import Path
import chess,chess.pgn
from c3x_explain.concepts import snapshot

H=lambda b:hashlib.sha256(b).hexdigest()
SRC="27a39d035767a30901b89602f33f2a7b27d4ab5025842071165fa079f8fff1df"
ORDER="7f9e865ced89aa47ed06aac5fa0d40ff02481f8ff4e696f12769fdcffbc9fa1b"
OLD={"247811ab6f13c31a51618fa906af1ed1baf2a01cf77a5b37edf8d3953e33464a",
"1de1ba37d8ed2e33c479e81396156c9a6c267857dfdf34d3eb30e319aa50b525",
"7239f44d0ae01efb88f25fa19885e09d506b0dd36feaaa94b1321578e53205ce",
"a11cfa178ae582b687dff899b0597f40220bb6d3cfca5d84bccd51fca9cf515b",
"55870d60349404f28be36a3303b5ba189643aa2fe05f48e5e4d47a58f73eb8d5",
"ddd6fa66985c2cf546b9ded67afcb17acc79bb86f04f00c0a583f9beaf72831f"}
FEATURES=["own_center_occupancy_count","own_isolated_pawn_count","own_passed_pawn_count"]
def extract(path):
    if H(Path(path).read_bytes())!=SRC:raise ValueError("SOURCE_SHA_MISMATCH")
    raw=subprocess.check_output(["zstd","-dc",str(path)])
    starts=[m.start() for m in re.finditer(rb'(?m)^\[Event "',raw)]
    groups={}
    for i,start in enumerate(starts):
        b=raw[start:starts[i+1] if i+1<len(starts) else len(raw)].strip()
        head=b.split(b"\n\n",1)[0]
        tags={m.group(1).decode():m.group(2).decode("utf8","replace")
              for m in re.finditer(rb'(?m)^\[([^]]+) "([^"]*)"\]',head)}
        group,url=tags.get("BroadcastName"),tags.get("GameURL","")
        if not(tags.get("Date","").startswith("2026.09.") and
               tags.get("Variant")=="Standard" and group and
               url.startswith("https://lichess.org/broadcast/")):continue
        if group not in groups or url<groups[group]["game_url"]:
            groups[group]={"broadcast":group,"game_url":url,"sha":H(b),"raw":b}
    selected=sorted(groups.values(),key=lambda z:(H(z["broadcast"].encode()),z["game_url"]))[:16]
    if len(starts)!=28638 or len(groups)!=299 or H(("\n".join(x["sha"] for x in selected)+"\n").encode())!=ORDER:
        raise ValueError("FROZEN_SELECTION_DRIFT")
    return selected
def court(row):
    game=chess.pgn.read_game(io.StringIO(row["raw"].decode("utf8","replace")))
    if not game or game.errors:return {"status":"HOLD_PGN_OR_VARIANT"}
    board=game.board()
    for index,m in enumerate(game.mainline_moves()):
        if index==32:break
        if m not in board.legal_moves:return {"status":"HOLD_ILLEGAL_MOVE"}
        board.push(m)
    if len(board.move_stack)!=32 or not board.is_valid() or board.is_game_over():
        return {"status":"HOLD_INELIGIBLE_BOARD"}
    fen=board.fen(en_passant="fen")
    fid=H(" ".join(fen.split()[:4]).encode())
    if fid in OLD:return {"status":"HOLD_PRIOR_POSITION"}
    facts=snapshot(board,board.turn)
    return {"status":"BOARD_FACT_ONLY","fen":fen,"fen4_sha256":fid,
            "feature_counts":{k:facts[k] for k in FEATURES},
            "binary_partition":{k:int(facts[k]>0) for k in FEATURES},
            "legal_root_count":board.legal_moves.count()}
def main():
    a=argparse.ArgumentParser();a.add_argument("--source",required=True)
    a.add_argument("--output",required=True);v=a.parse_args()
    rows=[]
    for x in extract(v.source):
        z={"broadcast":x["broadcast"],"game_url":x["game_url"],"raw_segment_sha256":x["sha"]}
        z.update(court(x));rows.append(z)
    seen=set()
    for z in rows:
        k=z.get("fen4_sha256")
        if k in seen:z["status"]="HOLD_DUPLICATE_FEN"
        if k:seen.add(k)
    valid=[z for z in rows if z["status"]=="BOARD_FACT_ONLY"]
    result={"schema":"c3x-013-p5-semantic-source-court-v1","source_sha256":SRC,
            "frozen_selection_sha256":ORDER,"sampled_events":len(rows),
            "counts":{k:sum(z["status"]==k for z in rows) for k in sorted(set(z["status"] for z in rows))},
            "partitions":{k:{"positive":sum(z["binary_partition"][k] for z in valid),
                             "negative":sum(not z["binary_partition"][k] for z in valid)} for k in FEATURES},
            "records":rows,"authority":"BOARD_RULE_ONLY_NO_CAUSAL_OR_HUMAN_CLAIM"}
    Path(v.output).parent.mkdir(parents=True,exist_ok=True)
    Path(v.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("C3X_013_P5",result["counts"],result["partitions"])
    if not valid:raise SystemExit("NO_VALID_P5_WORLDS")
if __name__=="__main__":main()
