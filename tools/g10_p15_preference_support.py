#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,hashlib
from pathlib import Path
from collections import defaultdict
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import p32_event_court as p32

ENGINES=("stockfish_19","berserk","ethereal")

def load(p): return json.loads(Path(p).read_text())
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def find_binary(root,e):
    xs=list(Path(root).rglob(f"c3x-p16-{e}"))
    if len(xs)!=1: raise SystemExit(f"P15_BINARY {e} {len(xs)}")
    xs[0].chmod(0o755); return xs[0]

def worlds(stage_a,pair):
    alloc={x["position_id"]:x for x in stage_a["stage_b_allocation"]}
    out=[]
    for pid,a in sorted(alloc.items()):
        z=pair["positions"][pid]
        for e in ENGINES:
            v=z["engine_views"].get(e,{})
            if v.get("active"):
                out.append({"position_id":pid,"source_id":z["source_id"],"engine":e,"allocation":a,"view":v})
    return out

def measure(binary,protocol,fen,A,B,nodes,repeats,root,tag):
    board=chess.Board(fen); legal={m.uci() for m in board.legal_moves}
    vals={}
    for mi,m in enumerate((A,B)):
        scores=[]
        for rep in range(repeats):
            r=p13.run_forced(binary,protocol,fen,m,nodes,root/tag,f"{mi}-{rep}")
            scores.append(r["semantic"].get("score"))
        cps=[p13.score_cp(s) for s in scores]
        stable=len(cps)==repeats and repeats>=2 and None not in cps and len(set(cps))==1
        vals[m]={"stable":stable,"cp":cps[0] if stable else None}
    gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
    ok=bool(A in legal and B in legal and gap is not None and gap<=50)
    return {"pair":vals,"gap_cp_abs":gap,"supported":ok,"legal_pair":A in legal and B in legal}

def run_shard(a):
    sa=load(a.stage_a);pf=load(a.pair_freeze)
    if sa.get("selected_grammar")!="G2_SAME_TYPE_SIDE_COLLATERAL": raise SystemExit("P15_STAGE_A_GRAMMAR")
    ws=worlds(sa,pf)
    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    n=0
    for i,w in enumerate(ws):
        if i%a.shards!=a.shard: continue
        e=w["engine"]; binary=find_binary(a.build_dir,e)
        expected=pf["variants"][e]["sha256"]
        if sha_file(binary)!=expected: raise SystemExit(f"P15_BINARY_SHA {e}")
        protocol=pf["variants"][e].get("protocol") or p32.protocol_for(e)
        ch=w["allocation"]["chain"]; pair=w["allocation"]["pair"];A=pair["A"]["uci"];B=pair["B"]["uci"]
        root=outdir/f".private-{i:03d}-{e}";root.mkdir(parents=True,exist_ok=True)
        boards={
          "TARGET":measure(binary,protocol,ch["target_fen"],A,B,20000,2,root,"target"),
          "SUBSET":measure(binary,protocol,ch["subset_fen"],A,B,20000,2,root,"subset"),
          "SHAM":measure(binary,protocol,ch["sham_fen"],A,B,20000,2,root,"sham")
        }
        supported=all(x["supported"] for x in boards.values())
        row={
          "schema":"c3x-g10-p15-stage-b-world-v1","stage":"C3X 0.9.0-G10-P15",
          "position_id":w["position_id"],"source_id":w["source_id"],"engine":e,
          "selected_grammar":"G2_SAME_TYPE_SIDE_COLLATERAL",
          "context":w["allocation"]["context"],"chain":ch,
          "original_pair_active":True,"preference_supported_chain":supported,
          "boards":boards,
          "edited_native_choice_consulted":False,"search_event_outcomes_consulted":False,"defect_outcomes_consulted":False
        }
        (outdir/f"{i:03d}-{e}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n")
        n+=1
    print("G10_P15_STAGE_B_SHARD",a.shard,n)

