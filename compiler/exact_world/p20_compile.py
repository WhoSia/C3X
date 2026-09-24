#!/usr/bin/env python3
"""P20-R2 disjoint exact-world constitution.

Reuses the frozen P19 exact-world construction algorithm while moving both the
deterministic namespace and generation offset. No engine outcome is consulted.
"""
import json
import sys
from pathlib import Path
import p19_compile as base

VERSION="c3x-p20-r2-stage-a-v1"
OFFSET=80000

base.VERSION=VERSION
base.OFFSET=OFFSET

def out_path(argv):
    for i,x in enumerate(argv):
        if x=="--out" and i+1<len(argv):
            return Path(argv[i+1])
    raise SystemExit("P20_OUT_PATH_MISSING")

if __name__=="__main__":
    p=out_path(sys.argv)
    base.main()
    x=json.loads(p.read_text())
    x["schema"]="c3x-p20-r2-stage-a-part-v1"
    x["scientific_stage"]="C3X 0.7.0-G9.4-P20-R2"
    x["compiler_version"]=VERSION
    x["stockfish_outcomes_consulted"]=False
    x["freshness"]={
        "generation_index_offset":OFFSET,
        "p19_selected_cells_reused":False,
        "p19_generation_offsets_reused":False
    }
    x["constitution"]["cross_engine_transport_outcomes_consulted"]=False
    x["pool_sha256"]=base.h(base.canon({k:v for k,v in x.items() if k!="pool_sha256"}))
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("P20_R2_STAGE_A_PART_PASS",len(x["candidates"]),x["pool_sha256"])
