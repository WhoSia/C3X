#!/usr/bin/env python3
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "upstream/stockfish-lock.json").read_text())

HEADER = r'''/*
  C3X G9.4-P12 TT-read intervention surface.
  This file is added to an exact Stockfish upstream checkout by the
  deterministic C3X patch materializer.
*/
#ifndef C3X_TTREAD_H_INCLUDED
#define C3X_TTREAD_H_INCLUDED

#include <cstdint>

namespace Stockfish::Search {

enum class C3XTTReadMode { NATIVE, SHAM, MASKED };
enum class C3XTTReadSite { MAIN, SUCCESSOR_VERIFY, QSEARCH };

struct C3XTTReadStats {
    std::uint64_t probesMain = 0, probesSuccessor = 0, probesQsearch = 0;
    std::uint64_t rawHitsMain = 0, rawHitsSuccessor = 0, rawHitsQsearch = 0;
    std::uint64_t useMainEval = 0, useMainValue = 0, useMainCutoffGate = 0;
    std::uint64_t useSuccessorValue = 0;
    std::uint64_t useQsearchEval = 0, useQsearchValue = 0, useQsearchCutoff = 0;

    C3XTTReadStats& operator+=(const C3XTTReadStats& o) {
        probesMain += o.probesMain;
        probesSuccessor += o.probesSuccessor;
        probesQsearch += o.probesQsearch;
        rawHitsMain += o.rawHitsMain;
        rawHitsSuccessor += o.rawHitsSuccessor;
        rawHitsQsearch += o.rawHitsQsearch;
        useMainEval += o.useMainEval;
        useMainValue += o.useMainValue;
        useMainCutoffGate += o.useMainCutoffGate;
        useSuccessorValue += o.useSuccessorValue;
        useQsearchEval += o.useQsearchEval;
        useQsearchValue += o.useQsearchValue;
        useQsearchCutoff += o.useQsearchCutoff;
        return *this;
    }

    std::uint64_t semantic_uses() const {
        return useMainEval + useMainValue + useMainCutoffGate + useSuccessorValue
             + useQsearchEval + useQsearchValue + useQsearchCutoff;
    }

    int breadth() const {
        int b = 0;
        if (useMainEval || useQsearchEval) ++b;
        if (useMainValue || useSuccessorValue || useQsearchValue) ++b;
        if (useMainCutoffGate || useQsearchCutoff) ++b;
        return b;
    }
};

struct C3XTTReadState {
    C3XTTReadMode mode = C3XTTReadMode::NATIVE;
    bool telemetry = false;
    C3XTTReadStats stats{};

    void reset(C3XTTReadMode m, bool t) {
        mode = m;
        telemetry = t;
        stats = {};
    }

    bool masked() const { return mode == C3XTTReadMode::MASKED; }

    void observe(C3XTTReadSite site, bool hit) {
        if (!telemetry)
            return;

        switch (site)
        {
        case C3XTTReadSite::MAIN:
            ++stats.probesMain;
            if (hit) ++stats.rawHitsMain;
            break;
        case C3XTTReadSite::SUCCESSOR_VERIFY:
            ++stats.probesSuccessor;
            if (hit) ++stats.rawHitsSuccessor;
            break;
        case C3XTTReadSite::QSEARCH:
            ++stats.probesQsearch;
            if (hit) ++stats.rawHitsQsearch;
            break;
        }
    }
};

inline const char* c3x_ttread_mode_name(C3XTTReadMode m) {
    switch (m)
    {
    case C3XTTReadMode::NATIVE: return "NATIVE";
    case C3XTTReadMode::SHAM: return "SHAM";
    case C3XTTReadMode::MASKED: return "MASKED";
    }
    return "UNKNOWN";
}

}  // namespace Stockfish::Search

#endif
'''

def run(cwd, *args):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 exact anchor, found {n}")
    return text.replace(old, new, 1)

def replace_nth(text, old, new, nth, label):
    starts = []
    pos = 0
    while True:
        i = text.find(old, pos)
        if i < 0:
            break
        starts.append(i)
        pos = i + len(old)
    if len(starts) <= nth:
        raise RuntimeError(f"{label}: expected occurrence {nth}, found {len(starts)}")
    i = starts[nth]
    return text[:i] + new + text[i+len(old):]

