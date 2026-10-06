#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict,Counter
from pathlib import Path
import chess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g10_p20_forced as forced
import p32_event_court as p32

ARMS=("BASE","NO_CUTOFF","NO_MOVE","NO_EVAL","NO_REDUCTION")

def load(p): return json.loads(Path(p).read_text())
def chain_sig(ch): return "|".join([ch["target_edit"],ch["subset_edit"],ch["sham_edit"],",".join(ch.get("target_atoms",[])),",".join(ch.get("subset_atoms",[]))])
def world_rows(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p19-engine-support-world-v1":out.append(x)
    return out
def find_binary(root,e):
    xs=list(Path(root).rglob(f"c3x-p20-{e}"))
    if len(xs)!=1: raise SystemExit(f"P20_BINARY_{e}_{len(xs)}")
    xs[0].chmod(0o755); return xs[0]
def cases(tensor,worlddir):
    T=load(tensor);bypos=defaultdict(list)
    for w in world_rows(worlddir): bypos[w["position_id"]].append(w)
    out=[]
    for r in T["rows"]:
        hit=None
        for w in bypos[r["position_id"]]:
            for _,ch in w["chains"].items():
                if ch and chain_sig(ch)==r["chain_signature"]: hit=(w,ch); break
            if hit: break
        if not hit: raise SystemExit("P20_JOIN "+r["row_id"])
        w,ch=hit
        for e,v in r["engine_survival"].items():
            if v is None: continue
            out.append({"case_id":r["row_id"]+"|"+e,"row_id":r["row_id"],"position_id":r["position_id"],
                "source_id":r["source_id"],"engine":e,"expected":bool(v),"raw":r["raw"],"chain":ch,"pair":w["pair"]})
    return out
def measure(b,protocol,fen,A,B,root,arm):
    legal={m.uci() for m in chess.Board(fen).legal_moves};vals={}
    for i,m in enumerate((A,B)):
        cps=[]
        for rep in range(2):
            s=forced.run(b,protocol,fen,m,20000,Path(root)/f"{i}-{rep}",arm)
            cps.append(forced.score_cp(s.get("score")))
        stable=None not in cps and len(set(cps))==1
        vals[m]={"stable":stable,"cp":cps[0] if stable else None}
    gap=None if not all(vals[m]["stable"] for m in (A,B)) else abs(vals[A]["cp"]-vals[B]["cp"])
    return {"pair":vals,"gap_cp_abs":gap,"supported":bool(A in legal and B in legal and gap is not None and gap<=50)}
def run(a):
    selected=tuple(x for x in a.arms.split(",") if x)
    if not selected or any(x not in ARMS for x in selected): raise SystemExit("P20_BAD_ARMS")
    cs=cases(a.tensor,a.worlds);out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
    for i,c in enumerate(cs):
        if i%a.shards!=a.shard: continue
        b=find_binary(a.build_dir,c["engine"]);protocol=p32.protocol_for(c["engine"])
        A=c["pair"]["A"]["uci"];B=c["pair"]["B"]["uci"];arms={}
        for arm in selected:
            bb={}
            for bn,key in (("TARGET","target_fen"),("SUBSET","subset_fen"),("SHAM","sham_fen")):
                bb[bn]=measure(b,protocol,c["chain"][key],A,B,out/f".private-{i}-{arm}-{bn}",arm)
            arms[arm]={"boards":bb,"supported":all(z["supported"] for z in bb.values())}
        row={"schema":"c3x-g10-p20-class-screen-row-v1","stage":"C3X 0.10.0-G10-P20",**c,"arms":arms,
             "base_reproduces_p19":(arms["BASE"]["supported"]==c["expected"]) if "BASE" in arms else None,
             "mediator_outcomes_opened":any(x!="BASE" for x in selected)}
        (out/f"{i:03d}-{c['engine']}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
    print("P20_SCREEN_SHARD",a.shard,n,"ARMS",",".join(selected))
def collect(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p20-class-screen-row-v1":out.append(x)
    return out
def basecheck(a):
    rows=collect(a.rows);bad=[r["case_id"] for r in rows if r.get("base_reproduces_p19") is not True]
    out={"schema":"c3x-g10-p20-base-transparency-v1","stage":"C3X 0.10.0-G10-P20","row_count":len(rows),
         "mismatches":bad,"mediator_outcomes_consulted":False,"verdict":"PASS" if rows and not bad else "FAIL"}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_BASE",out["verdict"],"ROWS",len(rows),"BAD",len(bad))
def aggregate(a):
    base=collect(a.base_rows);intr=collect(a.rows);bm={r["case_id"]:r for r in base};im={r["case_id"]:r for r in intr}
    if not bm or set(bm)!=set(im): raise SystemExit(f"P20_ROW_SET {len(bm)} {len(im)}")
    rows=[]
    for cid in sorted(bm):
        x=dict(bm[cid]);x["arms"]=dict(x["arms"]);x["arms"].update(im[cid]["arms"]);rows.append(x)
    bad=[r["case_id"] for r in rows if r.get("base_reproduces_p19") is not True];fam={}
    for arm in ARMS[1:]:
        changed=[r for r in rows if r["arms"][arm]["supported"]!=r["arms"]["BASE"]["supported"]]
        fam[arm]={"changed":len(changed),"cases":[r["case_id"] for r in changed],
                  "engines":dict(Counter(r["engine"] for r in changed)),"sources":dict(Counter(r["source_id"] for r in changed))}
    A=load(a.adjudication);rm={r["case_id"]:r for r in rows};obs=[]
    for o in A["ferrers_diagnostic"]["obstruction_witnesses"]:
        e1,e2=o["engine_pair"]
        for rid in (o["row_x"],o["row_y"]):
            x=rm.get(rid+"|"+e1);y=rm.get(rid+"|"+e2)
            if not x or not y: continue
            d0=int(x["arms"]["BASE"]["supported"])-int(y["arms"]["BASE"]["supported"])
            z={"engine_pair":[e1,e2],"row_id":rid,"base":d0,"arms":{}}
            for arm in ARMS[1:]:
                d=int(x["arms"][arm]["supported"])-int(y["arms"][arm]["supported"])
                z["arms"][arm]={"contrast":d,"breaks":d!=d0,"collapses":d==0,"reverses":d==-d0}
            obs.append(z)
    out={"schema":"c3x-g10-p20-class-screen-v1","stage":"C3X 0.10.0-G10-P20","row_count":len(rows),
         "base_identity":{"pass":not bad,"mismatches":bad},"families":fam,"obstructions":obs,
         "verdict":"PASS_CLASS_SCREEN" if not bad else "FAIL_INSTRUMENT_TRANSPARENCY"}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_SCREEN",out["verdict"],"ROWS",len(rows))
    for k,v in fam.items(): print("FAMILY",k,v["changed"],v["engines"],v["sources"])
    for z in obs: print("OBSTRUCTION",json.dumps(z,sort_keys=True))
def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    q=sp.add_parser("run");q.add_argument("--tensor",required=True);q.add_argument("--worlds",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--shard",type=int,required=True);q.add_argument("--shards",type=int,required=True);q.add_argument("--out-dir",required=True);q.add_argument("--arms",required=True)
    q=sp.add_parser("basecheck");q.add_argument("--rows",required=True);q.add_argument("--out",required=True)
    q=sp.add_parser("aggregate");q.add_argument("--adjudication",required=True);q.add_argument("--base-rows",required=True);q.add_argument("--rows",required=True);q.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="run":run(a)
    elif a.cmd=="basecheck":basecheck(a)
    else:aggregate(a)
if __name__=="__main__":main()
