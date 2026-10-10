#!/usr/bin/env python3
"""Read-only native Stockfish16 SEE search-state audit at four REAL search.cpp sites.

Apply only AFTER R2 SEE watcher + D1 passive observer + P1 parent-path witness.
Never intervene on SEE, TT, board legality, or search pruning.
"""
import argparse,hashlib,json
from pathlib import Path

SIG='''                   const char* site, Bitboard* occupied = nullptr) {'''
SIG_NEW='''                   const char* site, int source_ply, int source_depth,
                   int source_alpha, int source_beta, Bitboard* occupied = nullptr) {'''
LOG='''                  << " site=" << site
                  << " path_hash="'''
LOG_NEW='''                  << " site=" << site
                  << " state_ply=" << source_ply
                  << " state_depth=" << source_depth
                  << " state_alpha=" << source_alpha
                  << " state_beta=" << source_beta
                  << " state_rule50=" << pos.rule50_count()
                  << " state_occupied_given=" << int(occupied != nullptr)
                  << " state_occupied64=" << (occupied ? uint64_t(*occupied) : 0ULL)
                  << " path_hash="'''
SITES=[
('c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied)',
 'c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",ss->ply,depth,alpha,beta,&occupied)'),
('c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune")',
 'c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune",ss->ply,depth,alpha,beta)'),
('c3x022_r2_see(pos,move,VALUE_ZERO + 1,"qsearch_futility")',
 'c3x022_r2_see(pos,move,VALUE_ZERO + 1,"qsearch_futility",ss->ply,depth,alpha,beta)'),
('c3x022_r2_see(pos,move,Value(-95),"qsearch_prune")',
 'c3x022_r2_see(pos,move,Value(-95),"qsearch_prune",ss->ply,depth,alpha,beta)')]

def once(s,a,b,reason):
    if s.count(a)!=1:raise ValueError("T1_SOURCE_"+reason+"_ANCHOR_COUNT_"+str(s.count(a)))
    return s.replace(a,b,1)

def patch(s):
    if 'state_occupied64=' in s:raise ValueError("T1_ALREADY_PATCHED")
    s=once(s,SIG,SIG_NEW,"EXACT_NATIVE_SEE_WRAPPER")
    s=once(s,LOG,LOG_NEW,"PATH_SOURCE_WITNESS_LOG")
    for i,(a,b) in enumerate(SITES):
        s=once(s,a,b,"CALLSITE_"+str(i))
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args();f=Path(a.source)/"src/search.cpp"
    original=f.read_bytes();new=patch(original.decode()).encode()
    f.write_bytes(new);out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x023-P1-R2-T1-native-SEE-full-searchstate-source-observer-v1",
        "before_sha256":hashlib.sha256(original).hexdigest(),
        "after_sha256":hashlib.sha256(new).hexdigest(),
        "native_sites":["capture_prune","quiet_prune","qsearch_futility","qsearch_prune"],
        "observables":["state_ply","state_depth","state_alpha","state_beta",
                       "state_rule50","state_occupied_given","state_occupied64",
                       "path_hash","parent_key64","key64","move","site","threshold"],
        "alpha_beta_are_source_local_at_SEE_call":True,
        "does_not_instrument_PV_or_cutnode_or_explicit_branch_decision":True,
        "node_state_equivalence_is_conditional_on_ancestor_hash_not_raw_vector":True,
        "read_only_native_SEE_operator":True},sort_keys=True,indent=2)+"\n")
    print("C3X023_P1_R2_T1_NATIVE_SEE_FULL_STATE_SOURCE_OVERLAY",hashlib.sha256(new).hexdigest())
if __name__=="__main__":main()
