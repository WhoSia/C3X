#!/usr/bin/env python3
"""P9-A1 five-way source-native mediator-factorization at original P8/Stockfish16 source.
Applies AFTER the P8 observer patch; I/V/B must retain P8 UCI; G/W/L are one-event source treatments.
Never reselect P6S0 pre-frozen physical TT edge; fail closed on patch anchors.
"""
import argparse, hashlib, json
from pathlib import Path
def only(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError("P9_A1_ANCHOR_"+label+"_EXPECTED_1_GOT_"+str(n))
 return s.replace(old,new,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
 a=ap.parse_args();root=Path(a.source)/"src"
 names=["c3x014_pin_trace.h","position.cpp","search.cpp"]
 files={n:root/n for n in names};old={n:p.read_bytes() for n,p in files.items()}
 h,p,s=(old[n].decode() for n in names)
 h=only(h,"std::string c3x015_p8_events_summary();",r"""std::string c3x015_p8_events_summary();
bool c3x015_p9_allow_beta_break(Key key,int ply,int alpha,int beta,int value,int move,bool inCheck);
bool c3x015_p9_allow_qsearch_TT_write(Key key,int ply,int value);
int c3x015_p9_override_qsearch_return(Key key,int ply,int value);
std::string c3x015_p9_treatment_summary();""","DECL")
 p=only(p,"static thread_local C3X015P8Events c3x015_p8;",r"""static thread_local C3X015P8Events c3x015_p8;
// 0 sham; 1 exact beta break; 2 exact qsearch TT save; 3 exact local return value.
// The root position and target edge have already been pre-frozen in P6S0/P8.
struct C3X015P9A1 {
 int mode=0,break_gates=0,save_gates=0,relay_gates=0;
 int source_events=0,caseid=0,old_value=0,new_value=0,change_count=0;
};
static thread_local C3X015P9A1 c3x015_p9;
bool c3x015_p9_at_target(Key k,int ply) {
 return c3x015_p8.armed && c3x015_p8.target_key==k && c3x015_p8.target_ply==ply;
}
bool c3x015_p9_allow_beta_break(Key k,int ply,int a,int b,int value,int move,bool inCheck) {
 if(!c3x015_p9_at_target(k,ply))return true;
 ++c3x015_p9.source_events;
 if(c3x015_p9.mode==1 && !c3x015_p9.break_gates &&
    c3x015_p9.caseid==2 && inCheck && a==130 && b==131 &&
    value==173 && move==391) {
   ++c3x015_p9.break_gates;
   return false;
 }
 return true;
}
bool c3x015_p9_allow_qsearch_TT_write(Key k,int ply,int value){
 if(!c3x015_p9_at_target(k,ply))return true;
 ++c3x015_p9.source_events;
 if(c3x015_p9.mode==2 && !c3x015_p9.save_gates &&
    ((c3x015_p9.caseid==2 && value==173) ||
     (c3x015_p9.caseid==29 && value==29))) {
    ++c3x015_p9.save_gates;
    return false;
 }
 return true;
}
int c3x015_p9_override_qsearch_return(Key k,int ply,int value){
 if(!c3x015_p9_at_target(k,ply))return value;
 ++c3x015_p9.source_events;
 if(c3x015_p9.mode==3 && !c3x015_p9.relay_gates &&
    ((c3x015_p9.caseid==2 && value==173) ||
     (c3x015_p9.caseid==29 && value==29))) {
    ++c3x015_p9.relay_gates;
    c3x015_p9.old_value=value;
    c3x015_p9.new_value=(c3x015_p9.caseid==2 ? 14 : 29);
    c3x015_p9.change_count+=int(c3x015_p9.new_value != value);
    return c3x015_p9.new_value;
 }
 return value;
}
std::string c3x015_p9_treatment_summary(){
 std::ostringstream o;
 o<<"mode="<<c3x015_p9.mode<<" caseid="<<c3x015_p9.caseid
  <<" events="<<c3x015_p9.source_events
  <<" suppressed_beta_break="<<c3x015_p9.break_gates
  <<" suppressed_TT_write="<<c3x015_p9.save_gates
  <<" clamped_local_return="<<c3x015_p9.relay_gates
  <<" changed_return_value="<<c3x015_p9.change_count
  <<" original_qreturn="<<c3x015_p9.old_value
  <<" new_qreturn="<<c3x015_p9.new_value;
 return o.str();
}""","STATE")
 p=only(p," c3x015_p8=C3X015P8Events{};",r""" c3x015_p8=C3X015P8Events{};
 c3x015_p9=C3X015P9A1{};
 const char*p9mode=std::getenv("C3X015_P9_A1_MODE");
 const char*p9case=std::getenv("C3X015_P9_A1_CASE");
 if(!p9mode || !p9case)std::abort();
 c3x015_p9.caseid=std::atoi(p9case);
 if(std::strcmp(p9mode,"SHAM")==0)c3x015_p9.mode=0;
 else if(std::strcmp(p9mode,"G_BREAK")==0)c3x015_p9.mode=1;
 else if(std::strcmp(p9mode,"W_SAVE")==0)c3x015_p9.mode=2;
 else if(std::strcmp(p9mode,"L_CLAMP")==0)c3x015_p9.mode=3;
 else std::abort();
 if(c3x015_p9.caseid!=2 && c3x015_p9.caseid!=29)std::abort();""","ROOT_INIT")
 anchor="  // qsearch() is the quiescence search function, which is called by the main search"
 if s.count(anchor)!=1:raise RuntimeError("P9_QSEARCH_BOUNDARY_CHANGED")
 head,rest=s.split(anchor,1)
 end="  // value_to_tt() adjusts a mate or TB score"
 if rest.count(end)!=1:raise RuntimeError("P9_QSEARCH_END_CHANGED")
 q,tail=rest.split(end,1)
 q=only(q,"                    break; // Fail high",
 r"""                    if (c3x015_p9_allow_beta_break(posKey,int(ss->ply),int(alpha),int(beta),int(value),int(move),bool(ss->inCheck)))
                        break; // Fail high. In G case alone, suppress this exact one break.""","BETA_BREAK")
 # Guard one exact qsearch terminal TT write; keep stand-pat early TT write intact.
 q=only(q,"    // Save gathered info in transposition table\n    c3x015_tt_labeled_save(",
 r"""    // Save gathered info in transposition table
    if (c3x015_p9_allow_qsearch_TT_write(posKey,int(ss->ply),int(bestValue)))
    c3x015_tt_labeled_save(""","TT_WRITE")
 # P4 wrapper qsearch final call ends with ss->staticEval); and a trailing assert.
 q=only(q,"              ttDepth, bestMove, ss->staticEval);",
             "              ttDepth, bestMove, ss->staticEval);","TT_WRITE_END_IDENTITY")
 # Explicit return-value intervention after complete qsearch (do not modify stored TT value).
 q=only(q,"    c3x015_p8_qevent(posKey,int(ss->ply),11,int(alpha),int(beta),int(bestValue),int(bestMove));\n    return bestValue;",
 r"""    c3x015_p8_qevent(posKey,int(ss->ply),11,int(alpha),int(beta),int(bestValue),int(bestMove));
    return Value(c3x015_p9_override_qsearch_return(posKey,int(ss->ply),int(bestValue)));""","QRETURN")
 s=head+anchor+q+end+tail
 s=only(s,'  sync_cout << "info string c3x015_p8_qsearch_trace " << c3x015_p8_events_summary() << sync_endl;',
 '  sync_cout << "info string c3x015_p8_qsearch_trace " << c3x015_p8_events_summary() << sync_endl;\n  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;',"UCI")
 for name,text in zip(names,(h,p,s)):files[name].write_text(text)
 manifest={"schema":"c3x015-P9-A1-post-P8-event-specific-source-patch-v1",
 "modes":["SHAM","G_BREAK","W_SAVE","L_CLAMP"],
 "original_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in old.items()},
 "patched_sha256":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
 "test_scope":"TWO_OUTCOME_EXPOSED_WORLDS_POST_P6_DISCLOSURE",
 "limits":["Beta break gate applies only to world2 after exact match with child value173 in check.","TT save gating and local qreturn clamping at most once at original target fullkey/ply.","All original P7/P8 I/V/B UCI core results and exposure counters must remain exact.","Manipulated computation is not chess move legality or perfect game theoretic correctness."]}
 out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(manifest,indent=2)+"\n")
 print("C3X015_P9_A1_NATIVE_SINGLE_EVENT_BETA_WRITE_RELAY_SOURCE_PATCH_PASS")
if __name__=="__main__":main()
