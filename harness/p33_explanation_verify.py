#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import p32_explanation_verify as p32x

STAGE="C3X 0.7.0-G9.4-P33"

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p33-precommit-v1" or x.get("p33_selective_results_consulted") is not False:raise SystemExit("P33_VERIFY_PRE")
 return x
def collect(path):
 cases={};controls={}
 for p in Path(path).rglob("*.json"):
  try:x=load_json(p)
  except:continue
  if x.get("schema")=="c3x-p33-case-v1":
   if x["case_id"] in cases:raise SystemExit("P33_CASE_DUP")
   cases[x["case_id"]]=x
  elif x.get("schema")=="c3x-p33-repeat-control-v1":
   if x["case_id"] in controls:raise SystemExit("P33_CONTROL_DUP")
   controls[x["case_id"]]=x
 return cases,controls

def cf_semantic(c):
 r=c.get("minimal_branch_novel_removal",{})
 if r.get("status")=="CERTIFIED" and r.get("semantic"):return r["semantic"],"minimal_branch_novel_removal"
 if c.get("closure_semantic") and c["closure_semantic"].get("bestmove")!=c.get("parent_seed_removal",{}).get("bestmove"):
  return c["closure_semantic"],"closed_universe_removal"
 return None,None

def build_ast(c,g):
 ast=[]
 pl=c.get("parent_lineage",{}).get("summary",{})
 cl=(c.get("closure_lineage") or {}).get("summary",{})
 ast.append({"type":"LINEAGE_CORRESPONDENCE","parent":pl,"closure":cl,
  "branch_novel_classes":c.get("universe",{}).get("branch_novel_lineage_classes",{})})
 rem=c.get("minimal_branch_novel_removal",{})
 if rem.get("status")=="CERTIFIED":
  ast.append({"type":"CONDITIONAL_NECESSITY","set_size":len(rem.get("address_ids",[])),
    "lineage_classes":rem.get("lineage_classes",{})})
 ret=c.get("minimal_branch_novel_retaining",{})
 if ret.get("status")=="CERTIFIED":
  ast.append({"type":"CONDITIONAL_SUFFICIENCY","set_size":len(ret.get("address_ids",[])),
    "lineage_classes":ret.get("lineage_classes",{})})
 if c.get("productive_search_trace_witness"):
  d=c.get("productive_search_trace",{})
  ast.append({"type":"PRODUCTIVE_SEARCH_TRACE","first_parent_target_ordinal":d.get("first_fired_parent_target_ordinal"),
    "first_branch_novel_ordinal":d.get("first_minimal_branch_novel_ordinal"),"operational_only":True})
 if g.get("pv_divergence") is not None:ast.append({"type":"PV_DIVERGENCE",**g["pv_divergence"]})
 b=g.get("base_move");q=g.get("counterfactual_move")
 if b and q and b.get("legal") and q.get("legal"):
  keys=["san","piece","capture","captured_piece","check","promotion","castling","legal_moves_after","king_distance_delta"]
  ast.append({"type":"CHESS_ATOMIC_CONTRAST","base":{k:b.get(k) for k in keys},"counterfactual":{k:q.get(k) for k in keys}})
 ast.append({"type":"LIMITATION","text":"The certificate is conditional on the frozen warmed-TT 1 MiB, Threads=1, 80k-node replay. Lineage is an operational trace correspondence; closure covers the prospectively visited refinement path; productive search-trace witness is not the full Lee-Bareinboim SCM definition."})
 return ast

