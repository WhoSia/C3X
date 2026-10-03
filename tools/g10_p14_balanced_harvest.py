#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,zipfile
from collections import defaultdict,Counter
from pathlib import Path
import chess,chess.pgn

PHASES=("RICH","TRANSITIONAL","REDUCED")
BRANCH=("NARROW","MEDIUM","WIDE")
TACT=("FORCED_CHECK","TACTICAL_AVAILABLE","QUIET_SURFACE")
PIECE_PHASE={chess.KNIGHT:1,chess.BISHOP:1,chess.ROOK:2,chess.QUEEN:4}

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def canonical_fen(b):
    f=b.fen(en_passant="fen").split()
    return " ".join(f[:4])+" 0 1"
def phase(b):
    u=sum(len(b.pieces(pt,c))*w for pt,w in PIECE_PHASE.items() for c in (chess.WHITE,chess.BLACK))
    return "RICH" if u>=17 else "TRANSITIONAL" if u>=9 else "REDUCED"
def branching(b):
    n=b.legal_moves.count()
    return ("NARROW" if n<=20 else "MEDIUM" if n<=35 else "WIDE"),n
def tactical(b):
    if b.is_check():return "FORCED_CHECK"
    anycap=False;anycheck=False
    for m in b.legal_moves:
        if b.is_capture(m):anycap=True
        if b.gives_check(m):anycheck=True
        if anycap or anycheck:return "TACTICAL_AVAILABLE"
    return "QUIET_SURFACE"
def cell_of(b):
    br,n=branching(b)
    return (phase(b),br,tactical(b)),n
def walk_hashes(x,out):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ("candidate_sha256","sha256") and isinstance(v,str) and len(v)==64:
                # only candidate_sha256 is guaranteed FEN hash; generic sha is ignored below
                if k=="candidate_sha256":out.add(v)
            else:walk_hashes(v,out)
    elif isinstance(x,list):
        for v in x:walk_hashes(v,out)
def exclusions(paths):
    out=set()
    for p in paths:
        pp=Path(p)
        if pp.is_dir():
            files=list(pp.rglob("*.json"))
        else:files=[pp]
        for f in files:
            try:walk_hashes(json.loads(f.read_text()),out)
            except Exception:pass
    return out
