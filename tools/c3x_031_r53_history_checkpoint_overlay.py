#!/usr/bin/env python3
"""R53 passive history checkpoint/contact observer, reused R41 semantics.
Fixed attempt27 in two R51 cases; first root return marker only. No intervention on history.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_031_r41_history_contact_overlay import RULES

def rules():
    out={}
    for n,rs in RULES.items():
        out[n]=[]
        for old,new,label in rs:
            if label=="implementation":
                new=new.replace("thread_local uint64_t r41_serial = 0;","thread_local uint64_t r41_serial = 0;\nthread_local bool r53_marked = false;")
                new=new.replace("    r41_serial=0;","    r41_serial=0;\n    r53_marked=false;")
            elif label=="y1_marker":
                new="""              if (c3x_r41_active && !r53_marked) {
                  r53_marked=true;
                  r41_events << ++r41_serial << " endpoint 0 E " << int(value) << '\\n';
              }
              ++c3xCandidate;"""
            elif label=="root_hook":
                new=new.replace("c3xAttempt==17","c3xAttempt==27")
                new=new.replace(" || rootDepth!=14 || completedDepth!=13","")
            out[n].append((old,new,label))
    return out

def transform(src,reverse=False):
    out={}
    for n,rs in rules().items():
        s=src[n]
        for a,b,l in reversed(rs) if reverse else rs:
            if reverse:a,b=b,a
            if s.count(a)!=1:raise ValueError("R53 anchor "+n+" "+l)
            s=s.replace(a,b,1)
        out[n]=s
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("manifest",type=Path);a=p.parse_args()
    root=a.source/"src";old={n:(root/n).read_bytes().decode() for n in rules()};new=transform(old)
    if transform(new,True)!=old:raise ValueError("roundtrip")
    for n,s in new.items():(root/n).write_bytes(s.encode())
    h=lambda x:hashlib.sha256(x.encode()).hexdigest()
    a.manifest.write_text(json.dumps({"before":{n:h(s) for n,s in old.items()},"after":{n:h(s) for n,s in new.items()},"roundtrip":True,"scope":"R41 read/write instrumentation at fixed attempt27, no state mutation"},sort_keys=True)+"\n")
if __name__=="__main__":main()
