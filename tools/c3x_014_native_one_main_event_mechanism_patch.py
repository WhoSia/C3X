#!/usr/bin/env python3
"""C3X 0.14: minimal ONE_MAIN TT-return intervention + passive pathway counters.

MUST apply on pinned sf_16 source AFTER existing C3X 0.13 EP9 and
C3X 0.14 post-search native completedDepth patches, not on arbitrary code.
Exactly the first actual main TT return is suppressed; others remain valid.
TT read, quiet-history side effect and TT move ordering are NOT disabled.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError("ONE_MAIN_SOURCE_ANCHOR_COUNT_"+name+"_"+str(n))
    return s.replace(a,b,1)

COUNTERS=r'''
  struct C3X014TraceCounters {
      unsigned long long picker_main_nodes=0, picker_main_ttmove=0;
      unsigned long long lmr_invoked=0, lmr_with_reduction=0;
      unsigned long long history_quiet_update=0, history_continuation_update=0;
      unsigned long long main_evaluate_calls=0, main_tt_eval_reads=0;
      unsigned long long main_alpha_beta_move_cutoffs=0, main_tt_save_terminal=0;
      unsigned long long first_blocked_key=0;
      int first_blocked_ply=-1, first_blocked_depth=-1;
      int first_blocked_bound=-1, first_blocked_tt_value=0, first_blocked_beta=0;
  };
  C3X014TraceCounters c3x014_trace;
  void c3x014_dump_mechanism() {
    const auto& a=c3x014_trace;
    sync_cout << "info string c3x014_path"
      << " picker_main_nodes=" << a.picker_main_nodes
      << " picker_main_ttmove=" << a.picker_main_ttmove
      << " lmr_invoked=" << a.lmr_invoked
      << " lmr_with_reduction=" << a.lmr_with_reduction
      << " history_quiet_update=" << a.history_quiet_update
      << " history_continuation_update=" << a.history_continuation_update
      << " main_evaluate_calls=" << a.main_evaluate_calls
      << " main_tt_eval_reads=" << a.main_tt_eval_reads
      << " main_alpha_beta_move_cutoffs=" << a.main_alpha_beta_move_cutoffs
      << " main_tt_save_terminal=" << a.main_tt_save_terminal
      << " first_blocked_key=" << a.first_blocked_key
      << " first_blocked_ply=" << a.first_blocked_ply
      << " first_blocked_depth=" << a.first_blocked_depth
      << " first_blocked_bound=" << a.first_blocked_bound
      << " first_blocked_tt_value=" << a.first_blocked_tt_value
      << " first_blocked_beta=" << a.first_blocked_beta
      << sync_endl;
  }
'''

def instrument(original):
    s=original
    s=once(s,'  C3XEp9Stats c3x_ep9_stats;', '  C3XEp9Stats c3x_ep9_stats;\n'+COUNTERS,'COUNTER_DECL')
    s=once(s,'      c3x_ep9_stats = C3XEp9Stats{};',
              '      c3x_ep9_stats = C3XEp9Stats{};\n      c3x014_trace = C3X014TraceCounters{};','COUNTER_RESET')
    s=once(s,'      else if (!std::strcmp(env,"BOTH")) c3x_ep9_mode=3;',
        '      else if (!std::strcmp(env,"BOTH")) c3x_ep9_mode=3;\n      else if (!std::strcmp(env,"ONE_MAIN")) c3x_ep9_mode=4;','MODE')
    s=once(s,'  c3x_ep9_dump();',
              '  c3x_ep9_dump();\n  c3x014_dump_mechanism();','DUMP')
    # Exact EP9 return condition; counting and native cause-custody only inside the actual return.
    s=once(s,'''            if (c3x_ep9_mode & 1)
                ++c3x_ep9_stats.main_cutoff_blocked;
            else {
                ++c3x_ep9_stats.main_cutoff_taken;
                return ttValue;
            }''',
        '''            if ((c3x_ep9_mode & 1) || (c3x_ep9_mode == 4 && c3x_ep9_stats.main_cutoff_blocked == 0))
            {
                ++c3x_ep9_stats.main_cutoff_blocked;
                if (c3x014_trace.first_blocked_ply < 0)
                {
                    c3x014_trace.first_blocked_key = posKey;
                    c3x014_trace.first_blocked_ply = ss->ply;
                    c3x014_trace.first_blocked_depth = depth;
                    c3x014_trace.first_blocked_bound = int(tte->bound());
                    c3x014_trace.first_blocked_tt_value = int(ttValue);
                    c3x014_trace.first_blocked_beta = int(beta);
                }
            }
            else {
                ++c3x_ep9_stats.main_cutoff_taken;
                return ttValue;
            }''','ONE_EVENT_CUTOFF')
    s=once(s,'''    MovePicker mp(pos, ttMove, depth, &thisThread->mainHistory,
                                      &captureHistory,''',
        '''    ++c3x014_trace.picker_main_nodes;
    c3x014_trace.picker_main_ttmove += bool(ttMove);
    MovePicker mp(pos, ttMove, depth, &thisThread->mainHistory,
                                      &captureHistory,''','MOVE_PICKER_MAIN')
    s=once(s,'''          Depth d = std::clamp(newDepth - r, 1, newDepth + 1);

          value = -search<NonPV>''',
        '''          ++c3x014_trace.lmr_invoked;
          Depth d = std::clamp(newDepth - r, 1, newDepth + 1);
          c3x014_trace.lmr_with_reduction += (d < newDepth);

          value = -search<NonPV>''','LMR_SITE')
    s=once(s,'      ss->staticEval = eval = tte->eval();',
             '      ++c3x014_trace.main_tt_eval_reads;\n      ss->staticEval = eval = tte->eval();','TT_EVAL')
    # One main fallback and one main miss path; instrument BOTH source calls.
    q='ss->staticEval = eval = evaluate(pos);'
    n=s.count(q)
    if n!=2:raise RuntimeError("SF16_MAIN_EVAL_TWO_SITE_COUNT_"+str(n))
    s=s.replace(q,'{ ++c3x014_trace.main_evaluate_calls; '+q+' }')
    s=once(s,'                  ss->cutoffCnt += 1 + !ttMove;\n                  assert(value >= beta); // Fail high',
      '                  ++c3x014_trace.main_alpha_beta_move_cutoffs;\n                  ss->cutoffCnt += 1 + !ttMove;\n                  assert(value >= beta); // Fail high','ALPHA_BETA')
    s=once(s,'    if (!excludedMove && !(rootNode && thisThread->pvIdx))\n        tte->save(posKey, value_to_tt(bestValue, ss->ply), ss->ttPv,',
        '    if (!excludedMove && !(rootNode && thisThread->pvIdx))\n    {\n        ++c3x014_trace.main_tt_save_terminal;\n        tte->save(posKey, value_to_tt(bestValue, ss->ply), ss->ttPv,','TT_SAVE_A')
    s=once(s,'''                  depth, bestMove, ss->staticEval);

    assert(bestValue > -VALUE_INFINITE''',
        '''                  depth, bestMove, ss->staticEval);
    }

    assert(bestValue > -VALUE_INFINITE''','TT_SAVE_B')
    s=once(s,'''  // update_quiet_stats() updates move sorting heuristics

  void update_quiet_stats(const Position& pos, Stack* ss, Move move, int bonus) {
''',
       '''  // update_quiet_stats() updates move sorting heuristics

  void update_quiet_stats(const Position& pos, Stack* ss, Move move, int bonus) {
      ++c3x014_trace.history_quiet_update;
''','QUIET_HISTORY')
    s=once(s,'''  void update_continuation_histories(Stack* ss, Piece pc, Square to, int bonus) {
''',
       '''  void update_continuation_histories(Stack* ss, Piece pc, Square to, int bonus) {
      ++c3x014_trace.history_continuation_update;
''','CONT_HISTORY')
    return s

def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args();file=Path(a.source)/"src/search.cpp"
    raw=file.read_bytes();s=raw.decode()
    require=("c3x_p8_ep9","c3x014_completion_probe","C3XEp9Stats")
    if not all(x in s for x in require):raise SystemExit("C3X014_REQUIRES_EP9_AND_TRUE_DEPTH_PROBE")
    new=instrument(s)
    file.write_text(new)
    result={"schema":"c3x-014-first-single-tt-return-block-and-search-path-source-patch-v1",
         "source":"sf_16 upstream 68e1e9b3811e16cad014b590d7443b9063b3eb52 with exact EP9+native post-search depth patches",
         "original_sha256":hashlib.sha256(raw).hexdigest(),
         "patched_sha256":hashlib.sha256(new.encode()).hexdigest(),
         "modes":{"OFF":0,"MAIN":1,"ONE_MAIN":4},
         "ONE_MAIN_rules":"only first main-search TT return eligible under all original safety conditions is blocked per engine run; no TT probe, TT historical update, ttMove ordering or other TT returns intentionally disabled",
         "passive_channels":["main_move_picker_ttMove_nonzero","LMR_invoked_and_depth_reduced","history_quiet_and_continuation_calls","main_eval_and_TT_eval_reads","main_move_beta_cutoffs","terminal_main_TT_save","first_blocked_posKey_ply_depth_bound_ttValue_beta"],
         "scientific_limitation":"Counter values are pathway descendants, not separately randomized mediator interventions; probe changes runtime timing and cannot certify causal graph edge absent controls."}
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(result,indent=2)+"\n")
    print("C3X014_ONE_MAIN_NATIVE_SOURCE_PATCH_PASS",result["patched_sha256"],flush=True)
if __name__=="__main__":main()
