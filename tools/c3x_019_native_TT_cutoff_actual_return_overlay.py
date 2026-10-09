#!/usr/bin/env python3
"""Trace the ACTUAL Stockfish16 source TT cutoff RETURN after all guards.

Apply after C3X019 genuine TT eval assignment watcher. Reuses its independent
post-execution source logger; sites main_cutoff/qsearch_cutoff.
"""
import argparse,hashlib,json
from pathlib import Path

def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X019_NATIVE_CUTOFF_{label}_{n}")
    return s.replace(a,b,1)

def patch(s):
    s=one(s,
'''        if (pos.rule50_count() < 90)
            return ttValue;''',
'''        if (pos.rule50_count() < 90)
        {
            // Actual original main TT cutoff return, not mere candidate hit.
            c3x019_native_tt_eval_used(posKey,tte,ss->ply,
                int(depth),int(alpha),int(beta),int(ttValue),"main_cutoff");
            return ttValue;
        }''',"MAIN_RETURN")
    s=one(s,
'''        && !c3x018_consumer_gate("qsearch", posKey, tte, ss->ply,
                                 ttDepth, int(alpha), int(beta), int(ttValue)))
        return ttValue;''',
'''        && !c3x018_consumer_gate("qsearch", posKey, tte, ss->ply,
                                 ttDepth, int(alpha), int(beta), int(ttValue)))
    {
        // Actual original quiescence TT cutoff return.
        c3x019_native_tt_eval_used(posKey,tte,ss->ply,
            int(ttDepth),int(alpha),int(beta),int(ttValue),"qsearch_cutoff");
        return ttValue;
    }''',"QS_RETURN")
    return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/search.cpp";old=f.read_bytes()
 new=patch(old.decode()).encode();f.write_bytes(new)
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps({"schema":"c3x019-real-native-main-quiescence-TT-cutoff-return-source-watcher-v1",
   "before_sha256":hashlib.sha256(old).hexdigest(),
   "after_sha256":hashlib.sha256(new).hexdigest(),
   "watcher":"c3x019_native_tt_eval_used logged only at source original TT cutoff return",
   "sites":["main_cutoff","qsearch_cutoff"],
   "main_guard":"native original rule50<90, TT hit, bound, depth, non-PV conditions already passed",
   "limits":["value from cached TT cutoff is a distinct native use from eval=ttValue",
             "instrumentation must exactly preserve original final six-field UCI"]},indent=2)+"\n")
 print("C3X019_ACTUAL_NATIVE_TT_CUTOFF_RETURN_WATCH_READY")
if __name__=="__main__":main()
