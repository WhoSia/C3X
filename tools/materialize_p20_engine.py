#!/usr/bin/env python3
import argparse,json
from pathlib import Path

LOCKS={
    "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
    "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
}

def replace_once(text,old,new,label):
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {n}")
    return text.replace(old,new,1)

def helper_berserk(variant):
    removal = variant=="removal"
    mask_body = 'return 1;' if removal else r'''const char* m=c3x_psm_mode();
  if (!strcmp(m,"MASK_ALL") || !strcmp(m,"MASKED")) return 1;
  if (!strcmp(site,"MAIN"))
    return !strcmp(m,"MASK_MAIN") || !strcmp(m,"MASK_MAIN_QSEARCH");
  return !strcmp(m,"MASK_QSEARCH") || !strcmp(m,"MASK_MAIN_QSEARCH");'''
    mode_body = 'return "REMOVAL";' if removal else r'''const char* m=getenv("C3X_PSM_MODE");
  return m && *m ? m : "NATIVE";'''
    return f'''
static unsigned long long c3x_psm_probes_main=0, c3x_psm_probes_qsearch=0;
static unsigned long long c3x_psm_hits_main=0, c3x_psm_hits_qsearch=0;
static unsigned long long c3x_psm_masked_main=0, c3x_psm_masked_qsearch=0;

static const char* c3x_psm_mode(void) {{
  {mode_body}
}}

static int c3x_psm_should_mask(const char* site) {{
  {mask_body}
}}

static void c3x_psm_after_probe(const char* site, int defaultPv, int* hit, Move* move,
                                int* score, int* eval, int* depth, int* bound, int* pv) {{
  const int isMain=!strcmp(site,"MAIN");
  if (isMain) c3x_psm_probes_main++; else c3x_psm_probes_qsearch++;
  const int raw=*hit;
  if (raw) {{ if (isMain) c3x_psm_hits_main++; else c3x_psm_hits_qsearch++; }}
  if (c3x_psm_should_mask(site)) {{
    if (raw) {{ if (isMain) c3x_psm_masked_main++; else c3x_psm_masked_qsearch++; }}
    *hit=0; *move=NULL_MOVE; *score=UNKNOWN; *eval=EVAL_UNKNOWN;
    *depth=DEPTH_OFFSET; *bound=BOUND_UNKNOWN; *pv=defaultPv;
  }}
}}

static void c3x_psm_emit(void) {{
  printf("info string c3x_psm_v1 mode=%s probes_main=%llu hits_main=%llu masked_main=%llu probes_qsearch=%llu hits_qsearch=%llu masked_qsearch=%llu\\n",
         c3x_psm_mode(), c3x_psm_probes_main, c3x_psm_hits_main, c3x_psm_masked_main,
         c3x_psm_probes_qsearch, c3x_psm_hits_qsearch, c3x_psm_masked_qsearch);
}}
'''

def patch_berserk(root,variant):
    p=root/"src/search.c"; t=p.read_text()
    total=t.count("TTProbe(")
    if total!=3:
        raise RuntimeError(f"berserk TTProbe census drift: expected 3, found {total}")
    anchor="int STATIC_PRUNE[2][MAX_SEARCH_PLY];"
    t=replace_once(t,anchor,anchor+helper_berserk(variant),"berserk helper")
    main_old='''  TTEntry* tt =
    ss->skip ? NULL : TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;'''
    main_new='''  TTEntry* tt =
    ss->skip ? NULL : TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  if (!ss->skip)
    c3x_psm_after_probe("MAIN", isPV, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;'''
    t=replace_once(t,main_old,main_new,"berserk MAIN")
    q_old='''  TTEntry* tt = TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);

  // TT score pruning'''
    q_new='''  TTEntry* tt = TTProbe(board->zobrist, ss->ply, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);
  c3x_psm_after_probe("QSEARCH", isPV, &ttHit, &hashMove, &ttScore, &ttEval, &ttDepth, &ttBound, &ttPv);

  // TT score pruning'''
    t=replace_once(t,q_old,q_new,"berserk QSEARCH")
    best='''  printf("bestmove %s", MoveToStr(bestMove, board));'''
    t=replace_once(t,best,'''  c3x_psm_emit();
  printf("bestmove %s", MoveToStr(bestMove, board));''',"berserk telemetry")
    p.write_text(t)
    return {
      "engine":"berserk","variant":variant,"source_file":"src/search.c",
      "raw_probe_token":"TTProbe(","raw_probe_calls_total":total,
      "scoped_sites":{"MAIN":1,"QSEARCH":1},
      "excluded_sites":[{"kind":"POST_SEARCH_PONDER_REPORT","count":1}],
      "complete_scoped_mediation": t.count('c3x_psm_after_probe("MAIN"')==1 and t.count('c3x_psm_after_probe("QSEARCH"')==1
    }

