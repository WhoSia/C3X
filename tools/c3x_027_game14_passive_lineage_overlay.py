#!/usr/bin/env python3
"""C3X027 passive Game14 capture-guard lineage overlay; does not alter decisions.

Apply only AFTER sept_capture_prune_exact_outcome_patch and
sept_capture_counterfactual_patch. Original 0.24 C3a/C3b files remain untouched.
"""
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,tag):
    n=s.count(a)
    if n!=1: raise RuntimeError(f"C3X027_LINEAGE_ANCHOR_{tag}_{n}")
    return s.replace(a,b,1)

STATE=r"""
// Passive capture-guard descendant + depth boundary trace. One armed path per process.
struct C3X027_LineageState {
 bool armed=false, did_move=false, child_entered=false, child_returned=false;
 const Search::Stack* parent=nullptr;
 Key expected_child=0;
 Move move=MOVE_NONE;
 long long root_call=0;
 unsigned long long seq=0;
};
thread_local C3X027_LineageState c3x027_lineage;
bool c3x027_lineage_on() {
 const char* p=std::getenv("C3X027_GAME14_LINEAGE_LOG");
 return p && *p;
}
void c3x027_lineage_emit(const char* event,const Position& pos,int ply,
                         int value=0,int alpha=0,int beta=0) {
 const char* dest=std::getenv("C3X027_GAME14_LINEAGE_LOG");
 if (!dest || !*dest || c3x027_lineage.seq>=2048) return;
 if (auto* f=std::fopen(dest,"a")) {
  std::fprintf(f,"event=%s seq=%llu root_call=%lld key64=%llu expected_child64=%llu move=%d ply=%d value=%d alpha=%d beta=%d did_move=%d child_entered=%d\\n",
    event,++c3x027_lineage.seq,(long long)c3x018_root_context_call,
    (unsigned long long)std::uint64_t(pos.key()),
    (unsigned long long)std::uint64_t(c3x027_lineage.expected_child),
    int(c3x027_lineage.move),ply,value,alpha,beta,
    int(c3x027_lineage.did_move),int(c3x027_lineage.child_entered));
  std::fclose(f);
 }
}
void c3x027_lineage_arm(const Position& pos,Search::Stack* ss,Move move) {
 if (!c3x027_lineage_on()) return;
 c3x027_lineage={};
 c3x027_lineage.armed=true;
 c3x027_lineage.parent=ss;
 c3x027_lineage.move=move;
 c3x027_lineage.root_call=c3x018_root_context_call;
 c3x027_lineage.expected_child=pos.key_after(move);
 c3x027_lineage_emit("GUARD_REENABLED",pos,ss->ply);
}
void c3x027_lineage_after_do(const Position& pos,Search::Stack* ss,Move move) {
 auto& x=c3x027_lineage;
 if (!x.armed || x.did_move || ss!=x.parent || move!=x.move ||
     pos.key()!=x.expected_child || c3x018_root_context_call!=x.root_call) return;
 x.did_move=true;
 c3x027_lineage_emit("DO_MOVE_EXECUTED",pos,ss->ply);
}
void c3x027_lineage_child_entry(const Position& pos,Search::Stack* ss,
                                int depth,int alpha,int beta) {
 auto& x=c3x027_lineage;
 if (!x.armed || !x.did_move || x.child_entered || ss!=x.parent+1 ||
     pos.key()!=x.expected_child || c3x018_root_context_call!=x.root_call) return;
 x.child_entered=true;
 c3x027_lineage_emit("CHILD_ENTERED",pos,ss->ply,depth,alpha,beta);
}
void c3x027_lineage_child_return(const Position& pos,Search::Stack* ss,
                                Move move,int value,int alpha,int beta) {
 auto& x=c3x027_lineage;
 if (!x.armed || !x.child_entered || x.child_returned ||
     ss!=x.parent || move!=x.move || pos.key()!=x.expected_child ||
     c3x018_root_context_call!=x.root_call) return;
 x.child_returned=true;
 c3x027_lineage_emit("CHILD_VALUE_RETURNED",pos,ss->ply,value,alpha,beta);
}
void c3x027_lineage_parent_value(const Position& pos,Search::Stack* ss,
                                 Move move,int value,int alpha,int beta) {
 auto& x=c3x027_lineage;
 if (!x.armed || !x.child_returned || ss!=x.parent || move!=x.move ||
     c3x018_root_context_call!=x.root_call) return;
 c3x027_lineage_emit("PARENT_CANDIDATE_VALUE",pos,ss->ply,value,alpha,beta);
 x.armed=false;
}
"""
def patch(s):
    s=once(s,"thread_local unsigned long long c3x027_counterfactual_match_count=0;",
           "thread_local unsigned long long c3x027_counterfactual_match_count=0;\n"+STATE,"STATE")
    s=once(s,'c3x027_capture_branch_log(pos,move,Value(-205)*depth,"EXACT_ONE_EVENT_REENABLED");',
           'c3x027_capture_branch_log(pos,move,Value(-205)*depth,"EXACT_ONE_EVENT_REENABLED");\n                        c3x027_lineage_arm(pos,ss,move);',"ARM")
    main='Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {'
    s=once(s,main,main+'\n    c3x027_lineage_child_entry(pos,ss,int(depth),int(alpha),int(beta));',"ENTRY")
    main_do='      // Step 16. Make the move\n      pos.do_move(move, st, givesCheck);'
    s=once(s,main_do,main_do+'\n      c3x027_lineage_after_do(pos,ss,move);',"DO")
    main_undo='      // Step 19. Undo move\n      pos.undo_move(move);'
    s=once(s,main_undo,
      '      c3x027_lineage_child_return(pos,ss,move,int(value),int(alpha),int(beta));\n'+main_undo+
      '\n      c3x027_lineage_parent_value(pos,ss,move,int(value),int(alpha),int(beta));',"RETURN")
    # Post-depth diagnostic; captures root scores even when the target event is absent.
    anchor='      if (!Threads.stop)\n          completedDepth = rootDepth;\n'
    snapshot=r'''
      if (c3x027_lineage_on() && !rootMoves.empty()) {
          sync_cout << "info string c3x027_root_boundary depth=" << int(rootDepth)
                    << " leader=" << int(rootMoves.front().pv[0])
                    << " score=" << int(rootMoves.front().score)
                    << " average=" << int(rootMoves.front().averageScore)
                    << sync_endl;
      }
'''
    s=once(s,anchor,anchor+snapshot,"ROOT_BOUNDARY")
    return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/search.cpp"
 before=f.read_bytes();after=patch(before.decode()).encode()
 f.write_bytes(after)
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps({"schema":"c3x027-game14-passive-lineage-source-v1",
 "before_sha256":hashlib.sha256(before).hexdigest(),
 "after_sha256":hashlib.sha256(after).hexdigest(),
 "observer_environment":"C3X027_GAME14_LINEAGE_LOG",
 "source_event_names":["GUARD_REENABLED","DO_MOVE_EXECUTED","CHILD_ENTERED",
                       "CHILD_VALUE_RETURNED","PARENT_CANDIDATE_VALUE"],
 "root_boundary_UCI_diagnostic":True,
 "not_yet_full_ancestor_or_natural_mediation":True,
 "source_mutations":"read-only instrumentation only"},indent=2,sort_keys=True)+"\n")
 print("C3X027_GAME14_PASSIVE_LINEAGE_PATCH_READY")
if __name__=="__main__":main()
