#!/usr/bin/env python3
"""C3X018 fixed-depth TT source effect transport/falsification (8,10,12).

Source identities from sealed C3X018 #6/#8 and 10-nonfocal native receipts,
chosen before this depth experiment. No retargeting if no contacts.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import need
WORLDS=(1,2,5,6,8)
DEPTHS=(8,10,12)
TARGETS={
  1:{"key64":297437169592934899,"slot":0,"epoch":1},
  2:{"key64":3331180223238364038,"slot":0,"epoch":3},
  5:{"key64":17089595060187213539,"slot":0,"epoch":4},
  6:{"key64":3293258168769270517,"slot":0,"epoch":2},
  8:{"key64":14544738779862901516,"slot":0,"epoch":1},
}
def parse_score(lines,depth):
    rows=[]
    for line in lines:
        if not line.startswith("info depth "+str(depth)+" ") or " pv " not in line:continue
        score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?",line)
        nodes=re.search(r"\bnodes (\d+)",line)
        if score and nodes:
            rows.append({"score_kind":score.group(1),
                "score_value":int(score.group(2)),
                "score_flag":score.group(3) or "exact_reported",
                "nodes":int(nodes.group(1)),"pv":line.split(" pv ",1)[1].split()[:16]})
    best=[s.split()[1] for s in lines if s.startswith("bestmove ")]
    need(len(best)==1 and bool(rows) and rows[-1]["pv"][0]==best[0],"MISSING_DEPTH_SCORE")
    return {"bestmove":best[0],**rows[-1]}

def run(engine,world,root_mode,depth,ttmode="OBS",target=None,budget=1):
    env=dict(os.environ)
    for k in ("C3X018_TT_TARGET_KEY64","C3X018_TT_TARGET_SLOT","C3X018_TT_TARGET_EPOCH",
              "C3X018_TT_WRITER_BLOCK_BUDGET","C3X018_TT_RESCUE_ATTEMPT",
              "C3X018_TT_LOG_WRITES"):
        env.pop(k,None)
    env.update(C3X016_P4_MODE=root_mode,C3X016_P4_FEN4=world["fen4"],
       C3X016_P4_PLAYED_NATIVE=str(world["native_move"]),C3X018_TT_MODE=ttmode)
    if target:
        env.update(C3X018_TT_TARGET_KEY64=str(target["key64"]),
            C3X018_TT_TARGET_SLOT=str(target["slot"]),
            C3X018_TT_TARGET_EPOCH=str(target["epoch"]))
    if ttmode=="W":env["C3X018_TT_WRITER_BLOCK_BUDGET"]=str(budget)
    lines=[]
    with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
               stderr=subprocess.STDOUT,env=env,text=True,bufsize=1) as proc:
        def send(*commands):
            proc.stdin.write("\n".join(commands)+"\n");proc.stdin.flush()
        def read(marker,cap):
            for _ in range(cap):
                line=proc.stdout.readline()
                need(bool(line),"UCI_EOF")
                lines.append(line.rstrip("\n"))
                if line.startswith(marker):return
            raise RuntimeError("C3X018_UCI_CAP")
        send("uci");read("uciok",100)
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","setoption name Use NNUE value false",
             "ucinewgame","isready");read("readyok",100)
        send("position fen "+world["fen4"]+" 0 1","go depth "+str(depth))
        read("bestmove ",120000)
        send("quit")
        need(proc.wait(timeout=45)==0,"UCI_NONZERO")
    events=[line for line in lines if line.startswith("info string c3x018_lineage ")]
    need(events and not any("kind=trace_censored" in s for s in events),"LINEAGE_MISSING_OR_CENSORED")
    return {"UCI":parse_score(lines,depth),
            "TT_writer_blocks":sum("kind=writer_block " in s for s in events),
            "TT_reader_blocks":sum("kind=reader_block " in s for s in events),
            "TT_cutoff_branches":sum("kind=consumer_reached " in s for s in events)}

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","prior","patched","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    data=json.loads(Path(a.cohort).read_text());prior=json.loads(Path(a.prior).read_text())
    receipt={"schema":"c3x018-five-frozen-worlds-three-search-horizons-TT-operator-transport-v1",
      "worlds":list(WORLDS),"depths":list(DEPTHS),
      "targets":TARGETS,
      "prior_P4_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
      "cases":[]}
    for case_id in WORLDS:
        world=data["selected"][case_id-1];need(world["id"]==case_id,"ID")
        item={"id":case_id,"results":[]}
        for depth in DEPTHS:
            controls={}
            for arm in ("O","F","Z"):
                q=run(a.patched,world,arm,depth)
                replay=run(a.patched,world,arm,depth)
                need(q==replay,f"COLD_{case_id}_{depth}_{arm}")
                controls[arm]=q
                if depth==12:
                    need(q["UCI"]==prior["worlds"][case_id-1]["cells"][arm]["UCI"],
                         f"PRIOR_DEPTH12_DRIFT_{case_id}_{arm}")
            need(controls["O"]["UCI"]==controls["Z"]["UCI"],f"NO_CONTACT_OZ_{case_id}_{depth}")
            decoy=run(a.patched,world,"F",depth,"W",
                      {"key64":18446744073709551615,"slot":0,"epoch":1},budget=2)
            need(decoy["TT_writer_blocks"]==0 and decoy["UCI"]==controls["F"]["UCI"],
                 f"DECOY_CONTACT_{case_id}_{depth}")
            tests={}
            for name,mode,budget in (("W1","W",1),("W2","W",2),("R","R",1)):
                q=run(a.patched,world,"F",depth,mode,TARGETS[case_id],budget)
                replay=run(a.patched,world,"F",depth,mode,TARGETS[case_id],budget)
                need(q==replay,f"NONDETERMINISTIC_{case_id}_{depth}_{name}")
                tests[name]=dict(q,changes_bestmove_F=q["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"],
                    changes_full_core_F=q["UCI"]!=controls["F"]["UCI"])
                print("C3X018_DEPTH_TRANSPORT",case_id,depth,name,
                      q["TT_writer_blocks"],q["TT_reader_blocks"],q["UCI"]["bestmove"],
                      flush=True)
            item["results"].append({"depth":depth,
                 "controls":controls,"decoy_no_contact":True,
                 "treatments":tests})
        receipt["cases"].append(item)
    receipt["summary"]={
      "conditions":len(WORLDS)*len(DEPTHS),
      "W1_bestmove_changes":sum(t["treatments"]["W1"]["changes_bestmove_F"] for c in receipt["cases"] for t in c["results"]),
      "W2_bestmove_changes":sum(t["treatments"]["W2"]["changes_bestmove_F"] for c in receipt["cases"] for t in c["results"]),
      "R_bestmove_changes":sum(t["treatments"]["R"]["changes_bestmove_F"] for c in receipt["cases"] for t in c["results"]),
      "W2_not_fired":sum(t["treatments"]["W2"]["TT_writer_blocks"]==0 for c in receipt["cases"] for t in c["results"])}
    receipt["limitations"]=[
      "Operator target identities learned from depth12 F of selected initial 12-case cohort; not reselected at different depths",
      "Changing horizon changes TT population and event eligibility, not a pure engine-independent transport",
      "All 15 world-depth cells fixed before experiment, cold repeat, no-contact decoy, 12-depth prior exact core",
      "Writer block is full save; R blocks early cutoff branch only",
      "Source-only FEN, SF16 single-thread, 16MB hash, NNUE off, not other engines",
      "No counterfactual individual call identity or exclusive natural TT mediation proven"]
    Path(a.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("C3X018_FIXED_THREE_HORIZON_TRANSPORT_COURT_PASS",
          json.dumps(receipt["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
