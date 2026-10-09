#!/usr/bin/env python3
"""Independent native *post-assignment* TT value-as-evaluation use witness.

Does not substitute the meaning of V reader_block with source-native use.
When optional PASSIVE_SECOND is enabled, first V reader still blocked but
second matching V source reader is explicitly allowed to execute assignment.
Read-only watcher after the original assignment records actual engine use.
"""
import argparse,hashlib,json
from pathlib import Path

FN=r"""
// C3X019 native TT score-as-eval ASSIGNMENT observer; source-only diagnostic.
namespace {
uint64_t c3x019_native_use_count=0;
void c3x019_native_tt_eval_used(Key key, const TTEntry* entry,
    int ply,int depth,int alpha,int beta,int effective,const char* site) {
    const char* k=std::getenv("C3X019_NATIVE_USE_WATCH_KEY64");
    const char* c=std::getenv("C3X019_NATIVE_USE_WATCH_ROOT_CALL");
    if (!k || !c) return;
    if (uint64_t(key)!=std::strtoull(k,nullptr,10)
        || c3x018_root_context_call!=std::strtoull(c,nullptr,10))
        return;
    const uint64_t num=++c3x019_native_use_count;
    if (num>64) {
        if (num==65) sync_cout << "info string c3x019_native_use kind=censored" << sync_endl;
        return;
    }
    uint64_t epoch=0,serial=0,writer_key=0;
    int stored_depth=-1;
    c3x018_read_source_writer_epoch(key,entry,epoch,serial,writer_key,stored_depth);
    sync_cout << "info string c3x019_native_use kind=used"
              << " site=" << site << " key64=" << uint64_t(key)
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << " ply=" << ply << " depth=" << depth
              << " alpha=" << alpha << " beta=" << beta
              << " effective_tt_value=" << effective
              << " shadow_epoch=" << epoch
              << " shadow_serial=" << serial
              << " shadow_key64=" << writer_key
              << " full64_match=" << int(writer_key==uint64_t(key))
              << " raw_depth=" << int(entry->depth())
              << " raw_bound=" << int(entry->bound())
              << " raw_value=" << int(entry->value())
              << " raw_eval=" << int(entry->eval())
              << " raw_depth_shadow_match=" << int(int(entry->depth())==stored_depth)
              << sync_endl;
}
} // C3X019 native use observer
"""

def once(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X019_NATIVE_USE_{label}_ANCHOR_COUNT_{n}")
    return s.replace(a,b,1)

def patch_tt(s):
    old='''    c3x018_event(block ? "reader_block" : "consumer_reached", site,
                 key, slot, epoch, writer_key, exact_key,
                 ply, depth, alpha, beta, value);
    return block;'''
    new='''    const bool c3x019_allow_second_native=
        block && std::strcmp(mode,"V")==0 &&
        std::strcmp(site,"tt_value_eval_override")==0 &&
        std::getenv("C3X019_PASSIVE_SECOND_ROOT_CALL") &&
        c3x018_root_context_call==
           c3x018_parameter("C3X019_PASSIVE_SECOND_ROOT_CALL");
    c3x018_event(c3x019_allow_second_native ? "reader_native_allow" :
                 block ? "reader_block" : "consumer_reached",
                 site, key, slot, epoch, writer_key, exact_key,
                 ply, depth, alpha, beta, value);
    return block && !c3x019_allow_second_native;'''
    return once(s,old,new,"PASSIVE_SECOND")

def patch_search(s):
    s=once(s,"namespace Stockfish {","namespace Stockfish {\n"+FN,"NAMESPACE")
    s=once(s,"            eval = ttValue;",
      '''        {
            eval = ttValue;
            c3x019_native_tt_eval_used(posKey,tte,ss->ply,
                int(depth),int(alpha),int(beta),int(ttValue),"main");
        }''',"MAIN_ACTUAL_ASSIGNMENT")
    s=once(s,"                bestValue = ttValue;",
      '''            {
                bestValue = ttValue;
                c3x019_native_tt_eval_used(posKey,tte,ss->ply,
                    int(ttDepth),int(alpha),int(beta),int(ttValue),"qsearch");
            }''',"QS_ACTUAL_ASSIGNMENT")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();root=Path(a.source)/"src";changed={}
    for name,fn in (("tt.cpp",patch_tt),("search.cpp",patch_search)):
        f=root/name
        b=f.read_bytes();c=fn(b.decode()).encode();f.write_bytes(c)
        changed[name]={"before_sha256":hashlib.sha256(b).hexdigest(),
                       "after_sha256":hashlib.sha256(c).hexdigest()}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x019-native-TT-score-as-evaluation-post-assignment-witness-v1",
      "changed":changed,"watch_fields":["key64","root_call","ply","alpha","beta","effective_tt_value","raw_depth","raw_value","raw_eval","shadow_epoch","shadow_serial","shadow_key64"],
      "env":["C3X019_NATIVE_USE_WATCH_KEY64","C3X019_NATIVE_USE_WATCH_ROOT_CALL","C3X019_PASSIVE_SECOND_ROOT_CALL"],
      "source_branch":"AFTER native eval=ttValue OR bestValue=ttValue actually executes",
      "passive_second":"allow native use only for selected second source V candidate; keep first actual V block",
      "censor_limit":64,"semantic_warning":"V reader_block means prevented use, native_use used means assignment actually executed",
      "single_thread_only":True},indent=2)+"\n")
    print("C3X019_ACTUAL_NATIVE_TT_VALUE_AS_EVAL_USE_POST_ASSIGNMENT_SOURCE_WATCH_READY")
if __name__=="__main__":main()
