#!/usr/bin/env python3
"""C3X 0.16 P3: one physically frozen TT writer + same P6 exact reader, 2x2.
Apply after inherited P11 observer stack. W0 consumes one sidecar writer event
sequence as a ghost, but deliberately does NOT write the physical TT slot.
This preserves later writer ordinal alignment while measuring real TT absence.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,old,new,name):
 n=s.count(old)
 if n!=1:raise RuntimeError(f"C3X016_TT_FACTORIAL_SOURCE_ANCHOR_{name}_{n}_EXPECTED_1")
 return s.replace(old,new,1)
def main():
 q=argparse.ArgumentParser()
 q.add_argument("--source",required=True)
 q.add_argument("--out-manifest",required=True)
 args=q.parse_args()
 root=Path(args.source)/"src"
 names=["tt.cpp","position.cpp","search.cpp","c3x014_pin_trace.h"]
 files={n:root/n for n in names}
 before={n:p.read_bytes() for n,p in files.items()}
 tt,pos,search,header=(before[n].decode() for n in names)
 tt=one(tt,"static thread_local int c3x015_writer_tag=0;",
    """static thread_local int c3x015_writer_tag=0;
extern bool c3x016_exact_writer_allow(std::uint64_t,int,int,int,int,std::uint64_t);""","GATE_DECL")
 tt=one(tt,
   "  c3x015_writer_tag=tag;e->save(k,v,pv,b,d,m,ev);c3x015_writer_tag=prev;",
   """  c3x015_writer_tag=tag;
  // The original P4 sidecar sequence is incremented by every TTEntry::save.
  // Consume the single missing writer's ordinal as a GHOST, without changing
  // the physical slot. This keeps later writer ordinals comparably indexed.
  const bool permitted=c3x016_exact_writer_allow(
    std::uint64_t(k),int(e-TT.first_entry(k)),tag,int(b),int(d),
    c3x015_tt_sequence+1);
  if(permitted)e->save(k,v,pv,b,d,m,ev);
  else ++c3x015_tt_sequence;
  c3x015_writer_tag=prev;""","EXACT_WRITER")
 pos=one(pos,"static thread_local C3X015P11 c3x015_p11;",
r"""static thread_local C3X015P11 c3x015_p11;
struct C3X016WriterFactor {
 int assigned=1,writer_contact=0,suppressed=0,prior_writer_qualified=0;
 std::uint64_t suppressed_ordinal=0;
};
static thread_local C3X016WriterFactor c3x016_wr;
bool c3x016_exact_writer_allow(std::uint64_t k,int slot,int tag,int bound,int depth,
                               std::uint64_t next_seq) {
 if(!c3x015_p6s1.target_valid)return true;
 if(k!=c3x015_p6s1.target_key ||
    slot!=c3x015_p6s1.target_slot ||
    tag!=c3x015_p6s1.target_tag ||
    bound!=c3x015_p6s1.target_bound ||
    depth!=c3x015_p6s1.target_depth ||
    next_seq!=c3x015_p6s1.target_writer_sequence)return true;
 ++c3x016_wr.writer_contact;
 if(c3x016_wr.assigned==0 && c3x016_wr.suppressed==0){
  ++c3x016_wr.suppressed;
  c3x016_wr.suppressed_ordinal=next_seq;
  return false;
 }
 return true;
}
std::string c3x016_writer_factor_report(){
 std::ostringstream out;
 out<<"W="<<c3x016_wr.assigned
    <<" contact="<<c3x016_wr.writer_contact
    <<" suppressed="<<c3x016_wr.suppressed
    <<" ghost_ordinal="<<c3x016_wr.suppressed_ordinal
    <<" target_seq="<<c3x015_p6s1.target_writer_sequence;
 return out.str();
}""","FACTOR_STATE")
 pos=one(pos," c3x015_p11=C3X015P11{};",
r""" c3x015_p11=C3X015P11{};
 c3x016_wr=C3X016WriterFactor{};
 const char* wrmode=std::getenv("C3X016_TT_WRITER_MODE");
 if(!wrmode)std::abort();
 if(std::strcmp(wrmode,"W1")==0)c3x016_wr.assigned=1;
 else if(std::strcmp(wrmode,"W0")==0)c3x016_wr.assigned=0;
 else std::abort();""","STATE_RESET")
 header=one(header,"std::string c3x015_p11_root_relay_summary();",
    "std::string c3x015_p11_root_relay_summary();\nstd::string c3x016_writer_factor_report();","HEADER")
 search=one(search,
 '  sync_cout << "info string c3x015_p11_root_relay " << c3x015_p11_root_relay_summary() << sync_endl;',
 '  sync_cout << "info string c3x015_p11_root_relay " << c3x015_p11_root_relay_summary() << sync_endl;\n  sync_cout << "info string c3x016_writer_factor " << c3x016_writer_factor_report() << sync_endl;',
 "REPORT")
 for n,s in zip(names,(tt,pos,search,header)):files[n].write_text(s)
 report={"schema":"c3x016-P3-one-frozen-natural-TT-writer-source-ghost-ordinal-v1",
  "component":"TWO_CASE_DEVELOPMENT_2x2_ONE_EXACT_PHYSICAL_TT_WRITER_AND_ORIGINAL_P6S1_READER",
  "source_before_sha256":{n:hashlib.sha256(before[n]).hexdigest() for n in names},
  "source_after_sha256":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
  "W0_rule":"skip exactly one TTEntry::save after pre-frozen fullkey slot writer tag bound depth next ordinal match, increment ordinal ghost but DO NOT update physical TT slot",
  "R0_rule":"inherited P6S1 BLOCK_EXACT_ONCE at original reader physical writer/slot with no dynamic retarget",
  "warrant_ceilings":["W0 R0 may never contact original reader; keep in denominator",
    "Ghost ordinal is observer-time bookkeeping, NOT a TT physical write",
    "Source writer label/seq at code call is a nominal identity; if physical TT save lacks full-fields, report generation mismatch",
    "2 post-outcome worlds are a development experiment, not prospectively independent chess motif validation"]}
 out=Path(args.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2)+"\n")
 print("C3X016_P3_EXACT_TT_WRITER_FACTOR_SOURCE_PATCH_PASS")
if __name__=="__main__":main()
