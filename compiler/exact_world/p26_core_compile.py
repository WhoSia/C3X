#!/usr/bin/env python3
"""P26 fresh pawnless-core exact-world constitution.
No engine, atlas, descriptor-response, or intervention outcome is consulted here.
"""
import json,sys
from pathlib import Path
import p19_compile as base
from p20_tau4_fast import tau4_fast

VERSION="c3x-p26-core-v1"
OFFSET=720000
base.VERSION=VERSION
base.OFFSET=OFFSET
base.tau4=tau4_fast

def out_path(argv):
    for i,x in enumerate(argv):
        if x=="--out" and i+1<len(argv):return Path(argv[i+1])
    raise SystemExit("P26_CORE_OUT_MISSING")

if __name__=="__main__":
    p=out_path(sys.argv);base.main();x=json.loads(p.read_text())
    x["schema"]="c3x-p26-core-part-v1"
    x["scientific_stage"]="C3X 0.7.0-G9.4-P26"
    x["compiler_version"]=VERSION
    x["engine_outcomes_consulted"]=False
    x["atlas_outcomes_consulted"]=False
    x["descriptor_response_consulted"]=False
    x["freshness"]={"generation_index_offset":OFFSET,"p20_cells_reused":False,"p21_cells_reused":False,"p22_cells_reused":False,"p23_cells_reused":False,"p24_cells_reused":False,"p25_cells_reused":False}
    x["constitution"]["lane"]="PAWNLESS_CORE"
    x["constitution"]["tau4_semantics"]="P19_FROZEN_EXACT"
    x["constitution"]["tau4_implementation"]="P20_FAST_EXACT_SEMANTIC_V1"
    x["pool_sha256"]=base.h(base.canon({k:v for k,v in x.items() if k!="pool_sha256"}))
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("P26_CORE_PART_PASS",len(x["candidates"]),x["pool_sha256"])
