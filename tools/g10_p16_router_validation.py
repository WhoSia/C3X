#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,hashlib
from collections import defaultdict
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"harness"))
import g10_p15_grammar_census as gc
import g10_p15_preference_support as ps

def load(p): return json.loads(Path(p).read_text())
def ckey(c): return "|".join((c["phase"],c["branching"],c["tactical_surface"]))
def find_binary(root,e):
    xs=list(Path(root).rglob(f"c3x-p16-{e}"))
    if len(xs)!=1: raise SystemExit(f"P16_BINARY {e} {len(xs)}")
    xs[0].chmod(0o755); return xs[0]
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def choose_chain(fen,pair,grammar):
    edits=gc.enumerate_edits(fen,pair["A"]["uci"],pair["B"]["uci"])
    chains=gc.chains_for(edits,grammar)
    if not chains:return None
    c=chains[0]
    return {
      "type":c["type"],"target_edit":c["target"]["edit_id"],"subset_edit":c["subset"]["edit_id"],"sham_edit":c["sham"]["edit_id"],
      "target_atoms":list(c["target"]["atoms"]),"subset_atoms":list(c["subset"]["atoms"]),
      "piece_type":c["target"]["piece_type"],"side_role":c["target"]["side_role"],"profile":c["target"]["profile"],
      "total_collateral":c["total_collateral"],
      "target_fen":c["target"]["fen"],"subset_fen":c["subset"]["fen"],"sham_fen":c["sham"]["fen"]
    }

