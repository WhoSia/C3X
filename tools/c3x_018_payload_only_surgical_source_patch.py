#!/usr/bin/env python3
"""SF16 C3X 0.18 payload-only TT write ablation layered over epoch witness.

Base epoch patch stays immutable and reproducible. P skips accepted TT payload
(key/depth/bound/value/eval) while allowing source-original move16 update.
It can create a hybrid TTEntry and is explicitly NOT a natural TT writer.
"""
import argparse
import hashlib
import json
from pathlib import Path

def once(s,a,b,label):
    n=s.count(a)
    if n!=1: raise RuntimeError(f"C3X018_PAYLOAD_ONLY_{label}_ANCHOR_COUNT_{n}")
    return s.replace(a,b,1)

def patch(s):
    s=once(s,
       'if ((std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0)',
       'if ((std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0 ||\n         std::strcmp(mode, "P") == 0)',"OP_MODE")
    s=once(s,
       'c3x018_event("writer_block", "save", key, slot, next, uint64_t(key),',
       'c3x018_event("writer_block", std::strcmp(mode, "P") == 0 ? "payload" : "save",\n                     key, slot, next, uint64_t(key),',"EVENT_SITE")
    s=once(s,
       '''  if (c3x018_writer_block(k, this, c3x018_would_payload_write))
      return;
  // Preserve any existing move''',
       '''  const bool c3x018_block_payload = c3x018_writer_block(
      k, this, c3x018_would_payload_write);
  if (c3x018_block_payload && std::strcmp(c3x018_mode(), "P") != 0)
      return;
  // Preserve any existing move''',"KEEP_MOVE16")
    s=once(s,
       '''  if (   b == BOUND_EXACT
      || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4)
  {''',
       '''  if (  !c3x018_block_payload
      && (b == BOUND_EXACT
          || (uint16_t)k != key16
          || d - DEPTH_OFFSET + 2 * pv > depth8 - 4))
  {''',"SKIP_PAYLOAD")
    return s

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",required=True)
    parser.add_argument("--out-manifest",required=True)
    args=parser.parse_args()
    f=Path(args.source)/"src/tt.cpp"
    before=f.read_bytes()
    after=patch(before.decode()).encode()
    f.write_bytes(after)
    out=Path(args.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
       "schema":"c3x018-sf16-payload-only-write-ablation-overlay-v1",
       "source_before_sha256":hashlib.sha256(before).hexdigest(),
       "source_after_sha256":hashlib.sha256(after).hexdigest(),
       "precondition":"must be applied after c3x_018_physical_epoch_lineage_patch.py",
       "mode":"P: allow move16 update, inhibit TT payload fields for matched source writer",
       "scope_limits":[
          "P can create hybrid entry where move16 and depth/value/key16 refer to different writes",
          "W original whole-save suppression is untouched by this overlay",
          "P is a surgical source intervention, not a natural mediator",
          "Slot epoch, key, budget match remain path-dependent after intervention",
          "Use single-thread cold native with immutable original source control"]
    },indent=2)+"\n")
    print("C3X018_SF16_PAYLOAD_ONLY_OVERLAY_APPLIED")

if __name__=="__main__":main()
