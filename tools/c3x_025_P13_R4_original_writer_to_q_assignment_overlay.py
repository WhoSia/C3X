#!/usr/bin/env python3
"""P13-R4: strict reversible source C++ instrumentation over P8/P11/P12.
Only exact actual native qsearch child TT returns are promoted to P13 edges.
Python owns source patching, never engine branch or scientific truth.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import (
    SHA,patch as p8,restore as undo8)
from c3x_025_P11_native_stratified_real_TT_return_SEE_guard_root_update_overlay import (
    patch_prepatched as p11,restore as undo11)
from c3x_025_P12_native_source_recursive_frame_TT_return_overlay import (
    patch_prepatched as p12,restore as undo12)
TT_HOOK = "void c3x025_p12_leave(uint64_t frameid) {"
EXIT = "    c3x025_p12_frames.pop_back();"
QCALL = "        value = -qsearch<nodeType>(pos, ss+1, -beta, -alpha, depth - 1);"
QBEST = "            bestValue = value;"
SEARCH_HOOK = "struct C3X025_P12_SearchScope {"
R4_OLD_MARK = "    c3x025_p12_mark_tt_return(value);\n}"
R4_NEW_MARK = "    c3x025_p12_mark_tt_return(value);\n    c3x025_p13_r4_mark(slot,key,value);\n}"
P13_CPP = r"""
// C3X025-P13 actual original qsearch direct TT-child return to parent variable.
// P12 frame IDs are reused; this structure is metadata only.
struct C3X025_P13_Exit {
    uint64_t id=0,parent=0,root=0;
    bool is_tt=false;
    int tt_score=0;
    uint64_t original_writer=0,original_return_serial=0;
    bool original_writer_key_exact=false;
};
struct C3X025_P13_Assignment {
    uint64_t child=0,parent=0,root=0;
    int assigned=0,move=0;
    bool valid=false;
};
static thread_local C3X025_P13_Exit c3x025_p13_last_exit;
static thread_local C3X025_P13_Assignment c3x025_p13_last_assigned;
static thread_local unsigned c3x025_p13_qcount=0,c3x025_p13_bestcount=0;
static thread_local bool c3x025_p13_qcensored=false,c3x025_p13_bestcensored=false;

// C3X-P13-R4: witness the physical original TT score writer at real return.
struct C3X025_P13_R4_Origin {
    uint64_t id=0, writer=0, return_serial=0;
    int original_tt_value=0;
    bool exact=false;
};
static thread_local C3X025_P13_R4_Origin c3x025_p13_r4_origin;
void c3x025_p13_r4_mark(const TTEntry* slot,Key key,int value) {
    if (!c3x025_p8_on()) return;
    if (c3x025_p12_frames.empty()) std::abort();
    const auto& frame=c3x025_p12_frames.back();
    auto it=c3x025_p8_meta.find(slot);
    uint64_t writer=it==c3x025_p8_meta.end()?0:it->second.score_serial;
    bool exact=it!=c3x025_p8_meta.end() && writer &&
               it->second.score_key==key;
    c3x025_p13_r4_origin={frame.id,writer,c3x025_p8_clock,value,exact};
}

