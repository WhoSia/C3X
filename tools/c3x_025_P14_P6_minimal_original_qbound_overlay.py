#!/usr/bin/env python3
"""P14-P6 original-SF16 minimal source patch; C++ does all chess operations.
Reuses previous proven reversible P14-P4 original root observer without stacking
full historical TT instrumentation. Exact return-site reversal is required.
"""
import argparse,json
from pathlib import Path
from c3x_025_P14_P4_original_root_window_observer import patch as p4,undo as undo4,NEWQ,SCOPE
CALL="c3x025_p14p4_skip_one(int(ss->ply),int(ttValue),int(beta),int(pos.rule50_count()))"
ARG="c3x025_p14p6_skip(int(ss->ply),int(ttValue),int(beta),int(pos.rule50_count()),int(tte->bound()),int(tte->depth()),int(ttDepth),int(ss->ttHit),int(PvNode),int(ss->inCheck))"
P6_CPP=r"""
// The original Stockfish qsearch predicate is unchanged. Once its conjunction
// has passed, these fields certify a branch decision, NOT a semantic minimax
// value. Never infer a root winner gap from this certificate.
static thread_local bool c3x025_p14p6_mutated=false;
static thread_local int c3x025_p14p6_seen=0;
bool c3x025_p14p6_skip(int ply,int value,int beta,int rule50,int bound,
                       int storedDepth,int requiredDepth,int ttHit,int pv,int inCheck) {
    const char* e=std::getenv("C3X025_P14P6_POLICY");
    const bool sham=!e || std::strcmp(e,"SHAM")==0;
    const bool first=e&&std::strcmp(e,"FIRST")==0;
    const bool lower=e&&std::strcmp(e,"LOWER")==0;
    const bool upper=e&&std::strcmp(e,"UPPER")==0;
    if(!(sham||first||lower||upper))std::abort();
    const bool lowerSide=value>=beta;
    if(pv||!ttHit||storedDepth<requiredDepth||
       !(bound & (lowerSide ? BOUND_LOWER : BOUND_UPPER)))std::abort();
    const bool change=!sham&&!c3x025_p14p6_mutated
                   &&(first||(lower&&lowerSide)||(upper&&!lowerSide));
    if(std::getenv("C3X025_P14P4_TRACE") && (c3x025_p14p6_seen<2||change))
        sync_cout << "info string c3x025_p14p6 kind="
         <<(change?"ACTUATED":"CONTACT")
         <<" policy="<<(sham?"SHAM":first?"FIRST":lower?"LOWER":"UPPER")
         <<" side="<<(lowerSide?"LOWER":"UPPER")
         <<" score="<<value<<" beta="<<beta<<" bound="<<bound
         <<" stored_depth="<<storedDepth<<" required_depth="<<requiredDepth
         <<" ply="<<ply<<" rule50="<<rule50<<" check="<<inCheck
         <<" mutated="<<int(change)<<sync_endl;
    c3x025_p14p6_seen++;
    if(change)c3x025_p14p6_mutated=true;
    return change;
}
"""
Q6=NEWQ.replace(CALL,ARG)
def once(s,a,b,name):
 if s.count(a)!=1:raise ValueError("SOURCE_SITE_MISSING_OR_DUPLICATE_"+name+"_"+str(s.count(a)))
 return s.replace(a,b,1)
def patch(original):
 b=p4(original).decode()
 b=once(b,SCOPE,SCOPE+P6_CPP+"\n","cpp")
 b=once(b,NEWQ,Q6,"original_qsearch_cutoff")
 ans=b.encode()
 if undo(ans)!=original:raise ValueError("NATIVE_EXACT_REVERSAL_FAIL")
 return ans
def undo(data):
 s=data.decode()
 s=once(s,Q6,NEWQ,"undo_q")
 s=once(s,SCOPE+P6_CPP+"\n",SCOPE,"undo_cpp")
 return undo4(s.encode())
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",required=True);ap.add_argument("--out",required=True)
 args=ap.parse_args();p=Path(args.root)/"src/search.cpp"
 raw=p.read_bytes()
 from hashlib import sha256
 if sha256(raw).hexdigest()!="21b79baa7ce9dabec5b3b9e3854bed9869a1935277247832e550cf395bccd644":
  raise ValueError("NOT_OFFICIAL_PINNED_ORIGINAL_SF16_SOURCE")
 modified=patch(raw);p.write_bytes(modified)
 Path(args.out).write_text(json.dumps({
 "schema":"c3x025-P14-P6-original-qsearch-bound-class-policy-source-local-v1",
 "original_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
 "patch_reverses_exact_original":True,
 "source_predicate":"non-PV and TT.depth>=ttDepth and converted TT value valid and original TT bound confirms value>=beta(lower) or value<beta(upper)",
 "interventions":["SHAM","FIRST","LOWER","UPPER"],
 "each_policy_mutates_at_most_one_executed_original_TT_numeric_qsearch_return":True,
 "true_minimax_interval_from_TT_fields_proved":False,
 "original_root_challenger_gap_proved":False,
 "no_SEE_move_legality_or_root_move_generation_changes":True
 },indent=2)+"\n")
 print("C3X025_P14P6_ORIGINAL_SOURCE_EXACT_REVERSAL_PASS")
if __name__=="__main__":main()