def helper_ethereal(variant):
    removal = variant=="removal"
    mask_body = 'return 1;' if removal else r'''const char* m=c3x_psm_mode();
  if (!strcmp(m,"MASK_ALL") || !strcmp(m,"MASKED")) return 1;
  if (!strcmp(site,"MAIN"))
    return !strcmp(m,"MASK_MAIN") || !strcmp(m,"MASK_MAIN_QSEARCH");
  return !strcmp(m,"MASK_QSEARCH") || !strcmp(m,"MASK_MAIN_QSEARCH");'''
    mode_body = 'return "REMOVAL";' if removal else r'''const char* m=getenv("C3X_PSM_MODE");
  return m && *m ? m : "NATIVE";'''
    return f'''
static unsigned long long c3x_psm_probes_main=0, c3x_psm_probes_qsearch=0;
static unsigned long long c3x_psm_hits_main=0, c3x_psm_hits_qsearch=0;
static unsigned long long c3x_psm_masked_main=0, c3x_psm_masked_qsearch=0;

static const char* c3x_psm_mode(void) {{
  {mode_body}
}}

static int c3x_psm_should_mask(const char* site) {{
  {mask_body}
}}

static void c3x_psm_after_probe(const char* site, int* hit, uint16_t* move,
                                int* value, int* eval, int* depth, int* bound) {{
  const int isMain=!strcmp(site,"MAIN");
  if (isMain) c3x_psm_probes_main++; else c3x_psm_probes_qsearch++;
  const int raw=*hit;
  if (raw) {{ if (isMain) c3x_psm_hits_main++; else c3x_psm_hits_qsearch++; }}
  if (c3x_psm_should_mask(site)) {{
    if (raw) {{ if (isMain) c3x_psm_masked_main++; else c3x_psm_masked_qsearch++; }}
    *hit=0; *move=NONE_MOVE; *value=0; *eval=VALUE_NONE; *depth=0; *bound=0;
  }}
}}

static void c3x_psm_emit(void) {{
  printf("info string c3x_psm_v1 mode=%s probes_main=%llu hits_main=%llu masked_main=%llu probes_qsearch=%llu hits_qsearch=%llu masked_qsearch=%llu\\n",
         c3x_psm_mode(), c3x_psm_probes_main, c3x_psm_hits_main, c3x_psm_masked_main,
         c3x_psm_probes_qsearch, c3x_psm_hits_qsearch, c3x_psm_masked_qsearch);
}}
'''

def patch_ethereal(root,variant):
    p=root/"src/search.c"; t=p.read_text()
    token="tt_probe(board->hash, thread->height, &ttMove, &ttValue, &ttEval, &ttDepth, &ttBound)"
    total=t.count(token)
    if total!=2:
        raise RuntimeError(f"ethereal tt_probe census drift: expected 2, found {total}")
    anchor="volatile int ANALYSISMODE; // Whether to make some changes for Analysis"
    t=replace_once(t,anchor,anchor+helper_ethereal(variant),"ethereal helper")
    old=f'''    if ((ttHit = {token})) {{'''
    new_main=f'''    ttHit = {token};
    c3x_psm_after_probe("MAIN", &ttHit, &ttMove, &ttValue, &ttEval, &ttDepth, &ttBound);
    if (ttHit) {{'''
    t=replace_once(t,old,new_main,"ethereal MAIN")
    new_q=f'''    ttHit = {token};
    c3x_psm_after_probe("QSEARCH", &ttHit, &ttMove, &ttValue, &ttEval, &ttDepth, &ttBound);
    if (ttHit) {{'''
    t=replace_once(t,old,new_q,"ethereal QSEARCH")
    best='''    // Report best move ( we should always have one )
    moveToString(best, str, board->chess960);'''
    t=replace_once(t,best,'''    // Report best move ( we should always have one )
    c3x_psm_emit();
    moveToString(best, str, board->chess960);''',"ethereal telemetry")
    p.write_text(t)
    return {
      "engine":"ethereal","variant":variant,"source_file":"src/search.c",
      "raw_probe_token":"tt_probe(","raw_probe_calls_total":total,
      "scoped_sites":{"MAIN":1,"QSEARCH":1},"excluded_sites":[],
      "complete_scoped_mediation": t.count('c3x_psm_after_probe("MAIN"')==1 and t.count('c3x_psm_after_probe("QSEARCH"')==1
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--engine",choices=tuple(LOCKS),required=True)
    ap.add_argument("--root",required=True)
    ap.add_argument("--variant",choices=("instrument","removal"),required=True)
    ap.add_argument("--manifest",required=True)
    a=ap.parse_args()
    root=Path(a.root).resolve()
    import subprocess
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if head!=LOCKS[a.engine]:
        raise SystemExit(f"SOURCE_LOCK_FAIL {a.engine} {head}")
    manifest=(patch_berserk if a.engine=="berserk" else patch_ethereal)(root,a.variant)
    manifest.update({
      "schema":"c3x-p20-engine-adapter-manifest-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P20",
      "source_commit":head,
      "semantic_removal_definition":"Probe/write topology retained; all scoped decision-semantic read payload is reset to the engine-native miss defaults before downstream consumption.",
      "language_policy":"native engine source retained; patch materializer language is not an admission variable"
    })
    if not manifest["complete_scoped_mediation"]:
        raise SystemExit("INCOMPLETE_SCOPED_MEDIATION")
    Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
    Path(a.manifest).write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    subprocess.check_call(["git","diff","--check"],cwd=root)
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":
    main()
