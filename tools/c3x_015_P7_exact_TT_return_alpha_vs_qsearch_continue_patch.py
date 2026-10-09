#!/usr/bin/env python3
"""P7 Source-native matched TT return VALUE vs actual search continuation.
Apply AFTER exact P6S1 Stockfish16 patches. Fails closed on anchor drift.
"""
import argparse,hashlib,json
from pathlib import Path

def only(s,old,new,name):
 n=s.count(old)
 if n!=1:raise RuntimeError("P7_ANCHOR_"+name+"_COUNT_"+str(n))
 return s.replace(old,new,1)

def patch(path):
 root=Path(path)/"src"
 names=["c3x014_pin_trace.h","position.cpp","search.cpp"]
 files={n:root/n for n in names}
 raw={n:p.read_bytes() for n,p in files.items()}
 h,p,s=(raw[n].decode() for n in names)
 h=only(h,"std::string c3x015_p6s1_target_intervention_summary();",
   "std::string c3x015_p6s1_target_intervention_summary();\nint c3x015_p7_return_score(int value,int alpha,int beta);\nstd::string c3x015_p7_return_score_summary();",
   "HEADER")
 p=only(p,"static thread_local C3X015P6S1 c3x015_p6s1;",
r"""static thread_local C3X015P6S1 c3x015_p6s1;
struct C3X015P7Score {
 int mode=0, current_matched=0,delivery_count=0,numeric_difference_count=0;
 int original_value=0,delivered_value=0,alpha=0,beta=0;
};
static thread_local C3X015P7Score c3x015_p7;
int c3x015_p7_return_score(int value,int alpha,int beta) {
 if(c3x015_p7.mode!=1 || !c3x015_p7.current_matched || c3x015_p7.delivery_count>0)
    return value;
 c3x015_p7.delivery_count++;
 c3x015_p7.original_value=value;
 c3x015_p7.delivered_value=alpha;
 c3x015_p7.alpha=alpha;c3x015_p7.beta=beta;
 if(value!=alpha)c3x015_p7.numeric_difference_count++;
 return alpha;
}
std::string c3x015_p7_return_score_summary() {
 std::ostringstream o;
 o<<"mode="<<c3x015_p7.mode<<" matched_score_deliveries="<<c3x015_p7.delivery_count
  <<" numeric_changes="<<c3x015_p7.numeric_difference_count
  <<" old_value="<<c3x015_p7.original_value
  <<" delivered_value="<<c3x015_p7.delivered_value
  <<" alpha="<<c3x015_p7.alpha<<" beta="<<c3x015_p7.beta;
 return o.str();
}""","STATE")
 p=only(p," c3x015_p6s1=C3X015P6S1{};",
r""" c3x015_p6s1=C3X015P6S1{};
 c3x015_p7=C3X015P7Score{};
 const char* p7mode=std::getenv("C3X015_P7_SCORE_MODE");
 if(!p7mode)std::abort();
 if(std::strcmp(p7mode,"IDENTITY")==0)c3x015_p7.mode=0;
 else if(std::strcmp(p7mode,"RETURN_ALPHA")==0)c3x015_p7.mode=1;
 else std::abort();""","RESET")
 p=only(p," if(!c3x015_p6s1.target_valid || !c3x015_win.first_seen)return true;",
 """ c3x015_p7.current_matched=0;
 if(!c3x015_p6s1.target_valid || !c3x015_win.first_seen)return true;""","MATCH_RESET")
 p=only(p," ++c3x015_p6s1.exact_hits;",
 """ ++c3x015_p6s1.exact_hits;
 c3x015_p7.current_matched=1;""","MATCH_ARM")
 e='c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),1);'
 changes=0
 for spaces in (16,12):
  needle=e+'\n'+(' '*spaces)+'return ttValue;'
  target=e+'\n'+(' '*spaces)+'return Value(c3x015_p7_return_score(int(ttValue),int(alpha),int(beta)));'
  count=s.count(needle)
  if count==1:
   s=s.replace(needle,target,1);changes+=1
 if changes!=2:raise RuntimeError("P7_EXACT_MAIN_QSEARCH_RETURN_COUNT_"+str(changes))
 s=only(s,'  sync_cout << "info string c3x015_p6s1_target_intervention " << c3x015_p6s1_target_intervention_summary() << sync_endl;',
  '  sync_cout << "info string c3x015_p6s1_target_intervention " << c3x015_p6s1_target_intervention_summary() << sync_endl;\n  sync_cout << "info string c3x015_p7_return_score " << c3x015_p7_return_score_summary() << sync_endl;',
  "UCI_TRACE")
 for n,body in zip(names,(h,p,s)):files[n].write_text(body)
 return {"schema":"c3x015-p7-single-presealed-TT-return-score-or-continuation-v1",
 "source_before_sha":{n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
 "source_after_sha":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
 "modes":["IDENTITY","RETURN_ALPHA"],"source_sites_changed":2,
 "fail_closed_bound":"At most one RETURN_ALPHA is delivered, only when P6 exact physical full64 writer/reader match has occurred",
 "limitations":["TT alpha return changes reported fail-low score; no claim of natural TT indirect effect","NO_ORIGINAL_PGN_REHOST"]}

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",required=True)
 ap.add_argument("--out-manifest",required=True)
 args=ap.parse_args()
 result=patch(args.source)
 dest=Path(args.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2)+"\n")
 print("C3X015_P7_PRESEALED_EXACT_TT_RETURN_SCORE_PATCH_PASS")