def verify_checkout(sf, target):
    spec = LOCK["targets"][target]
    head = run(sf, "git", "rev-parse", "HEAD")
    if head != spec["commit"]:
        raise RuntimeError(f"HEAD mismatch: {head} != {spec['commit']}")
    for path, expected in spec["blobs"].items():
        actual = run(sf, "git", "rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise RuntimeError(f"blob mismatch {path}: {actual} != {expected}")
    if (sf / "src/c3x_ttread.h").exists():
        raise RuntimeError("src/c3x_ttread.h already exists; refusing non-pristine materialization")

def patch_search_h(sf):
    p = sf / "src/search.h"
    t = p.read_text()
    t = replace_once(
        t,
        '#include "history.h"\n#include "misc.h"',
        '#include "c3x_ttread.h"\n#include "history.h"\n#include "misc.h"',
        "search.h include"
    )
    t = replace_once(
        t,
        '    TimePoint elapsed() const;\n\n    Value evaluate(const Position&);',
        '    TimePoint elapsed() const;\n\n    C3XTTReadState c3xTt;\n\n    Value evaluate(const Position&);',
        "search.h Worker state"
    )
    p.write_text(t)

def patch_engine_cpp(sf):
    p = sf / "src/engine.cpp"
    t = p.read_text()
    t = replace_once(
        t,
        '    options.add("UCI_ShowWDL", Option(false));',
        '    options.add("UCI_ShowWDL", Option(false));\n\n'
        '    options.add("C3X_TTReadMode", Option("NATIVE var SHAM var MASKED", "NATIVE"));\n'
        '    options.add("C3X_Telemetry", Option(false));',
        "engine.cpp C3X options"
    )
    p.write_text(t)

def patch_search_cpp(sf):
    p = sf / "src/search.cpp"
    t = p.read_text()

    t = replace_once(
        t,
        'void Search::Worker::start_searching() {\n\n    accumulatorStack.reset();',
        'void Search::Worker::start_searching() {\n\n'
        '    const C3XTTReadMode c3xMode = options["C3X_TTReadMode"] == "MASKED"\n'
        '                                      ? C3XTTReadMode::MASKED\n'
        '                                  : options["C3X_TTReadMode"] == "SHAM"\n'
        '                                      ? C3XTTReadMode::SHAM\n'
        '                                      : C3XTTReadMode::NATIVE;\n'
        '    c3xTt.reset(c3xMode, int(options["C3X_Telemetry"]) != 0);\n\n'
        '    accumulatorStack.reset();',
        "start_searching configure"
    )

    probe = '    auto [ttHit, ttData, ttWriter] = tt.probe(posKey);'
    main_probe = probe + '\n'
    main_probe += '    c3xTt.observe(C3XTTReadSite::MAIN, ttHit);\n'
    main_probe += '    if (c3xTt.masked() && ttHit)\n'
    main_probe += '    {\n'
    main_probe += '        ttHit  = false;\n'
    main_probe += '        ttData = TTData(Move::none(), VALUE_NONE, VALUE_NONE, DEPTH_NONE, BOUND_NONE, false);\n'
    main_probe += '    }'
    t = replace_nth(t, probe, main_probe, 0, "main TT probe")

    q_probe = probe + '\n'
    q_probe += '    c3xTt.observe(C3XTTReadSite::QSEARCH, ttHit);\n'
    q_probe += '    if (c3xTt.masked() && ttHit)\n'
    q_probe += '    {\n'
    q_probe += '        ttHit  = false;\n'
    q_probe += '        ttData = TTData(Move::none(), VALUE_NONE, VALUE_NONE, DEPTH_NONE, BOUND_NONE, false);\n'
    q_probe += '    }'
    t = replace_nth(t, probe, q_probe, 1, "qsearch TT probe")

    succ = '                auto [ttHitNext, ttDataNext, ttWriterNext] = tt.probe(nextPosKey);'
    succ_new = succ + '\n'
    succ_new += '                c3xTt.observe(C3XTTReadSite::SUCCESSOR_VERIFY, ttHitNext);\n'
    succ_new += '                if (c3xTt.masked() && ttHitNext)\n'
    succ_new += '                {\n'
    succ_new += '                    ttHitNext  = false;\n'
    succ_new += '                    ttDataNext = TTData(Move::none(), VALUE_NONE, VALUE_NONE, DEPTH_NONE, BOUND_NONE, false);\n'
    succ_new += '                }'
    t = replace_once(t, succ, succ_new, "successor TT probe")

    # Main TT eval availability becomes realized use only when consumed as a valid TT eval.
    eval_anchor = '        unadjustedStaticEval = ttData.eval;\n        if (!is_valid(unadjustedStaticEval))'
    eval_main = '        unadjustedStaticEval = ttData.eval;\n'
    eval_main += '        if (c3xTt.telemetry && is_valid(unadjustedStaticEval))\n'
    eval_main += '            ++c3xTt.stats.useMainEval;\n'
    eval_main += '        if (!is_valid(unadjustedStaticEval))'
    t = replace_nth(t, eval_anchor, eval_main, 0, "main eval use")

    eval_q = '        unadjustedStaticEval = ttData.eval;\n\n'
    eval_q += '            if (c3xTt.telemetry && is_valid(unadjustedStaticEval))\n'
    eval_q += '                ++c3xTt.stats.useQsearchEval;\n\n'
    eval_q += '            if (!is_valid(unadjustedStaticEval))'
    q_old = '            unadjustedStaticEval = ttData.eval;\n\n            if (!is_valid(unadjustedStaticEval))'
    t = replace_once(t, q_old, '            ' + eval_q, "qsearch eval use")

    main_value_old = '''        if (is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
            eval = ttData.value;'''
    main_value_new = '''        if (is_valid(ttData.value)
            && (ttData.bound & (ttData.value > eval ? BOUND_LOWER : BOUND_UPPER)))
        {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useMainValue;
            eval = ttData.value;
        }'''
    t = replace_once(t, main_value_old, main_value_new, "main value use")

    q_value_old = '''            if (is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
                bestValue = ttData.value;'''
    q_value_new = '''            if (is_valid(ttData.value) && !is_decisive(ttData.value)
                && (ttData.bound & (ttData.value > bestValue ? BOUND_LOWER : BOUND_UPPER)))
            {
                if (c3xTt.telemetry)
                    ++c3xTt.stats.useQsearchValue;
                bestValue = ttData.value;
            }'''
    t = replace_once(t, q_value_old, q_value_new, "qsearch value use")

    cutoff_open_old = '''    {
        // If ttMove is quiet, update move sorting heuristics on TT hit'''
    cutoff_open_new = '''    {
        if (c3xTt.telemetry)
            ++c3xTt.stats.useMainCutoffGate;

        // If ttMove is quiet, update move sorting heuristics on TT hit'''
    # This anchor occurs at the main TT-cutoff block exactly once in both targets.
    t = replace_once(t, cutoff_open_old, cutoff_open_new, "main cutoff gate")

    succ_use_old = '''                // Check that the ttValue after the tt move would also trigger a cutoff
                if (!is_valid(ttDataNext.value))'''
    succ_use_new = '''                // Check that the ttValue after the tt move would also trigger a cutoff
                if (c3xTt.telemetry && ttHitNext && is_valid(ttDataNext.value))
                    ++c3xTt.stats.useSuccessorValue;
                if (!is_valid(ttDataNext.value))'''
    t = replace_once(t, succ_use_old, succ_use_new, "successor semantic use")

    q_cut_old = '''    if (!PvNode && ttData.depth >= DEPTH_QS'''
    # We insert only a marker before the existing qsearch cutoff and then brace the return.
    q_region_start = t.find(q_cut_old)
    if q_region_start < 0:
        raise RuntimeError("qsearch cutoff start not found")
    q_return = '        return ttData.value;'
    q_return_pos = t.find(q_return, q_region_start)
    if q_return_pos < 0:
        raise RuntimeError("qsearch cutoff return not found")
    t = t[:q_return_pos] + '''    {
            if (c3xTt.telemetry)
                ++c3xTt.stats.useQsearchCutoff;
            return ttData.value;
        }''' + t[q_return_pos + len(q_return):]

    telemetry_anchor = '    // When playing in \'nodes as time\' mode, subtract the searched nodes from'
    if telemetry_anchor not in t:
        raise RuntimeError("post-search telemetry anchor not found")
    telemetry = '''    if (c3xTt.telemetry)
    {
        C3XTTReadStats total{};
        for (auto&& th : threads)
            total += th->worker->c3xTt.stats;

        sync_cout << "info string c3x_ttread_v1"
                  << " mode=" << c3x_ttread_mode_name(c3xTt.mode)
                  << " probes_main=" << total.probesMain
                  << " raw_hits_main=" << total.rawHitsMain
                  << " probes_successor=" << total.probesSuccessor
                  << " raw_hits_successor=" << total.rawHitsSuccessor
                  << " probes_qsearch=" << total.probesQsearch
                  << " raw_hits_qsearch=" << total.rawHitsQsearch
                  << " use_main_eval=" << total.useMainEval
                  << " use_main_value=" << total.useMainValue
                  << " use_main_cutoff_gate=" << total.useMainCutoffGate
                  << " use_successor_value=" << total.useSuccessorValue
                  << " use_qsearch_eval=" << total.useQsearchEval
                  << " use_qsearch_value=" << total.useQsearchValue
                  << " use_qsearch_cutoff=" << total.useQsearchCutoff
                  << " semantic_uses=" << total.semantic_uses()
                  << " breadth=" << total.breadth()
                  << sync_endl;
    }

'''
    t = t.replace(telemetry_anchor, telemetry + telemetry_anchor, 1)
    p.write_text(t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stockfish", required=True)
    ap.add_argument("--target", required=True, choices=LOCK["targets"].keys())
    args = ap.parse_args()
    sf = pathlib.Path(args.stockfish).resolve()

    verify_checkout(sf, args.target)
    (sf / "src/c3x_ttread.h").write_text(HEADER)
    patch_search_h(sf)
    patch_engine_cpp(sf)
    patch_search_cpp(sf)

    print(f"materialized target={args.target} commit={LOCK['targets'][args.target]['commit']}")
    print(run(sf, "git", "diff", "--stat"))

if __name__ == "__main__":
    main()
