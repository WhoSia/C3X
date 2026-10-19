#!/usr/bin/env python3
"""Append exact SHAM-only live SEE FEN records at presealed T3 source match."""
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
f=Path(a.source)/"src/search.cpp";s=f.read_text()
needle='    if (t3eligible) {\n        sync_cout << "info string c3x023_t3_source kind=contact"'
assert s.count(needle)==1,"EXACT_T3_PATCH_ANCHOR_MISSING"
insert='''    if (t3eligible && t3num==1 && std::strcmp(t3mode,"SHAM")==0) {
        std::FILE* snapshot=std::fopen("private/C3X027_LIVE_SEE_TARGET_FENS.txt","a");
        if (snapshot) {
            const std::string state=pos.fen();
            std::fprintf(snapshot,"c3x027_live_SEE site=%s key=%llu move=%d threshold=%d root_call=%d original=%d fen=%s\\n",
                site,(unsigned long long)std::uint64_t(pos.key()),int(move),int(threshold),
                int(c3x018_root_context_call),int(original),state.c_str());
            std::fclose(snapshot);
        }
    }
'''
s=s.replace(needle,insert+needle,1)
s='#include <cstdio>\n'+s
f.write_text(s)
Path(a.out_manifest).write_text('{"schema":"C3X027_PASSIVE_SHAM_ONLY_FEN_LOGGER","not_operator_intervention":true}\n')
print("C3X027_PASSIVE_FEN_PATCH_PASS")
