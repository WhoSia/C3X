#!/usr/bin/env python3
"""Authority-neutral chess phenotype atlas for C3X G9.5-P7.

This compiler never selects or mutates a CSEG state law. It only reads target
artifacts whose opening has already been authorized by the canonical P7 court
and renders chess-native consequences of exact-event intervention.
"""
import argparse,json,math
from collections import Counter,defaultdict
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P7"

def load(p): return json.loads(Path(p).read_text())

def corpus_fens(c):
 out={}
 for key in ("structural_train_positions","structural_selection_positions","untouched_transport_positions"):
  for z in c.get(key,[]): out[z["position_id"]]=z["cell"]["fen"]
 return out

def require_authority(role,cert):
 if role=="STRUCTURAL_TRAIN":
  if cert.get("schema")!="c3x-p7-train-field-v1" or cert.get("train_targets_consulted") is not True:
   raise SystemExit("P7_ATLAS_TRAIN_AUTHORITY")
 elif role=="STRUCTURAL_SELECTION":
  if cert.get("schema")!="c3x-p7-selected-field-v1" or cert.get("selection_targets_consulted") is not True:
   raise SystemExit("P7_ATLAS_SELECTION_AUTHORITY")
 elif role=="UNTOUCHED_TRANSPORT":
  if cert.get("schema")!="c3x-p7-transport-verification-v1" or cert.get("transport_targets_consulted") is not True:
   raise SystemExit("P7_ATLAS_TRANSPORT_AUTHORITY")
 else: raise SystemExit("P7_ATLAS_ROLE")

def pv_list(x):
 if x is None:return []
 if isinstance(x,list):return [str(v) for v in x]
 if isinstance(x,str):return [z for z in x.strip().split() if z]
 return []

def first_divergence(a,b):
 n=min(len(a),len(b));i=0
 while i<n and a[i]==b[i]:i+=1
 if i==len(a)==len(b):return None
 return {"ply_index":i,"common_prefix":a[:i],"baseline_next":a[i] if i<len(a) else None,
  "counterfactual_next":b[i] if i<len(b) else None,"baseline_remaining":a[i:],"counterfactual_remaining":b[i:]}

def number_score(x):
 if isinstance(x,(int,float)) and math.isfinite(float(x)):return float(x)
 if isinstance(x,dict):
  for k in ("cp","value","score"):
   v=x.get(k)
   if isinstance(v,(int,float)) and math.isfinite(float(v)):return float(v)
 return None

def direction(a,b):
 x,y=number_score(a),number_score(b)
 if x is None or y is None:return "UNAVAILABLE"
 return "UP" if y>x else "DOWN" if y<x else "SAME"

def wdl_expectation(x):
 if isinstance(x,(list,tuple)) and len(x)>=3:
  try:
   w,d,l=map(float,x[:3]);s=w+d+l
   return None if s==0 else (w+0.5*d)/s
  except Exception:return None
 if isinstance(x,dict):
  try:
   w=float(x.get("win",x.get("w")));d=float(x.get("draw",x.get("d")));l=float(x.get("loss",x.get("l")));s=w+d+l
   return None if s==0 else (w+0.5*d)/s
  except Exception:return None
 return None

def wdl_direction(a,b):
 x,y=wdl_expectation(a),wdl_expectation(b)
 if x is None or y is None:return "UNAVAILABLE"
 return "UP" if y>x else "DOWN" if y<x else "SAME"

def san_move(fen,uci):
 if not fen or not uci:return None
 try:
  import chess
  b=chess.Board(fen);m=chess.Move.from_uci(uci)
  return b.san(m) if m in b.legal_moves else None
 except Exception:return None

def legal_pv(fen,pv):
 if not fen:return None
 try:
  import chess
  b=chess.Board(fen)
  for u in pv:
   m=chess.Move.from_uci(u)
   if m not in b.legal_moves:return False
   b.push(m)
  return True
 except Exception:return False

def add_counter(d,k):
 d[k]=d.get(k,0)+1

