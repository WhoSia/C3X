#!/usr/bin/env python3
"""Strict SF16 / SF17 same-semantic-site global TT evaluation override suppression.

Two distinct native source implementations, not shared TT layout or key-space.
Source exact anchors fail closed. This is NOT physically targeted V intervention.
"""
import argparse,hashlib,json
from pathlib import Path

PREAMBLE=r"""
// C3X018 source-exact observer + global TT bound-value-as-evaluation gate.
// ONLY one-thread independent cold native research processes.
namespace {
unsigned long long c3x018_global_v_contacts = 0;
bool c3x018_global_v_gate(const char* site) {
    const char* mode = std::getenv("C3X018_GLOBAL_TT_EVAL_GATE");
    if (!mode || std::strcmp(mode,"both") != 0)
        return false;
    ++c3x018_global_v_contacts;
    if (c3x018_global_v_contacts <= 16)
        sync_cout << "info string c3x018_global_tt_eval_contact"
                  << " site=" << site
                  << " ordinal=" << c3x018_global_v_contacts << sync_endl;
    return true;
}
} // C3X018_SOURCE_GLOBAL_V
"""
def one(s,a,b,k):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_GLOBAL_V_{k}_SOURCE_ANCHOR_COUNT_{n}")
 return s.replace(a,b,1)

def patch(s,version):
 s=one(s,"namespace Stockfish {", "#include <cstdlib>\n#include <cstring>\nnamespace Stockfish {\n"+PREAMBLE,"NAMESPACE")
 if version=="sf16":
    s=one(s,"            eval = ttValue;",
       '            if (!c3x018_global_v_gate("main")) eval = ttValue;',"MAIN16")
    s=one(s,"                bestValue = ttValue;",
       '                if (!c3x018_global_v_gate("qsearch")) bestValue = ttValue;',"QS16")
 elif version=="sf17":
    s=one(s,"            eval = ttData.value;",
       '            if (!c3x018_global_v_gate("main")) eval = ttData.value;',"MAIN17")
    s=one(s,"                bestValue = ttData.value;",
       '                if (!c3x018_global_v_gate("qsearch")) bestValue = ttData.value;',"QS17")
 else:raise RuntimeError("BAD_VERSION")
 return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--version",choices=["sf16","sf17"],required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/search.cpp"
 old=f.read_bytes();new=patch(old.decode(),a.version).encode();f.write_bytes(new)
 result={"schema":"c3x018-cross-version-global-TT-value-evaluation-native-v1",
   "version":a.version,"file":"src/search.cpp",
   "source_before_sha256":hashlib.sha256(old).hexdigest(),
   "source_after_sha256":hashlib.sha256(new).hexdigest(),
   "source_sites":["bound-conditioned TT as evaluation in main search",
                   "bound-conditioned TT as evaluation in qsearch"],
   "mode":"C3X018_GLOBAL_TT_EVAL_GATE=both",
   "limits":["This is global TT evaluation override suppression, not selective physical TT writer-reader mediation",
             "TT logical data structure and eval differ SF16 vs SF17, despite matching semantic branch role",
             "Only affected writes happen in existing unchanged engine code; extra source gate prints <=16 contacts per process",
             "Root order not forced in this court; original game FEN uses proper halfmove clock"]}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(result,indent=2)+"\n")
 print("C3X018_CROSS_VERSION_TT_EVAL_SOURCE_PATCH_APPLIED",a.version)
if __name__=="__main__":main()
