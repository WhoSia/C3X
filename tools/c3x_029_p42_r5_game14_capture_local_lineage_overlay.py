#!/usr/bin/env python3
"""C3X P42/R5: passive, source-anchored Game14 bypass-to-child/parent witness.

Run ONLY after C3X027 exact capture outcome + counterfactual overlays on the
pinned Stockfish16 source. Do not alter chess decisions or replace the prior
single-event intervention. A positive trace has local scope only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

STATE_ANCHOR = "thread_local unsigned long long c3x027_counterfactual_match_count=0;"
EVENT_ANCHOR = 'c3x027_capture_branch_log(pos,move,Value(-205)*depth,"EXACT_ONE_EVENT_REENABLED");'
MAIN_DO = '      // Step 16. Make the move\n      pos.do_move(move, st, givesCheck);'
MAIN_UNDO = '      // Step 19. Undo move\n      pos.undo_move(move);'
MAIN_STOP = '''      if (Threads.stop.load(std::memory_order_relaxed))
          return VALUE_ZERO;

      if (rootNode)'''
MAIN_ADOPT = '''      if (value > bestValue)
      {
          bestValue = value;'''
MAIN_ENTRY = 'Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {'
Q_ENTRY = 'Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {'

HELPER = r"""
// P42/R5: one observed local event; never controls search behavior.
struct C3X042_R5_Local {
  bool armed=false, did_move=false, child_entered=false, child_returned=false;
  bool parent_assessed=false, parent_adopted=false;
  const Search::Stack* frame=nullptr;
  Key parent_key=0, child_key=0;
  Move move=MOVE_NONE;
  long long root_call=0;
  std::uint64_t seq=0;
};
thread_local C3X042_R5_Local c3x042_r5;
void c3x042_r5_emit(const Position& pos, const char* event,
                   int score=0, int best=0, int alpha=0, int beta=0) {
  const char* dest=std::getenv("C3X027_CAPTURE_BRANCH_LOG");
  if (!dest || !*dest) return;
  if (auto* out=std::fopen(dest,"a")) {
    std::fprintf(out,
      "c3x042_r5 event=%s seq=%llu parent64=%llu child64=%llu key64=%llu "
      "root_call=%lld root_move=%d move=%d did_move=%d child_entered=%d "
      "score=%d pre_best=%d alpha=%d beta=%d\n",
      event,(unsigned long long)++c3x042_r5.seq,
      (unsigned long long)c3x042_r5.parent_key,
      (unsigned long long)c3x042_r5.child_key,
      (unsigned long long)pos.key(),
      c3x042_r5.root_call,int(c3x018_root_context_move),
      int(c3x042_r5.move),int(c3x042_r5.did_move),
      int(c3x042_r5.child_entered),score,best,alpha,beta);
    std::fclose(out);
  }
}
void c3x042_r5_arm(const Position& pos, Search::Stack* ss, Move move) {
  c3x042_r5={};
  c3x042_r5.armed=true;
  c3x042_r5.frame=ss;
  c3x042_r5.parent_key=pos.key();
  c3x042_r5.child_key=pos.key_after(move);
  c3x042_r5.move=move;
  c3x042_r5.root_call=c3x018_root_context_call;
  c3x042_r5_emit(pos,"GUARD_FALLTHROUGH");
}
void c3x042_r5_after_do(const Position& pos,Search::Stack* ss,Move move) {
  if (!c3x042_r5.armed || c3x042_r5.did_move
      || ss!=c3x042_r5.frame || move!=c3x042_r5.move
      || pos.key()!=c3x042_r5.child_key
      || c3x018_root_context_call!=c3x042_r5.root_call) return;
  c3x042_r5.did_move=true;
  c3x042_r5_emit(pos,"ACTUAL_DO_MOVE");
}
void c3x042_r5_entry(const Position& pos,Search::Stack* ss,const char* site,
                     int depth) {
  if (!c3x042_r5.armed || !c3x042_r5.did_move
      || c3x042_r5.child_entered || ss!=c3x042_r5.frame+1
      || pos.key()!=c3x042_r5.child_key) return;
  c3x042_r5.child_entered=true;
  c3x042_r5_emit(pos,site,depth);
}
void c3x042_r5_before_undo(const Position& pos,Search::Stack* ss,
                          Move move,int score) {
  if (!c3x042_r5.armed || !c3x042_r5.did_move
      || c3x042_r5.child_returned || ss!=c3x042_r5.frame
      || move!=c3x042_r5.move || pos.key()!=c3x042_r5.child_key)
    return;
  c3x042_r5.child_returned=true;
  c3x042_r5_emit(pos,"CHILD_RETURNED_TO_PARENT",score);
}
void c3x042_r5_assess(const Position& pos,Search::Stack* ss,
                     Move move,int score,int best,int alpha,int beta) {
  if (!c3x042_r5.armed || !c3x042_r5.child_returned
      || c3x042_r5.parent_assessed || ss!=c3x042_r5.frame
      || move!=c3x042_r5.move || pos.key()!=c3x042_r5.parent_key)
    return;
  c3x042_r5.parent_assessed=true;
  c3x042_r5_emit(pos,"PARENT_VALUE_ASSESSED",score,best,alpha,beta);
}
void c3x042_r5_adopt(const Position& pos,Search::Stack* ss,
                     Move move,int score,int alpha,int beta) {
  if (!c3x042_r5.armed || !c3x042_r5.parent_assessed
      || c3x042_r5.parent_adopted || ss!=c3x042_r5.frame
      || move!=c3x042_r5.move || pos.key()!=c3x042_r5.parent_key)
    return;
  c3x042_r5.parent_adopted=true;
  c3x042_r5_emit(pos,"PARENT_BESTVALUE_ASSIGNED",score,score,alpha,beta);
}
"""

def once(src: str, old: str, new: str, tag: str) -> str:
    count = src.count(old)
    if count != 1:
        raise ValueError(f"P42_R5_HOLD_{tag}_ANCHOR_COUNT_{count}")
    return src.replace(old, new, 1)

def patch(src: str) -> str:
    if "c3x042_r5_arm" in src:
        raise ValueError("P42_R5_HOLD_ALREADY_PATCHED")
    src = once(src, STATE_ANCHOR, STATE_ANCHOR + HELPER, "STATE")
    src = once(src, EVENT_ANCHOR,
               EVENT_ANCHOR + "\n                        c3x042_r5_arm(pos,ss,move);",
               "EXACT_GUARD")
    src = once(src, MAIN_DO, MAIN_DO +
               "\n      c3x042_r5_after_do(pos,ss,move);", "DO_MOVE")
    src = once(src, MAIN_ENTRY, MAIN_ENTRY +
               '\n    c3x042_r5_entry(pos,ss,"MAIN_CHILD_ENTERED",int(depth));',
               "MAIN_ENTRY")
    src = once(src, Q_ENTRY, Q_ENTRY +
               '\n    c3x042_r5_entry(pos,ss,"QSEARCH_CHILD_ENTERED",int(depth));',
               "Q_ENTRY")
    src = once(src, MAIN_UNDO,
               '      c3x042_r5_before_undo(pos,ss,move,int(value));\n' +
               MAIN_UNDO, "CHILD_RETURN")
    src = once(src, MAIN_STOP,
               '''      if (Threads.stop.load(std::memory_order_relaxed))
          return VALUE_ZERO;
      c3x042_r5_assess(pos,ss,move,int(value),int(bestValue),
                       int(alpha),int(beta));

      if (rootNode)''', "PARENT_ASSESS")
    src = once(src, MAIN_ADOPT,
               '''      if (value > bestValue)
      {
          bestValue = value;
          c3x042_r5_adopt(pos,ss,move,int(value),int(alpha),int(beta));''',
               "PARENT_ADOPT")
    return src

def main() -> None:
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    path=Path(args.source)/"src/search.cpp"
    before=path.read_bytes()
    after=patch(before.decode("utf-8")).encode()
    path.write_bytes(after)
    output=Path(args.out_manifest)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({
      "schema":"c3x042-r5-game14-exact-capture-local-ancestry-v1",
      "before_sha256":hashlib.sha256(before).hexdigest(),
      "after_sha256":hashlib.sha256(after).hexdigest(),
      "requires_source_anchored_c3x027_bypass":True,
      "observer_only":True,
      "log_env":"C3X027_CAPTURE_BRANCH_LOG",
      "required_trace":["GUARD_FALLTHROUGH","ACTUAL_DO_MOVE",
                        "MAIN_CHILD_ENTERED|QSEARCH_CHILD_ENTERED",
                        "CHILD_RETURNED_TO_PARENT","PARENT_VALUE_ASSESSED"],
      "optional_trace":["PARENT_BESTVALUE_ASSIGNED"],
      "not_full_ancestor_chain":True,
      "not_natural_mediation":True,
      "new_native_results":False
    },sort_keys=True,indent=2)+"\n")
    print("C3X042_R5_LOCAL_NATIVE_OVERLAY_WRITTEN_SOURCE_NOT_YET_VALIDATED")
if __name__=="__main__":
    main()
