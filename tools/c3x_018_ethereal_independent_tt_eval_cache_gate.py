#!/usr/bin/env python3
"""Source-strict independent Ethereal cached TT static evaluation gate.

No reinterpretation as Stockfish TT score-as-better-evaluation V. Original
Ethereal TT eval cache consumed only if valid, in main search and qsearch.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError("C3X018_ETHEREAL_CACHE_"+label+"_ANCHOR_"+str(n))
 return s.replace(a,b,1)

GATE=r"""
// C3X018 source research: Ethereal cached TT static evaluation route only.
static unsigned long long c3x018_eth_cache_contacts = 0;
static int c3x018_eth_cache_gate(const char *site) {
    const char *arm = getenv("C3X018_ETH_TT_CACHE_GATE");
    if (!arm || strcmp(arm, "all") != 0) return 0;
    ++c3x018_eth_cache_contacts;
    if (c3x018_eth_cache_contacts <= 16) {
        printf("info string c3x018_eth_cache_contact site=%s ordinal=%llu\n",
               site, c3x018_eth_cache_contacts);
        fflush(stdout);
    }
    return 1;
}
"""

def patch(s):
 s=one(s,"int LMRTable[64][64];",GATE+"\nint LMRTable[64][64];","GATE")
 s=one(s,
   "eval = ns->eval = inCheck ? VALUE_NONE\n         : ttEval != VALUE_NONE ? ttEval : evaluateBoard(thread, board);",
   'eval = ns->eval = inCheck ? VALUE_NONE\n'
   '         : (ttEval != VALUE_NONE && !c3x018_eth_cache_gate("main"))\n'
   '               ? ttEval : evaluateBoard(thread, board);',"MAIN")
 s=one(s,
   "eval = ns->eval = ttEval != VALUE_NONE\n                    ? ttEval : evaluateBoard(thread, board);",
   'eval = ns->eval = (ttEval != VALUE_NONE && !c3x018_eth_cache_gate("qsearch"))\n'
   '                    ? ttEval : evaluateBoard(thread, board);',"QSEARCH")
 return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/search.c"
 old=f.read_bytes();new=patch(old.decode()).encode()
 f.write_bytes(new)
 obj={
   "schema":"c3x018-independent-ethereal-source-TT-static-eval-cache-v1",
   "engine_source":"AndyGrant/Ethereal",
   "engine_git_sha":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
   "source_before_sha256":hashlib.sha256(old).hexdigest(),
   "source_after_sha256":hashlib.sha256(new).hexdigest(),
   "memory_object":"TT cached static evaluation ttEval, not TT search value ttValue",
   "sites":["main search ttEval fallback","qsearch ttEval fallback"],
   "mode":"C3X018_ETH_TT_CACHE_GATE=all",
   "limits":["A different engine architecture and narrower/different mechanism than Stockfish V",
             "No physical TT saved score value and bound causal carrier equivalence asserted",
             "Source gate prints up to first 16 actual cached evaluation reads per process"]}
 out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(obj,indent=2)+"\n")
 print("C3X018_INDEPENDENT_ETHEREAL_STATIC_CACHE_GATE_SOURCE_PATCH_PASS")
if __name__=="__main__":main()
