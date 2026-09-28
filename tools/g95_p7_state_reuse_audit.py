#!/usr/bin/env python3
"""Target-blind CSEG reuse audit for C3X G9.5-P7.

Reads profile artifacts only. Never reads ROOT_CHANGE targets and cannot modify
or select a causal field. Intended to distinguish reusable search states from
episode fingerprints before causal labels are considered.
"""
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

QLEVELS=("Q0","Q1","Q2","Q3")

def load(p):return json.loads(Path(p).read_text())

def key_board(r):return tuple(sorted((r.get("board_atoms") or {}).items()))
def key_current(r):
 c=r.get("current_event") or {}
 return tuple((k,c.get(k)) for k in ("scope","class","ply","depth","bound","window_relation","move_presence"))
def key_census(r):
 c=r.get("graph_census") or {}
 return (c.get("nodes"),c.get("edges"),c.get("prefix_events"))

def stats(rows,keyfn):
 g=defaultdict(list)
 for r in rows:g[keyfn(r)].append(r)
 reused=[v for v in g.values() if len(v)>1]
 return {
  "records":len(rows),
  "distinct":len(g),
  "compression":0.0 if not rows else 1-len(g)/len(rows),
  "reused_states":len(reused),
  "reused_records":sum(map(len,reused)),
  "max_support":max((len(v) for v in g.values()),default=0),
  "cross_engine_records":sum(len(v) for v in g.values() if len({x.get("engine") for x in v})>1),
  "cross_position_records":sum(len(v) for v in g.values() if len({x.get("position_id") for x in v})>1),
  "cross_source_records":sum(len(v) for v in g.values() if len({x.get("source_stratum") for x in v})>1)
 }

def main():
 ap=argparse.ArgumentParser(description="Audit target-blind P7 search-state reuse.")
 ap.add_argument("--profile",action="append",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 rows=[];roles=Counter()
 for p in a.profile:
  x=load(p)
  if x.get("schema") not in ("c3x-cseg-profile-batch-p7-v1","c3x-cseg-profile-merged-p7-v1"):
   raise SystemExit("P7_REUSE_AUDIT_PROFILE_SCHEMA")
  if x.get("target_fields_consulted") is not False:raise SystemExit("P7_REUSE_AUDIT_TARGET_FIREWALL")
  if x.get("raw_tt_key_emitted") is not False or x.get("counterfactual_information_consulted") is not False or x.get("fiber_id_consulted") is not False:
   raise SystemExit("P7_REUSE_AUDIT_PROFILE_FIREWALL")
  roles[x.get("role")]+=len(x.get("records",[]));rows.extend(x.get("records",[]))
 q={}
 for level in QLEVELS:q[level]=stats(rows,lambda r,l=level:r["state_ids"][l])
 decompositions={
  "graph_census":stats(rows,key_census),
  "board_atoms":stats(rows,key_board),
  "current_event":stats(rows,key_current),
  "board_plus_current":stats(rows,lambda r:(key_board(r),key_current(r))),
  "census_plus_current":stats(rows,lambda r:(key_census(r),key_current(r))),
  "board_plus_census":stats(rows,lambda r:(key_board(r),key_census(r)))
 }
 out={
  "schema":"c3x-g95-p7-target-blind-state-reuse-audit-v1",
  "scientific_stage":"C3X 0.7.0-G9.5-P7",
  "authority":"TARGET_BLIND_ENGINEERING_DIAGNOSTIC_ONLY",
  "target_fields_consulted":False,
  "may_select_or_modify_field":False,
  "may_expand_public_authority":False,
  "records":len(rows),
  "roles":dict(roles),
  "q_level_reuse":q,
  "decomposition":decompositions,
  "diagnostic_flags":{
   "all_observed_q_levels_zero_compression":all(abs(q[x]["compression"])<1e-15 for x in QLEVELS),
   "all_observed_q_levels_zero_reuse":all(q[x]["reused_records"]==0 for x in QLEVELS),
   "graph_census_near_identifier":decompositions["graph_census"]["distinct"]>=max(0,len(rows)-1),
   "board_plus_census_identifier":decompositions["board_plus_census"]["distinct"]==len(rows)
  },
  "interpretation_boundary":"This audit can diagnose fingerprint-like state construction before targets are opened. It cannot determine label consistency, causal sufficiency, train admissibility, selection stability or transport."
 }
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P7_TARGET_BLIND_REUSE_AUDIT",len(rows),q["Q0"]["distinct"],q["Q3"]["distinct"],out["diagnostic_flags"])

if __name__=="__main__":main()
