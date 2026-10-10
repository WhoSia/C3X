#!/usr/bin/env python3
"""C3X023-P1-R2-T1 exact *read-only* Stockfish16 SEE search-state telemetry.

Apply after pinned original Stockfish16, C3X0.22 four SEE source sites,
D1 passive-ancestry, and 0.23 ancestor path source patch. Four actual
search.cpp callsite arguments become native source facts. No SEE result,
board, TT entry, alpha-beta window or move generator is modified.

Critical original-source fact: Position::see_ge(m, Bitboard& occupied, v)
takes occupied by OUTPUT, possibly returns before assigning; reading that
out bitboard from the wrapper is undefined. We log initial pos.pieces() as
the *defined input occupancy* and mark output not inspected.
"""
import argparse,hashlib,json
from pathlib import Path
SIGNATURE='''bool c3x022_r2_see(const Position& pos, Move move, Value threshold,
                   const char* site, Bitboard* occupied = nullptr) {'''
NEW_SIGNATURE='''bool c3x022_r2_see(const Position& pos, Move move, Value threshold,
                   const char* site, int source_ply, int source_depth,
                   int source_alpha, int source_beta, bool source_pv,
                   Bitboard* occupied = nullptr) {'''
READ='''    const bool original=occupied ? pos.see_ge(move,*occupied,threshold)
                                 : pos.see_ge(move,threshold);'''
READ_NEW='''    const Bitboard native_input_occupancy=pos.pieces();
    const bool original=occupied ? pos.see_ge(move,*occupied,threshold)
                                 : pos.see_ge(move,threshold);'''
MARK='''                  << " site=" << site
                  << " path_hash=" << c3x023_native_path_fingerprint()'''
MARK_NEW='''                  << " site=" << site
                  << " path_exact=" << c3x023_t1_path_vector_hex()
                  << " source_ply=" << source_ply
                  << " source_depth=" << source_depth
                  << " source_alpha=" << source_alpha
                  << " source_beta=" << source_beta
                  << " source_pv=" << int(source_pv)
                  << " source_rule50=" << pos.rule50_count()
                  << " source_occupancy64=" << uint64_t(native_input_occupancy)
                  << " input_occ_defined=1"
                  << " occupied_is_output_arg=" << int(occupied != nullptr)
                  << " branch_prune_if_no_extra_capture_guard=" << int(!delivered)
                  << " branch_direct_continuation=" << int(std::strcmp(site,"capture_prune")!=0)
                  << " path_hash=" << c3x023_native_path_fingerprint()'''
INCLUDE='#include <vector>'
INCLUDE_NEW='#include <vector>\n#include <sstream>'
PATH_FN='''std::uint64_t c3x023_native_parent_key64() {'''
PATH_INSERT='''std::string c3x023_t1_path_vector_hex() {
    // Full explicit ancestor vector: unlike 64-bit fingerprint, no collision
    // ambiguity; solely the exact chess-position key path, not alpha/beta.
    std::ostringstream out;
    bool first=true;
    for (const Key k:c3x023_see_ancestor_path) {
        if (!first) out << ",";
        out << std::hex << std::uint64_t(k);
        first=false;
    }
    return out.str();
}
std::uint64_t c3x023_native_parent_key64() {'''
CALLS={
'c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied)':
'c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",ss->ply,int(depth),int(alpha),int(beta),PvNode,&occupied)',
'c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune")':
'c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune",ss->ply,int(depth),int(alpha),int(beta),PvNode)',
'c3x022_r2_see(pos,move,VALUE_ZERO + 1,"qsearch_futility")':
'c3x022_r2_see(pos,move,VALUE_ZERO + 1,"qsearch_futility",ss->ply,int(depth),int(alpha),int(beta),PvNode)',
'c3x022_r2_see(pos,move,Value(-95),"qsearch_prune")':
'c3x022_r2_see(pos,move,Value(-95),"qsearch_prune",ss->ply,int(depth),int(alpha),int(beta),PvNode)'
}

def once(s,src,dst,label):
    n=s.count(src)
    if n!=1:raise ValueError("T1_SOURCE_"+label+"_COUNT_"+str(n))
    return s.replace(src,dst,1)
def patch(s):
    if 'c3x023_t1_path_vector_hex()' in s:raise ValueError("T1_ALREADY_PATCHED")
    for a,b,label in [(SIGNATURE,NEW_SIGNATURE,"FN_SIGNATURE"),
                       (READ,READ_NEW,"ORIGINAL_OCC_SAFE"),
                       (MARK,MARK_NEW,"SOURCE_EVENT_FULL_STATE"),
                       (INCLUDE,INCLUDE_NEW,"STRINGSTREAM"),
                       (PATH_FN,PATH_INSERT,"FULL_EXACT_CHESS_ANCESTRY")]:
        s=once(s,a,b,label)
    for i,(a,b) in enumerate(CALLS.items()):
        s=once(s,a,b,"CALLSITE_"+str(i))
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();file=Path(a.source)/"src/search.cpp"
    original=file.read_bytes();new=patch(original.decode()).encode()
    file.write_bytes(new)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x023-P1-R2-T1-exact-native-search-state-SEE-source-only-v1",
      "source_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "before_sha256":hashlib.sha256(original).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "sites":list(CALLS),
      "source_fields":["path_exact","source_ply","source_depth","source_alpha",
         "source_beta","source_pv","source_rule50","source_occupancy64",
         "input_occ_defined","occupied_is_output_arg",
         "branch_prune_if_no_extra_capture_guard","branch_direct_continuation"],
      "not_measured":"actual capture_prune post-SEE discovered check guard outcome; also branch context outside native site",
      "IMPORTANT":"occupied output arg intentionally NEVER dereferenced. Original Stockfish Position::see_ge can return early without setting it. input pos.pieces is known defined bitboard.",
      "pure_passive":True,"no_SEE_Boolean_change":True,
      "no_search_window_mutation":True,
      "full_position_key_ancestor_path_exact_hex_in_PRIVATE_runtime":True
    },indent=2)+"\n")
    print("C3X023_P1_R2_T1_EXACT_NATIVE_COMPUTATIONAL_SEE_STATE_INSTRUMENTED",
           hashlib.sha256(new).hexdigest())
if __name__=="__main__":main()
