#!/usr/bin/env python3
"""P14-P1 adds source-native qbranch and final root contender summaries to P14-P0.
Runs original Stockfish16 C++; Python applies exact reversible patches only.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import SHA
from c3x_025_P14_P0_qscore_qhint_factorial_overlay import main as unused,patch as p0,undo as u0
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import patch as p8,restore as u8
from c3x_025_P11_native_stratified_real_TT_return_SEE_guard_root_update_overlay import patch_prepatched as p11,restore as u11
from c3x_025_P12_native_source_recursive_frame_TT_return_overlay import patch_prepatched as p12,restore as u12
from c3x_025_P13_R4_original_writer_to_q_assignment_overlay import patch as r4,undo as ur4
from c3x_025_P9_R1_native_root_final_source_endpoint_overlay import patch as p9,restore as u9

TT_LEAVE="void c3x025_p12_leave(uint64_t frameid) {"
ROOT_EXIT="    c3x025_p12_frames.pop_back();"
SEARCH_FWD="bool c3x025_p14_skip_q_hint(int);\n"
Q_ASSIGN="        c3x025_p13_qassignment(int(value),int(ss->currentMove),ss->ply);"
Q_BEST="            c3x025_p13_qbest(int(value),int(ss->currentMove),ss->ply);"
ROOT_BEST='  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
FWD="void c3x025_p14p1_qtrace(int,int,int,int,int);\n"
TRACK=r"""
// P14-P1: observer of original qsearch return/bestValue events, not a
// behavioural intervention. No position keys or PGNs enter the digest.
static thread_local uint64_t c3x025_p14p1_qhash=14695981039346656037ULL;
static thread_local uint64_t c3x025_p14p1_qevents=0;
static thread_local uint64_t c3x025_p14p1_qret=0;
static thread_local uint64_t c3x025_p14p1_qbest=0;
void c3x025_p14p1_qtrace(int kind,int ply,int score,int move,int window) {
    if (!c3x025_p8_on()) return;
    const unsigned v[]={unsigned(kind),unsigned(ply),unsigned(score),
                        unsigned(move),unsigned(window)};
    for (const unsigned element:v)
        c3x025_p14p1_qhash=(c3x025_p14p1_qhash ^ uint64_t(element))*1099511628211ULL;
    ++c3x025_p14p1_qevents;
    if (kind==1) ++c3x025_p14p1_qret;
    if (kind==2) ++c3x025_p14p1_qbest;
}
"""
EXIT_NEW="""    if (e.id==e.root) {
        sync_cout << "info string c3x025_p14p1 kind=ROOT_FRAME"
                  << " root_id=" << e.root
                  << " qhash=" << c3x025_p14p1_qhash
                  << " qevents=" << c3x025_p14p1_qevents
                  << " qreturns=" << c3x025_p14p1_qret
                  << " qbest=" << c3x025_p14p1_qbest << sync_endl;
    }
"""+ROOT_EXIT
ROOT_CODE=r"""  if (c3x025_p8_on()) {
      uint64_t h=14695981039346656037ULL;
      unsigned viable=0, nonempty=0;
      for (const auto& rm : bestThread->rootMoves) {
          if (!rm.pv.empty()) ++nonempty;
          if (rm.score != -VALUE_INFINITE) ++viable;
          const unsigned moveId=rm.pv.empty()?0u:unsigned(rm.pv[0]);
          const unsigned elements[]={moveId,unsigned(rm.score),
             unsigned(rm.uciScore),unsigned(rm.averageScore),
             unsigned(rm.pv.size()),unsigned(rm.scoreLowerbound),
             unsigned(rm.scoreUpperbound)};
          for (const unsigned element:elements)
              h=(h^uint64_t(element))*1099511628211ULL;
      }
      sync_cout << "info string c3x025_p14p1 kind=ROOT_CONTENDER_SET"
                << " digest=" << h
                << " count=" << bestThread->rootMoves.size()
                << " viable=" << viable << " nonempty_pv=" << nonempty
                << " first_score=" << int(bestThread->rootMoves[0].score)
                << " depth=" << int(bestThread->completedDepth)
                << sync_endl;
  }
