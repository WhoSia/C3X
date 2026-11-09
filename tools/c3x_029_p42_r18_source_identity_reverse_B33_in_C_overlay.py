#!/usr/bin/env python3
"""P42/R18: force the original B event33 draw return at its SAME
chess-board/search-window source identity in guard-bypassed C.

Match position, ply, depth, root move and pre-draw alpha/beta; do NOT match
nodes mod4, because changing that computation is the mechanism under test.
Freeze keys from original B event before running the reverse C intervention.
Private keys never enter public artifacts or action command lines.
"""
from pathlib import Path
import argparse,hashlib,json
ANCHOR='''        const Value c3x042_r11_candidate =
            c3x042_r12_hit ? VALUE_DRAW : c3x042_r12_native;'''
CODE=r'''        // R18: physical same board/search-window counterfactual, NOT ordinal.
        // Explicit original B event33 identity frozen by trusted Python court.
        const char* r18_on = std::getenv("C3X042_R18_REVERSE_EVENT33");
        const char* r18_k = std::getenv("C3X042_R18_TARGET_KEY");
        const char* r18_p = std::getenv("C3X042_R18_TARGET_PLY");
        const char* r18_d = std::getenv("C3X042_R18_TARGET_DEPTH");
        const char* r18_r = std::getenv("C3X042_R18_TARGET_ROOT_MOVE");
        const char* r18_a = std::getenv("C3X042_R18_TARGET_ALPHA");
        const char* r18_b = std::getenv("C3X042_R18_TARGET_BETA");
        const bool r18_eligible = r18_on && *r18_on == '1' && r18_on[1] == '\0'
          && r18_k && *r18_k && r18_p && *r18_p && r18_d && *r18_d
          && r18_r && *r18_r && r18_a && *r18_a && r18_b && *r18_b
          && static_cast<unsigned long long>(pos.key()) == std::strtoull(r18_k,nullptr,10)
          && ss->ply == std::atoi(r18_p) && int(depth) == std::atoi(r18_d)
          && int(c3x018_root_context_move) == std::atoi(r18_r)
          && int(c3x042_r11_old_alpha) == std::atoi(r18_a)
          && int(beta) == std::atoi(r18_b);
        if (r18_eligible) {
            ++c3x042_r18_matching_calls;
            if (const char* log=std::getenv("C3X042_R18_PRIVATE_HIT_LOG")) {
                if (*log) {
                    if (auto* out=std::fopen(log,"a")) {
                        std::fprintf(out,
                          "c3x042_r18 candidate_contact=1 ordinal_match=%llu applied=%d native=%d forced=-1\n",
                          c3x042_r18_matching_calls,
                          int(c3x042_r18_matching_calls == 1),
                          int(c3x042_r12_native));
                        std::fclose(out);
                    }
                }
            }
        }
        const bool r18_apply = r18_eligible && c3x042_r18_matching_calls == 1;
        const Value c3x042_r11_candidate = r18_apply ? Value(-1)
            : (c3x042_r12_hit ? VALUE_DRAW : c3x042_r12_native);'''
STATE='  // search<>() is the main search function for both PV and non-PV nodes'
def patch(src):
    if "c3x042_r18_matching_calls" in src:
        raise ValueError("R18_HOLD_ALREADY_PATCHED")
    if src.count(ANCHOR)!=1 or src.count(STATE)!=1:
        raise ValueError("R18_HOLD_R12_SOURCE_ANCHOR_DRIFT")
    src=src.replace(STATE,"  thread_local unsigned long long c3x042_r18_matching_calls=0;\n"+STATE,1)
    return src.replace(ANCHOR,CODE,1)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    before=f.read_bytes();after=patch(before.decode()).encode()
    f.write_bytes(after)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
        "schema":"c3x042-r18-native-source-identity-reverse-cycle-return-v1",
        "pre_patch_sha256":hashlib.sha256(before).hexdigest(),
        "post_patch_sha256":hashlib.sha256(after).hexdigest(),
        "target_selection":"frozen original B event33 key,ply,depth,root,oldalpha,beta",
        "force_return":-1,
        "ignores_node_mod4_intentionally":True,
        "single_application_per_physical_process":True,
        "natural_causal_mediator_claim":False
    },sort_keys=True,indent=2)+"\n")
    print("C3X042_R18_ORIGINAL_SOURCE_REVERSE_PATCH_ONLY_NO_CHESS_VERDICT")
if __name__=="__main__":
    main()
