#!/usr/bin/env python3
"""R47: source-frozen new development cohort, no source treatments.
Never replaces a case after engine observation. Archive only derived receipts.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import chess
import chess.pgn
from c3x_031_r46_source_admission_audit import read_archive,sha,board_key,group,name
from c3x_030_r33_gate_panel import trial,select
CENSUS="8506fa39511a15543e382eae0667d91e6ecbc492dc89f281f1c3862a72ca150e"
BIN="ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"
OLD="78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb"
NET="5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"

def require(ok,reason):
    if not ok:raise ValueError(reason)

def load_frozen(census,folder):
    require(sha(census.read_bytes())==CENSUS,"R46b census drift")
    c=json.loads(census.read_text())
    rows=c["provisional_sample"]
    require(len(rows)==64 and len({r["macro_family"] for r in rows})==24,"cohort count")
    require(len({r["game_sha256"] for r in rows})==len({r["board_sha256"] for r in rows})==64,"duplicate freeze")
    require(c["engine_searches"]==c["treatment_outcomes"]==0,"not preoutcome")
    stream,receipt=read_archive(folder,1672)
    require(receipt["zip_sha256"]==c["new_issue"]["zip_sha256"] and receipt["pgn_sha256"]==c["new_issue"]["pgn_sha256"],"publisher drift")
    by_ord={r["ordinal"]:r for r in rows}
    cases={}
    ordinal=0
    while (g:=chess.pgn.read_game(stream)) is not None:
        ordinal+=1
        if ordinal not in by_ord:continue
        r=by_ord[ordinal]
        b=g.board()
        require(not g.errors and b.fen()==chess.STARTING_FEN and not b.chess960,"invalid selected game")
        full=[m.uci() for m in g.mainline_moves()]
        require(sha(" ".join(full).encode())==r["game_sha256"],"game drift")
        require(name(g.headers["Event"])==r["event"] and group(g.headers["Event"])==r["macro_family"],"family drift")
        for m in full[:r["ply"]]:b.push_uci(m)
        require(sha(board_key(b).encode())==r["board_sha256"] and b.legal_moves.count()>=2 and not b.is_game_over(),"board drift")
        cases[ordinal]={**r,"moves":full[:r["ply"]]}
    require(ordinal==8117 and len(cases)==64,"missing selected games")
    return [dict(cases[r["ordinal"]],id=f"R47-{i:03}") for i,r in enumerate(rows,1)]

def main():
    p=argparse.ArgumentParser()
    for k in ("census","folder","old","patch","net","out","receipt"):p.add_argument(k,type=Path)
    a=p.parse_args()
    for k,h in (("old",OLD),("patch",BIN),("net",NET)):
        require(sha(getattr(a,k).read_bytes())==h,"binary/network drift "+k)
    cases=load_frozen(a.census,a.folder)
    a.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for case in cases:
        i=case["id"]
        old=trial(a,case,i+"/old",binary=a.old,observer=False)
        off=trial(a,case,i+"/off",binary=a.patch,observer=False)
        seen=trial(a,case,i+"/seen",binary=a.patch,observer=True)
        require(old["uci"]==off["uci"]==seen["uci"] and old["proof"]==off["proof"]==seen["proof"],"native parity "+i)
        nominated=select(seen["events"])
        row={k:case[k] for k in ("id","ordinal","game_sha256","board_sha256","macro_family","ply")}
        # No PGN histories, FENs or complete UCI move lines in public receipt.
        row.update(event_count=len(seen["events"]),targets={k:{"status":"FROZEN_UNTREATED","target":nominated[k]["open"]} if k in nominated else {"status":"NO_ELIGIBLE_EVENT"} for k in ("0","1")},baseline_best=seen["proof"]["best"]["move"],trace_sha256=seen["trace"])
        rows.append(row)
        print("R47_CASE",i,len(seen["events"]),sorted(nominated),flush=True)
    counts=Counter(t["status"] for r in rows for t in r["targets"].values())
    receipt={"source_census_sha256":CENSUS,"scope":"new development cohort, five archived issues plus prior family lists; not globally certified independent","games":64,"families":24,"control_searches":192,"treatment_searches":0,"potential_targets":128,"target_statuses":dict(counts),"cases":rows,"binary_sha256":BIN,"reference_sha256":OLD,"net_sha256":NET}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    a.receipt.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("R47_AGGREGATE",json.dumps({k:v for k,v in receipt.items() if k!="cases"},sort_keys=True),flush=True)
    print("R47_RECEIPT_SHA",sha(a.receipt.read_bytes()),flush=True)
if __name__=="__main__":main()
