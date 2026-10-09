#!/usr/bin/env python3
"""C3X P9-A2 exact first child qsearch return boundary intervention.
Apply AFTER P9-A1 patch on upstream SF16. Does not affect legal move generation.
"""
import argparse,hashlib,json
from pathlib import Path
def only(s,a,b,name):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"P9A2_SOURCE_{name}_FOUND_{n}_EXPECTED_1")
 return s.replace(a,b,1)
def patch(root):
 base=Path(root)/"src"
 names=["c3x014_pin_trace.h","position.cpp","search.cpp"]
 f={n:base/n for n in names};original={n:p.read_bytes() for n,p in f.items()}
 h,c,s=[original[n].decode() for n in names]
 h=only(h,"std::string c3x015_p9_treatment_summary();",
        "std::string c3x015_p9_treatment_summary();\nint c3x015_p9_a2_child_score(int score,Key key,int ply,int alpha,int beta,int move);\nstd::string c3x015_p9_a2_summary();","HEADER")
 c=only(c,"static thread_local C3X015P9A1 c3x015_p9;",
r"""static thread_local C3X015P9A1 c3x015_p9;
struct C3X015P9A2 {
 int demanded_score=0,caseid=0,matched=0,delivered=0;
 int original_value=0,returned_value=0,matching_move=0;
};
static thread_local C3X015P9A2 c3x015_p9_a2;
bool c3x015_p9_at_target(Key,int); // defined in the P9-A1 layer below
int c3x015_p9_a2_child_score(int score,Key key,int ply,int alpha,int beta,int move){
 if(!c3x015_p9_at_target(key,ply))return score;
 if(c3x015_p9_a2.caseid!=29 || alpha!=130 || beta!=131 ||
    move!=729 || score!=-59)return score;
 ++c3x015_p9_a2.matched;
 if(c3x015_p9_a2.delivered)return score;
 ++c3x015_p9_a2.delivered;
 c3x015_p9_a2.original_value=score;
 c3x015_p9_a2.returned_value=c3x015_p9_a2.demanded_score;
 c3x015_p9_a2.matching_move=move;
 return c3x015_p9_a2.demanded_score;
}
std::string c3x015_p9_a2_summary(){
 std::ostringstream o;
 o<<"caseid="<<c3x015_p9_a2.caseid
  <<" targetscore="<<c3x015_p9_a2.demanded_score
  <<" matched="<<c3x015_p9_a2.matched
  <<" delivered="<<c3x015_p9_a2.delivered
  <<" previous_score="<<c3x015_p9_a2.original_value
  <<" substituted_score="<<c3x015_p9_a2.returned_value
  <<" native_move="<<c3x015_p9_a2.matching_move;
 return o.str();
}""","STATE")
 c=only(c," c3x015_p9=C3X015P9A1{};",
r""" c3x015_p9=C3X015P9A1{};
 c3x015_p9_a2=C3X015P9A2{};
 const char *p9A2Score=std::getenv("C3X015_P9_A2_CHILD_VALUE");
 if(!p9A2Score)std::abort();
 c3x015_p9_a2.demanded_score=std::atoi(p9A2Score);
 if(c3x015_p9_a2.demanded_score!=129 &&
    c3x015_p9_a2.demanded_score!=130 &&
    c3x015_p9_a2.demanded_score!=131)std::abort();
 c3x015_p9_a2.caseid=std::atoi(std::getenv("C3X015_P9_A1_CASE"));""","ROOT_RESET")
 anchor="  // qsearch() is the quiescence search function, which is called by the main search"
 first,rest=s.split(anchor,1)
 marker="  // value_to_tt() adjusts a mate or TB score"
 q,tail=rest.split(marker,1)
 q=only(q,
 "        pos.undo_move(move);\n        c3x015_p8_qevent(posKey,int(ss->ply),7,int(alpha),int(beta),int(value),int(move));",
 """        pos.undo_move(move);
        value = Value(c3x015_p9_a2_child_score(int(value),posKey,int(ss->ply),int(alpha),int(beta),int(move)));
        c3x015_p8_qevent(posKey,int(ss->ply),7,int(alpha),int(beta),int(value),int(move));""","Q_CHILD_RETURN")
 s=first+anchor+q+marker+tail
 s=only(s,'  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;',
       '  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;\n  sync_cout << "info string c3x015_p9_a2_child_boundary " << c3x015_p9_a2_summary() << sync_endl;',
       "UCI")
 for n,value in zip(names,(h,c,s)):f[n].write_text(value)
 return {"schema":"c3x015-P9-A2-first-qsearch-child-boundary-exact-source-v1",
 "upstream_source":"SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52 plus P8 and P9-A1 patches",
 "before":{n:hashlib.sha256(b).hexdigest() for n,b in original.items()},
 "after":{n:hashlib.sha256(f[n].read_bytes()).hexdigest() for n in names},
 "mode":"P9-A1 SHAM+B with exact first child return substitution at world29 and no-hit world2",
 "world29_target":{"original_child_value":-59,"native_move":729,"reader_alpha":130,"reader_beta":131,"candidate_scores":[129,130,131]},
 "limits":["Source artificial boundary scores not chess evaluation truth","P9-A2 world2 is mandatory no-contact control","Two prior P6-outcome-selected worlds; not prospective transfer"]}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
 j=patch(a.source);dst=Path(a.out_manifest);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(j,indent=2)+"\n")
 print("C3X015_P9_A2_EXACT_QSEARCH_FIRST_CHILD_VALUE_BOUNDARY_SOURCE_PATCH_PASS")
