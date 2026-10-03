#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--gate",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    g=load(a.gate)
    rows=g["position_rows"]
    cells=defaultdict(lambda:{"positions":0,"pair":0,"chain":0,"sources":set(),"active_engines":set()})
    src=defaultdict(lambda:{"positions":0,"pair":0,"chain":0,"cells":set()})
    for r in rows:
        c=r["context"]; key=(c["phase"],c["branching"],c["tactical_surface"])
        z=cells[key];z["positions"]+=1;z["sources"].add(r["source_id"]);z["active_engines"].update(r["active_engines"])
        src[r["source_id"]]["positions"]+=1;src[r["source_id"]]["cells"].add(key)
        if r["pair_admitted"]:
            z["pair"]+=1;src[r["source_id"]]["pair"]+=1
        if r["selected_chain_count"]>0:
            z["chain"]+=1;src[r["source_id"]]["chain"]+=1
    cell_rows=[]
    for k,z in sorted(cells.items()):
        cell_rows.append({
          "phase":k[0],"branching":k[1],"tactical_surface":k[2],
          "positions":z["positions"],"pair_positions":z["pair"],"chain_positions":z["chain"],
          "pair_rate":z["pair"]/z["positions"] if z["positions"] else None,
          "chain_rate_given_pair":z["chain"]/z["pair"] if z["pair"] else None,
          "chain_rate_total":z["chain"]/z["positions"] if z["positions"] else None,
          "source_count":len(z["sources"]),"active_engines":sorted(z["active_engines"])
        })
    src_rows={}
    for s,z in sorted(src.items()):
        src_rows[s]={
          "positions":z["positions"],"pair_positions":z["pair"],"chain_positions":z["chain"],
          "pair_rate":z["pair"]/z["positions"] if z["positions"] else None,
          "chain_rate_given_pair":z["chain"]/z["pair"] if z["pair"] else None,
          "context_cells":len(z["cells"])
        }
    bottleneck=sorted(cell_rows,key=lambda x:(x["chain_rate_given_pair"] if x["chain_rate_given_pair"] is not None else 2,x["phase"],x["branching"],x["tactical_surface"]))
    best=sorted(cell_rows,key=lambda x:(-(x["chain_rate_given_pair"] or 0),-x["chain_positions"],x["phase"],x["branching"],x["tactical_surface"]))
    out={
      "schema":"c3x-g10-p14-stage-b-support-atlas-v1",
      "status":"POST_GATE_DEMOTION_ONLY",
      "can_strengthen_stage_b":False,
      "stage_b_verdict":g["verdict"],
      "global":{
        "positions":g["total_positions"],"pair_positions":g["pair_positions"],"chain_positions":g["chain_positions"],
        "pair_fraction":g["pair_fraction"],"chain_fraction_of_pairs":g["chain_fraction_of_pairs"],
        "context_cells_with_chain_support":g["context_cells_with_chain_support"]
      },
      "source_rows":src_rows,
      "cell_rows":cell_rows,
      "lowest_chain_feasibility_cells":bottleneck[:10],
      "highest_chain_feasibility_cells":best[:10],
      "interpretation":"Pair positivity survives balanced acquisition, but P16 chain-preserving perturbation feasibility is the dominant bottleneck. Atlas is descriptive and cannot rescue the Stage-B HOLD."
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P14_STAGE_B_ATLAS_PASS")
    print("SOURCE",json.dumps(src_rows,sort_keys=True))
    print("LOW",json.dumps(bottleneck[:10],sort_keys=True))
    print("HIGH",json.dumps(best[:10],sort_keys=True))
if __name__=="__main__": main()
