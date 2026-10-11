#!/usr/bin/env python3
"""C3X0.25 P11 exact SF16 P8-layer stratified rare operator observer.
A successful branch-predicate is NOT a native TT return when rule50>=90.
All P11 output independent of P8 first256 FIFO cap; observer-only.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import (
    patch as p8_patch,restore as p8_restore,SHA)
TT_ADDED= r"""
// C3X025-P11 class specific native executable operator evidence.
static thread_local unsigned c3x025_p11_cutoff_n=0;
static thread_local unsigned c3x025_p11_see_n=0;
static thread_local unsigned c3x025_p11_root_n=0;
static thread_local bool c3x025_p11_cutoff_censor=false;
static thread_local bool c3x025_p11_see_censor=false;
static thread_local bool c3x025_p11_root_censor=false;
void c3x025_p11_log(const char* cls,int ply,int depth,int value,
                    int alpha,int beta,int result,int move_code,
                    uint64_t score_writer,bool score_key_exact) {
    if (!c3x025_p8_on()) return;
    const uint64_t serial=++c3x025_p8_clock;
    const bool is_cutoff=std::strcmp(cls,"TT_MAIN_RETURN")==0 ||
                         std::strcmp(cls,"TT_Q_RETURN")==0;
    const bool is_see=std::strcmp(cls,"SEE_QUIET_GUARD")==0 ||
                      std::strcmp(cls,"SEE_QSEARCH_GUARD")==0;
    unsigned& count=is_cutoff ? c3x025_p11_cutoff_n :
                    is_see ? c3x025_p11_see_n : c3x025_p11_root_n;
    bool& censored=is_cutoff ? c3x025_p11_cutoff_censor :
                   is_see ? c3x025_p11_see_censor : c3x025_p11_root_censor;
    if (count++ >= 24) {
        if (!censored) {
            censored=true;
            sync_cout << "info string c3x025_p11 kind=CLASS_CENSORED"
                      << " class=" << (is_cutoff ? "CUTOFF" : is_see ? "SEE" : "ROOT")
                      << " cap=24 serial=" << serial << sync_endl;
        }
        return;
    }
    sync_cout << "info string c3x025_p11 kind=" << cls
              << " serial=" << serial << " ply=" << ply << " depth=" << depth
              << " value=" << value << " alpha=" << alpha << " beta=" << beta
              << " result=" << result << " move_code=" << move_code
              << " score_writer=" << score_writer
              << " score_writer_exact=" << int(score_key_exact) << sync_endl;
}
void c3x025_p11_return(const TTEntry* slot,Key key,bool main_return,
                       int ply,int depth,int value,int alpha,int beta) {
    if (!c3x025_p8_on()) return;
    auto it=c3x025_p8_meta.find(slot);
    const uint64_t writer=it==c3x025_p8_meta.end()?0:it->second.score_serial;
    const bool exact=it!=c3x025_p8_meta.end() && writer &&
                     it->second.score_key==key;
    c3x025_p11_log(main_return?"TT_MAIN_RETURN":"TT_Q_RETURN",ply,depth,
                   value,alpha,beta,1,0,writer,exact);
}
"""
# Anchor as exactly P8 layer; before c3x025_p8_consume.
TT_ANCHOR="// Source-native *actual assignment* or actual numeric cutoff, never guessed"
SEARCH_FORWARD="void c3x025_p8_consume(const TTEntry*, Key,const char*,bool,int,int);"
SEARCH_FORWARD_PLUS=SEARCH_FORWARD+"""
void c3x025_p11_return(const TTEntry*,Key,bool,int,int,int,int,int);
void c3x025_p11_log(const char*,int,int,int,int,int,int,int,uint64_t,bool);
"""
MAIN_RETURN="""        if (pos.rule50_count() < 90)
            return ttValue;"""
MAIN_REPLACE="""        if (pos.rule50_count() < 90) {
            c3x025_p11_return(tte,posKey,true,ss->ply,depth,int(ttValue),int(alpha),int(beta));
            return ttValue;
        }"""
Q_RETURN='''        c3x025_p8_consume(tte,posKey,"Q_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,ttDepth,ss->ply);
        return ttValue;'''
Q_REPLACE='''        c3x025_p8_consume(tte,posKey,"Q_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,ttDepth,ss->ply);
        c3x025_p11_return(tte,posKey,false,ss->ply,ttDepth,int(ttValue),int(alpha),int(beta));
        return ttValue;'''
QUIET='''              if (!pos.see_ge(move, Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth)))
                  continue;'''
QUIET_NEW='''              if (!([&]() {
                  const Value threshold=Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth);
                  const bool pass=pos.see_ge(move,threshold);
                  c3x025_p11_log("SEE_QUIET_GUARD",ss->ply,depth,int(threshold),
                                 int(alpha),int(beta),int(pass),int(move),0,false);
                  return pass;
              }()))
                  continue;'''
QS='''            if (!pos.see_ge(move, Value(-95)))
                continue;'''
QS_NEW='''            if (!([&]() {
                const bool pass=pos.see_ge(move,Value(-95));
                c3x025_p11_log("SEE_QSEARCH_GUARD",ss->ply,depth,-95,
                               int(alpha),int(beta),int(pass),int(move),0,false);
                return pass;
            }()))
                continue;'''
ROOT_SCORE="              rm.score =  rm.uciScore = value;"
ROOT_SCORE_NEW=ROOT_SCORE+'''
              c3x025_p11_log("ROOT_SCORE_UPDATE",ss->ply,depth,int(value),
                              int(alpha),int(beta),1,int(move),0,false);'''
SEARCH_REPL=(
    ("forward",SEARCH_FORWARD,SEARCH_FORWARD_PLUS),
    ("main-actual-return",MAIN_RETURN,MAIN_REPLACE),
    ("q-actual-return",Q_RETURN,Q_REPLACE),
    ("SEE-quiet-prune",QUIET,QUIET_NEW),
    ("SEE-q-prune",QS,QS_NEW),
    ("root-score-update",ROOT_SCORE,ROOT_SCORE_NEW),
)
def patch_prepatched(files:dict[str,bytes]):
    if set(files)!=set(SHA):raise ValueError("P11_EXPECT_EXACT_P8_PREPATCHED_TT_SEARCH")
    t=files["tt.cpp"].decode()
    s=files["search.cpp"].decode()
    if t.count(TT_ANCHOR)!=1:raise ValueError("P11_TT_ANCHOR_DRIFT")
    t=t.replace(TT_ANCHOR,TT_ADDED+"\n"+TT_ANCHOR,1)
    for name,old,new in SEARCH_REPL:
        if s.count(old)!=1:raise ValueError("P11_SF16_SOURCE_ANCHOR_"+name+"_"+str(s.count(old)))
        s=s.replace(old,new,1)
    patched={"tt.cpp":t.encode(),"search.cpp":s.encode()}
    if restore(patched)!=files:raise ValueError("P11_IRREVERSIBLE_NATIVE_SOURCE")
    return patched
def restore(patched):
    t=patched["tt.cpp"].decode()
    s=patched["search.cpp"].decode()
    if t.count(TT_ADDED)!=1:raise ValueError("P11_CANNOT_REMOVE_NATIVE_CUTOFF_LOGGER")
    t=t.replace(TT_ADDED+"\n","",1)
    for name,old,new in reversed(SEARCH_REPL):
        if s.count(new)!=1:raise ValueError("P11_CANNOT_REVERSE_"+name)
        s=s.replace(new,old,1)
    return {"tt.cpp":t.encode(),"search.cpp":s.encode()}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args()
    d=Path(a.root)/"src"
    native={n:(d/n).read_bytes() for n in SHA}
    original_p8,p8_manifest=p8_patch(native)
    if p8_restore(original_p8)!=native:raise ValueError("P11_P8_ANCHORS_NO_LONGER_EXACT")
    latest=patch_prepatched(original_p8)
    if p8_restore(restore(latest))!=native:raise ValueError("P11_NOT_BOTH_LAYERS_BYTE_RESTORABLE")
    for n,b in latest.items():(d/n).write_bytes(b)
    report={"schema":"c3x025-P11-SF16-P8-plus-stratified-TT-real-return-SEE-guard-root-score-overlay-v1",
     "original_upstream_source_SHA256":SHA,
     "P8_source_SHA256":{n:hashlib.sha256(v).hexdigest() for n,v in original_p8.items()},
     "P11_source_SHA256":{n:hashlib.sha256(v).hexdigest() for n,v in latest.items()},
     "both_layers_reverse_to_identical_upstream_bytes":True,
     "native_SF16_GPL_binary_not_exported":True,
     "source_event_classes":{"TT_REAL_RETURN":24,"SEE_GUARD":24,"ROOT_SCORE_UPDATE":24},
     "actual_main_TT_return_requires_rule50_below90":True,
     "same_thread_clock":"c3x025_p8_clock","causal_parent_return_link_proven":False,
     "original_stored_TT_and_SEE_results_never_modified":True}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X025_P11_SOURCE_DOUBLE_REVERSE_SHA_GATE",report,flush=True)
if __name__=="__main__":main()
