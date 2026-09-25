#!/usr/bin/env python3
import argparse,json,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}
def one(t,a,b,label):
 n=t.count(a)
 if n!=1: raise SystemExit(f"{label}_ANCHOR_{n}")
 return t.replace(a,b,1)
def head(r):return subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
def install(root,name):
 dst=root/"src"/"c3x_p30_victim.inc";shutil.copyfile(ROOT/"tools"/name,dst);return str(dst.relative_to(root))

def stockfish(root):
 inc=install(root,"p30_victim_stockfish.inc")
 p=root/"src"/"tt.cpp";t=p.read_text()
 t=one(t,'static_assert(sizeof(Cluster) == 32, "Suboptimal Cluster size");',
       'static_assert(sizeof(Cluster) == 32, "Suboptimal Cluster size");\n\n#include "c3x_p30_victim.inc"',"SF_INC")
 t=one(t,'            c3x_probe_result(&tte[i],key,occupied);',
       '            c3x_probe_result(&tte[i],key,occupied);\n            c3x_p30_hit(&tte[i],key);',"SF_HIT")
 t=one(t,'    c3x_loc(replace,c3xBucket,int(replace-tte));\n    return {false,',
       '    c3x_loc(replace,c3xBucket,int(replace-tte));\n    c3x_p30_victim(key,tte,replace,c3xBucket,generation8);\n    return {false,',"SF_VICTIM")
 p.write_text(t);return {"include":inc,"file":"src/tt.cpp"}

def berserk(root):
 inc=install(root,"p30_victim_berserk.inc")
 h=root/"src"/"transposition.h";t=h.read_text()
 t=one(t,'void c3x_tt_trace_age(TTEntry* e, uint64_t requested, uint8_t oldv, uint8_t newv);',
       'void c3x_tt_trace_age(TTEntry* e, uint64_t requested, uint8_t oldv, uint8_t newv);\nvoid c3x_p30_hit(uint64_t hash, TTEntry* e);\nvoid c3x_p30_victim(uint64_t requested, TTEntry* bucket, TTEntry* actual);',"BE_PROTO")
 t=one(t,'      c3x_tt_trace_probe_result(hash,&bucket[i],*hit);',
       '      c3x_tt_trace_probe_result(hash,&bucket[i],*hit);\n      c3x_p30_hit(hash,&bucket[i]);',"BE_HIT")
 t=one(t,'  c3x_tt_trace_probe_result(hash,replace,0);\n  return replace;',
       '  c3x_tt_trace_probe_result(hash,replace,0);\n  c3x_p30_victim(hash,bucket,replace);\n  return replace;',"BE_VICTIM")
 h.write_text(t)
 c=root/"src"/"transposition.c";u=c.read_text()
 u=one(u,'#include "c3x_p29_trace.inc"','#include "c3x_p29_trace.inc"\n#include "c3x_p30_victim.inc"',"BE_INC")
 c.write_text(u);return {"include":inc,"files":["src/transposition.h","src/transposition.c"]}

def ethereal(root):
 inc=install(root,"p30_victim_ethereal.inc")
 p=root/"src"/"transposition.c";t=p.read_text()
 t=one(t,'#include "c3x_p29_trace.inc"','#include "c3x_p29_trace.inc"\n#include "c3x_p30_victim.inc"',"ET_INC")
 # applies in either P29 age policy branch
 t=one(t,'            c3x_et_probe_result(hash,&slots[i],1,c3xOccupied);',
       '            c3x_et_probe_result(hash,&slots[i],1,c3xOccupied);\n            c3x_p30_hit(hash,&slots[i]);',"ET_HIT")
 t=one(t,'    replace = (i != TT_BUCKET_NB) ? &slots[i] : replace;\n\n    // Don\'t overwrite an entry',
       '    replace = (i != TT_BUCKET_NB) ? &slots[i] : replace;\n    c3x_p30_victim(hash,slots,replace,i != TT_BUCKET_NB);\n\n    // Don\'t overwrite an entry',"ET_VICTIM")
 p.write_text(t);return {"include":inc,"file":"src/transposition.c"}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":stockfish,"berserk":berserk,"ethereal":ethereal}[a.engine](r)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p30-victim-instrument-v1","scientific_stage":"C3X 0.7.0-G9.4-P30","engine":a.engine,
    "source_commit":h,"events":["V victim eligibility","H exact full-key hit"],"semantic_intervention":False,"edit":edit}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
