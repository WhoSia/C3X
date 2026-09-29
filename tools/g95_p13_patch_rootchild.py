#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}

INC=r'''#ifndef C3X_P13_ROOTCHILD_INC
#define C3X_P13_ROOTCHILD_INC
#include <stdio.h>
#include <stdlib.h>
static FILE *c3x_p13_rcf=0;
static int c3x_p13_rcinit=0;
static void c3x_p13_rootchild(unsigned long long key,int ply){
  if(ply!=1)return;
  const char *p=getenv("C3X_P13_ROOTCHILD_TRACE");
  if(!p||!*p)return;
  if(!c3x_p13_rcinit){
    c3x_p13_rcinit=1;
    c3x_p13_rcf=fopen(p,"a");
    if(!c3x_p13_rcf){perror("C3X_P13_ROOTCHILD_TRACE");abort();}
  }
  fprintf(c3x_p13_rcf,"K,%016llx\n",key);
  fflush(c3x_p13_rcf);
}
#endif
'''

def head(root):
 return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
def one(s,a,b,label):
 if s.count(a)!=1:raise SystemExit(f"P13_ROOTCHILD_ANCHOR {label} {s.count(a)}")
 return s.replace(a,b,1)

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"P13_ROOTCHILD_HEAD {a.engine} {h}")
 inc=r/"src"/"c3x_p13_rootchild.inc";inc.write_text(INC)
 s=r/"src"/"search.cpp" if a.engine=="stockfish_19" else r/"src"/"search.c"
 txt=s.read_text()
 if a.engine=="stockfish_19":
  txt=one(txt,'#include "c3x_p32_target.inc"','#include "c3x_p32_target.inc"\n#include "c3x_p13_rootchild.inc"',"SF_INC")
  anchor='''    ttData.value = ttHit ? value_from_tt(ttData.value, ss->ply, pos.rule50_count()) : VALUE_NONE;'''
  txt=one(txt,anchor,'''    c3x_p13_rootchild((unsigned long long)posKey,ss->ply);
'''+anchor,"SF_MAIN")
 elif a.engine=="berserk":
  txt=one(txt,'#include "c3x_p32_target.inc"','#include "c3x_p32_target.inc"\n#include "c3x_p13_rootchild.inc"',"BE_INC")
  anchor='''  if (!ss->skip) c3x_psm_probe("MAIN",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);'''
  txt=one(txt,anchor,'''  c3x_p13_rootchild((unsigned long long)board->zobrist,ss->ply);
'''+anchor,"BE_MAIN")
 else:
  txt=one(txt,'#include "c3x_p32_target.inc"','#include "c3x_p32_target.inc"\n#include "c3x_p13_rootchild.inc"',"ET_INC")
  anchor='''    c3x_psm_probe("MAIN",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);'''
  txt=one(txt,anchor,'''    c3x_p13_rootchild((unsigned long long)board->hash,thread->height);
'''+anchor,"ET_MAIN")
 s.write_text(txt)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-g95-p13-rootchild-observer-v1","scientific_stage":"C3X 0.7.0-G9.5-P13","engine":a.engine,
    "behavioral_intervention":False,"private_only":True,
    "semantics":"when C3X_P13_ROOTCHILD_TRACE is set, emit the current engine full position key at main-search ply/height 1; no search state is mutated",
    "raw_key_publication_forbidden":True,"files":[str(inc.relative_to(r)),str(s.relative_to(r))]}
 Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
