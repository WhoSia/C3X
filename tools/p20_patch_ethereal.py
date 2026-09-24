#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path
LOCK="0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"
def one(t,a,b):
 n=t.count(a)
 if n!=1: raise SystemExit(f"ANCHOR {n}")
 return t.replace(a,b,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--variant",choices=["instrument","removal"],required=True);ap.add_argument("--manifest",required=True);a=ap.parse_args()
 r=Path(a.root);head=subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
 if head!=LOCK:raise SystemExit("SOURCE_LOCK_FAIL")
 p=r/"src/search.c";t=p.read_text()
 tok="tt_probe(board->hash, thread->height, &ttMove, &ttValue, &ttEval, &ttDepth, &ttBound)"
 if t.count(tok)!=2:raise SystemExit("TT_CENSUS_DRIFT")
 rem=a.variant=="removal"
 mode='return "REMOVAL";' if rem else 'const char* m=getenv("C3X_PSM_MODE"); return m&&*m?m:"NATIVE";'
 mask='return 1;' if rem else 'const char* m=c3x_psm_mode(); if(!strcmp(m,"MASK_ALL")||!strcmp(m,"MASKED"))return 1; if(!strcmp(site,"MAIN"))return !strcmp(m,"MASK_MAIN")||!strcmp(m,"MASK_MAIN_QSEARCH"); return !strcmp(m,"MASK_QSEARCH")||!strcmp(m,"MASK_MAIN_QSEARCH");'
 h=f"""
static unsigned long long c3xp_pm=0,c3xp_pq=0,c3xp_hm=0,c3xp_hq=0,c3xp_mm=0,c3xp_mq=0;
static const char* c3x_psm_mode(void){{ {mode} }}
static int c3x_psm_mask(const char* site){{ {mask} }}
static void c3x_psm_probe(const char* site,int* hit,uint16_t* mv,int* val,int* ev,int* dep,int* bd){{
 int m=!strcmp(site,"MAIN"); if(m)c3xp_pm++;else c3xp_pq++; int raw=*hit; if(raw){{if(m)c3xp_hm++;else c3xp_hq++;}}
 if(c3x_psm_mask(site)){{if(raw){{if(m)c3xp_mm++;else c3xp_mq++;}} *hit=0;*mv=NONE_MOVE;*val=0;*ev=VALUE_NONE;*dep=0;*bd=0;}}
}}
static void c3x_psm_emit(void){{printf("info string c3x_psm_v1 mode=%s probes_main=%llu hits_main=%llu masked_main=%llu probes_qsearch=%llu hits_qsearch=%llu masked_qsearch=%llu\\n",c3x_psm_mode(),c3xp_pm,c3xp_hm,c3xp_mm,c3xp_pq,c3xp_hq,c3xp_mq);}}
"""
 t=one(t,"volatile int ANALYSISMODE; // Whether to make some changes for Analysis","volatile int ANALYSISMODE; // Whether to make some changes for Analysis"+h)
 old=f"    if ((ttHit = {tok})) {{"
 if t.count(old)!=2: raise SystemExit(f"TT_SITE_ANCHOR_DRIFT {t.count(old)}")
 main_rep=f"""    ttHit = {tok};
    c3x_psm_probe("MAIN",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (ttHit) {{"""
 q_rep=f"""    ttHit = {tok};
    c3x_psm_probe("QSEARCH",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (ttHit) {{"""
 t=t.replace(old,main_rep,1)
 t=one(t,old,q_rep)
 x="""    // Report best move ( we should always have one )
    moveToString(best, str, board->chess960);"""
 y="""    // Report best move ( we should always have one )
    c3x_psm_emit();
    moveToString(best, str, board->chess960);"""
 t=one(t,x,y)
 p.write_text(t);subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p20-adapter-v1","engine":"ethereal","variant":a.variant,"source_commit":head,"raw_probe_calls_total":2,"scoped":{"MAIN":1,"QSEARCH":1},"excluded":[],"complete_scoped_mediation":True}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2)+"\n");print(json.dumps(m))
if __name__=="__main__":main()
