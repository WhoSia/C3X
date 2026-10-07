#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
import g10_p19_source_census as p19

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",action="append",required=True,help="ID|PGN|URL|SHA256")
    ap.add_argument("--history-root",default=".")
    ap.add_argument("--ply-lo",type=int,default=12);ap.add_argument("--ply-hi",type=int,default=160)
    ap.add_argument("--game-limit",type=int,default=20000)
    ap.add_argument("--min-cell-support",type=int,default=4)
    ap.add_argument("--per-source-cell",type=int,default=2)
    ap.add_argument("--max-common-cells",type=int,default=8)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    specs=[]
    for raw in a.source:
        z=raw.split("|")
        if len(z)!=4:raise SystemExit("P22_SOURCE_SPEC")
        specs.append(tuple(z))
    if len(specs)!=2:raise SystemExit("P22_REQUIRE_TWO_SOURCES")
    excluded,hfiles=p19.historical_hashes(a.history_root)
    pools={};audit={}
    for sid,path,url,digest in specs:
        pools[sid],audit[sid]=p19.source_candidates(path,sid,excluded,a.ply_lo,a.ply_hi,a.game_limit)
        audit[sid].update({"url":url,"source_sha256":digest})
    fs=defaultdict(set)
    for sid,pool in pools.items():
        for rows in pool.values():
            for r in rows:fs[r["candidate_sha256"]].add(sid)
    crossdup={h for h,ss in fs.items() if len(ss)>1}
    for sid,pool in pools.items():
        for cell in list(pool):
            pool[cell]=[r for r in pool[cell] if r["candidate_sha256"] not in crossdup]
    allcells=[(ph,br,ta) for ph in p19.PHASES for br in p19.BRANCHES for ta in p19.TACTICS]
    common=[];support={}
    for cell in allcells:
        counts={sid:len(pools[sid].get(cell,[])) for sid,_,_,_ in specs}
        support["|".join(cell)]=counts
        if all(v>=a.min_cell_support for v in counts.values()):common.append(cell)
    common=sorted(common,key=lambda c:p19.PHASES.index(c[0])*9+p19.BRANCHES.index(c[1])*3+p19.TACTICS.index(c[2]))
    selected_cells=common[:a.max_common_cells]
    selected=[];used=set()
    for cell in selected_cells:
        for sid,_,_,_ in specs:
            take=[]
            for r in pools[sid][cell]:
                if r["candidate_sha256"] in used:continue
                used.add(r["candidate_sha256"]);take.append(r)
                if len(take)==a.per_source_cell:break
            if len(take)!=a.per_source_cell:raise SystemExit("P22_DEDUP_SHORT_"+"|".join(cell)+"_"+sid)
            selected.extend(take)
    phases=sorted({c[0] for c in selected_cells});branches=sorted({c[1] for c in selected_cells});tactics=sorted({c[2] for c in selected_cells})
    gate={"common_cells":len(selected_cells),"positions":len(selected),"phase_levels":phases,"branching_levels":branches,"tactical_levels":tactics,
          "history_hashes_excluded":len(excluded),"history_json_files_scanned":hfiles,"cross_source_duplicate_fens_excluded":len(crossdup)}
    passed=len(selected_cells)>=6 and len(selected)>=24 and len(phases)>=2 and len(branches)>=2 and len(tactics)>=2
    out={"schema":"c3x-g10-p22-heldout-census-v1","stage":"C3X 0.10.0-G10-P22",
         "verdict":"PASS_HELDOUT_WORLD_ECOLOGY_READY" if passed else "HOLD_HELDOUT_WORLD_ECOLOGY_SUPPORT",
         "authority":"PRE_PREDICTION_PRE_ENGINE_OUTCOME_SELECTION_ONLY",
         "selection":{"activation_predictions_consulted":False,"engine_outcomes_consulted":False,"full_class_outcomes_consulted":False,
                      "historical_fen_and_candidate_hashes_excluded":True,"cross_source_duplicate_fens_excluded":True,
                      "provider_independence_claimed":False,"cell":"phase × branching × tactical_surface",
                      "min_cell_support_per_source":a.min_cell_support,"positions_per_source_per_cell":a.per_source_cell,
                      "max_common_cells":a.max_common_cells,"ply_range":[a.ply_lo,a.ply_hi]},
         "source_audit":audit,"cell_support_after_history_exclusion":support,
         "selected_cells":[{"phase":c[0],"branching":c[1],"tactical_surface":c[2]} for c in selected_cells],
         "gate":gate,
         "positions":sorted(selected,key=lambda r:(r["source_id"],r["cell"]["phase"],r["cell"]["branching"],r["cell"]["tactical_surface"],r["trajectory_hash"]))}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P22_HELDOUT_CENSUS",out["verdict"]);print("GATE",json.dumps(gate,sort_keys=True))
    if not passed:raise SystemExit("P22_HELDOUT_CENSUS_HOLD")
if __name__=="__main__":main()
