#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from collections import defaultdict
from pathlib import Path
import chess, chess.pgn

PHASES=("RICH","TRANSITIONAL","REDUCED")
BRANCHES=("NARROW","MEDIUM","WIDE")
TACTICS=("FORCED_CHECK","TACTICAL_AVAILABLE","QUIET_SURFACE")
PIECE_PHASE={chess.KNIGHT:1,chess.BISHOP:1,chess.ROOK:2,chess.QUEEN:4}

def sha(s:str)->str:
    return hashlib.sha256(s.encode()).hexdigest()

def canonical_fen(board:chess.Board)->str:
    f=board.fen(en_passant="fen").split()
    return " ".join(f[:4])+" 0 1"

def canonicalize_fen_text(s:str):
    try:
        b=chess.Board(s)
        if not b.is_valid(): return None
        return canonical_fen(b)
    except Exception:
        return None

def phase(b):
    u=sum(len(b.pieces(pt,c))*w for pt,w in PIECE_PHASE.items() for c in (chess.WHITE,chess.BLACK))
    return "RICH" if u>=17 else "TRANSITIONAL" if u>=9 else "REDUCED"

def branching(b):
    n=b.legal_moves.count()
    return ("NARROW" if n<=20 else "MEDIUM" if n<=35 else "WIDE"),n

def tactical(b):
    if b.is_check(): return "FORCED_CHECK"
    for m in b.legal_moves:
        if b.is_capture(m) or b.gives_check(m): return "TACTICAL_AVAILABLE"
    return "QUIET_SURFACE"

def cell_of(b):
    br,n=branching(b)
    return (phase(b),br,tactical(b)),n

def walk_history(x, hashes):
    if isinstance(x,dict):
        for k,v in x.items():
            kl=str(k).lower()
            if isinstance(v,str):
                if kl=="candidate_sha256" and re.fullmatch(r"[0-9a-fA-F]{64}",v):
                    hashes.add(v.lower())
                if "fen" in kl:
                    cf=canonicalize_fen_text(v)
                    if cf: hashes.add(sha(cf))
            walk_history(v,hashes)
    elif isinstance(x,list):
        for v in x: walk_history(v,hashes)

def historical_hashes(root):
    out=set(); files=0
    for f in Path(root).rglob("*.json"):
        try:
            obj=json.loads(f.read_text())
        except Exception:
            continue
        files+=1; walk_history(obj,out)
    return out,files

