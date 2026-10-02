from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

def binary(root,engine):
    xs=list(Path(root).rglob(f"c3x-p16-{engine}"))
    if len(xs)!=1:raise SystemExit(f"P5_BINARY {engine} {len(xs)}")
    xs[0].chmod(0o755);return xs[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=["qualify","chain-qualify","factorial"],required=True)
    ap.add_argument("--state",required=True);ap.add_argument("--build-dir",required=True)
    ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
    a=ap.parse_args();state=json.load(open(a.state,encoding="utf-8"));cases=state["cases"];done=0
    for i,c in enumerate(cases):
        if i%a.shards!=a.shard:continue
        outdir=Path(a.out_dir)/f"{i:03d}-{c['engine']}";outdir.mkdir(parents=True,exist_ok=True)
        out=outdir/f"{a.phase}.json";cmd=[sys.executable,"harness/g95_p16_court.py",a.phase]
        if a.phase=="qualify":cmd+=["--design",a.state]
        else:cmd+=["--freeze",a.state]
        cmd+=["--case-id",c["case_id"],"--binary",str(binary(a.build_dir,c["engine"])),"--out",str(out)]
        subprocess.run(cmd,check=True);done+=1
    print("G10_P5_SHARD_PASS",a.phase,a.shard,done)
if __name__=="__main__":main()
