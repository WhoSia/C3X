#!/usr/bin/env python3
"""P35/R5 source-eval routing court. Exposed roots only; not neural mediation proof."""
import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path
import chess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_029_p35_r5_source_dispatch_probe import parse_route_log
from c3x_029_p32_original_history_reply_value_native import (
    replay_original, FROZEN_SOURCE_SHA256
)
P34_SHA = "c80704f2f81c4920597fbf6b559ef38dbae60f35458c7a2f665f1cf57d2563dc"

def must(ok, label):
    if not ok: raise ValueError("P35_R5_HOLD_" + label)

def digest(data): return hashlib.sha256(data).hexdigest()

def analysis_fingerprint(lines):
    infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
    must(bool(infos), "MISSING_SCORE_PV")
    last=infos[-1]
    nodes=re.search(r"\bnodes (\d+)\b",last)
    score=re.search(r"\bscore (cp|mate) (-?\d+)\b",last)
    pv=re.search(r"\bpv ([a-h][1-8][a-h][1-8][qrbn]?(?: [a-h][1-8][a-h][1-8][qrbn]?)*)",last)
    must(nodes is not None and score is not None and pv is not None,"INCOMPLETE_SEARCH_FINGERPRINT")
    return {"nodes":int(nodes.group(1)), "score_type":score.group(1),
            "score":int(score.group(2)), "pv":pv.group(1).split()}

def run_once(engine, history, root, nodes, log_mode, timeout=120):
    env=dict(os.environ)
    env.pop("C3X_P35_ROUTE_AUDIT",None)
    if log_mode:env["C3X_P35_ROUTE_AUDIT"]="1"
    with tempfile.TemporaryFile(mode="w+t",encoding="utf-8") as errors:
        process=subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                 stderr=errors,text=True,bufsize=1,env=env)
        lines=[]
        def issue(command):
            process.stdin.write(command+"\n")
            process.stdin.flush()
        def until(marker):
            while True:
                line=process.stdout.readline()
                must(bool(line),"ENGINE_EOF_"+marker)
                line=line.rstrip("\n")
                lines.append(line)
                if line.startswith(marker):return line
        def on_alarm(signum,frame):
            raise TimeoutError("P35_R5_ENGINE_TIMEOUT")
        old=signal.signal(signal.SIGALRM,on_alarm)
        signal.alarm(timeout)
        try:
            issue("uci")
            until("uciok")
            must("id name Stockfish 16" in lines,"ENGINE_NOT_PINNED_SF16_NAME")
            issue("setoption name Threads value 1")
            issue("setoption name Hash value 16")
            issue("setoption name Use NNUE value true")
            issue("ucinewgame")
            issue("isready")
            until("readyok")
            issue("position startpos moves "+" ".join(history))
            if root is None:
                issue(f"go nodes {nodes}")
            elif isinstance(root, (tuple, list)):
                must(len(root) >= 2 and len(set(root)) == len(root), "INVALID_PAIR_ROOTS")
                issue(f"go searchmoves {' '.join(root)} nodes {nodes}")
            else:
                issue(f"go searchmoves {root} nodes {nodes}")
            best=until("bestmove ")
            issue("quit")
            process.wait(timeout=10)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM,old)
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
        must(process.returncode==0,"ENGINE_EXIT_NONZERO")
        errors.seek(0)
        raw=errors.read()
        routes=parse_route_log(raw)
        must(bool(routes)==log_mode,"EVALUATOR_LOG_PRESENCE")
        return {"bestmove":best.split()[1],
                "final_info":analysis_fingerprint(lines),
                "route_count":len(routes),
                "route_by_arm":{arm:sum(r["arm"]==arm for r in routes)
                                for arm in ("NNUE","HCE")},
                "route_unique_keys":len({r["key"] for r in routes}),
                "stderr_sha256":digest(raw.encode()),
                "stdout_sha256":digest(("\n".join(lines)+"\n").encode())}

