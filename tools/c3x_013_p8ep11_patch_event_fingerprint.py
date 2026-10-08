#!/usr/bin/env python3
"""C3X 0.13 P8-EP11: expose actual SF16 TT event signature and enable signature-targeted replay.

Patch layers: official sf_16 -> EP9 TT counters -> EP10 ordinal one-shot -> EP11 FEN+Zobrist+TT metadata.
No NNUE, move legality, or move generator modification. Native TT Zobrist key is
a version-specific position fingerprint, not a history-complete causal identity.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

CODE=r'''
  struct C3XEp11Event {
      bool have_target_key=false;
      unsigned long long target_key=0, actual_key=0;
      int target_site=0,target_ply=-1,target_depth=-1;
      int selected=0,matching_previously_eligible=0;
      int actual_site=0,actual_ordinal=0,actual_ply=-1,actual_depth=-1;
      int actual_alpha=0,actual_beta=0,actual_value=0,actual_tt_bound=0,actual_tt_depth=0;
      int actual_rule50=0;
      std::string actual_fen;
  } c3x_ep11;
  void c3x_ep11_begin_search() {
      c3x_ep11=C3XEp11Event{};
      const char* key=std::getenv("C3X_P8_EP11_TARGET_KEY");
      if (key && *key) {
          char* end=nullptr;
          c3x_ep11.target_key=std::strtoull(key,&end,16);
          if(!end || *end || end==key){std::cerr<<"EP11_INVALID_TT_KEY"<<std::endl;std::exit(95);}
          c3x_ep11.have_target_key=true;
          const char* site=std::getenv("C3X_P8_EP11_TARGET_SITE");
          if(!site || std::strcmp(site,"MAIN")){std::cerr<<"EP11_SITE_MUST_BE_MAIN"<<std::endl;std::exit(96);}
          c3x_ep11.target_site=1;
          const char* ply=std::getenv("C3X_P8_EP11_TARGET_PLY");
          const char* depth=std::getenv("C3X_P8_EP11_TARGET_DEPTH");
          if(!ply || !depth || !*ply || !*depth){std::cerr<<"EP11_MISSING_CONTEXT"<<std::endl;std::exit(97);}
          char* endply=nullptr;char* enddepth=nullptr;
          auto pp=std::strtol(ply,&endply,10);
          auto dd=std::strtol(depth,&enddepth,10);
          if(!endply || *endply || !enddepth || *enddepth || pp<0 || dd<0 || pp>256 || dd>256) {
              std::cerr<<"EP11_INVALID_CONTEXT"<<std::endl;std::exit(98);
          }
          c3x_ep11.target_ply=int(pp);c3x_ep11.target_depth=int(dd);
      }
  }
  bool c3x_ep11_block(int site,unsigned long long key,int ply,int depth,int alpha,
                       int beta,int value,int ttbound,int ttdepth,int rule50,
                       const Position& pos) {
      // Preserve identical ordinal machinery for the exploratory anchor experiment.
      bool old=c3x_ep10_block_one(site,ply,depth,alpha,beta,value);
      int ordinal=int(site==1 ? c3x_ep10.main_seen : c3x_ep10.q_seen);
      bool same=(c3x_ep11.have_target_key && site==c3x_ep11.target_site
                 && key==c3x_ep11.target_key && ply==c3x_ep11.target_ply
                 && depth==c3x_ep11.target_depth);
      if(same) ++c3x_ep11.matching_previously_eligible;
      bool choose_key=same && !c3x_ep11.selected && !c3x_ep10.blocked;
      if(old || choose_key) {
          ++c3x_ep11.selected;
          c3x_ep11.actual_key=key;c3x_ep11.actual_site=site;
          c3x_ep11.actual_ordinal=ordinal;c3x_ep11.actual_ply=ply;
          c3x_ep11.actual_depth=depth;c3x_ep11.actual_alpha=alpha;
          c3x_ep11.actual_beta=beta;c3x_ep11.actual_value=value;
          c3x_ep11.actual_tt_bound=ttbound;c3x_ep11.actual_tt_depth=ttdepth;
          c3x_ep11.actual_rule50=rule50;c3x_ep11.actual_fen=pos.fen();
          return true;
      }
      return false;
  }
  void c3x_ep11_dump() {
      auto& s=c3x_ep11;
      sync_cout<<"info string c3x_p8_ep11"
        <<" key_targeted="<<s.have_target_key
        <<" target_key_hex="<<std::hex<<s.target_key<<std::dec
        <<" selected="<<s.selected
        <<" matching_events="<<s.matching_previously_eligible
        <<" actual_site="<<s.actual_site
        <<" actual_ordinal="<<s.actual_ordinal
        <<" actual_ply="<<s.actual_ply
        <<" actual_depth="<<s.actual_depth
        <<" actual_alpha="<<s.actual_alpha
        <<" actual_beta="<<s.actual_beta
        <<" actual_value="<<s.actual_value
        <<" actual_tt_bound="<<s.actual_tt_bound
        <<" actual_tt_depth="<<s.actual_tt_depth
        <<" actual_rule50="<<s.actual_rule50
        <<" actual_key_hex="<<std::hex<<s.actual_key<<std::dec
        <<" fen="<<s.actual_fen
        <<sync_endl;
  }
'''

def change(s,old,new,label):
    n=s.count(old)
    if n!=1:raise ValueError(f"EP11_{label}_ANCHOR_COUNT_{n}")
    return s.replace(old,new,1)

def patch(source):
    s=change(source,"  // Different node types, used as a template parameter",
             CODE+"\n  // Different node types, used as a template parameter","STRUCT")
    s=change(s,"  c3x_ep10_begin_search();\n  TT.new_search();",
             "  c3x_ep10_begin_search();\n  c3x_ep11_begin_search();\n  TT.new_search();","BEGIN")
    s=change(s,'  c3x_ep10_dump();\n  sync_cout << "bestmove "',
             '  c3x_ep10_dump();\n  c3x_ep11_dump();\n  sync_cout << "bestmove "',"DUMP")
    old="c3x_ep10_block_one(1,ss->ply,int(depth),int(alpha),int(beta),int(ttValue))"
    new="c3x_ep11_block(1,static_cast<unsigned long long>(pos.key()),ss->ply,int(depth),int(alpha),int(beta),int(ttValue),int(tte->bound()),int(tte->depth()),pos.rule50_count(),pos)"
    s=change(s,old,new,"MAIN")
    old="c3x_ep10_block_one(2,ss->ply,int(depth),int(alpha),int(beta),int(ttValue))"
    new="c3x_ep11_block(2,static_cast<unsigned long long>(pos.key()),ss->ply,int(depth),int(alpha),int(beta),int(ttValue),int(tte->bound()),int(tte->depth()),pos.rule50_count(),pos)"
    s=change(s,old,new,"QSEARCH")
    return s

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--search-cpp",required=True)
    a.add_argument("--manifest",required=True)
    ns=a.parse_args()
    path=Path(ns.search_cpp);raw=path.read_text();fixed=patch(raw);path.write_text(fixed)
    obj={"schema":"c3x-013-p8ep11-tt-key-fen-context-native-patch-v1",
      "layer":"official Stockfish sf_16 + EP9 + EP10",
      "before_sha256":hashlib.sha256(raw.encode()).hexdigest(),
      "after_sha256":hashlib.sha256(fixed.encode()).hexdigest(),
      "locator":"TT Zobrist key + node ply + remaining depth + main or qsearch site",
      "one_shot_maximum_per_search":1,
      "additional_attested_context":["actual full node FEN","TT entry bound type","TT entry depth","rule50","search alpha-beta window","returned TT value","execution ordinal"],
      "warning":"Stable TT key across these runs does not imply equal TT-entry versions, path provenance or full repetition histories; even successful keyed replay is same-source development, not human strategic explanation."}
    p=Path(ns.manifest);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+"\n")
    print("EP11_NATIVE_TT_FINGERPRINT_SOURCE_PATCH_PASS")
if __name__=="__main__": main()
