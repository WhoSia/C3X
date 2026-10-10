#!/usr/bin/env python3
"""Passive C3b: exact native parent candidate and ancestor frame returns.
Apply AFTER pinned T3, T4, P2 C3a source overlays.  No operator mutations.
"""
import argparse,hashlib,json
from pathlib import Path

STATE_ANCHOR='thread_local unsigned long long c3x023_t4_last_sequence=0;'
STATE_PATCH=STATE_ANCHOR+r"""
// C3X024 C3b guarded single-source ancestor-frame witness.
struct C3X024_C3bState {
    bool armed=false, child_returned=false, invalid=false;
    int top=-1, expected=-1;
    unsigned long long ordinal=0;
    std::uint64_t source_key=0;
    long long root_call=0;
    Move root_move=MOVE_NONE;
    const Search::Stack* frames[MAX_PLY]={};
    Move moves[MAX_PLY]={};
    bool candidate[MAX_PLY]={}, completed[MAX_PLY]={};
};
thread_local C3X024_C3bState c3x024_c3b;
bool c3x024_c3b_enabled() {
    const char* s=std::getenv("C3X024_C3B_RETURN_OBS");
    return s && std::strcmp(s,"1")==0;
}
void c3x024_c3b_emit(const Position& pos,const char* event,int ply,Move move,
                     int value=0,int prebest=0,int alpha=0,int beta=0,
                     int leader=0) {
    sync_cout << "info string c3x024_c3b"
              << " event=" << event
              << " ply=" << ply
              << " key64=" << std::uint64_t(pos.key())
              << " source_key64=" << c3x024_c3b.source_key
              << " native_move=" << int(move)
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << int(c3x024_c3b.root_move)
              << " sequence=" << ++c3x024_c3b.ordinal
              << " value=" << value << " pre_best=" << prebest
              << " alpha=" << alpha << " beta=" << beta
              << " beats_best=" << int(value > prebest)
              << " beats_alpha=" << int(value > alpha)
              << " leader_move=" << leader
              << sync_endl;
}
void c3x024_c3b_guard(const Position& pos,Search::Stack* ss,Move move,
                      const char* decision) {
    if (!c3x024_c3b_enabled()) return;
    c3x024_c3b={};
    if (std::strcmp(decision,"PASSED_SEE_GUARD")!=0) return;
    const int p=ss->ply;
    if (p<0 || p>=MAX_PLY-3) {
        c3x024_c3b.invalid=true;
        c3x024_c3b_emit(pos,"ANCESTOR_DEPTH_CENSORED",p,move);
        return;
    }
    c3x024_c3b.armed=true;
    c3x024_c3b.top=p;
    c3x024_c3b.expected=p;
    c3x024_c3b.source_key=std::uint64_t(pos.key());
    c3x024_c3b.root_call=c3x018_root_context_call;
    c3x024_c3b.root_move=Move(c3x018_root_context_move);
    for(int i=0;i<=p;++i) {
        auto* ancestor=ss-(p-i);
        c3x024_c3b.frames[i]=ancestor;
        c3x024_c3b.moves[i]=(i==p ? move : ancestor->currentMove);
    }
    c3x024_c3b_emit(pos,"ANCESTOR_SNAPSHOT",p,move,0,0,0,0,p);
}
void c3x024_c3b_child_return(const Position& pos,Search::Stack* ss,
                             Move move,int value) {
    if (!c3x024_c3b.armed || ss!=c3x024_c3b.frames[c3x024_c3b.top]
        || move!=c3x024_c3b.moves[c3x024_c3b.top]) return;
    c3x024_c3b.child_returned=true;
    c3x024_c3b_emit(pos,"CHILD_VALUE_RETURNED",ss->ply,move,value);
}
void c3x024_c3b_candidate(const Position& pos,Search::Stack* ss,
                          Move move,int value,int best,int alpha,int beta) {
    if(!c3x024_c3b.armed || !c3x024_c3b.child_returned
       || c3x024_c3b.expected<0
       || c3x018_root_context_call!=c3x024_c3b.root_call) return;
    const int p=c3x024_c3b.expected;
    if(ss!=c3x024_c3b.frames[p] || ss->ply!=p) return;
    if(move!=c3x024_c3b.moves[p] ||
       (p<c3x024_c3b.top && !c3x024_c3b.completed[p+1]) ||
       c3x024_c3b.candidate[p]) {
        c3x024_c3b.invalid=true;
        c3x024_c3b.armed=false;
        c3x024_c3b_emit(pos,"ANCESTOR_EDGE_AMBIGUOUS",p,move,value,best,alpha,beta);
        return;
    }
    c3x024_c3b.candidate[p]=true;
    c3x024_c3b_emit(pos,"PARENT_CANDIDATE_VALUE",p,move,value,best,alpha,beta);
    c3x024_c3b.expected=p-1;
}
void c3x024_c3b_node_return(const Position& pos,Search::Stack* ss,
                            int best,int alpha,int beta,Move leader) {
    if(!c3x024_c3b.armed || !c3x024_c3b.child_returned ||
       ss->ply<0 || ss->ply>c3x024_c3b.top ||
       c3x018_root_context_call!=c3x024_c3b.root_call) return;
    const int p=ss->ply;
    if(ss!=c3x024_c3b.frames[p] || !c3x024_c3b.candidate[p] ||
       c3x024_c3b.completed[p]) return;
    c3x024_c3b.completed[p]=true;
    c3x024_c3b_emit(pos,p==0?"ROOT_FRAME_RETURN":"FRAME_RETURN",
                    p,c3x024_c3b.moves[p],best,0,alpha,beta,int(leader));
}
"""
def once(s,old,new,tag):
    if s.count(old)!=1:raise ValueError("C3B_EXACT_ANCHOR_"+tag+"_"+str(s.count(old)))
    return s.replace(old,new,1)
