#!/usr/bin/env python3
"""Reader TT-probe shadow epoch and accepted writer serial at a source watch.

Runs after c3x_018_jan_original_key_TT_probe_watch_overlay.py.
TT shadow is independent of Stockfish 10-byte TTEntry, protected by mutex.
No changes to actual table entry, probe, search or stored score.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,name):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_PROBE_EPOCH_{name}_COUNT_{n}")
 return s.replace(a,b,1)
def patch_header(s):
 return one(s,"extern TranspositionTable TT;",
   """void c3x018_read_source_writer_epoch(Key key, const TTEntry* ptr,
    uint64_t& epoch, uint64_t& serial, uint64_t& writer_key, int& writer_depth);
extern TranspositionTable TT;""","HEADER")
def patch_tt(s):
 function=r"""
// Passive full64 writer ticket snapshot, never modifies TT or search.
void c3x018_read_source_writer_epoch(Key key, const TTEntry* ptr,
    uint64_t& epoch, uint64_t& serial, uint64_t& writer_key, int& writer_depth) {
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    const auto it = c3x018_shadow.find(ptr);
    epoch=0;serial=0;writer_key=0;writer_depth=-1;
    if (it!=c3x018_shadow.end()) {
        epoch=it->second.epoch;
        serial=it->second.writer_serial;
        writer_key=it->second.key64;
        writer_depth=it->second.depth;
    }
}
"""
 return one(s,"} // namespace Stockfish",function+"\n} // namespace Stockfish","TT_PUBLIC_SNAPSHOT")
def patch_search(s):
 s=one(s,'    auto slot = entry - TT.first_entry(key);',
  '''    uint64_t shadow_epoch=0, shadow_writer_serial=0, shadow_writer_key=0;
    int shadow_writer_depth=-1;
    c3x018_read_source_writer_epoch(key,entry,
        shadow_epoch,shadow_writer_serial,shadow_writer_key,shadow_writer_depth);
    auto slot = entry - TT.first_entry(key);''',"CALL_SOURCE_SHADOW")
 return one(s,'              << " tt_hit=" << int(hit)',
  '''              << " shadow_epoch=" << shadow_epoch
              << " shadow_writer_serial=" << shadow_writer_serial
              << " shadow_writer_key64=" << shadow_writer_key
              << " shadow_writer_depth=" << shadow_writer_depth
              << " shadow_full64_match=" << int(shadow_writer_key==uint64_t(key))
              << " tt_hit=" << int(hit)''',"LOG_SOURCE_SHADOW")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 changed={}
 for name,fn in (("tt.h",patch_header),("tt.cpp",patch_tt),("search.cpp",patch_search)):
  path=Path(a.source)/"src"/name
  old=path.read_bytes();new=fn(old.decode()).encode()
  path.write_bytes(new)
  changed[name]={"before_sha256":hashlib.sha256(old).hexdigest(),
                 "after_sha256":hashlib.sha256(new).hexdigest()}
 result={"schema":"c3x018-January-source-TT-probe-shadow-writer-epoch-and-new-version-v1",
         "changed":changed,"read_only":True,
         "logged":["shadow_epoch","shadow_writer_serial","shadow_writer_key64","shadow_writer_depth","shadow_full64_match"],
         "limits":["This reader side shadow snapshot is from current cold process only",
                   "An epoch change at the same key and slot means accepted TTEntry payload rewrite",
                   "Raw ttHit remains key16 table tag, full64 match requires separate shadow key check",
                   "No game-position transport or natural TT mediation guaranteed"]}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(result,indent=2)+"\n")
 print("C3X018_JANUARY_TT_PROBE_PHYSICAL_LAST_WRITER_EPOCH_WITNESS_READY")
if __name__=="__main__":main()
