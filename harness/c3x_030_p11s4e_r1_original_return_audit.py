#!/usr/bin/env python3
"""C3X 0.30 P11/S4E-R1: SHA-locked genuine native invocation edge audit.

Proves a limited *observed arithmetic return-edge*: for each selected event
node with a real TT-probe and normal return of exactly the same native
invocation ID, then a root candidate event with parent invocation id and
child_last identifier, real source-event order probe<return<root, root_value
must equal NEGATED child return as required by Stockfish negamax.

NOT a causal TT-probe effect: no intervention here, even if the trace
establishes literal numeric propagation of an observed child return.
No complete search tree, due to capped logging and early return paths.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

ORIGINAL_SHA="36f2087fc522e5f223ce6ea0072815b8501327e9192dcbc3529a1aae6aac2e4d"
INPUT_SCHEMA="c3x030-p11s4e-native-invocation-parent-trace-v1"
OUTPUT_SCHEMA="c3x030-p11s4e-r1-sha-verified-invocation-value-edge-v1"

def sha(data):return hashlib.sha256(data).hexdigest()

def exact_edges(events):
    probes={};returns={};edges=[];root_count=0
    for index,e in enumerate(events):
        kind=e.get("kind");id=e.get("id")
        if kind=="probe":
            if id in probes:raise ValueError("S4ER1_HOLD_DUPLICATE_PROBE_ID")
            probes[id]=(index,e)
        elif kind=="normal_return":
            if id in returns:raise ValueError("S4ER1_HOLD_DUPLICATE_RETURN_ID")
            returns[id]=(index,e)
        elif kind=="root_candidate":
            root_count+=1
            cid=e.get("child_last")
            if cid not in probes or cid not in returns:continue
            pi,p=probes[cid];ri,r=returns[cid]
            if not (pi<ri<index):raise ValueError("S4ER1_HOLD_TEMPORAL_CAUSAL_ORDER")
            if p.get("parent")!=r.get("parent") or r["parent"]!=id:
                raise ValueError("S4ER1_HOLD_PARENT_INVOCATION_MISMATCH")
            if p.get("hit")!="1" or p.get("ply")!="1":
                raise ValueError("S4ER1_HOLD_NOT_REAL_TT_HIT")
            try:
                child_value=int(r["value"]);root_value=int(e["value"])
            except (ValueError,TypeError,KeyError) as exc:
                raise ValueError("S4ER1_HOLD_SOURCE_VALUE_NOT_INTEGER") from exc
            if root_value!=-child_value:
                raise ValueError("S4ER1_HOLD_NEGAMAX_CHILD_ROOT_VALUE_DISAGREEMENT")
            edges.append({"child_invocation":cid,"parent_root_invocation":id,
                          "source_event_orders":{"probe":pi,"child_return":ri,"root_candidate":index},
                          "chess_position_key":p["key"],
                          "parent_raw_move_code_unverified":None,
                          "child_return_value":child_value,"root_candidate_value":root_value,
                          "arithmetically_negated_return_observed":True,
                          "TT_hit_caused_return_value":False})
    return {"candidate_root_events_logged":root_count,
            "root_edges_with_same_id_parent_time_and_negated_value":len(edges),
            "edges":edges,
            "bounded_trace_is_not_full_tree":True,
            "physical_intervention_in_this_evidence":False,
            "no_statement_about_TT_only_causation":True}

def audit(data):
    if (data.get("schema")!=INPUT_SCHEMA or data.get("status")!="PASS_INCOMPLETE_INVOCATION_TRACE"
        or data.get("native_searches")!=12 or data.get("not_independent_cohort") is not True
        or data.get("causal_return_to_root_proven") is not False or
        data.get("noninterference_pass") is not True):
        raise ValueError("S4ER1_HOLD_UNSEALED_OR_INVALID_NATIVE_SOURCE")
    if len(data.get("positions",{}))!=3:raise ValueError("S4ER1_HOLD_UNEXPECTED_POSITION_COUNT")
    results={}
    for id,packet in sorted(data["positions"].items()):
        if packet.get("noninterference") is not True:
            raise ValueError("S4ER1_HOLD_SOURCE_NONINTERFERENCE")
        results[id]=exact_edges(packet["events"])
    return {"schema":OUTPUT_SCHEMA,"original_S4E_native_json_sha256":ORIGINAL_SHA,
            "real_native_searches_inherited":data["native_searches"],
            "new_native_searches":0,
            "actual_inherited_native_nodes":data["actual_native_nodes"],
            "verified_observed_edges_per_position":{k:v["root_edges_with_same_id_parent_time_and_negated_value"]
                for k,v in results.items()},
            "verified_observed_edges_total":sum(v["root_edges_with_same_id_parent_time_and_negated_value"]
                for v in results.values()),
            "per_position":results,
            "full_TT_to_root_causal_mediation_proven":False,
            "individual_TT_entry_causal_proven":False,
            "heldout_confirmation_proven":False,
            "result_scope":"observed negamax child-return-to-root-candidate equality within same invocation for limited logged paths"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--original",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    raw=Path(args.original).read_bytes()
    if sha(raw)!=ORIGINAL_SHA:raise ValueError("S4ER1_HOLD_RAW_ORIGINAL_SHA256")
    result=audit(json.loads(raw))
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("S4ER1_REAL_ORIGINAL_NEGAMAX_RETURN_EDGE_PASS",result["verified_observed_edges_total"],
          result["verified_observed_edges_per_position"],"JSON_SHA",sha(dest.read_bytes()))
if __name__=="__main__":main()
