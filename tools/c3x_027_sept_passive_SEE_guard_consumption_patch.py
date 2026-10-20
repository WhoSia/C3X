#!/usr/bin/env python3
"""C3X 0.27 September read-only guards for original SEE consumer callsites.
Borrow strict source anchors of historical 0.23 T4 but do not require a T3
Boolean-flip target. No SEE return, TT, pruning, move, or engine value mutation.
"""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
f=Path(a.source)/"src/search.cpp";s=f.read_text()
anchor="unsigned long long c3x022_r2_see_matches=0;"
assert s.count(anchor)==1,"NO_ORIGINAL_SEE_WRAPPER"
fn=r'''
thread_local unsigned long long c3x027_guard_line_count = 0;
void c3x027_native_SEE_guard_result(const Position& pos,Move move,Value threshold,
                                    const char* site,const char* decision) {
    const char* filename=std::getenv("C3X027_GUARD_LOG");
    const char* call=std::getenv("C3X027_GUARD_ROOT_CALL");
    if (!filename || !call || !*filename || !*call) return;
    if (std::strtoll(call,nullptr,10)!=c3x018_root_context_call) return;
    if (++c3x027_guard_line_count>8192) return;
    if (auto* stream=std::fopen(filename,"a")) {
        std::fprintf(stream,
           "site=%s key64=%llu root_call=%d move=%d threshold=%d decision=%s\n",
           site,(unsigned long long)std::uint64_t(pos.key()),
           int(c3x018_root_context_call),int(move),int(threshold),decision);
        std::fclose(stream);
    }
}
'''
s=s.replace(anchor,anchor+"\n"+fn,1)
sites={
 "quiet_prune":(
 'if (!c3x022_r2_see(pos,move,Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth),"quiet_prune"))',
 '                  continue;',
 'Value(-27 * lmrDepth * lmrDepth - 16 * lmrDepth)'),
 "qsearch_prune":(
 'if (!c3x022_r2_see(pos,move,Value(-95),"qsearch_prune"))',
 '                continue;',
 'Value(-95)')
}
for site,(condition,cont,threshold) in sites.items():
 needle=condition+"\n"+cont
 assert s.count(needle)==1,("SOURCE_GUARD_MISMATCH",site,s.count(needle))
 spaces=cont[:len(cont)-len(cont.lstrip())]
 # Both branches preserve original if-return and continue logic.
 change=(condition+" {\n"+spaces+
         '    c3x027_native_SEE_guard_result(pos,move,'+threshold+',"'+site+'","ACTUAL_CONTINUE");\n'+
         cont+"\n"+spaces[:-2]+"}\n"+spaces[:-2]+
         'c3x027_native_SEE_guard_result(pos,move,'+threshold+',"'+site+'","PASSED_GUARD");')
 s=s.replace(needle,change,1)
s='#include <cstdio>\n'+s
f.write_text(s)
Path(a.out_manifest).write_text(json.dumps({
  "schema":"c3x027-sept-passive-native-SEE-guard-consumption-v1",
  "historical_T4_caller_source_sites":["quiet_prune","qsearch_prune"],
  "source_exact_anchor_compatible":True,"read_only":True,
  "changes_to_SEE_Boolean_TT_and_chess_legality":0,
  "engine_guard_log_private":True,
  "guard_output_limit_per_process":8192
 },indent=2)+"\n")
print("C3X027_SEPT_ACTUAL_SEE_CONSUMER_PATCH_PASS",len(sites))
