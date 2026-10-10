#!/usr/bin/env python3
"""C3X023-P1 source-identity trace: actual Stack search/qsearch ancestor key sequence.

Apply AFTER C3X0.22 R2 native 4-site SEE watcher (including D1 read-only),
BEFORE compiling the SAME pinned SF16. Read-only; no mutations of SEE/TT/board.
Node alignment requires exact root-call, root-move, position key, SEE site,
threshold, move, and actual ordered chess-position ancestor path digest.
"""
import argparse,hashlib,json
from pathlib import Path
EXTRA=r"""
// C3X023 path identity witness; thread-local, no chess-semantic mutation.
namespace {
thread_local std::vector<Key> c3x023_see_ancestor_path;
struct C3X023_AncestorGuard {
    explicit C3X023_AncestorGuard(Key current) {
        c3x023_see_ancestor_path.push_back(current);
    }
    ~C3X023_AncestorGuard() { c3x023_see_ancestor_path.pop_back(); }
    C3X023_AncestorGuard(const C3X023_AncestorGuard&) = delete;
    C3X023_AncestorGuard& operator=(const C3X023_AncestorGuard&) = delete;
};
std::uint64_t c3x023_native_path_fingerprint() {
    std::uint64_t h=14695981039346656037ULL;
    for (const Key k:c3x023_see_ancestor_path) {
        h ^= std::uint64_t(k);
        h *= 1099511628211ULL;
    }
    return h;
}
std::uint64_t c3x023_native_parent_key64() {
    return c3x023_see_ancestor_path.size()<2 ? 0 :
           std::uint64_t(c3x023_see_ancestor_path[
                 c3x023_see_ancestor_path.size()-2]);
}
}
"""
MAIN="""  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {

    constexpr bool PvNode"""
MAIN_NEW="""  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {
    C3X023_AncestorGuard c3x023_node_entry(pos.key());

    constexpr bool PvNode"""
QS="""  Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {

    static_assert"""
QS_NEW="""  Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {
    C3X023_AncestorGuard c3x023_node_entry(pos.key());

    static_assert"""
LOG='''                  << " site=" << site
                  << " key64=" << uint64_t(pos.key())'''
LOG_NEW='''                  << " site=" << site
                  << " path_hash=" << c3x023_native_path_fingerprint()
                  << " path_length=" << c3x023_see_ancestor_path.size()
                  << " parent_key64=" << c3x023_native_parent_key64()
                  << " key64=" << uint64_t(pos.key())'''

def one(s,a,b,name):
    if s.count(a)!=1:raise ValueError("C3X023_PATH_WITNESS_"+name+"_COUNT_"+str(s.count(a)))
    return s.replace(a,b,1)
def patch(s):
    if "c3x023_see_ancestor_path" in s:raise ValueError("P1_PATH_OBSERVER_ALREADY_PATCHED")
    s=one(s,"namespace Stockfish {","namespace Stockfish {\n"+EXTRA,"NAMESPACE")
    s=one(s,MAIN,MAIN_NEW,"MAIN_ENTRY")
    s=one(s,QS,QS_NEW,"QS_ENTRY")
    s=one(s,LOG,LOG_NEW,"ACTUAL_NATIVE_SEE_LOG")
    if "#include <vector>" not in s:
        s=one(s,"#include <algorithm>","#include <algorithm>\n#include <vector>","VECTOR")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args();file=Path(a.source)/"src/search.cpp"
    original=file.read_bytes();modified=patch(original.decode()).encode()
    file.write_bytes(modified)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x023-P1-native-SEE-search-ancestor-position-key-fingerprint-v1",
      "original_stockfish16_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "search_cpp_before_sha256":hashlib.sha256(original).hexdigest(),
      "search_cpp_after_sha256":hashlib.sha256(modified).hexdigest(),
      "trace_fields":["path_hash","path_length","parent_key64","key64",
                      "root_call","root_move","move","site","threshold","original"],
      "no_change_to_stockfish_original_SEE_return":True,
      "no_change_to_TT_or_position_contents":True,
      "one_hash_collision_caution":"This is a 64-bit path digest; a hash match is identity evidence under cryptographic/nonadversarial collision assumption, not absolute unique node identity; compare full path if needed.",
      "scope":"Single-thread Stockfish16 search and qsearch. No cross-arm rootcall numeric equality assumed without root candidate+parent signature."},sort_keys=True,indent=2)+"\n")
    print("C3X023_P1_NATIVE_SEE_PARENT_KEY_PATH_OBSERVER_READY",hashlib.sha256(modified).hexdigest())
if __name__=="__main__":main()
