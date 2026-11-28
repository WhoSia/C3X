#!/usr/bin/env python3
"""R56 reversible exact-image conditional history splice on the R53 observer."""
import argparse, hashlib, json
from pathlib import Path
from c3x_031_r53_history_checkpoint_overlay import transform, rules

ANCHOR='    std::ofstream snap("r41_snapshot.bin",std::ios::binary|std::ios::trunc);'
HELPER=r'''
    const char* r56_receiver=std::getenv("C3X_R56_RECEIVER");
    const char* r56_image=std::getenv("C3X_R56_IMAGE");
    if (r56_receiver || r56_image) {
        if (!r56_receiver || !r56_image) std::abort();
        std::ifstream in(r56_receiver,std::ios::binary), image(r56_image,std::ios::binary);
        if (!in || !image) std::abort();
        std::vector<char> desired[4];
        for (int k=0;k<4;++k) {
            const auto& r=r41_ranges[k];
            std::vector<char> expected(r.size);
            desired[k].resize(r.size);
            if (!in.read(expected.data(),r.size) || !image.read(desired[k].data(),r.size)
                || std::memcmp(expected.data(),r.base,r.size)!=0) std::abort();
        }
        if (in.peek()!=std::char_traits<char>::eof() || image.peek()!=std::char_traits<char>::eof())
            std::abort();
        size_t changed=0;
        for (int k=0;k<4;++k) {
            const auto& r=r41_ranges[k];
            for (size_t off=0;off<r.size;off+=r.width) {
                if (std::memcmp(r.base+off,desired[k].data()+off,r.width)!=0) {
                    std::memcpy(const_cast<char*>(r.base)+off,desired[k].data()+off,r.width);
                    ++changed;
                }
            }
        }
        std::cerr << "C3X_R56_SPLICE changed=" << changed << '\n';
    }
'''
def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path);p.add_argument("manifest",type=Path);a=p.parse_args()
    root=a.source/"src"
    old={n:(root/n).read_bytes().decode() for n in rules()}
    observer=transform(old)
    s=observer["search.cpp"]
    if s.count(ANCHOR)!=1: raise ValueError("R56 anchor")
    new=dict(observer,**{"search.cpp":s.replace(ANCHOR,HELPER+ANCHOR,1)})
    restored=dict(new,**{"search.cpp":new["search.cpp"].replace(HELPER,"",1)})
    if restored!=observer or transform(restored,True)!=old:raise ValueError("R56 reverse")
    for n,s in new.items():(root/n).write_bytes(s.encode())
    h=lambda s:hashlib.sha256(s.encode()).hexdigest()
    a.manifest.write_text(json.dumps({"before":{n:h(s) for n,s in old.items()},"after":{n:h(s) for n,s in new.items()},"roundtrip":True,"scope":"R53 attempt27; history scalar image only, no node reset"},sort_keys=True)+"\n")
if __name__=="__main__":main()
