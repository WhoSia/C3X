#!/usr/bin/env python3
"""Source-exact SF16 TTEntry::save decision observer + single old writer repair.

Overlay AFTER age/bound/root pair V and physical payload writer, and after TT
source root context. Diagnostic-only, one-thread cold process. Leaves
native 10-byte TTEntry layout unchanged.
"""
import argparse,hashlib,json
from pathlib import Path

def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_P01_{label}_ANCHOR_{n}")
 return s.replace(a,b,1)

FUNCTIONS=r"""
// P0+P1 actual TTEntry::save decision and post-write byte reinstatement.
// All source events are optional, single-thread only, no global state mutation
// when target is absent. Source TTEntry layout remains 10 packed bytes.
namespace {
C3X018Writer c3x018_p1_old_shadow;
bool c3x018_p1_seen_first_V=false;
bool c3x018_p1_done=false;
uint64_t c3x018_p0_proposals=0;
uint64_t c3x018_p1_saves=0;
bool c3x018_p1_selected(Key key, const TTEntry* slot) {
    return std::getenv("C3X018_P1_WRITER_KEY64") &&
           std::getenv("C3X018_P1_WRITER_SLOT") &&
           std::getenv("C3X018_P1_WRITER_EPOCH") &&
           uint64_t(key)==c3x018_parameter("C3X018_P1_WRITER_KEY64") &&
           c3x018_slot(key,slot)==int(c3x018_parameter("C3X018_P1_WRITER_SLOT"));
}
void c3x018_p1_log(const char* kind, Key key, const TTEntry* slot,
                   uint64_t oldepoch, uint64_t oldserial,
                   int olddepth, int oldbound, int oldvalue,
                   bool would, bool exact, bool different_key,
                   bool deeper, int newdepth, int newbound,
                   int newvalue, int neweval) {
    if (++c3x018_p0_proposals>96) {
        if (c3x018_p0_proposals==97)
            sync_cout << "info string c3x018_p1_save kind=censored" << sync_endl;
        return;
    }
    sync_cout << "info string c3x018_p1_save kind=" << kind
              << " ordinal=" << c3x018_p0_proposals
              << " key64=" << uint64_t(key)
              << " slot=" << c3x018_slot(key,slot)
              << " old_epoch=" << oldepoch
              << " old_serial=" << oldserial
              << " old_depth=" << olddepth
              << " old_bound=" << oldbound
              << " old_value=" << oldvalue
              << " would_write=" << int(would)
              << " exact=" << int(exact)
              << " different_key16=" << int(different_key)
              << " deeper=" << int(deeper)
              << " new_depth=" << newdepth
              << " new_bound=" << newbound
              << " new_value=" << newvalue
              << " new_eval=" << neweval
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << " first_V_seen=" << int(c3x018_p1_seen_first_V)
              << sync_endl;
}
} // C3X018_P1_GLOBAL

// Return 0=original write,1=skip,2=write-then-reinstate.
int c3x018_p1_before_save(Key key,const TTEntry* ptr,
       bool would,bool exact,bool different_key,bool deeper,
       int newdepth,int newbound,int newvalue,int neweval) {
    if (!c3x018_p1_selected(key,ptr)) return 0;
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    const auto it=c3x018_shadow.find(ptr);
    const bool known=it!=c3x018_shadow.end();
    const C3X018Writer old=known?it->second:C3X018Writer{};
    // Track every proposed save of the watched 64-bit key and physical slot.
    c3x018_p1_log("proposal",key,ptr,old.epoch,old.writer_serial,
                   old.depth,old.bound,old.value,
                   would,exact,different_key,deeper,
                   newdepth,newbound,newvalue,neweval);
    const char* policy=std::getenv("C3X018_P1_WRITE_POLICY");
    if (!policy || !*policy || c3x018_p1_done || !c3x018_p1_seen_first_V ||
        !would || !known || old.key64!=uint64_t(key) ||
        old.epoch!=c3x018_parameter("C3X018_P1_WRITER_EPOCH"))
        return 0;
    const int kind=std::strcmp(policy,"SKIP")==0 ? 1:
                   std::strcmp(policy,"REINSTATE")==0 ? 2:0;
    if (!kind) return 0;
    c3x018_p1_done=true;   // at most one accepted write proposal is affected
    c3x018_p1_old_shadow=old;
    c3x018_p1_log(kind==1?"writer_skip":"writer_reinstate_selected",
       key,ptr,old.epoch,old.writer_serial,old.depth,old.bound,old.value,
       would,exact,different_key,deeper,newdepth,newbound,newvalue,neweval);
    return kind;
}
void c3x018_p1_after_reinstate(Key key,TTEntry* ptr) {
    // Called from within TTEntry::save after original accepted payload update,
    // and after the local previous TTEntry bytes have been restored.
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    auto it=c3x018_shadow.find(ptr);
    const uint64_t overwritten_epoch=it==c3x018_shadow.end()?0:it->second.epoch;
    const uint64_t overwritten_serial=it==c3x018_shadow.end()?0:it->second.writer_serial;
    if (it!=c3x018_shadow.end())it->second=c3x018_p1_old_shadow;
    ++c3x018_p1_saves;
    sync_cout << "info string c3x018_p1_save kind=writer_reinstated"
              << " key64=" << uint64_t(key)
              << " slot=" << c3x018_slot(key,ptr)
              << " old_epoch=" << c3x018_p1_old_shadow.epoch
              << " old_serial=" << c3x018_p1_old_shadow.writer_serial
              << " overwritten_epoch=" << overwritten_epoch
              << " overwritten_serial=" << overwritten_serial
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << sync_endl;
}
"""

