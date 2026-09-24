#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

SETS={
 "core":(
   ("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN"),
   "c3x-p21-core-v1","c3x-p21-core-part-v1","p21-core-*.json",140000,"PAWNLESS_CORE"
 ),
 "carrier":(
   ("KQQPvKQP","KQRPvKQP","KQQPvKRP","KQRPvKRP","KRBPvKBP","KRNPvKBP","KRBPvKNP","KRNPvKNP"),
   "c3x-p21-pawn-carrier-v1","c3x-p21-pawn-carrier-part-v1","p21-carrier-*.json",180000,"PAWN_CARRIER"
 )
}

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--lane",choices=SETS,required=True);ap.add_argument("--parts",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 expected,version,schema,pat,offset,lane=SETS[a.lane]
 files=sorted(Path(a.parts).rglob(pat))
 if len(files)!=8:raise SystemExit(f"P21_PART_COUNT {a.lane} {len(files)}/8")
 by={};allc=[];seen=set();audits={};template=None
 for p in files:
  x=json.loads(p.read_text())
  if x.get("scientific_stage")!="C3X 0.7.0-G9.4-P21":raise SystemExit("P21_STAGE_MISMATCH")
  if x.get("compiler_version")!=version or x.get("schema")!=schema:raise SystemExit("P21_SCHEMA_VERSION_MISMATCH")
  leak=x.get("engine_outcomes_consulted",x.get("stockfish_outcomes_consulted"))
  if leak is not False:raise SystemExit("P21_OUTCOME_LEAK")
  cs=x["candidates"];mats={c["material_seed_name"] for c in cs}
  if len(mats)!=1:raise SystemExit("P21_PART_MATERIAL_SET")
  m=next(iter(mats))
  if m in by:raise SystemExit("P21_PART_DUP "+m)
  sides=Counter(c["side_to_move"] for c in cs)
  if len(cs)!=48 or sides!=Counter({"WHITE":24,"BLACK":24}):raise SystemExit(f"P21_PART_CONSTITUTION {m} {len(cs)} {dict(sides)}")
  if any(int(c["generation_index"])<offset for c in cs):raise SystemExit("P21_OFFSET_FAIL "+m)
  for c in cs:
   z=c["candidate_sha256"]
   if z in seen:raise SystemExit("P21_CANDIDATE_DUP "+z)
   seen.add(z)
  by[m]=x;allc.extend(cs);audits[m]=x["audit_by_vertex"][m]
  if template is None:template=x
 if set(by)!=set(expected):raise SystemExit("P21_MATERIAL_SET")
 out={
  "schema":f"c3x-p21-{a.lane}-pool-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P21",
  "lane":lane,
  "compiler_version":version,
  "engine_outcomes_consulted":False,
  "freshness":{"generation_index_offset":offset,"p20_cells_reused":False},
  "constitution":dict(template["constitution"],worlds_per_vertex=48,worlds_per_side_per_vertex=24),
  "squares":template["squares"],
  "world_authority":template["world_authority"],
  "component_pool_sha256":{m:by[m]["pool_sha256"] for m in expected},
  "audit_by_vertex":audits,
  "candidates":allc
 }
 out["pool_sha256"]=hashlib.sha256(canon(out)).hexdigest()
 if len(allc)!=384:raise SystemExit(f"P21_TOTAL {len(allc)}/384")
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_POOL_PASS",a.lane,len(allc),out["pool_sha256"])

if __name__=="__main__":main()