def run(a):
    corpus=load(a.corpus);pf=load(a.pair_freeze);router=load(a.router)
    bypid={f"p16:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corpus["positions"]}
    admitted=[(pid,z) for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    n=0
    for idx,(pid,z) in enumerate(admitted):
        if idx%a.shards!=a.shard:continue
        meta=bypid.get(pid)
        if meta is None:raise SystemExit(f"P16_META {pid}")
        route=router["policy"].get(ckey(meta["context"]),"ABSTAIN")
        if route=="ABSTAIN":raise SystemExit(f"P16_ADMITTED_OUTSIDE_ROUTE {pid}")
        pair=z["pair"];fen=meta["fen"]
        policy_chain={
          "ROUTED":choose_chain(fen,pair,route),
          "GLOBAL_G2":choose_chain(fen,pair,"G2_SAME_TYPE_SIDE_COLLATERAL")
        }
        active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"))
        engines={}
        for e in active:
            binary=find_binary(a.build_dir,e)
            expected=pf["variants"][e]["sha256"]
            if sha_file(binary)!=expected:raise SystemExit(f"P16_BIN_SHA {e}")
            protocol=pf["variants"][e].get("protocol")
            engines[e]={}
            for pol,ch in policy_chain.items():
                if ch is None:
                    engines[e][pol]={"structural":False,"supported":False,"boards":None}
                    continue
                A=pair["A"]["uci"];B=pair["B"]["uci"]
                root=outdir/f".private-{idx}-{e}-{pol}"
                boards={
                  "TARGET":ps.measure(binary,protocol,ch["target_fen"],A,B,20000,2,root,"target"),
                  "SUBSET":ps.measure(binary,protocol,ch["subset_fen"],A,B,20000,2,root,"subset"),
                  "SHAM":ps.measure(binary,protocol,ch["sham_fen"],A,B,20000,2,root,"sham")
                }
                engines[e][pol]={"structural":True,"supported":all(v["supported"] for v in boards.values()),"boards":boards}
        row={
          "schema":"c3x-g10-p16-router-validation-world-v1","position_id":pid,"source_id":z["source_id"],
          "context":meta["context"],"router_grammar":route,"pair":pair,"active_engines":active,
          "chains":policy_chain,"engines":engines,
          "edited_native_choice_consulted":False,"search_event_outcomes_consulted":False,"defect_outcomes_consulted":False
        }
        (outdir/f"{idx:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
    print("G10_P16_VALIDATE_SHARD",a.shard,n)

def aggregate(a):
    corpus=load(a.corpus);pf=load(a.pair_freeze)
    admitted=[pid for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
    rows=[]
    for p in Path(a.worlds).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p16-router-validation-world-v1":rows.append(x)
    if {r["position_id"] for r in rows}!=set(admitted):raise SystemExit(f"P16_WORLD_SET {len(rows)} {len(admitted)}")
    cats=defaultdict(int);positive={"ROUTED":[],"GLOBAL_G2":[]};struct={"ROUTED":0,"GLOBAL_G2":0}
    source=defaultdict(lambda:defaultdict(lambda:{"n":0,"positive":0}))
    cell=defaultdict(lambda:defaultdict(lambda:{"n":0,"positive":0}))
    detail=[]
    for r in rows:
        vals={}
        for pol in ("ROUTED","GLOBAL_G2"):
            ch=r["chains"][pol]
            if ch is not None:struct[pol]+=1
            supp=[e for e,z in r["engines"].items() if z[pol]["supported"]]
            ok=len(supp)>=2
            vals[pol]=ok
            if ok:positive[pol].append(r["position_id"])
            source[r["source_id"]][pol]["n"]+=1;source[r["source_id"]][pol]["positive"]+=int(ok)
            k=ckey(r["context"]);cell[k][pol]["n"]+=1;cell[k][pol]["positive"]+=int(ok)
        cat=("BOTH" if vals["ROUTED"] and vals["GLOBAL_G2"] else
             "ROUTED_ONLY" if vals["ROUTED"] else "G2_ONLY" if vals["GLOBAL_G2"] else "NEITHER")
        cats[cat]+=1
        detail.append({"position_id":r["position_id"],"source_id":r["source_id"],"context":r["context"],
                       "router_grammar":r["router_grammar"],"routed":vals["ROUTED"],"global_g2":vals["GLOBAL_G2"],"category":cat})
    n=len(rows)
    rates={p:len(positive[p])/n if n else 0 for p in positive}
    for s in source:
        for p in source[s]:
            z=source[s][p];z["fraction"]=z["positive"]/z["n"] if z["n"] else 0
    for k in cell:
        for p in cell[k]:
            z=cell[k][p];z["fraction"]=z["positive"]/z["n"] if z["n"] else 0
    routed_sources=all(source[s]["ROUTED"]["fraction"]>=0.25 for s in source)
    routed_cells=sum(1 for k in cell if cell[k]["ROUTED"]["positive"]>0)
    routed_engine_sources=True
    gate=(rates["ROUTED"]>=0.35 and routed_cells>=6 and len(source)>=2 and routed_sources and
          len(positive["ROUTED"])>len(positive["GLOBAL_G2"]))
    verdict=("PASS_CONTEXT_ROUTER_HELDOUT_SUPERIORITY_DEFECT_REPLAY_REENTRY" if gate else
             "PASS_ROUTER_POSITIVITY_NO_GLOBAL_G2_SUPERIORITY" if rates["ROUTED"]>=0.35 and routed_sources else
             "HOLD_ROUTER_PREFERENCE_SUPPORT_INSUFFICIENT")
    out={
      "schema":"c3x-g10-p16-router-validation-v1","stage":"C3X 0.9.0-G10-P16","verdict":verdict,
      "admitted_pair_positions":n,"structural_positions":struct,
      "preference_positive_positions":{k:len(v) for k,v in positive.items()},
      "preference_positive_fraction":rates,"paired_categories":dict(cats),
      "routed_positive_context_cells":routed_cells,
      "by_source":{s:dict(v) for s,v in source.items()},"by_context":{k:dict(v) for k,v in cell.items()},
      "superiority_difference_positions":len(positive["ROUTED"])-len(positive["GLOBAL_G2"]),
      "router_gate_pass":gate,"position_rows":detail,
      "edited_native_choice_consulted":False,"search_event_outcomes_consulted":False,"defect_outcomes_consulted":False
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P16_ROUTER_VALIDATION",verdict)
    print("N",n,"STRUCT",struct,"POS",out["preference_positive_positions"],"RATE",rates)
    print("PAIRED",dict(cats),"CELLS",routed_cells,"DIFF",out["superiority_difference_positions"])
    print("SOURCE",json.dumps(out["by_source"],sort_keys=True))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
    r=sub.add_parser("run");r.add_argument("--corpus",required=True);r.add_argument("--pair-freeze",required=True);r.add_argument("--router",required=True);r.add_argument("--build-dir",required=True);r.add_argument("--shard",type=int,required=True);r.add_argument("--shards",type=int,required=True);r.add_argument("--out-dir",required=True)
    g=sub.add_parser("aggregate");g.add_argument("--corpus",required=True);g.add_argument("--pair-freeze",required=True);g.add_argument("--worlds",required=True);g.add_argument("--out",required=True)
    a=ap.parse_args();run(a) if a.cmd=="run" else aggregate(a)
if __name__=="__main__":main()
