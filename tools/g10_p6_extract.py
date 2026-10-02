from __future__ import annotations
import argparse,json,glob
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def norm_move(move,a,b):
    if move is None: return None
    if move==a: return "A"
    if move==b: return "B"
    return "OTHER"

def find_world(worlds_dir,position_id,engine):
    for p in glob.glob(str(Path(worlds_dir)/"**/*.json"),recursive=True):
        try:x=load(p)
        except Exception:continue
        if x.get("position_id")==position_id and x.get("engine")==engine:
            return x
    raise KeyError((position_id,engine))

def find_chain(obj,chain_id):
    for ch in obj.get("chains",[]):
        if ch.get("chain_id")==chain_id:return ch
    raise KeyError(chain_id)

def bridge_record(adjud,cert):
    for r in adjud.get("bridge_records",[]):
        if r.get("position_id")==cert["position_id"] and r.get("engine")==cert["engine"] and r.get("exact_signature")==cert["structural_signature"]:
            return r
    raise KeyError(cert["certificate_id"])

def main():
    ap=argparse.ArgumentParser()
    for x in ["fresh","chain_freeze","worlds","out"]:ap.add_argument("--"+x,required=True)
    a=ap.parse_args()
    fresh=load(a.fresh);freeze=load(a.chain_freeze)
    positions=freeze["positions"];out=[]
    for cert in fresh.get("causal_explanation_certificates",[]):
        pos=positions[cert["position_id"]]
        chain=next(x for x in pos["chain_candidates"] if x["chain_id"]==cert["chain_id"])
        world=find_world(a.worlds,cert["position_id"],cert["engine"])
        wchain=find_chain(world,cert["chain_id"])
        A=pos["pair"]["A"]["uci"];B=pos["pair"]["B"]["uci"];bound=cert["bound"]
        topology={}
        for board in ("B0","TARGET","SUBSET","SHAM"):
            cell=wchain["boards"][board]["bounds"][bound]
            rec=cell.get("record")
            topology[board]={
              "state":cell["state"],
              "native":norm_move(rec and rec["native"]["bestmove"],A,B),
              "t_only":norm_move(rec and rec["t_only"]["bestmove"],A,B),
            }
        br=bridge_record(fresh,cert)
        orig=norm_move(br["original_native"],A,B);edit=norm_move(br["edited_native"],A,B)
        out.append({
          "id":"HOLDOUT_"+cert["certificate_id"],
          "certificate_id":cert["certificate_id"],
          "source_id":cert["source_id"],"position_id":cert["position_id"],"engine":cert["engine"],"bound":cert["bound"],
          "exact_signature":cert["structural_signature"],
          "context":{"pair_id":cert["pair_id"],"physical_edit_id":cert["physical_edit_id"]},
          "board_trigger":{
            "moved_side_role":cert["moved_side_role"],
            "target_atom":chain["target"]["atoms"][0] if chain["target"]["atoms"] else None,
            "relation_before":chain["target"]["relation_before"],
            "relation_after":chain["target"]["relation_after"],
          },
          "response_topology":topology,
          "falsifier":{"subset_reproduced":cert["subset_reproduced"],"sham_reproduced":cert["sham_reproduced"],"chain_relative_minimality":True},
          "surface":{"board_native_transition":f"{orig}_TO_{edit}"},
        })
    result={
      "schema":"c3x-g10-p6-holdout-normalized-certificates-v1",
      "fresh_instrument_verdict":fresh["verdict"],
      "support":fresh["support"],
      "certificates":out,
      "mapping_refit_after_outcome":False,
    }
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("G10_P6_HOLDOUT_NORMALIZED",len(out),fresh["verdict"])
if __name__=="__main__":main()
