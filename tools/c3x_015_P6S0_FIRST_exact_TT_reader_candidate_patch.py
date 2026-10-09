#!/usr/bin/env python3
"""C3X 0.15 P6-S0 read-only first exact TT writer->consumer return target.
Apply after P3-R2 and P4 TT-physical provenance patches, prior to ANY P6 block.
Original 10-byte TTEntry, original return decisions and chess laws are unchanged.
"""
import argparse,json,hashlib
from pathlib import Path
def one(s,a,b,k):
 n=s.count(a)
 if n!=1:raise RuntimeError("C3X015_P6S0_ANCHOR_"+k+"_"+str(n))
 return s.replace(a,b,1)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
 args=ap.parse_args();src=Path(args.source)/"src"
 names=("c3x014_pin_trace.h","position.cpp","search.cpp")
 old={n:(src/n).read_bytes() for n in names}
 h,p,s=(old[n].decode() for n in names)
 h=one(h,"std::string c3x015_tt_summary();",
        "std::string c3x015_tt_summary();\nvoid c3x015_p6s0_record_candidate_return(TTEntry*,Key,int,int,int,int,int,int);\nstd::string c3x015_p6s0_target_summary();","HEADER")
 anchor="static thread_local C3X015TTProvenance c3x015_tt_events;"
 p=one(p,anchor,anchor+r"""
// This candidate is determined by OFF source execution, never P2/P5 outcomes.
struct C3X015P6S0Target {
  std::uint64_t fullkey=0,writer_sequence=0;
  int eligible=0,slot_offset=-1,writer_tag=0,stored_bound=0,stored_depth=0;
  int reader_alpha=0,reader_beta=0,reader_depth=0,reader_ply=0,reader_kind=0,reader_ttvalue=0;
};
static thread_local C3X015P6S0Target c3x015_p6s0;
void c3x015_p6s0_record_candidate_return(TTEntry*slot,Key key,int alpha,int beta,
                                         int depth,int ply,int kind,int ttvalue) {
  if(!c3x015_win.first_seen || c3x015_p6s0.eligible)return;
  auto w=c3x015_tt_writer(slot,key);
  if(!w.known || !w.key_exact)return;
  c3x015_p6s0.eligible=1;
  c3x015_p6s0.fullkey=std::uint64_t(key);
  c3x015_p6s0.writer_sequence=w.sequence;
  c3x015_p6s0.slot_offset=int(slot-TT.first_entry(key));
  c3x015_p6s0.writer_tag=w.tag;
  c3x015_p6s0.stored_bound=w.bound;
  c3x015_p6s0.stored_depth=w.depth;
  c3x015_p6s0.reader_alpha=alpha;c3x015_p6s0.reader_beta=beta;
  c3x015_p6s0.reader_depth=depth;c3x015_p6s0.reader_ply=ply;
  c3x015_p6s0.reader_kind=kind;c3x015_p6s0.reader_ttvalue=ttvalue;
}
std::string c3x015_p6s0_target_summary(){
  std::ostringstream o;
  o<<"eligible="<<c3x015_p6s0.eligible
   <<" key="<<c3x015_p6s0.fullkey
   <<" slot_offset="<<c3x015_p6s0.slot_offset
   <<" writer_seq="<<c3x015_p6s0.writer_sequence
   <<" writer_tag="<<c3x015_p6s0.writer_tag
   <<" stored_bound="<<c3x015_p6s0.stored_bound
   <<" stored_depth="<<c3x015_p6s0.stored_depth
   <<" alpha="<<c3x015_p6s0.reader_alpha
   <<" beta="<<c3x015_p6s0.reader_beta
   <<" consumer_depth="<<c3x015_p6s0.reader_depth
   <<" ply="<<c3x015_p6s0.reader_ply
   <<" node_type="<<c3x015_p6s0.reader_kind
   <<" tt_value="<<c3x015_p6s0.reader_ttvalue;
  return o.str();
}""","TARGET_REPORTER")
 p=one(p,"  c3x015_tt_events=C3X015TTProvenance{};",
       "  c3x015_tt_events=C3X015TTProvenance{};\n  c3x015_p6s0=C3X015P6S0Target{};","TARGET_RESET")
 needle='c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),1);'
 if s.count(needle)!=2:raise RuntimeError("TT_RETURN_SITES_NOT_TWO_"+str(s.count(needle)))
 s=s.replace(needle,needle+'\n            c3x015_p6s0_record_candidate_return(tte,posKey,int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),int(ttValue));')
 s=one(s,'  sync_cout << "info string c3x015_tt_provenance " << c3x015_tt_summary() << sync_endl;',
       '  sync_cout << "info string c3x015_tt_provenance " << c3x015_tt_summary() << sync_endl;\n  sync_cout << "info string c3x015_p6s0_target " << c3x015_p6s0_target_summary() << sync_endl;',
       "UCI_P6_TARGET")
 for name,v in zip(names,(h,p,s)):(src/name).write_text(v)
 info={"schema":"c3x015-p6s0-first-natural-OFF-exact-TT-return-writer-reader-target-v1",
    "source_patch_type":"observer only; no TT early return changed; after first root-object SEE candidate",
    "source_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in old.items()},
    "modified_sha256":{n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in names}}
 dest=Path(args.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(info,indent=2)+"\n")
 print("C3X015_P6S0_FIRST_FULLKEY_WRITER_READER_TARGET_SOURCE_OBSERVER_PASS",flush=True)
if __name__=="__main__":main()
