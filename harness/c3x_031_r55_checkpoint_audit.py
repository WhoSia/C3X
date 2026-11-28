#!/usr/bin/env python3
"""R55 development-only paired checkpoint audit on the frozen R47 games.
No engines, treatment labels, or independent-cohort claims. No move/FEN output.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import chess.pgn
from c3x_031_r46_source_admission_audit import board_key, read_archive, sha, name, group
from c3x_031_r47_frozen_discovery import CENSUS, require
from c3x_031_r55_checkpoint_policy import choose_checkpoint, legal_checkpoints, distribution, SEED

def main():
    p=argparse.ArgumentParser()
    for k in ("census","folder","out"): p.add_argument(k,type=Path)
    a=p.parse_args()
    require(sha(a.census.read_bytes())==CENSUS,"frozen R46 census drift")
    c=json.loads(a.census.read_text())
    rows=c["provisional_sample"]
    require(len(rows)==64 and len({r["ordinal"] for r in rows})==64,"frozen sample size")
    require(c["engine_searches"]==c["treatment_outcomes"]==0,"source census not preoutcome")
    stream,receipt=read_archive(a.folder,1672)
    require(all(receipt[k]==c["new_issue"][k] for k in ("zip_sha256","pgn_sha256")),"publisher drift")
    by_ord={r["ordinal"]:r for r in rows}
    old_boards={r["board_sha256"] for r in rows}
    audit=[]
    ordinal=0
    while (g:=chess.pgn.read_game(stream)) is not None:
        ordinal+=1
        if ordinal not in by_ord: continue
        old=by_ord[ordinal]
        b=g.board()
        require(not g.errors and b.fen()==chess.STARTING_FEN and not b.chess960,"invalid frozen game")
        moves=list(g.mainline_moves())
        digest=sha(" ".join(m.uci() for m in moves).encode())
        require(digest==old["game_sha256"] and name(g.headers["Event"])==old["event"] and group(g.headers["Event"])==old["macro_family"],"frozen identity drift")
        eligible=legal_checkpoints(b,moves,board_key)
        require(bool(eligible) and eligible[0][0]==old["ply"] and sha(eligible[0][1].encode())==old["board_sha256"],"R46 first-checkpoint mismatch")
        selected=choose_checkpoint(digest,eligible)
        ply,bk=selected
        bh=sha(bk.encode())
        audit.append({"ordinal":ordinal,"game_sha256":digest,"macro_family":old["macro_family"],"old_ply":old["ply"],"ply":ply,"eligible_count":len(eligible),"board_sha256":bh,"same_board":bh==old["board_sha256"],"overlap_frozen_board":bh in old_boards})
    require(ordinal==8117 and len(audit)==64,"denominator mismatch")
    dup=Counter(r["board_sha256"] for r in audit)
    result={"status":"EXPOSED_SOURCE_POLICY_DIAGNOSTIC_NOT_ADMISSION","seed":SEED,"census_sha256":CENSUS,"source_zip_sha256":receipt["zip_sha256"],"engine_searches":0,"treatment_outcomes_read":0,"games":64,"old_distribution":distribution([dict(r,ply=r["old_ply"]) for r in audit]),"new_distribution":distribution(audit),"changed_checkpoint":sum(r["ply"]!=r["old_ply"] for r in audit),"overlap_frozen_boards":sum(r["overlap_frozen_board"] for r in audit),"duplicate_new_board_rows":sum(n-1 for n in dup.values()),"limitations":["same exposed games, not a new cohort","only historical R46 checkpoints; conditional on legal checkpoint availability","no audit against all prior board keys in this paired diagnostic"],"rows":audit}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},sort_keys=True))
if __name__=="__main__": main()
