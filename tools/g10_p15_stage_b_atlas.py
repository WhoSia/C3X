#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict,Counter
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def ckey(c): return "|".join((c["phase"],c["branching"],c["tactical_surface"]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage-a",required=True)
    ap.add_argument("--stage-b",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    sa=load(a.stage_a);sb=load(a.stage_b)
    alloc=sa["stage_b_allocation"];adm=sb["position_admissions"]
    adm_ids={x["position_id"] for x in adm}
    bycell=defaultdict(lambda:{"structural":0,"preference":0,"sources":set(),"support_engines":Counter()})
    bysrc=defaultdict(lambda:{"structural":0,"preference":0})
    for x in alloc:
        k=ckey(x["context"]);z=bycell[k]
        z["structural"]+=1;z["sources"].add(x["source_id"]);bysrc[x["source_id"]]["structural"]+=1
        if x["position_id"] in adm_ids:
            z["preference"]+=1;bysrc[x["source_id"]]["preference"]+=1
    for x in adm:
        k=ckey(x["context"])
        for e in x["supporting_engines"]:bycell[k]["support_engines"][e]+=1
    cells=[]
    for k,z in sorted(bycell.items()):
        cells.append({
          "context":k,"structural_positions":z["structural"],"preference_supported_positions":z["preference"],
          "preservation_fraction":z["preference"]/z["structural"] if z["structural"] else None,
          "source_count":len(z["sources"]),"support_engine_counts":dict(z["support_engines"])
        })
    sources={}
    for s,z in sorted(bysrc.items()):
        sources[s]={**z,"preservation_fraction":z["preference"]/z["structural"] if z["structural"] else None}
    phase=defaultdict(lambda:[0,0]);branch=defaultdict(lambda:[0,0]);tact=defaultdict(lambda:[0,0])
    for x in alloc:
        y=int(x["position_id"] in adm_ids);c=x["context"]
        for table,key in ((phase,c["phase"]),(branch,c["branching"]),(tact,c["tactical_surface"])):
            table[key][0]+=1;table[key][1]+=y
    def pack(d):
        return {k:{"structural":v[0],"preference":v[1],"preservation_fraction":v[1]/v[0] if v[0] else None} for k,v in sorted(d.items())}
    out={
      "schema":"c3x-g10-p15-stage-b-atlas-v1","status":"POST_HOLD_DEMOTION_ONLY",
      "can_strengthen_stage_b":False,"stage_b_verdict":sb["verdict"],
      "global":{
        "structural_positions":len(alloc),"preference_supported_positions":len(adm),
        "conditional_preservation":len(adm)/len(alloc) if alloc else None,
        "pair_denominator":sb["admitted_pair_positions"],
        "chain_fraction_of_pairs":sb["chain_fraction_of_pairs"]
      },
      "by_source":sources,"by_phase":pack(phase),"by_branching":pack(branch),"by_tactical_surface":pack(tact),
      "context_cells":cells,
      "lowest_preservation_cells":sorted(cells,key=lambda z:(z["preservation_fraction"],-z["structural_positions"],z["context"]))[:10],
      "highest_preservation_cells":sorted(cells,key=lambda z:(-z["preservation_fraction"],-z["preference_supported_positions"],z["context"]))[:10],
      "interpretation":"G2 recovers structural chains broadly, but preference-support preservation remains context-dependent. Atlas cannot authorize G3/G4 or alter the frozen Stage-B HOLD."
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P15_STAGE_B_ATLAS_PASS")
    print("GLOBAL",out["global"])
    print("SOURCE",json.dumps(sources,sort_keys=True))
    print("PHASE",json.dumps(out["by_phase"],sort_keys=True))
    print("BRANCH",json.dumps(out["by_branching"],sort_keys=True))
    print("TACT",json.dumps(out["by_tactical_surface"],sort_keys=True))
    print("LOW",json.dumps(out["lowest_preservation_cells"],sort_keys=True))
    print("HIGH",json.dumps(out["highest_preservation_cells"],sort_keys=True))
if __name__=="__main__":main()
