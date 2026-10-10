#!/usr/bin/env python3
"""T2 exact source-node native SEE Boolean policy actuator, Stockfish16.

MUST run only after pinned SEE-4sites + D1 passive ancestry + 0.23-P1
path observer + 0.23-R2-T1 exact live computational search-state overlay.
Opt-in env TARGET is exact pos.key, parent key, full ORIGINAL ancestor vector,
rootcall, rootmove, source ply/depth/alpha/beta/pv, rule50, defined initial
input occupancy, native move/site/threshold. One native Boolean complement.
The actuation never affects legal move generation nor Position::see_ge itself.
"""
import argparse,hashlib,json
from pathlib import Path
ANCHOR='''    const bool applied=requested_flip && n==1;'''
REPLACE=r'''    // C3X023 T2: exact source-event Boolean intervention, separately
    // precommitted. Suppressed if native path and live search state differ.
    const char* t2mode=std::getenv("C3X023_T2_ENABLE");
    const bool t2enable=t2mode && std::strcmp(t2mode,"1")==0;
    const auto env_u64=[](const char* name)->std::uint64_t {
        const char* x=std::getenv(name);
        return x ? std::strtoull(x,nullptr,10) : 0ULL;
    };
    const auto env_i64=[](const char* name)->long long {
        const char* x=std::getenv(name);
        return x ? std::strtoll(x,nullptr,10) : 0LL;
    };
    const char* t2site=std::getenv("C3X023_T2_site");
    const char* t2path=std::getenv("C3X023_T2_path_exact");
    const bool t2legal_site=std::strcmp(site,"quiet_prune")==0
                          || std::strcmp(site,"qsearch_prune")==0
                          || std::strcmp(site,"qsearch_futility")==0;
    const bool t2exact=t2enable && observe_descendant
          && policy && std::strcmp(policy,"OBS")==0
          && t2legal_site && t2site && t2path
          && std::strcmp(site,t2site)==0
          && c3x023_t1_path_vector_hex()==std::string(t2path)
          && uint64_t(pos.key())==env_u64("C3X023_T2_key64")
          && c3x023_native_parent_key64()==env_u64("C3X023_T2_parent_key64")
          && c3x018_root_context_call==env_u64("C3X023_T2_root_call")
          && c3x018_root_context_move==env_i64("C3X023_T2_root_move")
          && int(move)==env_i64("C3X023_T2_move")
          && int(threshold)==env_i64("C3X023_T2_threshold")
          && source_ply==env_i64("C3X023_T2_source_ply")
          && source_depth==env_i64("C3X023_T2_source_depth")
          && source_alpha==env_i64("C3X023_T2_source_alpha")
          && source_beta==env_i64("C3X023_T2_source_beta")
          && int(source_pv)==env_i64("C3X023_T2_source_pv")
          && pos.rule50_count()==env_i64("C3X023_T2_source_rule50")
          && uint64_t(native_input_occupancy)==env_u64("C3X023_T2_source_occupancy64");
    static unsigned long long c3x023_T2_delivered_count=0;
    const bool applied=t2enable
          ? (t2exact && ++c3x023_T2_delivered_count==1)
          : (requested_flip && n==1);'''
END='''    return delivered;
}
}
'''
END_NEW=r'''    if (applied && n>32) {
        sync_cout << "info string c3x022_r2_see kind=forced"
                  << " site=" << site
                  << " key64=" << uint64_t(pos.key())
                  << " parent_key64=" << c3x023_native_parent_key64()
                  << " path_hash=" << c3x023_native_path_fingerprint()
                  << " path_exact=" << c3x023_t1_path_vector_hex()
                  << " path_length=" << c3x023_see_ancestor_path.size()
                  << " root_call=" << c3x018_root_context_call
                  << " root_move=" << c3x018_root_context_move
                  << " move=" << int(move)
                  << " threshold=" << int(threshold)
                  << " source_ply=" << source_ply
                  << " source_depth=" << source_depth
                  << " source_alpha=" << source_alpha
                  << " source_beta=" << source_beta
                  << " source_pv=" << int(source_pv)
                  << " source_rule50=" << pos.rule50_count()
                  << " source_occupancy64=" << uint64_t(native_input_occupancy)
                  << " original=" << int(original)
                  << " delivered=" << int(delivered)
                  << " altered=1 sequence=" << n << sync_endl;
    }
    return delivered;
}
}
'''
def once(s,a,b,name):
    n=s.count(a)
    if n!=1:raise ValueError("T2_NATIVE_ACTUATOR_"+name+"_ANCHOR_"+str(n))
    return s.replace(a,b,1)
def patch(s):
    if "c3x023_T2_delivered_count" in s:raise ValueError("T2_ALREADY_PATCHED")
    s=once(s,ANCHOR,REPLACE,"FIRST_SINGLE_ACTUATOR")
    s=once(s,END,END_NEW,"T2_OVERFLOW_INDEPENDENT_FORCED_WITNESS")
    return s
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();f=Path(a.source)/"src/search.cpp"
    old=f.read_bytes();new=patch(old.decode()).encode()
    f.write_bytes(new)
    dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({
      "schema":"c3x023-P1-R2-T2-ONLY-full-source-exact-native-SEE-Boolean-one-use-v1",
      "before_sha256":hashlib.sha256(old).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "controlled_source_fields":["key64","parent_key64","path_exact","root_call",
          "root_move","move","site","threshold","source_ply","source_depth",
          "source_alpha","source_beta","source_pv","source_rule50","source_occupancy64"],
      "eligible_site_only":["quiet_prune","qsearch_prune","qsearch_futility"],
      "actual_native_see_ge_algorithm_unchanged":True,
      "actual_chess_move_generator_unchanged":True,
      "single_source_delivery":"at most one Boolean complementary value per UCI engine process",
      "watcher_off_default_legacy":"all new opt-in T2 ENV vars are erased by play"
    },sort_keys=True,indent=2)+"\n")
    print("C3X023_R2_T2_SOURCE_EXACT_NATIVE_SEE_SINGLE_ACTUATOR_COMPILED",
          hashlib.sha256(new).hexdigest())
if __name__=="__main__":main()
