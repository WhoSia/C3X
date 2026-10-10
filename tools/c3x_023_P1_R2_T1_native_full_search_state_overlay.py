#!/usr/bin/env python3
"""Pinned SF16 C3X023-T1 real search state at four native see_ge callsites.

AFTER older C3X022 native SEE four-site watcher, D1 and C3X023 ancestor-path
overlay. Completely passive, no modifications to SEE Boolean or TT. The
capture-pruning 'occupied' Bitboard is an OUTPUT from native see_ge, not an
input; record it after original SEE computation with 't1_occupied_out'.
"""
import argparse,hashlib,json
from pathlib import Path

CPP=r"""
// C3X023-T1 exact native SEE caller state; passive only.
namespace {
struct C3X023_T1_Frame {
    const Value* alpha;
    const Value* beta;
    const Depth* depth;
    const Search::Stack* ss;
    bool pv;
    bool qsearch;
};
thread_local std::vector<C3X023_T1_Frame> c3x023_t1_stack;
struct C3X023_T1_Scope {
    C3X023_T1_Scope(const Value* a,const Value* b,const Depth* d,
                   const Search::Stack* s,bool p,bool q) {
        c3x023_t1_stack.push_back({a,b,d,s,p,q});
    }
    ~C3X023_T1_Scope() { c3x023_t1_stack.pop_back(); }
    C3X023_T1_Scope(const C3X023_T1_Scope&)=delete;
    C3X023_T1_Scope& operator=(const C3X023_T1_Scope&)=delete;
};
C3X023_T1_Frame c3x023_t1_current() {
    if (c3x023_t1_stack.empty()) return {nullptr,nullptr,nullptr,nullptr,false,false};
    return c3x023_t1_stack.back();
}
std::string c3x023_t1_exact_path() {
    std::string out;
    for (const Key key : c3x023_see_ancestor_path) {
        if (!out.empty()) out += ",";
        out += std::to_string(std::uint64_t(key));
    }
    return out.empty() ? "NONE" : out;
}
}
"""
MAIN='''  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {
    C3X023_AncestorGuard c3x023_node_entry(pos.key());'''
MAIN_NEW=MAIN+'''
    C3X023_T1_Scope c3x023_t1_frame(&alpha,&beta,&depth,ss,
                                     nodeType != NonPV,false);'''
QS='''  Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {
    C3X023_AncestorGuard c3x023_node_entry(pos.key());'''
QS_NEW=QS+'''
    C3X023_T1_Scope c3x023_t1_frame(&alpha,&beta,&depth,ss,
                                     nodeType != NonPV,true);'''
BEFORE='''    const bool delivered=applied ? !original : original;
    if (n<=32) {'''
AFTER='''    const bool delivered=applied ? !original : original;
    const C3X023_T1_Frame t1 = c3x023_t1_current();
    if (n<=32) {'''
LOG='''                  << " site=" << site
                  << " path_hash=" << c3x023_native_path_fingerprint()'''
LOG_NEW='''                  << " site=" << site
                  << " t1_path=" << c3x023_t1_exact_path()
                  << " t1_ply=" << (t1.ss ? t1.ss->ply : -1)
                  << " t1_depth=" << (t1.depth ? int(*t1.depth) : -999)
                  << " t1_alpha=" << (t1.alpha ? int(*t1.alpha) : -99999)
                  << " t1_beta=" << (t1.beta ? int(*t1.beta) : -99999)
                  << " t1_pv=" << int(t1.pv)
                  << " t1_qsearch=" << int(t1.qsearch)
                  << " t1_rule50=" << pos.rule50_count()
                  << " t1_occupied_present=" << int(occupied != nullptr)
                  << " t1_occupied_out=" << (occupied ? std::uint64_t(*occupied) : 0ULL)
                  << " path_hash=" << c3x023_native_path_fingerprint()'''

def patch(src):
    if "c3x023_t1_stack" in src: raise ValueError("T1_SEARCH_STATE_ALREADY_PATCHED")
    rules=[("// C3X022-R2 NATIVE SEE decision witness / first-site Boolean intervention.", CPP+"\n// C3X022-R2 NATIVE SEE decision witness / first-site Boolean intervention.","CPP_AFTER_ANCESTRY_BEFORE_SEE_WRAPPER"),
      (MAIN,MAIN_NEW,"MAIN_CALL_FRAME"),
      (QS,QS_NEW,"QSEARCH_CALL_FRAME"),
      (BEFORE,AFTER,"NATIVE_SEE_RETURN"),
      (LOG,LOG_NEW,"NATIVE_SEE_LOG")]
    for a,b,tag in rules:
        if src.count(a)!=1: raise ValueError("T1_SOURCE_ANCHOR_"+tag+"_"+str(src.count(a)))
        src=src.replace(a,b,1)
    if "#include <string>" not in src:
        if src.count("#include <vector>")!=1:
            raise ValueError("T1_PREEXISTING_VECTOR_INCLUDE_REQUIRED")
        src=src.replace("#include <vector>","#include <vector>\n#include <string>",1)
    return src

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp";before=f.read_bytes()
    after=patch(before.decode()).encode();f.write_bytes(after)
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps({"schema":"c3x023-P1-R2-T1-native-full-search-state-passive-source-v1",
       "stockfish16_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "before_sha256":hashlib.sha256(before).hexdigest(),
       "after_sha256":hashlib.sha256(after).hexdigest(),
       "observed_fields":["t1_path","t1_ply","t1_depth","t1_alpha","t1_beta",
           "t1_pv","t1_qsearch","t1_rule50","t1_occupied_present",
           "t1_occupied_out"],
       "occupied_is_OUTPUT_of_SEE_overload_not_an_input":True,
       "does_not_mutate_SEE_return_or_search_board_or_TT":True,
       "scope":"first32 calls per watched source rootcall; censored histories HOLD"},indent=2)+"\n")
    print("C3X023_T1_PASSIVE_NATIVE_SEARCH_STATE_SOURCE_PATCHED",hashlib.sha256(after).hexdigest())
if __name__=="__main__":main()
