#!/usr/bin/env python3
"""P42/R10: source-site-specific value_draw neutralization, atop proven R9 build.

Disentangles original Stockfish16 call sites:
1: search-cycle alpha draw; 2: draw/terminal return. 3: both.
Requires R9's exact actual source function to exist; never changes historical
0.27 or R8/R9 original code. Raw physical trace is private, not causal proof.
"""
from pathlib import Path
import argparse,hashlib,json

FUNCTION_TAIL="    return c3x042_r9_neutral ? VALUE_DRAW : c3x042_r9_native;\n  }"
CYCLE="alpha = value_draw(pos.this_thread());"
TERMINAL=": value_draw(pos.this_thread());"

HELPER=r'''
  // R10 independent site challenge. Site 1=cycle-alpha, site 2=terminal draw.
  Value c3x042_r10_draw_site(const Thread* thread, int site, int ply) {
      const Value original = value_draw(thread);
      const char* mode = std::getenv("C3X042_R10_NEUTRAL_DRAW_SITE");
      const char code = mode && mode[1] == '\0' ? mode[0] : '0';
      const bool selected = ((code == '1' && site == 1)
                          || (code == '2' && site == 2)
                          || code == '3');
      const Value result = selected ? VALUE_DRAW : original;
      if (const char* path = std::getenv("C3X042_R10_DRAW_SITE_TRACE")) {
          if (*path) {
              if (auto* f=std::fopen(path,"a")) {
                  std::fprintf(f,"c3x042_r10 site=%d ply=%d mod4=%d original=%d selected=%d result=%d\n",
                      site,ply,int(thread->nodes & 3),int(original),
                      int(selected),int(result));
                  std::fclose(f);
              }
          }
      }
      return result;
  }
'''

def patch(source):
    if "c3x042_r10_draw_site(" in source:
        raise ValueError("R10_HOLD_ALREADY_PATCHED")
    for name,anchor in (("R9",FUNCTION_TAIL),("CYCLE",CYCLE),("TERMINAL",TERMINAL)):
        if source.count(anchor)!=1:
            raise ValueError(f"R10_HOLD_{name}_ANCHOR_COUNT_{source.count(anchor)}")
    source=source.replace(FUNCTION_TAIL,FUNCTION_TAIL+"\n"+HELPER,1)
    source=source.replace(CYCLE,"alpha = c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);",1)
    source=source.replace(TERMINAL,": c3x042_r10_draw_site(pos.this_thread(),2,ss->ply);",1)
    return source

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    original=f.read_bytes()
    after=patch(original.decode("utf-8")).encode("utf-8")
    f.write_bytes(after)
    output=Path(a.out_manifest);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({
      "schema":"c3x042-r10-native-site-specific-draw-v1",
      "original_sha256":hashlib.sha256(original).hexdigest(),
      "source_sha256":hashlib.sha256(after).hexdigest(),
      "site_1":"search-cycle-alpha-value_draw",
      "site_2":"search-terminal-value_draw",
      "site_3":"both simultaneously",
      "privacy":"raw site and ply events private",
      "root_choice_or_strategy_certified":False
    },indent=2,sort_keys=True)+"\n")
    print("C3X042_R10_SITE_SOURCE_PATCHED_NATIVE_RESULT_HOLD")
if __name__=="__main__":
    main()
