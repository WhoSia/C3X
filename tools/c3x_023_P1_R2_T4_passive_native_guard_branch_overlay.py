#!/usr/bin/env python3
"""T4 passive exact-source branch witness, applied ONLY after sealed T3 overlay.

Records actually executed if(!see_ge) continue versus actual fallthrough.
No changes to SEE, legal moves, TT, root order; targets inherited from T2.
"""
import argparse,hashlib,json
from pathlib import Path

STATE_OLD='unsigned long long c3x022_r2_see_matches=0;'
STATE_NEW=STATE_OLD+"""
// C3X023 T4 passive source-guard observer state, set in same SEE wrapper call.
thread_local bool c3x023_t4_last_scope=false;
thread_local unsigned long long c3x023_t4_last_sequence=0;
bool c3x023_t4_enabled() {
    const char* v=std::getenv("C3X023_T4_BRANCH_OBS");
    return v && std::strcmp(v,"1")==0;
}
void c3x023_t4_branch(const Position& pos,const char* site,const char* decision) {
    sync_cout << "info string c3x023_t4_guard"
              << " site=" << site << " decision=" << decision
              << " key64=" << std::uint64_t(pos.key())
              << " root_call=" << c3x018_root_context_call
              << " exact_sequence=" << c3x023_t4_last_sequence
              << sync_endl;
    c3x023_t4_last_scope=false;
}
"""
SEQ_OLD='const unsigned long long t3num=t3eligible ? ++c3x023_t3_scope_hits : 0;'
SEQ_NEW=SEQ_OLD+"""
    c3x023_t4_last_scope=t3eligible;
    c3x023_t4_last_sequence=t3num;"""

SITES={
"quiet_prune":(
'if (!c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune"))',
'                  continue;'),
"qsearch_prune":(
'if (!c3x022_r2_see(pos,move,Value(-95),"qsearch_prune"))',
'                continue;')
}

def patch(source):
    if "c3x023_t4_last_scope" in source:
        raise ValueError("T4_ALREADY_PATCHED")
    for old,new,name in ((STATE_OLD,STATE_NEW,"GLOBAL"),
                         (SEQ_OLD,SEQ_NEW,"SOURCE_CONTACT")):
        if source.count(old)!=1:
            raise ValueError("T4_SOURCE_ANCHOR_"+name+"_"+str(source.count(old)))
        source=source.replace(old,new,1)
    for site,(call,cont) in SITES.items():
        anchor=call+"\n"+cont
        if source.count(anchor)!=1:
            raise ValueError("T4_SITE_ANCHOR_"+site+"_"+str(source.count(anchor)))
        indent=cont[:len(cont)-len(cont.lstrip())]
        new=(call+" {\n"+indent+
             '    if (c3x023_t4_last_scope && c3x023_t4_enabled())\n'+indent+
             '        c3x023_t4_branch(pos,"'+site+'","ACTUAL_CONTINUE");\n'+
             cont+"\n"+indent[:-2]+"}\n"+indent[:-2]+
             'if (c3x023_t4_last_scope && c3x023_t4_enabled())\n'+indent[:-2]+
             '    c3x023_t4_branch(pos,"'+site+'","PASSED_SEE_GUARD");')
        source=source.replace(anchor,new,1)
    return source

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    raw=f.read_bytes()
    new=patch(raw.decode()).encode()
    f.write_bytes(new)
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x023-P1-R2-T4-passive-native-actual-prune-continue-v1",
      "before_sha256":hashlib.sha256(raw).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "sites":["quiet_prune","qsearch_prune"],
      "opt_in_env":"C3X023_T4_BRANCH_OBS=1",
      "actual_taken_branch":"ACTUAL_CONTINUE",
      "fallthrough_only":"PASSED_SEE_GUARD",
      "no_SEE_TT_or_legality_mutations":True,
      "no_search_beyond_guard_certified":True,
      "T2_source_target_identity_unchanged":True,
      "preregistered_protocol":"c3x/ontology/c3x-023-P1-R2-T4-native-pruning-branch-survival-source-observer-precommit.md"
    },indent=2,sort_keys=True)+"\n")
    print("C3X023_T4_ACTUAL_SOURCE_GUARD_BRANCH_OBSERVER_READY",hashlib.sha256(new).hexdigest())

if __name__=="__main__":
    main()
