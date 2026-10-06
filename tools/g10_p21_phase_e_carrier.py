#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p27_age_morphism as p27
import p32_event_court as p32
import g95_p13_court as p13
import g10_p20_phase_c_census as p20c

def load(p):return json.loads(Path(p).read_text())
def pb(x):
 x=int(x);return "0" if x==0 else "1" if x==1 else "2" if x==2 else "3-4" if x<=4 else "5-8"
def db(x):
 x=int(x);return "<=0" if x<=0 else "1-4" if x<=4 else "5-8" if x<=8 else "9-12" if x<=12 else "13+"
def find_binary(root,e):
 xs=list(Path(root).rglob(f"c3x-p20c-{e}"))
 if len(xs)!=1:raise SystemExit(f"P21C_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def run(binary,protocol,fen,move,family,work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True);p=p20c.setup(binary,protocol,family,work)
 try:
  p.stdin.write(f"position fen {fen}\ngo nodes 20000 searchmoves {move}\n");p.stdin.flush();lines=p27.read_until(p,lambda x:x.startswith("bestmove "));sem=p27.parse_sem(lines)
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except:pass
 finally:
  if p.poll() is None:p.kill()
 tr=p32.parse_trace(work/"p32.csv");return p13.score_cp(sem.get("score")),tr["events"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--row",required=True);ap.add_argument("--build-dir",required=True);ap.add_argument("--preseal",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 row=load(a.row);P=load(a.preseal);frozen={tuple(x) for x in P["frozen_positive_keys"]};out=[]
 if row["chain"] is None:
  Path(a.out).write_text(json.dumps({"schema":"c3x-g10-p21-phase-e-carrier-world-v1","position_id":row["position_id"],"cells":[]},indent=2)+"\n");return
 A=row["pair"]["A"]["uci"];B=row["pair"]["B"]["uci"]
 for e in row["active_engines"]:
  if not row["engines"][e]["structural"]:continue
  b=find_binary(a.build_dir,e);protocol=p32.protocol_for(e)
  for family in ("MOVE_ORDER","CUTOFF"):
   boards={};keys=set();stable_all=True
   for arm,fk in (("TARGET","target_fen"),("SUBSET","subset_fen"),("SHAM","sham_fen")):
    vals={}
    for slot,move in (("A",A),("B",B)):
     reps=[run(b,protocol,row["chain"][fk],move,family,Path(a.out).parent/f".tmp-{e}-{family}-{arm}-{slot}-{r}") for r in range(2)]
     cpok=reps[0][0] is not None and reps[0][0]==reps[1][0];stable_all &= cpok;vals[slot]=reps[0][0]
     ids0=[(family,z["scope"],arm,slot,pb(z["ply"]),db(z["depth"])) for z in reps[0][1] if int(z["ply"])<=8]
     ids1=[(family,z["scope"],arm,slot,pb(z["ply"]),db(z["depth"])) for z in reps[1][1] if int(z["ply"])<=8]
     stable_all &= ids0==ids1
     keys.update(k for k in ids0 if k in frozen)
    gap=None if None in vals.values() else abs(vals["A"]-vals["B"]);boards[arm]={"cp":vals,"gap":gap,"supported":gap is not None and gap<=50}
   support=stable_all and all(boards[x]["supported"] for x in ("TARGET","SUBSET","SHAM"))
   expected=bool(row["engines"][e]["supported"]);matches=sorted([list(k) for k in keys])
   out.append({"engine":e,"family":family,"base_support":support,"expected_p16_support":expected,"base_identity":support==expected,"stable":stable_all,"frozen_q0_matches":matches,"carrier":bool(matches) and support==expected and stable_all})
 obj={"schema":"c3x-g10-p21-phase-e-carrier-world-v1","stage":"C3X 0.10.0-G10-P21","position_id":row["position_id"],"source_id":row["source_id"],"cells":out,"p21_intervention_outcomes_consulted":False}
 Path(a.out).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n");print("P21_CARRIER",row["position_id"],sum(x["carrier"] for x in out),"OF",len(out))
if __name__=="__main__":main()
