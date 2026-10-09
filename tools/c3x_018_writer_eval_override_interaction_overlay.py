#!/usr/bin/env python3
"""Nested TT write-and-evaluation-consumer court (WV) on frozen SF16.

Apply strictly after source physical epoch patch and E/V evaluation overlay.
WV jointly blocks 2 selected writes and the selected bound-conditioned TT
value-as-evaluation use, with independent contact accounting.
Not a proof of natural mediation or path uniqueness.
"""
import argparse,hashlib,json
from pathlib import Path
def once(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X018_WV_EPISTASIS_{name}_{n}")
    return s.replace(a,b,1)
def patch_tt(s):
    s=once(s,
       '(std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0)',
       '(std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0 ||\n         std::strcmp(mode, "WV") == 0)',"WRITER_ARM")
    s=once(s,
       '''(std::strcmp(mode, "V") == 0
                            && std::strcmp(site, "tt_value_eval_override") == 0)''',
       '''((std::strcmp(mode, "V") == 0 || std::strcmp(mode, "WV") == 0)
                            && std::strcmp(site, "tt_value_eval_override") == 0)''',
       "READER_ARM")
    s=once(s,
       '''(std::strcmp(mode, "V") == 0 &&
         std::strcmp(site, "tt_value_eval_override") == 0 && !block)''',
       '''((std::strcmp(mode, "V") == 0 || std::strcmp(mode, "WV") == 0) &&
         std::strcmp(site, "tt_value_eval_override") == 0 && !block)''',
       "NO_CONTACT_LOG")
    return s
def patch_search(s):
    a='std::strcmp(std::getenv("C3X018_TT_MODE"), "V") == 0 &&'
    n=s.count(a)
    if n!=2:raise RuntimeError(f"C3X018_WV_EPISTASIS_TWO_EVAL_BRANCHES_{n}")
    b='(std::strcmp(std::getenv("C3X018_TT_MODE"), "V") == 0 ||\n                 std::strcmp(std::getenv("C3X018_TT_MODE"), "WV") == 0) &&'
    return s.replace(a,b)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();root=Path(a.source)/"src";d={}
    for name,fn in (("tt.cpp",patch_tt),("search.cpp",patch_search)):
        f=root/name;before=f.read_bytes();after=fn(before.decode()).encode()
        f.write_bytes(after);d[name]={"before":hashlib.sha256(before).hexdigest(),
                                      "after":hashlib.sha256(after).hexdigest()}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x018-W2-plus-V-TT-physical-writer-reader-factorial-source-overlay-v1",
      "mode":"WV","modified":d,
      "scope":["WV = original W whole-save writer suppression plus V bound-based evaluation correction reader suppression",
               "Reader suppression requires exact current full64 writer shadow, physical slot and epoch",
               "W2 may eliminate later eligible V read, report not-fired rather than infer no mechanism",
               "W2+V outcome equality to either operator does not identify unique mediation",
               "All source actions must be cold repeated and compared to original O/F/Z UCI tuple"]
    },indent=2)+"\n")
    print("C3X018_WV_COMBINED_TT_SOURCE_PATCH_APPLIED")
if __name__=="__main__":main()
