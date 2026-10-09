#!/usr/bin/env python3
"""C3X018 #6/#8 exploratory native physical TT lineage and selective factorial court.

Pre-existing case selection (#6/#8) and root-order treatments are frozen.
TT event selection from this tranche is exploratory, NOT a pre-registered mediator.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

FIELDS = ("bestmove", "score_kind", "score_value", "score_flag", "nodes", "pv")
FOCAL = (6, 8)
SOURCE_SELECTION = "08bf2179e141ba6a862314660298fa90fa61c3d377e46accc07bd4c5d9cacae2"

def need(test, label):
    if not test:
        raise RuntimeError("C3X018_PHYSICAL_COURT_" + label)

def parse_fields(line):
    return dict(p.split("=", 1) for p in line.split()[3:] if "=" in p)

def core(raw):
    rows = []
    for line in raw:
        if line.startswith("info depth 12 ") and " pv " in line:
            value = re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?", line)
            nodes = re.search(r"\bnodes (\d+)", line)
            if value and nodes:
                rows.append(dict(score_kind=value.group(1),
                    score_value=int(value.group(2)), score_flag=value.group(3) or "exact_reported",
                    nodes=int(nodes.group(1)), pv=line.split(" pv ",1)[1].split()[:16]))
    need(rows, "MISSING_DEPTH12_SCORE")
    best = [x.split()[1] for x in raw if x.startswith("bestmove ")]
    need(len(best)==1 and best[0]==rows[-1]["pv"][0], "MISSING_BESTMOVE")
    return {"bestmove":best[0],**rows[-1]}

def play(engine, world, p4_mode, lineage_mode=None, target=None):
    env = dict(os.environ)
    for name in ("C3X018_TT_MODE", "C3X018_TT_TARGET_KEY64",
                 "C3X018_TT_TARGET_SLOT", "C3X018_TT_TARGET_EPOCH",
                 "C3X018_TT_LOG_WRITES"):
        env.pop(name,None)
    if lineage_mode is not None:
        env.update(C3X016_P4_MODE=p4_mode,C3X016_P4_FEN4=world["fen4"],
                   C3X016_P4_PLAYED_NATIVE=str(world["native_move"]),
                   C3X018_TT_MODE=lineage_mode)
        if target:
            env.update(C3X018_TT_TARGET_KEY64=str(target["key64"]),
                       C3X018_TT_TARGET_SLOT=str(target["slot"]),
                       C3X018_TT_TARGET_EPOCH=str(target["epoch"]))
    lines=[]
    with subprocess.Popen([engine], stdin=subprocess.PIPE,
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
          env=env,text=True,bufsize=1) as proc:
        def send(*commands):
            proc.stdin.write("\n".join(commands)+"\n");proc.stdin.flush()
        def receive(marker,cap):
            for _ in range(cap):
                line=proc.stdout.readline()
                need(bool(line),"PREMATURE_EOF_"+marker)
                lines.append(line.rstrip("\n"))
                if line.startswith(marker):return
            raise RuntimeError("C3X018_UCI_LINE_CAP_"+marker)
        send("uci");receive("uciok",100)
        send("setoption name Threads value 1",
             "setoption name Hash value 16",
             "setoption name MultiPV value 1",
             "setoption name Use NNUE value false",
             "ucinewgame","isready")
        receive("readyok",100)
        send("position fen "+world["fen4"]+" 0 1","go depth 12")
        receive("bestmove ",120000)
        send("quit")
        need(proc.wait(timeout=50)==0,"NATIVE_NONZERO_EXIT")
    result=core(lines)
    if lineage_mode is None: return {"UCI":result}
    events=[]
    for line in lines:
        if line.startswith("info string c3x018_lineage "):
            evt=parse_fields(line)
            events.append({k:(v if k in ("kind","site") else int(v)) for k,v in evt.items()})
    need(events, "NO_LINEAGE_EVENTS")
    need(not any(x["kind"]=="trace_censored" for x in events), "TRACE_CENSORED")
    roots=[parse_fields(x) for x in lines if x.startswith("info string c3x016_p4_root_order ")]
    need(len(roots)==1 and roots[0]["mode"]==p4_mode,"P4_ROOT_CONTACT_MISSING")
    return {
       "UCI":result,
       "lineage_summary":{
           "records":len(events),
           "consumer_reached":sum(e["kind"]=="consumer_reached" for e in events),
           "writer_block":sum(e["kind"]=="writer_block" for e in events),
           "reader_block":sum(e["kind"]=="reader_block" for e in events),
           "exact_key_consumers":sum(e["kind"]=="consumer_reached" and
                                      e.get("key_match")==1 for e in events),
           "key16_or_unknown_consumers":sum(e["kind"]=="consumer_reached" and
                                      e.get("key_match")==0 for e in events)
       },
       "consumer_records":[e for e in events if e["kind"]=="consumer_reached"],
       "blocks":[e for e in events if e["kind"] in ("writer_block","reader_block")],
       "root_contact":roots[0]}

def stable(t):
    return json.dumps(t,sort_keys=True,separators=(",",":"))

def select_candidate(O,F):
    # Predeclared algorithm, determined without observing ANY treatment output.
    o={(e["key64"],e["slot"],e["epoch"]) for e in O
        if e["kind"]=="consumer_reached" and e["key_match"]==1 and e["epoch"]>0}
    good=[e for e in F if e["kind"]=="consumer_reached" and
          e["key_match"]==1 and e["epoch"]>0 and 0<=e["slot"]<3]
    novel=[e for e in good if (e["key64"],e["slot"],e["epoch"]) not in o]
    pool=novel if novel else good
    if not pool:return None, "NO_EXACT_KEY_WRITER_CONSUMER"
    first=pool[0]
    return {k:first[k] for k in ("key64","slot","epoch")}, \
           ("FIRST_F_UNIQUE_EXACT_KEY_CONSUMER" if novel
            else "FIRST_F_EXACT_KEY_CONSUMER_NO_UNIQUE_CONTRAST")

def main():
    p=argparse.ArgumentParser()
    for field in ("cohort","prior","original","patched","out"):
        p.add_argument("--"+field,required=True)
    args=p.parse_args()
    data=json.loads(Path(args.cohort).read_text())
    need(data["original_private_12_source_only_selection_sha256"]==SOURCE_SELECTION,
         "FROZEN_SELECTION_MISMATCH")
    old=json.loads(Path(args.prior).read_text())
    need(old["new_native_processes"]==72,"PRIOR_NATIVE_SIZE")
    result={"schema":"c3x018-natural-physical-TT-lineage-6-8-exploratory-factorial-v1",
            "prior_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
            "cohort_sha256":hashlib.sha256(Path(args.cohort).read_bytes()).hexdigest(),
            "source_only":True,"cases":[],
            "scope":"actual main/qsearch TT cutoff branch, not other TT uses",
            "status":"NATIVE_EXPLORATORY_NOT_UNIQUE_CAUSAL_MEDIATION"}
    for case_id in FOCAL:
        world=data["selected"][case_id-1]
        need(world["id"]==case_id,"FOCAL_CASE_INDEX")
        historical=old["worlds"][case_id-1]["cells"]
        original=play(args.original,world,"O")
        need(original["UCI"]==historical["O"]["UCI"],"UNMODIFIED_P4_SHAM")
        controls={}
        for arm in ("O","F","Z"):
            a=play(args.patched,world,arm,"OBS")
            b=play(args.patched,world,arm,"OBS")
            need(a==b,"COLD_OBSERVER_REPLAY_ID_"+str(case_id)+"_"+arm)
            need(a["UCI"]==historical[arm]["UCI"],"P4_NONINTERFERENCE_"+str(case_id)+"_"+arm)
            controls[arm]=a
        need(controls["O"]["UCI"]==controls["Z"]["UCI"],"NO_CONTACT_NOT_EQUAL")
        need(controls["O"]["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"],
             "HISTORICAL_FLIP_NOT_REPRODUCED")
        target,basis=select_candidate(controls["O"]["consumer_records"],
                                      controls["F"]["consumer_records"])
        row={"id":case_id,
             "prior_output":{arm:controls[arm]["UCI"] for arm in controls},
             "observer":{arm:controls[arm]["lineage_summary"] for arm in controls},
             "target_selection":basis,"target":target,
             "target_design":"EXPLORATORY_F_ONLY_SELECTION_NOT_INDEPENDENT_PREREGISTRATION",
             "interventions":{}}
        if target:
            for treatment in ("W","R","WR"):
                a=play(args.patched,world,"F",treatment,target)
                b=play(args.patched,world,"F",treatment,target)
                need(a==b,"COLD_FACTORIAL_"+str(case_id)+"_"+treatment)
                expected_w=treatment in ("W","WR")
                expected_r=treatment in ("R","WR")
                w=a["lineage_summary"]["writer_block"]
                r=a["lineage_summary"]["reader_block"]
                row["interventions"][treatment]={
                    "UCI":a["UCI"],"observer":a["lineage_summary"],
                    "writer_contact":w,"reader_contact":r,
                    "relative_to_F":{
                      "bestmove_changed":a["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"],
                      "score_or_bound_changed":tuple(a["UCI"][k] for k in ("score_kind","score_value","score_flag"))!=tuple(
                          controls["F"]["UCI"][k] for k in ("score_kind","score_value","score_flag")),
                      "nodes_changed":a["UCI"]["nodes"]!=controls["F"]["UCI"]["nodes"]},
                    "arm_contact_status":("CONTACT" if ((not expected_w or w>0) and
                                        (not expected_r or r>0)) else "PARTIAL_OR_NOT_FIRED"),
                    "sample_block_events":a["blocks"][:5]}
                print("C3X018",case_id,treatment,"contact",w,r,
                      "bestmove",a["UCI"]["bestmove"],flush=True)
        result["cases"].append(row)
        print("C3X018_SOURCE_LINEAGE",case_id,"target",basis,
              "observed_consumers",row["observer"]["F"]["consumer_reached"],flush=True)
    result["limitations"]=[
        "Intervention key/slot/epoch selected on treated F observation, not on independent cohort",
        "Slot epoch is per-slot accepted payload-write ordinal after native TT clear",
        "Writer source ablation may also prevent move16 update; not an isolated score mediator",
        "W and R blocking do not test unique natural mediation; other TT uses remain active",
        "Writer suppression may alter future epoch numbering; missing contact is not an effect",
        "Only cases 6 and 8, standalone FEN, SF16 single-thread depth12",
        "Censor gate rejects missing full lineage event buffer",
        "No source-exact rescue; no human chess tactical proof"
    ]
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_LINEAGE_FACTORIAL_NATIVE_EVIDENCE_MATERIALIZED",flush=True)

if __name__=="__main__":
    main()
