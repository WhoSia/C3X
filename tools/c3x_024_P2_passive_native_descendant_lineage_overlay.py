#!/usr/bin/env python3
"""C3X 0.24 P2: passive exact-source C2 guard to C3 child-execution witness.
Requires pinned T3 source and T4 branch overlay; makes no move/TT/SEE decisions.
Log status is strictly conditional on observing EXACT original T3 source guard.
"""
import argparse,hashlib,json
from pathlib import Path

STATE_ANCHOR='thread_local unsigned long long c3x023_t4_last_sequence=0;'
STATE_NEW=STATE_ANCHOR+r"""
// P2: single-thread native, bounded to one preselected exact T3/T4 event per run.
struct C3X024_P2_Pending {
    bool active=false;
    bool did_move=false;
    bool child_entered=false;
    const Search::Stack* frame=nullptr;
    Key parent=0, expected_child=0;
    Move move=MOVE_NONE;
    unsigned long long sequence=0, ordinal=0;
    const char* site="";
};
thread_local C3X024_P2_Pending c3x024_p2;
bool c3x024_p2_enabled() {
    const char* s=std::getenv("C3X024_P2_LINEAGE_OBS");
    return s && std::strcmp(s,"1")==0;
}
void c3x024_p2_emit(const Position& pos,const char* event, const char* origin,
                     int child_depth=0, int child_value=0) {
    sync_cout << "info string c3x024_p2_path"
              << " event=" << event
              << " site=" << c3x024_p2.site
              << " origin=" << origin
              << " key64=" << std::uint64_t(pos.key())
              << " parent64=" << std::uint64_t(c3x024_p2.parent)
              << " expected_child64=" << std::uint64_t(c3x024_p2.expected_child)
              << " native_move=" << int(c3x024_p2.move)
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << " exact_sequence=" << c3x024_p2.sequence
              << " event_ordinal=" << ++c3x024_p2.ordinal
              << " child_depth=" << child_depth
              << " child_value=" << child_value
              << " did_move=" << int(c3x024_p2.did_move)
              << " child_entered=" << int(c3x024_p2.child_entered)
              << sync_endl;
}
void c3x024_p2_guard(const Position& pos,Search::Stack* ss,Move move,
                     const char* site,const char* decision) {
    if (!c3x024_p2_enabled()) return;
    c3x024_p2 = {};
    c3x024_p2.frame=ss;
    c3x024_p2.parent=pos.key();
    c3x024_p2.move=move;
    c3x024_p2.site=site;
    c3x024_p2.sequence=c3x023_t4_last_sequence;
    // Computing the expected key is a pure source-native board lookup.
    c3x024_p2.expected_child=std::strcmp(decision,"PASSED_SEE_GUARD")==0
                                   ? pos.key_after(move) : Key(0);
    c3x024_p2.active=std::strcmp(decision,"PASSED_SEE_GUARD")==0;
    c3x024_p2_emit(pos,std::strcmp(decision,"ACTUAL_CONTINUE")==0
                         ? "GUARD_CONTINUE" : "GUARD_PASS", "exact_native_guard");
}
void c3x024_p2_after_do(const Position& pos,Search::Stack* ss,Move move,
                        const char* origin) {
    if (!c3x024_p2.active || c3x024_p2.did_move ||
        ss!=c3x024_p2.frame || move!=c3x024_p2.move ||
        pos.key()!=c3x024_p2.expected_child)
        return;
    c3x024_p2.did_move=true;
    c3x024_p2_emit(pos,"DO_MOVE_EXECUTED",origin);
}
void c3x024_p2_child_entry(const Position& pos,Search::Stack* ss,
                           const char* origin,int depth) {
    if (!c3x024_p2.active || !c3x024_p2.did_move ||
        c3x024_p2.child_entered ||
        ss!=c3x024_p2.frame+1 ||
        pos.key()!=c3x024_p2.expected_child)
        return;
    c3x024_p2.child_entered=true;
    c3x024_p2_emit(pos,"CHILD_ENTERED",origin,depth);
}
void c3x024_p2_child_returned(const Position& pos,Search::Stack* ss,Move move,
                              const char* origin,int value) {
    if (!c3x024_p2.active || !c3x024_p2.did_move ||
        ss!=c3x024_p2.frame || move!=c3x024_p2.move ||
        pos.key()!=c3x024_p2.expected_child)
        return;
    c3x024_p2_emit(pos,"CHILD_RETURNED_TO_PARENT",origin,0,value);
    c3x024_p2.active=false;
}
"""

