#!/usr/bin/env python3
"""C3X022 P2-R2 four exact Stockfish16 search.cpp native SEE callsites.

Apply AFTER pinned base Stockfish16 + all C3X016..020 standard overlays.
PASSIVE OBS returns original Position::see_ge bool; FLIP toggles only the
FIRST exact (pos.key(), root_call) matched SEE return, leaves later events
original. Logs original vs delivered bool, threshold, native move, source site.
Never modifies legal move generation nor SEE internals. Development ONLY.
"""
import argparse,hashlib,json
from pathlib import Path

FN=r"""
// C3X022-R2 NATIVE SEE decision witness / first-site Boolean intervention.
namespace {
unsigned long long c3x022_r2_see_matches=0;
bool c3x022_r2_see(const Position& pos, Move move, Value threshold,
                   const char* site, Bitboard* occupied = nullptr) {
    const bool original=occupied ? pos.see_ge(move,*occupied,threshold)
                                 : pos.see_ge(move,threshold);
    const char* key_env=std::getenv("C3X022_R2_SEE_KEY64");
    const char* call_env=std::getenv("C3X022_R2_SEE_ROOT_CALL");
    if (!key_env || !call_env) return original;
    const unsigned long long target=std::strtoull(key_env,nullptr,10);
    const unsigned long long call=std::strtoull(call_env,nullptr,10);
    if (uint64_t(pos.key())!=target || c3x018_root_context_call!=call)
        return original;
    const char* policy=std::getenv("C3X022_R2_SEE_POLICY");
    const bool requested_flip=policy && std::strcmp(policy,"FLIP")==0;
    const unsigned long long n=++c3x022_r2_see_matches;
    const bool applied=requested_flip && n==1;
    const bool delivered=applied ? !original : original;
    if (n<=32) {
        sync_cout << "info string c3x022_r2_see kind=witness"
                  << " site=" << site
                  << " key64=" << uint64_t(pos.key())
                  << " root_call=" << c3x018_root_context_call
                  << " root_move=" << c3x018_root_context_move
                  << " move=" << int(move)
                  << " threshold=" << int(threshold)
                  << " original=" << int(original)
                  << " delivered=" << int(delivered)
                  << " altered=" << int(applied)
                  << " sequence=" << n
                  << sync_endl;
    }
    else if (n==33) {
        sync_cout << "info string c3x022_r2_see kind=censored"
                  << " key64=" << target
                  << " root_call=" << call << sync_endl;
    }
    return delivered;
}
}
"""
ANCHORS=[
("if (!pos.see_ge(move, occupied, Value(-205) * depth))",
 'if (!c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied))'),
("if (!pos.see_ge(move, Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth)))",
 'if (!c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune"))'),
("if (futilityBase <= alpha && !pos.see_ge(move, VALUE_ZERO + 1))",
 'if (futilityBase <= alpha && !c3x022_r2_see(pos,move,VALUE_ZERO + 1,"qsearch_futility"))'),
("if (!pos.see_ge(move, Value(-95)))",
 'if (!c3x022_r2_see(pos,move,Value(-95),"qsearch_prune"))'),
]

def patch(s):
    if "c3x022_r2_see_matches" in s:
        raise ValueError("R2_SEE_ALREADY_PATCHED")
    if s.count("namespace Stockfish {")!=1:
        raise ValueError("NAMESPACE_UNIQUE_ANCHOR")
    s=s.replace("namespace Stockfish {","namespace Stockfish {\n"+FN,1)
    for a,b in ANCHORS:
        if s.count(a)!=1:raise ValueError("R2_SEE_SITE_MISSING_"+a)
        s=s.replace(a,b,1)
    return s

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    p=Path(args.source)/"src/search.cpp"
    raw=p.read_bytes()
    modified=patch(raw.decode("utf-8")).encode()
    p.write_bytes(modified)
    out=Path(args.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x022-P2-R2-Stockfish16-four-search-site-native-SEE-operator-v1",
      "source_file":"src/search.cpp",
      "original_stockfish_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "before_sha256":hashlib.sha256(raw).hexdigest(),
      "after_sha256":hashlib.sha256(modified).hexdigest(),
      "sites":["capture_prune","quiet_prune","qsearch_futility","qsearch_prune"],
      "mode":"OBS or FLIP only, exact key64/rootcall, first matching native Position::see_ge return",
      "bound":"Witness is the exact native SEE Boolean at search.cpp callsite, NOT a faithful reconstruction of the SEE exchange tree and NOT a legal board intervention",
      "log_cap":32,
      "singleton_matching_source_requirement":True},indent=2)+"\n")
    print("C3X022_P2_R2_NATIVE_STOCKFISH16_SEE_SITE_WITNESS_READY",hashlib.sha256(modified).hexdigest())
if __name__=="__main__":main()
