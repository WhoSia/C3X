#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict,Counter
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--balanced-corpus",required=True)
    ap.add_argument("--pair-freeze",required=True)
    ap.add_argument("--chain-freeze",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    corp=load(a.balanced_corpus);pf=load(a.pair_freeze);cf=load(a.chain_freeze)
    if corp.get("verdict")!="PASS_BALANCED_CHESS_ECOLOGY_POSITIVITY":raise SystemExit("P14_ECOLOGY_NOT_PASS")
    ctx={f"p14:{z['source_id']}:{z['trajectory_hash'][:12]}":z["cell"] for z in corp["positions"]}
    pos_total=len(pf["positions"])
    admitted=[z for z in pf["positions"].values() if z.get("admitted")]
    chain_pos=[pid for pid,z in cf["selected_chains"].items() if z]
    bysource_eng=defaultdict(set);cells=set();rows=[]
    for pid,z in pf["positions"].items():
        c=ctx.get(pid)
        if c is None:raise SystemExit("P14_CONTEXT_JOIN_"+pid)
        active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"))
        for e in active:bysource_eng[z["source_id"]].add(e)
        if pid in chain_pos:
            cells.add((c["phase"],c["branching"],c["tactical_surface"]))
        rows.append({
          "position_id":pid,"source_id":z["source_id"],"context":c,
          "pair_admitted":bool(z.get("admitted")),"active_engines":active,
          "selected_chain_count":len(cf["selected_chains"].get(pid,[]))
        })
    pair_frac=len(admitted)/pos_total if pos_total else 0
    chain_frac=len(chain_pos)/len(admitted) if admitted else 0
    min_eng=min((len(v) for v in bysource_eng.values()),default=0)
    pass_gate=pair_frac>=0.45 and chain_frac>=0.35 and min_eng>=2 and len(cells)>=6
    verdict="PASS_BALANCED_SEARCH_STATE_POSITIVITY_REPLAY_FROZEN" if pass_gate else "HOLD_BALANCED_SEARCH_STATE_POSITIVITY_INSUFFICIENT"

    # Outcome-blind Stage-C allocation: at most one position per context x source.
    candidates=[]
    for pid,z in pf["positions"].items():
        chains=cf["selected_chains"].get(pid,[])
        if not chains:continue
        c=ctx[pid]
        support=max((x["support_count"] for x in chains),default=0)
        maxgap=min((x["max_gap_cp_abs"] for x in chains),default=999)
        candidates.append((c["phase"],c["branching"],c["tactical_surface"],z["source_id"],-support,maxgap,pid))
    chosen=[];seen=set()
    for x in sorted(candidates):
        key=x[:4]
        if key in seen:continue
        seen.add(key);chosen.append(x[-1])
    allocation=[next(r for r in rows if r["position_id"]==pid) for pid in chosen]
    out={
      "schema":"c3x-g10-p14-search-positivity-v1","verdict":verdict,
      "pair_positions":len(admitted),"total_positions":pos_total,"pair_fraction":pair_frac,
      "chain_positions":len(chain_pos),"chain_fraction_of_pairs":chain_frac,
      "active_engines_by_source":{k:sorted(v) for k,v in sorted(bysource_eng.items())},
      "context_cells_with_chain_support":len(cells),
      "chain_supported_cells":[{"phase":x[0],"branching":x[1],"tactical_surface":x[2]} for x in sorted(cells)],
      "stage_c_allocation_frozen":pass_gate,
      "stage_c_position_ids":chosen if pass_gate else [],
      "stage_c_allocation_rows":allocation if pass_gate else [],
      "intervention_outcomes_consulted":False,"defect_outcomes_consulted":False,
      "position_rows":rows
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P14_SEARCH_GATE",verdict)
    print("PAIR",len(admitted),"/",pos_total,pair_frac)
    print("CHAIN",len(chain_pos),"/",len(admitted),chain_frac)
    print("CELLS",len(cells),"ALLOC",len(chosen) if pass_gate else 0)
    print("ACTIVE_ENGINES",out["active_engines_by_source"])
if __name__=="__main__":main()
