#!/usr/bin/env python3
"""GMBench v0.2 public move-choice reference comparison; not the official grader.
All 25 move-choice tasks, deterministic top-two reference candidate selection.
No expert-point text fed to the product, no benchmark training, no paid model.
Compare actual product's classical default vs NNUE under the same SF16 binary.
"""
import argparse
from collections import Counter
import hashlib
import json
import time
from pathlib import Path
import chess
import chess.engine
from c3x_explain_two_moves import generate,make_markdown

DATA_COMMIT="3f594cc736f85bb3c812b2203a684fb7f0eb9dce"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sign(x):return None if x is None else (x>0)-(x<0)

def audit(data,engine_file,net,out):
    tasks=[json.loads(x) for x in data.read_text().splitlines() if x.strip()]
    if len(tasks)!=70:raise ValueError("GMBench version count")
    tasks=[x for x in tasks if x["task"]["family"]=="move_choice"]
    if len(tasks)!=25:raise ValueError("move choice denominator")
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for item in tasks:
        task=item["task"]
        ref=item["reference"]["position"]
        tid=item["task_id"]
        board=chess.Board(task["fen"])
        if not board.is_valid() or board.is_game_over(claim_draw=False):
            rows.append({"task_id":tid,"status":"INVALID_OR_TERMINAL"});continue
        if chess.Board(ref["fen"]).fen()!=board.fen():raise ValueError("reference FEN mismatch "+tid)
        lines=sorted(ref["lines"],key=lambda x:x["rank"])
        if len(lines)<2:
            rows.append({"task_id":tid,"status":"NO_SECOND_REFERENCE"});continue
        a,b=[board.parse_san(x["move_san"]).uci() for x in lines[:2]]
        if a==b:raise ValueError("duplicate reference candidate "+tid)
        cp=[x["cp_white"] for x in lines[:2]]
        gap=(cp[0]-cp[1])*(1 if board.turn else -1) if all(x is not None for x in cp) and all(x["mate"] is None for x in lines[:2]) else None
        row={"task_id":tid,"audience":task["audience"],"candidates":[a,b],
             "reference_gap_mover_cp":gap,"reference_depths":[x["depth"] for x in lines[:2]],"modes":{}}
        for label,nnue in (("classical",False),("nnue",True)):
            try:
                start=time.monotonic()
                with chess.engine.SimpleEngine.popen_uci(str(engine_file.resolve()),timeout=120) as e:
                    e.configure({"Use NNUE":nnue,"Threads":1,"Hash":16,"EvalFile":str(net.resolve())})
                    report=generate(board,a,b,e)
                elapsed=time.monotonic()-start
                report["evaluation_mode"]=label
                report["engine_sha256"]=sha(engine_file)
                (out/f"{tid}-{label}.json").write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
                (out/f"{tid}-{label}.md").write_text(make_markdown(report),encoding="utf-8")
                # Independent replay of the product's sampled reply and follow-up moves.
                for root in report["root_candidates"]:
                    child=board.copy();child.push_uci(root["move_uci"])
                    for branch in root["opponent_reply_probe"]["reply_lines"]:
                        after=child.copy();after.push_uci(branch["opponent_reply_uci"])
                        move=branch["measured_own_contingent_followup_uci_or_null"]
                        if move:after.push_uci(move)
                gaps=report["candidate_A_minus_B_cp_by_depth_or_null"]
                row["modes"][label]={"status":"OK","gaps":gaps,"signs":{k:sign(v) for k,v in gaps.items()},
                  "caution":report["small_gap_or_mate_caution"],"depth_flip":report["candidate_preference_sign_flipped_across_depths"],
                  "distinct_rule_facts":len(report["contrastive_measured_facts"]["different_measured_facts"]),
                  "reply_counts":[x["opponent_reply_probe"]["sampled_reply_count"] for x in report["root_candidates"]],
                  "wall_seconds":round(elapsed,4)}
            except Exception as err:
                row["modes"][label]={"status":"FAILED","error":type(err).__name__+": "+str(err)}
        row["status"]="OK" if all(x["status"]=="OK" for x in row["modes"].values()) else "INCOMPLETE"
        rows.append(row)
        print("GMBENCH_CASE",json.dumps(row,sort_keys=True),flush=True)
    paired=[r for r in rows if r["status"]=="OK"]
    summaries={}
    for mode in ("classical","nnue"):
        for d in ("8","10"):
            observed=[r for r in paired if r["reference_gap_mover_cp"] is not None and r["reference_gap_mover_cp"]>0 and r["modes"][mode]["signs"][d] is not None]
            summaries[f"{mode}/{d}"]={"strict_reference_agreement":sum(r["modes"][mode]["signs"][d]==1 for r in observed),
              "ties":sum(r["modes"][mode]["signs"][d]==0 for r in observed),"opposite":sum(r["modes"][mode]["signs"][d]==-1 for r in observed),"denominator":len(observed)}
    opposite={}
    for d in ("8","10"):
        finite=[r for r in paired if all(r["modes"][m]["signs"][d] is not None for m in ("classical","nnue"))]
        opposite[d]={"opposite_sign":sum(r["modes"]["classical"]["signs"][d]*r["modes"]["nnue"]["signs"][d]==-1 for r in finite),
            "denominator":len(finite)}
    result={"dataset_commit":DATA_COMMIT,"dataset_sha256":sha(data),"engine_sha256":sha(engine_file),"net_sha256":sha(net),
      "tasks":25,"paired_success":len(paired),"reference_near_equal_count":sum(r.get("reference_gap_mover_cp") is not None and abs(r["reference_gap_mover_cp"])<=20 for r in rows),
      "reference_agreement":summaries,"classical_nnue_opposite":opposite,"rows":rows,
      "scope":"public exposed top-two reference pair diagnostic; SF19 reference vs SF16 finite-depth; no official GMBench grade, no competitor or learner efficacy"}
    (out/"GMBENCH_REFERENCE_AUDIT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GMBENCH_AGGREGATE",json.dumps({k:v for k,v in result.items() if k!="rows"},sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ("data","engine","net","output"):p.add_argument(n,type=Path)
    a=p.parse_args();audit(a.data,a.engine,a.net,a.output)
