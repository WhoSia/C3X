#!/usr/bin/env python3
"""C3X 0.15 P6-S1: suppress ONE EXACT presealed full64 physical TT return,
otherwise original native TT rules and chess move legality remain unchanged.
Applies after P3-R2, P4 and P6-S0 passive target observers.
"""
import argparse,hashlib,json
from pathlib import Path
def only(s,old,new,k):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'C3X015_P6S1_ANCHOR_{k}_{n}')
 return s.replace(old,new,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out-manifest',required=True)
 a=ap.parse_args();src=Path(a.source)/'src'
 names=['c3x014_pin_trace.h','position.cpp','search.cpp']
 files={n:src/n for n in names};old={n:f.read_bytes() for n,f in files.items()}
 h,p,s=(old[n].decode() for n in names)
 h=only(h,'std::string c3x015_p6s0_target_summary();',
  'std::string c3x015_p6s0_target_summary();\nbool c3x015_p6s1_permit_selected_return(TTEntry*,Key,int,int,int,int,int,int);\nstd::string c3x015_p6s1_target_intervention_summary();','HEADER')
 anchor='static thread_local C3X015P6S0Target c3x015_p6s0;'
 patch=r"""static thread_local C3X015P6S0Target c3x015_p6s0;
struct C3X015P6S1 {
 int mode=0,target_valid=0,target_slot=-1,target_tag=0,target_bound=0,target_depth=0;
 int target_alpha=0,target_beta=0,target_cdepth=0,target_ply=0,target_kind=0;
 std::uint64_t target_key=0,target_writer_sequence=0,exact_hits=0,suppressed=0;
};
static thread_local C3X015P6S1 c3x015_p6s1;
void c3x015_p6s1_reset(){
 c3x015_p6s1=C3X015P6S1{};
 const char*mode=std::getenv("C3X015_P6S1_MODE");
 if(!mode)std::abort();
 if(std::strcmp(mode,"ALLOW")==0)c3x015_p6s1.mode=0;
 else if(std::strcmp(mode,"BLOCK_EXACT_ONCE")==0)c3x015_p6s1.mode=1;
 else std::abort();
 const char*key=std::getenv("C3X015_P6S1_TARGET_FULLKEY");
 if(!key)std::abort();
 c3x015_p6s1.target_key=std::strtoull(key,nullptr,10);
 c3x015_p6s1.target_valid=int(c3x015_p6s1.target_key!=0);
 auto num=[](const char*name)->int{
   const char*v=std::getenv(name);if(!v)std::abort();
   return std::atoi(v);
 };
 auto unum=[](const char*name)->std::uint64_t{
   const char*v=std::getenv(name);if(!v)std::abort();
   return std::strtoull(v,nullptr,10);
 };
 c3x015_p6s1.target_slot=num("C3X015_P6S1_TARGET_SLOT");
 c3x015_p6s1.target_tag=num("C3X015_P6S1_TARGET_TAG");
 c3x015_p6s1.target_bound=num("C3X015_P6S1_TARGET_BOUND");
 c3x015_p6s1.target_depth=num("C3X015_P6S1_TARGET_DEPTH");
 c3x015_p6s1.target_writer_sequence=unum("C3X015_P6S1_TARGET_WRITESEQ");
 c3x015_p6s1.target_alpha=num("C3X015_P6S1_TARGET_ALPHA");
 c3x015_p6s1.target_beta=num("C3X015_P6S1_TARGET_BETA");
 c3x015_p6s1.target_cdepth=num("C3X015_P6S1_TARGET_CDEPTH");
 c3x015_p6s1.target_ply=num("C3X015_P6S1_TARGET_PLY");
 c3x015_p6s1.target_kind=num("C3X015_P6S1_TARGET_KIND");
}
bool c3x015_p6s1_permit_selected_return(TTEntry*slot,Key key,int a,int b,
                                         int d,int ply,int kind,int value){
 if(!c3x015_p6s1.target_valid || !c3x015_win.first_seen)return true;
 if(std::uint64_t(key)!=c3x015_p6s1.target_key)return true;
 const auto w=c3x015_tt_writer(slot,key);
 if(!w.known || !w.key_exact)return true;
 if(int(slot-TT.first_entry(key))!=c3x015_p6s1.target_slot)return true;
 if(w.sequence!=c3x015_p6s1.target_writer_sequence || w.tag!=c3x015_p6s1.target_tag
    || w.bound!=c3x015_p6s1.target_bound || w.depth!=c3x015_p6s1.target_depth)return true;
 if(a!=c3x015_p6s1.target_alpha || b!=c3x015_p6s1.target_beta
   || d!=c3x015_p6s1.target_cdepth || ply!=c3x015_p6s1.target_ply
   || kind!=c3x015_p6s1.target_kind)return true;
 ++c3x015_p6s1.exact_hits;
 if(c3x015_p6s1.mode==1 && c3x015_p6s1.suppressed==0){
  ++c3x015_p6s1.suppressed;
  return false;
 }
 return true;
}
std::string c3x015_p6s1_target_intervention_summary(){
 std::ostringstream o;
 o<<"mode="<<c3x015_p6s1.mode<<" target_valid="<<c3x015_p6s1.target_valid
  <<" exact_hits="<<c3x015_p6s1.exact_hits<<" suppressed="<<c3x015_p6s1.suppressed
  <<" target_key="<<c3x015_p6s1.target_key
  <<" target_seq="<<c3x015_p6s1.target_writer_sequence;
 return o.str();
}"""
 p=only(p,anchor,patch,'STATE_AND_EXACT_MATCHER')
 p=only(p,'  c3x015_p6s0=C3X015P6S0Target{};',
        '  c3x015_p6s0=C3X015P6S0Target{};\n  c3x015_p6s1_reset();','ROOT_RESET')
 p=only(p,'  if(cutoff)++c3x015_tt_events.taken_cutoffs;',
        '  if(cutoff==1)++c3x015_tt_events.taken_cutoffs;','P4_REAL_TAKEN_CUTOFF_COUNT')
 event='c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),1);'
 choice='c3x015_p6s0_record_candidate_return(tte,posKey,int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),int(ttValue));'
 if s.count(event)!=2 or s.count(choice)!=2:raise RuntimeError('PREPARE_P6_TT_READER_SITES_NOT_TWO')
 # The P6-S0 source observer calls occur after P4's 'would-return' provenance record:
 # reorder to log a *taken* cutoff only when an actual return takes place.
 oldblock=event+'\n            '+choice+'\n            return ttValue;'
 newblock=choice+'''
            if(c3x015_p6s1_permit_selected_return(tte,posKey,int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),int(ttValue))){
                '''+event+'''
                return ttValue;
            } else {
                c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),2);
            }'''
 if s.count(oldblock)!=2:raise RuntimeError('TT_RETURN_AND_P6S0_BLOCK_ANCHOR_'+str(s.count(oldblock)))
 s=s.replace(oldblock,newblock)
 s=only(s,'  sync_cout << "info string c3x015_p6s0_target " << c3x015_p6s0_target_summary() << sync_endl;',
        '  sync_cout << "info string c3x015_p6s0_target " << c3x015_p6s0_target_summary() << sync_endl;\n  sync_cout << "info string c3x015_p6s1_target_intervention " << c3x015_p6s1_target_intervention_summary() << sync_endl;',
        'P6_SOURCE_INFO')
 for n,v in zip(names,(h,p,s)):files[n].write_text(v)
 out={'schema':'c3x015-P6S1-suppress-exact-presealed-full64-writer-read-return-once-v1',
   'suppressions_per_search_max':1,'source_mutation_only':'conditionally bypass one original TT early return after source eligibility if key, writer source, physical slot, write sequence, bound/depth and current read frame match presealed OFF target',
   'OFF_unmodified_comparison_required':True,
   'native_TTEntry_layout_changed':False,
   'tt_pruning_counter_blocked_return_recorded_as_taken':False,
   'orig_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in old.items()},
   'new_sha256':{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names}}
 dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(out,indent=2)+'\n')
 print('C3X015_P6S1_STRICT_TT_FULLKEY_SINGLE_RETURN_INTERVENTION_PATCH_PASS',flush=True)
if __name__=='__main__':main()
