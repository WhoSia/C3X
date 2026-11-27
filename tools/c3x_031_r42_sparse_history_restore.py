#!/usr/bin/env python3
"""R42: conditional sparse scalar history intervention on R41 observer.
No changes to node counters, TT, stack, root order or draw rule.
Requires exact natural receiver snapshot and verified donor snapshot.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_031_r41_history_contact_overlay import transform

CONTACT = (("main",6556),("main",7738),("cont",1427258),("cont",1741626),
           ("cont",1743516),("cont",1743674),("counter",369))
PLACEBO = (("cont",1427100),("cont",1741468))
ANCHOR='    std::ofstream snap("r41_snapshot.bin",std::ios::binary|std::ios::trunc);'
HELPER=r'''
    // Conditional R42 sparse intervention. Validate ALL native receiver bytes
    // and donor layout before changing any of the predeclared cells.
    const char* mode=std::getenv("C3X_R42_MODE");
    if (mode && std::strcmp(mode,"off")!=0) {
        const bool contact=std::strcmp(mode,"H7")==0 || std::strcmp(mode,"self")==0;
        const bool placebo=std::strcmp(mode,"P2")==0;
        if (!contact && !placebo) std::abort();
        const char* receiver=std::getenv("C3X_R42_RECEIVER");
        const char* donor=std::getenv("C3X_R42_DONOR");
        if (!receiver || !donor) std::abort();
        std::ifstream in(receiver,std::ios::binary), other(donor,std::ios::binary);
        if (!in || !other) std::abort();
        std::vector<char> values[4];
        for (int k=0;k<4;++k) {
            const auto& r=r41_ranges[k];
            std::vector<char> expected(r.size);
            values[k].resize(r.size);
            if (!in.read(expected.data(),r.size) || !other.read(values[k].data(),r.size)
                || std::memcmp(expected.data(),r.base,r.size)!=0) std::abort();
        }
        if (in.peek()!=std::char_traits<char>::eof() || other.peek()!=std::char_traits<char>::eof())
            std::abort();
        struct Cell { int family; size_t index; };
        constexpr Cell h7[]={{0,6556},{0,7738},{2,1427258},{2,1741626},
                             {2,1743516},{2,1743674},{3,369}};
        constexpr Cell p2[]={{2,1427100},{2,1741468}};
        const Cell* cells=contact?h7:p2;
        const size_t count=contact?7:2;
        for (size_t i=0;i<count;++i) {
            const auto& r=r41_ranges[cells[i].family];
            if (cells[i].index>=r.size/r.width) std::abort();
        }
        for (size_t i=0;i<count;++i) {
            const auto& r=r41_ranges[cells[i].family];
            const auto off=cells[i].index*r.width;
            std::memcpy(const_cast<char*>(r.base)+off,values[cells[i].family].data()+off,r.width);
        }
        std::cerr << "C3X_R42_RESTORE mode=" << mode << " cells=" << count << '\n';
    }
'''
def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("manifest",type=Path)
    a=p.parse_args()
    root=a.source/"src"
    names=("search.cpp","movepick.h")
    old={n:(root/n).read_bytes().decode() for n in names}
    r41=transform(old)
    s=r41["search.cpp"]
    if s.count(ANCHOR)!=1: raise ValueError("R42 anchor")
    r42=dict(r41,**{"search.cpp":s.replace(ANCHOR,HELPER+ANCHOR,1)})
    restored=dict(r42,**{"search.cpp":r42["search.cpp"].replace(HELPER,"",1)})
    if restored!=r41 or transform(restored,True)!=old: raise ValueError("R42 reverse")
    for n,s in r42.items():(root/n).write_bytes(s.encode())
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    h=lambda s:hashlib.sha256(s.encode()).hexdigest()
    a.manifest.write_text(json.dumps({"source_before":{n:h(s) for n,s in old.items()},
      "source_after":{n:h(s) for n,s in r42.items()},"H7":CONTACT,"P2":PLACEBO,
      "no_node_counter_mutation":True,"roundtrip":True},indent=2)+"\n")
if __name__=="__main__":main()
