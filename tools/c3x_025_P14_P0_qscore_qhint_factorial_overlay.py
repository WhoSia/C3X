#!/usr/bin/env python3
"""P14-P0 qsearch TT score-return vs move-hint 2x2 source intervention.
Only source patch orchestration is Python. Original mechanics remain C++.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import SHA,patch as p8,restore as u8
from c3x_025_P11_native_stratified_real_TT_return_SEE_guard_root_update_overlay import patch_prepatched as p11,restore as u11
from c3x_025_P12_native_source_recursive_frame_TT_return_overlay import patch_prepatched as p12,restore as u12
from c3x_025_P13_R4_original_writer_to_q_assignment_overlay import patch as r4,undo as ur4
TT_HOOK="void c3x025_p13_qassignment(int assigned,int move,int ply) {"
SEARCH_FWD="void c3x025_p13_qbest(int,int,int);\n"
QSCORE='''        c3x025_p8_consume(tte,posKey,"Q_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,ttDepth,ss->ply);
        c3x025_p11_return(tte,posKey,false,ss->ply,ttDepth,int(ttValue),int(alpha),int(beta));
        return ttValue;'''
QSCORE_NEW='''        if (!c3x025_p14_skip_q_score(ss->ply)) {
            c3x025_p8_consume(tte,posKey,"Q_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,ttDepth,ss->ply);
            c3x025_p11_return(tte,posKey,false,ss->ply,ttDepth,int(ttValue),int(alpha),int(beta));
            return ttValue;
        }'''
QHINT="    ttMove = ss->ttHit ? tte->move() : MOVE_NONE;\n"
QHINT_NEW=QHINT+"    if (ss->ttHit && ttMove && c3x025_p14_skip_q_hint(ss->ply)) ttMove=MOVE_NONE;\n"
FWD="""bool c3x025_p14_skip_q_score(int);
bool c3x025_p14_skip_q_hint(int);
"""
CPP=r"""
// P14-P0 original qsearch direct source operator intervention, not SEE coercion.
// 0=SHAM,1=SCORE_CUTOFF_FIRST,2=MOVE_HINT_FIRST,3=BOTH_FIRST.
static thread_local bool c3x025_p14_score_contact=false,c3x025_p14_hint_contact=false;
static thread_local bool c3x025_p14_score_used=false,c3x025_p14_hint_used=false;
int c3x025_p14_arm() {
    const char* s=std::getenv("C3X025_P14_ARM");
    if (!s || std::strcmp(s,"SHAM")==0) return 0;
    if (std::strcmp(s,"SCORE")==0) return 1;
    if (std::strcmp(s,"HINT")==0) return 2;
    if (std::strcmp(s,"BOTH")==0) return 3;
    std::abort();
}
bool c3x025_p14_skip_q_score(int ply) {
    if (!c3x025_p8_on()) return false;
    const int arm=c3x025_p14_arm();
    const bool mutate=(arm&1) && !c3x025_p14_score_used;
    if (!c3x025_p14_score_contact) {
       c3x025_p14_score_contact=true;
       sync_cout << "info string c3x025_p14 kind=Q_SCORE_RETURN_BOUND_CONTACT"
                 << " arm=" << arm << " mutated=" << int(mutate)
                 << " ply=" << ply << sync_endl;
    }
    if (mutate) c3x025_p14_score_used=true;
    return mutate;
}
bool c3x025_p14_skip_q_hint(int ply) {
    if (!c3x025_p8_on()) return false;
    const int arm=c3x025_p14_arm();
    const bool mutate=(arm&2) && !c3x025_p14_hint_used;
    if (!c3x025_p14_hint_contact) {
       c3x025_p14_hint_contact=true;
       sync_cout << "info string c3x025_p14 kind=Q_NONZERO_HINT_CONTACT"
                 << " arm=" << arm << " mutated=" << int(mutate)
                 << " ply=" << ply << sync_endl;
    }
    if (mutate) c3x025_p14_hint_used=true;
    return mutate;
}
"""
def sub(s,old,new,where):
    if s.count(old)!=1:raise ValueError("P14_EXACT_SOURCE_ANCHOR_"+where+"_"+str(s.count(old)))
    return s.replace(old,new,1)
def patch(pre):
    if set(pre)!=set(SHA):raise ValueError("P14_PREPATCHED_SOURCE_KEYS")
    t=pre["tt.cpp"].decode();s=pre["search.cpp"].decode()
    t=sub(t,TT_HOOK,CPP+"\n"+TT_HOOK,"tt_cpp")
    s=sub(s,SEARCH_FWD,SEARCH_FWD+FWD,"search_fwd")
    s=sub(s,QSCORE,QSCORE_NEW,"q_cutoff_score")
    s=sub(s,QHINT,QHINT_NEW,"q_hint")
    z={"tt.cpp":t.encode(),"search.cpp":s.encode()}
    if undo(z)!=pre:raise ValueError("P14_SOURCE_INVERSE_NOT_P13_R4")
    return z
def undo(post):
    t=post["tt.cpp"].decode();s=post["search.cpp"].decode()
    t=sub(t,CPP+"\n"+TT_HOOK,TT_HOOK,"undo_tt")
    s=sub(s,QHINT_NEW,QHINT,"undo_hint")
    s=sub(s,QSCORE_NEW,QSCORE,"undo_score")
    s=sub(s,SEARCH_FWD+FWD,SEARCH_FWD,"undo_fwd")
    return {"tt.cpp":t.encode(),"search.cpp":s.encode()}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args()
    src=Path(a.root)/"src"
    raw={n:(src/n).read_bytes() for n in SHA}
    x8,_=p8(raw);x11=p11(x8);x12=p12(x11);x13=r4(x12);x14=patch(x13)
    if u8(u11(u12(ur4(undo(x14)))))!=raw:raise ValueError("P14_ALL_LAYERS_NOT_EXACT_BYTE_RESTORED")
    for n,data in x14.items():(src/n).write_bytes(data)
    meta={"schema":"c3x025-P14-P0-native-source-Q-score-return-vs-hint-factorial-v1",
      "original_upstream_SHA256":SHA,
      "P8_then_P11_then_P12_reverse_exact_original_source_byte_equal":True,
      "P8_P11_P12_P13_R4_P14_P0_exact_upstream_inverse":True,
      "modified_SHA256":{n:hashlib.sha256(v).hexdigest() for n,v in x14.items()},
      "arms":{"SHAM":0,"SCORE":1,"HINT":2,"BOTH":3},
      "intervention_scope":"ONE_REAL_FIRST_Q_BOUNDED_SCORE_RETURN_AND_ONE_FIRST_NONZERO_Q_MOVE_HINT",
      "qscore_early_return_skipped_at_most_once":True,
      "qhint_assignment_replaced_with_MOVE_NONE_at_most_once":True,
      "original_see_guards_not_forced":True,
      "natural_TT_SEE_root_mediation_proven":False,
      "speed_or_strength_improvement_proven":False}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("C3X025_P14_P0_SOURCE_EXACT_INV",meta,flush=True)
if __name__=="__main__":main()
