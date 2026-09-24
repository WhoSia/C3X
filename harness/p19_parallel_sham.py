#!/usr/bin/env python3
import argparse,hashlib,json,os
from pathlib import Path
import p19_morphism as p19

TARGETS=p19.TARGETS
FAMILIES=p19.FAMILIES

def sha_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def census(a):
    stage=json.loads(Path(a.stage_a).read_text())
    bins=p19.bins(a.binary)
    fam=a.family
    src=[c for c in stage["candidates"] if c["material_seed_name"]==fam]
    if len(src)!=72: raise SystemExit(f"P19-PARALLEL-CENSUS-STAGE-A {fam} {len(src)}/72")
    rows=[]
    for i,c in enumerate(src,1):
        sham={}; eg={}; allpass=True
        for t,path in bins.items():
            r=p19.run_search(path,c["fen"],"SHAM")
            sham[t]=r
            eg[t]=p19.engagement(r)
            allpass=allpass and eg[t]["passed"]
        floor=min(eg[t]["site_use_floor"] for t in TARGETS)
        rows.append({"candidate":c,"sham":sham,"engagement":eg,
                     "all_targets_engaged":allpass,"selection_floor":floor})
        print(f"P19_PARALLEL_SHAM {fam} {i:02d}/72 pass={allpass} floor={floor}",flush=True)
    payload={
      "schema":"c3x-p19-sham-census-vertex-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P19",
      "family":fam,
      "stage_a_pool_sha256":stage["pool_sha256"],
      "intervention_outcomes_consulted":False,
      "binary_sha256":{t:sha_file(path) for t,path in bins.items()},
      "rows":rows,
      "counts":{
        "total":len(rows),
        "engaged_total":sum(r["all_targets_engaged"] for r in rows),
        "engaged_by_side":{
          s:sum(r["all_targets_engaged"] and r["candidate"]["side_to_move"]==s for r in rows)
          for s in ("WHITE","BLACK")
        }
      }
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P19_VERTEX_CENSUS_PASS",fam,payload["counts"])

def parse_census(items):
    out={}
    for x in items:
        fam,path=x.split("=",1)
        if fam in out: raise SystemExit(f"P19-CENSUS-DUP {fam}")
        out[fam]=json.loads(Path(path).read_text())
    if set(out)!=set(FAMILIES): raise SystemExit(f"P19-CENSUS-FAMILY-SET {sorted(out)}")
    return out

def seal(a):
    stage=json.loads(Path(a.stage_a).read_text())
    cs=parse_census(a.census)
    shas=None
    selected=[]; counts={}
    for fam in FAMILIES:
        x=cs[fam]
        if x.get("intervention_outcomes_consulted") is not False: raise SystemExit("P19-CENSUS-OUTCOME-LEAK")
        if x["stage_a_pool_sha256"]!=stage["pool_sha256"]: raise SystemExit("P19-CENSUS-POOL-MISMATCH")
        if shas is None: shas=x["binary_sha256"]
        elif x["binary_sha256"]!=shas: raise SystemExit("P19-CENSUS-BINARY-MISMATCH")
        rows=x["rows"]
        elig=[r for r in rows if r["all_targets_engaged"]]
        chosen=p19.select_vertex(elig)
        side_elig={s:sum(r["candidate"]["side_to_move"]==s for r in elig) for s in ("WHITE","BLACK")}
        if len(chosen)!=12:
            raise SystemExit(f"P19-ENGAGEMENT-HOLD {fam} eligible={len(elig)} by_side={side_elig} committed={len(chosen)}")
        counts[fam]={
          "eligible":len(elig),
          "eligible_by_side":side_elig,
          "committed":12,
          "committed_by_side":{"WHITE":6,"BLACK":6}
        }
        selected.extend(chosen)
    payload={
      "schema":"c3x-p19-sham-precommit-v2-parallel",
      "scientific_stage":"C3X 0.7.0-G9.4-P19",
      "stage_a_pool_sha256":stage["pool_sha256"],
      "intervention_outcomes_consulted":False,
      "engine_targets":list(TARGETS),
      "chronology":list(p19.CHRONOLOGY),
      "binaries":{
        "stockfish_18":{"sha256":shas["stockfish_18"],"path_basename":"c3x-p19-sf18"},
        "frozen_20260810":{"sha256":shas["frozen_20260810"],"path_basename":"c3x-p19-frozen"},
        "stockfish_19":{"sha256":shas["stockfish_19"],"path_basename":"c3x-p19-sf19"}
      },
      "runtime":{"threads":1,"hash_mib":64,"nodes":p19.NODES,"clear_hash_each_arm":True,"syzygy_probe_limit":0},
      "counts":{"stage_a":len(stage["candidates"]),"committed":len(selected),"by_vertex":counts},
      "authorization":"P19-MORPHISM-READY",
      "committed_cells":selected
    }
    payload["precommit_sha256"]=p19.sha_obj(payload)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P19_PARALLEL_PRECOMMIT",payload["precommit_sha256"],payload["counts"])

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    c=sp.add_parser("census")
    c.add_argument("--stage-a",required=True)
    c.add_argument("--binary",action="append",required=True)
    c.add_argument("--family",choices=FAMILIES,required=True)
    c.add_argument("--out",required=True)
    s=sp.add_parser("seal")
    s.add_argument("--stage-a",required=True)
    s.add_argument("--census",action="append",required=True)
    s.add_argument("--out",required=True)
    a=ap.parse_args()
    {"census":census,"seal":seal}[a.cmd](a)

if __name__=="__main__":
    main()
