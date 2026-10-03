#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

PAIRS=(("berserk","ethereal"),("berserk","stockfish_19"),("ethereal","stockfish_19"))
MAPS={
 ("berserk","ethereal"):{s:s for s in ("00","01","10","11")},
 ("berserk","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
 ("ethereal","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
}
EDITS=("TARGET","SUBSET","SHAM")

def load(p):return json.loads(Path(p).read_text())
def collect(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")=="c3x-g10-p10-opportunity-world-v1":out.append(x)
 return out
def vec(chain,board):
 s=set(chain["board_topology"][board]["available_bounds"])
 return "".join("1" if q in s else "0" for q in ("UPPER","LOWER"))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--worlds",required=True)
 ap.add_argument("--search-gate",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 gate=load(a.search_gate)
 if gate.get("verdict")!="PASS_BALANCED_SEARCH_STATE_POSITIVITY_REPLAY_FROZEN":raise SystemExit("P14_STAGE_B_NOT_PASS")
 alloc=set(gate["stage_c_position_ids"])
 ctx={r["position_id"]:r["context"] for r in gate["stage_c_allocation_rows"]}
 worlds=[w for w in collect(a.worlds) if w.get("active") and w.get("position_id") in alloc]
 bypos=defaultdict(dict)
 for w in worlds:bypos[w["position_id"]][w["engine"]]=w
 rows=[]
 for pid,engs in sorted(bypos.items()):
  for e1,e2 in PAIRS:
   if e1 not in engs or e2 not in engs:continue
   c1={x["chain_id"]:x for x in engs[e1].get("chains",[])}
   c2={x["chain_id"]:x for x in engs[e2].get("chains",[])}
   for cid in sorted(set(c1)&set(c2)):
    a1,b1=c1[cid],c2[cid];m=MAPS[(e1,e2)]
    for edit in EDITS:
     l=(m[vec(a1,"B0")],m[vec(a1,edit)])
     r=(vec(b1,"B0"),vec(b1,edit))
     rows.append({
      "position_id":pid,"source_id":engs[e1]["source_id"],"context":ctx[pid],
      "engine_pair":f"{e1}|{e2}","chain_id":cid,"edit":edit,
      "left_edge":">".join(l),"right_edge":">".join(r),"defect":int(l!=r)
     })
 cells=defaultdict(list)
 for r in rows:
  c=r["context"];key=(c["phase"],c["branching"],c["tactical_surface"],r["engine_pair"],r["edit"])
  cells[key].append(r)
 summary=[]
 for k,rs in sorted(cells.items()):
  src=sorted({r["source_id"] for r in rs})
  summary.append({
   "phase":k[0],"branching":k[1],"tactical_surface":k[2],"engine_pair":k[3],"edit":k[4],
   "rows":len(rs),"sources":src,"source_count":len(src),
   "defects":sum(r["defect"] for r in rs),"defect_rate":sum(r["defect"] for r in rs)/len(rs),
   "all_source_defect":all(any(x["defect"] for x in rs if x["source_id"]==s) for s in src)
  })
 out={"schema":"c3x-g10-p14-balanced-defect-table-v1","status":"STAGE_C_MEASUREMENT_ONLY",
      "allocation_positions":len(alloc),"opportunity_worlds":len(worlds),"row_count":len(rows),
      "rows":rows,"cell_summary":summary,"p11_semantic_maps_refit":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G10_P14_DEFECT_TABLE","positions",len(alloc),"worlds",len(worlds),"rows",len(rows))
 print("CELLS",len(summary),"MULTISOURCE",sum(x["source_count"]>=3 for x in summary))
if __name__=="__main__":main()