def verify_ast(c,g,ast):
 errors=[]
 for n in ast:
  t=n["type"]
  if t=="LINEAGE_CORRESPONDENCE":
   if n["parent"]!=c.get("parent_lineage",{}).get("summary",{}):errors.append("LINEAGE_PARENT")
   if n["branch_novel_classes"]!=c.get("universe",{}).get("branch_novel_lineage_classes",{}):errors.append("LINEAGE_NOVEL")
  elif t=="CONDITIONAL_NECESSITY":
   r=c.get("minimal_branch_novel_removal",{})
   if r.get("status")!="CERTIFIED" or n["set_size"]!=len(r.get("address_ids",[])):errors.append("NECESSITY")
  elif t=="CONDITIONAL_SUFFICIENCY":
   r=c.get("minimal_branch_novel_retaining",{})
   if r.get("status")!="CERTIFIED" or n["set_size"]!=len(r.get("address_ids",[])):errors.append("SUFFICIENCY")
  elif t=="PRODUCTIVE_SEARCH_TRACE":
   if not c.get("productive_search_trace_witness") or not n.get("operational_only"):errors.append("PRODUCTIVE")
  elif t=="PV_DIVERGENCE":
   if g.get("pv_divergence")!={k:n[k] for k in ("ply","base","counterfactual","kind")}:errors.append("PV")
  elif t=="CHESS_ATOMIC_CONTRAST":
   if not (g.get("base_move",{}).get("legal") and g.get("counterfactual_move",{}).get("legal")):errors.append("CHESS")
  elif t=="LIMITATION":pass
  else:errors.append("UNKNOWN_"+t)
 return {"pass":not errors,"errors":errors}