def source_candidates(path,sid,excluded,ply_lo,ply_hi,game_limit):
    pools=defaultdict(list); games=0; positions=0
    with open(path,encoding="utf-8",errors="replace") as fh:
        for gi in range(game_limit):
            g=chess.pgn.read_game(fh)
            if g is None: break
            games+=1; b=g.board(); seen=set(); ply=0
            for mv in g.mainline_moves():
                b.push(mv); ply+=1
                if not (ply_lo<=ply<=ply_hi): continue
                if not b.is_valid() or b.chess960 or b.is_game_over(claim_draw=False): continue
                cell,nlegal=cell_of(b)
                if cell in seen: continue
                seen.add(cell)
                fen=canonical_fen(b); h=sha(fen)
                if h in excluded: continue
                traj=sha(f"{sid}|{gi}|{ply}|{fen}")
                pools[cell].append({
                    "source_id":sid,"game_index":gi,"ply":ply,"fen":fen,
                    "candidate_sha256":h,"trajectory_hash":traj,
                    "cell":{"phase":cell[0],"branching":cell[1],"tactical_surface":cell[2]},
                    "legal_move_count":nlegal,
                    "side_to_move":"WHITE" if b.turn else "BLACK"
                }); positions+=1
    for cell in pools:
        pools[cell].sort(key=lambda r:(r["trajectory_hash"],r["candidate_sha256"]))
    return pools,{"games_scanned":games,"eligible_pre_dedup":positions,
                  "cell_support":{"|".join(c):len(v) for c,v in sorted(pools.items())}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",action="append",required=True,help="ID|PGN|URL|SHA256")
    ap.add_argument("--history-root",default=".")
    ap.add_argument("--ply-lo",type=int,default=12); ap.add_argument("--ply-hi",type=int,default=160)
    ap.add_argument("--game-limit",type=int,default=20000)
    ap.add_argument("--min-cell-support",type=int,default=4)
    ap.add_argument("--per-source-cell",type=int,default=2)
    ap.add_argument("--max-common-cells",type=int,default=12)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    specs=[]
    for raw in a.source:
        z=raw.split("|")
        if len(z)!=4: raise SystemExit("P19_SOURCE_SPEC")
        specs.append(tuple(z))
    if len(specs)<2: raise SystemExit("P19_NEED_TWO_SOURCES")

    excluded,history_files=historical_hashes(a.history_root)
    pools={}; audit={}
    for sid,path,url,digest in specs:
        pools[sid],audit[sid]=source_candidates(path,sid,excluded,a.ply_lo,a.ply_hi,a.game_limit)
        audit[sid].update({"url":url,"source_sha256":digest})

    fen_sources=defaultdict(set)
    for sid,p in pools.items():
        for rows in p.values():
            for r in rows: fen_sources[r["candidate_sha256"]].add(sid)
    crossdup={h for h,ss in fen_sources.items() if len(ss)>1}
    for sid,p in pools.items():
        for cell in list(p):
            p[cell]=[r for r in p[cell] if r["candidate_sha256"] not in crossdup]

    allcells=[(p,b,t) for p in PHASES for b in BRANCHES for t in TACTICS]
    common=[]
    support={}
    for cell in allcells:
        counts={sid:len(pools[sid].get(cell,[])) for sid,_,_,_ in specs}
        support["|".join(cell)]=counts
        if all(n>=a.min_cell_support for n in counts.values()): common.append(cell)

    # Deterministic geometry-only cap. No engine/counterfactual outcomes enter ordering.
    common=sorted(common,key=lambda c:("RICH","TRANSITIONAL","REDUCED").index(c[0])*9+
                                      ("NARROW","MEDIUM","WIDE").index(c[1])*3+
                                      ("FORCED_CHECK","TACTICAL_AVAILABLE","QUIET_SURFACE").index(c[2]))
    selected_cells=common[:a.max_common_cells]
    selected=[]; used=set()
    for cell in selected_cells:
        for sid,_,_,_ in specs:
            take=[]
            for r in pools[sid][cell]:
                if r["candidate_sha256"] in used: continue
                used.add(r["candidate_sha256"]); take.append(r)
                if len(take)==a.per_source_cell: break
            if len(take)!=a.per_source_cell:
                raise SystemExit("P19_DEDUP_SHORT_"+"|".join(cell)+"_"+sid)
            selected.extend(take)

    phases=sorted({c[0] for c in selected_cells})
    branches=sorted({c[1] for c in selected_cells})
    tactics=sorted({c[2] for c in selected_cells})
    gate={
        "common_cells":len(selected_cells),"positions":len(selected),
        "phase_levels":phases,"branching_levels":branches,"tactical_levels":tactics,
        "history_hashes_excluded":len(excluded),"history_json_files_scanned":history_files,
        "cross_source_duplicate_fens_excluded":len(crossdup)
    }
    passed=(len(selected_cells)>=6 and len(selected)>=24 and len(phases)>=2 and len(branches)>=2 and len(tactics)>=2)
    out={
        "schema":"c3x-g10-p19-fresh-event-census-v1",
        "stage":"C3X 0.9.0-G10-P19",
        "verdict":"PASS_FRESH_EVENT_WORLD_ECOLOGY_READY" if passed else "HOLD_FRESH_EVENT_WORLD_ECOLOGY_SUPPORT_INSUFFICIENT",
        "authority":"PRE_ENGINE_OUTCOME_SELECTION_ONLY",
        "selection":{
            "engine_outcomes_consulted":False,"counterfactual_outcomes_consulted":False,
            "historical_fen_and_candidate_hashes_excluded":True,
            "cross_source_duplicate_fens_excluded":True,
            "provider_independence_claimed":False,
            "freshness_claim":"EVENT_NEW_WORLD_DISJOINT_PROSPECTIVE_ENGINE_OUTCOME",
            "cell":"phase × branching × tactical_surface",
            "min_cell_support_per_source":a.min_cell_support,
            "positions_per_source_per_cell":a.per_source_cell,
            "max_common_cells":a.max_common_cells,
            "ply_range":[a.ply_lo,a.ply_hi]
        },
        "source_audit":audit,"cell_support_after_history_exclusion":support,
        "selected_cells":[{"phase":c[0],"branching":c[1],"tactical_surface":c[2]} for c in selected_cells],
        "gate":gate,
        "positions":sorted(selected,key=lambda r:(r["source_id"],r["cell"]["phase"],r["cell"]["branching"],r["cell"]["tactical_surface"],r["trajectory_hash"]))
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P19_SOURCE_CENSUS",out["verdict"])
    print("GATE",json.dumps(gate,sort_keys=True))
    for sid in sorted(audit): print("SOURCE",sid,json.dumps(audit[sid],sort_keys=True))

if __name__=="__main__":
    main()
