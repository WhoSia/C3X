#!/usr/bin/env python3
"""C3X0.25-P12 precommitted source-layer stack identities, actual TT-return
frame-unwind witness. No original TT, SEE or search value modified.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import (
    SHA,patch as p8_patch,restore as p8_restore)
from c3x_025_P11_native_stratified_real_TT_return_SEE_guard_root_update_overlay import (
    patch_prepatched as p11_patch, restore as p11_restore)
P12_TT=r"""
// C3X025-P12 actual recursive native C++ call stack, *single-thread* observer.
struct C3X025_P12_Frame {
   uint64_t id=0,parent=0,root=0;
   int ply=0,depth=0;
   bool tt_return=false;
   int tt_value=0;
};
static thread_local std::vector<C3X025_P12_Frame> c3x025_p12_frames;
static thread_local uint64_t c3x025_p12_next_id=0;
static thread_local unsigned c3x025_p12_public_return_n=0;
static thread_local bool c3x025_p12_returns_censored=false;
uint64_t c3x025_p12_enter(int ply,int depth,bool root) {
    if (!c3x025_p8_on()) return 0;
    C3X025_P12_Frame frame;
    frame.id=++c3x025_p12_next_id;
    frame.parent=c3x025_p12_frames.empty()?0:c3x025_p12_frames.back().id;
    frame.root=root?frame.id:
        (c3x025_p12_frames.empty()?0:c3x025_p12_frames.back().root);
    frame.ply=ply;frame.depth=depth;
    c3x025_p12_frames.push_back(frame);
    return frame.id;
}
void c3x025_p12_mark_tt_return(int value) {
    if (!c3x025_p8_on()) return;
    if (c3x025_p12_frames.empty()) return;
    c3x025_p12_frames.back().tt_return=true;
    c3x025_p12_frames.back().tt_value=value;
}
void c3x025_p12_leave(uint64_t frameid) {
    if (!c3x025_p8_on()) return;
    if (c3x025_p12_frames.empty() || c3x025_p12_frames.back().id!=frameid)
        std::abort();  // A broken observer frame invalidates this experiment.
    auto e=c3x025_p12_frames.back();
    if (e.tt_return) {
        if (c3x025_p12_public_return_n++<24) {
            sync_cout << "info string c3x025_p12 kind=TT_RETURN_FRAME_EXIT"
                      << " call_id=" << e.id << " parent_id=" << e.parent
                      << " root_id=" << e.root << " value=" << e.tt_value
                      << " serial=" << ++c3x025_p8_clock << sync_endl;
        } else if (!c3x025_p12_returns_censored) {
            c3x025_p12_returns_censored=true;
            sync_cout << "info string c3x025_p12 kind=RETURN_CENSORED cap=24"
                      << sync_endl;
        }
    }
    c3x025_p12_frames.pop_back();
}
void c3x025_p12_source_event(uint64_t serial,const char* kind) {
    if (!c3x025_p8_on() || c3x025_p12_frames.empty()) return;
    const auto& f=c3x025_p12_frames.back();
    sync_cout << "info string c3x025_p12 kind=SOURCE_EVENT"
              << " serial=" << serial << " source_kind=" << kind
              << " call_id=" << f.id << " parent_id=" << f.parent
              << " root_id=" << f.root << " ply=" << f.ply
              << " depth=" << f.depth << sync_endl;
}
"""
TT_TARGET="// C3X025-P11 class specific native executable operator evidence."
TT_INCLUDE="#include <unordered_map>\n"
SEARCH_FORWARD="void c3x025_p11_log(const char*,int,int,int,int,int,int,int,uint64_t,bool);"
SEARCH_DEF=SEARCH_FORWARD+"""
uint64_t c3x025_p12_enter(int,int,bool);
void c3x025_p12_leave(uint64_t);
struct C3X025_P12_SearchScope {
   uint64_t frame_id;
   C3X025_P12_SearchScope(int ply,int depth,bool root) :
      frame_id(c3x025_p12_enter(ply,depth,root)) {}
   ~C3X025_P12_SearchScope() {c3x025_p12_leave(frame_id);}
};
"""
SEARCH_MAIN="    constexpr bool rootNode = nodeType == Root;"
SEARCH_MAIN_NEW=SEARCH_MAIN+"\n    C3X025_P12_SearchScope c3x025_p12_scope(ss->ply,depth,rootNode);"
SEARCH_Q="    constexpr bool PvNode = nodeType == PV;\n\n    assert(alpha >= -VALUE_INFINITE"
SEARCH_Q_NEW="    constexpr bool PvNode = nodeType == PV;\n    C3X025_P12_SearchScope c3x025_p12_scope(ss->ply,depth,false);\n\n    assert(alpha >= -VALUE_INFINITE"
TT_EVENT='''              << " score_writer_exact=" << int(score_key_exact) << sync_endl;
}'''
TT_EVENT_NEW='''              << " score_writer_exact=" << int(score_key_exact) << sync_endl;
    c3x025_p12_source_event(serial,cls);
}'''
TT_RETURN='''    c3x025_p11_log(main_return?"TT_MAIN_RETURN":"TT_Q_RETURN",ply,depth,
                   value,alpha,beta,1,0,writer,exact);
}'''
TT_RETURN_NEW='''    c3x025_p11_log(main_return?"TT_MAIN_RETURN":"TT_Q_RETURN",ply,depth,
                   value,alpha,beta,1,0,writer,exact);
    c3x025_p12_mark_tt_return(value);
}'''
def patch_prepatched(pre):
    if set(pre)!=set(SHA):raise ValueError("P12_EXPECT_P8_P11_SOURCE_FILES")
    t=pre["tt.cpp"].decode()
    s=pre["search.cpp"].decode()
    patches_tt=(("include",TT_INCLUDE,TT_INCLUDE+"#include <vector>\n"),
      ("stack",TT_TARGET,P12_TT+"\n"+TT_TARGET),
      ("event",TT_EVENT,TT_EVENT_NEW),
      ("native-return",TT_RETURN,TT_RETURN_NEW))
    patches_search=(("forward",SEARCH_FORWARD,SEARCH_DEF),
       ("main-enter",SEARCH_MAIN,SEARCH_MAIN_NEW),
       ("q-enter",SEARCH_Q,SEARCH_Q_NEW))
    for name,old,new in patches_tt:
        if t.count(old)!=1:raise ValueError("P12_TT_NATIVE_SOURCE_ANCHOR_"+name+"_"+str(t.count(old)))
        t=t.replace(old,new,1)
    for name,old,new in patches_search:
        if s.count(old)!=1:raise ValueError("P12_SEARCH_NATIVE_SOURCE_ANCHOR_"+name+"_"+str(s.count(old)))
        s=s.replace(old,new,1)
    changed={"tt.cpp":t.encode(),"search.cpp":s.encode()}
    if restore(changed)!=pre:raise AssertionError("P12_CANNOT_RESTORE_P11_PREPATCHED_SOURCE")
    return changed
def restore(patched):
    t=patched["tt.cpp"].decode()
    s=patched["search.cpp"].decode()
    patches_tt=(("include",TT_INCLUDE,TT_INCLUDE+"#include <vector>\n"),
      ("stack",TT_TARGET,P12_TT+"\n"+TT_TARGET),
      ("event",TT_EVENT,TT_EVENT_NEW),
      ("native-return",TT_RETURN,TT_RETURN_NEW))
    patches_search=(("forward",SEARCH_FORWARD,SEARCH_DEF),
       ("main-enter",SEARCH_MAIN,SEARCH_MAIN_NEW),
       ("q-enter",SEARCH_Q,SEARCH_Q_NEW))
    for name,old,new in reversed(patches_tt):
        if t.count(new)!=1:raise ValueError("P12_TT_REVERSE_"+name)
        t=t.replace(new,old,1)
    for name,old,new in reversed(patches_search):
        if s.count(new)!=1:raise ValueError("P12_SEARCH_REVERSE_"+name)
        s=s.replace(new,old,1)
    return {"tt.cpp":t.encode(),"search.cpp":s.encode()}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();path=Path(a.root)/"src"
    raw={n:(path/n).read_bytes() for n in SHA}
    p8,_=p8_patch(raw)
    p11=p11_patch(p8)
    p12=patch_prepatched(p11)
    if p8_restore(p11_restore(restore(p12)))!=raw:
        raise ValueError("P12_ALL_THREE_NATIVE_SOURCE_LAYER_REVERSES_FAILED")
    for n,b in p12.items():(path/n).write_bytes(b)
    d={"schema":"c3x025-P12-SF16-native-call-frame-source-TT-return-unwind-v1",
       "original_upstream_SHA256":SHA,
       "P8_then_P11_then_P12_reverse_exact_original_source_byte_equal":True,
       "instrumented_cpp_SHA256":{n:hashlib.sha256(v).hexdigest() for n,v in p12.items()},
       "call_identity":"thread_local_monotone_call_id_and_exact_parent_id",
       "TT_return_marked_at_actual_TT_return_pre_unwind":True,
       "SOURCE_EVENT_every_preregistered_P11_class":True,
       "original_search_value_mutated":False,
       "TT_to_exact_parent_call_edge_possible":True,
       "actual_parent_value_consumed_and_root_impact_proven":False}
    dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("C3X025_P12_EXACT_NATIVE_THREE_LAYER_ORIGINAL_REVERSE",d,flush=True)
if __name__=="__main__":main()