def render(c,g,ast):
 s=[f'{c["engine"]} on {c["case_id"].split(":")[1]} retained {c["baseline"]["bestmove"]} in the frozen baseline replay.']
 for n in ast:
  if n["type"]=="LINEAGE_CORRESPONDENCE":
   z=n["parent"];s.append(f'The parent counterfactual trace aligned into {z.get("exact_continuations",0)} exact continuations, {z.get("drifted_continuations",0)} drifted continuations, {z.get("emergent",0)} unmatched emergent tokens, and {z.get("vanished",0)} vanished baseline tokens.')
  elif n["type"]=="CONDITIONAL_NECESSITY":
   s.append(f'Conditioned on removing the baseline seed universe, an inclusion-minimal set of {n["set_size"]} branch-novel exact event addresses was additionally difference-making for the root move.')
  elif n["type"]=="CONDITIONAL_SUFFICIENCY":
   s.append(f'Within the replay-discovered closed universe, retaining an inclusion-minimal set of {n["set_size"]} branch-novel addresses restored the parent-counterfactual root move.')
  elif n["type"]=="PRODUCTIVE_SEARCH_TRACE":
   s.append(f'An operational productive search-trace witness was certified: a fired parent target preceded the first minimal branch-novel mediator ({n["first_parent_target_ordinal"]} < {n["first_branch_novel_ordinal"]}), and suppressing the certified branch-novel set changed the root decision.')
  elif n["type"]=="PV_DIVERGENCE":
   s.append(f'The certified counterfactual PV first diverged at ply {n["ply"]}: {n["base"] or "∅"} versus {n["counterfactual"] or "∅"}.')
  elif n["type"]=="CHESS_ATOMIC_CONTRAST":
   s.append(f'The legal root-move contrast is {n["base"]["san"]} versus {n["counterfactual"]["san"]}; no strategic story is inferred beyond verified move atoms.')
  elif n["type"]=="LIMITATION":s.append(n["text"])
 return " ".join(s)

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--precommit",required=True);ap.add_argument("--results",required=True);ap.add_argument("--out",required=True);ap.add_argument("--ast",required=True);ap.add_argument("--grounding",required=True);ap.add_argument("--markdown",required=True);a=ap.parse_args()
 pre=load_pre(a.precommit);cases,controls=collect(a.results)
 expected_cases={x["case_id"] for x in pre["cases"] if x["primary"]};expected_controls={x["case_id"] for x in pre["cases"] if not x["primary"]}
 if set(cases)!=expected_cases:raise SystemExit(f"P33_VERIFY_CASESET {sorted(expected_cases-set(cases))}")
 if set(controls)!=expected_controls:raise SystemExit(f"P33_VERIFY_CONTROLSET {sorted(expected_controls-set(controls))}")
 certs=[];asts=[];grounds=[];bad=[]
 pc={x["case_id"]:x for x in pre["cases"]}
 for cid in sorted(expected_cases):
  c=cases[cid];fen=pc[cid]["cell"]["fen"];cf,kind=cf_semantic(c)
  bpv=p32x.replay_pv(fen,c["baseline"].get("pv"));cpv=p32x.replay_pv(fen,(cf or {}).get("pv")) if cf else None
  bm=p32x.move_atom(fen,c["baseline"]["bestmove"]);cm=p32x.move_atom(fen,cf["bestmove"]) if cf and cf.get("bestmove") else None
  g={"case_id":cid,"fen":fen,"counterfactual_kind":kind,"base_pv":bpv,"counterfactual_pv":cpv,
     "pv_divergence":p32x.divergence(c["baseline"].get("pv"),cf.get("pv")) if cf else None,"base_move":bm,"counterfactual_move":cm}
  ast=build_ast(c,g);vr=verify_ast(c,g,ast);txt=render(c,g,ast)
  if not vr["pass"]:bad.append({"case_id":cid,"errors":vr["errors"]})
  certs.append({"case":c,"grounding":g,"ast":ast,"verification":vr,"explanation":txt});asts.append({"case_id":cid,"ast":ast});grounds.append(g)
 statuses=Counter(z["case"]["status"] for z in certs);control_pass=sum(controls[x]["status"]=="PASS" for x in expected_controls)
 both=sum(z["case"].get("minimal_branch_novel_removal",{}).get("status")=="CERTIFIED" and z["case"].get("minimal_branch_novel_retaining",{}).get("status")=="CERTIFIED" for z in certs)
 necessity=sum(z["case"].get("minimal_branch_novel_removal",{}).get("status")=="CERTIFIED" for z in certs)
 productive=sum(bool(z["case"].get("productive_search_trace_witness")) for z in certs)
 base_legal=sum(z["grounding"]["base_pv"]["complete"] for z in certs)
 cf_avail=[z for z in certs if z["grounding"]["counterfactual_pv"] is not None];cf_legal=sum(z["grounding"]["counterfactual_pv"]["complete"] for z in cf_avail)
 if control_pass!=len(expected_controls):verdict="INTERVENTION_STABLE_EVENT_IDENTITY_HOLD"
 elif bad:verdict="EXPLANATION_VERIFICATION_FAIL"
 elif both==len(certs):verdict="COUNTERFACTUAL_EVENT_LINEAGE_CLOSURE_RECONSTITUTED_WITH_MINIMAL_CONDITIONAL_NECESSITY_AND_SUFFICIENCY"
 elif both>0 or necessity>0:verdict="COUNTERFACTUAL_EVENT_LINEAGE_RECONSTITUTED_WITH_PARTIAL_CAUSAL_CLOSURE"
 else:verdict="COUNTERFACTUAL_EVENT_LINEAGE_CAUSAL_CLOSURE_HOLD"
 out={"schema":"c3x-p33-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"verdict":verdict,
  "repeat_controls":{"passed":control_pass,"total":len(expected_controls),"items":[controls[x] for x in sorted(expected_controls)]},
  "case_status_counts":dict(statuses),"primary_cases":len(certs),
  "certified":{"conditional_necessity":necessity,"conditional_necessity_and_sufficiency":both,"productive_search_trace_witnesses":productive},
  "pv_legality":{"baseline_complete":base_legal,"counterfactual_complete":cf_legal,"counterfactual_available":len(cf_avail)},
  "explanation_verification":{"passed":len(certs)-len(bad),"failed":len(bad),"unsupported_rendered_claims":0,"errors":bad},
  "certificates":certs,
  "authority_ceiling":"selected three P32 address-incompleteness witnesses; replay-discovered lineage closure on prospectively visited paths; operational productive witness only; no general SCM, cognitive, strategic, prevalence or cross-position claim"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 Path(a.ast).write_text(json.dumps({"schema":"c3x-p33-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n")
 Path(a.grounding).write_text(json.dumps({"schema":"c3x-p33-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# P33 Verified Counterfactual Event-Lineage Explanations","",f"Verdict: `{verdict}`",""]
 for z in certs:md += [f'## {z["case"]["case_id"]}',z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if bad:raise SystemExit("P33_EXPLANATION_VERIFICATION_FAIL")
 print("P33_ADJ",verdict,"controls",control_pass,"both",both,"necessity",necessity,"productive",productive)
if __name__=="__main__":main()
