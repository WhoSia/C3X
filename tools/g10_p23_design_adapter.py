#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
def load(p):return json.loads(Path(p).read_text())
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--projected",required=True);ap.add_argument("--legacy-p16-constitution",required=True);ap.add_argument("--build-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 corp=load(a.projected);old=load(a.legacy_p16_constitution)
 if corp.get("verdict")!="PASS_P23_ROUTER_PROJECTION":raise SystemExit("P23_PROJECT_NOT_PASS")
 if old.get("schema")!="c3x-g95-p16-constitution-v1":raise SystemExit("P23_P16_CONST")
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"));import p32_event_court as p32
 engines=("stockfish_19","berserk","ethereal");variants={}
 for e in engines:
  xs=list(Path(a.build_dir).rglob(f"c3x-p16-{e}"))
  if len(xs)!=1:raise SystemExit(f"P23_BUILD_{e}_{len(xs)}")
  xs[0].chmod(0o755);variants[e]={"sha256":sha_file(xs[0]),"protocol":p32.protocol_for(e)}
 positions=[]
 for z in corp["positions"]:
  pid=f"p23:{z['source_id']}:{z['trajectory_hash'][:12]}"
  positions.append({"position_id":pid,"trajectory_id":f"p23:traj:{z['source_id']}:{z['trajectory_hash'][:12]}","source_id":z["source_id"],
    "source_rank":z["source_rank"],"source_order":z["source_order"],"source_ply":z["ply"],"candidate_sha256":z["candidate_sha256"],
    "complexity":{"legal_move_count":z["legal_move_count"],"routed_context":z["context"],"router_grammar":z["router_grammar"]},
    "cell":{"fen":z["fen"],"history":{"decoys":[]}},"p16_context":z["context"],"router_grammar":z["router_grammar"],"family":"MOVE_ORDER","frontier":8})
 cases=[{"case_id":f"p23:{e}:{p['position_id']}","engine":e,**p} for p in positions for e in engines]
 out={"schema":"c3x-g95-p16-design-precommit-v1","scientific_stage":"C3X 0.10.0-G10-P23","intervention_outcomes_consulted":False,
      "activation_predictions_consulted":False,"variants":variants,"execution":old["execution"],"unordered_pair_constitution":old["unordered_pair_constitution"],
      "board_intervention_family":old["board_intervention_family"],"relation_atoms":old["relation_atoms"],"chain_constitution":old["chain_constitution"],
      "exact_event_mediator":old["exact_event_mediator"],"bridge_definitions":old["bridge_definitions"],"structural_equivalence":old["structural_equivalence"],
      "support_gate":old["support_gate"],"certificate":old["certificate"],"claim_ceiling":old["claim_ceiling"],"positions":positions,"cases":cases}
 out["receipt_sha256"]=hashlib.sha256(canon(out)).hexdigest();Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_DESIGN",len(positions),len(cases),out["receipt_sha256"])
if __name__=="__main__":main()
