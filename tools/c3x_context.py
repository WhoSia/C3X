#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from collections import Counter

STAGE="C3X 0.7.0-G9.5-P2"
CLASSES=("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL")

def _bucket(n,cuts,labels):
 for c,l in zip(cuts,labels):
  if n<=c:return l
 return labels[-1]

def board_context(fen):
 import chess
 b=chess.Board(fen)
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

def score_bucket(score):
 if not score:return "UNKNOWN"
 m=re.fullmatch(r"(cp|mate)\s+(-?\d+)",str(score).strip())
 if not m:return "UNKNOWN"
 typ,val=m.group(1),int(m.group(2))
 if typ=="mate":return "MATE_NEG" if val<0 else "MATE_POS"
 if val<=-150:return "LE_NEG150"
 if val<=-50:return "NEG149_NEG50"
 if val<=49:return "NEG49_POS49"
 if val<=149:return "POS50_POS149"
 return "GE_POS150"

def parent_context(parent_sem,parent_trace):
 events=parent_trace["events"]
 depth=int(parent_sem.get("depth") or 0)
 depth_bucket="LE8" if depth<=8 else "9_12" if depth<=12 else "13_16" if depth<=16 else "GE17"
 n=len(events)
 activity="LE63" if n<=63 else "64_255" if n<=255 else "256_1023" if n<=1023 else "GE1024"
 q=sum(1 for e in events if e["scope"]=="QSEARCH")
 share=(q/n) if n else 0.0
 qshare="ZERO" if q==0 else "LE_0_1" if share<=.1 else "LE_0_3" if share<=.3 else "GT_0_3"
 cc=Counter(e["class"] for e in events)
 bal=cc["MOVE_ORDER_SEED"]-(cc["EVAL_REUSE"]+cc["TT_VALUE_AS_EVAL"])
 balance="MOVE_LT_EVAL" if bal<0 else "BALANCED" if bal==0 else "MOVE_GT_EVAL"
 return {
  "parent_score_bucket":score_bucket(parent_sem.get("score")),
  "parent_depth_bucket":depth_bucket,
  "parent_activity_bucket":activity,
  "parent_qshare_bucket":qshare,
  "parent_class_balance":balance,
 }

def event_context(event,ordinal,total_events):
 d=int(event["depth"])
 db="LE0" if d<=0 else "1_4" if d<=4 else "5_8" if d<=8 else "9_12" if d<=12 else "13_16" if d<=16 else "GE17"
 occ=int(event.get("occ",1));ob="1" if occ==1 else "2" if occ==2 else "3_PLUS"
 if total_events<=0:q="Q1"
 else:
  idx=min(3,(4*int(ordinal))//max(1,total_events))
  q=("Q1","Q2","Q3","Q4")[idx]
 tv=int(event["tt_value"]);a=int(event["alpha"]);b=int(event["beta"])
 wr="LE_ALPHA" if tv<=a else "GE_BETA" if tv>=b else "BETWEEN"
 payload=int(event.get("payload",0));ps="NEG" if payload<0 else "POS" if payload>0 else "ZERO"
 return {
  "event_depth_bucket":db,
  "event_occ_bucket":ob,
  "event_ordinal_bucket":q,
  "event_window_relation":wr,
  "event_move_presence":"HAS_MOVE" if int(event.get("tt_move",0))!=0 else "NO_MOVE",
  "event_payload_sign":ps,
 }

def architecture_context(descriptor):
 return {
  "arch_indexing_family":str(descriptor["indexing_family"]),
  "arch_probe_refreshes_age":str(bool(descriptor["probe_refreshes_age_on_hit"])).lower(),
  "arch_probe_returns_replacement_handle":str(bool(descriptor["probe_returns_replacement_handle"])).lower(),
  "arch_eval_move_packed":str(bool(descriptor["eval_move_packed_together"])).lower(),
 }

def build_context(fen,parent_sem,parent_trace,event,event_ordinal,descriptor):
 out={}
 out.update(board_context(fen));out.update(parent_context(parent_sem,parent_trace))
 out.update(event_context(event,event_ordinal,len(parent_trace["events"])))
 return out,architecture_context(descriptor)

def main():
 ap=argparse.ArgumentParser(description="Materialize a frozen C3X pre-intervention context profile.")
 ap.add_argument("--fen",required=True);ap.add_argument("--parent-semantic",required=True);ap.add_argument("--parent-trace",required=True)
 ap.add_argument("--event-id",required=True);ap.add_argument("--fiber-id",required=True);ap.add_argument("--engine",required=True)
 ap.add_argument("--position-id",required=True);ap.add_argument("--architecture",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 sem=json.loads(Path(a.parent_semantic).read_text());tr=json.loads(Path(a.parent_trace).read_text());desc=json.loads(Path(a.architecture).read_text())
 hits=[(i,e) for i,e in enumerate(tr["events"]) if e["address_id"]==a.event_id]
 if len(hits)!=1:raise SystemExit(f"C3X_CONTEXT_EVENT_MATCH {len(hits)}")
 i,e=hits[0];ctx,arch=build_context(a.fen,sem,tr,e,i,desc)
 z={"schema":"c3x-context-profile-v1","scientific_stage":STAGE,"record_id":f"{a.position_id}:{a.engine}:{a.event_id[:16]}",
    "engine":a.engine,"position_id":a.position_id,"event_id":a.event_id,"fiber_id":a.fiber_id,
    "context":ctx,"architecture_context":arch,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
 print("C3X_CONTEXT_PROFILE",z["record_id"])

if __name__=="__main__":main()
