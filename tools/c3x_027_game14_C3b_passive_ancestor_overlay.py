#!/usr/bin/env python3
"""Additional passive C3b ancestry over C3X027 game14 overlay (not old C3b).

Requires c3x_027_game14_passive_lineage_overlay.py applied first.
Matches frame pointers and native moves; never changes engine decisions.
"""
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,name):
 n=s.count(a)
 if n!=1:raise ValueError("C3X027_C3B_ANCHOR_"+name+"_"+str(n))
 return s.replace(a,b,1)

HELPER=r'''
struct C3X027_C3b {
 bool active=false;
 int top=-1, next=-1;
 long long root_call=0;
 unsigned long long ordinal=0;
 const Search::Stack* frame[MAX_PLY]={};
 Move moves[MAX_PLY]={};
 bool candidate[MAX_PLY]={},returned[MAX_PLY]={};
};
thread_local C3X027_C3b c3x027_c3b;
void c3x027_c3b_event(const char* kind,const Position& pos,int ply,
                      Move move,int value) {
 if (!c3x027_lineage_on()) return;
 if (auto* f=std::fopen(std::getenv("C3X027_GAME14_LINEAGE_LOG"),"a")) {
  std::fprintf(f,"event=%s sequence=%llu root_call=%lld ply=%d key64=%llu native_move=%d value=%d frame_id=%llu\n",
    kind,++c3x027_c3b.ordinal,(long long)c3x018_root_context_call,ply,
    (unsigned long long)std::uint64_t(pos.key()),int(move),value,\n    (unsigned long long)(ply>=0 && ply<MAX_PLY ? reinterpret_cast<std::uintptr_t>(c3x027_c3b.frame[ply]) : 0));
  std::fclose(f);
 }
}
void c3x027_c3b_arm(const Position& pos,Search::Stack* ss,Move move) {
 c3x027_c3b={};
 int p=ss->ply;
 if (p<1 || p>=MAX_PLY-3) {
  c3x027_c3b_event("ANCESTOR_DEPTH_CENSORED",pos,p,move,0);
  return;
 }
 auto& x=c3x027_c3b;
 x.active=true;x.top=p;x.next=p;x.root_call=c3x018_root_context_call;
 for(int i=0;i<=p;++i) {
  const auto* a=ss-(p-i);
  x.frame[i]=a;
  x.moves[i]=i==p?move:a->currentMove;
 }
 c3x027_c3b_event("ANCESTOR_SNAPSHOT",pos,p,move,0);
}
void c3x027_c3b_child_return(const Position& pos,Search::Stack* ss,Move move,int value) {
 auto& x=c3x027_c3b;
 if (!x.active || ss!=x.frame[x.top] || move!=x.moves[x.top]) return;
 c3x027_c3b_event("CHILD_VALUE_RETURNED",pos,x.top,move,value);
}
void c3x027_c3b_candidate(const Position& pos,Search::Stack* ss,Move move,int value) {
 auto& x=c3x027_c3b;
 if (!x.active || x.next<0 || c3x018_root_context_call!=x.root_call) return;
 int p=x.next;
 if (ss!=x.frame[p]) return;
 if (move!=x.moves[p] || (p<x.top && !x.returned[p+1]) || x.candidate[p]) {
  c3x027_c3b_event("ANCESTOR_EDGE_AMBIGUOUS",pos,p,move,value);
  x.active=false;return;
 }
 x.candidate[p]=true;x.next=p-1;
 c3x027_c3b_event("PARENT_CANDIDATE_VALUE",pos,p,move,value);
}
void c3x027_c3b_frame_return(const Position& pos,Search::Stack* ss,int value) {
 auto& x=c3x027_c3b;
 int p=ss->ply;
 if (!x.active || p<0 || p>x.top || ss!=x.frame[p] ||
     !x.candidate[p] || x.returned[p]) return;
 x.returned[p]=true;
 c3x027_c3b_event(p==0?"ROOT_FRAME_RETURN":"FRAME_RETURN",
                   pos,p,x.moves[p],value);
 if (p==0)x.active=false;
}
'''
def patch(s):
 s=once(s,"void c3x027_lineage_arm(const Position& pos,Search::Stack* ss,Move move) {",
        HELPER+"\nvoid c3x027_lineage_arm(const Position& pos,Search::Stack* ss,Move move) {","HELPERS")
 s=once(s,'c3x027_lineage_emit("GUARD_REENABLED",pos,ss->ply);',
        'c3x027_lineage_emit("GUARD_REENABLED",pos,ss->ply);\n c3x027_c3b_arm(pos,ss,move);',"GUARD")
 s=once(s,'c3x027_lineage_emit("CHILD_VALUE_RETURNED",pos,ss->ply,value,alpha,beta);',
        'c3x027_lineage_emit("CHILD_VALUE_RETURNED",pos,ss->ply,value,alpha,beta);\n c3x027_c3b_child_return(pos,ss,move,value);',"CHILD")
 s=once(s,'c3x027_lineage_emit("PARENT_CANDIDATE_VALUE",pos,ss->ply,value,alpha,beta);',
        'c3x027_lineage_emit("PARENT_CANDIDATE_VALUE",pos,ss->ply,value,alpha,beta);\n c3x027_c3b_candidate(pos,ss,move,value);',"FIRST_PARENT")
 # Original source-main post-undo candidate site is required for upper ancestor edges.
 anchor='      // Step 19. Undo move\n      pos.undo_move(move);'
 s=once(s,anchor,anchor+'\n      c3x027_c3b_candidate(pos,ss,move,int(value));',"UPPER_PARENT")
 # Original Stockfish16 main final return source boundary.
 anchor='    return bestValue;\n  }\n\n\n  // qsearch() is the quiescence search function'
 s=once(s,anchor,'    c3x027_c3b_frame_return(pos,ss,int(bestValue));\n'+anchor,"MAIN_FRAME_RETURN")
 anchor='    return bestValue;\n  }\n\n\n  // value_to_tt() adjusts a mate or TB score'
 s=once(s,anchor,'    c3x027_c3b_frame_return(pos,ss,int(bestValue));\n'+anchor,"Q_FRAME_RETURN")
 return s

def main():
 a=argparse.ArgumentParser()
 a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True)
 x=a.parse_args();f=Path(x.source)/"src/search.cpp"
 before=f.read_bytes();after=patch(before.decode()).encode();f.write_bytes(after)
 out=Path(x.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"schema":"c3x027-game14-source-C3b-passive-extension-v1",
  "before_sha256":hashlib.sha256(before).hexdigest(),
  "after_sha256":hashlib.sha256(after).hexdigest(),
  "source_event_transport":"private_C3X027_GAME14_LINEAGE_LOG",
  "causal_root_effect_not_certified":True,"original_024_overlay_untouched":True},
  indent=2,sort_keys=True)+"\n")
 print("C3X027_GAME14_SOURCE_C3B_PASSIVE_EXTENSION_PATCHED")
if __name__=="__main__":main()
