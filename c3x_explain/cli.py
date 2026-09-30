#!/usr/bin/env python3
import argparse,json
from .core import analyze_pgn,load_certificates
def main():
 p=argparse.ArgumentParser(description="C3X evidence-aware PGN commentator")
 p.add_argument("pgn");p.add_argument("--engine");p.add_argument("--multipv",type=int,default=3);p.add_argument("--nodes",type=int,default=20000)
 p.add_argument("--certificate",action="append",default=[]);p.add_argument("--threshold-cp",type=int,default=20);p.add_argument("--out")
 a=p.parse_args();text=open(a.pgn,encoding="utf-8").read();certs=load_certificates(a.certificate)
 out=analyze_pgn(text,a.engine,a.multipv,a.nodes,certs,a.threshold_cp);s=json.dumps(out,ensure_ascii=False,indent=2)
 if a.out:open(a.out,"w",encoding="utf-8").write(s+"\n")
 else:print(s)
if __name__=="__main__":main()
