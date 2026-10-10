#!/usr/bin/env python3
"""D2 development-only operator flip on first root-ancestry quiet/qsearch pruning SEE.
After strict SEE witness and D1 passive ancestor add-on. Does not mutate
Position::see_ge or board legality. Disabled unless explicit opt-in env.
"""
import argparse,hashlib,json
from pathlib import Path

OLD=r'''    const bool requested_flip=!observe_descendant && policy
                              && std::strcmp(policy,"FLIP")==0;
    const unsigned long long n=++c3x022_r2_see_matches;
    const bool applied=requested_flip && n==1;'''
NEW=r'''    const char* d2=std::getenv("C3X022_R2_SEE_DESCENDANT_FIRST_PRUNE");
    const bool D2_ancestry_pruning_toggle=d2 && std::strcmp(d2,"1")==0;
    const bool D2_prune_site=std::strcmp(site,"quiet_prune")==0
                             || std::strcmp(site,"qsearch_prune")==0;
    const bool requested_flip=policy && std::strcmp(policy,"FLIP")==0
                 && (!observe_descendant || D2_ancestry_pruning_toggle);
    const unsigned long long n=++c3x022_r2_see_matches;
    static unsigned long long c3x022_r2_D2_eligible_prune_seen=0;
    const bool applied=D2_ancestry_pruning_toggle && observe_descendant
        ? (requested_flip && D2_prune_site
            && ++c3x022_r2_D2_eligible_prune_seen==1)
        : (requested_flip && n==1);'''
NEEDLE=r'''    else if (n==33) {
        sync_cout << "info string c3x022_r2_see kind=censored"'''
EXTRA=r'''    if (applied && n>32)
        sync_cout << "info string c3x022_r2_see kind=forced"
                  << " site=" << site
                  << " key64=" << uint64_t(pos.key())
                  << " root_call=" << c3x018_root_context_call
                  << " move=" << int(move)
                  << " threshold=" << int(threshold)
                  << " original=" << int(original)
                  << " delivered=" << int(delivered)
                  << " altered=1 sequence=" << n << sync_endl;
    else if (n==33) {
        sync_cout << "info string c3x022_r2_see kind=censored"'''

def patch(s):
    if s.count(OLD)!=1:raise ValueError("D2_REQUIRES_STRICT_PLUS_D1_SOURCE")
    if s.count(NEEDLE)!=1:raise ValueError("D2_SOURCE_LOGGING_SITE")
    return s.replace(OLD,NEW,1).replace(NEEDLE,EXTRA,1)

def main():
    a=argparse.ArgumentParser();a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    f=Path(args.source)/"src/search.cpp";raw=f.read_bytes()
    new=patch(raw.decode()).encode();f.write_bytes(new)
    o=Path(args.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps({"schema":"c3x022-R2-D2-first-root-descendant-quiet-or-qsearch-native-SEE-Bool-toggle-v1",
      "before_sha256":hashlib.sha256(raw).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "control_env":"C3X022_R2_SEE_DESCENDANT_FIRST_PRUNE=1",
      "sites":["quiet_prune","qsearch_prune"],
      "scope":"same rootcall descendant first eligible Boolean only; exact original node key logged but not fixed across contrasting arms",
      "position_rule":"chess board, legal move generator, C++ native see_ge internal algorithm unchanged",
      "not_heldout":True},indent=2)+"\n")
    print("C3X022_R2_D2_FIRST_PRUNE_SEE_SOURCE_ARM_READY",hashlib.sha256(new).hexdigest())
if __name__=="__main__":main()
