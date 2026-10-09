#!/usr/bin/env python3
"""C3X 0.14 source-native root-key pin-site and PSQ fallback routing observer.

Requires FIRST existing four PIN operator site observers. Adds only counters,
does not edit NNUE/classical selection or legally possible chess moves.
"""
import argparse,hashlib,json
from pathlib import Path

EXTRA_FIELDS=("root_key","root_legal_pinned_checks","root_legal_pin_rejects",
 "root_see_pinned_masks","root_mobility_pin_blockers","root_WeakQueen_hits",
 "eval_calls","eval_selected_classical","eval_selected_NNUE",
 "eval_NNUE_option_PSQ_classic_fallback")
def rep(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError("C3X014_ROOT_PIN_ANCHOR_"+name+"_"+str(n))
    return s.replace(a,b,1)
def patch(root):
    root=Path(root);fn={n:root/"src"/n for n in
       ("c3x014_pin_trace.h","position.cpp","evaluate.cpp","search.cpp")}
    old={n:p.read_bytes() for n,p in fn.items()}
    x={n:b.decode() for n,b in old.items()}
    h=x["c3x014_pin_trace.h"]
    h=rep(h,"struct C3X014PinTrace {\n",
          "struct C3X014PinTrace {\n"+"".join("  std::uint64_t "+k+"=0;\n" for k in EXTRA_FIELDS),
          "ROOT_EXTRA_FIELDS")
    x["c3x014_pin_trace.h"]=h
    p=x["position.cpp"]
    p=rep(p,"    ++c3x014_pin.legal_pinned_tests;",
        """    ++c3x014_pin.legal_pinned_tests;
    if (key()==c3x014_pin.root_key) {
       ++c3x014_pin.root_legal_pinned_checks;
       if (!aligned(from,to,square<KING>(us))) ++c3x014_pin.root_legal_pin_rejects;
    }""","EXACT_ROOT_LEGAL_BRANCH")
    p=rep(p,"            ++c3x014_pin.see_masked_recapture_episodes;",
        """            ++c3x014_pin.see_masked_recapture_episodes;
            if (key()==c3x014_pin.root_key) ++c3x014_pin.root_see_pinned_masks;""",
        "EXACT_ROOT_SEE_BRANCH")
    x["position.cpp"]=p
    e=x["evaluate.cpp"]
    e=rep(e,"      ++c3x014_pin.classical_mobility_nonzero_pin_blockers;",
        """      ++c3x014_pin.classical_mobility_nonzero_pin_blockers;
      if (pos.key()==c3x014_pin.root_key) ++c3x014_pin.root_mobility_pin_blockers;""",
        "EXACT_ROOT_CLASSIC_MOBILITY")
    e=rep(e,"              ++c3x014_pin.classical_WeakQueen_hits;",
        """              ++c3x014_pin.classical_WeakQueen_hits;
              if (pos.key()==c3x014_pin.root_key) ++c3x014_pin.root_WeakQueen_hits;""",
        "EXACT_ROOT_CLASSIC_WEAKQUEEN")
    e=rep(e,"  bool useClassical = !useNNUE || abs(psq) > 2048;",
        """    bool useClassical = !useNNUE || abs(psq) > 2048;
    ++c3x014_pin.eval_calls;
    if (useClassical) {
       ++c3x014_pin.eval_selected_classical;
       if (useNNUE && abs(psq) > 2048) ++c3x014_pin.eval_NNUE_option_PSQ_classic_fallback;
    } else ++c3x014_pin.eval_selected_NNUE;""","EVAL_BRANCH_NO_PREDICATE_CHANGE")
    x["evaluate.cpp"]=e
    s=x["search.cpp"]
    s=rep(s,"  c3x014_pin = C3X014PinTrace{};",
        "  c3x014_pin = C3X014PinTrace{};\n  c3x014_pin.root_key=rootPos.key();",
        "ROOT_KEY_INIT")
    anchor='    << " legal_normal_tests=" << c3x014_pin.legal_normal_tests'
    extras="".join('    << " '+k+'=" << c3x014_pin.'+k+'\n' for k in EXTRA_FIELDS)
    s=rep(s,anchor,extras+anchor,"ROOT_PSQR_COUNTER_DUMP")
    x["search.cpp"]=s
    for n,s in x.items():fn[n].write_text(s)
    return {"schema":"c3x-014-real-pin-root-key-and-Eval-PSQ-branch-observer-v1",
       "SF16":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "extra_fields":EXTRA_FIELDS,
       "root_key_scope":"Exact 64-bit source root position key. Root counters reflect only actually executed calls during search; they can be zero even with a legal root pin.",
       "eval_predicate":"bool useClassical = !useNNUE || abs(psq) > 2048; original unchanged",
       "original_sha256":{n:hashlib.sha256(v).hexdigest() for n,v in old.items()},
       "patched_sha256":{n:hashlib.sha256(v.encode()).hexdigest() for n,v in x.items()}}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args();v=patch(a.source)
    p=Path(a.out_manifest);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+"\n")
    print("C3X014_ROOT_KEY_AND_PSQ_FALLBACK_BRANCH_PATCH_PASS",json.dumps(v["patched_sha256"]),flush=True)
