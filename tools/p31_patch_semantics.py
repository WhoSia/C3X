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
 if n!=1:raise SystemExit(f"{label}_ANCHOR_{n}")
 return t.replace(a,b,1)
def nth(t,a,b,n,label):
 pos=-1
 for _ in range(n+1):
  pos=t.find(a,pos+1)
  if pos<0:raise SystemExit(f"{label}_NTH_{n}")
 return t[:pos]+b+t[pos+len(a):]
def head(r):return subprocess.check_output(["git","-C",str(r),"rev-parse","HEAD"],text=True).strip()
def install(r):
 dst=r/"src"/"c3x_p31_semantic.inc"
 shutil.copyfile(ROOT/"tools"/"p31_semantic_common.inc",dst)
 return str(dst.relative_to(r))

def stockfish(r):
 inc=install(r)
 tt=r/"src"/"tt.cpp";t=tt.read_text()
 t=one(t,'#include "c3x_p30_victim.inc"',
       '#include "c3x_p30_victim.inc"\n\nextern "C" unsigned long long c3x_p31_tt_seq(void){ return c3xSeq; }',"SF_SEQ")
 tt.write_text(t)
 p=r/"src"/"search.cpp";s=p.read_text()
 s=one(s,'#include "ucioption.h"','#include "ucioption.h"\n#include "c3x_p31_semantic.inc"',"SF_INC")

 # Main: remove TT move semantics only in measurement search, never root move constraint.
 a='''    ttData.value = ttHit ? value_from_tt(ttData.value, ss->ply, pos.rule50_count()) : VALUE_NONE;
    ss->ttPv     = excludedMove ? ss->ttPv : PvNode || (ttHit && ttData.is_pv);
    ttCapture    = ttData.move && pos.capture_stage(ttData.move);'''
 b='''    ttData.value = ttHit ? value_from_tt(ttData.value, ss->ply, pos.rule50_count()) : VALUE_NONE;
    ss->ttPv     = excludedMove ? ss->ttPv : PvNode || (ttHit && ttData.is_pv);
    if (!rootNode && c3x_p31_no_move()) ttData.move = Move::none();
    ttCapture    = ttData.move && pos.capture_stage(ttData.move);'''
 s=one(s,a,b,"SF_MAIN_MOVE_MASK")

 # Main TT eval reuse.
 a='''        if (c3xTt.telemetry && is_valid(unadjustedStaticEval))
            ++c3xTt.stats.useMainEval;
        if (!is_valid(unadjustedStaticEval))'''
 b='''        if (c3xTt.telemetry && is_valid(unadjustedStaticEval))
            ++c3xTt.stats.useMainEval;
        if (is_valid(unadjustedStaticEval) && !c3x_p31_no_eval())
            c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
        if (c3x_p31_no_eval()) unadjustedStaticEval = VALUE_NONE;
        if (!is_valid(unadjustedStaticEval))'''
 s=one(s,a,b,"SF_MAIN_EVAL")

 a='''        if (is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
        {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useMainValue;
            eval = ttData.value;
        }'''
 b='''        if (!c3x_p31_no_eval() && is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
        {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useMainValue;
            c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)eval);
            eval = ttData.value;
        }'''
 s=one(s,a,b,"SF_MAIN_VALUE")

 # Main cutoff gate inserted by P12/P15.
 a='''        && (cutNode == (ttData.value >= beta) || depth > 4))
    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useMainCutoffGate;'''
 b='''        && (cutNode == (ttData.value >= beta) || depth > 4)
        && !c3x_p31_no_cutoff())
    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useMainCutoffGate;
        c3x_p31_event("MAIN",C3X_P31_CUTOFF,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);'''
 s=one(s,a,b,"SF_MAIN_CUTOFF")

 # Main move-order seed.
 a='''    MovePicker mp(pos, ttData.move, depth, &mainHistory, &lowPlyHistory, &captureHistory, contHist,
                  &sharedHistory, ss->ply);'''
 b='''    if (ttData.move)
        c3x_p31_event("MAIN",C3X_P31_MOVE,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
    MovePicker mp(pos, ttData.move, depth, &mainHistory, &lowPlyHistory, &captureHistory, contHist,
                  &sharedHistory, ss->ply);'''
 s=one(s,a,b,"SF_MAIN_PICK")

 # Main PV promotion.
 a='''            if (value + inc > alpha)
            {
                bestMove = move;'''
 b='''            if (value + inc > alpha)
            {
                bestMove = move;
                if (move == ttData.move)
                    c3x_p31_event("MAIN",C3X_P31_PV,(unsigned long long)posKey,ss->ply,(int)depth,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)move.raw(),(long long)value);'''
 s=one(s,a,b,"SF_MAIN_PV")

 # Qsearch: mask move after probe assignment.
 a='''    ttData.move  = ttHit ? ttData.move : Move::none();
    ttData.value = ttHit ? value_from_tt(ttData.value, ss->ply, pos.rule50_count()) : VALUE_NONE;
    pvHit        = ttHit && ttData.is_pv;'''
 b='''    ttData.move  = ttHit ? ttData.move : Move::none();
    ttData.value = ttHit ? value_from_tt(ttData.value, ss->ply, pos.rule50_count()) : VALUE_NONE;
    pvHit        = ttHit && ttData.is_pv;
    if (c3x_p31_no_move()) ttData.move = Move::none();'''
 s=one(s,a,b,"SF_Q_MOVE_MASK")

 a='''    if (!PvNode && ttData.depth >= DEPTH_QS && is_valid(ttData.value)
        && (ttData.bound & (ttData.value >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useQsearchCutoff;
        return ttData.value;
    }'''
 b='''    if (!c3x_p31_no_cutoff() && !PvNode && ttData.depth >= DEPTH_QS && is_valid(ttData.value)
        && (ttData.bound & (ttData.value >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useQsearchCutoff;
        c3x_p31_event("QSEARCH",C3X_P31_CUTOFF,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
        return ttData.value;
    }'''
 s=one(s,a,b,"SF_Q_CUTOFF")

 a='''            if (c3xTt.telemetry && is_valid(unadjustedStaticEval))
                ++c3xTt.stats.useQsearchEval;

            if (!is_valid(unadjustedStaticEval))'''
 b='''            if (c3xTt.telemetry && is_valid(unadjustedStaticEval))
                ++c3xTt.stats.useQsearchEval;
            if (is_valid(unadjustedStaticEval) && !c3x_p31_no_eval())
                c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)unadjustedStaticEval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
            if (c3x_p31_no_eval()) unadjustedStaticEval = VALUE_NONE;

            if (!is_valid(unadjustedStaticEval))'''
 s=one(s,a,b,"SF_Q_EVAL")

 a='''            if (is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
            {
                if (c3xTt.telemetry)
                    ++c3xTt.stats.useQsearchValue;
                bestValue = ttData.value;
            }'''
 b='''            if (!c3x_p31_no_eval() && is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
            {
                if (c3xTt.telemetry)
                    ++c3xTt.stats.useQsearchValue;
                c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),(long long)bestValue);
                bestValue = ttData.value;
            }'''
 s=one(s,a,b,"SF_Q_VALUE")

 a='''    MovePicker mp(pos, ttData.move, DEPTH_QS, &mainHistory, &lowPlyHistory, &captureHistory,
                  contHist, &sharedHistory, ss->ply);'''
 b='''    if (ttData.move)
        c3x_p31_event("QSEARCH",C3X_P31_MOVE,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)ttData.move.raw(),0);
    MovePicker mp(pos, ttData.move, DEPTH_QS, &mainHistory, &lowPlyHistory, &captureHistory,
                  contHist, &sharedHistory, ss->ply);'''
 s=one(s,a,b,"SF_Q_PICK")

 a='''            if (value > alpha)
            {
                bestMove = move;

                // Update pv even in fail-high case'''
 b='''            if (value > alpha)
            {
                bestMove = move;
                if (move == ttData.move)
                    c3x_p31_event("QSEARCH",C3X_P31_PV,(unsigned long long)posKey,ss->ply,(int)DEPTH_QS,(int)alpha,(int)beta,(int)ttData.value,(int)ttData.eval,(int)ttData.bound,(unsigned long long)move.raw(),(long long)value);

                // Update pv even in fail-high case'''
 s=one(s,a,b,"SF_Q_PV")
 p.write_text(s)
 return {"files":["src/tt.cpp","src/search.cpp"],"include":inc}