def patch(s):
    if 'c3x024_c3b_candidate' in s:raise ValueError("C3B_ALREADY_PATCHED")
    s=once(s,STATE_ANCHOR,STATE_PATCH,"STATE")
    old='    c3x024_p2_emit(pos,std::strcmp(decision,"ACTUAL_CONTINUE")==0\n                         ? "GUARD_CONTINUE" : "GUARD_PASS", "exact_native_guard");'
    s=once(s,old,old+'\n    c3x024_c3b_guard(pos,ss,move,decision);',"EXACT_GUARD")
    old='    c3x024_p2_emit(pos,"CHILD_RETURNED_TO_PARENT",origin,0,value);'
    s=once(s,old,old+'\n    c3x024_c3b_child_return(pos,ss,move,value);',"CHILD_VALUE")
    main='      // Step 19. Undo move\n      pos.undo_move(move);'
    s=once(s,main,main+'\n      c3x024_c3b_candidate(pos,ss,move,int(value),int(bestValue),int(alpha),int(beta));',"MAIN_PARENT")
    q='        c3x024_p2_child_returned(pos,ss,move,"qsearch_child_return",int(value));\n        pos.undo_move(move);'
    s=once(s,q,q+'\n        c3x024_c3b_candidate(pos,ss,move,int(value),int(bestValue),int(alpha),int(beta));',"Q_PARENT")
    # Main and qsearch return are both final original Stockfish16 `return bestValue`,
    # distinguished by adjacent source chapter comments.
    old='    return bestValue;\n  }\n\n\n  // qsearch() is the quiescence search function'
    new='    c3x024_c3b_node_return(pos,ss,int(bestValue),int(alpha),int(beta),bestMove);\n'+old
    s=once(s,old,new,"MAIN_FINAL_RETURN")
    old='    return bestValue;\n  }\n\n\n  // value_to_tt() adjusts a mate or TB score'
    new='    c3x024_c3b_node_return(pos,ss,int(bestValue),int(alpha),int(beta),bestMove);\n'+old
    s=once(s,old,new,"Q_FINAL_RETURN")
    return s
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    f=Path(args.source)/"src/search.cpp";raw=f.read_bytes()
    b=patch(raw.decode()).encode();f.write_bytes(b)
    out=Path(args.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x024-P2-R2-source-native-root-ancestor-return-v1",
      "before_SHA256":hashlib.sha256(raw).hexdigest(),
      "after_SHA256":hashlib.sha256(b).hexdigest(),
      "opt_in":"C3X024_C3B_RETURN_OBS=1",
      "sites":["original presealed May11 qsearch","original presealed May2 quiet"],
      "source_events":["ANCESTOR_SNAPSHOT","CHILD_VALUE_RETURNED",
                       "PARENT_CANDIDATE_VALUE","FRAME_RETURN","ROOT_FRAME_RETURN"],
      "source_return_value_native_not_mediation_estimate":True,
      "no_mutations":True},sort_keys=True,indent=2)+"\n")
    print("C3X024_P2_R2_NATIVE_ANCESTOR_SOURCE_OVERLAY_READY",hashlib.sha256(b).hexdigest(),flush=True)
if __name__=="__main__":main()