def replace_once(s,old,new,label):
    if s.count(old)!=1:
        raise ValueError("C3X024_P2_NONUNIQUE_SOURCE_"+label+"_"+str(s.count(old)))
    return s.replace(old,new,1)

def patch(s):
    if "c3x024_p2_child_entry" in s: raise ValueError("C3X024_P2_ALREADY_PATCHED")
    s=replace_once(s,STATE_ANCHOR,STATE_NEW,"P2_STATE")
    for site in ("quiet_prune","qsearch_prune"):
        for decision in ("ACTUAL_CONTINUE","PASSED_SEE_GUARD"):
            old='c3x023_t4_branch(pos,"'+site+'","'+decision+'");'
            new='(c3x024_p2_guard(pos,ss,move,"'+site+'","'+decision+'"), '+old[:-1]+');'
            s=replace_once(s,old,new,site+"_"+decision)
    main_signature='Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {'
    qsearch_signature='Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {'
    s=replace_once(s,main_signature,main_signature+'\n    c3x024_p2_child_entry(pos,ss,"main_search",int(depth));',"MAIN_ENTRY")
    s=replace_once(s,qsearch_signature,qsearch_signature+'\n    c3x024_p2_child_entry(pos,ss,"qsearch",int(depth));',"QSEARCH_ENTRY")
    main_do='      // Step 16. Make the move\n      pos.do_move(move, st, givesCheck);'
    s=replace_once(s,main_do,main_do+'\n      c3x024_p2_after_do(pos,ss,move,"main_do_move");',"MAIN_DO")
    q_do='        // Step 7. Make and search the move\n        pos.do_move(move, st, givesCheck);'
    s=replace_once(s,q_do,q_do+'\n        c3x024_p2_after_do(pos,ss,move,"qsearch_do_move");',"Q_DO")
    main_undo='      // Step 19. Undo move\n      pos.undo_move(move);'
    s=replace_once(s,main_undo,'      c3x024_p2_child_returned(pos,ss,move,"main_child_return",int(value));\n'+main_undo,"MAIN_RETURN")
    q_return='        value = -qsearch<nodeType>(pos, ss+1, -beta, -alpha, depth - 1);\n        pos.undo_move(move);'
    s=replace_once(s,q_return,'        value = -qsearch<nodeType>(pos, ss+1, -beta, -alpha, depth - 1);\n        c3x024_p2_child_returned(pos,ss,move,"qsearch_child_return",int(value));\n        pos.undo_move(move);',"Q_RETURN")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    raw=f.read_bytes()
    patched=patch(raw.decode("utf8")).encode()
    f.write_bytes(patched)
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x024-P2-actual-native-child-entry-and-return-witness-v1",
      "before_SHA256":hashlib.sha256(raw).hexdigest(),
      "after_SHA256":hashlib.sha256(patched).hexdigest(),
      "exact_sites":["quiet_prune","qsearch_prune"],
      "enabled_by":"C3X024_P2_LINEAGE_OBS=1, only with T4 exact source guard",
      "source_anchors":["actual C2 continue/pass","main/qsearch do_move",
                        "main/qsearch child search entry","source child return before undo"],
      "fail_closed_if_no_matching_source_event":True,
      "no_TT_SEE_or_move_mutation":True,
      "development_only":True,
      "not_full_recursive_decision_mediation":True
    },sort_keys=True,indent=2)+"\n")
    print("C3X024_P2_PASSIVE_SOURCE_DESCENDANT_OVERLAY_READY",hashlib.sha256(patched).hexdigest())

if __name__=="__main__":
    main()
