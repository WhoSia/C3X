#!/usr/bin/env python3
"""C3X S4G: same native C++ binary merges source invocation-ID logging and
bounded TT-hit signal masking, with independent negative-key sham controls.

Enhances S4E read-only logger by logging ROOT candidates only immediately
after a completed main-search target-key child invocation. A single source
binary is compiled for sham, 0, 1, 2, and 10000 target-key hit-mask limits.
Target keys were frozen from prior original S4B before observing S4G.
"""
import argparse,hashlib
from pathlib import Path
from c3x_030_p11s4e_invocation_patch import apply as s4e_patch

NS_ADD='''static std::atomic<unsigned> c3x_g_matching_hits{0};
static thread_local unsigned long long c3x_e_last_target[MAX_PLY + 8] = {};'''
PROBE_MASK='''    // C3X S4G: same compiled binary, literal source TT hit signal intervention.
    static const unsigned long long c3x_g_mask_key = []() -> unsigned long long {
        const char* s = std::getenv("C3X_S4G_MASK_KEY");
        return s ? std::strtoull(s, nullptr, 10) : 0ULL;
    }();
    static const unsigned c3x_g_mask_limit = []() -> unsigned {
        const char* s = std::getenv("C3X_S4G_MASK_LIMIT");
        return s ? static_cast<unsigned>(std::strtoul(s, nullptr, 10)) : 0U;
    }();
    if (c3x_g_mask_key && ss->ply == 1 && ss->ttHit
        && static_cast<unsigned long long>(posKey) == c3x_g_mask_key)
    {
        const auto ordinal = c3x_g_matching_hits.fetch_add(1, std::memory_order_relaxed);
        if (ordinal < c3x_g_mask_limit)
        {
            if (ordinal < 8)
                std::cerr << "C3X_S4G_MASK ordinal=" << ordinal
                          << " key=" << posKey << " ply=" << ss->ply
                          << " id=" << c3x_e_scope.id
                          << " parent=" << c3x_e_scope.parent_id
                          << " hit_before=1 hit_after=0" << std::endl;
            ss->ttHit = false;
        }
    }
'''
def sha(b):return hashlib.sha256(b).hexdigest()
def patch(original):
    modified=s4e_patch(original)
    changes=[
     ("static thread_local unsigned c3x_e_logs = 0;",
      "static thread_local unsigned c3x_e_logs = 0;\n"+NS_ADD),
     ("            c3x_e_last_child[ply] = id;",
      "            c3x_e_last_child[ply] = id;\n            c3x_e_last_target[ply] = interested ? id : 0;"),
     ('    if (c3x_e_target && ss->ply == 1\n',
      PROBE_MASK+'    if (c3x_e_target && ss->ply == 1\n'),
     ('          if (c3x_e_target && c3x_e_logs++ < 240)',
      '          if (c3x_e_target && c3x_e_last_child[ss->ply + 1] != 0\n'
      '              && c3x_e_last_child[ss->ply + 1] == c3x_e_last_target[ss->ply + 1]\n'
      '              && c3x_e_logs++ < 240)')]
    for old,new in changes:
        if modified.count(old)!=1:
            raise ValueError("S4G_HOLD_UNIQUE_OBSERVATION_SOURCE_PATCH:"+str(modified.count(old)))
        modified=modified.replace(old,new,1)
    if modified.count('C3X_S4G_MASK ordinal=')!=1:
        raise ValueError("S4G_HOLD_PHYSICAL_SOURCE_EVENT_ABSENT")
    return modified

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    b=Path(args.source).read_bytes()
    x=patch(b.decode("utf8")).encode("utf8")
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(x)
    print("S4G_ORIGINAL_SOURCE_SHA",sha(b),"S4G_MERGED_SOURCE_SHA",sha(x))
if __name__=="__main__":main()
