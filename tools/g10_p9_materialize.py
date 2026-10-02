#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from copy import deepcopy
from pathlib import Path
import harness.g95_p16_court as p16

def load(p): return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pair-freeze",action="append",required=True)
    ap.add_argument("--census",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    pfs=[p16.load_pair(x) for x in a.pair_freeze]
    census=load(a.census)
    assert census["verdict"]=="PASS_PREOUTCOME_GRADED_SELECTOR_POSITIVITY"
    positions={};cases=[];template=None
    for pf in pfs:
        if template is None: template=pf
        positions.update(pf["positions"]);cases.extend(pf["cases"])
    arm={};selected=set()
    for z in census["assignments"]:
        arm[z["target_position_id"]]="TARGET"
        arm[z["control_position_id"]]="CONTROL"
        selected|={z["target_position_id"],z["control_position_id"]}
    selected_positions={pid:deepcopy(positions[pid]) for pid in sorted(selected)}
    for pid,p in selected_positions.items(): p["p9_arm"]=arm[pid]
    selected_cases=[]
    for c in cases:
        if c["position_id"] in selected:
            z=deepcopy(c);z["position_pair"]=selected_positions[c["position_id"]];z["p9_arm"]=arm[c["position_id"]];selected_cases.append(z)
    keys=("schema","scientific_stage","execution","chain_constitution","exact_event_mediator","bridge_definitions","structural_equivalence","support_gate","certificate","claim_ceiling","variants")
    out={k:deepcopy(template[k]) for k in keys}
    out.update({
      "design_receipt_sha256":"P9_GRADED_PREOUTCOME_ASSIGNMENT",
      "intervention_outcomes_consulted":False,
      "admitted_pair_positions":sum(p.get("admitted",False) for p in selected_positions.values()),
      "active_engine_worlds":sum(1 for c in selected_cases if c["engine_view"].get("active")),
      "positions_with_chain_candidates":sum(bool(p.get("chain_candidates")) for p in selected_positions.values()),
      "positions":selected_positions,"cases":selected_cases,
      "p9_preoutcome_verdict":census["verdict"],
    })
    p16.seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P9_SELECTED_POSITIONS",len(selected_positions))

if __name__=="__main__": main()
