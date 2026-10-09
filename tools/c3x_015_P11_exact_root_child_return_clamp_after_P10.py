#!/usr/bin/env python3
"""C3X 0.15 P11: clamp exactly one P10-first-disclosed root child return, after source search, before root candidate consumer.
Patch pinned Stockfish16 AFTER P10 observer patch; outcome-only data from post-P6 world 2. FAIL CLOSED.
"""
import argparse,hashlib,json
from pathlib import Path
def exactly(s,a,b,n):
 c=s.count(a)
 if c!=1:raise RuntimeError(f"P11_PATCH_ANCHOR_{n}_EXPECTED_1_GOT_{c}")
 return s.replace(a,b,1)
def patch(root):
 root=Path(root)/"src";names=("c3x014_pin_trace.h","position.cpp","search.cpp")
 paths={n:root/n for n in names};original={n:paths[n].read_bytes() for n in names}
 h,p,s=(original[n].decode() for n in names)
 h=exactly(h,"std::string c3x015_p10_root_trace_summary();",
 """std::string c3x015_p10_root_trace_summary();
int c3x015_p11_root_relay(Key key,int depth,int move,int count,int alpha,int beta,int child_return);
std::string c3x015_p11_root_relay_summary();""","HEADER")
 p=exactly(p,"static thread_local C3X015P10 c3x015_p10;",
r"""static thread_local C3X015P10 c3x015_p10;
struct C3X015P11 {
 int requested=0,matching=0,fired=0,old_value=0,new_value=0;
};
static thread_local C3X015P11 c3x015_p11;
int c3x015_p11_root_relay(Key key,int depth,int move,int count,int alpha,int beta,int child_return) {
 if (std::uint64_t(key)!=5622551786424219112ULL ||
     depth!=4 || move!=1380 || count!=42 || alpha!=130 || beta!=162 ||
     (child_return!=0 && child_return!=130))return child_return;
 ++c3x015_p11.matching;
 if(c3x015_p11.requested!=1||c3x015_p11.fired>0)return child_return;
 ++c3x015_p11.fired;
 c3x015_p11.old_value=child_return;
 c3x015_p11.new_value=14;
 return 14;
}
std::string c3x015_p11_root_relay_summary(){
 std::ostringstream o;
 o<<"requested="<<c3x015_p11.requested<<" matching="<<c3x015_p11.matching
  <<" fired="<<c3x015_p11.fired<<" original="<<c3x015_p11.old_value
  <<" replacement="<<c3x015_p11.new_value;
 return o.str();
}""","STATE")
 p=exactly(p," c3x015_p10=C3X015P10{};",
r""" c3x015_p10=C3X015P10{};
 c3x015_p11=C3X015P11{};
 const char* p11_env=std::getenv("C3X015_P11_ROOT_CLAMP");
 if(!p11_env)std::abort();
 if(std::strcmp(p11_env,"SHAM")==0)c3x015_p11.requested=0;
 else if(std::strcmp(p11_env,"CLAMP")==0)c3x015_p11.requested=1;
 else std::abort();""","RESET")
 s=exactly(s,"      if (rootNode)\n      {\n          RootMove& rm = *std::find",
    """      if (rootNode)
      {
          value=Value(c3x015_p11_root_relay(pos.key(),int(thisThread->rootDepth),
                  int(move),int(moveCount),int(alpha),int(beta),int(value)));
          RootMove& rm = *std::find""","ROOT_VALUE_CONSUMER")
 s=exactly(s,'  sync_cout << "info string c3x015_p10_root_lineage " << c3x015_p10_root_trace_summary() << sync_endl;',
 '  sync_cout << "info string c3x015_p10_root_lineage " << c3x015_p10_root_trace_summary() << sync_endl;\n  sync_cout << "info string c3x015_p11_root_relay " << c3x015_p11_root_relay_summary() << sync_endl;',
 "UCI_READOUT")
 for n,t in zip(names,(h,p,s)):paths[n].write_text(t)
 return {"schema":"c3x015-p11-one-root-child-return-clamp-source-patch-v1",
  "pinned_original_sf16":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
  "exact_source_target":{"root_key":5622551786424219112,"root_depth":4,"native_move":1380,
    "root_move_count":42,"alpha":130,"beta":162,"original_p10_arm_values":[0,130],
    "replacement_child_return":14},
  "original_files_sha256":{n:hashlib.sha256(original[n]).hexdigest() for n in names},
  "patched_files_sha256":{n:hashlib.sha256(paths[n].read_bytes()).hexdigest() for n in names},
  "strict_limits":["No TT/qsearch engine source edit; single ROOT score relay before candidate consumption",
   "Case29 and case2 identity arms are exact no-fire controls", "Only first source match is replaced when requested",
   "Program trace is not a proof of natural TT-to-root necessary mediator."]}
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True);z=a.parse_args()
 j=patch(z.source);p=Path(z.out_manifest);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(j,indent=2)+"\n")
 print("C3X015_P11_EXACT_ROOT_VALUE_CONSUMER_CXX_PATCH_PASS")
