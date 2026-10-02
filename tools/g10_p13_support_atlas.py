#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
import chess
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("p13",ROOT/"tools/g10_p13_context_factorization.py")
p13=importlib.util.module_from_spec(spec);spec.loader.exec_module(p13)

def load(p):return json.loads(Path(p).read_text())
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True);ap.add_argument("--chain-freeze",required=True)
    ap.add_argument("--p9-census",required=True);ap.add_argument("--primary",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    worlds=p13.collect(a.worlds);freeze=load(a.chain_freeze);census=load(a.p9_census);primary=load(a.primary)
    cases={x["case_id"]:x for x in freeze["cases"]}
    # Position-level chess context census, avoiding triple-counting engine-pair/edit rows.
    pos={}
    for w in worlds:
        case=cases[w["case_id"]];pid=w["position_id"];src=w["source_id"]
        if (src,pid) in pos:continue
        b=chess.Board(case["cell"]["fen"])
        A=case["position_pair"]["pair"]["A"]["uci"];B=case["position_pair"]["pair"]["B"]["uci"]
        br,n=p13.branching(b)
        ps=census["position_scores"].get(pid,{})
        pos[(src,pid)]={
          "material_phase":p13.material_phase(b),"material_imbalance":p13.material_imbalance(b),
          "legal_branching":br,"legal_move_count":n,"in_check":str(bool(b.is_check())),
          "candidate_tactical_mode":p13.cand_mode(b,A,B),
          "polarity":"|".join(ps.get("polarity_profile",[])),
          "family_distance_bucket":p13.fd_bucket(ps.get("family_distance",99))
        }
    sources=sorted({s for s,_ in pos})
    fields=("material_phase","material_imbalance","legal_branching","in_check","candidate_tactical_mode","polarity","family_distance_bucket")
    dist={}
    for src in sources:
        rows=[v for (s,_),v in pos.items() if s==src]
        dist[src]={"positions":len(rows)}
        for f in fields:
            c=Counter(r[f] for r in rows);dist[src][f]=dict(sorted(c.items()))
        vals=[r["legal_move_count"] for r in rows]
        dist[src]["legal_move_count"]={"min":min(vals),"max":max(vals),"mean":sum(vals)/len(vals)}
    # summarize overlap ladder from primary artifact
    levels=defaultdict(lambda:{"pair_edits":0,"cells":0,"weight":0,"overlap_mass":[]})
    for pair,x in primary["pair_edit_results"].items():
      for edit,y in x.items():
        for level,z in y.items():
          levels[level]["pair_edits"]+=1;levels[level]["cells"]+=z["matched_cell_count"];levels[level]["weight"]+=z["matched_weight"];levels[level]["overlap_mass"].append(z["overlap_mass"])
    for level,z in levels.items():
        z["mean_overlap_mass"]=sum(z["overlap_mass"])/len(z["overlap_mass"]);del z["overlap_mass"]
    out={
      "schema":"c3x-g10-p13-posthold-support-atlas-v1","status":"POST_RESULT_DESCRIPTIVE_DEMOTION_ONLY",
      "can_strengthen_primary":False,"primary_verdict":primary["verdict"],
      "source_position_context_distribution":dist,"context_overlap_ladder":dict(levels),
      "interpretation":[
        "The development ecology is dominated by rich-material, non-check positions.",
        "Exact FULL-context overlap is too sparse for the preregistered composition-vs-drift estimand.",
        "Lower-resolution overlap is reported only to diagnose which coordinates consume support; it cannot rescue the primary HOLD."
      ]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P13_SUPPORT_ATLAS_PASS")
    print("DIST",json.dumps(dist,sort_keys=True))
    print("OVERLAP",json.dumps(dict(levels),sort_keys=True))
if __name__=="__main__":main()
