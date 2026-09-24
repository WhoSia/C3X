#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import chess
import p19_compile as base

VERSION="c3x-p21-core-v1"
OFFSET=140000

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--parts",required=True)
    ap.add_argument("--material",choices=tuple(base.VERTICES),required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    files=sorted(Path(a.parts).rglob(f"p21-core-side-{a.material}-*.json"))
    if len(files)!=2:raise SystemExit(f"P21_CORE_SIDE_FILE_COUNT {len(files)}/2")
    sides={};audit={}
    for p in files:
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p21-core-side-part-v1" or x.get("compiler_version")!=VERSION:raise SystemExit("P21_CORE_SIDE_SCHEMA")
        if x.get("engine_outcomes_consulted") is not False or x["material"]!=a.material:raise SystemExit("P21_CORE_SIDE_LEAK_OR_MATERIAL")
        sides[x["side"]]=x
    if set(sides)!={"WHITE","BLACK"}:raise SystemExit("P21_CORE_SIDE_SET")
    square,vertex,_=base.VERTICES[a.material]
    cs=sides["WHITE"]["candidates"]+sides["BLACK"]["candidates"]
    # Exact original loop order: generation index ascending, WHITE before BLACK.
    cs.sort(key=lambda c:(int(c["generation_index"]),0 if c["side_to_move"]=="WHITE" else 1))
    if len(cs)!=48:raise SystemExit("P21_CORE_SIDE_TOTAL")
    audit_vertex={
      "square":square,"vertex":vertex,
      "audited":sum(sides[s]["audit"]["audited"] for s in sides),
      "world_split_pass":sum(sides[s]["audit"]["world_split_pass"] for s in sides),
      "accepted":48,
      "accepted_by_side":{"WHITE":24,"BLACK":24}
    }
    out={
      "schema":"c3x-p21-core-part-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P21",
      "compiler_version":VERSION,
      "stockfish_outcomes_consulted":False,
      "cross_engine_outcomes_consulted":False,
      "freshness":{"generation_index_offset":OFFSET,"p20_cells_reused":False,"p20_generation_offsets_reused":False},
      "constitution":{
        "legal_move_fine_exact_value_distinct_min":2,
        "split_definition":"distinct (mover_wdl,mover_precise_dtz) tuples; robust-WDL split alone is not required",
        "lane":"PAWNLESS_CORE",
        "tau4_semantics":"P19_FROZEN_EXACT",
        "tau4_implementation":"P20_FAST_EXACT_SEMANTIC_V1"
      },
      "squares":{"HEAVY_HEAVY":{"00":"KQQvKQ","10":"KQRvKQ","01":"KQQvKR","11":"KQRvKR"},
                 "MINOR_MINOR":{"00":"KRBvKB","10":"KRNvKB","01":"KRBvKN","11":"KRNvKN"}},
      "world_authority":{"provider":"Lichess public Syzygy tablebase API","endpoint":base.API,
                         "robust_categories_only":["win","draw","loss"],"precise_dtz_required_for_every_move":True,
                         "root_halfmove_clock":0,"pawnless":True},
      "audit_by_vertex":{a.material:audit_vertex},
      "candidates":cs
    }
    out["pool_sha256"]=base.h(base.canon(out))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P21_CORE_SIDE_MERGE_PASS",a.material,out["pool_sha256"])

if __name__=="__main__":main()
