from __future__ import annotations
import itertools,json,math
from copy import deepcopy
from typing import Any
from c3x_g10.morphism_grammar import development_adjudication

ENDPOINTS=("A_FROM","A_TO","B_FROM","B_TO")
GRAMMAR=("C","S","E")

def _canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def edges(before,after):
 out=[]
 for i,(x,y) in enumerate(zip(before,after)):
  if x==y:continue
  out.append((ENDPOINTS[i],"GAIN" if (not x and y) else "LOSS"))
 return tuple(sorted(out))
def role_from_target(t):
 side=t["fen"].split()[1];own=("WHITE" if side=="w" else "BLACK")
 return "OWN" if t["piece_color"]==own else "OPPONENT"
def trigger_from_chain(ch):
 t=ch["target"];return {"role":role_from_target(t),"delta_edges":edges(t["relation_before"],t["relation_after"])}
def trigger_from_cert(c):
 b=c["board_trigger"];return {"role":b["moved_side_role"],"delta_edges":edges(b["relation_before"],b["relation_after"])}
def _map_endpoint(ep,g):
 cand,where=ep.split("_",1)
 if g=="C":cand="B" if cand=="A" else "A"
 if g=="E":where="TO" if where=="FROM" else "FROM"
 return cand+"_"+where
def transform_trigger(t,gens):
 role=t["role"];es=[list(x) for x in t["delta_edges"]]
 for g in gens:
  if g=="S":role="OPPONENT" if role=="OWN" else "OWN"
  elif g in ("C","E"):
   for e in es:e[0]=_map_endpoint(e[0],g)
  else:raise ValueError(g)
 return {"role":role,"delta_edges":tuple(sorted(tuple(x) for x in es))}
def orbit_keys(t):
 return {_canon(transform_trigger(t,subset)) for r in range(len(GRAMMAR)+1) for subset in itertools.combinations(GRAMMAR,r)}
def nontrivial_orbit_prototypes(ecology):
 d=development_adjudication(ecology);ids={c["id"]:c for c in ecology["certificates"]};out={}
 for i,part in enumerate(d["orbit_partition"]):
  if len(part)<2:continue
  keys=set()
  for cid in part:keys|=orbit_keys(trigger_from_cert(ids[cid]))
  out[f"orbit-{i}"]={"members":part,"trigger_keys":sorted(keys)}
 return out
def gap_bucket(x):
 if x is None:return 9
 if x<=5:return 0
 if x<=10:return 1
 if x<=20:return 2
 return 3
