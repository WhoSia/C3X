#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from collections import Counter,defaultdict
from pathlib import Path
import chess

EDITS=("TARGET","SUBSET","SHAM")
PAIRS=(("berserk","ethereal"),("berserk","stockfish_19"),("ethereal","stockfish_19"))
MAPS={
 ("berserk","ethereal"):{s:s for s in ("00","01","10","11")},
 ("berserk","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
 ("ethereal","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
}
LEVELS={
 "FULL":["material_phase","material_imbalance","legal_branching","in_check","candidate_tactical_mode","polarity_profile","chain_type","engine_pair_preedit_state_pair","family_distance_bucket"],
 "CHESS_SEARCH_CORE":["material_phase","legal_branching","candidate_tactical_mode","polarity_profile","chain_type","engine_pair_preedit_state_pair","family_distance_bucket"],
 "SEARCH_CORE":["polarity_profile","chain_type","engine_pair_preedit_state_pair","family_distance_bucket"]
}

def load(p):return json.loads(Path(p).read_text())

def collect(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1" and x.get("active"):out.append(x)
    return out

def vec(ch,b):
    s=set(ch["board_topology"][b]["available_bounds"])
    return "".join("1" if q in s else "0" for q in ("UPPER","LOWER"))

def material_phase(board):
    pts={chess.KNIGHT:1,chess.BISHOP:1,chess.ROOK:2,chess.QUEEN:4}
    u=sum(len(board.pieces(pt,c))*w for pt,w in pts.items() for c in (chess.WHITE,chess.BLACK))
    return "RICH" if u>=17 else "TRANSITIONAL" if u>=9 else "REDUCED"

def material_imbalance(board):
    val={chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9}
    w=sum(len(board.pieces(pt,chess.WHITE))*v for pt,v in val.items())
    b=sum(len(board.pieces(pt,chess.BLACK))*v for pt,v in val.items())
    d=abs(w-b)
    return "BALANCED" if d==0 else "SMALL" if d<=2 else "LARGE"

def branching(board):
    n=board.legal_moves.count()
    return ("NARROW" if n<=20 else "MEDIUM" if n<=35 else "WIDE"),n

def cand_mode(board,A,B):
    caps=[];checks=[]
    for u in (A,B):
        try:m=chess.Move.from_uci(u)
        except:continue
        if m not in board.legal_moves:continue
        caps.append(board.is_capture(m));checks.append(board.gives_check(m))
    if any(c and h for c,h in zip(caps,checks)):return "CAPTURE_AND_CHECK"
    if any(checks):return "ANY_CHECK"
    if any(caps):return "ANY_CAPTURE"
    return "QUIET_QUIET"

def fd_bucket(x):
    x=int(x)
    return "NEAR" if x<=1 else "MID" if x==2 else "FAR"

def sig(row,level):
    return tuple(str(row[f]) for f in LEVELS[level])

def summarize_source(rows,src):
    r=[x for x in rows if x["source_id"]==src]
    return {"n":len(r),"defect":sum(x["defect"] for x in r),"rate":sum(x["defect"] for x in r)/len(r) if r else None}

def overlap_stats(rows,e1,e2,edit,level,sources):
    sub=[r for r in rows if r["engine_pair"]==f"{e1}|{e2}" and r["edit"]==edit]
    by={s:defaultdict(list) for s in sources}
    for r in sub:by[r["source_id"]][sig(r,level)].append(r)
    cells=sorted(set(by[sources[0]])&set(by[sources[1]]))
    detail=[];num=den=0;matched0=matched1=0
    recurrent_defect_cells=0
    for c in cells:
        a=by[sources[0]][c];b=by[sources[1]][c]
        m=min(len(a),len(b))
        r0=sum(x["defect"] for x in a)/len(a)
        r1=sum(x["defect"] for x in b)/len(b)
        num += m*(r1-r0);den += m
        matched0+=m;matched1+=m
        if r0>0 and r1>0:recurrent_defect_cells+=1
        detail.append({"signature":list(c),"n0":len(a),"n1":len(b),"m":m,"rate0":r0,"rate1":r1,"gap":r1-r0})
    n0=sum(len(v) for v in by[sources[0]].values());n1=sum(len(v) for v in by[sources[1]].values())
    raw0=sum(r["defect"] for r in sub if r["source_id"]==sources[0])/n0 if n0 else None
    raw1=sum(r["defect"] for r in sub if r["source_id"]==sources[1])/n1 if n1 else None
    overlap_mass=(2*den/(n0+n1)) if (n0+n1) else 0
    return {
      "level":level,"matched_cell_count":len(cells),"matched_weight":den,
      "overlap_mass":overlap_mass,
      "raw_rate_1657":raw0,"raw_rate_1658":raw1,
      "raw_gap":(raw1-raw0) if raw0 is not None and raw1 is not None else None,
      "overlap_standardized_gap":num/den if den else None,
      "recurrent_defect_cells":recurrent_defect_cells,
      "cells":detail
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--chain-freeze",required=True)
    ap.add_argument("--p9-census",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    worlds=collect(a.worlds);freeze=load(a.chain_freeze);census=load(a.p9_census)
    cases={x["case_id"]:x for x in freeze["cases"]}
    # rows keyed by source-position-chain with available engine worlds
    grouped=defaultdict(dict)
    chainmeta={}
    for w in worlds:
        case=cases[w["case_id"]]
        for ch in w.get("chains",[]):
            k=(w["source_id"],w["position_id"],ch["chain_id"])
            grouped[k][w["engine"]]=ch
            chainmeta[k]=(case,ch)
    rows=[]
    for k,eng in grouped.items():
        src,pid,cid=k;case,ch0=chainmeta[k]
        board=chess.Board(case["cell"]["fen"])
        A=case["position_pair"]["pair"]["A"]["uci"];B=case["position_pair"]["pair"]["B"]["uci"]
        ph=material_phase(board);imb=material_imbalance(board);br,nlegal=branching(board)
        cm=cand_mode(board,A,B);ic=board.is_check()
        ps=census["position_scores"].get(pid,{})
        pol="|".join(ps.get("polarity_profile",[]))
        fdb=fd_bucket(ps.get("family_distance",99))
        for e1,e2 in PAIRS:
            if e1 not in eng or e2 not in eng:continue
            c1,c2=eng[e1],eng[e2];mp=MAPS[(e1,e2)]
            b01=mp[vec(c1,"B0")];b02=vec(c2,"B0")
            pre=f"{b01}|{b02}"
            # chain type should be identical; retain directional left if not
            ctype=c1.get("chain_type")
            for d in EDITS:
                edge1=(mp[vec(c1,"B0")],mp[vec(c1,d)])
                edge2=(vec(c2,"B0"),vec(c2,d))
                rows.append({
                  "source_id":src,"position_id":pid,"chain_id":cid,"engine_pair":f"{e1}|{e2}","edit":d,
                  "defect":int(edge1!=edge2),
                  "aligned_left_edge":">".join(edge1),"right_edge":">".join(edge2),
                  "material_phase":ph,"material_imbalance":imb,"legal_branching":br,"legal_move_count":nlegal,
                  "in_check":str(bool(ic)),"candidate_tactical_mode":cm,"polarity_profile":pol,
                  "chain_type":ctype,"engine_pair_preedit_state_pair":pre,"family_distance_bucket":fdb,
                  "family_distance":ps.get("family_distance"),"family_margin":ps.get("family_margin")
                })
    sources=sorted({r["source_id"] for r in rows})
    results={}
    supported=[]
    for e1,e2 in PAIRS:
      pk=f"{e1}|{e2}";results[pk]={}
      for d in EDITS:
        results[pk][d]={}
        for level in LEVELS:
          z=overlap_stats(rows,e1,e2,d,level,sources)
          results[pk][d][level]=z
          if level=="FULL" and z["matched_cell_count"]>=3 and z["matched_weight"]>=6:
            supported.append((pk,d,z))
    # chess regime enrichment descriptively
    regime={}
    for field in ("material_phase","material_imbalance","legal_branching","in_check","candidate_tactical_mode","family_distance_bucket"):
      g=defaultdict(list)
      for r in rows:g[r[field]].append(r["defect"])
      regime[field]={k:{"n":len(v),"defect_rate":sum(v)/len(v)} for k,v in sorted(g.items())}
    if not supported:
      verdict="HOLD_CONTEXT_OVERLAP_INSUFFICIENT"
    else:
      # classify only from supported FULL cells, descriptive no arbitrary zero threshold:
      raw=[abs(z["raw_gap"]) for _,_,z in supported if z["raw_gap"] is not None]
      std=[abs(z["overlap_standardized_gap"]) for _,_,z in supported if z["overlap_standardized_gap"] is not None]
      # exact comparison: median standardized magnitude vs raw magnitude
      mr=sorted(raw)[len(raw)//2] if raw else 0
      ms=sorted(std)[len(std)//2] if std else 0
      recurrent=sum(z["recurrent_defect_cells"] for _,_,z in supported)
      if recurrent>0 and ms<=mr*0.5:
        verdict="DEVELOPMENT_CONTEXT_STABLE_OBSTRUCTION_REGIMES_IDENTIFIED"
      elif ms<=mr*0.5:
        verdict="DEVELOPMENT_CONTEXT_COMPOSITION_EXPLAINS_SOURCE_FRAGILITY"
      elif ms>=mr*0.8:
        verdict="DEVELOPMENT_CONDITIONAL_DEFECT_DRIFT_PERSISTS_AFTER_MATCHING"
      else:
        verdict="DEVELOPMENT_MIXED_COMPOSITION_AND_CONDITIONAL_DRIFT"
    out={
      "schema":"c3x-g10-p13-context-factorization-v1","status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "verdict":verdict,"row_count":len(rows),"sources":sources,
      "context_levels":LEVELS,"pair_edit_results":results,"chess_regime_defect_rates":regime,
      "supported_full_pair_edits":[{"engine_pair":p,"edit":d,"matched_cells":z["matched_cell_count"],"matched_weight":z["matched_weight"],"overlap_mass":z["overlap_mass"],"raw_gap":z["raw_gap"],"standardized_gap":z["overlap_standardized_gap"],"recurrent_cells":z["recurrent_defect_cells"]} for p,d,z in supported],
      "authority":{"context_matching_observational":True,"engine_internal_mechanism":False,"fresh_replication":False},
      "claim_ceiling":"DEVELOPMENT_CHESS_CONTEXT_CONDITIONALITY_ONLY"
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P13_CONTEXT_PASS",verdict)
    print("ROWS",len(rows))
    print("SUPPORTED",json.dumps(out["supported_full_pair_edits"],sort_keys=True))
    print("REGIME",json.dumps(regime,sort_keys=True))
if __name__=="__main__":main()
