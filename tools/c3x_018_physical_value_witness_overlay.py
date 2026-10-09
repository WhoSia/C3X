#!/usr/bin/env python3
"""Observer-only Stockfish 16 TT physical last writer -> V consumer payload proof.

Apply after C3X018 physical epoch and V evaluator overlays. No search mutation.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError("C3X018_VALUE_WITNESS_"+label+"_"+str(n))
 return s.replace(a,b,1)
def patch_header(s):
 return one(s,"extern TranspositionTable TT;",
 """bool c3x018_verify_V_payload(Key key, const TTEntry* slot, int effective,
                                   int ply, int depth, int alpha, int beta, const char* site);
extern TranspositionTable TT;""","HEADER")
def patch_tt(s):
 s=one(s,"    uint64_t key64 = 0;\n};",
   "    uint64_t key64 = 0;\n    uint64_t writer_serial = 0;\n    int value=0, eval=0, depth=0, bound=0, move=0;\n};","SHADOW_STRUCT")
 s=one(s,"uint64_t c3x018_event_seq = 0;",
   "uint64_t c3x018_event_seq = 0;\nuint64_t c3x018_write_serial = 0;","WRITE_SERIAL")
 s=one(s,"    record.key64 = uint64_t(key);",
   """    record.key64 = uint64_t(key);
    record.writer_serial = ++c3x018_write_serial;
    record.value = int(slot->value());
    record.eval = int(slot->eval());
    record.depth = int(slot->depth());
    record.bound = int(slot->bound());
    record.move = int(slot->move());
    if (c3x018_target(key,slot,record.epoch))
        sync_cout << "info string c3x018_value_witness kind=writer"
                  << " key64=" << record.key64
                  << " slot=" << c3x018_slot(key,slot)
                  << " epoch=" << record.epoch
                  << " writer_serial=" << record.writer_serial
                  << " raw_value=" << record.value
                  << " raw_depth=" << record.depth
                  << " raw_bound=" << record.bound
                  << " raw_eval=" << record.eval
                  << " raw_move=" << record.move << sync_endl;""","PAYLOAD_CAPTURE")
 s=one(s,"      c3x018_event_seq = 0;",
   "      c3x018_event_seq = 0;\n      c3x018_write_serial = 0;","RESET")
 fn="""
bool c3x018_verify_V_payload(Key key, const TTEntry* slot, int effective,
                                   int ply, int depth, int alpha, int beta, const char* site) {
    if (!c3x018_active()) return true;
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    const auto it = c3x018_shadow.find(slot);
    const bool known = it != c3x018_shadow.end();
    const C3X018Writer w = known ? it->second : C3X018Writer{};
    if (!c3x018_target(key,slot,w.epoch)) return true;
    const bool matched = known && w.key64 == uint64_t(key)
       && w.value == int(slot->value())
       && w.eval == int(slot->eval())
       && w.depth == int(slot->depth())
       && w.bound == int(slot->bound())
       && w.move == int(slot->move());
    sync_cout << "info string c3x018_value_witness kind=reader"
              << " site=" << site
              << " key64=" << uint64_t(key)
              << " writer_key64=" << w.key64
              << " slot=" << c3x018_slot(key,slot)
              << " epoch=" << w.epoch
              << " writer_serial=" << w.writer_serial
              << " known=" << int(known)
              << " matched=" << int(matched)
              << " raw_value=" << int(slot->value())
              << " raw_depth=" << int(slot->depth())
              << " raw_bound=" << int(slot->bound())
              << " raw_eval=" << int(slot->eval())
              << " raw_move=" << int(slot->move())
              << " effective_value=" << effective
              << " ply=" << ply << " depth=" << depth
              << " alpha=" << alpha << " beta=" << beta << sync_endl;
    return true; // instrumentation never changes a search condition
}
"""
 return one(s,"} // namespace Stockfish",fn+"\n} // namespace Stockfish","NAMESPACE")
def patch_search(s):
 s=one(s,
 '&& (tte->bound() & (ttValue > eval ? BOUND_LOWER : BOUND_UPPER))\n            && !(std::getenv("C3X018_TT_MODE")',
 '&& (tte->bound() & (ttValue > eval ? BOUND_LOWER : BOUND_UPPER))\n            && c3x018_verify_V_payload(posKey,tte,int(ttValue),ss->ply,depth,int(alpha),int(beta),"main")\n            && !(std::getenv("C3X018_TT_MODE")',"MAIN")
 s=one(s,
 '&& (tte->bound() & (ttValue > bestValue ? BOUND_LOWER : BOUND_UPPER))\n                && !(std::getenv("C3X018_TT_MODE")',
 '&& (tte->bound() & (ttValue > bestValue ? BOUND_LOWER : BOUND_UPPER))\n                && c3x018_verify_V_payload(posKey,tte,int(ttValue),ss->ply,ttDepth,int(alpha),int(beta),"qsearch")\n                && !(std::getenv("C3X018_TT_MODE")',"QSEARCH")
 return s
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args();root=Path(a.source)/"src";modified={}
 for name,fn in (("tt.h",patch_header),("tt.cpp",patch_tt),("search.cpp",patch_search)):
  f=root/name;before=f.read_bytes();after=fn(before.decode()).encode()
  f.write_bytes(after);modified[name]={"before":hashlib.sha256(before).hexdigest(),"after":hashlib.sha256(after).hexdigest()}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps({"schema":"c3x018-physical-payload-snapshot-V-consumer-witness-v1",
 "files":modified,"event":"c3x018_value_witness",
 "invariants":["write serialization within one cold process","physical slot and full64 writer key match","source raw TT payload fields equal at actual reader","writer ID is nonzero and globally monotonically assigned per accepted save"],
 "limits":["same payload is not proof of unique mediation","only actual bound-value-as-evaluation branches covered",
 "single-thread and standalone FEN; no cross-process writer event identity"]},indent=2)+"\n")
 print("C3X018_PHYSICAL_TT_VALUE_WITNESS_PATCH_APPLIED")
if __name__=="__main__":main()
