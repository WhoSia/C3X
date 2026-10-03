#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 import hashlib
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--balanced-corpus",required=True)
 ap.add_argument("--p16-constitution",required=True)
 ap.add_argument("--build-dir",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 corp=load(a.balanced_corpus)
 if corp.get("verdict")!="PASS_BALANCED_CHESS_ECOLOGY_POSITIVITY":raise SystemExit("P14_ECOLOGY_NOT_PASS")
 p16=load(a.p16_constitution)
 if p16.get("schema")!="c3x-g95-p16-constitution-v1":raise SystemExit("P14_P16_CONSTITUTION")
 import sys
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
 import p32_event_court as p32
 engines=("stockfish_19","berserk","ethereal")
 variants={}
 for e in engines:
  xs=list(Path(a.build_dir).rglob(f"c3x-p16-{e}"))
  if len(xs)!=1:raise SystemExit(f"P14_BUILD_{e}_{len(xs)}")
  xs[0].chmod(0o755);variants[e]={"sha256":sha_file(xs[0]),"protocol":p32.protocol_for(e)}
 positions=[]
 for z in corp["positions"]:
  pid=f"p14:{z['source_id']}:{z['trajectory_hash'][:12]}"
  positions.append({
   "position_id":pid,"trajectory_id":f"p14:traj:{z['source_id']}:{z['trajectory_hash'][:12]}",
   "source_id":z["source_id"],"source_ply":z["ply"],"candidate_sha256":z["candidate_sha256"],
   "complexity":{"legal_move_count":z["legal_move_count"],"balanced_context":z["cell"],"side_to_move":z["side_to_move"]},
   "cell":{"fen":z["fen"],"history":{"decoys":[]}},
   "p14_context":z["cell"],"family":"MOVE_ORDER","frontier":8
  })
 cases=[]
 for pos in positions:
  for e in engines:
   cases.append({"case_id":f"p14:{e}:{pos['position_id']}","engine":e,"position_id":pos["position_id"],
    "source_id":pos["source_id"],"source_ply":pos["source_ply"],"candidate_sha256":pos["candidate_sha256"],
    "complexity":pos["complexity"],"cell":pos["cell"],"p14_context":pos["p14_context"]})
 out={
  "schema":"c3x-g95-p16-design-precommit-v1","scientific_stage":"C3X 0.8.0-G10-P14",
  "intervention_outcomes_consulted":False,"p14_balanced_corpus_sha256":digest(corp),
  "variants":variants,"execution":p16["execution"],"unordered_pair_constitution":p16["unordered_pair_constitution"],
  "board_intervention_family":p16["board_intervention_family"],"relation_atoms":p16["relation_atoms"],
  "chain_constitution":p16["chain_constitution"],"exact_event_mediator":p16["exact_event_mediator"],
  "bridge_definitions":p16["bridge_definitions"],"structural_equivalence":p16["structural_equivalence"],
  "support_gate":p16["support_gate"],"certificate":p16["certificate"],"claim_ceiling":p16["claim_ceiling"],
  "p14_context_balanced":True,"positions":positions,"cases":cases
 }
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G10_P14_DESIGN_PASS","positions",len(positions),"cases",len(cases),out["receipt_sha256"])
if __name__=="__main__":main()
