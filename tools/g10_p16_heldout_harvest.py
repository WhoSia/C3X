#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import chess,chess.pgn

PHASE_W={chess.KNIGHT:1,chess.BISHOP:1,chess.ROOK:2,chess.QUEEN:4}

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()
def load(p): return json.loads(Path(p).read_text())
def canonical_fen(b):
    f=b.fen(en_passant="fen").split()
    return " ".join(f[:4])+" 0 1"
def phase(b):
    u=sum(len(b.pieces(pt,c))*w for pt,w in PHASE_W.items() for c in (chess.WHITE,chess.BLACK))
    return "RICH" if u>=17 else "TRANSITIONAL" if u>=9 else "REDUCED"
def branching(b):
    n=b.legal_moves.count()
    return ("NARROW" if n<=20 else "MEDIUM" if n<=35 else "WIDE"),n
def tactical(b):
    if b.is_check(): return "FORCED_CHECK"
    for m in b.legal_moves:
        if b.is_capture(m) or b.gives_check(m): return "TACTICAL_AVAILABLE"
    return "QUIET_SURFACE"
def cell(b):
    br,n=branching(b)
    return (phase(b),br,tactical(b)),n
def walk_hashes(x,out):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=="candidate_sha256" and isinstance(v,str) and len(v)==64: out.add(v)
            else: walk_hashes(v,out)
    elif isinstance(x,list):
        for v in x: walk_hashes(v,out)
def exclusions(root):
    out=set()
    for p in Path(root).rglob("*.json"):
        try: walk_hashes(json.loads(p.read_text()),out)
        except Exception: pass
    return out
def scan_pgn(path,sid,routed,excluded,limit,ply_lo,ply_hi):
    pools=defaultdict(list);games=0
    with open(path,encoding="utf-8",errors="replace") as f:
        for gi in range(limit):
            g=chess.pgn.read_game(f)
            if g is None: break
            games+=1;b=g.board();seen=set();ply=0
            for m in g.mainline_moves():
                b.push(m);ply+=1
                if ply<ply_lo or ply>ply_hi: continue
                if not b.is_valid() or b.chess960 or b.is_game_over(claim_draw=False): continue
                c,n=cell(b);k="|".join(c)
                if k not in routed or k in seen: continue
                seen.add(k)
                fen=canonical_fen(b);h=sha(fen)
                if h in excluded: continue
                tr=sha(f"{sid}|{gi}|{ply}|{fen}")
                pools[k].append({
                  "source_id":sid,"game_index":gi,"ply":ply,"fen":fen,
                  "candidate_sha256":h,"trajectory_hash":tr,
                  "context":{"phase":c[0],"branching":c[1],"tactical_surface":c[2]},
                  "legal_move_count":n,"router_grammar":routed[k]
                })
    for k in pools:pools[k].sort(key=lambda z:(z["trajectory_hash"],z["candidate_sha256"]))
    return pools,{"games_scanned":games,"cell_counts":{k:len(v) for k,v in sorted(pools.items())}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--router",required=True)
    ap.add_argument("--source",action="append",required=True,help="ID|PGN|ZIP|URL")
    ap.add_argument("--exclude-root",required=True)
    ap.add_argument("--game-limit",type=int,default=6144)
    ap.add_argument("--ply-lo",type=int,default=12);ap.add_argument("--ply-hi",type=int,default=160)
    ap.add_argument("--min-per-source-cell",type=int,default=3)
    ap.add_argument("--take-per-source-cell",type=int,default=2)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    router=load(a.router)
    if router.get("status")!="ROUTER_FROZEN_PRE_HELDOUT_SOURCE": raise SystemExit("P16_ROUTER_STATE")
    routed={k:v for k,v in router["policy"].items() if v!="ABSTAIN"}
    specs=[]
    for s in a.source:
        z=s.split("|",3)
        if len(z)!=4: raise SystemExit("P16_SOURCE_SPEC")
        specs.append(z)
    if len(specs)!=2: raise SystemExit("P16_SOURCE_COUNT")
    ex=exclusions(a.exclude_root)
    pools={};aud={}
    for sid,pgn,zp,url in specs:
        pools[sid],aud[sid]=scan_pgn(pgn,sid,routed,ex,a.game_limit,a.ply_lo,a.ply_hi)
        aud[sid]["zip_sha256"]=file_sha(zp);aud[sid]["url"]=url
    # remove cross-source duplicate FENs from both arms
    fs=defaultdict(set)
    for sid in pools:
        for rows in pools[sid].values():
            for r in rows:fs[r["candidate_sha256"]].add(sid)
    dup={h for h,s in fs.items() if len(s)>1}
    for sid in pools:
        for k in list(pools[sid]):pools[sid][k]=[r for r in pools[sid][k] if r["candidate_sha256"] not in dup]
    admiss=[]
    support={}
    for k in sorted(routed):
        cnt={sid:len(pools[sid].get(k,[])) for sid,_,_,_ in specs}
        support[k]=cnt
        if all(v>=a.min_per_source_cell for v in cnt.values()):admiss.append(k)
    selected=[];used=set()
    for k in admiss:
        for sid,_,_,_ in specs:
            take=[]
            for r in pools[sid][k]:
                if r["candidate_sha256"] in used:continue
                used.add(r["candidate_sha256"]);take.append(r)
                if len(take)==a.take_per_source_cell:break
            if len(take)!=a.take_per_source_cell:raise SystemExit("P16_CELL_SHORT "+k+" "+sid)
            selected.extend(take)
    phases=sorted({x["context"]["phase"] for x in selected})
    branches=sorted({x["context"]["branching"] for x in selected})
    tacts=sorted({x["context"]["tactical_surface"] for x in selected})
    passed=len(admiss)>=8 and len(phases)>=2 and len(branches)>=3 and len(tacts)>=2 and len(selected)>=32
    out={
      "schema":"c3x-g10-p16-heldout-corpus-v1","stage":"C3X 0.9.0-G10-P16",
      "verdict":"PASS_HELDOUT_ROUTED_ECOLOGY_POSITIVITY" if passed else "HOLD_HELDOUT_ROUTED_ECOLOGY_SUPPORT_INSUFFICIENT",
      "selection":{
        "engine_outcomes_consulted":False,"preference_outcomes_consulted":False,"defect_outcomes_consulted":False,
        "router_frozen_before_source_bytes":True,"historical_candidate_hashes_excluded":len(ex),
        "cross_source_duplicate_fens_excluded":len(dup),"game_limit":a.game_limit,
        "positions_per_source_per_cell":a.take_per_source_cell
      },
      "source_audit":aud,"router_policy":routed,"cell_support_after_dedup":support,
      "admissible_cells":admiss,
      "gate":{"admissible_cells":len(admiss),"phase_levels":phases,"branching_levels":branches,"tactical_levels":tacts,"frozen_positions":len(selected)},
      "positions":sorted(selected,key=lambda r:(r["context"]["phase"],r["context"]["branching"],r["context"]["tactical_surface"],r["source_id"],r["trajectory_hash"]))
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P16_HELDOUT",out["verdict"])
    print("HASHES",json.dumps({s:aud[s]["zip_sha256"] for s in aud},sort_keys=True))
    print("CELLS",len(admiss),admiss)
    print("LEVELS",phases,branches,tacts,"POSITIONS",len(selected),"EXCLUDED",len(ex),"DUP",len(dup))
if __name__=="__main__":main()
