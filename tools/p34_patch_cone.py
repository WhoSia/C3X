#!/usr/bin/env python3
import argparse,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}
def head(r):return subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True);a=ap.parse_args()
 r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"P34_SOURCE_LOCK {h}")
 dst=r/"src"/"c3x_p34_cone.inc";shutil.copyfile(ROOT/"tools"/"p34_cone_target.inc",dst)
 p=r/"src"/"search.cpp" if a.engine=="stockfish_19" else r/"src"/"search.c"
 s=p.read_text()
 anchor='#include "c3x_p32_target.inc"'
 if s.count(anchor)!=1:raise SystemExit(f"P34_INCLUDE_ANCHOR_{s.count(anchor)}")
 s=s.replace(anchor,anchor+'\n#include "c3x_p34_cone.inc"',1)
 n=s.count("c3x_p32_block(")
 if n<3:raise SystemExit(f"P34_BLOCK_SITE_COUNT_{n}")
 s=s.replace("c3x_p32_block(","c3x_p34_block(")
 p.write_text(s)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p34-dynamic-cone-variant-v1","scientific_stage":"C3X 0.7.0-G9.4-P34","engine":a.engine,
    "source_commit":h,"wrapped_p32_block_sites":n,"quotient_levels":["Q0","Q1","Q2","Q3"],
    "modes":["BASE","CATALOG","SEED_ONLY","REMOVE_ALL","REMOVE_SET","KEEP_SET"],
    "semantic_intervention":"P33 exact seed removal plus dynamic finite quotient predicates at TT semantic-use sites during measurement search only; TT storage/replacement/index/age untouched"}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