void c3x025_p13_qassignment(int assigned,int move,int ply) {
    if (!c3x025_p8_on()) return;
    if (c3x025_p12_frames.empty()) std::abort();
    const auto& parent=c3x025_p12_frames.back();
    const auto child=c3x025_p13_last_exit;
    if (!child.id || child.parent!=parent.id || child.root!=parent.root) std::abort();
    c3x025_p13_last_assigned={};
    if (!child.is_tt) return; // Non-TT child: no P13 direct-TT claim.
    if (assigned!=-child.tt_score) std::abort(); // Actual negamax assignment.
    c3x025_p13_last_assigned={child.id,parent.id,parent.root,assigned,move,true};
    if (c3x025_p13_qcount++>=24) {
        if (!c3x025_p13_qcensored) {
            c3x025_p13_qcensored=true;
            sync_cout << "info string c3x025_p13 kind=Q_DIRECT_CENSORED cap=24"
                      << sync_endl;
        }
        return;
    }
    sync_cout << "info string c3x025_p13 kind=Q_DIRECT_PARENT_ASSIGN"
              << " serial=" << ++c3x025_p8_clock
              << " child_id=" << child.id << " parent_id=" << parent.id
              << " root_id=" << parent.root
              << " child_tt_score=" << child.tt_score
              << " writer_serial=" << child.original_writer
              << " return_serial=" << child.original_return_serial
              << " writer_exact=" << int(child.original_writer_key_exact)
              << " assigned_score=" << assigned
              << " move_code=" << move << " ply=" << ply << sync_endl;
}
void c3x025_p13_qbest(int value,int move,int ply) {
    if (!c3x025_p8_on()) return;
    auto a=c3x025_p13_last_assigned;
    if (!a.valid || c3x025_p12_frames.empty() ||
        a.parent!=c3x025_p12_frames.back().id ||
        a.assigned!=value || a.move!=move) return;
    c3x025_p13_last_assigned={};
    if (c3x025_p13_bestcount++>=24) {
        if (!c3x025_p13_bestcensored) {
            c3x025_p13_bestcensored=true;
            sync_cout << "info string c3x025_p13 kind=Q_BEST_CENSORED cap=24"
                      << sync_endl;
        }
        return;
    }
    sync_cout << "info string c3x025_p13 kind=Q_BEST_VALUE_ASSIGNED"
              << " serial=" << ++c3x025_p8_clock
              << " child_id=" << a.child << " parent_id=" << a.parent
              << " root_id=" << a.root << " assigned_score=" << value
              << " move_code=" << move << " ply=" << ply
              << " final_root_mediation=0" << sync_endl;
}
"""
FWD = """void c3x025_p13_qassignment(int,int,int);
void c3x025_p13_qbest(int,int,int);
"""

def patch(stage):
    if set(stage)!=set(SHA):raise ValueError("P13_REQUIRED_TWO_PREPATCHED_FILES")
    t=stage["tt.cpp"].decode()
    s=stage["search.cpp"].decode()
    for label,content,needle in (
        ("TT_HOOK",t,TT_HOOK),("P12_LEAVE",t,EXIT),
        ("P12_SEARCH_SCOPE",s,SEARCH_HOOK),
        ("QSEARCH_CHILD",s,QCALL),("QSEARCH_BEST",s,QBEST)):
        if content.count(needle)!=1:raise ValueError("P13_EXACT_ANCHOR_"+label)
    t=t.replace(TT_HOOK,P13_CPP+"\n"+TT_HOOK,1)
    t=t.replace(EXIT,"    if (e.tt_return && (c3x025_p13_r4_origin.id!=e.id || c3x025_p13_r4_origin.original_tt_value!=e.tt_value)) std::abort();\n    c3x025_p13_last_exit = {e.id,e.parent,e.root,e.tt_return,e.tt_value,\n        e.tt_return?c3x025_p13_r4_origin.writer:0,\n        e.tt_return?c3x025_p13_r4_origin.return_serial:0,\n        e.tt_return?c3x025_p13_r4_origin.exact:false};\n"+EXIT,1)
    if t.count(R4_OLD_MARK)!=1:raise ValueError("P13_R4_UNIQUE_ORIGINAL_NATIVE_TT_RETURN_ANCHOR")
    t=t.replace(R4_OLD_MARK,R4_NEW_MARK,1)
    s=s.replace(SEARCH_HOOK,FWD+SEARCH_HOOK,1)
    s=s.replace(QCALL,QCALL+"\n        c3x025_p13_qassignment(int(value),int(ss->currentMove),ss->ply);",1)
    s=s.replace(QBEST,QBEST+"\n            c3x025_p13_qbest(int(value),int(ss->currentMove),ss->ply);",1)
    result={"tt.cpp":t.encode(),"search.cpp":s.encode()}
    if undo(result)!=stage:raise ValueError("P13_REVERSE_P12_BYTES_FAILED")
    return result

def undo(post):
    t=post["tt.cpp"].decode()
    s=post["search.cpp"].decode()
    t=t.replace("    if (e.tt_return && (c3x025_p13_r4_origin.id!=e.id || c3x025_p13_r4_origin.original_tt_value!=e.tt_value)) std::abort();\n    c3x025_p13_last_exit = {e.id,e.parent,e.root,e.tt_return,e.tt_value,\n        e.tt_return?c3x025_p13_r4_origin.writer:0,\n        e.tt_return?c3x025_p13_r4_origin.return_serial:0,\n        e.tt_return?c3x025_p13_r4_origin.exact:false};\n"+EXIT,EXIT,1)
    t=t.replace(P13_CPP+"\n","",1)
    s=s.replace(FWD+SEARCH_HOOK,SEARCH_HOOK,1)
    s=s.replace(QCALL+"\n        c3x025_p13_qassignment(int(value),int(ss->currentMove),ss->ply);",QCALL,1)
    s=s.replace(QBEST+"\n            c3x025_p13_qbest(int(value),int(ss->currentMove),ss->ply);",QBEST,1)
    if t.count(R4_NEW_MARK)!=1:raise ValueError("P13_R4_UNIQUE_REVERSE_NATIVE_RETURN")
    t=t.replace(R4_NEW_MARK,R4_OLD_MARK,1)
    return {"tt.cpp":t.encode(),"search.cpp":s.encode()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args()
    root=Path(a.root)/"src"
    raw={n:(root/n).read_bytes() for n in SHA}
    p8s,_=p8(raw)
    p11s=p11(p8s)
    p12s=p12(p11s)
    p13s=patch(p12s)
    if undo8(undo11(undo12(undo(p13s))))!=raw:
        raise ValueError("P13_ALL_FOUR_SOURCE_LAYERS_NOT_BYTE_RESTORED")
    for n,blob in p13s.items():(root/n).write_bytes(blob)
    report={"schema":"c3x025-P13-R4-same-native-run-original-writer-return-parent-qassignment-v1",
      "original_upstream_SHA256":SHA,
      "P8_then_P11_then_P12_reverse_exact_original_source_byte_equal":True,
      "P8_P11_P12_P13_exact_original_inverse":True,
      "P13_source_SHA256":{n:hashlib.sha256(v).hexdigest() for n,v in p13s.items()},
      "P13_coverage":"QSEARCH_RECURSIVE_CHILD_CALL_ONLY",
      "R4_original_full64_score_field_writer_at_actual_TT_return":True,
      "P11_first24_censor_explicit":True,
      "remaining_native_call_sites":"CENSORED_SITE",
      "natural_TT_SEE_root_mediation_proven":False,
      "engine_strength_improvement_proven":False}
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("P13_NATIVE_SOURCE_EXACT_REVERSE",report,flush=True)
if __name__=="__main__":main()