def source_candidates(path,source_id,excluded,game_limit,ply_lo,ply_hi):
    pools=defaultdict(list);games=0;visited=0
    with open(path,encoding="utf-8",errors="strict") as f:
        for gi in range(game_limit):
            g=chess.pgn.read_game(f)
            if g is None:break
            games+=1;b=g.board();seen_cells=set();ply=0
            for m in g.mainline_moves():
                b.push(m);ply+=1
                if ply<ply_lo or ply>ply_hi:continue
                if not b.is_valid() or b.chess960 or b.is_game_over(claim_draw=False):continue
                cell,nlegal=cell_of(b)
                if cell in seen_cells:continue
                seen_cells.add(cell)
                fen=canonical_fen(b);h=sha(fen)
                if h in excluded:continue
                traj=sha(f"{source_id}|{gi}|{ply}|{fen}")
                pools[cell].append({
                  "source_id":source_id,"game_index":gi,"ply":ply,"fen":fen,
                  "candidate_sha256":h,"trajectory_hash":traj,
                  "cell":{"phase":cell[0],"branching":cell[1],"tactical_surface":cell[2]},
                  "legal_move_count":nlegal,
                  "side_to_move":"WHITE" if b.turn else "BLACK"
                });visited+=1
    for c in pools:pools[c].sort(key=lambda z:(z["trajectory_hash"],z["candidate_sha256"]))
    return pools,{"games_scanned":games,"candidates_recorded":visited,"cell_support":{"|".join(c):len(v) for c,v in sorted(pools.items())}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",action="append",required=True,help="ID|PGN_PATH|ZIP_SHA")
    ap.add_argument("--exclude",action="append",default=[])
    ap.add_argument("--game-limit",type=int,default=6144)
    ap.add_argument("--ply-lo",type=int,default=12);ap.add_argument("--ply-hi",type=int,default=160)
    ap.add_argument("--max-pool",type=int,default=64)
    ap.add_argument("--min-cell-support",type=int,default=3)
    ap.add_argument("--per-source-cell",type=int,default=2)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    ex=exclusions(a.exclude)
    specs=[]
    for x in a.source:
        z=x.split("|")
        if len(z)!=3:raise SystemExit("P14_SOURCE_SPEC")
        specs.append((z[0],z[1],z[2]))
    if len(specs)!=4:raise SystemExit("P14_SOURCE_COUNT")
    pools={};aud={}
    for sid,path,zsha in specs:
        pools[sid],aud[sid]=source_candidates(path,sid,ex,a.game_limit,a.ply_lo,a.ply_hi)
    # Cross-source duplicate FENs are removed from all source pools.
    fen_sources=defaultdict(set)
    for sid,p in pools.items():
        for rows in p.values():
            for r in rows:fen_sources[r["candidate_sha256"]].add(sid)
    dup={h for h,s in fen_sources.items() if len(s)>1}
    for sid,p in pools.items():
        for cell in list(p):
            p[cell]=[r for r in p[cell] if r["candidate_sha256"] not in dup]
    allcells=[(p,b,t) for p in PHASES for b in BRANCH for t in TACT]
    admissible=[]
    support={}
    for cell in allcells:
        cnt={sid:len(pools[sid].get(cell,[])) for sid,_,_ in specs}
        support["|".join(cell)]=cnt
        if all(n>=a.min_cell_support for n in cnt.values()):admissible.append(cell)
    selected=[];used=set()
    for cell in admissible:
        for sid,_,_ in specs:
            take=[]
            for r in pools[sid][cell]:
                if r["candidate_sha256"] in used:continue
                used.add(r["candidate_sha256"]);take.append(r)
                if len(take)==a.per_source_cell:break
            if len(take)!=a.per_source_cell:raise SystemExit("P14_CELL_DEDUP_SHORT_"+"|".join(cell)+"_"+sid)
            selected.extend(take)
    phases=sorted({c[0] for c in admissible});branches=sorted({c[1] for c in admissible});tacts=sorted({c[2] for c in admissible})
    gate={
      "admissible_cells":len(admissible),"phase_levels":phases,"branching_levels":branches,"tactical_levels":tacts,
      "frozen_positions":len(selected)
    }
    passed=(len(admissible)>=9 and len(phases)>=2 and len(branches)>=3 and len(tacts)>=2 and len(selected)>=72)
    out={
      "schema":"c3x-g10-p14-balanced-corpus-v1","stage":"C3X 0.8.0-G10-P14",
      "verdict":"PASS_BALANCED_CHESS_ECOLOGY_POSITIVITY" if passed else "HOLD_BALANCED_CHESS_ECOLOGY_SUPPORT_INSUFFICIENT",
      "selection":{
        "engine_outcomes_consulted":False,"certificate_outcomes_consulted":False,
        "historical_candidate_hashes_excluded":len(ex),"cross_source_duplicate_fens_excluded":len(dup),
        "game_limit":a.game_limit,"ply_range":[a.ply_lo,a.ply_hi],"min_cell_support_all_sources":a.min_cell_support,
        "positions_per_source_per_admissible_cell":a.per_source_cell,
        "cell_rule":"phase × branching × tactical_surface; cell admitted iff each of 4 sources has >=3 historical-excluded, cross-source-unique candidates",
        "tie_break":"lexicographic trajectory_hash then candidate_sha256"
      },
      "source_audit":aud,"cell_support_after_dedup":support,
      "admissible_cells":[{"phase":c[0],"branching":c[1],"tactical_surface":c[2]} for c in admissible],
      "gate":gate,"positions":sorted(selected,key=lambda r:(r["cell"]["phase"],r["cell"]["branching"],r["cell"]["tactical_surface"],r["source_id"],r["trajectory_hash"]))
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P14_BALANCED",out["verdict"])
    print("EXCLUDED",len(ex),"DUP",len(dup),"CELLS",len(admissible),"POSITIONS",len(selected))
    print("LEVELS",phases,branches,tacts)
    for c in admissible:print("CELL","|".join(c),support["|".join(c)])
if __name__=="__main__":main()
