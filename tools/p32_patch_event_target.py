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
def install(r):
 dst=r/"src"/"c3x_p32_target.inc";shutil.copyfile(ROOT/"tools"/"p32_event_target.inc",dst);return str(dst.relative_to(r))

def stockfish(r):
 inc=install(r);p=r/"src"/"search.cpp";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p32_target.inc"',"SF_INC")
 s=one(s,'if (!rootNode && c3x_p31_no_move()) ttData.move = Move::none();',
 '''if (!rootNode && ttData.move
        && c3x_p32_block("MAIN",C3X_P32_MOVE,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,
                         (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))
        ttData.move = Move::none();''',"SF_MAIN_MOVE")
 s=one(s,'if (c3x_p31_no_move()) ttData.move = Move::none();',
 '''if (ttData.move
        && c3x_p32_block("QSEARCH",C3X_P32_MOVE,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,
                         (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))
        ttData.move = Move::none();''',"SF_Q_MOVE")

 s=one(s,'''        if (is_valid(unadjustedStaticEval) && !c3x_p31_no_eval())
            c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
        if (c3x_p31_no_eval()) unadjustedStaticEval = VALUE_NONE;''',
 '''        if (is_valid(unadjustedStaticEval)) {
            c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
            if (c3x_p32_block("MAIN",C3X_P32_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,
                              (int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))
                unadjustedStaticEval = VALUE_NONE;
        }''',"SF_MAIN_EVAL")
 s=one(s,'''            if (is_valid(unadjustedStaticEval) && !c3x_p31_no_eval())
                c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
            if (c3x_p31_no_eval()) unadjustedStaticEval = VALUE_NONE;''',
 '''            if (is_valid(unadjustedStaticEval)) {
                c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
                if (c3x_p32_block("QSEARCH",C3X_P32_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,
                                  (int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))
                    unadjustedStaticEval = VALUE_NONE;
            }''',"SF_Q_EVAL")

 s=one(s,'''        if (!c3x_p31_no_eval() && is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
        {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useMainValue;
            c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)eval);
            eval = ttData.value;
        }''',
 '''        if (is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
        {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useMainValue;
            c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)eval);
            if (!c3x_p32_block("MAIN",C3X_P32_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,
                               (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)eval))
                eval = ttData.value;
        }''',"SF_MAIN_VALUE")
 s=one(s,'''            if (!c3x_p31_no_eval() && is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
            {
                if (c3xTt.telemetry)
                    ++c3xTt.stats.useQsearchValue;
                c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)bestValue);
                bestValue = ttData.value;
            }''',
 '''            if (is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
            {
                if (c3xTt.telemetry)
                    ++c3xTt.stats.useQsearchValue;
                c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)bestValue);
                if (!c3x_p32_block("QSEARCH",C3X_P32_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,
                                   (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)bestValue))
                    bestValue = ttData.value;
            }''',"SF_Q_VALUE")
 s=one(s,'&& !c3x_p31_no_cutoff())\n    {\n        if (c3xTt.telemetry)\n            ++c3xTt.stats.useMainCutoffGate;',
 '''&& !c3x_p32_block("MAIN",C3X_P32_CUTOFF,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,
                           (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))
    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useMainCutoffGate;''',"SF_MAIN_CUTOFF")
 s=one(s,'''    if (!c3x_p31_no_cutoff() && !PvNode && ttData.depth >= DEPTH_QS && is_valid(ttData.value)
        && (ttData.bound & (ttData.value >= beta ? BOUND_LOWER : BOUND_UPPER)))''',
 '''    if (!PvNode && ttData.depth >= DEPTH_QS && is_valid(ttData.value)
        && (ttData.bound & (ttData.value >= beta ? BOUND_LOWER : BOUND_UPPER))
        && !c3x_p32_block("QSEARCH",C3X_P32_CUTOFF,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,
                           (int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0))''',"SF_Q_CUTOFF")
 p.write_text(s);return {"include":inc,"file":"src/search.cpp"}

