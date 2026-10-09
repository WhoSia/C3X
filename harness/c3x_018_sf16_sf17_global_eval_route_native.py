#!/usr/bin/env python3
"""Preregistered source-similar TT value-as-eval route SF16 vs SF17.

Global operator both: suppress all bound-conditioned tt score-as-evaluation
uses at main and quiescence search. This is NOT physically targeted V.
SF16 classical and SF17 NNUE are deliberately distinct static eval algorithms.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_native_TT_lineage_factorial_6_8 import need

SOURCE_SHA="2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402"
DEPTHS=(8,12)
VERSIONS=("sf16","sf17")

def trial(engine,world,version,depth,enabled,half,full):
    env=dict(os.environ)
    env.pop("C3X018_GLOBAL_TT_EVAL_GATE",None)
    if enabled:env["C3X018_GLOBAL_TT_EVAL_GATE"]="both"
    lines=[]
    with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as proc:
        def command(*strings):
            proc.stdin.write("\n".join(strings)+"\n");proc.stdin.flush()
        def recv(tag,cap):
            for _ in range(cap):
                line=proc.stdout.readline()
                need(bool(line),"ENGINE_EOF_"+version+"_"+tag)
                line=line.rstrip("\n")
                lines.append(line)
                if line.startswith(tag):return
            raise RuntimeError("ENGINE_LINE_CAP_"+tag)
        command("uci");recv("uciok",160)
        setup=["setoption name Threads value 1","setoption name Hash value 16",
               "setoption name MultiPV value 1"]
        if version=="sf16":setup.append("setoption name Use NNUE value false")
        setup+=["ucinewgame","isready"]
        command(*setup);recv("readyok",160)
        command("position fen "+world["fen4"]+" "+str(half)+" "+str(full),
                "go depth "+str(depth))
        recv("bestmove ",130000)
        command("quit")
        need(proc.wait(timeout=45)==0,"ENGINE_NATIVE_EXIT_"+version)
    rows=[]
    for s in lines:
        if s.startswith("info depth "+str(depth)+" ") and " pv " in s:
            score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?",s)
            nodes=re.search(r"\bnodes (\d+)",s)
            if score and nodes:
                rows.append({"score_kind":score.group(1),
                 "score_value":int(score.group(2)),
                 "score_flag":score.group(3) or "exact_reported",
                 "nodes":int(nodes.group(1)),
                 "pv":s.split(" pv ",1)[1].split()[:16]})
    moves=[s.split()[1] for s in lines if s.startswith("bestmove ")]
    need(len(moves)==1 and rows and moves[0]==rows[-1]["pv"][0],
         "NO_NATIVE_BESTMOVE_OR_DEPTH_SCORE")
    contacts=[s for s in lines if s.startswith("info string c3x018_global_tt_eval_contact ")]
    if not enabled:need(not contacts,"PASSIVE_GLOBAL_GATE_FIRED")
    return {"UCI":{"bestmove":moves[0],**rows[-1]},
            "gate_contact_logged":len(contacts),
            "gate_contact_censored_at":16,
            "site_categories":sorted({re.search(r"site=(\w+)",c).group(1) for c in contacts})}

def main():
    p=argparse.ArgumentParser()
    for field in ("source","sf16","sf17","out"):p.add_argument("--"+field,required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"NOVEMBER_BLIND_SOURCE_SHA")
    source=json.loads(raw)
    need(len(source["selected"])==12,"TWELVE_SOURCE_GAMES")
    report={"schema":"c3x018-sf16-sf17-global-TT-value-as-eval-two-horizon-12-game-v1",
      "study_status":"PREREGISTERED_CROSS_VERSION_SAME_ENGINE_FAMILY",
      "source_sha256":SOURCE_SHA,"depths":list(DEPTHS),
      "versions":list(VERSIONS),"cases":[]}
    for orig in source["selected"]:
        w,normal=canonical_engine_world(orig)
        half,full=game_clocks(orig)
        row={"id":orig["id"],"game":orig["source_game_sha256"],
             "halfmove":half,"fullmove":full,"cells":[]}
        for version,engine in (("sf16",a.sf16),("sf17",a.sf17)):
            for depth in DEPTHS:
                item={"version":version,"depth":depth,"status":"NOT_RUN"}
                try:
                    for label,flag in (("baseline",False),("TT_all_value_eval_blocked",True)):
                        first=trial(engine,w,version,depth,flag,half,full)
                        second=trial(engine,w,version,depth,flag,half,full)
                        need(first==second,"ENGINE_NONDETERMINISTIC_"+label)
                        item[label]=first
                    item["changed_bestmove"]=(
                        item["baseline"]["UCI"]["bestmove"]!=
                        item["TT_all_value_eval_blocked"]["UCI"]["bestmove"])
                    item["changed_full_core"]=(
                        item["baseline"]["UCI"]!=item["TT_all_value_eval_blocked"]["UCI"])
                    item["status"]="VALID"
                except (RuntimeError,KeyError,ValueError) as exc:
                    item["status"]="HOLD_FAIL_CLOSED"
                    item["failure"]=type(exc).__name__+":"+str(exc)[:260]
                row["cells"].append(item)
                print("C3X018_CROSS_ENGINE_SOURCE",row["id"],version,depth,item["status"],
                    item.get("changed_bestmove"),item.get("TT_all_value_eval_blocked",{}).get("gate_contact_logged"),
                    flush=True)
        report["cases"].append(row)
    valid=[x for r in report["cases"] for x in r["cells"] if x["status"]=="VALID"]
    need(len(report["cases"])==12 and all(len(r["cells"])==4 for r in report["cases"]),"FULL_DENOMINATOR_LOST")
    all_changed=any(x["changed_bestmove"] for x in valid)
    diffs=[]
    for row in report["cases"]:
      for depth in DEPTHS:
        a1=next((x for x in row["cells"] if x["version"]=="sf16" and x["depth"]==depth and x["status"]=="VALID"),None)
        a2=next((x for x in row["cells"] if x["version"]=="sf17" and x["depth"]==depth and x["status"]=="VALID"),None)
        if a1 and a2 and a1["changed_bestmove"]!=a2["changed_bestmove"]:
            diffs.append({"id":row["id"],"depth":depth,
                         "sf16_changed":a1["changed_bestmove"],"sf17_changed":a2["changed_bestmove"]})
    reach={v+"_"+str(d):sum(x["TT_all_value_eval_blocked"]["gate_contact_logged"]>0
        for x in valid if x["version"]==v and x["depth"]==d)
        for v in VERSIONS for d in DEPTHS}
    summary={"expected_cells":48,"valid_cells":len(valid),
      "changed_bestmove":sum(x["changed_bestmove"] for x in valid),
      "changed_full_core":sum(x["changed_full_core"] for x in valid),
      "gate_reach_by_version_depth":reach,
      "cross_version_effect_differences":diffs,
      "C1_STRUCTURAL":"PASS" if len(valid)==48 else "HOLD",
      "C2_PERTURBATION":"PASS" if all_changed else "FAIL",
      "C3_VERSION_NONIDENTITY":"PASS" if diffs else "FAIL",
      "C4_GATE_REACHED":"PASS" if all(n>0 for n in reach.values()) else "FAIL",
      "C5_FROZEN_DENOMINATOR":"PASS" if len(valid)==48 else "HOLD_FAIL_CLOSED"}
    if len(valid)!=48:
       for x in ("C2_PERTURBATION","C3_VERSION_NONIDENTITY","C4_GATE_REACHED"):summary[x]="HOLD"
    report["summary"]=summary
    report["limits"]=[
      "This is a same-family version comparison not an independent chess engine implementation",
      "SF16 NNUE disabled vs SF17 native NNUE; evaluation baselines are substantially different",
      "Full value-as-eval branch is globally suppressed, not the physical first/8th/24th targeted V reader",
      "No direct TT stored-payload writer-reader identity traced across engine versions",
      "Halfmove/fullmove original, standalone FEN without repetition move stack",
      "No sole TT mediation or chess-concept causal transfer proved"]
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X018_SF16_SF17_SEMANTIC_TT_GATE_NATIVE_RESULT",json.dumps(summary,sort_keys=True),flush=True)
    if len(valid)!=48:raise RuntimeError("C3X018_CROSS_VERSION_FULL_DENOMINATOR_FAIL_CLOSED")
if __name__=="__main__":main()