def berserk(r):
 inc=install(r)
 h=r/"src"/"transposition.h";t=h.read_text()
 t=one(t,'void c3x_p30_victim(uint64_t requested, TTEntry* bucket, TTEntry* actual);',
       'void c3x_p30_victim(uint64_t requested, TTEntry* bucket, TTEntry* actual);\nuint64_t c3x_p31_tt_seq(void);',"BE_PROTO")
 h.write_text(t)
 c=r/"src"/"transposition.c";u=c.read_text()
 u=one(u,'#include "c3x_p30_victim.inc"',
       '#include "c3x_p30_victim.inc"\n\nuint64_t c3x_p31_tt_seq(void){ return C3XSeq; }',"BE_SEQ")
 c.write_text(u)
 p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "zobrist.h"','#include "zobrist.h"\n#include "c3x_p31_semantic.inc"',"BE_INC")

 a='''  if (!ss->skip) c3x_psm_probe("MAIN",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;'''
 b='''  if (!ss->skip) c3x_psm_probe("MAIN",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);
  hashMove = isRoot ? thread->rootMoves[thread->multiPV].move : hashMove;
  if (!isRoot && c3x_p31_no_move()) hashMove = NULL_MOVE;'''
 s=one(s,a,b,"BE_MAIN_MOVE_MASK")

 a='''  if (!isPV && ttScore != UNKNOWN && ttDepth >= depth && (cutnode || ttScore <= alpha) &&
      (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER)))
    return ttScore;'''
 b='''  if (!c3x_p31_no_cutoff() && !isPV && ttScore != UNKNOWN && ttDepth >= depth && (cutnode || ttScore <= alpha) &&
      (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER))) {
    c3x_p31_event("MAIN",C3X_P31_CUTOFF,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
    return ttScore;
  }'''
 s=one(s,a,b,"BE_MAIN_CUTOFF")

 a='''      rawEval = ttEval;
      if (rawEval == EVAL_UNKNOWN)
        rawEval = Evaluate(board, thread);'''
 b='''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN && !c3x_p31_no_eval())
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
      if (c3x_p31_no_eval()) rawEval = EVAL_UNKNOWN;
      if (rawEval == EVAL_UNKNOWN)
        rawEval = Evaluate(board, thread);'''
 s=one(s,a,b,"BE_MAIN_EVAL")

 a='''      if (ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER)))
        eval = ttScore;'''
 b='''      if (!c3x_p31_no_eval() && ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("MAIN",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        eval = ttScore;
      }'''
 s=one(s,a,b,"BE_MAIN_VALUE")

 a='''  InitNormalMovePicker(&mp, hashMove, thread, ss);'''
 b='''  if (hashMove)
    c3x_p31_event("MAIN",C3X_P31_MOVE,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
  InitNormalMovePicker(&mp, hashMove, thread, ss);'''
 s=one(s,a,b,"BE_MAIN_PICK")

 a='''      if (score > alpha) {
        bestMove = move;
        alpha    = score;'''
 b='''      if (score > alpha) {
        bestMove = move;
        if (move == hashMove)
          c3x_p31_event("MAIN",C3X_P31_PV,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)move,(long long)score);
        alpha    = score;'''
 s=one(s,a,b,"BE_MAIN_PV")

 # Qsearch PSM site.
 a='''  c3x_psm_probe("QSEARCH",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);

  // TT score pruning'''
 b='''  c3x_psm_probe("QSEARCH",isPV,&ttHit,&hashMove,&ttScore,&ttEval,&ttDepth,&ttBound,&ttPv);
  if (c3x_p31_no_move()) hashMove = NULL_MOVE;

  // TT score pruning'''
 s=one(s,a,b,"BE_Q_MOVE_MASK")

 a='''  if (!isPV && ttScore != UNKNOWN && (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER)))
    return ttScore;'''
 b='''  if (!c3x_p31_no_cutoff() && !isPV && ttScore != UNKNOWN && (ttBound & (ttScore >= beta ? BOUND_LOWER : BOUND_UPPER))) {
    c3x_p31_event("QSEARCH",C3X_P31_CUTOFF,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
    return ttScore;
  }'''
 s=one(s,a,b,"BE_Q_CUTOFF")

 a='''      rawEval = ttEval;
      if (rawEval == EVAL_UNKNOWN)
        rawEval = Evaluate(board, thread);'''
 b='''      rawEval = ttEval;
      if (rawEval != EVAL_UNKNOWN && !c3x_p31_no_eval())
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
      if (c3x_p31_no_eval()) rawEval = EVAL_UNKNOWN;
      if (rawEval == EVAL_UNKNOWN)
        rawEval = Evaluate(board, thread);'''
 s=one(s,a,b,"BE_Q_EVAL")

 a='''      if (ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER)))
        eval = ttScore;'''
 b='''      if (!c3x_p31_no_eval() && ttScore != UNKNOWN && (ttBound & (ttScore > eval ? BOUND_LOWER : BOUND_UPPER))) {
        c3x_p31_event("QSEARCH",C3X_P31_VALUE_EVAL,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,(long long)eval);
        eval = ttScore;
      }'''
 s=one(s,a,b,"BE_Q_VALUE")

 # Q move seed only when in-check evasions actually use hashMove.
 a='''  if (!inCheck)
    InitQSMovePicker(&mp, thread, depth >= -1);
  else
    InitQSEvasionsPicker(&mp, hashMove, thread, ss);'''
 b='''  if (!inCheck)
    InitQSMovePicker(&mp, thread, depth >= -1);
  else {
    if (hashMove)
      c3x_p31_event("QSEARCH",C3X_P31_MOVE,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)hashMove,0);
    InitQSEvasionsPicker(&mp, hashMove, thread, ss);
  }'''
 s=one(s,a,b,"BE_Q_PICK")

 # qsearch PV promotion has unique alpha assignment after bestMove.
 a='''      if (score > alpha) {
        bestMove = move;
        alpha    = score;'''
 b='''      if (score > alpha) {
        bestMove = move;
        if (move == hashMove)
          c3x_p31_event("QSEARCH",C3X_P31_PV,(unsigned long long)board->zobrist,ss->ply,depth,alpha,beta,ttScore,ttEval,ttBound,(unsigned long long)move,(long long)score);
        alpha    = score;'''
 s=one(s,a,b,"BE_Q_PV")
 p.write_text(s)
 return {"files":["src/transposition.h","src/transposition.c","src/search.c"],"include":inc}

