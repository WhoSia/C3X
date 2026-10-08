#!/usr/bin/env python3
"""EP10 one-execution-event TT return surgery atop frozen Stockfish16 EP9."""
import argparse, hashlib, json
from pathlib import Path

def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise ValueError(f"EP10_ANCHOR_{label}_COUNT_{n}")
    return s.replace(a,b,1)

CPP=r"""
  struct C3XEp10Stats {
    unsigned long long main_seen=0,q_seen=0,blocked=0,target_ordinal=0,actual_ordinal=0;
    int target_site=0,actual_site=0,actual_ply=-1,actual_depth=-1;
    int actual_alpha=0,actual_beta=0,actual_value=0;
  } c3x_ep10;
  void c3x_ep10_begin_search() {
      c3x_ep10=C3XEp10Stats{};
      const char* site=std::getenv("C3X_P8_EP10_SITE");
      const char* ordinal=std::getenv("C3X_P8_EP10_ORDINAL");
      if(!site || !std::strcmp(site,"NONE")) c3x_ep10.target_site=0;
      else if(!std::strcmp(site,"MAIN")) c3x_ep10.target_site=1;
      else if(!std::strcmp(site,"QSEARCH")) c3x_ep10.target_site=2;
      else { std::cerr<<"EP10_BAD_SITE"<<std::endl;std::exit(92); }
      if(ordinal && *ordinal) {
          char* end=nullptr;auto v=std::strtoull(ordinal,&end,10);
          if(!end || *end || v>1000000000ULL) {std::cerr<<"EP10_BAD_ORDINAL"<<std::endl;std::exit(93);}
          c3x_ep10.target_ordinal=v;
      }
      if((c3x_ep10.target_site==0)!=(c3x_ep10.target_ordinal==0)) {
          std::cerr<<"EP10_SITE_ORDINAL_MISMATCH"<<std::endl;std::exit(94);
      }
  }
  bool c3x_ep10_block_one(int site,int ply,int depth,int alpha,int beta,int value) {
      auto ordinal=site==1 ? ++c3x_ep10.main_seen : ++c3x_ep10.q_seen;
      if(site!=c3x_ep10.target_site || ordinal!=c3x_ep10.target_ordinal || c3x_ep10.blocked) return false;
      ++c3x_ep10.blocked;
      c3x_ep10.actual_site=site;c3x_ep10.actual_ordinal=ordinal;
      c3x_ep10.actual_ply=ply;c3x_ep10.actual_depth=depth;
      c3x_ep10.actual_alpha=alpha;c3x_ep10.actual_beta=beta;c3x_ep10.actual_value=value;
      return true;
  }
  void c3x_ep10_dump() {
      const auto& s=c3x_ep10;
      sync_cout<<"info string c3x_p8_ep10"
        <<" site="<<s.target_site<<" ordinal="<<s.target_ordinal
        <<" main_seen="<<s.main_seen<<" q_seen="<<s.q_seen
        <<" blocked="<<s.blocked<<" actual_site="<<s.actual_site
        <<" actual_ordinal="<<s.actual_ordinal<<" actual_ply="<<s.actual_ply
        <<" actual_depth="<<s.actual_depth<<" actual_alpha="<<s.actual_alpha
        <<" actual_beta="<<s.actual_beta<<" actual_value="<<s.actual_value
        <<sync_endl;
  }
"""

def instrument(s):
    s=one(s,"  // Different node types, used as a template parameter",CPP+"\n  // Different node types, used as a template parameter","STRUCT")
    s=one(s,"  c3x_ep9_begin_search();\n  TT.new_search();","  c3x_ep9_begin_search();\n  c3x_ep10_begin_search();\n  TT.new_search();","RESET")
    s=one(s,'  c3x_ep9_dump();\n  sync_cout << "bestmove "','  c3x_ep9_dump();\n  c3x_ep10_dump();\n  sync_cout << "bestmove "',"DUMP")
    s=one(s,"                ++c3x_ep9_stats.main_cutoff_taken;\n                return ttValue;",
      """                if(c3x_ep10_block_one(1,ss->ply,int(depth),int(alpha),int(beta),int(ttValue)))
                    ++c3x_ep9_stats.main_cutoff_blocked;
                else { ++c3x_ep9_stats.main_cutoff_taken;return ttValue; }""","MAIN")
    s=one(s,"            ++c3x_ep9_stats.q_cutoff_taken;\n            return ttValue;",
      """            if(c3x_ep10_block_one(2,ss->ply,int(depth),int(alpha),int(beta),int(ttValue)))
                ++c3x_ep9_stats.q_cutoff_blocked;
            else { ++c3x_ep9_stats.q_cutoff_taken;return ttValue; }""","QSEARCH")
    return s

def main():
    p=argparse.ArgumentParser();p.add_argument("--search-cpp",required=True);p.add_argument("--out-manifest",required=True);a=p.parse_args()
    f=Path(a.search_cpp);before=f.read_text();after=instrument(before);f.write_text(after)
    obj={"schema":"c3x-013-p8ep10-single-tt-return-site-ordinal-v1",
         "from":"official Stockfish sf_16 + EP9 exact-anchor instrumentation",
         "input_sha256":hashlib.sha256(before.encode()).hexdigest(),
         "output_sha256":hashlib.sha256(after.encode()).hexdigest(),
         "site":{"NONE":0,"MAIN":1,"QSEARCH":2},"max_blocked_per_cold_run":1,
         "target":"site-specific ordinal of actual TT bound early-return opportunity",
         "target_selection_outcome_blind":True,
         "raw_TT_keys_exported":False,
         "limitations":["the ordinal identifies a deterministic execution occurrence within a cold run, not a persistent board-invariant event", "global search changes after one cutoff is blocked","no claim about chess concepts or cross-engine causal transport"]}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(obj,indent=2)+"\n")
    print("EP10_EXACT_ANCHORS_PATCHED")
if __name__=="__main__":main()
