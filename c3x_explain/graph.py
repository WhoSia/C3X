from __future__ import annotations
from typing import Any

def assemble_typed_graph(moment:dict[str,Any])->dict[str,Any]:
    atoms=moment.get("atoms",[])
    nodes=[];edges=[]
    move_id=f"ply:{moment['ply']}:move"
    nodes.append({"node_id":move_id,"node_type":"played_move","payload":{"uci":moment["played_uci"],"san":moment["played_san"]}})
    for a in atoms:
        aid=a.get("atom_id")
        if not aid:continue
        nodes.append({"node_id":aid,"node_type":"evidence_atom","payload":{"type":a.get("type"),
                     "provenance":a.get("provenance"),"authority":a.get("authority"),"claim":a.get("claim")}})
        edges.append({"from":aid,"to":move_id,"relation":"supports_commentary_about"})
        claim=a.get("claim") or {}
        for key in ("source_id","certificate_id"):
            if claim.get(key):
                pid=f"{key}:{claim[key]}"
                nodes.append({"node_id":pid,"node_type":"provenance_object","payload":{key:claim[key]}})
                edges.append({"from":pid,"to":aid,"relation":"provenance_for"})
    uniq={n["node_id"]:n for n in nodes}
    return {"schema":"c3x-typed-explanation-subgraph-v1","nodes":list(uniq.values()),"edges":edges,
            "root":move_id,"authority":"graph_structure_does_not_upgrade_evidence"}

def attach_graphs(moments:list[dict[str,Any]])->None:
    for m in moments:m["typed_graph"]=assemble_typed_graph(m)
