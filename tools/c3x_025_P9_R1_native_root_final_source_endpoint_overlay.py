#!/usr/bin/env python3
"""P9-R1 strictly source-anchored post-P8 root->bestmove scalar observer."""
import argparse,hashlib,json
from pathlib import Path
from c3x_025_P8_native_TT_field_writer_consumer_source_overlay import (
    SHA as ORIGINAL_HASHES,patch as p8_patch)
FORWARD='void c3x025_p8_consume(const TTEntry*, Key,const char*,bool,int,int);'
FORWARD_ADD=FORWARD+'\nbool c3x025_p8_on();'
FINAL='  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
FINAL_ADD='''  if (c3x025_p8_on()) {
      sync_cout << "info string c3x025_p9_root kind=FINAL_CANDIDATE"
                << " UCI=" << UCI::move(bestThread->rootMoves[0].pv[0],rootPos.is_chess960())
                << " root_score=" << int(bestThread->rootMoves[0].score)
                << " completed_depth=" << int(bestThread->completedDepth)
                << " root_candidate_count=" << unsigned(bestThread->rootMoves.size())
                << sync_endl;
  }
'''+FINAL
def patch(s:str)->str:
    for label,old,new in (("external-native-env",FORWARD,FORWARD_ADD),("root-final",FINAL,FINAL_ADD)):
        if s.count(old)!=1:raise ValueError("P9_SOURCE_REQUIRED_ANCHOR_"+label+"_"+str(s.count(old)))
        s=s.replace(old,new,1)
    return s
def restore(s:str)->str:
    for label,old,new in reversed((("external-native-env",FORWARD,FORWARD_ADD),("root-final",FINAL,FINAL_ADD))):
        if s.count(new)!=1:raise ValueError("P9_CANNOT_EXACTLY_REVERSE_ROOT_OBSERVER_"+label)
        s=s.replace(new,old,1)
    return s
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src"/"search.cpp"
    old=f.read_bytes();s=old.decode()
    s2=patch(s)
    if restore(s2).encode()!=old:
        raise ValueError("P9_ROOT_OBSERVER_NOT_EXACT_BYTE_REVERSIBLE")
    f.write_bytes(s2.encode())
    result={"schema":"c3x025-P9-R1-native-root-final-candidate-to-UCI-source-only-witness-v1",
      "pinned_upstream_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "original_P8_modified_search_cpp_SHA256":hashlib.sha256(old).hexdigest(),
      "P9_root_observer_patched_search_cpp_SHA256":hashlib.sha256(s2.encode()).hexdigest(),
      "exact_reverse_source_bytes_match":True,
      "native_E6_final_root_bestmove_UCI_field_source":"bestThread->rootMoves[0].pv[0]",
      "complete_TT_to_SEE_branch_to_parent_root_causal_chain":False,
      "source_changed_only_opt_in_reporting":True}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X025_P9_R1_SOURCE_ROOT_ENDPOINT_REVERSE_SHA",result,flush=True)
if __name__=="__main__":main()