def main():
 ap=argparse.ArgumentParser(description="Compile authority-neutral C3X P7 chess phenotype atlas.")
 ap.add_argument("--role",choices=["STRUCTURAL_TRAIN","STRUCTURAL_SELECTION","UNTOUCHED_TRANSPORT"],required=True)
 ap.add_argument("--targets",required=True);ap.add_argument("--profiles",required=True);ap.add_argument("--corpus",required=True)
 ap.add_argument("--authority-certificate",required=True);ap.add_argument("--field")
 ap.add_argument("--out",required=True);ap.add_argument("--markdown",required=True)
 a=ap.parse_args()
 t,p,c,cert=map(load,(a.targets,a.profiles,a.corpus,a.authority_certificate));require_authority(a.role,cert)
 if t.get("role")!=a.role or p.get("role")!=a.role:raise SystemExit("P7_ATLAS_ROLE_MISMATCH")
 tm={r["record_id"]:r for r in t["records"]};pm={r["record_id"]:r for r in p["records"]}
 if set(tm)!=set(pm):raise SystemExit("P7_ATLAS_JOIN")
 fens=corpus_fens(c)
 field=load(a.field) if a.field else None
 q=None if field is None else field.get("selected_q_level")
 rows=[]
 for rid in sorted(tm):
  tr,pr=tm[rid],pm[rid];base=tr.get("baseline") or {};cf=tr.get("counterfactual") or {}
  bpv,cpv=pv_list(base.get("pv")),pv_list(cf.get("pv"));fen=fens.get(pr["position_id"])
  phen=tr.get("chess_phenotype") or {}
  buci=(phen.get("baseline") or {}).get("uci") or base.get("bestmove")
  cuci=(phen.get("counterfactual") or {}).get("uci") or cf.get("bestmove")
  cur=pr.get("current_event") or {}
  state_id=None if q is None else (pr.get("state_ids") or {}).get(q)
  rows.append({
   "record_id":rid,"role":a.role,"engine":pr["engine"],"position_id":pr["position_id"],
   "source_stratum":pr["source_stratum"],"source_kind":pr.get("source_kind"),
   "sampling_stratum":pr.get("sampling_stratum"),"semantic_class":cur.get("class"),"search_scope":cur.get("scope"),
   "q_level":q,"state_id":state_id,"root_change":bool(tr["root_change"]),
   "root_move":{"baseline_uci":buci,"counterfactual_uci":cuci,"baseline_san":san_move(fen,buci),
     "counterfactual_san":san_move(fen,cuci),"baseline_atoms":phen.get("baseline"),"counterfactual_atoms":phen.get("counterfactual")},
   "pv":{"baseline":bpv,"counterfactual":cpv,"first_divergence":first_divergence(bpv,cpv),
     "baseline_legal":legal_pv(fen,bpv),"counterfactual_legal":legal_pv(fen,cpv)},
   "score":{"baseline":base.get("score"),"counterfactual":cf.get("score"),"direction":direction(base.get("score"),cf.get("score"))},
   "wdl":{"baseline":base.get("wdl"),"counterfactual":cf.get("wdl"),"direction":wdl_direction(base.get("wdl"),cf.get("wdl"))}
  })
 positives=[r for r in rows if r["root_change"]]
 def group(field):
  z=defaultdict(lambda:{"records":0,"root_change":0})
  for r in rows:
   k=str(r.get(field));z[k]["records"]+=1;z[k]["root_change"]+=int(r["root_change"])
  return dict(sorted(z.items()))
 transitions=Counter()
 piece=Counter();score_dir=Counter();wdl_dir=Counter();pvdiv=Counter()
 for r in positives:
  rm=r["root_move"];transitions[(rm["baseline_uci"],rm["counterfactual_uci"])]+=1
  piece[((rm["baseline_atoms"] or {}).get("piece"),(rm["counterfactual_atoms"] or {}).get("piece"))]+=1
  score_dir[r["score"]["direction"]]+=1;wdl_dir[r["wdl"]["direction"]]+=1
  d=r["pv"]["first_divergence"];pvdiv["NONE" if d is None else str(d["ply_index"])]+=1
 out={"schema":"c3x-g95-p7-chess-phenotype-atlas-v1","scientific_stage":STAGE,"role":a.role,
  "authority":"DOWNSTREAM_EXPLANATION_ONLY","may_select_or_modify_field":False,"may_expand_public_authority":False,
  "authority_certificate_schema":cert.get("schema"),"selected_q_level":q,"records":len(rows),"root_change_records":len(positives),
  "by_engine":group("engine"),"by_source_kind":group("source_kind"),"by_source_stratum":group("source_stratum"),
  "by_semantic_class":group("semantic_class"),"positive_root_move_transitions":[{"baseline":k[0],"counterfactual":k[1],"count":v} for k,v in transitions.most_common()],
  "positive_piece_transitions":[{"baseline_piece":k[0],"counterfactual_piece":k[1],"count":v} for k,v in piece.most_common()],
  "positive_score_direction":dict(score_dir),"positive_wdl_direction":dict(wdl_dir),"positive_pv_first_divergence_ply":dict(pvdiv),
  "record_atlas":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=[f"# C3X G9.5-P7 Chess Phenotype Atlas — {a.role}","",
  "**Authority:** downstream explanation only; this atlas cannot select, split or modify a CSEG state law.","",
  f"- Records: **{len(rows)}**",f"- ROOT_CHANGE records: **{len(positives)}**",f"- Selected CSEG level: **{q or 'none'}**","",
  "## ROOT_CHANGE by engine"]
 for k,v in out["by_engine"].items():lines.append(f"- {k}: **{v['root_change']}/{v['records']}**")
 lines+=["","## ROOT_CHANGE by chess-world lane"]
 for k,v in out["by_source_kind"].items():lines.append(f"- {k}: **{v['root_change']}/{v['records']}**")
 lines+=["","## ROOT_CHANGE by source stratum"]
 for k,v in out["by_source_stratum"].items():lines.append(f"- {k}: **{v['root_change']}/{v['records']}**")
 lines+=["","## TT semantic-use class"]
 for k,v in out["by_semantic_class"].items():lines.append(f"- {k}: **{v['root_change']}/{v['records']}**")
 lines+=["","## Most frequent positive root-move transitions"]
 for z in out["positive_root_move_transitions"][:25]:lines.append(f"- `{z['baseline']}` → `{z['counterfactual']}`: **{z['count']}**")
 lines+=["","## Interpretation boundary",
  "This atlas describes chess consequences of already-authorized exact-event interventions. It does not change the P7 train, selection or transport verdict and does not promote a search-state abstraction into human strategic intent."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P7_CHESS_PHENOTYPE_ATLAS",a.role,len(rows),len(positives),q)

if __name__=="__main__":main()
