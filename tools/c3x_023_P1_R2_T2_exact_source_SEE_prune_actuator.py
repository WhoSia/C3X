#!/usr/bin/env python3
"""T2 exact live native source-identity SEE-Boolean actuator; explicit opt-in.

Only after 0.23 T1 full search-window observer on pinned Stockfish16.
No board, legal moves or SEE input is mutated. First exact identity only.
One call to Position::see_ge always occurs BEFORE this source actuator.
"""
import argparse,hashlib,json
from pathlib import Path
OLD='''    const bool applied=requested_flip && n==1;'''
NEW=r'''    const char* t2_arm=std::getenv("C3X023_T2_ARM");
    const bool t2_enable=t2_arm && std::strcmp(t2_arm,"FLIP")==0;
    const char* t2_key=std::getenv("C3X023_T2_KEY64");
    const char* t2_root=std::getenv("C3X023_T2_ROOT_CALL");
    const char* t2_rootmove=std::getenv("C3X023_T2_ROOT_MOVE");
    const char* t2_parent=std::getenv("C3X023_T2_PARENT_KEY64");
    const char* t2_path=std::getenv("C3X023_T2_PATH_HASH");
    const char* t2_pathlen=std::getenv("C3X023_T2_PATH_LENGTH");
    const char* t2_move=std::getenv("C3X023_T2_MOVE");
    const char* t2_site=std::getenv("C3X023_T2_SITE");
    const char* t2_threshold=std::getenv("C3X023_T2_THRESHOLD");
    const char* t2_ply=std::getenv("C3X023_T2_STATE_PLY");
    const char* t2_depth=std::getenv("C3X023_T2_STATE_DEPTH");
    const char* t2_alpha=std::getenv("C3X023_T2_STATE_ALPHA");
    const char* t2_beta=std::getenv("C3X023_T2_STATE_BETA");
    const char* t2_rule50=std::getenv("C3X023_T2_STATE_RULE50");
    const char* t2_occupied_given=std::getenv("C3X023_T2_STATE_OCCUPIED_GIVEN");
    const char* t2_occupied64=std::getenv("C3X023_T2_STATE_OCCUPIED64");
    auto t2_u=[](const char* p)->uint64_t {
        return p ? std::strtoull(p,nullptr,10) : 0ULL;
    };
    auto t2_i=[](const char* p)->int64_t {
        return p ? std::strtoll(p,nullptr,10) : 0;
    };
    const bool t2_complete=t2_key&&t2_root&&t2_rootmove&&t2_parent
         &&t2_path&&t2_pathlen&&t2_move&&t2_site&&t2_threshold
         &&t2_ply&&t2_depth&&t2_alpha&&t2_beta&&t2_rule50
         &&t2_occupied_given&&t2_occupied64;
    const bool t2_eligible=t2_enable&&t2_complete
         && (std::strcmp(site,"quiet_prune")==0 ||
             std::strcmp(site,"qsearch_prune")==0)
         && std::strcmp(site,t2_site)==0
         && uint64_t(pos.key())==t2_u(t2_key)
         && uint64_t(c3x018_root_context_call)==t2_u(t2_root)
         && int64_t(c3x018_root_context_move)==t2_i(t2_rootmove)
         && c3x023_native_parent_key64()==t2_u(t2_parent)
         && c3x023_native_path_fingerprint()==t2_u(t2_path)
         && c3x023_see_ancestor_path.size()==t2_u(t2_pathlen)
         && int64_t(move)==t2_i(t2_move)
         && int64_t(threshold)==t2_i(t2_threshold)
         && int64_t(source_ply)==t2_i(t2_ply)
         && int64_t(source_depth)==t2_i(t2_depth)
         && int64_t(source_alpha)==t2_i(t2_alpha)
         && int64_t(source_beta)==t2_i(t2_beta)
         && int64_t(pos.rule50_count())==t2_i(t2_rule50)
         && int64_t(occupied!=nullptr)==t2_i(t2_occupied_given)
         && uint64_t(occupied ? *occupied : 0ULL)==t2_u(t2_occupied64);
    static uint64_t c3x023_t2_actuator_dose=0ULL;
    const bool t2_applied=t2_eligible && ++c3x023_t2_actuator_dose==1ULL;
    const bool applied=t2_applied || (requested_flip && n==1);'''
# Need T1 overlay provides path funcs, exact T2 is opt-in.
CENSORED='''    else if (n==33) {
        sync_cout << "info string c3x022_r2_see kind=censored"'''
CENSORED_NEW='''    if (t2_applied && n>32) {
        sync_cout << "info string c3x022_r2_see kind=forced"
                  << " site=" << site
                  << " key64=" << uint64_t(pos.key())
                  << " root_call=" << c3x018_root_context_call
                  << " root_move=" << c3x018_root_context_move
                  << " move=" << int(move)
                  << " threshold=" << int(threshold)
                  << " original=" << int(original)
                  << " delivered=" << int(delivered)
                  << " altered=1 sequence=" << n
                  << " path_hash=" << c3x023_native_path_fingerprint()
                  << " path_length=" << c3x023_see_ancestor_path.size()
                  << " parent_key64=" << c3x023_native_parent_key64()
                  << " state_ply=" << source_ply
                  << " state_depth=" << source_depth
                  << " state_alpha=" << source_alpha
                  << " state_beta=" << source_beta
                  << " state_rule50=" << pos.rule50_count()
                  << " state_occupied_given=" << int(occupied!=nullptr)
                  << " state_occupied64=" << (occupied ? uint64_t(*occupied) : 0ULL)
                  << sync_endl;
    }
    else if (n==33) {
        sync_cout << "info string c3x022_r2_see kind=censored"'''
def once(s,a,b,label):
    if s.count(a)!=1:raise ValueError("T2_SOURCE_"+label+"_ANCHOR_COUNT_"+str(s.count(a)))
    return s.replace(a,b,1)
def patch(s):
    if "c3x023_t2_actuator_dose" in s:raise ValueError("T2_ALREADY_PATCHED")
    return once(once(s,OLD,NEW,"ACTUAL_NATIVE_SEE_BOOLEAN"),CENSORED,CENSORED_NEW,"CENSORED_RETURN_LOG")
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp";before=f.read_bytes();after=patch(before.decode()).encode();f.write_bytes(after)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x023-T2-exact-full64-source-path-window-SEE-pruning-return-actuator-v1",
     "original_sha256":hashlib.sha256(before).hexdigest(),
     "modified_sha256":hashlib.sha256(after).hexdigest(),
     "source_site_scope":["quiet_prune","qsearch_prune"],
     "full_original_identity_and_all_native_SEE_inputs_required":True,
     "first_exact_source_occurrence_only":True,
     "sham_with_nonmatching_key":True,
     "stockfish_SEE_native_function_itself_unchanged":True,
     "original_legal_chess_generator_unchanged":True,
     "no_natural_mediation_claim":True},sort_keys=True,indent=2)+"\n")
    print("C3X023_T2_EXACT_QUIET_SEE_RETURN_ACTUATOR_SOURCE_READY",hashlib.sha256(after).hexdigest())
if __name__=="__main__":main()
