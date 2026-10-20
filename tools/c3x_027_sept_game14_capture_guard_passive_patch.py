#!/usr/bin/env python3
"""Passive source exact capture-prune decision observer for exposed Sept game14.
No SEE/TT/root/search value edits. Logs only pre-frozen physical source tuple.
"""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--source',required=True);p.add_argument('--out-manifest',required=True)
a=p.parse_args()
file=Path(a.source)/'src/search.cpp'
s=file.read_text()
needle='if (!c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied))'
if s.count(needle)!=1:raise RuntimeError('ORIGINAL_CAPTURE_SEE_ANCHOR_NOT_UNIQUE_'+str(s.count(needle)))
insert='''const bool c3x027_g14_target =
                  std::getenv("C3X027_GAME14_CAPTURE_AUDIT")
                  && std::uint64_t(pos.key()) == 1379048240519518309ULL
                  && c3x018_root_context_call == 6
                  && int(move) == 292
                  && int(Value(-205)*depth) == -205;
              auto c3x027_g14_log = [&](const char* outcome) {
                  if (!c3x027_g14_target) return;
                  std::FILE* fh = std::fopen("private/C3X027_GAME14_CAPTURE_GUARD_ACTUAL.txt","a");
                  if (!fh) return;
                  const char* arm = std::getenv("C3X027_GAME14_ARM");
                  std::fprintf(fh,"arm=%s root_call=6 key64=1379048240519518309 move=292 threshold=-205 decision=%s\\n",
                              arm ? arm : "UNKNOWN",outcome);
                  std::fclose(fh);
              };
              const bool c3x027_g14_SEE_boolean =
                  c3x022_r2_see(pos,move,Value(-205)*depth,"capture_prune",&occupied);
              if (!c3x027_g14_SEE_boolean)'''
s=s.replace(needle,insert,1)
depth_old='''if (depth < 2 - capture)
                    continue;'''
if s.count(depth_old)!=1:raise RuntimeError('CAPTURE_DEPTH_GATE_ANCHOR_'+str(s.count(depth_old)))
s=s.replace(depth_old,'''if (depth < 2 - capture)
                 {
                    c3x027_g14_log("ACTUAL_DEPTH_CONTINUE");
                    continue;
                 }''',1)
attack_old='''if (!attacks)
                    continue;'''
if s.count(attack_old)!=1:raise RuntimeError('CAPTURE_DISCOVERED_ATTACK_GATE_ANCHOR_'+str(s.count(attack_old)))
s=s.replace(attack_old,'''if (!attacks)
                 {
                    c3x027_g14_log("ACTUAL_NO_DISCOVERED_ATTACK_CONTINUE");
                    continue;
                 }
                 c3x027_g14_log("DISCOVERED_ATTACK_RESCUE_SURVIVES");''',1)
file.write_text('#include <cstdio>\n'+s)
Path(a.out_manifest).write_text(json.dumps({
 'schema':'c3x027-postexposure-source-exact-native-capture-guard-observer',
 'source_site':'capture_prune','source_key64':'1379048240519518309',
 'root_call':6,'native_move':292,'threshold':-205,
 'nature':'passive_source_actual_branch_file_sink_only',
 'source_SEE_return_mutated':False,'TT_reader_policy_mutated':False,
 'source_rights':'Original Stockfish16 GPLv3 modified only inside CI runner'},indent=2)+'\n')
print('C3X027_G14_CAPTURE_GUARD_SOURCE_PATCH_PASS')
