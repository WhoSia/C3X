#!/usr/bin/env python3
"""P14-P3: source-native guard-policy synthesis on pinned ORIGINAL Stockfish16.
Guard is narrow exploratory policy, not a proof of identical chess evaluation.
Only Python applies exact reversible source overlays; chess search is C++.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import SHA,patch as p8,restore as u8
from c3x_025_P11_native_stratified_real_TT_return_SEE_guard_root_update_overlay import patch_prepatched as p11,restore as u11
from c3x_025_P12_native_source_recursive_frame_TT_return_overlay import patch_prepatched as p12,restore as u12
from c3x_025_P13_R4_original_writer_to_q_assignment_overlay import patch as r4,undo as ur4
from c3x_025_P14_P0_qscore_qhint_factorial_overlay import patch as p0,undo as u0
from c3x_025_P9_R1_native_root_final_source_endpoint_overlay import patch as p9,restore as u9
from c3x_025_P14_P2_native_first_source_overlay import patch as p2,undo as u2
TT_ANCHOR="void c3x025_p12_leave(uint64_t frameid) {"
Q_ORIG="if (!c3x025_p14_skip_q_score(ss->ply)) {"
Q_GUARD="if (!(c3x025_p14p3_guard(ss->ply,int(ttValue),int(beta),int(pos.rule50_count()),bool(ss->inCheck)) || c3x025_p14_skip_q_score(ss->ply))) {"
FWD_ANCHOR="bool c3x025_p14_skip_q_hint(int);\n"
FWD_ADD="bool c3x025_p14p3_guard(int,int,int,int,bool);\n"
CPP=r"""
// P14-P3 exploratory narrow contextual source-policy guard.
// This never manufactures a move or evaluation and never changes SEE directly.
// LEGALITY GUARD != ALPHA-BETA SEMANTIC-PRESERVATION CERTIFICATE.
static thread_local bool c3x025_p14p3_used=false;
static thread_local bool c3x025_p14p3_first_logged=false;
int c3x025_p14p3_policy() {
  const char* p=std::getenv("C3X025_P14P3_POLICY");
  if(!p || std::strcmp(p,"SHAM")==0)return 0;
  if(std::strcmp(p,"GUARD")==0)return 1;
  std::abort();
}
bool c3x025_p14p3_guard(int ply,int score,int beta,int rule50,bool inCheck){
  if(!c3x025_p8_on()) return false;
  const int policy=c3x025_p14p3_policy();
  // Numeric band excludes mate-range and sentinel values, NOT a theorem
  // that TT may safely be ignored for game-theoretic reasons.
  const bool eligible=ply>=2 && ply<=6 && !inCheck && rule50<80
       && score>-1000 && score<1000 && beta>-1000 && beta<1000
       && std::abs(score-beta)<=64;
  const bool mutate=policy==1 && eligible && !c3x025_p14p3_used;
  if(!c3x025_p14p3_first_logged){
    c3x025_p14p3_first_logged=true;
    sync_cout << "info string c3x025_p14p3 kind=FIRST_ORIGINAL_QSCORE_CONTACT"
       << " eligible=" << int(eligible) << " mutated=" << int(mutate)
       << " policy=" << policy << " ply=" << ply
       << " tt_score=" << score << " beta=" << beta
       << " rule50=" << rule50 << " check=" << int(inCheck) << sync_endl;
  }
  if(mutate){
    c3x025_p14p3_used=true;
    sync_cout << "info string c3x025_p14p3 kind=GUARD_ACTUATED"
       << " eligible=1 mutated=1 policy=1 ply=" << ply
       << " tt_score=" << score << " beta=" << beta
       << " rule50=" << rule50 << " check=" << int(inCheck) << sync_endl;
  }
  return mutate;
}
"""
def once(s,a,b,label):
 if s.count(a)!=1:raise ValueError("P14P3_SOURCE_ANCHOR_"+label+"_"+str(s.count(a)))
 return s.replace(a,b,1)
def patch(pre):
 t=pre["tt.cpp"].decode();s=pre["search.cpp"].decode()
 t=once(t,TT_ANCHOR,CPP+"\n"+TT_ANCHOR,"native_original_tt")
 s=once(s,FWD_ANCHOR,FWD_ANCHOR+FWD_ADD,"original_search_forward")
 s=once(s,Q_ORIG,Q_GUARD,"original_qscore_bound_return_guard")
 v={"tt.cpp":t.encode(),"search.cpp":s.encode()}
 if undo(v)!=pre:raise ValueError("P14P3_NATIVE_REVERSAL_FAIL")
 return v
def undo(post):
 t=once(post["tt.cpp"].decode(),CPP+"\n"+TT_ANCHOR,TT_ANCHOR,"inverse_cpp")
 s=once(post["search.cpp"].decode(),Q_GUARD,Q_ORIG,"inverse_q")
 s=once(s,FWD_ANCHOR+FWD_ADD,FWD_ANCHOR,"inverse_forward")
 return {"tt.cpp":t.encode(),"search.cpp":s.encode()}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",required=True);ap.add_argument("--out-manifest",required=True)
 x=ap.parse_args();d=Path(x.root)/"src";raw={n:(d/n).read_bytes() for n in SHA}
 for n,digest in SHA.items():
  if hashlib.sha256(raw[n]).hexdigest()!=digest:raise ValueError("UNPINNED_ORIGINAL_SF16_"+n)
 b8,_=p8(raw);b11=p11(b8);b12=p12(b11);b13=r4(b12);b14=p0(b13)
 b9={"tt.cpp":b14["tt.cpp"],"search.cpp":p9(b14["search.cpp"].decode()).encode()}
 b2=p2(b9);b3=patch(b2)
 back=undo(b3)
 if back!=b2:raise ValueError("P14P3_REVERSE_FAILED")
 back=u2(back)
 back={"tt.cpp":back["tt.cpp"],"search.cpp":u9(back["search.cpp"].decode()).encode()}
 if u8(u11(u12(ur4(u0(back)))))!=raw:raise ValueError("NINE_LAYER_ORIGINAL_BYTE_NOT_RESTORED")
 for n,v in b3.items():(d/n).write_bytes(v)
 manifest={
  "schema":"c3x025-P14-P3-original-native-qscore-context-guard-policy-overlay-v1",
  "upstream_SF16_SHA256":SHA,
  "full_nine_layer_exact_inverse_original":True,
  "original_see_flags_mutated":False,"moves_generated_or_mutated":False,
  "guard":"single original qsearch TT bounded score return candidate: 2<=ply<=6, !incheck, rule50<80, abs(ttScore),abs(beta)<1000, abs(ttScore-beta)<=64; first eligible in a process only",
  "guard_suffices_for_root_choice_invariance":False,
  "guard_suffices_for_chess_semantics_or_tactical_correctness":False,
  "guard_is_narrow_diagnostic_not_proven_safe_optimization":True,
  "modified_sha256":{n:hashlib.sha256(v).hexdigest() for n,v in b3.items()}
 }
 out=Path(x.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
 print("C3X025_P14P3_NATIVE_NINE_LAYER_EXACT_REVERSAL",json.dumps(manifest),flush=True)
if __name__=="__main__":main()
