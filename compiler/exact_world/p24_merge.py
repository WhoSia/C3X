#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
FAMILIES=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
VERSION="c3x-p24-core-v1";PART="c3x-p24-core-part-v1";OFFSET=520000

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--parts",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    files=sorted(Path(a.parts).rglob("p24-core-*.json"))
    if len(files)!=8:raise SystemExit(f"P24_PART_COUNT {len(files)}/8")
    by={};allc=[];seen=set();audits={};template=None
    for p in files:
        x=json.loads(p.read_text())
        if x.get("scientific_stage")!="C3X 0.7.0-G9.4-P24" or x.get("compiler_version")!=VERSION or x.get("schema")!=PART:raise SystemExit("P24_PART_AUTHORITY")
        if x.get("cross_engine_outcomes_consulted") is not False:raise SystemExit("P24_OUTCOME_LEAK")
        cs=x["candidates"];mats={c["material_seed_name"] for c in cs};m=next(iter(mats)) if len(mats)==1 else None
        if m is None or m in by:raise SystemExit("P24_PART_MATERIAL")
        sides=Counter(c["side_to_move"] for c in cs)
        if len(cs)!=48 or sides!=Counter({"WHITE":24,"BLACK":24}):raise SystemExit("P24_PART_CONSTITUTION "+str(m))
        if any(int(c["generation_index"])<OFFSET for c in cs) or any(c["candidate_sha256"] in seen for c in cs):raise SystemExit("P24_FRESHNESS")
        seen.update(c["candidate_sha256"] for c in cs);by[m]=x;allc.extend(cs);audits[m]=x["audit_by_vertex"][m];template=template or x
    if set(by)!=set(FAMILIES):raise SystemExit("P24_MATERIAL_SET")
    out={"schema":"c3x-p24-core-pool-v1","scientific_stage":"C3X 0.7.0-G9.4-P24","lane":"PAWNLESS_CORE","compiler_version":VERSION,"engine_outcomes_consulted":False,"freshness":{"generation_index_offset":OFFSET,"p20_cells_reused":False,"p21_cells_reused":False,"p22_cells_reused":False,"p23_cells_reused":False},"constitution":dict(template["constitution"],worlds_per_vertex=48,worlds_per_side_per_vertex=24),"squares":template["squares"],"world_authority":template["world_authority"],"component_pool_sha256":{m:by[m]["pool_sha256"] for m in FAMILIES},"audit_by_vertex":audits,"candidates":allc}
    out["pool_sha256"]=hashlib.sha256(canon(out)).hexdigest()
    if len(allc)!=384:raise SystemExit("P24_TOTAL")
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P24_POOL_PASS",len(allc),out["pool_sha256"])

if __name__=="__main__":main()
