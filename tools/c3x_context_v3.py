#!/usr/bin/env python3
import argparse,json
from collections import Counter
from pathlib import Path


STAGE="C3X 0.7.0-G9.5-P5"
SCHEMA_VERSION="c3x-context-v3"
CAUSAL_AVAILABILITY="STRICT_EVENT_PREFIX_ONLY"

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
 if n<=8:return "5_8"
 return "9_PLUS"

def index_bucket(i):
 n=i+1
 if n<=8:return "LE8"
 if n<=32:return "9_32"
 if n<=128:return "33_128"
 if n<=512:return "129_512"
 return "GE513"

def ply_bucket(p):
 p=int(p)
 if p<=0:return "LE0"
 if p==1:return "1"
 if p<=3:return "2_3"
 return "4_PLUS"

def depth_bucket(d):
 d=int(d)
 if d<=0:return "LE0"
 if d<=4:return "1_4"
 if d<=8:return "5_8"
 if d<=12:return "9_12"
 if d<=16:return "13_16"
 return "GE17"

def signed_delta_bucket(x):
 if x is None:return "NONE"
 x=int(x)
 if x<=-5:return "LE_NEG5"
 if x<=-1:return "NEG4_NEG1"
 if x==0:return "ZERO"
 if x<=4:return "POS1_4"
 return "GE_POS5"

def ratio_bucket(num,den):
 if den<=0 or num<=0:return "ZERO"
 r=num/den
 if r<=0.10:return "LE_0_10"
 if r<=0.30:return "LE_0_30"
 if r<=0.60:return "LE_0_60"
 return "GT_0_60"

def bound_bucket(v):
 try:n=int(v)
 except Exception:return "OTHER"
 return {0:"NONE",1:"UPPER",2:"LOWER",3:"EXACT"}.get(n,"OTHER")

def board_context(fen):
 import chess
 b=chess.Board(fen)
 if not b.is_valid() or b.chess960:raise ValueError("standard chess FEN required")
 legal=b.legal_moves.count()
 legal_bucket="0_20" if legal<=20 else "21_30" if legal<=30 else "31_40" if legal<=40 else "41_PLUS"
 center=sum(1 for s in (chess.D4,chess.E4,chess.D5,chess.E5) if b.piece_at(s))
 center_bucket="0" if center==0 else "1" if center==1 else "2_PLUS"
 homes={
  (chess.WHITE,chess.KNIGHT):{chess.B1,chess.G1},(chess.WHITE,chess.BISHOP):{chess.C1,chess.F1},
  (chess.WHITE,chess.ROOK):{chess.A1,chess.H1},(chess.WHITE,chess.QUEEN):{chess.D1},
  (chess.BLACK,chess.KNIGHT):{chess.B8,chess.G8},(chess.BLACK,chess.BISHOP):{chess.C8,chess.F8},
  (chess.BLACK,chess.ROOK):{chess.A8,chess.H8},(chess.BLACK,chess.QUEEN):{chess.D8},
 }
 displaced=0
 for sq,p in b.piece_map().items():
  k=(p.color,p.piece_type)
  if k in homes and sq not in homes[k]:displaced+=1
 dev="0_2" if displaced<=2 else "3_5" if displaced<=5 else "6_PLUS"
 rights=int(b.has_kingside_castling_rights(b.turn))+int(b.has_queenside_castling_rights(b.turn))
 return {
  "board_legal_bucket":legal_bucket,
  "board_center_bucket":center_bucket,
  "board_development_bucket":dev,
  "board_castling_bucket":str(rights),
 }

