#!/usr/bin/env python3
"""Read-only SF16 main+qsearch TT.probe watcher for a single selected full64 key.

Log source TT probe independently of the downstream bound-value-eval
consumer. Root-call guard fixed from prior January observational source.
"""
import argparse,hashlib,json
from pathlib import Path

PREFIX=r"""
// C3X018 independent source probe witness, no TT outcome changes.
namespace {
unsigned long long c3x018_jan_probe_watch_count = 0;
void c3x018_jan_probe_watch(Key key, const TTEntry* entry, bool hit,
                            int ply, int depth, int alpha, int beta,
                            const char* site) {
    const char* key_env = std::getenv("C3X018_PROBE_WATCH_KEY64");
    const char* call_env = std::getenv("C3X018_PROBE_WATCH_ROOT_CALL");
    if (!key_env || !call_env) return;
    if (uint64_t(key) != std::strtoull(key_env,nullptr,10)
        || c3x018_root_context_call != std::strtoull(call_env,nullptr,10))
        return;
    const auto ordinal = ++c3x018_jan_probe_watch_count;
    if (ordinal > 64) {
        if (ordinal == 65)
            sync_cout << "info string c3x018_jan_probe_watch kind=censored"
                      << " probe_count=" << ordinal << sync_endl;
        return;
    }
    auto slot = entry - TT.first_entry(key);
    sync_cout << "info string c3x018_jan_probe_watch kind=probe"
              << " ordinal=" << ordinal << " site=" << site
              << " key64=" << uint64_t(key)
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << " ply=" << ply << " depth=" << depth
              << " alpha=" << alpha << " beta=" << beta
              << " tt_hit=" << int(hit)
              << " tt_slot=" << int(slot)
              << " raw_bound=" << (hit ? int(entry->bound()) : -1)
              << " raw_depth=" << (hit ? int(entry->depth()) : -1)
              << " raw_value=" << (hit ? int(entry->value()) : -32001)
              << " raw_eval=" << (hit ? int(entry->eval()) : -32001)
              << sync_endl;
}
} // C3X018_JAN_PROBE_WATCH
"""
def patch(s):
    anchor="    tte = TT.probe(posKey, ss->ttHit);"
    if s.count(anchor)!=2:raise RuntimeError("C3X018_JAN_PROBE_SOURCE_TWO_SITES_COUNT_"+str(s.count(anchor)))
    ns="namespace Stockfish {"
    if s.count(ns)!=1:raise RuntimeError("C3X018_JAN_PROBE_NAMESPACE")
    s=s.replace(ns,ns+"\n"+PREFIX,1)
    part=s.split(anchor)
    # Engine source order main search, then qsearch.
    return (part[0]+anchor+
       '\n    c3x018_jan_probe_watch(posKey,tte,ss->ttHit,ss->ply,depth,int(alpha),int(beta),"main");'
       +part[1]+anchor+
       '\n    c3x018_jan_probe_watch(posKey,tte,ss->ttHit,ss->ply,depth,int(alpha),int(beta),"qsearch");'
       +part[2])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    old=f.read_bytes();new=patch(old.decode()).encode()
    f.write_bytes(new)
    receipt={"schema":"c3x018-January-passive-full64-key-root-call-TT-probe-watcher-v1",
      "source_before_sha256":hashlib.sha256(old).hexdigest(),
      "source_after_sha256":hashlib.sha256(new).hexdigest(),
      "source_sites":["main TT.probe","qsearch TT.probe"],
      "watch_env":["C3X018_PROBE_WATCH_KEY64","C3X018_PROBE_WATCH_ROOT_CALL"],
      "per_cold_process_event_cap":64,
      "semantic_boundary":["TT.probe hit is Stockfish native TT key16 tag match, not independent full64 last writer proof",
         "Physical writer lineage and actual blocked eval value remain separate sources",
         "No probe at a root call is not direct evidence the position was never evaluated",
         "No mutation to alpha beta, TT record, score evaluation or move sorting"]}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2)+"\n")
    print("C3X018_JAN_SOURCE_TT_PROBE_WATCHER_INSTALLED")
if __name__=="__main__":main()
