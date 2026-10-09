#!/usr/bin/env python3
"""P9-A2 targeted first-child return threshold intervention for RISR #29 only.
Apply AFTER the full P9-A1 patch; restore baselines via original unmodified P8/P9-A1 outputs.
"""
import argparse,hashlib,json
from pathlib import Path
def only(s,a,b,code):
 n=s.count(a)
 if n!=1:raise RuntimeError("P9_A2_ANCHOR_"+code+"_COUNT_"+str(n))
 return s.replace(a,b,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True);a=ap.parse_args()
 root=Path(a.source)/"src";files={n:root/n for n in ("c3x014_pin_trace.h","position.cpp","search.cpp")}
 original={n:p.read_bytes() for n,p in files.items()}
 h,p,s=(original[n].decode() for n in files)
 h=only(h,"std::string c3x015_p9_treatment_summary();",r"""std::string c3x015_p9_treatment_summary();
int c3x015_p9_a2_child_threshold(Key k,int ply,int alpha,int beta,int value,int move);
std::string c3x015_p9_a2_summary();""","HEADER")
 p=only(p,"static thread_local C3X015P9A1 c3x015_p9;",r"""static thread_local C3X015P9A1 c3x015_p9;
struct C3X015P9A2 {
 int requested=0,caseid=0,contacts=0,numeric_changes=0,
    original_score=0,substituted_score=0,source_ply=0,source_move=0;
};
static thread_local C3X015P9A2 c3x015_a2;
bool c3x015_p9_at_target(Key,int); // defined in the preceding P9-A1 source patch
int c3x015_p9_a2_child_threshold(Key key,int ply,int a,int b,int val,int move) {
 if(!c3x015_p9_at_target(key,ply))return val;
 if(c3x015_a2.caseid!=29 || c3x015_a2.contacts!=0 || val!=-59
    || move!=729 || a!=130 || b!=131)return val;
 c3x015_a2.contacts++;
 c3x015_a2.original_score=val;
 c3x015_a2.substituted_score=c3x015_a2.requested;
 c3x015_a2.source_ply=ply;c3x015_a2.source_move=move;
 c3x015_a2.numeric_changes+=int(val!=c3x015_a2.requested);
 return c3x015_a2.requested;
}
std::string c3x015_p9_a2_summary(){
 std::ostringstream o;
 o<<"requested="<<c3x015_a2.requested<<" caseid="<<c3x015_a2.caseid
  <<" contacts="<<c3x015_a2.contacts
  <<" changes="<<c3x015_a2.numeric_changes
  <<" first_original="<<c3x015_a2.original_score
  <<" substituted="<<c3x015_a2.substituted_score
  <<" ply="<<c3x015_a2.source_ply
  <<" move="<<c3x015_a2.source_move;
 return o.str();
}""","STATE")
 p=only(p," c3x015_p9=C3X015P9A1{};",r""" c3x015_p9=C3X015P9A1{};
 c3x015_a2=C3X015P9A2{};
 const char*a2val=std::getenv("C3X015_P9_A2_CHILD_VALUE");
 const char*a2case=std::getenv("C3X015_P9_A2_CASE");
 if(!a2val || !a2case)std::abort();
 c3x015_a2.requested=std::atoi(a2val);
 c3x015_a2.caseid=std::atoi(a2case);
 if(c3x015_a2.requested!=129 && c3x015_a2.requested!=130
    && c3x015_a2.requested!=131)std::abort();
 if(c3x015_a2.caseid!=2 && c3x015_a2.caseid!=29)std::abort();""","RESET")
 anchor="  // qsearch() is the quiescence search function, which is called by the main search"
 if s.count(anchor)!=1:raise RuntimeError("P9_A2_QSEARCH_BOUNDS")
 head,tail0=s.split(anchor,1)
 stop="  // value_to_tt() adjusts a mate or TB score"
 if tail0.count(stop)!=1:raise RuntimeError("P9_A2_QSEARCH_STOP_CHANGED")
 q,rest=tail0.split(stop,1)
 q=only(q,"        c3x015_p8_qevent(posKey,int(ss->ply),7,int(alpha),int(beta),int(value),int(move));",
 r"""        c3x015_p8_qevent(posKey,int(ss->ply),7,int(alpha),int(beta),int(value),int(move));
        value = Value(c3x015_p9_a2_child_threshold(posKey,int(ss->ply),int(alpha),int(beta),int(value),int(move)));""","FIRST_CHILD_SOURCE_VALUE")
 s=head+anchor+q+stop+rest
 s=only(s,'  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;',
 '  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;\n  sync_cout << "info string c3x015_p9_a2_threshold " << c3x015_p9_a2_summary() << sync_endl;',
 "UCI")
 for n,v in zip(files,(h,p,s)):files[n].write_text(v)
 receipt={"schema":"c3x015-P9-A2-RISR-first-qchild-alpha-beta-boundary-source-patch",
 "values":[129,130,131],"target_world":29,"exact_child_old_value":-59,"exact_source_move":729,
 "reader_alpha":130,"reader_beta":131,"negative_no_contact_world":2,
 "original_sha":{n:hashlib.sha256(b).hexdigest() for n,b in original.items()},
 "patched_sha":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in files},
 "scientific_ceiling":"Artificial one-time child-value perturbation on two P6 outcome-disclosed chess worlds; not correct-chess oracle or prospective transfer."}
 out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(receipt,indent=2)+"\n")
 print("C3X015_P9_A2_FIRST_QCHILD_BOUNDARY_SOURCE_PATCH_PASS")
if __name__=="__main__":main()
