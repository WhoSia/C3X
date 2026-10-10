#!/usr/bin/env python3
"""Native SF16 T3 strictly bounded same-source SEE Bool do-intervention.

This is a local C++ source operator perturbation. NOT natural mediation proof.
Apply AFTER C3X023 P1 ancestry, T1 full native frame observer; candidate
literal source tuple sealed in git BEFORE this actuator runs. Only original
quiet_prune / qsearch_prune permitted and exactly one alteration. Never mutate
Position::see_ge, legality, Stockfish TT, or any non-target SEE call.
"""
import argparse,hashlib,json
from pathlib import Path
EXACT='''    const bool applied=requested_flip && n==1;
    const bool delivered=applied ? !original : original;
    const C3X023_T1_Frame t1 = c3x023_t1_current();'''
NEW=r'''    const bool applied=requested_flip && n==1;
    const C3X023_T1_Frame t1 = c3x023_t1_current();
    const char* t3mode=std::getenv("C3X023_T3_MODE");
    auto t3int=[&](const char* field, long long actual) {
        std::string variable="C3X023_T3_"+std::string(field);
        const char* input=std::getenv(variable.c_str());
        return input && std::strtoll(input,nullptr,10)==actual;
    };
    auto t3u64=[&](const char* field,std::uint64_t actual) {
        std::string variable="C3X023_T3_"+std::string(field);
        const char* input=std::getenv(variable.c_str());
        return input && std::strtoull(input,nullptr,10)==actual;
    };
    const char* t3path=std::getenv("C3X023_T3_t1_path");
    const char* t3site=std::getenv("C3X023_T3_site");
    const bool t3policy=t3mode && (std::strcmp(t3mode,"SHAM")==0
                          || std::strcmp(t3mode,"FLIP")==0);
    const bool t3site_allowed=std::strcmp(site,"quiet_prune")==0
                               || std::strcmp(site,"qsearch_prune")==0;
    const bool t3eligible=t3policy && t3site_allowed && t3site
        && std::strcmp(t3site,site)==0 && t3path
        && c3x023_t1_exact_path()==t3path
        && t3u64("key64",std::uint64_t(pos.key()))
        && t3u64("parent_key64",c3x023_native_parent_key64())
        && t3int("root_call",c3x018_root_context_call)
        && t3int("root_move",c3x018_root_context_move)
        && t3int("move",int(move))
        && t3int("threshold",int(threshold))
        && t3int("t1_ply",t1.ss ? t1.ss->ply : -1)
        && t3int("t1_depth",t1.depth ? int(*t1.depth) : -999)
        && t3int("t1_alpha",t1.alpha ? int(*t1.alpha) : -99999)
        && t3int("t1_beta",t1.beta ? int(*t1.beta) : -99999)
        && t3int("t1_pv",int(t1.pv))
        && t3int("t1_qsearch",int(t1.qsearch))
        && t3int("t1_rule50",pos.rule50_count())
        && t3int("t1_occupied_present",int(occupied!=nullptr))
        && t3u64("t1_occupied_out",occupied ? std::uint64_t(*occupied) : 0ULL)
        && t3int("original_SEE_Boolean",int(original));
    static unsigned long long c3x023_t3_scope_hits=0;
    const unsigned long long t3num=t3eligible ? ++c3x023_t3_scope_hits : 0;
    const bool t3altered=t3eligible && t3num==1
             && std::strcmp(t3mode,"FLIP")==0;
    const bool delivered=(applied || t3altered) ? !original : original;
    if (t3eligible) {
        sync_cout << "info string c3x023_t3_source kind=contact"
                  << " site=" << site
                  << " key64=" << std::uint64_t(pos.key())
                  << " root_call=" << c3x018_root_context_call
                  << " original=" << int(original)
                  << " delivered=" << int(delivered)
                  << " altered=" << int(t3altered)
                  << " exact_hits=" << t3num << sync_endl;
    }'''
WITNESS='''                  << " altered=" << int(applied)
                  << " sequence=" << n'''
WITNESS_NEW='''                  << " altered=" << int(applied || t3altered)
                  << " sequence=" << n'''

def patch(s):
    if "c3x023_t3_scope_hits" in s:raise ValueError("T3_ALREADY_PATCHED")
    if s.count(EXACT)!=1:raise ValueError("T3_NEEDS_T1_AND_D1_NATIVE_SEE_RETURN")
    s=s.replace(EXACT,NEW,1)
    if s.count(WITNESS)!=1:raise ValueError("T3_NATIVE_SEE_WITNESS_SOURCE_NOT_UNIQUE")
    s=s.replace(WITNESS,WITNESS_NEW,1)
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    args=p.parse_args();f=Path(args.source)/"src/search.cpp"
    raw=f.read_bytes();patched=patch(raw.decode()).encode();f.write_bytes(patched)
    o=Path(args.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps({"schema":"c3x023-P1-R2-T3-native-first-exact-site-SEE-bool-singleton-v1",
       "before_sha256":hashlib.sha256(raw).hexdigest(),
       "after_sha256":hashlib.sha256(patched).hexdigest(),
       "allowed_sites":["quiet_prune","qsearch_prune"],
       "modes":["SHAM","FLIP"],
       "matching_includes_exact_ancestry_vector_rootcandidate_search_window_and_original_Boolean":True,
       "source_dose_exactly_one_even_if_repeated_match":True,
       "source_precommit_required":"c3x/forecasts/c3x-023-P1-R2-T2-exact-native-SEE-targets-before-first-actuator-20261011.json",
       "not_natural_TT_SEE_mediation_even_if_cat_move_flips":True},sort_keys=True,indent=2)+"\n")
    print("C3X023_T3_STRICT_NATIVE_SEE_BOOL_ACTUATOR_COMPILED_SOURCE_PATCH",hashlib.sha256(patched).hexdigest())
if __name__=="__main__":main()
