#!/usr/bin/env python3
"""R47 product profile court: real pinned SF16 R31-prefix binary, no treatment.
HTTP + CLI, classical/NNUE. Exact file IDs, explicit mode; no learner study.
"""
import argparse
import hashlib
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading

from c3x_explain_two_moves import evaluation_profile, NNUE_SHA256, sha
from c3x_local_web import create_handler

BINARY_SHA="78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb"
START="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
REPEAT="rnbqkb1r/pppppppp/5n2/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 7 4"
HISTORY="g1f3 g8f6 f3g1 f6g8 g1f3 g8f6 f3g1".split()
CASES={"start":{"fen":START,"move_a":"e2e4","move_b":"d2d4"},
       "repeat":{"fen":REPEAT,"move_a":"f6g8","move_b":"f6h5","history":HISTORY}}

def require(ok,reason):
    if not ok:raise ValueError(reason)

def check(prov,mode):
    require(prov["evaluation_mode"]==mode and prov["engine_binary_sha256"]==BINARY_SHA
        and prov["nnue_sha256"]==(NNUE_SHA256 if mode=="nnue" else None)
        and prov["threads"]==1 and prov["hash_mib"]==16
        and not prov["source_build_verified_by_this_call"],"wrong profile receipt")

def http(server,method,path,payload=None):
    conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=120)
    try:
        conn.request(method,path,body=None if payload is None else json.dumps(payload),
                     headers={"Content-Type":"application/json"})
        r=conn.getresponse()
        return r.status,json.loads(r.read())
    finally:conn.close()

def main():
    p=argparse.ArgumentParser()
    for n in ("binary","net","out"):p.add_argument(n,type=Path)
    a=p.parse_args()
    require(sha(a.binary)==BINARY_SHA and sha(a.net)==NNUE_SHA256,"pinned file mismatch")
    a.out.mkdir(parents=True,exist_ok=True)
    rows={}
    for mode in ("classical","nnue"):
        net=a.net if mode=="nnue" else None
        server=ThreadingHTTPServer(("127.0.0.1",0),create_handler(a.binary,mode,net))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            status,health=http(server,"GET","/api/health")
            require(status==200 and health["evaluation_mode"]==mode,"health profile")
            status,_=http(server,"POST","/api/analyze",dict(CASES["start"],evaluation_mode="other"))
            require(status==422,"request override accepted")
            for label,payload in CASES.items():
                status,data=http(server,"POST","/api/analyze",payload)
                require(status==200,"actual HTTP analysis "+str(data)[:200])
                report=data["engine_report"]
                check(data["engine_provenance"],mode);check(report["engine_provenance"],mode)
                require(mode in data["learner_markdown"] and BINARY_SHA in data["learner_markdown"],"markdown provenance missing")
                if label=="repeat":
                    require(report["input_history_ply_count"]==7 and report["root_candidates"][0]["facts"]["threefold_position_after_move"],"history lost")
                prefix=a.out/f"{mode}-{label}"
                cli=[sys.executable,str(Path(__file__).with_name("c3x_explain_two_moves.py")),
                     "--fen",payload["fen"],"--move-a",payload["move_a"],"--move-b",payload["move_b"],
                     "--engine",str(a.binary.resolve()),"--out-json",str(prefix)+".json","--out-md",str(prefix)+".md",
                     "--evaluation-mode",mode]
                if net:cli.extend(["--nnue-file",str(net.resolve())])
                if "history" in payload:cli.extend(["--history"," ".join(payload["history"])])
                subprocess.run(cli,check=True,timeout=120)
                exported=json.loads(Path(str(prefix)+".json").read_text())
                check(exported["engine_provenance"],mode)
                key="candidate_A_minus_B_cp_by_depth_or_null"
                require(exported[key]==report[key],"CLI HTTP evaluation mismatch")
                Path(str(prefix)+"-http.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
                rows[f"{mode}/{label}"]={"gaps":report[key],"history_ply":report["input_history_ply_count"]}
            for path in ("/api/strategy","/api/mirror"):
                status,data=http(server,"POST",path,CASES["start"])
                require(status==200,"adjacent real route "+path)
                check(data["engine_provenance"],mode)
            print("R47_PROFILE_PASS",mode,flush=True)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)
    receipt={"profiles":rows,"native_http_routes":8,"native_cli_reports":4,
             "scope":"real pinned R31-prefix SF16 binary, two input boards, no source treatment; not original unmodified SF16 or explanation quality score"}
    (a.out/"R47_PROFILE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("R47_PROFILE_RECEIPT",json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__":main()
