#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--chain-freeze",required=True)
 ap.add_argument("--search-gate",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 cf=load(a.chain_freeze);g=load(a.search_gate)
 if g.get("verdict")!="PASS_BALANCED_SEARCH_STATE_POSITIVITY_REPLAY_FROZEN":raise SystemExit("P14_STAGE_B_NOT_PASS")
 ids=set(g["stage_c_position_ids"])
 out=dict(cf)
 out["cases"]=[c for c in cf["cases"] if c["position_id"] in ids]
 if "positions" in cf:out["positions"]={k:v for k,v in cf["positions"].items() if k in ids}
 if "selected_chains" in cf:out["selected_chains"]={k:v for k,v in cf["selected_chains"].items() if k in ids}
 out["p14_stage_c_allocation"]=sorted(ids)
 out["p14_parent_chain_freeze_receipt_sha256"]=cf.get("receipt_sha256")
 seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G10_P14_FILTER_PASS","positions",len(ids),"cases",len(out["cases"]))
if __name__=="__main__":main()
