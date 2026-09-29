#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

LOCKS={
 "stockfish_19":"edb0d9db6731067ec50ce619ff372b463bc4dd5d",
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}

HELPER=r'''
/* C3X G9.5-P11: bounded repeat-key/same-move move-order patch. */
#define C3X_P11_SEEN_N 1048576
static unsigned long long c3x_p11_key[C3X_P11_SEEN_N];
static unsigned long long c3x_p11_move[C3X_P11_SEEN_N];
static unsigned char c3x_p11_used[C3X_P11_SEEN_N];
static int c3x_p11_mode_init=0;
static char c3x_p11_mode[8]="NONE";

static void c3x_p11_setup(void){
  if(c3x_p11_mode_init)return;
  c3x_p11_mode_init=1;
  const char *m=getenv("C3X_P11_PATCH");
  if(m&&*m)snprintf(c3x_p11_mode,sizeof(c3x_p11_mode),"%s",m);
  if(strcmp(c3x_p11_mode,"NONE")&&strcmp(c3x_p11_mode,"LOWER")&&
     strcmp(c3x_p11_mode,"UPPER")&&strcmp(c3x_p11_mode,"BOTH")){
    fprintf(stderr,"C3X_P11_BAD_PATCH %s\n",c3x_p11_mode);abort();
  }
}
static int c3x_p11_mediator_all(void){
  const char *x=getenv("C3X_P11_MEDIATOR_ALL");
  return x&&*x&&!strcmp(x,"1");
}
static int c3x_p11_bound_match(int bound){
  if(!strcmp(c3x_p11_mode,"BOTH"))return bound==1||bound==2;
  if(!strcmp(c3x_p11_mode,"UPPER"))return bound==1;
  if(!strcmp(c3x_p11_mode,"LOWER"))return bound==2;
  return 0;
}
static int c3x_p11_repeat_same(unsigned long long key,unsigned long long move){
  unsigned long long h=(key^(key>>33)^(key>>17))&(C3X_P11_SEEN_N-1);
  for(unsigned long long j=0;j<C3X_P11_SEEN_N;j++){
    unsigned long long i=(h+j)&(C3X_P11_SEEN_N-1);
    if(!c3x_p11_used[i]){
      c3x_p11_used[i]=1;c3x_p11_key[i]=key;c3x_p11_move[i]=move;return 0;
    }
    if(c3x_p11_key[i]==key){
      int same=c3x_p11_move[i]==move;
      c3x_p11_move[i]=move;
      return same;
    }
  }
  fprintf(stderr,"C3X_P11_SEEN_OVERFLOW\n");abort();
}
static int c3x_p11_patch_block(const char *scope,int cls,unsigned long long key,int ply,int depth,int bound,unsigned long long move){
  c3x_p11_setup();
  if(!c3x_p32_measurement())return 0;
  int repeat_same=c3x_p11_repeat_same(key,move);
  if(!strcmp(c3x_p11_mode,"NONE"))return 0;
  return cls==1 && !strcmp(scope,"MAIN") && ply==1 && depth>=5 && depth<=8 &&
         move!=0 && repeat_same && c3x_p11_bound_match(bound);
}
'''

def head(root):
 return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",required=True)
 ap.add_argument("--engine",choices=LOCKS,required=True)
 ap.add_argument("--manifest",required=True)
 a=ap.parse_args();root=Path(a.root);h=head(root)
 if h!=LOCKS[a.engine]:raise SystemExit(f"P11_SOURCE_LOCK {h}")
 p=root/"src"/"c3x_p34_cone.inc"
 if not p.exists():raise SystemExit("P11_REQUIRES_P34_CONE")
 s=p.read_text()
 anchor="static int c3x_p34_block(const char *scope"
 if s.count(anchor)!=1:raise SystemExit(f"P11_BLOCK_ANCHOR_{s.count(anchor)}")
 s=s.replace(anchor,HELPER+"\n"+anchor,1)
 seed_anchor="  int seed=c3x_p32_block(scope,cls,key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload);"
 seed_new=seed_anchor+"\n  int p11=c3x_p11_patch_block(scope,cls,key,ply,depth,bound,move);"
 if s.count(seed_anchor)!=1:raise SystemExit(f"P11_SEED_ANCHOR_{s.count(seed_anchor)}")
 s=s.replace(seed_anchor,seed_new,1)
 old_gate="  if(!c3x_p32_measurement() || !c3x_p32_family_has(cls))return seed;"
 new_gate="  if(!c3x_p32_measurement() || (!c3x_p32_family_has(cls) && !c3x_p11_mediator_all()))return seed||p11;"
 if s.count(old_gate)!=1:raise SystemExit(f"P11_GATE_ANCHOR_{s.count(old_gate)}")
 s=s.replace(old_gate,new_gate,1)
 old="  return seed||extra;\n}"
 new="  return seed||extra||p11;\n}"
 if s.count(old)!=1:raise SystemExit(f"P11_RETURN_ANCHOR_{s.count(old)}")
 s=s.replace(old,new,1)
 p.write_text(s)
 subprocess.check_call(["git","diff","--check"],cwd=root)
 m={"schema":"c3x-g95-p11-repeatkey-patch-v1","scientific_stage":"C3X 0.7.0-G9.5-P11",
    "engine":a.engine,"source_commit":h,"runtime_modes":["NONE","LOWER","UPPER","BOTH"],
    "semantic_intervention":True,
    "predicate":"measurement-only MAIN MOVE_ORDER_SEED at ply1 depth5..8 with repeated full key, same most-recent TT move and selected bound sign",
    "raw_key_publication":False}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
 Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