def aggregate(a):
    sa=load(a.stage_a);pf=load(a.pair_freeze)
    rows=[]
    for p in Path(a.worlds).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p15-stage-b-world-v1":rows.append(x)
    expected=worlds(sa,pf)
    exp={(x["position_id"],x["engine"]) for x in expected}
    got={(x["position_id"],x["engine"]) for x in rows}
    if got!=exp: raise SystemExit(f"P15_WORLD_SET got={len(got)} expected={len(exp)}")
    bypos=defaultdict(list)
    for r in rows:bypos[r["position_id"]].append(r)
    admitted=[]
    for pid,a0 in {x["position_id"]:x for x in sa["stage_b_allocation"]}.items():
        rr=bypos.get(pid,[])
        supp=sorted(r["engine"] for r in rr if r["preference_supported_chain"])
        if len(supp)>=2:
            admitted.append({
              "position_id":pid,"source_id":a0["source_id"],"context":a0["context"],
              "supporting_engines":supp,"support_count":len(supp),
              "pair":a0["pair"],"chain":a0["chain"]
            })
    total_pairs=int(sa["admitted_pair_positions"])
    frac=len(admitted)/total_pairs if total_pairs else 0
    cells=sorted({"|".join((x["context"]["phase"],x["context"]["branching"],x["context"]["tactical_surface"])) for x in admitted})
    srceng=defaultdict(set)
    for x in admitted:
        for e in x["supporting_engines"]:srceng[x["source_id"]].add(e)
    source_ok=all(len(srceng[s])>=2 for s in sorted({x["source_id"] for x in sa["stage_b_allocation"]}))
    passed=frac>=0.35 and len(cells)>=6 and source_ok
    allocation=[]
    if passed:
        buckets=defaultdict(list)
        for x in admitted:
            key=(x["source_id"],x["context"]["phase"],x["context"]["branching"],x["context"]["tactical_surface"])
            buckets[key].append(x)
        for key,v in sorted(buckets.items()):
            v.sort(key=lambda x:(-x["support_count"],x["chain"]["total_collateral"],x["position_id"]))
            allocation.append(v[0])
    out={
      "schema":"c3x-g10-p15-stage-b-v1","stage":"C3X 0.9.0-G10-P15",
      "status":"PREFERENCE_SUPPORT_ONLY","selected_grammar":"G2_SAME_TYPE_SIDE_COLLATERAL",
      "world_count":len(rows),"structural_positions":len(sa["stage_b_allocation"]),
      "admitted_pair_positions":total_pairs,"preference_supported_chain_positions":len(admitted),
      "chain_fraction_of_pairs":frac,"context_cells_with_chain_support":len(cells),"supported_cells":cells,
      "supporting_engines_by_source":{k:sorted(v) for k,v in sorted(srceng.items())},
      "stage_c_allocation":allocation,
      "verdict":"PASS_CONTEXT_ADAPTIVE_PREFERENCE_SUPPORTED_CHAIN_RECOVERY" if passed else "HOLD_PREFERENCE_SUPPORT_COLLAPSES_AFTER_STRUCTURAL_RECOVERY",
      "edited_native_choice_consulted":False,"search_event_outcomes_consulted":False,"defect_outcomes_consulted":False,
      "position_admissions":admitted
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P15_STAGE_B",out["verdict"])
    print("WORLD",len(rows),"STRUCT",len(sa["stage_b_allocation"]),"ADMITTED",len(admitted),"/",total_pairs,frac)
    print("CELLS",len(cells),cells)
    print("ENGINES",out["supporting_engines_by_source"])
    print("STAGE_C_ALLOC",len(allocation))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
    r=sub.add_parser("run");r.add_argument("--stage-a",required=True);r.add_argument("--pair-freeze",required=True);r.add_argument("--build-dir",required=True);r.add_argument("--shard",type=int,required=True);r.add_argument("--shards",type=int,required=True);r.add_argument("--out-dir",required=True)
    g=sub.add_parser("aggregate");g.add_argument("--stage-a",required=True);g.add_argument("--pair-freeze",required=True);g.add_argument("--worlds",required=True);g.add_argument("--out",required=True)
    a=ap.parse_args()
    run_shard(a) if a.cmd=="run" else aggregate(a)
if __name__=="__main__":main()
