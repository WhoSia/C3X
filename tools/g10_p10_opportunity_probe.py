#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g95_p13_court as p13
import g95_p15_court as p15
import g95_p16_court as p16
import p32_event_court as p32

FORBIDDEN_KEYS={"bestmove","score","wdl","pv","t_only","native_root","edited_native_choice","certificate"}

def sha_file(p):
    import hashlib
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def find_binary(root,engine):
    xs=list(Path(root).rglob(f"c3x-p16-{engine}"))
    if len(xs)!=1:raise SystemExit(f"P10_BINARY {engine} {len(xs)}")
    xs[0].chmod(0o755)
    return xs[0]

def native_topology(binary,protocol,base_cell,fen,A,B,anchor,root,tag,max_targets):
    cell={"fen":fen,"history":base_cell["history"]}
    native=p13.run_context(binary,protocol,cell,"CATALOG",None,root/f"{tag}-catalog")
    fp,key_to_move,coll=p13.fingerprint(binary,protocol,fen,[A,B],12000,root/f"{tag}-fp")
    selected,eligible=p15.select_anchor_targets(native["trace"]["events"],key_to_move,anchor,max_targets)
    by_bound={}
    for _,_,e in selected:
        bn=p15.BOUND_NAME[int(e["bound"])]
        by_bound[bn]={"depth":int(e.get("depth",0)),"ply":int(e.get("ply",-1))}
    return {
      "eligible_anchor_target_count":int(eligible),
      "available_bounds":sorted(by_bound),
      "selected_target_depth_by_bound":by_bound,
      "fingerprint_collision_count":len(coll),
      "trace_event_count":len(native["trace"]["events"]),
      "fingerprint_public_cell_count":len(fp) if hasattr(fp,"__len__") else None,
    }

def probe_case(pre,case,binary,outdir):
    if not case.get("factorial_active") or not case.get("selected_chains"):
        return {
          "schema":"c3x-g10-p10-opportunity-world-v1","case_id":case["case_id"],
          "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],
          "active":False,"chains":[],"remove_set_runs":0,"event_ablation_runs":0,
          "edited_native_choice_recorded":False,"certificate_outcomes_consulted":False
        }
    pos=case["position_pair"];A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"]
    preferred=case["engine_view"]["baseline_preferred"]
    anchor=B if preferred==A else A
    protocol=p32.protocol_for(case["engine"])
    max_targets=int(pre["execution"]["max_semantic_targets_per_board"])
    rows=[]
    for i,z in enumerate(case["selected_chains"]):
        ch=z["chain"]
        boards={
          "B0":case["cell"]["fen"],
          "TARGET":ch["target"]["fen"],
          "SUBSET":ch["subset"]["fen"],
          "SHAM":ch["sham"]["fen"],
        }
        topo={}
        for bn,fen in boards.items():
            topo[bn]=native_topology(binary,protocol,case["cell"],fen,A,B,anchor,outdir/f"chain-{i}",bn,max_targets)
        sets={bn:set(v["available_bounds"]) for bn,v in topo.items()}
        common_target=sets["B0"]&sets["TARGET"]
        common_subset=sets["B0"]&sets["SUBSET"]
        common_sham=sets["B0"]&sets["SHAM"]
        n=len(common_target)
        rows.append({
          "chain_id":ch["chain_id"],"chain_type":ch["chain_type"],
          "supporting_engines":z["supporting_engines"],
          "board_topology":topo,
          "common_target_bounds":sorted(common_target),
          "common_target_bound_count":n,
          "common_subset_bound_count":len(common_subset),
          "common_sham_bound_count":len(common_sham),
          "target_specific_common_bound_delta":n-len(common_sham),
          "opportunity_class":("NO_COMMON_BOUND" if n==0 else "ONE_COMMON_BOUND" if n==1 else "TWO_COMMON_BOUNDS"),
        })
    rows.sort(key=lambda x:(x["common_target_bound_count"],x["target_specific_common_bound_delta"],x["chain_id"]),reverse=True)
    return {
      "schema":"c3x-g10-p10-opportunity-world-v1","case_id":case["case_id"],
      "engine":case["engine"],"position_id":case["position_id"],"source_id":case["source_id"],
      "active":True,"chains":rows,
      "case_opportunity_class":rows[0]["opportunity_class"] if rows else "NO_COMMON_BOUND",
      "max_common_target_bound_count":max((x["common_target_bound_count"] for x in rows),default=0),
      "max_target_specific_common_bound_delta":max((x["target_specific_common_bound_delta"] for x in rows),default=-2),
      "remove_set_runs":0,"event_ablation_runs":0,
      "edited_native_choice_recorded":False,"certificate_outcomes_consulted":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chain-freeze",required=True)
    ap.add_argument("--build-dir",required=True)
    ap.add_argument("--shard",type=int,required=True)
    ap.add_argument("--shards",type=int,required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    pre=p16.load_chain(a.chain_freeze)
    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    done=0
    for i,case in enumerate(pre["cases"]):
        if i%a.shards!=a.shard:continue
        binary=find_binary(a.build_dir,case["engine"])
        expected=pre["variants"][case["engine"]]["sha256"]
        if sha_file(binary)!=expected:raise SystemExit(f"P10_BINARY_SHA {case['engine']}")
        row=probe_case(pre,case,binary,outdir/f"{i:03d}-{case['engine']}")
        raw=json.dumps(row,sort_keys=True)
        if any(f'"{k}"' in raw for k in FORBIDDEN_KEYS):
            raise SystemExit(f"P10_FORBIDDEN_FIELD {case['case_id']}")
        (outdir/f"{i:03d}-{case['engine']}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n")
        done+=1
    print("G10_P10_OPPORTUNITY_PROBE_PASS",a.shard,done)

if __name__=="__main__":main()
