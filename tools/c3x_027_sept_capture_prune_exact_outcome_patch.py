#!/usr/bin/env python3
"""Observe exact original SF16 capture SEE caller branches without changing decisions."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
f=Path(a.source)/"src/search.cpp";s=f.read_text()
head='if (!c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied))'
start=s.find(head)
assert start>=0 and s.count(head)==1,"EXACT_CAPTURE_SEE_SOURCE_MISSING"
tail=s.find('          else\n          {\n              int history',start)
assert tail>start and tail-start<2100,"CAPTURE_GUARD_SPAN_UNRECOGNIZED"
part=s[start:tail]
def replace_once(old,new):
 global part
 assert part.count(old)==1,(old,part.count(old))
 part=part.replace(old,new,1)
replace_once('if (depth < 2 - capture)\n                    continue;',
'''if (depth < 2 - capture) {
                    c3x027_capture_branch_log(pos,move,Value(-205)*depth,"DEPTH_CONTINUE");
                    continue;
                 }''')
replace_once('if (!attacks)\n                    continue;',
'''if (!attacks) {
                    c3x027_capture_branch_log(pos,move,Value(-205)*depth,"NO_DISCOVERED_ATTACK_CONTINUE");
                    continue;
                 }
                 c3x027_capture_branch_log(pos,move,Value(-205)*depth,"DISCOVERED_ATTACK_RETAIN");''')
# Only FALSE SEE path is observed. TRUE is not a capture-pruning candidate.
s=s[:start]+part+s[tail:]
anchor='unsigned long long c3x022_r2_see_matches=0;'
assert s.count(anchor)==1
logger=r'''
thread_local unsigned long long c3x027_capture_trace_count=0;
void c3x027_capture_branch_log(const Position& pos,Move move,Value threshold,const char* decision) {
 const char* dest=std::getenv("C3X027_CAPTURE_BRANCH_LOG");
 if (!dest || !*dest || ++c3x027_capture_trace_count>32768) return;
 if (auto* out=std::fopen(dest,"a")) {
  std::fprintf(out,"key64=%llu root_call=%d move=%d threshold=%d action=%s\n",
   (unsigned long long)std::uint64_t(pos.key()),int(c3x018_root_context_call),
   int(move),int(threshold),decision);
  std::fclose(out);
 }
}
'''
s=s.replace(anchor,anchor+"\n"+logger,1)
s='#include <cstdio>\n'+s
f.write_text(s)
Path(a.out_manifest).write_text(json.dumps({"schema":"c3x027-capture-prune-direct-source-outcome-v1","actions":["DEPTH_CONTINUE","NO_DISCOVERED_ATTACK_CONTINUE","DISCOVERED_ATTACK_RETAIN"],"no_original_SEE_boolean_or_TT_mutations":True,"private_event_log":True},indent=2)+"\n")
print("C3X027_CAPTURE_BRANCH_SOURCE_PATCH_PASS")
