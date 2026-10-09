#!/usr/bin/env python3
"""Post-P0P1 orthogonal raw TTEntry bytes / shadow writer identity repair.

Native SF16 10-byte structure unchanged. This is a deliberately destructive
measurement-identifiability test, not a natural writer treatment.
Apply after temporal scope overlay and P0P1 source overlay.
"""
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,label):
    count=s.count(a)
    if count!=1:raise RuntimeError(f"C3X019_TAG_BYTES_{label}_ANCHOR_{count}")
    return s.replace(a,b,1)

def patch(s):
    s=once(s,
'''    const int kind=std::strcmp(policy,"SKIP")==0 ? 1:
                   std::strcmp(policy,"REINSTATE")==0 ? 2:0;''',
'''    const int kind=std::strcmp(policy,"SKIP")==0 ? 1:
                   std::strcmp(policy,"REINSTATE")==0 ? 2:
                   std::strcmp(policy,"SHADOW_ONLY")==0 ? 3:
                   std::strcmp(policy,"BYTES_ONLY")==0 ? 4:0;''',
"POLICY")
    s=once(s,
'''    c3x018_p1_log(kind==1?"writer_skip":"writer_reinstate_selected",''',
'''    c3x018_p1_log(kind==1?"writer_skip":
                   kind==3?"writer_shadow_only_selected":
                   kind==4?"writer_bytes_only_selected":"writer_reinstate_selected",''',
"POLICY_EVENT")
    s=once(s,
'''void c3x018_p1_after_reinstate(Key key,TTEntry* ptr) {''',
'''void c3x018_p1_after_reinstate(Key key,TTEntry* ptr,
                                bool restore_shadow,bool restore_bytes) {''',
"AFTER_SIGNATURE")
    s=once(s,
'''    if (it!=c3x018_shadow.end())it->second=c3x018_p1_old_shadow;''',
'''    if (restore_shadow && it!=c3x018_shadow.end())
        it->second=c3x018_p1_old_shadow;''',
"SHADOW_CONDITIONAL")
    s=once(s,
'''              << " overwritten_serial=" << overwritten_serial
              << " root_call=" << c3x018_root_context_call''',
'''              << " overwritten_serial=" << overwritten_serial
              << " restore_shadow=" << int(restore_shadow)
              << " restore_bytes=" << int(restore_bytes)
              << " shadow_epoch_after=" << (it==c3x018_shadow.end()?0:it->second.epoch)
              << " shadow_serial_after=" << (it==c3x018_shadow.end()?0:it->second.writer_serial)
              << " native_depth_after=" << int(ptr->depth())
              << " native_bound_after=" << int(ptr->bound())
              << " native_value_after=" << int(ptr->value())
              << " native_eval_after=" << int(ptr->eval())
              << " shadow_native_match=" << int(it!=c3x018_shadow.end() &&
                       it->second.depth==int(ptr->depth()) &&
                       it->second.bound==int(ptr->bound()) &&
                       it->second.value==int(ptr->value()) &&
                       it->second.eval==int(ptr->eval()) &&
                       it->second.move==int(ptr->move()))
              << " root_call=" << c3x018_root_context_call''',
"REPAIR_RECEIPT")
    s=once(s,
'''      if (c3x018_p1_policy==2) {
          // Source write really occurred; only afterward repair old resident
          // TT bytes and the sidecar writer epoch/serial/payload identity.
          *this=c3x018_p1_before;
          c3x018_p1_after_reinstate(k,this);
      }''',
'''      if (c3x018_p1_policy>=2) {
          // Factorize native TTEntry bytes from shadow writer identity.
          // SHADOW_ONLY=3 deliberately creates a raw payload mismatch.
          const bool restore_bytes=c3x018_p1_policy!=3;
          const bool restore_shadow=c3x018_p1_policy!=4;
          if (restore_bytes) *this=c3x018_p1_before;
          c3x018_p1_after_reinstate(k,this,restore_shadow,restore_bytes);
      }''',
"FACTORIAL_AFTER")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/tt.cpp"
    orig=f.read_bytes();new=patch(orig.decode()).encode()
    f.write_bytes(new)
    result={"schema":"c3x019-TT-raw-ten-bytes-shadow-sidecar-two-factor-v1",
      "before_sha256":hashlib.sha256(orig).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "new_policies":["BYTES_ONLY","SHADOW_ONLY"],
      "negative_controls":["SKIP","REINSTATE","NONE"],
      "destructive_warning":"SHADOW_ONLY creates a deliberate metadata/TTEntry mismatch; it can satisfy V gate merely by the shadow address. Not a valid natural engine state.",
      "first_reader_actual_block_and_temporal_write_guard":"unchanged from prior P0P1",
      "TT_entry_physical_size_bytes":10}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("C3X019_RAW_TTENTRY_AND_WRITER_TICKET_ORTHOGONAL_SOURCE_PATCHED")
if __name__=="__main__":main()
