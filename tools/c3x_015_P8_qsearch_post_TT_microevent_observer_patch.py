#!/usr/bin/env python3
"""Add passive post-TT-source qsearch micro-event provenance observer to P7 SF16."""
import argparse,hashlib,json
from pathlib import Path
def sub(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError("P8_SOURCE_ANCHOR_"+label+"_EXPECTED1_ACTUAL"+str(n))
 return s.replace(a,b,1)
def patch(dir):
 p=Path(dir)/"src"; names=["c3x014_pin_trace.h","position.cpp","search.cpp"]
 files={n:p/n for n in names}; originals={n:f.read_bytes() for n,f in files.items()}
 h,c,s=(originals[n].decode() for n in names)
 h=sub(h,"std::string c3x015_p7_return_score_summary();",
 """std::string c3x015_p7_return_score_summary();
void c3x015_p8_mark_exact_TT(Key,int,int,int,int);
void c3x015_p8_qevent(Key,int,int,int,int,int,int);
std::string c3x015_p8_events_summary();""","P8_HEADER")
 c=sub(c,"static thread_local C3X015P7Score c3x015_p7;",
 r"""static thread_local C3X015P7Score c3x015_p7;
// Bounded, passive and position-key/ply tagged. Not a whole-stack counterfactual proof.
struct C3X015P8Events {
 bool armed=false;
 Key target_key=0;
 int target_ply=-1,source_mark_count=0;
 std::uint64_t observed=0, recorded=0, overflow=0;
 std::vector<std::string> lines;
};
static thread_local C3X015P8Events c3x015_p8;
void c3x015_p8_qevent(Key k,int ply,int tag,int alpha,int beta,int value,int move){
 if(!c3x015_p8.armed)return;
 ++c3x015_p8.observed;
 if(c3x015_p8.lines.size()>=1024){++c3x015_p8.overflow;return;}
 std::ostringstream o;
 o<<std::hex<<std::uint64_t(k)<<std::dec<<":"<<ply<<":"<<tag
  <<":"<<alpha<<":"<<beta<<":"<<value<<":"<<move;
 c3x015_p8.lines.push_back(o.str());
 ++c3x015_p8.recorded;
}
void c3x015_p8_mark_exact_TT(Key k,int ply,int alpha,int beta,int value){
 ++c3x015_p8.source_mark_count;
 if(!c3x015_p8.armed){
  c3x015_p8.armed=true;
  c3x015_p8.target_key=k;c3x015_p8.target_ply=ply;
 }
 c3x015_p8_qevent(k,ply,1,alpha,beta,value,0);
}
std::string c3x015_p8_events_summary(){
 std::ostringstream o;
 o<<"marks="<<c3x015_p8.source_mark_count
  <<" target_key="<<std::uint64_t(c3x015_p8.target_key)
  <<" target_ply="<<c3x015_p8.target_ply
  <<" seen="<<c3x015_p8.observed<<" listed="<<c3x015_p8.recorded
  <<" truncated="<<c3x015_p8.overflow<<" stream=";
 for(const auto&e:c3x015_p8.lines)o<<e<<"|";
 return o.str();
}""","P8_STATE")
 c=sub(c," c3x015_p7=C3X015P7Score{};",
 " c3x015_p7=C3X015P7Score{};\n c3x015_p8=C3X015P8Events{};","P8_RESET")
 c=sub(c," c3x015_p7.current_matched=1;",
 " c3x015_p7.current_matched=1;\n c3x015_p8_mark_exact_TT(key,ply,a,b,value);","P8_FIRST_EXACT_MATCH")
 anchor="  // qsearch() is the quiescence search function, which is called by the main search"
 if s.count(anchor)!=1:raise RuntimeError("P8_QSEARCH_BOUNDARY_NOT_UNIQUE")
 head,body=s.split(anchor,1)
 end="  // value_to_tt() adjusts a mate or TB score"
 if body.count(end)!=1:raise RuntimeError("P8_QSEARCH_END_NOT_UNIQUE")
 q,tail=body.split(end,1)
 q=sub(q,"    // Step 1. Initialize node\n    if (PvNode)",
         "    c3x015_p8_qevent(pos.key(),int(ss->ply),2,int(alpha),int(beta),int(depth),0);\n    // Step 1. Initialize node\n    if (PvNode)","Q_ENTER")
 q=sub(q,"    // Step 4. Static evaluation of the position\n    if (ss->inCheck)",
        "    c3x015_p8_qevent(posKey,int(ss->ply),3,int(alpha),int(beta),int(ttValue),0);\n    // Step 4. Static evaluation of the position\n    if (ss->inCheck)","POST_TT_CONTINUATION")
 q=sub(q,"        futilityBase = bestValue + 200;",
        "        c3x015_p8_qevent(posKey,int(ss->ply),4,int(alpha),int(beta),int(bestValue),0);\n        futilityBase = bestValue + 200;","STANDPAT")
 q=sub(q,"        moveCount++;\n\n        // Step 6.",
        "        moveCount++;\n        c3x015_p8_qevent(posKey,int(ss->ply),5,int(alpha),int(beta),int(bestValue),int(move));\n\n        // Step 6.","Q_LEGAL_MOVE")
 q=sub(q,"        pos.do_move(move, st, givesCheck);\n        value = -qsearch<nodeType>",
        "        c3x015_p8_qevent(posKey,int(ss->ply),6,int(alpha),int(beta),int(bestValue),int(move));\n        pos.do_move(move, st, givesCheck);\n        value = -qsearch<nodeType>","BEFORE_Q_CHILD")
 q=sub(q,"        pos.undo_move(move);\n\n        assert(value >",
         "        pos.undo_move(move);\n        c3x015_p8_qevent(posKey,int(ss->ply),7,int(alpha),int(beta),int(value),int(move));\n\n        assert(value >","AFTER_Q_CHILD")
 q=sub(q,"                if (PvNode && value < beta) // Update alpha here!\n                    alpha = value;\n                else\n                    break; // Fail high",
         """                if (PvNode && value < beta) // Update alpha here!
                {
                    alpha = value;
                    c3x015_p8_qevent(posKey,int(ss->ply),8,int(alpha),int(beta),int(value),int(move));
                }
                else
                {
                    c3x015_p8_qevent(posKey,int(ss->ply),9,int(alpha),int(beta),int(value),int(move));
                    break; // Fail high
                }""","Q_ALPHA_OR_BETA")
 q=sub(q,"    // Save gathered info in transposition table\n",
         "    c3x015_p8_qevent(posKey,int(ss->ply),10,int(alpha),int(beta),int(bestValue),int(bestMove));\n    // Save gathered info in transposition table\n","Q_TT_SAVE")
 q=sub(q,"    return bestValue;\n  }\n\n\n",
         "    c3x015_p8_qevent(posKey,int(ss->ply),11,int(alpha),int(beta),int(bestValue),int(bestMove));\n    return bestValue;\n  }\n\n\n","Q_COMPLETE_RETURN")
 # Note: source-exact return vs bypass difference is witnessed by source MARK
 # plus (Q_CONTINUE or not) at the matching full-key same-ply target.
 s=head+anchor+q+end+tail
 s=sub(s,'  sync_cout << "info string c3x015_p7_return_score " << c3x015_p7_return_score_summary() << sync_endl;',
       '  sync_cout << "info string c3x015_p7_return_score " << c3x015_p7_return_score_summary() << sync_endl;\n  sync_cout << "info string c3x015_p8_qsearch_trace " << c3x015_p8_events_summary() << sync_endl;',
       "P8_UCI_REPORT")
 for n,data in zip(names,(h,c,s)):files[n].write_text(data)
 return {"schema":"c3x015-p8-native-SF16-post-TT-match-qsearch-observer-v1",
 "original":{n:hashlib.sha256(b).hexdigest() for n,b in originals.items()},
 "patched":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
 "event_codes":{"1":"EXACT_TT_MATCH","2":"QSEARCH_ENTER","3":"TT_BYPASS_TO_QSEARCH_STATIC_EVAL","4":"STANDPAT_VALUE","5":"LEGAL_QMOVE_CONSIDERED","6":"BEFORE_QRECURSE","7":"AFTER_QRECURSE","8":"PV_ALPHA_UPDATED","9":"FAIL_HIGH_BREAK","10":"QSEARCH_TT_SAVE","11":"QSEARCH_RETURN"},
 "bounded_events":1024,"scope":"PASSIVE_POST_SELECTED_PHYSICAL_TT_MATCH_ONLY",
 "limits":["This is a chronological source-key/ply event suffix not proof of natural mediation.","Captures and SEE-prune outcomes are not all individually tagged at this stage.","Source, legal chess and numeric TT/SEE code must remain behaviorally identical by full P7 replay."]}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
 a=ap.parse_args();d=patch(a.source);f=Path(a.out_manifest);f.parent.mkdir(parents=True,exist_ok=True)
 f.write_text(json.dumps(d,indent=2)+"\n")
 print("C3X015_P8_PASSIVE_QSEARCH_POST_EXACT_TT_MATCH_SOURCE_PATCH_PASS")
