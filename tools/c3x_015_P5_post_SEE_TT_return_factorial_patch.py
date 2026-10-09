#!/usr/bin/env python3
"""C3X 0.15 P5 source-native 2x2 TT early-return regime x ROOT_OBJECT_SEE.
Apply AFTER passive PIN + root SEE patch + P3R2 4096-search-entry observer.
TT table, storage, move ordering and chess laws remain unmodified.
"""
import argparse,hashlib,json
from pathlib import Path
def exactly_one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError(f'C3X015_P5_PATCH_{label}_MATCHED_{n}')
 return s.replace(a,b,1)
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--source',required=True);p.add_argument('--out-manifest',required=True)
 a=p.parse_args();base=Path(a.source)/'src'
 names=['c3x014_pin_trace.h','position.cpp','search.cpp'];files={n:base/n for n in names}
 old={n:f.read_bytes() for n,f in files.items()}
 h,c,s=[old[n].decode() for n in names]
 h=exactly_one(h,'void c3x015_window_reset();',
   'void c3x015_window_reset();\nbool c3x015_post_see_tt_return_permitted();\nstd::string c3x015_post_see_tt_factorial_summary();',
   'HEADER_DECLARE')
 c=exactly_one(c,'static thread_local C3X015SearchFrame c3x015_active_frame;',
   r'''static thread_local C3X015SearchFrame c3x015_active_frame;
struct C3X015TTReturnFactor {
  int block_mode=0;
  std::uint64_t eligible_return_decisions=0;
  std::uint64_t return_blocked=0;
  std::uint64_t returns_before_first_see_candidate=0;
  std::uint64_t returns_after_first_candidate_allowed=0;
};
static thread_local C3X015TTReturnFactor c3x015_tt_factor;
bool c3x015_post_see_tt_return_permitted() {
  ++c3x015_tt_factor.eligible_return_decisions;
  if(!c3x015_win.first_seen){
    ++c3x015_tt_factor.returns_before_first_see_candidate;
    return true;
  }
  if(c3x015_tt_factor.block_mode==1){
    ++c3x015_tt_factor.return_blocked;
    return false;
  }
  ++c3x015_tt_factor.returns_after_first_candidate_allowed;
  return true;
}
std::string c3x015_post_see_tt_factorial_summary(){
  std::ostringstream o;
  o<<"mode="<<c3x015_tt_factor.block_mode
   <<" eligible_returns="<<c3x015_tt_factor.eligible_return_decisions
   <<" before_candidate="<<c3x015_tt_factor.returns_before_first_see_candidate
   <<" after_candidate_allowed="<<c3x015_tt_factor.returns_after_first_candidate_allowed
   <<" after_candidate_blocked="<<c3x015_tt_factor.return_blocked;
  return o.str();
}''','P5_TT_REGIME')
 c=exactly_one(c,'  c3x015_win=C3X015WindowObserver{};',
   r'''  c3x015_win=C3X015WindowObserver{};
  c3x015_tt_factor=C3X015TTReturnFactor{};
  const char*ttMode=std::getenv("C3X015_POST_SEE_TT_RETURN_MODE");
  if(ttMode && std::strcmp(ttMode,"BLOCK_AFTER_CANDIDATE")==0)c3x015_tt_factor.block_mode=1;
  else if(ttMode && std::strcmp(ttMode,"ALLOW")==0)c3x015_tt_factor.block_mode=0;
  else std::abort();''','RUN_RESET')
 s=exactly_one(s,'        if (pos.rule50_count() < 90)\n            return ttValue;',
   '''        if (pos.rule50_count() < 90 && c3x015_post_see_tt_return_permitted())
            return ttValue;''','MAIN_TT_RETURN')
 s=exactly_one(s,'''        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;''',
   '''        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER))) {
        if (c3x015_post_see_tt_return_permitted())
            return ttValue;
    }''','QS_TT_RETURN')
 s=exactly_one(s,'  sync_cout << "info string c3x015_first_site_window " << c3x015_window_summary() << sync_endl;',
   '''  sync_cout << "info string c3x015_first_site_window " << c3x015_window_summary() << sync_endl;
  sync_cout << "info string c3x015_tt_return_factorial " << c3x015_post_see_tt_factorial_summary() << sync_endl;''',
   'UCI_PROVENANCE')
 for n,v in zip(names,(h,c,s)):files[n].write_text(v)
 out={'schema':'c3x-015-P5-conditional-TT-early-return-source-patch-v1',
      'orig_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in old.items()},
      'patched_sha256':{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
      'mode_env':'C3X015_POST_SEE_TT_RETURN_MODE',
      'modes':['ALLOW','BLOCK_AFTER_CANDIDATE'],
      'source_intervention_effect':'only suppress MAIN and QSEARCH TT early RETURN after first root-object SEE eligible source candidate; no table reset, TT save/probe, move order, legality or evaluation changes',
      'limitations':['Blocking all eligible TT returns after first SEE candidate is a broad regime, not a single-writer counterfactual',
                     'First candidate is eligibility site, not guaranteed first returned SEE value difference',
                     'After running P2 outcomes, this P5 is post-outcome interaction assessment.']}
 dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(out,indent=2)+'\n')
 print('C3X015_P5_SOURCE_NATIVE_TT_RETURN_2X2_PATCH_PASS',flush=True)
if __name__=='__main__':main()