def patch_tt(s):
    s=one(s,"bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write) {",
          FUNCTIONS+"\nbool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write) {","P01_GLOBAL")
    # The reader gate witnesses an ACTUAL first V read block, not just table read.
    old='''    c3x018_event(block ? "reader_block" : "consumer_reached", site,'''
    new='''    if (block && std::strcmp(mode,"V")==0 &&
        std::strcmp(site,"tt_value_eval_override")==0 &&
        std::getenv("C3X018_P1_FIRST_CALL") &&
        c3x018_root_context_call==c3x018_parameter("C3X018_P1_FIRST_CALL"))
        c3x018_p1_seen_first_V=true;
    c3x018_event(block ? "reader_block" : "consumer_reached", site,'''
    s=one(s,old,new,"FIRST_ACTUAL_V")
    old='''  if (c3x018_writer_block(k, this, c3x018_would_payload_write))
      return;
  // Preserve any existing move'''
    new='''  // The EXACT original predicate includes bound, 16-bit key mismatch,
  // and effective depth, with possible separate move16-only update.
  const bool c3x018_p0_exact=b==BOUND_EXACT;
  const bool c3x018_p0_different=(uint16_t)k!=key16;
  const bool c3x018_p0_deeper=d-DEPTH_OFFSET+2*pv>depth8-4;
  const int c3x018_p1_policy=c3x018_p1_before_save(
      k,this,c3x018_would_payload_write,c3x018_p0_exact,
      c3x018_p0_different,c3x018_p0_deeper,
      int(d),int(b),int(v),int(ev));
  if (c3x018_p1_policy==1) return; // no move16 update either
  const TTEntry c3x018_p1_before=*this; // full original 10-byte TT payload
  if (c3x018_writer_block(k, this, c3x018_would_payload_write))
      return;
  // Preserve any existing move'''
    s=one(s,old,new,"SAVE_BRANCH_DECISION")
    old='''      c3x018_note_payload_write(k, this, int(depth8),
                                int(genBound8 & 3), int(value16));
  }
}'''
    new='''      c3x018_note_payload_write(k, this, int(depth8),
                                int(genBound8 & 3), int(value16));
      if (c3x018_p1_policy==2) {
          // Source write really occurred; only afterward repair old resident
          // TT bytes and the sidecar writer epoch/serial/payload identity.
          *this=c3x018_p1_before;
          c3x018_p1_after_reinstate(k,this);
      }
  }
}'''
    s=one(s,old,new,"POST_WRITE_REINSTATEMENT")
    old='''      c3x018_discovery_count = 0;'''
    new='''      c3x018_discovery_count = 0;
      c3x018_p1_seen_first_V=false;
      c3x018_p1_done=false;
      c3x018_p0_proposals=0;
      c3x018_p1_saves=0;'''
    s=one(s,old,new,"CLEAR_P1_STATE")
    return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 file=Path(a.source)/"src/tt.cpp"
 old=file.read_bytes();new=patch_tt(old.decode()).encode()
 file.write_bytes(new)
 obj={"schema":"c3x018-P0-actual-save-decision-and-P1-physical-writer-reinstatement-v1",
      "source_file":"src/tt.cpp","before_sha256":hashlib.sha256(old).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "actual_source_branch":"b==BOUND_EXACT || key16_mismatch || d-DEPTH_OFFSET+2pv>old_depth8-4",
      "policies":["NONE","SKIP","REINSTATE"],
      "only_after_actual_first_V_reader_block":True,
      "max_selected_epoch_next_rewrites":1,
      "restoration":"restore all previous ten bytes of TTEntry and full shadow last writer with old physical epoch; global writer serial remains advanced",
      "writer_watch_key_slot_epoch_env":["C3X018_P1_WRITER_KEY64","C3X018_P1_WRITER_SLOT","C3X018_P1_WRITER_EPOCH"],
      "first_actual_V_env":"C3X018_P1_FIRST_CALL",
      "policy_env":"C3X018_P1_WRITE_POLICY",
      "scope":"single source-local actual TT payload overwrite after first selected V read, not global engine writing",
      "limits":["Move-only writes distinguish from accepted payload rewrites",
         "Reinstatement is synthetic after the original save; different from naturally persistent old TT writer",
         "P0 event log capped 96 and labels censorship",
         "Slot write generation of the repaired shadow is restored but global accepted writer serial is never rolled back",
         "One-thread only; no cross-arm causal identity from root_call alone",
         "Any second reader recovery proves a conditional writer-lifetime channel, NOT root bestmove natural mediation"]}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(obj,indent=2)+"\n")
 print("C3X018_P0_SAVE_BRANCH_P1_REWRITE_REINSTATE_SOURCE_OVERLAY_READY")
if __name__=="__main__":main()