def berserk(r):
 inc=install(r);p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p32_target.inc"',"BE_INC")
 s=one(s,'if (!isRoot && c3x_p31_no_move()) hashMove = NULL_MOVE;',
 '''if (!isRoot && hashMove && c3x_p32_block("MAIN",C3X_P32_MOVE,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                                                ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) hashMove = NULL_MOVE;''',"BE_MAIN_MOVE")
 s=one(s,'if (c3x_p31_no_move()) hashMove = NULL_MOVE;',
 '''if (hashMove && c3x_p32_block("QSEARCH",C3X_P32_MOVE,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                                    ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) hashMove = NULL_MOVE;''',"BE_Q_MOVE")
 s=one(s,'''  if (!c3x_p31_no_cutoff() && !isPV && ttScore != UNKNOWN && ttDepth >= depth && (cutnode || ttScore <= alpha) &&
      (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER))) {''',
 '''  if (!isPV && ttScore != UNKNOWN && ttDepth >= depth && (cutnode || ttScore <= alpha) &&
      (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER)) &&
      !c3x_p32_block("MAIN",C3X_P32_CUTOFF,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                      ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) {''',"BE_MAIN_CUTOFF")
 s=one(s,'''  if (!c3x_p31_no_cutoff() && !isPV && ttScore != UNKNOWN && (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER))) {''',
 '''  if (!isPV && ttScore != UNKNOWN && (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER)) &&
      !c3x_p32_block("QSEARCH",C3X_P32_CUTOFF,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                      ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) {''',"BE_Q_CUTOFF")
 s=one(s,'''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN && !c3x_p31_no_eval())
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
      if (c3x_p31_no_eval()) rawEval = EVAL_UNKNOWN;''',
 '''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN) {
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
        if (c3x_p32_block("MAIN",C3X_P32_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                          ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) rawEval = EVAL_UNKNOWN;
      }''',"BE_MAIN_EVAL")
 s=one(s,'''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN && !c3x_p31_no_eval())
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
      if (c3x_p31_no_eval()) rawEval = EVAL_UNKNOWN;''',
 '''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN) {
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
        if (c3x_p32_block("QSEARCH",C3X_P32_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                          ttScore,ttEval,ttBound,(unsigned long long)hashMove,0)) rawEval = EVAL_UNKNOWN;
      }''',"BE_Q_EVAL")
 s=one(s,'''      if (!c3x_p31_no_eval() && ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        eval = ttScore;
      }''',
 '''      if (ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        if (!c3x_p32_block("MAIN",C3X_P32_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                           ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval)) eval = ttScore;
      }''',"BE_MAIN_VALUE")
 s=one(s,'''      if (!c3x_p31_no_eval() && ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        eval = ttScore;
      }''',
 '''      if (ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        if (!c3x_p32_block("QSEARCH",C3X_P32_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,
                           ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval)) eval = ttScore;
      }''',"BE_Q_VALUE")
 p.write_text(s);return {"include":inc,"file":"src/search.c"}

