from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import chess.pgn

def key(g):
    h=g.headers
    raw="|".join(str(h.get(k,"?")) for k in ("Event","Site","Date","Round","White","Black"))
    return hashlib.sha256(raw.encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pgn",required=True);ap.add_argument("--a",required=True);ap.add_argument("--b",required=True);ap.add_argument("--meta",required=True);a=ap.parse_args()
    A=[];B=[];n=0
    with open(a.pgn,encoding="utf-8",errors="replace") as f:
        while True:
            g=chess.pgn.read_game(f)
            if g is None:break
            n+=1
            (A if int(key(g),16)%2==0 else B).append(g)
    for path,rows in [(a.a,A),(a.b,B)]:
        with open(path,"w",encoding="utf-8") as out:
            for g in rows:
                print(g,file=out,end="\n\n")
    meta={"schema":"c3x-g10-p5-twic-split-v1","games_total":n,"stratum_a":len(A),"stratum_b":len(B),"split_rule":"sha256(Event|Site|Date|Round|White|Black) parity","outcome_fields_used":False}
    Path(a.meta).write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("G10_P5_TWIC_SPLIT",meta)
if __name__=="__main__":main()
