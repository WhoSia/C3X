#!/usr/bin/env python3
"""TT cached evaluation and TT bound-value override competing consumers (E/V).

Layer after physical_epoch_lineage_patch on frozen SF16. E recomputes static
eval rather than reusing targeted TT.eval(); V ignores targeted TT.value()
only when used as a *better positional evaluation*, not at cutoff.
Never mutate TT source table directly.
"""
import argparse,hashlib,json
from pathlib import Path
def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"C3X018_TT_EVAL_{label}_ANCHOR_{n}")
    return s.replace(old,new,1)

def patch_tt(s):
    old='''    const bool block = (std::strcmp(mode, "R") == 0 ||
                        std::strcmp(mode, "WR") == 0)
                   && exact_key && c3x018_target(key, slot, epoch);'''
    new='''    const bool block = ((std::strcmp(mode, "R") == 0 ||
                         std::strcmp(mode, "WR") == 0)
                        || (std::strcmp(mode, "E") == 0
                            && std::strcmp(site, "tt_cached_eval") == 0)
                        || (std::strcmp(mode, "V") == 0
                            && std::strcmp(site, "tt_value_eval_override") == 0))
                   && exact_key && c3x018_target(key, slot, epoch);
    // E/V read gates only emit contact on a realized targeted source match.
    if ((std::strcmp(mode, "E") == 0 &&
         std::strcmp(site, "tt_cached_eval") == 0 && !block) ||
        (std::strcmp(mode, "V") == 0 &&
         std::strcmp(site, "tt_value_eval_override") == 0 && !block))
        return false;'''
    return once(s,old,new,"TT_GATE")

def patch_search(s):
    # Cached TT evaluation reuse: keep bound and value unchanged; independent
    # evaluate(pos) may yield same numerical value as the TT cache.
    s=once(s,'ss->staticEval = eval = tte->eval();',
      '''ss->staticEval = eval =
            (std::getenv("C3X018_TT_MODE") &&
             std::strcmp(std::getenv("C3X018_TT_MODE"), "E") == 0 &&
             tte->eval() != VALUE_NONE &&
             c3x018_consumer_gate("tt_cached_eval", posKey, tte, ss->ply,
                                  depth, int(alpha), int(beta), int(tte->eval())))
                ? evaluate(pos) : tte->eval();''',"MAIN_E")
    s=once(s,'if ((ss->staticEval = bestValue = tte->eval()) == VALUE_NONE)',
      '''if ((ss->staticEval = bestValue =
              (std::getenv("C3X018_TT_MODE") &&
               std::strcmp(std::getenv("C3X018_TT_MODE"), "E") == 0 &&
               tte->eval() != VALUE_NONE &&
               c3x018_consumer_gate("tt_cached_eval", posKey, tte, ss->ply,
                                    ttDepth, int(alpha), int(beta), int(tte->eval())))
                ? evaluate(pos) : tte->eval()) == VALUE_NONE)''',"QS_E")
    s=once(s,
       '''        if (    ttValue != VALUE_NONE
            && (tte->bound() & (ttValue > eval ? BOUND_LOWER : BOUND_UPPER)))
            eval = ttValue;''',
       '''        if (    ttValue != VALUE_NONE
            && (tte->bound() & (ttValue > eval ? BOUND_LOWER : BOUND_UPPER))
            && !(std::getenv("C3X018_TT_MODE") &&
                 std::strcmp(std::getenv("C3X018_TT_MODE"), "V") == 0 &&
                 c3x018_consumer_gate("tt_value_eval_override", posKey, tte,
                                      ss->ply, depth, int(alpha), int(beta), int(ttValue))))
            eval = ttValue;''',"MAIN_V")
    s=once(s,
       '''            if (    ttValue != VALUE_NONE
                && (tte->bound() & (ttValue > bestValue ? BOUND_LOWER : BOUND_UPPER)))
                bestValue = ttValue;''',
       '''            if (    ttValue != VALUE_NONE
                && (tte->bound() & (ttValue > bestValue ? BOUND_LOWER : BOUND_UPPER))
                && !(std::getenv("C3X018_TT_MODE") &&
                     std::strcmp(std::getenv("C3X018_TT_MODE"), "V") == 0 &&
                     c3x018_consumer_gate("tt_value_eval_override", posKey, tte,
                                          ss->ply, ttDepth, int(alpha), int(beta), int(ttValue))))
                bestValue = ttValue;''',"QS_V")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();root=Path(a.source)/"src";changed={}
    for n,fn in (("tt.cpp",patch_tt),("search.cpp",patch_search)):
        file=root/n;before=file.read_bytes()
        after=fn(before.decode()).encode();file.write_bytes(after)
        changed[n]={"before":hashlib.sha256(before).hexdigest(),
                    "after":hashlib.sha256(after).hexdigest()}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x018-TT-eval-consumer-route-modes-E-V-v1",
      "mode_E":"recompute rather than read TT cached static evaluation at the selected full64-writer physical slot",
      "mode_V":"skip TT score/bound use as improved evaluation only; early TT cutoff untouched",
      "event_site_E":"tt_cached_eval",
      "event_site_V":"tt_value_eval_override",
      "modified_files":changed,
      "limits":["Recomputed eval may equal stored eval exactly and thus leave search unchanged",
                "Mode E can influence static-eval-dependent heuristics and continuation histories",
                "Mode V only bypasses one TT score use, not all other TT score uses or move hints",
                "Neither E nor V is proof of sole natural TT causal mediation",
                "Single-thread, fixed FEN, exact source/target and original-core controls mandatory"]
    },indent=2)+"\n")
    print("C3X018_TT_EVAL_VALUE_COMPETING_ROUTES_PATCH_APPLIED")
if __name__=="__main__":main()
