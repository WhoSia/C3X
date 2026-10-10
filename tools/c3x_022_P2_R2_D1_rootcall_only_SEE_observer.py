#!/usr/bin/env python3
"""D1 additive read-only SEE ancestry observer, applied AFTER strict SEE patch.

Broaden root-call scope only for OBS; never mutate SEE results under ancestry.
Original source exact-key factorial from R2 remains a separate experiment.
"""
import argparse,hashlib,json
from pathlib import Path

BEFORE=r'''    if (uint64_t(pos.key())!=target || c3x018_root_context_call!=call)
        return original;'''
AFTER=r'''    const char* ancestry=std::getenv("C3X022_R2_SEE_PASSIVE_ANCESTRY");
    const bool observe_descendant=ancestry && std::strcmp(ancestry,"1")==0;
    if (c3x018_root_context_call!=call
        || (!observe_descendant && uint64_t(pos.key())!=target))
        return original;'''
OLD_FLIP=r'''    const bool requested_flip=policy && std::strcmp(policy,"FLIP")==0;'''
NEW_FLIP=r'''    const bool requested_flip=!observe_descendant && policy
                              && std::strcmp(policy,"FLIP")==0;'''

def patch(s):
    if s.count(BEFORE)!=1:raise ValueError("STRICT_SEE_SOURCE_WATCH_REQUIRED")
    if s.count(OLD_FLIP)!=1:raise ValueError("STRICT_FIRST_SINGLETON_SOURCE")
    s=s.replace(BEFORE,AFTER,1).replace(OLD_FLIP,NEW_FLIP,1)
    return s

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    z=a.parse_args()
    f=Path(z.source)/"src/search.cpp"
    raw=f.read_bytes()
    updated=patch(raw.decode()).encode()
    f.write_bytes(updated)
    out=Path(z.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"c3x022-R2-D1-root-ancestry-SEE-read-only-source-witness-v1",
       "before_sha256":hashlib.sha256(raw).hexdigest(),
       "after_sha256":hashlib.sha256(updated).hexdigest(),
       "env":"C3X022_R2_SEE_PASSIVE_ANCESTRY=1",
       "mandatory_policy":"OBS",
       "no_native_SEE_result_mutation_in_passive_ancestry":True,
       "only_shows_witnessed_first32_calls_not_exhaustive_if_censored":True},indent=2)+"\n")
    print("C3X022_R2_D1_NATIVE_ROOT_ANCESTRY_OBSERVER_READY",hashlib.sha256(updated).hexdigest())
if __name__=="__main__":main()
