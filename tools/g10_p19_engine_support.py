#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,hashlib
from pathlib import Path
import chess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import g10_p15_grammar_census as gc
import g10_p15_preference_support as ps

def load(p): return json.loads(Path(p).read_text())
def find_binary(root,e):
    xs=list(Path(root).rglob(f"c3x-p16-{e}"))
    if len(xs)!=1: raise SystemExit(f"P19_BINARY {e} {len(xs)}")
    xs[0].chmod(0o755); return xs[0]
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()
def choose_chain(fen,pair,grammar):
    edits=gc.enumerate_edits(fen,pair["A"]["uci"],pair["B"]["uci"])
    chains=gc.chains_for(edits,grammar)
    if not chains:return None
    c=chains[0]
    return {"type":c["type"],"target_edit":c["target"]["edit_id"],"subset_edit":c["subset"]["edit_id"],"sham_edit":c["sham"]["edit_id"],
      "target_atoms":list(c["target"]["atoms"]),"subset_atoms":list(c["subset"]["atoms"]),
      "piece_type":c["target"]["piece_type"],"side_role":c["target"]["side_role"],"profile":c["target"]["profile"],
      "total_collateral":c["total_collateral"],"target_fen":c["target"]["fen"],"subset_fen":c["subset"]["fen"],"sham_fen":c["sham"]["fen"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",required=True);ap.add_argument("--pair-freeze",required=True);ap.add_argument("--build-dir",required=True)
    ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    corpus=load(a.corpus);pf=load(a.pair_freeze)
    bypid={f"p19:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corpus["positions"]}
    admitted=[(pid,z) for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True);n=0
    for idx,(pid,z) in enumerate(admitted):
        if idx%a.shards!=a.shard:continue
        meta=bypid.get(pid)
        if meta is None:raise SystemExit(f"P19_META {pid}")
        route=meta["router_grammar"]
        if route=="ABSTAIN":raise SystemExit(f"P19_ADMITTED_OUTSIDE_ROUTE {pid}")
        pair=z["pair"];fen=meta["fen"]
        policy_chain={"ROUTED":choose_chain(fen,pair,route),"GLOBAL_G2":choose_chain(fen,pair,"G2_SAME_TYPE_SIDE_COLLATERAL")}
        active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"))
        engines={}
        for e in active:
            binary=find_binary(a.build_dir,e); expected=pf["variants"][e]["sha256"]
            if sha_file(binary)!=expected:raise SystemExit(f"P19_BIN_SHA {e}")
            protocol=pf["variants"][e].get("protocol");engines[e]={}
            for pol,ch in policy_chain.items():
                if ch is None:
                    engines[e][pol]={"structural":False,"supported":False,"boards":None};continue
                A=pair["A"]["uci"];B=pair["B"]["uci"];root=outdir/f".private-{idx}-{e}-{pol}"
                boards={"TARGET":ps.measure(binary,protocol,ch["target_fen"],A,B,20000,2,root,"target"),
                        "SUBSET":ps.measure(binary,protocol,ch["subset_fen"],A,B,20000,2,root,"subset"),
                        "SHAM":ps.measure(binary,protocol,ch["sham_fen"],A,B,20000,2,root,"sham")}
                engines[e][pol]={"structural":True,"supported":all(v["supported"] for v in boards.values()),"boards":boards}
        row={"schema":"c3x-g10-p19-engine-support-world-v1","stage":"C3X 0.9.0-G10-P19",
          "position_id":pid,"source_id":z["source_id"],"context":meta["context"],"router_grammar":route,"pair":pair,
          "active_engines":active,"chains":policy_chain,"engines":engines,
          "edited_native_choice_consulted":False,"search_event_outcomes_consulted":False,"defect_outcomes_consulted":False}
        (outdir/f"{idx:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
    print("G10_P19_VALIDATE_SHARD",a.shard,n)
if __name__=="__main__": main()
