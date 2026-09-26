#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_context as base

STAGE="C3X 0.7.0-G9.5-P3"
SCHEMA_VERSION="c3x-context-v2"

def gap_bucket(g):
 if g is None:return "NONE"
 if g==1:return "1"
 if g<=4:return "2_4"
 if g<=16:return "5_16"
 return "17_PLUS"

def count_bucket(n):
 if n<=1:return "1"
 if n==2:return "2"
 if n<=4:return "3_4"
 return "5_PLUS"

def bound_bucket(v):
 try:n=int(v)
 except Exception:return "OTHER"
 return {0:"NONE",1:"UPPER",2:"LOWER",3:"EXACT"}.get(n,"OTHER")

def topology_context(trace,event_ordinal):
 events=trace["events"];i=int(event_ordinal);e=events[i]
 prev=events[i-1] if i>0 else None
 nxt=events[i+1] if i+1<len(events) else None

 prev_same_class=next((j for j in range(i-1,-1,-1) if events[j]["class"]==e["class"]),None)
 same_class_gap=None if prev_same_class is None else i-prev_same_class

 fk=e.get("full_key")
 same_key=[j for j,z in enumerate(events) if z.get("full_key")==fk] if fk is not None else [i]
 prev_key=max((j for j in same_key if j<i),default=None)
 next_key=min((j for j in same_key if j>i),default=None)

 lo=max(0,i-4);hi=min(len(events),i+5)
 diversity=len({z["class"] for z in events[lo:hi]})
 diversity_bucket="1" if diversity<=1 else "2" if diversity==2 else "3_PLUS"

 if prev is None:scope_transition="START_TO_"+str(e["scope"])
 else:scope_transition=str(prev["scope"])+"_TO_"+str(e["scope"])

 if prev is None:ply_transition="START"
 else:
  pp=int(prev["ply"]);cp=int(e["ply"])
  ply_transition="UP" if cp>pp else "DOWN" if cp<pp else "SAME"

 return {
  "event_bound_bucket":bound_bucket(e.get("bound",0)),
  "prev_semantic_class":"START" if prev is None else str(prev["class"]),
  "next_semantic_class":"END" if nxt is None else str(nxt["class"]),
  "same_class_prev_gap_bucket":gap_bucket(same_class_gap),
  "local_class_diversity_bucket":diversity_bucket,
  "same_key_count_bucket":count_bucket(len(same_key)),
  "same_key_prev_gap_bucket":gap_bucket(None if prev_key is None else i-prev_key),
  "same_key_next_gap_bucket":gap_bucket(None if next_key is None else next_key-i),
  "scope_transition_bucket":scope_transition,
  "ply_transition_bucket":ply_transition,
 }

def build_context(fen,parent_sem,parent_trace,event,event_ordinal,descriptor):
 ctx,arch=base.build_context(fen,parent_sem,parent_trace,event,event_ordinal,descriptor)
 ctx.update(topology_context(parent_trace,event_ordinal))
 return ctx,arch

def main():
 ap=argparse.ArgumentParser(description="Materialize C3X G9.5-P3 pre-intervention topology-aware context profile.")
 ap.add_argument("--fen",required=True);ap.add_argument("--parent-semantic",required=True);ap.add_argument("--parent-trace",required=True)
 ap.add_argument("--event-id",required=True);ap.add_argument("--fiber-id",required=True);ap.add_argument("--engine",required=True)
 ap.add_argument("--position-id",required=True);ap.add_argument("--architecture",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 sem=json.loads(Path(a.parent_semantic).read_text());tr=json.loads(Path(a.parent_trace).read_text());desc=json.loads(Path(a.architecture).read_text())
 hits=[(i,e) for i,e in enumerate(tr["events"]) if e["address_id"]==a.event_id]
 if len(hits)!=1:raise SystemExit(f"C3X_CONTEXT_V2_EVENT_MATCH {len(hits)}")
 i,e=hits[0];ctx,arch=build_context(a.fen,sem,tr,e,i,desc)
 z={"schema":"c3x-context-profile-v2","schema_version":SCHEMA_VERSION,"scientific_stage":STAGE,
    "record_id":f"{a.position_id}:{a.engine}:{a.event_id[:16]}","engine":a.engine,"position_id":a.position_id,
    "event_id":a.event_id,"fiber_id":a.fiber_id,"context":ctx,"architecture_context":arch,
    "raw_full_key_emitted":False,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
 print("C3X_CONTEXT_V2_PROFILE",z["record_id"])

if __name__=="__main__":main()