"""+ROOT_BEST
def once(s,old,new,label):
    if s.count(old)!=1:raise ValueError("P14P1_EXACT_ANCHOR_"+label+"_"+str(s.count(old)))
    return s.replace(old,new,1)
def patch(pre):
    t=pre["tt.cpp"].decode();s=pre["search.cpp"].decode()
    t=once(t,TT_LEAVE,TRACK+"\n"+TT_LEAVE,"native_tt_scope")
    t=once(t,ROOT_EXIT,EXIT_NEW,"root_frame")
    s=once(s,SEARCH_FWD,SEARCH_FWD+FWD,"source_forward")
    s=once(s,Q_ASSIGN,Q_ASSIGN+"\n        c3x025_p14p1_qtrace(1,ss->ply,int(value),int(ss->currentMove),int(alpha));","qreturn")
    s=once(s,Q_BEST,Q_BEST+"\n            c3x025_p14p1_qtrace(2,ss->ply,int(value),int(ss->currentMove),int(beta));","qbest")
    s=once(s,ROOT_BEST,ROOT_CODE,"final_native_root_contenders")
    z={"tt.cpp":t.encode(),"search.cpp":s.encode()}
    if undo(z)!=pre:raise ValueError("P14P1_SOURCE_NOT_REVERSIBLE")
    return z
def undo(post):
    t=post["tt.cpp"].decode();s=post["search.cpp"].decode()
    t=once(t,EXIT_NEW,ROOT_EXIT,"undo_root_frame")
    t=once(t,TRACK+"\n"+TT_LEAVE,TT_LEAVE,"undo_tt")
    s=once(s,ROOT_CODE,ROOT_BEST,"undo_root_set")
    s=once(s,Q_BEST+"\n            c3x025_p14p1_qtrace(2,ss->ply,int(value),int(ss->currentMove),int(beta));",Q_BEST,"undo_qbest")
    s=once(s,Q_ASSIGN+"\n        c3x025_p14p1_qtrace(1,ss->ply,int(value),int(ss->currentMove),int(alpha));",Q_ASSIGN,"undo_qreturn")
    s=once(s,SEARCH_FWD+FWD,SEARCH_FWD,"undo_forward")
    return {"tt.cpp":t.encode(),"search.cpp":s.encode()}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args()
    d=Path(a.root)/"src";original={n:(d/n).read_bytes() for n in SHA}
    p8s,_=p8(original);p11s=p11(p8s);p12s=p12(p11s);p13s=r4(p12s);p14s=p0(p13s)
    p14p9={"tt.cpp":p14s["tt.cpp"],"search.cpp":p9(p14s["search.cpp"].decode()).encode()}
    result=patch(p14p9)
    inv=undo(result)
    if inv!=p14p9 or u8(u11(u12(ur4(u0({"tt.cpp":inv["tt.cpp"],"search.cpp":u9(inv["search.cpp"].decode()).encode()})))))!=original:
        raise ValueError("P14P1_ALL_NATIVE_SOURCE_LAYERS_EXACT_REVERSE_FAILED")
    for n,v in result.items():(d/n).write_bytes(v)
    manifest={"schema":"c3x025-P14-P1-source-native-root-contender-and-qtrace-v1",
      "original_upstream_SHA256":SHA,
      "exact_reversible_P8_P11_P12_P13R4_P14P0_P9_P14P1":True,
      "final_source_sha256":{n:hashlib.sha256(v).hexdigest() for n,v in result.items()},
      "source_events":["q-recursive-parent-scores","q-parent-bestValue","root-frame-qdigest","original-root-candidate-set"],
      "source_interventions":"P14-P0 first eligible q score early return vs q move hint, SHAM and BOTH",
      "q_digest_excludes_private_full64_position_keys":True,
      "source_policy_unchanged_in_sham":True,
      "natural_SEE_mediation_proven":False,"Elo_improvement_proven":False}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("C3X025_P14_P1_SOURCE_REVERSE_CERT",json.dumps(manifest),flush=True)
if __name__=="__main__":main()