def strict_prefix_context(trace,event_ordinal):
 events=trace["events"];i=int(event_ordinal)
 if i<0 or i>=len(events):raise ValueError("event ordinal")
 e=events[i];prefix=events[:i+1];past=events[:i];prev=events[i-1] if i>0 else None
 raw_key=e.get("key")
 if raw_key is None:raise ValueError("missing parent-trace TT key")

 cc=Counter(str(z["class"]) for z in prefix)
 q=sum(1 for z in prefix if str(z["scope"])=="QSEARCH")
 bal=cc["MOVE_ORDER_SEED"]-(cc["EVAL_REUSE"]+cc["TT_VALUE_AS_EVAL"])
 balance="MOVE_LT_EVAL" if bal<0 else "BALANCED" if bal==0 else "MOVE_GT_EVAL"

 prev_same_class=next((j for j in range(i-1,-1,-1) if events[j]["class"]==e["class"]),None)
 same_class_count=sum(1 for z in prefix if z["class"]==e["class"])

 same_key_prefix=[j for j,z in enumerate(prefix) if z.get("key")==raw_key]
 prev_key=max((j for j in same_key_prefix if j<i),default=None)
 unique_keys=len({z.get("key") for z in prefix if z.get("key") is not None})

 if prev is None:
  scope_transition="START_TO_"+str(e["scope"]);ply_transition="START";prev_depth_delta=None
 else:
  scope_transition=str(prev["scope"])+"_TO_"+str(e["scope"])
  pp=int(prev["ply"]);cp=int(e["ply"])
  ply_transition="UP" if cp>pp else "DOWN" if cp<pp else "SAME"
  prev_depth_delta=int(e["depth"])-int(prev["depth"])
 key_depth_delta=None if prev_key is None else int(e["depth"])-int(events[prev_key]["depth"])

 tv=int(e["tt_value"]);alpha=int(e["alpha"]);beta=int(e["beta"])
 wr="LE_ALPHA" if tv<=alpha else "GE_BETA" if tv>=beta else "BETWEEN"
 payload=int(e.get("payload",0))

 return {
  "source_scope":str(e["scope"]),
  "source_class":str(e["class"]),
  "source_ply_bucket":ply_bucket(e["ply"]),
  "event_depth_bucket":depth_bucket(e["depth"]),
  "event_occ_bucket":count_bucket(int(e.get("occ",1))),
  "event_index_bucket":index_bucket(i),
  "event_window_relation":wr,
  "event_move_presence":"HAS_MOVE" if int(e.get("tt_move",0))!=0 else "NO_MOVE",
  "event_payload_sign":"NEG" if payload<0 else "POS" if payload>0 else "ZERO",
  "event_bound_bucket":bound_bucket(e.get("bound",0)),
  "prefix_event_count_bucket":count_bucket(len(prefix)),
  "prefix_qshare_bucket":ratio_bucket(q,len(prefix)),
  "prefix_class_balance":balance,
  "prefix_cutoff_count_bucket":count_bucket(cc["CUTOFF"]),
  "prefix_move_order_count_bucket":count_bucket(cc["MOVE_ORDER_SEED"]),
  "prefix_eval_count_bucket":count_bucket(cc["EVAL_REUSE"]+cc["TT_VALUE_AS_EVAL"]),
  "prefix_unique_key_ratio_bucket":ratio_bucket(unique_keys,len(prefix)),
  "prev_semantic_class":"START" if prev is None else str(prev["class"]),
  "prev_scope":"START" if prev is None else str(prev["scope"]),
  "same_class_count_bucket":count_bucket(same_class_count),
  "same_class_prev_gap_bucket":gap_bucket(None if prev_same_class is None else i-prev_same_class),
  "same_key_count_bucket":count_bucket(len(same_key_prefix)),
  "same_key_prev_gap_bucket":gap_bucket(None if prev_key is None else i-prev_key),
  "scope_transition_bucket":scope_transition,
  "ply_transition_bucket":ply_transition,
  "prev_depth_delta_bucket":signed_delta_bucket(prev_depth_delta),
  "same_key_depth_delta_bucket":signed_delta_bucket(key_depth_delta),
 }

def architecture_context(descriptor):
 return {
  "arch_indexing_family":str(descriptor["indexing_family"]),
  "arch_probe_refreshes_age":str(bool(descriptor["probe_refreshes_age_on_hit"])).lower(),
  "arch_probe_returns_replacement_handle":str(bool(descriptor["probe_returns_replacement_handle"])).lower(),
  "arch_eval_move_packed":str(bool(descriptor["eval_move_packed_together"])).lower(),
 }

def build_context(fen,parent_trace,event_ordinal,descriptor):
 out=board_context(fen)
 out.update(strict_prefix_context(parent_trace,event_ordinal))
 return out,architecture_context(descriptor)

def main():
 ap=argparse.ArgumentParser(description="Materialize C3X G9.5-P5 strict-prefix causal representation atoms.")
 ap.add_argument("--fen",required=True);ap.add_argument("--parent-trace",required=True)
 ap.add_argument("--event-id",required=True);ap.add_argument("--fiber-id",required=True);ap.add_argument("--engine",required=True)
 ap.add_argument("--position-id",required=True);ap.add_argument("--architecture",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 tr=json.loads(Path(a.parent_trace).read_text());desc=json.loads(Path(a.architecture).read_text())
 hits=[(i,e) for i,e in enumerate(tr["events"]) if e["address_id"]==a.event_id]
 if len(hits)!=1:raise SystemExit(f"C3X_CONTEXT_V3_EVENT_MATCH {len(hits)}")
 i,_=hits[0];ctx,arch=build_context(a.fen,tr,i,desc)
 z={"schema":"c3x-context-profile-v3","schema_version":SCHEMA_VERSION,"scientific_stage":STAGE,
    "record_id":f"{a.position_id}:{a.engine}:{a.event_id[:16]}","engine":a.engine,"position_id":a.position_id,
    "event_id":a.event_id,"fiber_id":a.fiber_id,"context":ctx,"architecture_context":arch,
    "causal_availability":CAUSAL_AVAILABILITY,"raw_full_key_emitted":False,"future_parent_trace_consulted":False,
    "parent_terminal_semantic_consulted":False,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
 print("C3X_CONTEXT_V3_PROFILE",z["record_id"],CAUSAL_AVAILABILITY)

if __name__=="__main__":main()
