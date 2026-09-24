#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path
LOCK="32628515050b83805bab4afa1026dd2bcaa93f55"
def one(t,a,b):
 n=t.count(a)
 if n!=1: raise SystemExit(f"ANCHOR {n}")
 return t.replace(a,b,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--variant",choices=["instrument","removal"],required=True);ap.add_argument("--manifest",required=True);a=ap.parse_args()
 r=Path(a.root); head=subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
 if head!=LOCK: raise SystemExit("SOURCE_LOCK_FAIL")
 p=r/"src/search.c";t=p.read_text()
 if t.count("TTProbe(")!=3: raise SystemExit("TT_CENSUS_DRIFT")
 rem=a.variant=="removal"
 mode='return "REMOVAL";' if rem else 'const char* m=getenv("C3X_PSM_MODE"); return m&&*m?m:"NATIVE";'
 mask='return 1;' if rem else 'const char* m=c3x_psm_mode(); if(!strcmp(m,"MASK_ALL")||!strcmp(m,"MASKED"))return 1; if(!strcmp(site,"MAIN"))return !strcmp(m,"MASK_MAIN")||!strcmp(m,"MASK_MAIN_QSEARCH"); return !strcmp(m,"MASK_QSEARCH")||!strcmp(m,"MASK_MAIN_QSEARCH");'
 h=f"""
static unsigned long long c3xp_pm=0,c3xp_pq=0,c3xp_hm=0,c3xp_hq=0,c3xp_mm=0,c3xp_mq=0;
static const char* c3x_psm_mode(void){{ {mode} }}
static int c3x_psm_mask(const char* site){{ {mask} }}
static void c3x_psm_probe(const char* site,int dpv,int* hit,Move* mv,int* sc,int* ev,int* dep,int* bd,int* pv){{
 int m=!strcmp(site,"MAIN"); if(m)c3xp_pm++;else c3xp_pq++; int raw=*hit; if(raw){{if(m)c3xp_hm++;else c3xp_hq++;}}
 if(c3x_psm_mask(site)){{if(raw){{if(m)c3xp_mm++;else c3xp_mq++;}} *hit=0;*mv=NULL_MOVE;*sc=UNKNOWN;*ev=EVAL_UNKNOWN;*dep=DEPTH_OFFSET;*bd=BOUND_UNKNOWN;*pv=dpv;}}
}}
static void c3x_psm_emit(void){{printf("info string c3x_psm_v1 mode=%s probes_main=%llu hits_main=%llu masked_main=%llu probes_qsearch=%llu hits_qsearch=%llu masked_qsearch=%llu\\n",c3x_psm_mode(),c3xp_pm,c3xp_hm,c3xp_mm,c3xp_pq,c3xp_hq,c3xp_mq);}}
"""
 t=one(t,"int STATIC_PRUNE[2][MAX_SEARCH_PLY];","int STATIC_PRUNE[2][MAX_SEARCH_PLY];"+h)
 x="""  TTEntry* tt =
    ss->skip ? NULL : TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;"""
 y="""  TTEntry* tt =
    ss->skip ? NULL : TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  if (!ss->skip) c3x_psm_probe("MAIN",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;"""
 t=one(t,x,y)
 x="""  TTEntry* tt = TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);

  // TT score pruning"""
 y="""  TTEntry* tt = TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  c3x_psm_probe("QSEARCH",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);

  // TT score pruning"""
 t=one(t,x,y)
 t=one(t,'  printf("bestmove %s", MoveToStr(bestMove, board));','  c3x_psm_emit();\n  printf("bestmove %s", MoveToStr(bestMove, board));')
 p.write_text(t); subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p20-adapter-v1","engine":"berserk","variant":a.variant,"source_commit":head,"raw_probe_calls_total":3,"scoped":{"MAIN":1,"QSEARCH":1},"excluded":[{"kind":"POST_SEARCH_PONDER_REPORT","count":1}],"complete_scoped_mediation":True}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2)+"\n");print(json.dumps(m))
if __name__=="__main__":main()
