#!/usr/bin/env python3
"""Exploratory one-event intervention: bypass exactly first native false-SEE capture continue."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
f=Path(a.source)/"src/search.cpp";s=f.read_text()
anchor='thread_local unsigned long long c3x027_capture_trace_count = 0;'
# previous logger is no spaces around '='.
anchor='thread_local unsigned long long c3x027_capture_trace_count=0;'
assert s.count(anchor)==1,"ORIGINAL_CAPTURE_AUDIT_PATCH_REQUIRED"
helper=r"""
thread_local unsigned long long c3x027_counterfactual_match_count=0;
bool c3x027_exact_capture_reenable(const Position& pos,Move move,Value threshold) {
 const char* key=std::getenv("C3X027_FORCE_CAPTURE_KEY64");
 const char* call=std::getenv("C3X027_FORCE_CAPTURE_ROOT_CALL");
 const char* nativeMove=std::getenv("C3X027_FORCE_CAPTURE_MOVE");
 const char* val=std::getenv("C3X027_FORCE_CAPTURE_THRESHOLD");
 if (!key || !call || !nativeMove || !val) return false;
 if (std::strtoull(key,nullptr,10)!=std::uint64_t(pos.key())
     || std::strtoll(call,nullptr,10)!=c3x018_root_context_call
     || std::strtol(nativeMove,nullptr,10)!=int(move)
     || std::strtol(val,nullptr,10)!=int(threshold)) return false;
 return ++c3x027_counterfactual_match_count==1;
}
"""
s=s.replace(anchor,anchor+"\n"+helper,1)
old='''if (!attacks) {
                    c3x027_capture_branch_log(pos,move,Value(-205)*depth,"NO_DISCOVERED_ATTACK_CONTINUE");
                    continue;
                 }
                 c3x027_capture_branch_log(pos,move,Value(-205)*depth,"DISCOVERED_ATTACK_RETAIN");'''
new='''if (!attacks) {
                    if (c3x027_exact_capture_reenable(pos,move,Value(-205)*depth)) {
                        c3x027_capture_branch_log(pos,move,Value(-205)*depth,"EXACT_ONE_EVENT_REENABLED");
                    } else {
                        c3x027_capture_branch_log(pos,move,Value(-205)*depth,"NO_DISCOVERED_ATTACK_CONTINUE");
                        continue;
                    }
                 } else {
                    c3x027_capture_branch_log(pos,move,Value(-205)*depth,"DISCOVERED_ATTACK_RETAIN");
                 }'''
assert s.count(old)==1,"MUTATION_ANCHOR_MISSING"
s=s.replace(old,new,1)
f.write_text(s)
Path(a.out_manifest).write_text(json.dumps({"schema":"c3x027-case14-exact-one-event-capture-guard-reenable-v1","source_site":"capture_prune / !attacks guard","match_requirements":["key64","root_call","move","threshold"],"max_reenable_per_process":1,"default_when_env_absent":"ORIGINAL_SOURCE_BEHAVIOR","intervention":"guard-only-after-original_false-SEE","TT_reader_setting_unchanged":True},indent=2)+"\n")
print("C3X027_COUNTERFACTUAL_CAPTURE_PATCH_PASS")