def court(source_path,p34_path,vanilla,instrumented,nodes):
    source_raw=Path(source_path).read_bytes()
    search_raw=Path(p34_path).read_bytes()
    must(digest(source_raw)==FROZEN_SOURCE_SHA256,"SOURCE_SHA")
    must(digest(search_raw)==P34_SHA,"P34_SHA")
    source=json.loads(source_raw)
    prior=json.loads(search_raw)
    cases={x["id"]:x for x in source["selected"]}
    must(len(prior["records"])==4,"ROOT_COUNT")
    records=[]
    root_groups={}
    for candidate in prior["records"]:
        root_groups.setdefault(candidate["case_id"], []).append(candidate["root_uci"])
    must(len(root_groups)==2 and all(len(set(roots))==2 for roots in root_groups.values()),"CASE_ROOT_GROUPS")
    for candidate in prior["records"]:
        c=cases[candidate["case_id"]]
        board=replay_original(c)
        root=chess.Move.from_uci(candidate["root_uci"])
        must(root in board.legal_moves,"ROOT_ILLEGAL")
        history=c["full_original_mainline_uci"][:c["source_ply_before_original_move"]]
        normal=run_once(vanilla,history,candidate["root_uci"],nodes,False)
        probed=run_once(instrumented,history,candidate["root_uci"],nodes,True)
        parity=normal["bestmove"]==probed["bestmove"] and normal["final_info"]==probed["final_info"]
        records.append({"case_id":candidate["case_id"],"root":candidate["root_uci"],
                        "arm":"forced_one", "allowed_roots":[candidate["root_uci"]],
                        "natural_choice_evidence":False,
                        "parity":parity,"vanilla":normal,"probed":probed})
        print("P35_R5_SEARCH",candidate["case_id"],candidate["root_uci"],
              "parity=",parity,"evals=",probed["route_by_arm"],flush=True)
    for case_id, roots in sorted(root_groups.items()):
        case=cases[case_id]
        board=replay_original(case)
        must(all(chess.Move.from_uci(move) in board.legal_moves for move in roots),
             "PAIR_ROOT_ILLEGAL")
        history=case["full_original_mainline_uci"][:case["source_ply_before_original_move"]]
        for arm, allowed in (("pair",roots),("unrestricted",None)):
            normal=run_once(vanilla,history,allowed,nodes,False)
            probed=run_once(instrumented,history,allowed,nodes,True)
            parity=normal["bestmove"]==probed["bestmove"] and normal["final_info"]==probed["final_info"]
            if arm=="pair":
                must(normal["bestmove"] in roots,"PAIR_BESTMOVE_NOT_ALLOWED")
            else:
                must(chess.Move.from_uci(normal["bestmove"]) in board.legal_moves,
                     "UNRESTRICTED_BESTMOVE_ILLEGAL")
            records.append({"case_id":case_id,"root":None,
                            "arm":arm,"allowed_roots":allowed,
                            "natural_choice_evidence":arm=="unrestricted",
                            "third_candidate":arm=="unrestricted" and normal["bestmove"] not in roots,
                            "parity":parity,"vanilla":normal,"probed":probed})
            print("P35_R6_COMPETITION",case_id,arm,"parity=",parity,
                  "bestmove=",normal["bestmove"],
                  "evals=",probed["route_by_arm"],flush=True)
    must(len(records)==8,"EXPECTED_EIGHT_ROOT_ARMS")
    must(all(r["parity"] for r in records),"SOURCE_INSTRUMENTATION_PARITY")
    return {"status":"P35_R6_THREE_ARM_NATIVE_DISPATCH_PARITY_PASS_NOT_CAUSAL_MEDIATION",
            "claim_ceiling":"Actual HCE/NNUE dispatch + forced, pair and unrestricted root parity. No causal neural mediator or explanation superiority.",
            "requested_nodes":nodes,"game_disjoint_heldout":False,"records":records}

def main():
    parser=argparse.ArgumentParser()
    for key in ("source","p34","vanilla","instrumented","out"):
        parser.add_argument("--"+key,required=True)
    parser.add_argument("--nodes",type=int,default=24000)
    args=parser.parse_args()
    must(0<args.nodes<=100000,"NODE_BUDGET")
    result=court(args.source,args.p34,args.vanilla,args.instrumented,args.nodes)
    Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

if __name__=="__main__":main()
