#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path
LOCKS={"stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d","berserk":"32628515050b83805bab4afa1026dd2bcaa93f55","ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root)
 h=subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
 if h!=LOCKS[a.engine]:raise SystemExit("SOURCE_LOCK")
 p=r/"src"/"c3x_p32_target.inc";t=p.read_text()
 old='static int c3x_p32_measurement(void){c3x_p32_setup();return c3x_p31_tt_seq()==5ULL;}'
 new='''static int c3x_p32_measurement(void){
  c3x_p32_setup();
  const char *p20=getenv("C3X_P20_FORCE_SEMANTIC_MEASUREMENT");
  if(p20 && !strcmp(p20,"1")) return 1;
  return c3x_p31_tt_seq()==5ULL;
}'''
 if t.count(old)!=1:raise SystemExit("P20_P32_OVERRIDE_ANCHOR")
 p.write_text(t.replace(old,new,1))
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-g10-p20-event-override-v1","stage":"C3X 0.10.0-G10-P20","engine":a.engine,
    "source_commit":h,"purpose":"enable inherited P32 exact event addressing under P20 cold forced-search support protocol","base_semantics_changed":False}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
