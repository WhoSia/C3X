#!/usr/bin/env python3
"""Source-exact TT move route intervention: suppress matching ttMove use only.

Overlay on C3X018 physical epoch TT source patch. Preserves TT score/bound,
probe result and direct TT early-cutoff branch. Prevents TT move hint being
handed to search move ordering/related heuristics for matching source slot.
Not a unique natural mediator certificate.
"""
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X018_TT_MOVE_GATE_{label}_COUNT_{n}")
    return s.replace(a,b,1)

def patch_tt(s):
    old='''    const bool block = (std::strcmp(mode, "R") == 0 ||
                        std::strcmp(mode, "WR") == 0)
                   && exact_key && c3x018_target(key, slot, epoch);'''
    new='''    const bool block = ((std::strcmp(mode, "R") == 0 ||
                         std::strcmp(mode, "WR") == 0)
                        || (std::strcmp(mode, "M") == 0
                            && std::strcmp(site, "tt_move") == 0))
                   && exact_key && c3x018_target(key, slot, epoch);'''
    return once(s,old,new,"TT_MODE")

def patch_search(s):
    s=once(s,
      '''    ttMove =  rootNode ? thisThread->rootMoves[thisThread->pvIdx].pv[0]
            : ss->ttHit    ? tte->move() : MOVE_NONE;
    ttCapture = ttMove && pos.capture_stage(ttMove);''',
      '''    ttMove =  rootNode ? thisThread->rootMoves[thisThread->pvIdx].pv[0]
            : ss->ttHit    ? tte->move() : MOVE_NONE;
    if (!rootNode && ss->ttHit && ttMove &&
        c3x018_consumer_gate("tt_move", posKey, tte, ss->ply, depth,
                            int(alpha), int(beta), int(ttMove))
        )
        ttMove = MOVE_NONE;
    ttCapture = ttMove && pos.capture_stage(ttMove);''',"MAIN_MOVE")
    s=once(s,
       '''    ttMove = ss->ttHit ? tte->move() : MOVE_NONE;
    pvHit = ss->ttHit && tte->is_pv();''',
       '''    ttMove = ss->ttHit ? tte->move() : MOVE_NONE;
    if (ss->ttHit && ttMove &&
        c3x018_consumer_gate("tt_move", posKey, tte, ss->ply, ttDepth,
                            int(alpha), int(beta), int(ttMove)))
        ttMove = MOVE_NONE;
    pvHit = ss->ttHit && tte->is_pv();''',"QSEARCH_MOVE")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    root=Path(a.source)/"src"
    changes={}
    for filename,transform in (("tt.cpp",patch_tt),("search.cpp",patch_search)):
        f=root/filename;old=f.read_bytes()
        new=transform(old.decode()).encode();f.write_bytes(new)
        changes[filename]={"before":hashlib.sha256(old).hexdigest(),
                           "after":hashlib.sha256(new).hexdigest()}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x018-targeted-TT-move-hint-read-route-gate-v1",
      "mode":"M","modified":changes,
      "read_event":"c3x018_lineage kind=reader_block site=tt_move",
      "scope":["Matching full64 writer shadow key, physical slot, accepted payload-write epoch",
               "Mute returned ttMove before move ordering; TT score and bounds unchanged",
               "May also affect pruning/heuristics using ttMove, not isolated MovePicker alone",
               "Main and qsearch; root TT move unaffected (rootNode guarded)",
               "R original early cutoff remains unchanged; M does not block early cutoff",
               "No proof of sole natural TT reader mediating a final move"]
    },indent=2)+"\n")
    print("C3X018_TT_MOVE_HINT_ROUTE_NATIVE_SOURCE_PATCH_APPLIED")
if __name__=="__main__":main()
