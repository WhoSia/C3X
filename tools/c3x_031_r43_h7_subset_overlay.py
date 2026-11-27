#!/usr/bin/env python3
"""R43: vary only a frozen subset of R42 H7, with exact image checks.
No node/TT/stack/draw changes. Preserve R41 observer and R42 receiver gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_031_r41_history_contact_overlay import transform
from c3x_031_r42_sparse_history_restore import CONTACT, ANCHOR, HELPER

def once(s,a,b):
    if s.count(a)!=1: raise ValueError("R43 anchor "+a)
    return s.replace(a,b,1)

def helper():
    s=HELPER
    s=once(s,'const bool contact=std::strcmp(mode,"H7")==0 || std::strcmp(mode,"self")==0;',
             'const bool contact=std::strcmp(mode,"mask")==0;')
    s=once(s,'const bool placebo=std::strcmp(mode,"P2")==0;', 'const bool placebo=false;')
    s=once(s,'const Cell* cells=contact?h7:p2;\n        const size_t count=contact?7:2;',
             '''const char* raw=std::getenv("C3X_R43_MASK");
        if (!raw || !*raw) std::abort();
        char* end=nullptr;
        const long mask=std::strtol(raw,&end,10);
        if (*end || mask<0 || mask>127) std::abort();
        Cell selected[7];
        size_t count=0;
        for (int i=0;i<7;++i) if (mask & (1L<<i)) selected[count++]=h7[i];
        const Cell* cells=selected;''')
    return once(s,'std::cerr << "C3X_R42_RESTORE mode=" << mode << " cells=" << count',
                'std::cerr << "C3X_R43_RESTORE mask=" << mask << " cells=" << count')

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("manifest",type=Path)
    a=p.parse_args()
    root=a.source/"src"
    names=("search.cpp","movepick.h")
    old={n:(root/n).read_bytes().decode() for n in names}
    passive=transform(old)
    inserted=helper()
    new=dict(passive,**{"search.cpp":once(passive["search.cpp"],ANCHOR,inserted+ANCHOR)})
    if transform(dict(new,**{"search.cpp":once(new["search.cpp"],inserted,"")}),True)!=old:
        raise ValueError("R43 inverse")
    for n,s in new.items(): (root/n).write_bytes(s.encode())
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    h=lambda s:hashlib.sha256(s.encode()).hexdigest()
    a.manifest.write_text(json.dumps({"source_before":{n:h(s) for n,s in old.items()},
      "source_after":{n:h(s) for n,s in new.items()},"mask_bit_order":CONTACT,
      "node_counter_mutated":False,"roundtrip":True},indent=2)+"\n")
if __name__=="__main__":main()
