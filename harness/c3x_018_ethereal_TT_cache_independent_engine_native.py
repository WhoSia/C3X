#!/usr/bin/env python3
"""Native independent Ethereal TT cached evaluation transport source court.

12 new November games, depths 8/12, baseline and cache-bypass double cold.
Distinct from Stockfish16/17 V value-as-evaluation override intervention.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_native_TT_lineage_factorial_6_8 import need

SHA="2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402"

def run(engine,w,half,full,depth,gate):
 env=dict(os.environ)
 env.pop("C3X018_ETH_TT_CACHE_GATE",None)
 if gate:env["C3X018_ETH_TT_CACHE_GATE"]="all"
 lines=[]
 with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,env=env,text=True,bufsize=1) as proc:
  def send(*cmd):
   proc.stdin.write("\n".join(cmd)+"\n");proc.stdin.flush()
  def collect(marker,limit):
   for _ in range(limit):
    line=proc.stdout.readline()
    need(bool(line),"ETHEREAL_UCI_PREMATURE_EOF_"+marker)
    lines.append(line.rstrip("\n"))
    if line.startswith(marker):return
   raise RuntimeError("ETHEREAL_UCI_LINE_CAP_"+marker)
  send("uci");collect("uciok",180)
  send("setoption name Threads value 1",
       "setoption name Hash value 16",
       "setoption name MultiPV value 1",
       "ucinewgame","isready");collect("readyok",180)
  send("position fen "+w["fen4"]+" "+str(half)+" "+str(full),
       "go depth "+str(depth));collect("bestmove ",120000)
  send("quit");need(proc.wait(timeout=45)==0,"ETHEREAL_FAILED_NATIVE_EXIT")
 best=[line.split()[1] for line in lines if line.startswith("bestmove ")]
 candidates=[]
 for line in lines:
  if line.startswith("info depth "+str(depth)+" ") and " pv " in line:
   score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?",line)
   nodes=re.search(r"\bnodes (\d+)",line)
   if score and nodes:
    candidates.append({"score_kind":score.group(1),
      "score_value":int(score.group(2)),
      "score_flag":score.group(3) or "exact_reported",
      "nodes":int(nodes.group(1)),
      "pv":line.split(" pv ",1)[1].split()[:16]})
 need(len(best)==1 and candidates and best[0]==candidates[-1]["pv"][0],
      "ETHEREAL_FINAL_DEPTH_UCI_MISSING")
 contacts=[s for s in lines if s.startswith("info string c3x018_eth_cache_contact ")]
 if not gate:need(not contacts,"PASSIVE_GATE_CONTACT")
 return {"UCI":{"bestmove":best[0],**candidates[-1]},
         "cache_gate_logged":len(contacts),
         "cache_gate_cap":16,
         "cache_gate_sites":sorted({re.search(r"site=(\w+)",s).group(1)
                                   for s in contacts})}

def main():
 p=argparse.ArgumentParser()
 for v in ("source","engine","out"):p.add_argument("--"+v,required=True)
 a=p.parse_args()
 b=Path(a.source).read_bytes()
 need(hashlib.sha256(b).hexdigest()==SHA,"BLIND_NOVEMBER_GAME_SOURCE_SHA")
 source=json.loads(b)
 need(len(source["selected"])==12,"FROZEN_NOVEMBER_12")
 output={"schema":"c3x018-independent-ethereal-nov12-TT-static-cache-8-12-depth-v1",
        "engine":"AndyGrant/Ethereal 0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
        "source_SHA":SHA,"cases":[]}
 for raw in source["selected"]:
  world,norm=canonical_engine_world(raw)
  half,full=game_clocks(raw)
  case={"id":raw["id"],"game_sha256":raw["source_game_sha256"],
        "clock":[half,full],"depths":[]}
  for depth in (8,12):
   item={"depth":depth,"status":"NOT_RUN"}
   try:
    for name,gate in (("original",False),("cache_bypass",True)):
     x=run(a.engine,world,half,full,depth,gate)
     y=run(a.engine,world,half,full,depth,gate)
     need(x==y,"ETHEREAL_COLD_REPLAY_"+name)
     item[name]=x
    item["status"]="VALID"
    item["bestmove_changed"]=(item["original"]["UCI"]["bestmove"]!=
                              item["cache_bypass"]["UCI"]["bestmove"])
    item["full_core_changed"]=item["original"]["UCI"]!=item["cache_bypass"]["UCI"]
   except (RuntimeError,KeyError,ValueError) as error:
    item["status"]="HOLD_FAIL_CLOSED";item["failure"]=type(error).__name__+":"+str(error)[:280]
   case["depths"].append(item)
   print("C3X018_ETHEREAL_CACHE_NATIVE",case["id"],depth,item["status"],
         item.get("bestmove_changed"),item.get("cache_bypass",{}).get("cache_gate_logged"),
         flush=True)
  output["cases"].append(case)
 valid=[item for c in output["cases"] for item in c["depths"] if item["status"]=="VALID"]
 reach={str(d):sum(t["cache_bypass"]["cache_gate_logged"]>0
      for t in valid if t["depth"]==d) for d in (8,12)}
 summary={"prespecified_game_depth":24,"completed":len(valid),
       "hold":24-len(valid),
       "bestmove_changed":sum(t["bestmove_changed"] for t in valid),
       "full_core_changed":sum(t["full_core_changed"] for t in valid),
       "read_gate_reach":reach,
       "I1_SOURCE_ROLE":"PASS" if len(valid)==24 else "HOLD",
       "I2_READER_CONTACT":"PASS" if all(n>0 for n in reach.values()) else "FAIL",
       "I3_ROOT_IMPACT":"PASS" if any(t["bestmove_changed"] for t in valid) else "FAIL",
       "I4_FULL_DENOMINATOR":"PASS" if len(valid)==24 else "HOLD",
       "I5_NONISOMORPHIC_BOUNDARY":"PASS"}
 if len(valid)!=24:
  summary["I2_READER_CONTACT"]=summary["I3_ROOT_IMPACT"]="HOLD"
 output["summary"]=summary
 output["limitations"]=[
  "Ethereal is a distinct chess engine implementation; its source ttEval cache is NOT bound-conditioned ttValue-as-eval Stockfish V",
  "Global bypass of every eligible TT cached static evaluation, not a physical single-reader intervention",
  "No direct TT writer generation or identity across engines, no TT mediation uniqueness claim",
  "Classical eval Ethereal; original six-field board clocks; history stack not replayed",
  "Full 12 new games and two depths frozen before engine outcomes"]
 path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print("C3X018_INDEPENDENT_ETHEREAL_CACHE_NATIVE_SUMMARY",json.dumps(summary,sort_keys=True),flush=True)
 if len(valid)!=24:raise RuntimeError("ETHEREAL_NATIVE_FULL_DENOMINATOR_HOLD")
if __name__=="__main__":main()