def ethereal(r):
 inc=install(r);p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "c3x_p31_semantic.inc"','#include "c3x_p31_semantic.inc"\n#include "c3x_p32_target.inc"',"ET_INC")
 s=one(s,'if (c3x_p31_no_move()) ttMove = NONE_MOVE;',
 '''if (ttMove && c3x_p32_block("MAIN",C3X_P32_MOVE,(unsigned long long)board->hash,thread->height,depth,alpha,beta,
                                  ttValue,ttEval,ttBound,(unsigned long long)ttMove,0)) ttMove = NONE_MOVE;''',"ET_MAIN_MOVE")
 # qsearch move was never an actual move-order semantic use in this source; leave its P31 no-op mask false under BASE.
 s=one(s,'''            if (!c3x_p31_no_cutoff() && (ttBound == BOUND_EXACT
                || (ttBound == BOUND_LOWER && ttValue >= beta)
                || (ttBound == BOUND_UPPER && ttValue <= alpha))) {''',
 '''            if ((ttBound == BOUND_EXACT
                || (ttBound == BOUND_LOWER && ttValue >= beta)
                || (ttBound == BOUND_UPPER && ttValue <= alpha))
                && !c3x_p32_block("MAIN",C3X_P32_CUTOFF,(unsigned long long)board->hash,thread->height,depth,alpha,beta,
                                   ttValue,ttEval,ttBound,(unsigned long long)ttMove,0)) {''',"ET_MAIN_CUTOFF")
 s=one(s,'''        if (!c3x_p31_no_cutoff()
            && !PvNode
            && ttDepth >= depth - 1
            && (ttBound & BOUND_UPPER)
            && (cutnode || ttValue <= alpha)
            && ttValue + TTResearchMargin <= alpha) {''',
 '''        if (!PvNode
            && ttDepth >= depth - 1
            && (ttBound & BOUND_UPPER)
            && (cutnode || ttValue <= alpha)
            && ttValue + TTResearchMargin <= alpha
            && !c3x_p32_block("MAIN",C3X_P32_CUTOFF,(unsigned long long)board->hash,thread->height,depth,alpha,beta,
                               ttValue,ttEval,ttBound,(unsigned long long)ttMove,1)) {''',"ET_MAIN_RESEARCH")
 s=one(s,'''    if (!inCheck && ttHit && ttEval != VALUE_NONE && !c3x_p31_no_eval())
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
    if (c3x_p31_no_eval()) ttEval = VALUE_NONE;''',
 '''    if (!inCheck && ttHit && ttEval != VALUE_NONE) {
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
        if (c3x_p32_block("MAIN",C3X_P32_EVAL,(unsigned long long)board->hash,thread->height,depth,alpha,beta,
                          ttValue,ttEval,ttBound,(unsigned long long)ttMove,0)) ttEval = VALUE_NONE;
    }''',"ET_MAIN_EVAL")
 s=one(s,'''        if (!c3x_p31_no_cutoff() && (ttBound == BOUND_EXACT
            || (ttBound == BOUND_LOWER && ttValue >= beta)
            || (ttBound == BOUND_UPPER && ttValue <= alpha))) {''',
 '''        if ((ttBound == BOUND_EXACT
            || (ttBound == BOUND_LOWER && ttValue >= beta)
            || (ttBound == BOUND_UPPER && ttValue <= alpha))
            && !c3x_p32_block("QSEARCH",C3X_P32_CUTOFF,(unsigned long long)board->hash,thread->height,0,alpha,beta,
                               ttValue,ttEval,ttBound,(unsigned long long)ttMove,0)) {''',"ET_Q_CUTOFF")
 s=one(s,'''    if (ttHit && ttEval != VALUE_NONE && !c3x_p31_no_eval())
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,0,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
    if (c3x_p31_no_eval()) ttEval = VALUE_NONE;''',
 '''    if (ttHit && ttEval != VALUE_NONE) {
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,0,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
        if (c3x_p32_block("QSEARCH",C3X_P32_EVAL,(unsigned long long)board->hash,thread->height,0,alpha,beta,
                          ttValue,ttEval,ttBound,(unsigned long long)ttMove,0)) ttEval = VALUE_NONE;
    }''',"ET_Q_EVAL")
 p.write_text(s);return {"include":inc,"file":"src/search.c"}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":stockfish,"berserk":berserk,"ethereal":ethereal}[a.engine](r)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p32-event-target-variant-v1","scientific_stage":"C3X 0.7.0-G9.4-P32","engine":a.engine,
    "source_commit":h,"measurement_seq":5,
    "modes":["BASE","CATALOG","FRONTIER_NULL","REMOVE_SET","KEEP_SET"],
    "address_fields":["scope","event_type","full_key","ply","depth","tt_move","bound","payload","baseline_signature_occurrence"],
    "semantic_intervention":"measurement-search-only event-address semantic-use blocking/restoration; no TT storage/replacement/index/age edit","edit":edit}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