def position_features(p):
 active=sum(1 for v in p["engine_views"].values() if v.get("active"))
 ply=int(p.get("source_ply") or 0)
 chains=len(p.get("chain_candidates",[]))
 return {
  "active_engines":active,
  "ply_bucket":max(0,min(3,(ply-14)//4)),
  "pair_support":int((p.get("pair") or {}).get("support_count") or 0),
  "chain_bucket":min(chains,3),
  "gap_bucket":gap_bucket((p.get("pair") or {}).get("median_gap_cp")),
 }
def target_hits(p,prototypes):
 hits={}
 for ch in p.get("chain_candidates",[]):
  keyset=orbit_keys(trigger_from_chain(ch))
  for oid,o in prototypes.items():
   if keyset & set(o["trigger_keys"]):
    hits.setdefault(oid,[]).append(ch["chain_id"])
 return hits
def distance(a,b):
 fa,fb=position_features(a),position_features(b)
 return (abs(fa["active_engines"]-fb["active_engines"])*4+
         abs(fa["ply_bucket"]-fb["ply_bucket"])*2+
         abs(fa["pair_support"]-fb["pair_support"])*3+
         abs(fa["chain_bucket"]-fb["chain_bucket"])+
         abs(fa["gap_bucket"]-fb["gap_bucket"]))
def select(pair_freezes,ecology,max_target_per_source=12,min_target_per_source=6):
 prototypes=nontrivial_orbit_prototypes(ecology);positions={};cases=[];template=None
 for pf in pair_freezes:
  if template is None:template=pf
  positions.update(pf["positions"]);cases.extend(pf["cases"])
 bysource={}
 for pid,p in positions.items():bysource.setdefault(p["source_id"],[]).append((pid,p))
 assignments=[];selected_ids=set();support=True;source_stats={}
 for source,rows in sorted(bysource.items()):
  eligible=[(pid,p,target_hits(p,prototypes)) for pid,p in rows if p.get("admitted") and p.get("chain_candidates")]
  target_all=[x for x in eligible if x[2]]
  controls=[(pid,p) for pid,p,h in eligible if not h]
  target_all.sort(key=lambda x:(-len(x[2]),-sum(len(v) for v in x[2].values()),x[1]["candidate_sha256"],x[0]))
  targets=target_all[:max_target_per_source];used=set();source_assignments=[]
  for pid,p,h in targets:
   available=[x for x in controls if x[0] not in used]
   if not available:break
   cid,cp=min(available,key=lambda x:(distance(p,x[1]),x[1]["candidate_sha256"],x[0]))
   used.add(cid);selected_ids|={pid,cid}
   rec={"source_id":source,"target_position_id":pid,"control_position_id":cid,"target_hits":h,
    "target_features":position_features(p),"control_features":position_features(cp),"match_distance":distance(p,cp)}
   assignments.append(rec);source_assignments.append(rec)
  source_stats[source]={"chain_eligible_positions":len(eligible),"target_eligible_positions":len(target_all),
    "control_eligible_positions":len(controls),"requested_targets":len(targets),"matched_pairs":len(source_assignments)}
  if len(source_assignments)<min_target_per_source:support=False
 selected_positions={pid:deepcopy(positions[pid]) for pid in sorted(selected_ids)}
 arm={}
 for a in assignments:
  arm[a["target_position_id"]]="TARGET";arm[a["control_position_id"]]="CONTROL"
 for pid,p in selected_positions.items():p["p8_arm"]=arm[pid]
 selected_cases=[]
 for c in cases:
  if c["position_id"] in selected_ids:
   z=deepcopy(c);z["position_pair"]=selected_positions[c["position_id"]];z["p8_arm"]=arm[c["position_id"]];selected_cases.append(z)
 out={k:deepcopy(template[k]) for k in ("schema","scientific_stage","execution","chain_constitution","exact_event_mediator","bridge_definitions","structural_equivalence","support_gate","certificate","claim_ceiling","variants")}
 out.update({"design_receipt_sha256":"P8_MULTI_BATCH_PREOUTCOME_SELECTION","intervention_outcomes_consulted":False,
  "admitted_pair_positions":sum(p.get("admitted",False) for p in selected_positions.values()),
  "active_engine_worlds":sum(1 for c in selected_cases if c["engine_view"].get("active")),
  "positions_with_chain_candidates":sum(bool(p.get("chain_candidates")) for p in selected_positions.values()),
  "positions":selected_positions,"cases":selected_cases})
 receipt={"schema":"c3x-g10-p8-acquisition-freeze-v1","support_pass":support,"prototypes":prototypes,
  "assignments":assignments,"target_count":sum(1 for v in arm.values() if v=="TARGET"),"control_count":sum(1 for v in arm.values() if v=="CONTROL"),
  "source_stats":source_stats,"target_eligible_count":sum(x["target_eligible_positions"] for x in source_stats.values()),
  "control_eligible_count":sum(x["control_eligible_positions"] for x in source_stats.values()),
  "sources":sorted(bysource),"features_used":["active_engines","ply_bucket","pair_support","chain_bucket","gap_bucket"],
  "forbidden_outcomes_consulted":[],"chain_qualification_opened":False,"factorial_outcomes_opened":False,"certificate_outcomes_opened":False,
  "p7_grammar":["C","S","E"],"unlicensed_generators":["G","U"]}
 return out,receipt
