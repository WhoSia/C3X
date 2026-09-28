#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import c3x_context_v3 as base

STAGE="C3X 0.7.0-G9.5-P6"
SCHEMA_VERSION="c3x-context-v4-relational"
CAUSAL_AVAILABILITY="STRICT_EVENT_PREFIX_ONLY"

def count_bucket(n):
 if n<=1:return "1"
 if n==2:return "2"
 if n<=4:return "3_4"
 return "5_PLUS"

def direction(a,b):
 if a is None or b is None:return "NONE"
 a=int(a);b=int(b)
 return "UP" if a>b else "DOWN" if a<b else "SAME"

def eq_pattern(vals):
 if len(vals)<3:return "SHORT"
 mp={};n=0;out=[]
 for v in vals[-3:]:
  if v not in mp:
   mp[v]=chr(ord("A")+n);n+=1
  out.append(mp[v])
 return "".join(out)

def diversity_bucket(xs):
 n=len(set(xs))
 if n<=1:return "1"
 if n==2:return "2"
 return "3_PLUS"

def move_flag(e):
 return "MOVE" if int(e.get("tt_move",0))!=0 else "NO_MOVE"

def relational_context(trace,event_ordinal):
 events=trace["events"];i=int(event_ordinal)
 if i<0 or i>=len(events):raise ValueError("event ordinal")
 e=events[i];prefix=events[:i+1];past=events[:i];prev=events[i-1] if i>0 else None
 key=e.get("key")
 if key is None:raise ValueError("missing parent-trace TT key")
 same_key=[z for z in past if z.get("key")==key]
 same_class=[z for z in past if z.get("class")==e.get("class")]
 pkey=same_key[-1] if same_key else None
 pclass=same_class[-1] if same_class else None

 key_classes=[str(z.get("class")) for z in same_key+[e]]
 key_scopes=[str(z.get("scope")) for z in same_key+[e]]
 key_seq=[z.get("key") for z in prefix]
 cls_seq=[str(z.get("class")) for z in prefix]
 last2_key_classes=[str(z.get("class")) for z in same_key[-2:]]+[str(e.get("class"))]
 last2_key_scopes=[str(z.get("scope")) for z in same_key[-2:]]+[str(e.get("scope"))]

 if not same_key:key_history="FIRST_KEY"
 elif all(z.get("class")==e.get("class") for z in same_key):key_history="REPEAT_KEY_SAME_CLASS"
 else:key_history="REPEAT_KEY_CROSS_CLASS"

 if not same_key:key_scope="FIRST_KEY"
 elif len(set(str(z.get("scope")) for z in same_key+[e]))==1:key_scope="SINGLE_SCOPE_LINEAGE"
 else:key_scope="MULTI_SCOPE_LINEAGE"

 if not same_class:same_class_key="FIRST_CLASS"
 else:same_class_key="SAME_KEY" if pclass.get("key")==key else "DIFF_KEY"

 if prev is None:
  imm_key="START";imm_class="START"
 else:
  imm_key="SAME_KEY" if prev.get("key")==key else "DIFF_KEY"
  imm_class="SAME_CLASS" if prev.get("class")==e.get("class") else "DIFF_CLASS"

 if pkey is None:move_transition="FIRST_KEY"
 else:move_transition=move_flag(pkey)+"_TO_"+move_flag(e)

 return {
  "rel_key_history_state":key_history,
  "rel_key_scope_state":key_scope,
  "rel_same_key_depth_direction":"FIRST_KEY" if pkey is None else direction(e.get("depth"),pkey.get("depth")),
  "rel_same_key_ply_direction":"FIRST_KEY" if pkey is None else direction(e.get("ply"),pkey.get("ply")),
  "rel_same_class_key_relation":same_class_key,
  "rel_immediate_key_relation":imm_key,
  "rel_immediate_class_relation":imm_class,
  "rel_triplet_key_pattern":eq_pattern(key_seq),
  "rel_triplet_class_pattern":eq_pattern(cls_seq),
  "rel_same_key_class_diversity":diversity_bucket(key_classes),
  "rel_same_key_scope_diversity":diversity_bucket(key_scopes),
  "rel_same_key_lineage_length":count_bucket(len(same_key)+1),
  "rel_same_class_lineage_length":count_bucket(len(same_class)+1),
  "rel_same_key_move_transition":move_transition,
  "rel_same_key_last2_class_pattern":eq_pattern(last2_key_classes),
  "rel_same_key_last2_scope_pattern":eq_pattern(last2_key_scopes)
 }

def build_context(fen,parent_trace,event_ordinal,descriptor):
 ctx,arch=base.build_context(fen,parent_trace,event_ordinal,descriptor)
 rel=relational_context(parent_trace,event_ordinal)
 return ctx,rel,arch

def main():
 ap=argparse.ArgumentParser(description="Materialize C3X G9.5-P6 strict-prefix relational representation atoms.")
 ap.add_argument("--fen",required=True);ap.add_argument("--parent-trace",required=True)
 ap.add_argument("--event-id",required=True);ap.add_argument("--fiber-id",required=True);ap.add_argument("--engine",required=True)
 ap.add_argument("--position-id",required=True);ap.add_argument("--architecture",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 tr=json.loads(Path(a.parent_trace).read_text());desc=json.loads(Path(a.architecture).read_text())
 hits=[(i,e) for i,e in enumerate(tr["events"]) if e["address_id"]==a.event_id]
 if len(hits)!=1:raise SystemExit(f"C3X_P6_REL_EVENT_MATCH {len(hits)}")
 i,_=hits[0];ctx,rel,arch=build_context(a.fen,tr,i,desc)
 z={"schema":"c3x-context-profile-v4-relational","schema_version":SCHEMA_VERSION,"scientific_stage":STAGE,
    "record_id":f"{a.position_id}:{a.engine}:{a.event_id[:16]}","engine":a.engine,"position_id":a.position_id,
    "event_id":a.event_id,"fiber_id":a.fiber_id,"context":ctx,"relations":rel,"architecture_context":arch,
    "causal_availability":CAUSAL_AVAILABILITY,"raw_full_key_emitted":False,"future_parent_trace_consulted":False,
    "parent_terminal_semantic_consulted":False,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
 print("C3X_P6_REL_PROFILE",z["record_id"],CAUSAL_AVAILABILITY)

if __name__=="__main__":main()
