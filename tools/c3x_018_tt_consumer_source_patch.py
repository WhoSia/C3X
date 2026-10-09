#!/usr/bin/env python3
"""C3X 0.18 native SF16 TT-consumption trace: main/qsearch early-return events only.

Layer over frozen SF16 search.cpp. Observational sites mark realized TT cutoff,
not mere probe hit or proof of natural writer-to-reader mediation.
"""
import argparse
import hashlib
import json
from pathlib import Path

def once(s, old, new, tag):
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f"C3X018_TT_CONSUME_{tag}_ANCHOR_{count}")
    return s.replace(old, new, 1)

def patch(s):
    s = once(s, "namespace Stockfish {\n",
'''namespace Stockfish {

// C3X018 observational TT return sites. Logs are opt-in; never modify TT values.
static thread_local unsigned long long c3x018_consumed_seq = 0;
static constexpr unsigned long long c3x018_consumed_cap = 4096;
static inline void c3x018_report_tt_cutoff(const char* site, Key key, int ply,
                                            int depth, Value alpha, Value beta,
                                            Value value, int bound) {
    if (!std::getenv("C3X018_TT_CONSUME")) return;
    ++c3x018_consumed_seq;
    if (c3x018_consumed_seq > c3x018_consumed_cap) return;
    sync_cout << "info string c3x018_tt_consumed site=" << site
              << " seq=" << c3x018_consumed_seq
              << " key64=" << uint64_t(key) << " ply=" << ply
              << " depth=" << depth << " alpha=" << int(alpha)
              << " beta=" << int(beta) << " value=" << int(value)
              << " bound=" << bound << sync_endl;
}
''', "NAMESPACE")
    # Locate main-search unique early-return region by its precise original source block.
    needle = '''    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && !excludedMove
        && tte->depth() > depth - (tte->bound() == BOUND_EXACT)
        && ttValue != VALUE_NONE // Possible in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {'''
    s = once(s, needle, needle + '''
        c3x018_report_tt_cutoff("main", posKey, ss->ply, depth,
                                alpha, beta, ttValue, int(tte->bound()));''', "MAIN")
    needle2 = '''    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;'''
    s = once(s, needle2, '''    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        c3x018_report_tt_cutoff("qsearch", posKey, ss->ply, ttDepth,
                                alpha, beta, ttValue, int(tte->bound()));
        return ttValue;
    }''', "QSEARCH")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    before=f.read_bytes()
    after=patch(before.decode()).encode()
    f.write_bytes(after)
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
       "schema":"c3x018-actual-tt-early-cutoff-observer-v1",
       "before_sha256":hashlib.sha256(before).hexdigest(),
       "after_sha256":hashlib.sha256(after).hexdigest(),
       "activation":"C3X018_TT_CONSUME=1",
       "sites":["main TT early-cutoff","qsearch TT early-cutoff"],
       "scope_limits":["No writer generation or slot linkage in search.cpp",
                       "Main cutoff handler can later return a value different from ttValue; this event records condition reached, not necessarily exact returned score",
                       "Other TT uses (move sorting, evaluation, ProbCut, depth) NOT recorded",
                       "Event log capped at 4096; sequence counter beyond cap not emitted",
                       "No natural mediation established"]
    },indent=2)+"\n")
if __name__=="__main__":main()