def ethereal(r):
 inc=install(r)
 h=r/"src"/"transposition.h";t=h.read_text()
 t=one(t,'void tt_store(uint64_t hash, int height, uint16_t move, int value, int eval, int depth, int bound);',
       'void tt_store(uint64_t hash, int height, uint16_t move, int value, int eval, int depth, int bound);\nuint64_t c3x_p31_tt_seq(void);',"ET_PROTO")
 h.write_text(t)
 c=r/"src"/"transposition.c";u=c.read_text()
 u=one(u,'#include "c3x_p30_victim.inc"',
       '#include "c3x_p30_victim.inc"\n\nuint64_t c3x_p31_tt_seq(void){ return C3XSeq; }',"ET_SEQ")
 c.write_text(u)
 p=r/"src"/"search.c";s=p.read_text()
 s=one(s,'#include "windows.h"','#include "windows.h"\n#include "c3x_p31_semantic.inc"',"ET_INC")

 a='''    c3x_psm_probe("MAIN",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (ttHit) {'''
 b='''    c3x_psm_probe("MAIN",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (c3x_p31_no_move()) ttMove = NONE_MOVE;
    if (ttHit) {'''
 s=one(s,a,b,"ET_MAIN_MOVE_MASK")

 a='''            if (    ttBound == BOUND_EXACT
                || (ttBound == BOUND_LOWER && ttValue >= beta)
                || (ttBound == BOUND_UPPER && ttValue <= alpha))
                return ttValue;'''
 b='''            if (!c3x_p31_no_cutoff() && (ttBound == BOUND_EXACT
                || (ttBound == BOUND_LOWER && ttValue >= beta)
                || (ttBound == BOUND_UPPER && ttValue <= alpha))) {
                c3x_p31_event("MAIN",C3X_P31_CUTOFF,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
                return ttValue;
            }'''
 s=one(s,a,b,"ET_MAIN_CUTOFF")

 # research cutoff is also TT-derived
 a='''        if (   !PvNode
            &&  ttDepth >= depth - 1
            && (ttBound & BOUND_UPPER)
            && (cutnode || ttValue <= alpha)
            &&  ttValue + TTResearchMargin <= alpha)
            return alpha;'''
 b='''        if (!c3x_p31_no_cutoff()
            && !PvNode
            && ttDepth >= depth - 1
            && (ttBound & BOUND_UPPER)
            && (cutnode || ttValue <= alpha)
            && ttValue + TTResearchMargin <= alpha) {
            c3x_p31_event("MAIN",C3X_P31_CUTOFF,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,1);
            return alpha;
        }'''
 s=one(s,a,b,"ET_MAIN_RESEARCH")

 a='''    // Step 6. Initialize flags and values used by pruning and search methods
    search_init_goto:

    // We can grab in check based on the already computed king attackers bitboard
    inCheck = !!board->kingAttackers;

    // Save a history of the static evaluations
    eval = ns->eval = inCheck ? VALUE_NONE
         : ttEval != VALUE_NONE ? ttEval : evaluateBoard(thread, board);'''
 b='''    // Step 6. Initialize flags and values used by pruning and search methods
    search_init_goto:

    // We can grab in check based on the already computed king attackers bitboard
    inCheck = !!board->kingAttackers;

    if (!inCheck && ttHit && ttEval != VALUE_NONE && !c3x_p31_no_eval())
        c3x_p31_event("MAIN",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
    if (c3x_p31_no_eval()) ttEval = VALUE_NONE;

    // Save a history of the static evaluations
    eval = ns->eval = inCheck ? VALUE_NONE
         : ttEval != VALUE_NONE ? ttEval : evaluateBoard(thread, board);'''
 s=one(s,a,b,"ET_MAIN_EVAL")

 a='''    if (!ns->excluded) init_picker(&ns->mp, thread, ttMove);'''
 b='''    if (!ns->excluded) {
        if (ttMove)
            c3x_p31_event("MAIN",C3X_P31_MOVE,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
        init_picker(&ns->mp, thread, ttMove);
    }'''
 s=one(s,a,b,"ET_MAIN_PICK")

 a='''            best = value;
            bestMove = move;

            if (value > alpha) {'''
 b='''            best = value;
            bestMove = move;

            if (value > alpha) {
                if (move == ttMove)
                    c3x_p31_event("MAIN",C3X_P31_PV,(unsigned long long)board->hash,thread->height,depth,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)move,(long long)value);'''
 s=one(s,a,b,"ET_MAIN_PV")

 # Qsearch second PSM site.
 a='''    c3x_psm_probe("QSEARCH",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (ttHit) {'''
 b='''    c3x_psm_probe("QSEARCH",&ttHit,&ttMove,&ttValue,&ttEval,&ttDepth,&ttBound);
    if (c3x_p31_no_move()) ttMove = NONE_MOVE;
    if (ttHit) {'''
 s=one(s,a,b,"ET_Q_MOVE_MASK")

 a='''        if (    ttBound == BOUND_EXACT
            || (ttBound == BOUND_LOWER && ttValue >= beta)
            || (ttBound == BOUND_UPPER && ttValue <= alpha))
            return ttValue;'''
 b='''        if (!c3x_p31_no_cutoff() && (ttBound == BOUND_EXACT
            || (ttBound == BOUND_LOWER && ttValue >= beta)
            || (ttBound == BOUND_UPPER && ttValue <= alpha))) {
            c3x_p31_event("QSEARCH",C3X_P31_CUTOFF,(unsigned long long)board->hash,thread->height,0,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
            return ttValue;
        }'''
 s=one(s,a,b,"ET_Q_CUTOFF")

 a='''    // Save a history of the static evaluations
    eval = ns->eval = ttEval != VALUE_NONE
                    ? ttEval : evaluateBoard(thread, board);'''
 b='''    if (ttHit && ttEval != VALUE_NONE && !c3x_p31_no_eval())
        c3x_p31_event("QSEARCH",C3X_P31_EVAL,(unsigned long long)board->hash,thread->height,0,alpha,beta,ttValue,ttEval,ttBound,(unsigned long long)ttMove,0);
    if (c3x_p31_no_eval()) ttEval = VALUE_NONE;

    // Save a history of the static evaluations
    eval = ns->eval = ttEval != VALUE_NONE
                    ? ttEval : evaluateBoard(thread, board);'''
 s=one(s,a,b,"ET_Q_EVAL")
 # Ethereal qsearch does not seed move ordering from ttMove in this source; record none rather than inventing one.
 p.write_text(s)
 return {"files":["src/transposition.h","src/transposition.c","src/search.c"],"include":inc}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--engine",choices=LOCKS,required=True);ap.add_argument("--manifest",required=True)
 a=ap.parse_args();r=Path(a.root);h=head(r)
 if h!=LOCKS[a.engine]:raise SystemExit(f"SOURCE_LOCK {h}")
 edit={"stockfish_19":stockfish,"berserk":berserk,"ethereal":ethereal}[a.engine](r)
 subprocess.check_call(["git","diff","--check"],cwd=r)
 m={"schema":"c3x-p31-semantic-instrument-v1","scientific_stage":"C3X 0.7.0-G9.4-P31","engine":a.engine,
    "source_commit":h,"measurement_seq":5,
    "modes":["BASE","NO_CUTOFF","NO_MOVE","NO_EVAL","NO_CUTOFF_MOVE","NO_CUTOFF_EVAL","NO_MOVE_EVAL","NO_ALL"],
    "semantic_classes":["CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL","PV_PROMOTION"],
    "semantic_intervention":"measurement-search-only TT-use masking; no TT storage/replacement/index edit","edit":edit}
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
 print(json.dumps(m,sort_keys=True))
if __name__=="__main__":main()
